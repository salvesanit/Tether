# One-line purpose: the six-step rebuild — read → clean → pull → check → group → queue. The machine proposes; people decide.
import json
import time

from .. import config
from ..checks import ck1_quote, ck2_caps, ck3_conflicts, ck4_gaps, risk
from ..db import read_path as db
from ..llm import adapter
from ..llm.rules_extractor import ceiling_for
from ..pipeline.clean import redact, injection_hits
from ..readers import readers
from ..storage import find_upload
from ..policy.labels import weakest_label


def _spans_for_source(source: dict):
    """Read one source into raw chunks. Excluded channels never reach here."""
    path = find_upload(source["id"])
    if path is None:
        return [], {"missing": True}
    raw = path.read_bytes()
    kind, name = source["kind"], source["name"]
    try:
        if kind == "repo":
            stats = readers.git_module_stats(str(path))
            return readers.read_git_bundle(str(path), name), {"module_stats": stats}
        if kind == "notes":
            return readers.read_notes(name, raw.decode("utf-8", "replace")), {}
        if kind == "chat":
            try:
                excluded = json.loads(source.get("excluded_channels") or "[]")
            except Exception:
                excluded = []
            return readers.read_chat_export(name, raw, excluded), {}
        if kind == "issues":
            return readers.read_issues(name, raw), {}
        if kind == "prs":
            return readers.read_prs(name, raw), {}
        return [], {"missing": True, "error": f"unknown source kind {kind}"}
    except readers.SourceError as e:
        return [], {"error": str(e)}


