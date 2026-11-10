# One-line purpose: HTTP API + static UI. Every gate is enforced here and in the DB layer, never by hidden buttons.
import io
import json
import os
import time
import uuid
import hashlib
import zipfile
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .. import config
from ..checks import ck1_quote
from ..db import read_path as db
from ..llm import adapter
from ..pipeline.run import run_rebuild
from ..pipeline.seed_demo import load_demo_project
from ..policy.labels import role_labels, can_read_label, weakest_label
from ..readers import readers
from ..storage import save_upload
from ..util import now_iso, sha256_text, new_id

DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() == "true"
ROLES = ("leaver", "reviewer", "successor", "admin")
APP_ROOT = Path(__file__).resolve().parents[3]  # repo root (api -> app -> backend -> repo)
FRONTEND = APP_ROOT / "frontend"

app = FastAPI(title="Tether", version="1.0.0", docs_url="/docs", openapi_url="/openapi.json")


@app.exception_handler(HTTPException)
async def http_exc(_, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


# ---------------------------------------------------------------- identity (demo-mode role switcher; DEMO_MODE only)
def identity(x_tether_role: str | None = Header(default=None)):
    if not DEMO_MODE:
        raise HTTPException(401, "demo role switcher disabled (DEMO_MODE=false); no other sign-in is built — see docs/LIMITATIONS.md")
    role = (x_tether_role or "").lower().strip()
    if role not in ROLES:
        raise HTTPException(401, "missing or unknown X-Tether-Role header (expected leaver, reviewer, successor or admin)")
    return role


def _actor(project_id: str, role: str) -> str:
    user = db.user_by_role(project_id, role)
    return user["name"] if user else role


def _project_or_404(project_id: str):
    p = db.get_project(project_id)
    if p is None:
        raise HTTPException(404, "project not found")
    return p


def _role_guard(role: str, allowed):
    if role not in allowed:
        raise HTTPException(403, f"role {role} may not do that")


def _claim_readable(role: str, label: str) -> bool:
    return can_read_label(role, label)


def _visible_claims(project_id: str, role: str):
    if role == "successor":
        raise HTTPException(403, "the successor reads the signed handover, not the queue — open /handover")
    labels = role_labels(role)
    return [c for c in db.list_claims(project_id) if c["label"] in labels]


def _claim_public(c: dict, role: str) -> dict:
    ev = db.list_evidence(c["id"])
    return {
        "id": c["id"], "type": c["type"], "text": c["text"], "status": c["status"],
        "review_state": c["review_state"], "review_reason": c["review_reason"],
        "confidence": c["confidence"], "confidence_rule": c["confidence_rule"],
        "label": c["label"], "subject": c["subject"], "attribute": c["attribute"], "value": c["value"],
        "reason": c["reason"], "rejected_options": json.loads(c["rejected_options"] or "[]"),
        "risk_estimate": c.get("risk_estimate"), "risk_rule": c.get("risk_rule"),
        "gap_subject": c.get("gap_subject"),
        "evidence": [{"quote": e["quote"], "locator": e["locator"], "source_label": e["source_label"],
                      "captured_at": e["captured_at"], "span_id": e["span_id"]} for e in ev],
    }


# ---------------------------------------------------------------- meta
@app.get("/api/health")
def health():
    db.init_db()
    return {"ok": True, "at": now_iso(), "demo_mode": DEMO_MODE, "llm_mode": adapter.llm_mode()}


@app.get("/api/selftest")
def selftest():
    db.init_db()
    checks = {
        "database_reachable": True,
        "schema_present": db.list_projects() is not None,
        "seed_demo_present": (APP_ROOT / "data" / "demo_project" / "answer_key.json").exists(),
        "replay_fixtures": adapter.llm_mode(),
    }
    if not all(v is True or isinstance(v, str) for v in checks.values()):
        return JSONResponse(checks, status_code=500)
    return {"ok": True, "checks": checks, "at": now_iso()}


# ---------------------------------------------------------------- projects
class ProjectIn(BaseModel):
    name: str


@app.post("/api/projects")
def create_project(body: ProjectIn, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    if not body.name.strip():
        raise HTTPException(400, "name is required")
    p = db.create_project(body.name.strip())
    db.seed_users(p["id"])
    db.append_log(_actor(p["id"], role), role, "project.created", p["id"], {"name": p["name"]})
    return p


@app.post("/api/projects/demo")
def create_demo(x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin", "leaver", "successor"))
    # Idempotent: a freshly seeded Aster (still at the label gate) is reused; a finished demo
    # never blocks creating the next one.
    for p in db.list_projects():
        if p["name"] == "Aster — campus club events app" and p["state"] == "scoped":
            return p
    p = load_demo_project(name=None, role=role)
    return db.get_project(p["id"])


@app.get("/api/projects")
def list_projects(x_tether_role: str | None = Header(default=None)):
    identity(x_tether_role)
    return db.list_projects()


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    p = _project_or_404(project_id)
    p = dict(p)
    p["users"] = [{"name": u["name"], "role": u["role"]} for u in db.list_users(project_id)]
    return p


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("admin",))
    p = _project_or_404(project_id)
    db.append_log(_actor(project_id, role), role, "project.deleted", project_id, {"name": p["name"]})
    db.delete_project(project_id)
    return {"ok": True, "deleted": project_id}


@app.post("/api/projects/{project_id}/delete-request")
def delete_request(project_id: str, detail: str = Form(default="a person asked for their rows to be deleted"),
                   x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    p = _project_or_404(project_id)
    db.insert_retention_request(project_id, _actor(project_id, role), detail)
    db.append_log(_actor(project_id, role), role, "retention.requested", project_id, detail)
    return {"ok": True, "note": "request logged; data kept until the admin deletes the project or its retention expires"}


@app.put("/api/projects/{project_id}/retention")
def set_retention(project_id: str, days: int = Form(...), x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("admin",))
    _project_or_404(project_id)
    if not (1 <= days <= 365):
        raise HTTPException(400, "retention must be between 1 and 365 days")
    db.set_retention(project_id, days)
    db.append_log(_actor(project_id, role), role, "retention.set", project_id, {"days": days})
    return {"ok": True, "retention_days": days}


# ---------------------------------------------------------------- sources & connect step
@app.get("/api/projects/{project_id}/sources")
def sources(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _project_or_404(project_id)
    out = []
    for s in db.list_sources(project_id):
        item = dict(s)
        if item["label"] and role == "successor":
            pass  # successor may see source metadata (counts as metadata, no claim text)
        out.append(item)
    return out


def _sniff_json_kind(name: str, raw: bytes):
    return readers.sniff_json_kind(name, raw)


async def _ingest_one(project_id: str, path_name: str, data: bytes, label, manifest_labels):
    name = Path(path_name).name
    lower = name.lower()
    if lower == "manifest.json":
        return None  # metadata only
    manifest_key = path_name.replace("\\", "/")
    label = manifest_labels.get(manifest_key) or manifest_labels.get(name) or label or "internal"
    if lower.endswith((".bundle",)):
        kind = "repo"
    elif lower.endswith((".md", ".markdown", ".txt")):
        kind = "notes"
    elif lower.endswith(".json"):
        kind = _sniff_json_kind(name, data)
        if kind == "unknown":
            raise HTTPException(415, f"{name}: unrecognised JSON — expected a chat export, an issues list, a PR list, or a repo bundle")
    else:
        raise HTTPException(415, f"{name}: unsupported file type. Accepted: .md, .txt, .json, .bundle (git bundle create)")
    src = db.create_source(project_id, kind, path_name.replace("\\", "/") if "/" in path_name else name,
                           label, "pending", hashlib.sha256(data).hexdigest())
    save_upload(src["id"], name, data)
    return src


@app.post("/api/projects/{project_id}/sources")
async def upload_sources(project_id: str,
                         x_tether_role: str | None = Header(default=None),
                         consent: str = Form(default=""),
                         files: list[UploadFile] = File(default=[])):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin", "leaver"))
    p = _project_or_404(project_id)
    if consent.lower() not in ("true", "on", "1", "yes"):
        db.append_log(_actor(project_id, role), role, "consent.missing", project_id, "upload refused — consent not ticked")
        raise HTTPException(400, "consent is required before any source is stored: tick the box that you are allowed to use these sources")
    if not files:
        raise HTTPException(400, "no files uploaded")
    # a companion manifest.json supplies labels and channel exclusions
    raw = {f.filename: await f.read() for f in files}
    manifest = None
    for name, data in raw.items():
        if Path(name).name.lower() == "manifest.json":
            try:
                manifest = json.loads(data)
            except json.JSONDecodeError:
                raise HTTPException(400, "manifest.json is not valid JSON")
    manifest_labels = {}
    manifest_excl = {}
    if manifest:
        for s in manifest.get("sources", []):
            manifest_labels[s.get("path", "")] = s.get("label")
            manifest_labels[Path(s.get("path", "")).name] = s.get("label")
            if s.get("excluded_channels"):
                manifest_excl[Path(s.get("path", "")).name] = s["excluded_channels"]
        for ch in manifest.get("excluded_channels", []):
            manifest_excl.setdefault("__all_chat__", [])
            if ch not in manifest_excl["__all_chat__"]:
                manifest_excl["__all_chat__"].append(ch)
    created = []
    for name, data in raw.items():
        if Path(name).name.lower() == "manifest.json":
            continue
        excl = manifest_excl.get(Path(name).name) or manifest_excl.get("__all_chat__") or []
        src = await _ingest_one(project_id, name, data, None, manifest_labels)
        if src:
            if excl and src["kind"] == "chat":
                db.set_source_label(src["id"], src["label"])  # label unchanged; exclusions recorded
                db.set_source_excluded_channels(src["id"], excl)
                for ch in excl:
                    db.create_source(project_id, "chat", f"{Path(name).name} · #{ch}", None, "not read", "",
                                     f"excluded — {manifest.get('exclude_reasons', {}).get(ch, 'not ours to read')}" if manifest else "excluded — not read")
            created.append(db.get_source(src["id"]))
    db.append_log(_actor(project_id, role), role, "consent.ticked", project_id,
                  {"files": len(created), "consent": True})
    db.append_log(_actor(project_id, role), role, "sources.uploaded", project_id,
                  [c["name"] for c in created])
    return {"created": created}


@app.put("/api/projects/{project_id}/sources/{source_id}")
def set_label(project_id: str, source_id: str, label: str = Form(...), x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    p = _project_or_404(project_id)
    if p["state"] not in ("scoped", "labelled"):
        raise HTTPException(409, f"labels are locked once the project is {p['state']} — re-run policies via a new project")
    if label not in config.LABELS:
        raise HTTPException(400, f"label must be one of {', '.join(config.LABELS)}")
    src = db.get_source(source_id)
    if src is None or src["project_id"] != project_id:
        raise HTTPException(404, "source not found")
    if src["read_state"] == "not read":
        raise HTTPException(409, "an excluded channel has no label — it is not read")
    before = src["label"]
    db.set_source_label(source_id, label)
    db.append_log(_actor(project_id, role), role, "label.set", source_id, {"before": before, "after": label})
    return db.get_source(source_id)


@app.post("/api/projects/{project_id}/gates/labels")
def clear_labels(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    p = _project_or_404(project_id)
    pending = [s for s in db.list_sources(project_id) if s["read_state"] != "not read" and not s["label"]]
    if pending:
        db.append_log(_actor(project_id, role), role, "gate.refused", project_id,
                      {"gate": "labels", "reason": "labels still pending", "pending": [s["name"] for s in pending]})
        raise HTTPException(409, {"pending": [s["name"] for s in pending], "note": "every source that will be read needs a label first"})
    if p["state"] != "scoped":
        db.append_log(_actor(project_id, role), role, "gate.refused", project_id,
                      {"gate": "labels", "reason": f"project is {p['state']}"})
        raise HTTPException(409, f"the labels gate already ran — project is {p['state']}")
    db.set_project_state(project_id, "labelled")
    for s in db.list_sources(project_id):
        if s["read_state"] == "pending" and s["label"]:
            db.set_source_read(s["id"], "read")
    db.append_log(_actor(project_id, role), role, "gate.labels_cleared", project_id, {"gate": 1})
    return {"ok": True, "state": db.get_project(project_id)["state"]}


@app.post("/api/projects/{project_id}/runs")
def start_run(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    p = _project_or_404(project_id)
    try:
        result = run_rebuild(project_id, actor=_actor(project_id, role), role=role)
    except PermissionError as e:
        db.append_log(_actor(project_id, role), role, "run.refused", project_id, str(e))
        raise HTTPException(409, str(e))
    counts = result["counts"]
    warnings = list(result["warnings"])
    if counts["kept"] < 10:
        warnings.append("fewer than ten claims kept — the rules extractor ran as backup; treat the queue accordingly")
    return {"run": {"id": result["run"]["id"], "extractor": counts["extractor"], "model_id": counts["model_id"],
                    "finished_at": result["run"]["finished_at"]},
            "counts": counts, "steps": result["steps"], "warnings": warnings}


@app.get("/api/runs/{run_id}/report")
def run_report(run_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    r = db.get_run(run_id)
    if r is None:
        raise HTTPException(404, "run not found")
    counts = json.loads(r["counts"] or "{}")
    return {"id": r["id"], "project_id": r["project_id"], "extractor": r["extractor"],
            "model_id": r["model_id"], "prompt_version": r["prompt_version"], "params": json.loads(r["params"] or "{}"),
            "started_at": r["started_at"], "finished_at": r["finished_at"], "counts": counts}


# ---------------------------------------------------------------- claims & review queue
@app.get("/api/projects/{project_id}/claims")
def list_claims(project_id: str, status: str | None = None, type: str | None = None,
                review_state: str | None = None, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _project_or_404(project_id)
    labels = role_labels(role)
    claims = [c for c in _visible_claims(project_id, role)]
    if status:
        claims = [c for c in claims if c["status"] == status]
    if type:
        claims = [c for c in claims if c["type"] == type]
    if review_state:
        claims = [c for c in claims if c["review_state"] == review_state]
    return [_claim_public(c, role) for c in claims]


class ClaimAction(BaseModel):
    action: str           # confirm | edit | reject | park | proposal
    text: str | None = None
    reason: str | None = None


@app.post("/api/claims/{claim_id}/review")
def review_claim(claim_id: str, body: ClaimAction, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    claim = db.get_claim(claim_id)
    if claim is None:
        raise HTTPException(404, "claim not found")
    project_id = claim["project_id"]
    p = _project_or_404(project_id)
    actor = _actor(project_id, role)
    before = {"text": claim["text"], "review_state": claim["review_state"], "status": claim["status"]}

    if role == "leaver":
        if body.action != "proposal":
            raise HTTPException(403, "the leaver proposes corrections — only the reviewer confirms, edits, rejects or parks")
        if not (body.text or body.reason):
            raise HTTPException(400, "a proposal needs text or a reason")
        db.insert_review(project_id, "claim", claim_id, actor, "proposal", before, {"proposal": body.text, "note": body.reason}, body.reason)
        db.append_log(actor, role, "claim.proposal", claim_id, {"text": body.text})
        return {"ok": True, "note": "proposal sent — the reviewer decides what lands"}

    _role_guard(role, ("reviewer",))
    action = body.action.lower()
    if action == "confirm":
        db.update_claim_fields(claim_id, review_state="confirmed", review_actor=actor, review_reason=None)
    elif action == "edit":
        if not body.text or not body.text.strip():
            raise HTTPException(400, "edit needs the new text")
        if len(body.text.strip()) > 240:
            raise HTTPException(400, "claim text stays one short sentence (240 chars)")
        db.update_claim_fields(claim_id, text=body.text.strip(), review_state="edited", review_actor=actor, review_reason=body.reason)
    elif action == "reject":
        if not body.reason or len(body.reason.strip()) < 3:
            raise HTTPException(400, "reject needs a written reason")
        db.update_claim_fields(claim_id, review_state="rejected", review_actor=actor, review_reason=body.reason.strip())
    elif action == "park":
        if not body.reason or len(body.reason.strip()) < 3:
            raise HTTPException(400, "park needs a written reason")
        db.update_claim_fields(claim_id, review_state="parked", review_actor=actor, review_reason=body.reason.strip())
    else:
        raise HTTPException(400, "action must be confirm, edit, reject or park")

    after_claim = db.get_claim(claim_id)
    db.insert_review(project_id, "claim", claim_id, actor, action, before,
                     {"text": after_claim["text"], "review_state": after_claim["review_state"]},
                     body.reason)
    db.append_log(actor, role, f"claim.{action}", claim_id, {"reason": body.reason})
    if p["state"] == "rebuilt":
        db.set_project_state(project_id, "in review")
    return _claim_public(db.get_claim(claim_id), role)


@app.get("/api/projects/{project_id}/proposals")
def proposals(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    return [r for r in db.list_reviews(project_id) if r["action"] == "proposal"]


# ---------------------------------------------------------------- conflicts
@app.get("/api/projects/{project_id}/conflicts")
def list_conflicts(project_id: str, state: str | None = None, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    if role == "successor":
        raise HTTPException(403, "the successor reads the signed handover, not the conflict queue")
    _project_or_404(project_id)
    out = []
    for c in db.list_conflicts(project_id, state):
        visible_claims = [cl for cl in c["claims"] if _claim_readable(role, cl["label"])]
        if len(visible_claims) != len(c["claims"]) and role == "leaver":
            continue  # a side the leaver may not see means the conflict waits for the reviewer
        c = dict(c)
        c["claims"] = [_claim_public(cl, role) for cl in c["claims"]]
        out.append(c)
    return out


class ConflictDecision(BaseModel):
    value: str | None = None
    reason: str
    park: bool = False


@app.post("/api/conflicts/{conflict_id}/decide")
def decide_conflict(conflict_id: str, body: ConflictDecision, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer",))
    conflict = db.get_conflict(conflict_id)
    if conflict is None:
        raise HTTPException(404, "conflict not found")
    project_id = conflict["project_id"]
    actor = _actor(project_id, role)
    if not body.reason or len(body.reason.strip()) < 3:
        raise HTTPException(400, "a decision needs a written reason")
    if body.park:
        db.park_conflict(conflict_id, actor, body.reason.strip())
        db.insert_review(project_id, "conflict", conflict_id, actor, "park", {"state": "open"}, {"state": "parked"}, body.reason)
        db.append_log(actor, role, "conflict.parked", conflict_id, {"reason": body.reason.strip()})
    else:
        values = [cl["value"] for cl in conflict["claims"]]
        if body.value not in values:
            raise HTTPException(400, f"value must be one of: {', '.join(str(v) for v in values)}")
        db.decide_conflict(conflict_id, body.value, actor, body.reason.strip())
        db.insert_review(project_id, "conflict", conflict_id, actor, "decide", {"state": "open"}, {"state": "decided", "value": body.value}, body.reason)
        db.append_log(actor, role, "conflict.decided", conflict_id, {"value": body.value, "reason": body.reason.strip()})
    p = db.get_project(project_id)
    if p["state"] == "rebuilt":
        db.set_project_state(project_id, "in review")
    return db.get_conflict(conflict_id)


# ---------------------------------------------------------------- gaps
@app.get("/api/projects/{project_id}/gaps")
def list_gaps(project_id: str, state: str | None = None, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    if role == "successor":
        raise HTTPException(403, "the successor reads the signed handover, not the gap queue")
    _project_or_404(project_id)
    gaps = db.list_gaps(project_id, state)
    return gaps + [g for g in db.list_suggested_gaps(project_id)]


class GapAction(BaseModel):
    owner: str | None = None
    next_step: str | None = None
    park: bool = False
    reason: str | None = None


@app.post("/api/gaps/{gap_id}/assign")
def assign_gap(gap_id: str, body: GapAction, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer",))
    gap = db.get_gap(gap_id)
    if gap is None:
        raise HTTPException(404, "gap not found")
    project_id = gap["project_id"]
    actor = _actor(project_id, role)
    if body.park:
        if not body.reason or len(body.reason.strip()) < 3:
            raise HTTPException(400, "park needs a written reason")
        db.park_gap(gap_id, body.reason.strip())
        db.insert_review(project_id, "gap", gap_id, actor, "park", {"state": gap["state"]}, {"state": "parked"}, body.reason)
        db.append_log(actor, role, "gap.parked", gap_id, {"reason": body.reason.strip()})
    else:
        if not body.owner or not body.next_step:
            raise HTTPException(400, "assign needs an owner (who may know) and a next step")
        db.assign_gap(gap_id, body.owner.strip(), body.next_step.strip())
        db.insert_review(project_id, "gap", gap_id, actor, "assign", {"state": gap["state"]}, {"state": "closed", "owner": body.owner}, None)
        db.append_log(actor, role, "gap.assigned", gap_id, {"owner": body.owner.strip()})
    p = db.get_project(project_id)
    if p["state"] == "rebuilt":
        db.set_project_state(project_id, "in review")
    return db.get_gap(gap_id)


# ---------------------------------------------------------------- quarantine (injection defence)
@app.get("/api/projects/{project_id}/quarantine")
def list_quarantine(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    return db.list_quarantine(project_id)


class QuarantineAction(BaseModel):
    action: str  # dismissed | confirmed
    note: str | None = None


@app.post("/api/quarantine/{quar_id}/act")
def act_quarantine(quar_id: str, body: QuarantineAction, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer",))
    if body.action not in ("dismissed", "confirmed"):
        raise HTTPException(400, "action must be dismissed or confirmed")
    db.act_quarantine(quar_id, body.action, _actor(_project_of_quar(quar_id), role))
    db.append_log(_actor(_project_of_quar(quar_id), role), role, f"quarantine.{body.action}", quar_id, body.note or "")
    return {"ok": True}


def _project_of_quar(quar_id: str) -> str:
    for p in db.list_projects():
        for q in db.list_quarantine(p["id"]):
            if q["id"] == quar_id:
                return p["id"]
    raise HTTPException(404, "quarantine item not found")


# ---------------------------------------------------------------- gates & sign-off
def _gate_report(project_id: str):
    p = db.get_project(project_id)
    sources = db.list_sources(project_id)
    readable = [s for s in sources if s["read_state"] != "not read"]
    gate1_ok = p["state"] != "scoped" and all(s["label"] for s in readable)
    gate1 = {"ok": gate1_ok, "detail": "labels cleared" if gate1_ok else "label gate not passed (scoped)"}

    open_conflicts = db.list_conflicts(project_id, "open")
    gate2a = {"ok": len(open_conflicts) == 0,
              "detail": "every conflict decided or parked" if not open_conflicts else f"{len(open_conflicts)} conflict(s) still open"}

    uncertain = [c for c in db.list_claims(project_id, status="uncertain")]
    unsettled = [c for c in uncertain if c["review_state"] == "pending"]
    gate2b = {"ok": not unsettled,
              "detail": "every uncertain item settled or parked with a reason" if not unsettled else f"{len(unsettled)} uncertain claim(s) still pending"}

    confirmed = [c for c in db.list_claims(project_id) if c["review_state"] in ("confirmed", "edited")]
    failures = []
    for c in confirmed:
        for e in db.list_evidence(c["id"]):
            span = db.get_span(e["span_id"])
            if span is None or not ck1_quote.check_quote(span["text"], e["quote"]):
                failures.append(e["locator"])
    gate3 = {"ok": not failures, "detail": f"citation test 100% ({len(confirmed)} confirmed/edited claims re-verified)" if not failures else f"citation test FAILED at {failures[:3]}"}

    return {"gate1_labels": gate1, "gate2_conflicts": gate2a, "gate2_uncertain": gate2b, "gate3_citation": gate3,
            "all": gate1["ok"] and gate2a["ok"] and gate2b["ok"] and gate3["ok"],
            "confirmed_or_edited": len(confirmed)}


@app.get("/api/projects/{project_id}/gates")
def gates(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    return _gate_report(project_id)


def _signed_payload(project_id: str, version_number: str):
    p = db.get_project(project_id)
    items = []
    for c in db.list_claims(project_id):
        if c["review_state"] not in ("confirmed", "edited"):
            continue
        ev = db.list_evidence(c["id"])
        items.append({
            "id": c["id"], "type": c["type"], "text": c["text"],
            "subject": c["subject"], "attribute": c["attribute"], "value": c["value"],
            "reason": c["reason"], "rejected_options": json.loads(c["rejected_options"] or "[]"),
            "confidence": c["confidence"], "confidence_rule": c["confidence_rule"],
            "status": c["status"], "label": c["label"],
            "risk_estimate": c.get("risk_estimate"), "risk_rule": c.get("risk_rule"),
            "evidence": [{"quote": e["quote"], "locator": e["locator"], "source_label": e["source_label"],
                          "captured_at": e["captured_at"], "span_id": e["span_id"]} for e in ev],
        })
    gaps = [dict(g) for g in db.list_gaps(project_id) if g["state"] in ("open", "parked", "closed")]
    latest = db.latest_run(project_id)
    return {
        "version": version_number,
        "project": {"id": p["id"], "name": p["name"], "codename": p["codename"]},
        "generated_from_run": latest["id"] if latest else None,
        "items": items,
        "gaps": gaps,
        "risk_rule": "estimate · type weight +3 single-author module ≥80% +2 open issue/PR link +2 conflict or gap beside it. Estimates rank work, never people.",
        "counts": {"items": len(items), "gaps": len(gaps)},
    }


@app.post("/api/projects/{project_id}/versions/sign")
def sign_version(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer",))
    p = _project_or_404(project_id)
    actor = _actor(project_id, role)
    if p["state"] not in ("in review", "rebuilt"):
        db.append_log(actor, role, "sign.refused", project_id, {"reason": f"project is {p['state']}"})
        raise HTTPException(409, f"project is {p['state']} — only a project in review can be signed")
    report = _gate_report(project_id)
    if not report["all"]:
        failures = [k for k, v in report.items() if k.startswith("gate") and not v["ok"]]
        db.append_log(actor, role, "sign.refused", project_id, {"failed": failures})
        raise HTTPException(409, {"errors": failures, "gates": report, "note": "sign-off refused: every conflict decided or parked with a reason, every uncertain item settled or parked with a reason, citation test at 100%"})
    number = f"v1.{len(db.list_versions(project_id))}"
    payload = _signed_payload(project_id, number)
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    vid_hash = hashlib.sha256(payload_bytes).hexdigest()
    version = db.create_version(project_id, number, payload, vid_hash, actor)
    db.set_project_state(project_id, "signed")
    db.append_log(actor, role, "version.signed", version["id"], {"number": number, "sha256": vid_hash, "items": len(payload["items"])})
    return {"id": version["id"], "number": number, "sha256": vid_hash, "signed_by": actor, "signed_at": version["signed_at"], "items": len(payload["items"])}


@app.post("/api/projects/{project_id}/share")
def share_version(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    p = _project_or_404(project_id)
    actor = _actor(project_id, role)
    if db.latest_signed_version(project_id) is None:
        db.append_log(actor, role, "share.refused", project_id, {"reason": "nothing signed to share"})
        raise HTTPException(409, "nothing signed to share")
    if p["state"] != "signed":
        db.append_log(actor, role, "share.refused", project_id, {"reason": f"project is {p['state']}"})
        raise HTTPException(409, f"project is {p['state']} — only a signed version can be shared")
    db.set_project_state(project_id, "shared")
    db.append_log(actor, role, "version.shared", project_id, {})
    return {"ok": True, "state": "shared"}


def _visible_version(project_id: str, role: str):
    p = db.get_project(project_id)
    if p is None:
        raise HTTPException(404, "project not found")
    if role in ("successor", "leaver") and p["state"] not in ("signed", "shared", "received"):
        raise HTTPException(403, "the handover opens once the reviewer has signed — nothing is shared yet")
    v = db.latest_signed_version(project_id)
    if v is None:
        raise HTTPException(403, "no signed version exists")
    return p, v


def _filter_payload(payload: dict, role: str):
    allowed = set(role_labels(role))
    items = [i for i in payload["items"] if i["label"] in allowed]
    hidden = len(payload["items"]) - len(items)
    payload = dict(payload)
    payload["items"] = items
    return payload, hidden


def _sections(payload: dict):
    items = sorted(payload["items"], key=lambda i: (i.get("risk_estimate") or 0), reverse=True)
    by_type = lambda t: [i for i in items if i["type"] == t]
    gaps = payload.get("gaps", [])
    return [
        {"id": "own-first", "title": "Own first", "hint": "sorted by the risk estimate — take these before anything else", "items": items[:5], "kind": "claims"},
        {"id": "open-work", "title": "Open work", "hint": "next steps the sources actually name", "items": by_type("next step"), "kind": "claims"},
        {"id": "decisions", "title": "Decisions and why", "hint": "every decision keeps its reason and what was rejected", "items": by_type("decision"), "kind": "claims"},
        {"id": "dependencies", "title": "Dependencies and accounts", "hint": "what this project stands on", "items": by_type("dependency"), "kind": "claims"},
        {"id": "repeated", "title": "Repeated problems", "hint": "things that keep happening — do not be the next person surprised", "items": by_type("repeated problem"), "kind": "claims"},
        {"id": "unknowns", "title": "What nobody knows — and who to ask", "hint": "gaps stay visible; each has an owner and a next step", "items": gaps, "kind": "gaps"},
    ]


@app.get("/api/projects/{project_id}/handover")
def handover(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    p, v = _visible_version(project_id, role)
    payload = json.loads(v["payload"])
    filtered, hidden = _filter_payload(payload, role)
    notice = "Some information is restricted for your role." if hidden else None
    successor = db.user_by_role(project_id, "successor")
    return {
        "project": {"name": p["name"], "codename": p["codename"]},
        "version": {"id": v["id"], "number": v["number"], "sha256": v["sha256"], "signed_by": v["signed_by"], "signed_at": v["signed_at"]},
        "state": p["state"],
        "sections": _sections(filtered),
        "risk_rule": payload.get("risk_rule"),
        "restricted_notice": notice,
        "receipt": db.receipt_exists(v["id"], successor["id"]) if successor and role == "successor" else None,
        "role": role,
    }


@app.get("/api/projects/{project_id}/versions/{version_id}")
def get_version(project_id: str, version_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    p, v = _visible_version(project_id, role)
    if version_id not in (v["id"], v["number"], "latest"):
        raise HTTPException(404, "version not found")
    payload = json.loads(v["payload"])
    filtered, hidden = _filter_payload(payload, role)
    return {"id": v["id"], "number": v["number"], "state": v["state"], "sha256": v["sha256"],
            "signed_by": v["signed_by"], "signed_at": v["signed_at"],
            "payload": filtered,
            "restricted_notice": "Some information is restricted for your role." if hidden else None}


@app.post("/api/projects/{project_id}/receipt")
def receipt(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("successor",))
    p, v = _visible_version(project_id, role)
    successor = db.user_by_role(project_id, "successor")
    db.create_receipt(v["id"], successor["id"])
    if p["state"] in ("signed", "shared"):
        db.set_project_state(project_id, "received")
    db.append_log(successor["name"], role, "receipt.confirmed", v["id"], {"number": v["number"]})
    return {"ok": True, "state": db.get_project(project_id)["state"]}


# ---------------------------------------------------------------- export & audit log (admin / reviewer)
@app.get("/api/projects/{project_id}/export")
def export_project(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("admin",))
    p = _project_or_404(project_id)
    data = {
        "project": p,
        "sources": db.list_sources(project_id),
        "claims": [_claim_public(c, role) for c in db.list_claims(project_id)],
        "conflicts": db.list_conflicts(project_id),
        "gaps": db.list_gaps(project_id),
        "suggested_gaps": db.list_suggested_gaps(project_id),
        "quarantine": db.list_quarantine(project_id),
        "reviews": db.list_reviews(project_id),
        "versions": [{k: v for k, v in ver.items() if k != "payload"} | {"sha256": ver["sha256"]} for ver in db.list_versions(project_id)],
        "log": db.list_log(10000),
        "redaction_total": db.redaction_total(project_id),
    }
    body = json.dumps(data, indent=2, default=str).encode("utf-8")
    fname = f"tether-export-{project_id}-{now_iso()[:10]}.json"
    db.append_log(_actor(project_id, role), role, "project.exported", project_id, {"bytes": len(body)})
    return Response(body, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@app.get("/api/projects/{project_id}/log")
def get_log(project_id: str, verify: int = 0, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    rows = db.list_log(2000)
    out = {"rows": rows}
    if verify:
        out["chain"] = db.verify_log_chain()
    return out


@app.post("/api/projects/{project_id}/verify-chain")
def verify_chain(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    return db.verify_log_chain()


# ---------------------------------------------------------------- citations (label-checked)
@app.get("/api/spans/{span_id}")
def get_span(span_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    span = db.get_span(span_id)
    if span is None:
        raise HTTPException(404, "span not found")
    src = db.get_source(span["source_id"])
    if src is None:
        raise HTTPException(404, "span source not found")
    if not _claim_readable(role, src["label"] or "confidential"):
        raise HTTPException(403, "this citation is restricted for your role")
    # fail closed on the claim path too: a span is readable only when at least one claim
    # citing it is readable by this role (or nothing cites it yet and the source label allows)
    citing = db.claims_citing_span(span_id)
    if citing and not any(_claim_readable(role, c["label"] or "restricted") for c in citing):
        raise HTTPException(403, "this citation is restricted for your role")
    return {"id": span["id"], "locator": span["locator"], "text": span["text"],
            "sha256": span["text_sha256"], "source_label": src["label"], "source_name": src["name"],
            "captured_at": src["captured_at"], "redactions": json.loads(span["redactions"] or "[]")}


# ---------------------------------------------------------------- latest run & dropped list
@app.get("/api/projects/{project_id}/runs/latest")
def latest_run_report(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    r = db.latest_run(project_id)
    if r is None:
        return {"run": None, "counts": None}
    return {"run": {"id": r["id"], "extractor": r["extractor"], "model_id": r["model_id"],
                    "started_at": r["started_at"], "finished_at": r["finished_at"]},
            "counts": json.loads(r["counts"] or "{}")}


@app.get("/api/projects/{project_id}/dropped")
def dropped_list(project_id: str, x_tether_role: str | None = Header(default=None)):
    role = identity(x_tether_role)
    _role_guard(role, ("reviewer", "admin"))
    _project_or_404(project_id)
    r = db.latest_run(project_id)
    if r is None:
        return []
    out = []
    for c in db.list_candidates(r["id"]):
        if c["quote_found"] == 0 or c["drop_reason"]:
            payload = json.loads(c["payload"] or "{}")
            out.append({"id": c["id"], "drop_reason": c["drop_reason"],
                        "type": payload.get("type"), "text": payload.get("text"),
                        "quote": payload.get("quote"), "locator": payload.get("locator")})
    return out


# ---------------------------------------------------------------- static frontend + /judge
def _frontend_file(path: str):
    target = (FRONTEND / path).resolve()
    if target.is_file() and str(target).startswith(str(FRONTEND.resolve())):
        return target
    return None


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/judge")
def judge_page():
    return FileResponse(FRONTEND / "index.html")


@app.get("/{full_path:path}")
def spa(full_path: str):
    if full_path.startswith("api/") or full_path in ("docs", "openapi.json"):
        raise HTTPException(404, "not found")
    f = _frontend_file(full_path)
    if f is not None:
        media = {".js": "application/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}.get(f.suffix, "application/octet-stream")
        return FileResponse(f, media_type=media)
    return FileResponse(FRONTEND / "index.html")  # client-side route (e.g. /p/<id>/review)
