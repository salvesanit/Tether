# One read/write path for the whole app — every SQL statement lives in this module (test PERM-4).
import json
import os
import sqlite3
from pathlib import Path

from ..util import new_id, now_iso, sha256_text
from .. import config

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "db" / "migrations" / "001_init.sql"


def db_path() -> str:
    return os.environ.get("TETHER_DB", str(Path(__file__).resolve().parents[3] / "tether.db"))


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row):
    return dict(row) if row is not None else None


# ---------------------------------------------------------------- projects
def create_project(name: str, codename: str = "Aster") -> dict:
    pid = new_id("p")
    with get_conn() as c:
        c.execute(
            "INSERT INTO projects(id,name,codename,state,retention_days,created_at) VALUES (?,?,?,?,?,?)",
            (pid, name, codename, "scoped", 30, now_iso()),
        )
    return get_project(pid)


def get_project(project_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone())


def list_projects() -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()]


def set_project_state(project_id: str, state: str) -> None:
    assert state in config.PROJECT_STATES
    with get_conn() as c:
        c.execute("UPDATE projects SET state=? WHERE id=?", (state, project_id))


def set_retention(project_id: str, days: int) -> None:
    with get_conn() as c:
        c.execute("UPDATE projects SET retention_days=? WHERE id=?", (int(days), project_id))


def delete_project(project_id: str) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM projects WHERE id=?", (project_id,))


# ---------------------------------------------------------------- users (demo identities)
DEMO_USERS = [
    ("Aarav Mehta", "aaravm", "leaver"),
    ("Sanit Salve", "sanit-s", "reviewer"),
    ("Diya Raman", "diyar", "successor"),
    ("Krushna Patil", "krushnap", "admin"),
]


def seed_users(project_id: str) -> None:
    with get_conn() as c:
        for name, gh, role in DEMO_USERS:
            c.execute(
                "INSERT INTO users(id,project_id,name,github,role) VALUES (?,?,?,?,?)",
                (new_id("u"), project_id, name, gh, role),
            )