def run_rebuild(project_id: str, excluded_channels=None, actor: str = "system", role: str = "system") -> dict:
    # excluded_channels accepted for backwards compatibility; the authority is sources.excluded_channels
    started = time.time()
    project = db.get_project(project_id)
    if project is None:
        raise KeyError("project not found")
    if project["state"] not in ("labelled", "rebuilt", "in review"):
        raise PermissionError(f"project is {project['state']}; labels must be cleared before a rebuild")

    steps, warnings = [], []
    db.delete_pipeline_output(project_id)
    sources = db.list_sources(project_id)
    not_read = [{"name": s["name"], "reason": s["not_read_reason"] or "excluded"} for s in sources if s["read_state"] == "not read"]

    # Step 1+2 — read, cut, clean. Redact before anything is stored. Quarantine instruction-like text.
    t = time.time()
    stored_spans = []
    module_stats = {}
    source_errors = []
    for src in sources:
        if src["read_state"] == "not read":
            continue
        if src["label"] is None:
            raise PermissionError(f"source {src['name']} has no label; clear the labels first")
        chunks, meta = _spans_for_source(src)
        if meta.get("error"):
            source_errors.append(meta["error"])
            warnings.append(f"{src['name']}: {meta['error']}")
            continue
        if meta.get("module_stats"):
            module_stats.update(meta["module_stats"])
        for ch in chunks:
            hits = injection_hits(ch["text"])
            text_r, redactions = redact(ch["text"])
            if hits:
                db.insert_quarantine(project_id, src["id"], None,
                                     f"instruction-like text: {', '.join(hits[:2])}",
                                     text_r[:400])
                continue  # never stored as quotable evidence
            span = db.insert_span(src["id"], ch["locator"], text_r, redactions)
            span["ceiling_kind"] = ch.get("ceiling", "file")
            span["source_kind"] = src["kind"]
            span["source_label"] = src["label"]
            stored_spans.append(span)
    steps.append({"step": "read & clean", "detail": f"{len(stored_spans)} spans from {sum(1 for s in sources if s['read_state'] != 'not read')} sources", "ms": int((time.time() - t) * 1000)})

    # Step 3 — pull claims (model may only propose; quotes travel with each candidate).
    t = time.time()
    run = db.create_run(project_id, extractor="rules", model_id=None, prompt_version=config.PROMPT_VERSION,
                        params={"llm_mode": adapter.llm_mode()})
    candidates = []
    extractor_counts = {"rules": 0, "replay": 0, "live": 0}
    for span in stored_spans:
        ceiling = ceiling_for(span["ceiling_kind"])
        cands, used = adapter.extract_claims(span["text"], span["ceiling_kind"], ceiling, span["locator"])
        extractor_counts[used] = extractor_counts.get(used, 0) + 1
        for cand in cands:
            cand["locator"] = span["locator"]
            cand["ceiling_kind"] = span["ceiling_kind"]
            candidates.append((span, cand))
    steps.append({"step": "pull claims", "detail": f"{len(candidates)} candidates", "ms": int((time.time() - t) * 1000)})

    # Step 4 — CK-1 quote check + CK-2 caps.
    t = time.time()
    kept, dropped = [], []
    for span, cand in candidates:
        ok = ck1_quote.check_quote(span["text"], cand.get("quote", "")) and ck1_quote.check_locator_format(cand.get("locator", ""))
        if not ok:
            reason = "quote_not_found" if not ck1_quote.check_quote(span["text"], cand.get("quote", "")) else "bad_locator"
            dropped.append({**cand, "drop_reason": reason})
            db.insert_candidate(run["id"], span["id"], cand, 0, reason)
            continue
        db.insert_candidate(run["id"], span["id"], cand, 1, None)
        raw = float(cand.get("confidence", 0.9))
        ceiling = ceiling_for(cand.get("ceiling_kind", "file"))
        conf, rule = ck2_caps.cap(raw, cand.get("ceiling_kind", "file"), ceiling)
        cand["confidence"], cand["confidence_rule"] = conf, rule
        cand["_span"] = span
        kept.append(cand)
    steps.append({"step": "check (quote, caps)", "detail": f"{len(kept)} kept · {len(dropped)} dropped", "ms": int((time.time() - t) * 1000)})

    # Step 5 — dedupe (identical fact from two sources keeps both evidences, weakest label wins), then keep claims.
    t = time.time()
    merged = {}
    for cand in kept:
        key = (cand["type"], (cand.get("subject") or "").lower(), (cand.get("attribute") or "").lower(),
               (cand.get("value_norm") or "").lower(), " ".join(cand["text"].lower().split()))
        merged.setdefault(key, []).append(cand)

    claim_rows = []
    for key, group in merged.items():
        first = group[0]
        label = weakest_label([g["_span"]["source_label"] for g in group])
        conf = min(g["confidence"] for g in group)
        rule = group[0]["confidence_rule"]
        status = "verified" if conf >= config.CONFIDENCE_VERIFIED_FLOOR else "uncertain"
        claim = {
            "type": first["type"], "text": first["text"],
            "subject": first.get("subject"), "attribute": first.get("attribute"),
            "value": first.get("value"), "rejected_options": first.get("rejected_options", []),
            "confidence": conf, "confidence_rule": rule,
            "gap_subject": first.get("gap_subject"), "has_issue_ref": first.get("has_issue_ref", False),
        }
        row = db.insert_claim(project_id, run["id"], claim, label, status)
        for g in group:
            db.insert_evidence(row["id"], g["_span"]["id"], g["quote"], g["locator"], g["_span"]["source_label"])
        claim_rows.append(row)
    steps.append({"step": "group", "detail": f"{len(claim_rows)} claims from {len(kept)} quotes", "ms": int((time.time() - t) * 1000)})

    # Step 5b — CK-3 conflicts (same subject+attribute, different values). The code never picks a winner.
    t = time.time()
    by_key = {}
    for r in claim_rows:
        if r.get("subject") and r.get("attribute") and r.get("value"):
            by_key.setdefault((ck3_conflicts.norm(r["subject"]), ck3_conflicts.norm(r["attribute"])), []).append(r)
    conflicts = {k: v for k, v in by_key.items() if len({ck3_conflicts.norm(c["value"]) for c in v}) > 1}
    conflict_claim_ids = set()
    for (subj, attr), group in conflicts.items():
        c = db.insert_conflict(project_id, subj, attr, [r["id"] for r in group])
        for r in group:
            db.set_claim_status(r["id"], "conflicting")
            conflict_claim_ids.add(r["id"])
    steps.append({"step": "conflicts", "detail": f"{len(conflicts)} open", "ms": int((time.time() - t) * 1000)})

    # Step 6 — CK-4 gaps; module concentration for risk; risk estimate; fill the queue.
    t = time.time()
    covered = {r.get("gap_subject") for r in claim_rows if r.get("gap_subject")}
    missing = ck4_gaps.missing_subjects(covered)
    for subject in missing:
        row = ck4_gaps.gap_row(subject)
        db.insert_gap(project_id, row["subject"], row["question"], row["owner"], row["next_step"], "open")
    db.insert_gap(project_id, "analytics and privacy",
                  "Which metrics may we collect, and what does the consent notice say?",
                  "Aarav Mehta (leaver)", "Write the one-page data-notice before the season starts.", "suggested")

    open_gap_subjects = set(missing)
    import re as _re
    for r in claim_rows:
        ev_quotes = " ".join(e["quote"] for e in db.list_evidence(r["id"]))
        r["has_issue_ref"] = bool(_re.search(r"#\d+", f"{r['text']} {ev_quotes}"))
        conc = module_stats.get(_module_of(r), 0.0)
        r_est, rule = risk.estimate(
            r, conc,
            has_open_conflict=r["id"] in conflict_claim_ids,
            gap_is_open=(r.get("gap_subject") in open_gap_subjects),
        )
        db.set_claim_risk(r["id"], r_est, rule)
    steps.append({"step": "fill the queue", "detail": f"{len(missing)} gaps, risk order set", "ms": int((time.time() - t) * 1000)})

    # Finish the run record — honest extractor accounting. Never label handwritten files as model output.
    used = "rules" if extractor_counts["rules"] else ("replay" if extractor_counts["replay"] else "live")
    if extractor_counts["rules"] and (extractor_counts["replay"] or extractor_counts["live"]):
        used = "mixed"
    duration_ms = int((time.time() - started) * 1000)
    counts = {
        "spans": len(stored_spans),
        "candidates": len(candidates),
        "kept": len(claim_rows),
        "dropped": len(dropped),
        "dropped_by_reason": _count_by(dropped, "drop_reason"),
        "conflicts": len(conflicts),
        "gaps": len(missing),
        "extractor": used,
        "extractor_chunks": extractor_counts,
        "model_id": None,
        "confidence_floor_kept": sum(1 for r in claim_rows if r["confidence"] >= config.CONFIDENCE_VERIFIED_FLOOR),
        "redactions": sum(sum(int(x.get("count", 1)) for x in _json_list(s.get("redactions"))) for s in [db.get_span(sp["id"]) for sp in stored_spans]) if stored_spans else 0,
        "quarantined": len(db.list_quarantine(project_id)),
        "source_errors": source_errors,
        "not_read_sources": not_read,
        "duration_ms": duration_ms,
        "steps": steps,
    }
    db.finish_run(run["id"], counts)
    db.set_project_state(project_id, "rebuilt")
    db.append_log(actor, role, "rebuild", project_id, counts)
    return {"run": db.get_run(run["id"]), "counts": counts, "steps": steps, "warnings": warnings}


def _json_list(s):
    import json
    try:
        return json.loads(s or "[]")
    except Exception:
        return []


def _count_by(rows, key):
    out = {}
    for r in rows:
        out[r.get(key, "unknown")] = out.get(r.get(key, "unknown"), 0) + 1
    return out


_MODULE_WORDS = ("payments", "notifications", "search")


def _module_of(claim) -> str:
    text = f"{claim.get('text', '')} {claim.get('subject', '')}".lower()
    for m in _MODULE_WORDS:
        if m in text:
            return m
    return ""