def list_users(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM users WHERE project_id=?", (project_id,)).fetchall()]


def user_by_role(project_id: str, role: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM users WHERE project_id=? AND role=?", (project_id, role)).fetchone())


def user_by_id(user_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone())


# ---------------------------------------------------------------- sources & spans
def create_source(project_id: str, kind: str, name: str, label, read_state: str, sha256: str, not_read_reason=None, excluded_channels=()) -> dict:
    sid = new_id("src")
    with get_conn() as c:
        c.execute(
            "INSERT INTO sources(id,project_id,kind,name,label,read_state,not_read_reason,excluded_channels,sha256,captured_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sid, project_id, kind, name, label, read_state, not_read_reason, json.dumps(list(excluded_channels)), sha256, now_iso()),
        )
    return get_source(sid)


def get_source(source_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone())


def list_sources(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM sources WHERE project_id=? ORDER BY kind,name", (project_id,)).fetchall()]


def set_source_excluded_channels(source_id: str, channels: list) -> None:
    with get_conn() as c:
        c.execute("UPDATE sources SET excluded_channels=? WHERE id=?", (json.dumps(list(channels)), source_id))


def set_source_label(source_id: str, label) -> None:
    with get_conn() as c:
        c.execute("UPDATE sources SET label=? WHERE id=?", (label, source_id))


def set_source_read(source_id: str, read_state: str, reason=None) -> None:
    with get_conn() as c:
        c.execute("UPDATE sources SET read_state=?, not_read_reason=? WHERE id=?", (read_state, reason, source_id))


def insert_span(source_id: str, locator: str, text: str, redactions: list) -> dict:
    sid = new_id("span")
    with get_conn() as c:
        c.execute(
            "INSERT INTO spans(id,source_id,locator,text,text_sha256,redactions) VALUES (?,?,?,?,?,?)",
            (sid, source_id, locator, text, sha256_text(text), json.dumps(redactions)),
        )
    return get_span(sid)


def get_span(span_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM spans WHERE id=?", (span_id,)).fetchone())


def get_span_by_locator(project_id: str, locator: str):
    with get_conn() as c:
        row = c.execute(
            "SELECT spans.* FROM spans JOIN sources ON sources.id=spans.source_id WHERE sources.project_id=? AND spans.locator=?",
            (project_id, locator),
        ).fetchone()
        return _row_to_dict(row)


def list_spans(project_id: str, source_id=None) -> list:
    q = "SELECT spans.* FROM spans JOIN sources ON sources.id=spans.source_id WHERE sources.project_id=?"
    args = [project_id]
    if source_id:
        q += " AND spans.source_id=?"
        args.append(source_id)
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute(q, args).fetchall()]


def redaction_total(project_id: str) -> int:
    total = 0
    for s in list_spans(project_id):
        total += sum(int(r.get("count", 1)) for r in json.loads(s.get("redactions") or "[]"))
    return total


# ---------------------------------------------------------------- runs
def create_run(project_id: str, extractor: str, model_id, prompt_version, params: dict) -> dict:
    rid = new_id("run")
    with get_conn() as c:
        c.execute(
            "INSERT INTO runs(id,project_id,extractor,model_id,prompt_version,params,started_at,counts) VALUES (?,?,?,?,?,?,?,?)",
            (rid, project_id, extractor, model_id, prompt_version, json.dumps(params), now_iso(), "{}"),
        )
    return get_run(rid)


def finish_run(run_id: str, counts: dict) -> None:
    with get_conn() as c:
        c.execute("UPDATE runs SET finished_at=?, counts=? WHERE id=?", (now_iso(), json.dumps(counts), run_id))


def get_run(run_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone())


def latest_run(project_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM runs WHERE project_id=? ORDER BY started_at DESC LIMIT 1", (project_id,)).fetchone())


def insert_candidate(run_id: str, span_id, payload: dict, quote_found, drop_reason) -> None:
    with get_conn() as c:
        c.execute(
            "INSERT INTO candidates(id,run_id,span_id,payload,quote_found,drop_reason) VALUES (?,?,?,?,?,?)",
            (new_id("cand"), run_id, span_id, json.dumps(payload), quote_found, drop_reason),
        )


def list_candidates(run_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM candidates WHERE run_id=?", (run_id,)).fetchall()]


# ---------------------------------------------------------------- claims & evidence
def insert_claim(project_id: str, run_id, claim: dict, label: str, status: str) -> dict:
    cid = new_id("claim")
    with get_conn() as c:
        c.execute(
            """INSERT INTO claims(id,project_id,run_id,type,text,subject,attribute,value,reason,rejected_options,
                                   confidence,confidence_rule,status,label,gap_subject,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                cid, project_id, run_id, claim["type"], claim["text"],
                claim.get("subject"), claim.get("attribute"), claim.get("value"),
                claim.get("reason"), json.dumps(claim.get("rejected_options", [])),
                claim["confidence"], claim["confidence_rule"], status, label,
                claim.get("gap_subject"), now_iso(),
            ),
        )
    return get_claim(cid)


def get_claim(claim_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM claims WHERE id=?", (claim_id,)).fetchone())


def list_claims(project_id: str, status=None, ctype=None, review_state=None, label_in=None) -> list:
    q = "SELECT * FROM claims WHERE project_id=?"
    args = [project_id]
    if status:
        q += " AND status=?"
        args.append(status)
    if ctype:
        q += " AND type=?"
        args.append(ctype)
    if review_state:
        q += " AND review_state=?"
        args.append(review_state)
    if label_in:
        q += " AND label IN (%s)" % ",".join("?" * len(label_in))
        args.extend(label_in)
    q += " ORDER BY created_at, id"
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute(q, args).fetchall()]


def delete_pipeline_output(project_id: str) -> None:
    """Re-running a rebuild replaces prior spans/claims/conflicts/gaps/quarantine for the project."""
    with get_conn() as c:
        c.execute("DELETE FROM evidence WHERE claim_id IN (SELECT id FROM claims WHERE project_id=?)", (project_id,))
        c.execute("DELETE FROM conflict_claims WHERE conflict_id IN (SELECT id FROM conflicts WHERE project_id=?)", (project_id,))
        c.execute("DELETE FROM candidates WHERE run_id IN (SELECT id FROM runs WHERE project_id=?)", (project_id,))
        c.execute("DELETE FROM claims WHERE project_id=?", (project_id,))
        c.execute("DELETE FROM conflicts WHERE project_id=?", (project_id,))
        c.execute("DELETE FROM gaps WHERE project_id=?", (project_id,))
        c.execute("DELETE FROM quarantine WHERE project_id=?", (project_id,))
        c.execute("DELETE FROM spans WHERE source_id IN (SELECT id FROM sources WHERE project_id=?)", (project_id,))


def set_claim_status(claim_id: str, status: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE claims SET status=? WHERE id=?", (status, claim_id))


def set_claim_gap_subject(claim_id: str, gap_subject) -> None:
    with get_conn() as c:
        c.execute("UPDATE claims SET gap_subject=? WHERE id=?", (gap_subject, claim_id))


def set_claim_risk(claim_id: str, estimate: float, rule: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE claims SET risk_estimate=?, risk_rule=? WHERE id=?", (estimate, rule, claim_id))


def set_claim_label(claim_id: str, label: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE claims SET label=? WHERE id=?", (label, claim_id))


def delete_claim(claim_id: str) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM claims WHERE id=?", (claim_id,))


def update_claim_fields(claim_id: str, **fields) -> None:
    if not fields:
        return
    cols = ", ".join(f"{k}=?" for k in fields)
    with get_conn() as c:
        c.execute(f"UPDATE claims SET {cols} WHERE id=?", (*fields.values(), claim_id))


def merge_claims(keep_id: str, drop_id: str) -> None:
    """Fold duplicate claim `drop_id` into `keep_id`: union evidence, weakest label wins."""
    keep, drop = get_claim(keep_id), get_claim(drop_id)
    weakest = keep["label"] if config.LABEL_RANK[keep["label"]] >= config.LABEL_RANK[drop["label"]] else drop["label"]
    with get_conn() as c:
        c.execute("UPDATE evidence SET claim_id=? WHERE claim_id=?", (keep_id, drop_id))
        c.execute("UPDATE claims SET label=? WHERE id=?", (weakest, keep_id))
        c.execute("DELETE FROM claims WHERE id=?", (drop_id,))


def insert_evidence(claim_id: str, span_id: str, quote: str, locator: str, source_label) -> dict:
    eid = new_id("ev")
    with get_conn() as c:
        c.execute(
            "INSERT INTO evidence(id,claim_id,span_id,quote,locator,captured_at,source_label) VALUES (?,?,?,?,?,?,?)",
            (eid, claim_id, span_id, quote, locator, now_iso(), source_label),
        )
    return eid


def list_evidence(claim_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM evidence WHERE claim_id=?", (claim_id,)).fetchall()]


def evidence_by_ids(claim_ids: list) -> dict:
    if not claim_ids:
        return {}
    q = "SELECT * FROM evidence WHERE claim_id IN (%s)" % ",".join("?" * len(claim_ids))
    out = {cid: [] for cid in claim_ids}
    with get_conn() as c:
        for r in c.execute(q, claim_ids).fetchall():
            out[r["claim_id"]].append(_row_to_dict(r))
    return out


# ---------------------------------------------------------------- conflicts
def insert_conflict(project_id: str, subject: str, attribute: str, claim_ids: list) -> dict:
    xid = new_id("conflict")
    with get_conn() as c:
        c.execute(
            "INSERT INTO conflicts(id,project_id,subject,attribute,state) VALUES (?,?,?,?,?)",
            (xid, project_id, subject, attribute, "open"),
        )
        for cid in claim_ids:
            c.execute("INSERT OR IGNORE INTO conflict_claims(conflict_id,claim_id) VALUES (?,?)", (xid, cid))
    return get_conflict(xid)


def get_conflict(conflict_id: str):
    with get_conn() as c:
        row = _row_to_dict(c.execute("SELECT * FROM conflicts WHERE id=?", (conflict_id,)).fetchone())
        if row:
            row["claims"] = [_row_to_dict(r) for r in c.execute(
                "SELECT claims.* FROM claims JOIN conflict_claims ON conflict_claims.claim_id=claims.id WHERE conflict_claims.conflict_id=?",
                (conflict_id,)).fetchall()]
        return row


def list_conflicts(project_id: str, state=None) -> list:
    q = "SELECT * FROM conflicts WHERE project_id=?"
    args = [project_id]
    if state:
        q += " AND state=?"
        args.append(state)
    q += " ORDER BY subject, attribute"
    with get_conn() as c:
        rows = [_row_to_dict(r) for r in c.execute(q, args).fetchall()]
    return [get_conflict(r["id"]) for r in rows]


def decide_conflict(conflict_id: str, value: str, by: str, reason: str) -> None:
    with get_conn() as c:
        c.execute(
            "UPDATE conflicts SET state='decided', decided_value=?, decided_by=?, reason=? WHERE id=?",
            (value, by, reason, conflict_id),
        )


def park_conflict(conflict_id: str, by: str, reason: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE conflicts SET state='parked', decided_by=?, reason=? WHERE id=?", (by, reason, conflict_id))


# ---------------------------------------------------------------- gaps
def insert_gap(project_id: str, subject: str, question: str, owner, next_step, state="open") -> dict:
    gid = new_id("gap")
    with get_conn() as c:
        c.execute(
            "INSERT INTO gaps(id,project_id,subject,question,owner,next_step,state) VALUES (?,?,?,?,?,?,?)",
            (gid, project_id, subject, question, owner, next_step, state),
        )
    return get_gap(gid)


def get_gap(gap_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM gaps WHERE id=?", (gap_id,)).fetchone())


def list_gaps(project_id: str, state=None) -> list:
    q = "SELECT * FROM gaps WHERE project_id=?"
    args = [project_id]
    if state:
        q += " AND state=?"
        args.append(state)
    else:
        q += " AND state != 'suggested'"
    q += " ORDER BY subject"
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute(q, args).fetchall()]


def list_suggested_gaps(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM gaps WHERE project_id=? AND state='suggested'", (project_id,)).fetchall()]


def assign_gap(gap_id: str, owner: str, next_step: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE gaps SET owner=?, next_step=?, state='closed' WHERE id=?", (owner, next_step, gap_id))


def park_gap(gap_id: str, reason: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE gaps SET state='parked', parked_reason=? WHERE id=?", (reason, gap_id))


# ---------------------------------------------------------------- quarantine
def insert_quarantine(project_id: str, source_id: str, span_id, reason: str, excerpt: str) -> None:
    with get_conn() as c:
        c.execute(
            "INSERT INTO quarantine(id,project_id,source_id,span_id,reason,excerpt) VALUES (?,?,?,?,?,?)",
            (new_id("quar"), project_id, source_id, span_id, reason, excerpt),
        )


def list_quarantine(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM quarantine WHERE project_id=? ORDER BY id", (project_id,)).fetchall()]


def act_quarantine(quar_id: str, action: str, actor: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE quarantine SET action=?, acted_by=?, acted_at=? WHERE id=?", (action, actor, now_iso(), quar_id))


# ---------------------------------------------------------------- reviews (audit trail of person actions)
def insert_review(project_id: str, target_type: str, target_id: str, actor: str, action: str, before, after, reason) -> None:
    with get_conn() as c:
        c.execute(
            "INSERT INTO reviews(id,project_id,target_type,target_id,actor,action,before,after,reason,at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (new_id("rev"), project_id, target_type, target_id, actor, action,
             json.dumps(before) if isinstance(before, (dict, list)) else before,
             json.dumps(after) if isinstance(after, (dict, list)) else after,
             reason, now_iso()),
        )


def list_reviews(project_id: str, target_id=None) -> list:
    q = "SELECT * FROM reviews WHERE project_id=?"
    args = [project_id]
    if target_id:
        q += " AND target_id=?"
        args.append(target_id)
    q += " ORDER BY at, id"
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute(q, args).fetchall()]


# ---------------------------------------------------------------- versions & receipts
def create_version(project_id: str, number: str, payload: dict, sha256: str, signed_by: str) -> dict:
    vid = new_id("ver")
    with get_conn() as c:
        c.execute(
            "INSERT INTO versions(id,project_id,number,state,payload,sha256,signed_by,signed_at) VALUES (?,?,?,?,?,?,?,?)",
            (vid, project_id, number, "signed", json.dumps(payload), sha256, signed_by, now_iso()),
        )
    return get_version(vid)


def get_version(version_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM versions WHERE id=?", (version_id,)).fetchone())


def latest_signed_version(project_id: str):
    with get_conn() as c:
        return _row_to_dict(c.execute("SELECT * FROM versions WHERE project_id=? ORDER BY signed_at DESC LIMIT 1", (project_id,)).fetchone())


def list_versions(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM versions WHERE project_id=? ORDER BY signed_at", (project_id,)).fetchall()]


def create_receipt(version_id: str, user_id: str) -> None:
    with get_conn() as c:
        c.execute("INSERT OR IGNORE INTO receipts(id,version_id,user_id,at) VALUES (?,?,?,?)", (new_id("rcpt"), version_id, user_id, now_iso()))


def receipt_exists(version_id: str, user_id: str) -> bool:
    with get_conn() as c:
        return c.execute("SELECT 1 FROM receipts WHERE version_id=? AND user_id=?", (version_id, user_id)).fetchone() is not None


# ---------------------------------------------------------------- audit log (append-only, hash chained)
def append_log(actor: str, role: str, action: str, obj, detail) -> dict:
    with get_conn() as c:
        last = c.execute("SELECT hash FROM log ORDER BY id DESC LIMIT 1").fetchone()
        prev_hash = last["hash"] if last else "0" * 64
        at = now_iso()
        detail_s = detail if isinstance(detail, str) else json.dumps(detail, sort_keys=True)
        material = "|".join([prev_hash, at, actor, role, action, str(obj), detail_s])
        h = sha256_text(material)
        c.execute(
            "INSERT INTO log(at,actor,role,action,object,detail,prev_hash,hash) VALUES (?,?,?,?,?,?,?,?)",
            (at, actor, role, action, str(obj), detail_s, prev_hash, h),
        )
    return {"hash": h, "prev_hash": prev_hash, "at": at}


def list_log(limit: int = 500, offset: int = 0) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM log ORDER BY id LIMIT ? OFFSET ?", (limit, offset)).fetchall()]


def verify_log_chain() -> dict:
    with get_conn() as c:
        rows = [_row_to_dict(r) for r in c.execute("SELECT * FROM log ORDER BY id").fetchall()]
    prev = "0" * 64
    for r in rows:
        material = "|".join([prev, r["at"], r["actor"], r["role"], r["action"], str(r["object"]), r["detail"]])
        if sha256_text(material) != r["hash"] or r["prev_hash"] != prev:
            return {"ok": False, "broken_at": r["id"], "rows": len(rows)}
        prev = r["hash"]
    return {"ok": True, "rows": len(rows), "head": prev}


# ---------------------------------------------------------------- retention & admin
def insert_retention_request(project_id: str, requestor: str, detail: str) -> None:
    with get_conn() as c:
        c.execute(
            "INSERT INTO retention_requests(id,project_id,requestor,at,detail) VALUES (?,?,?,?,?)",
            (new_id("del"), project_id, requestor, now_iso(), detail),
        )


def list_retention_requests(project_id: str) -> list:
    with get_conn() as c:
        return [_row_to_dict(r) for r in c.execute("SELECT * FROM retention_requests WHERE project_id=?", (project_id,)).fetchall()]
