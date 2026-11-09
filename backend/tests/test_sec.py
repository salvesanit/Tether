# SEC-1 — Honeytokens: neither token appears in the database, logs, exports, API responses or screens.
# SEC-2 — Secrets and personal data appear only as [REDACTED:type] or masked.
# SEC-3 — Injection: the planted note becomes a reviewer item and changes no status, label, role or gate.
import json
import sqlite3


def test_sec1_honeytokens_not_in_database_bytes(built, answer_key):
    import os
    raw = open(os.environ["TETHER_DB"], "rb").read()
    for token in answer_key["honeytokens"]:
        assert token.encode() not in raw, f"honeytoken persisted in the database file"


def test_sec1_honeytokens_not_in_api_or_exports(built, client):
    pid = built["project_id"]
    for role in ("reviewer", "admin", "successor", "leaver"):
        for path in (f"/api/projects/{pid}/claims", f"/api/projects/{pid}/export",
                     f"/api/projects/{pid}/log", f"/api/projects/{pid}/handover",
                     f"/api/projects/{pid}/sources", f"/api/projects/{pid}/runs/latest",
                     f"/api/projects/{pid}/dropped", f"/api/projects/{pid}/proposals"):
            r = client.get(path, headers={"X-Tether-Role": role})
            for token in ("HONEYPHRASE-KESTREL-7719", "HONEYPHRASE-MARLOWE-3308"):
                assert token not in r.text, f"honeytoken via {role} on {path}"


def test_sec1_honeytokens_not_in_frontend_bundle():
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    for f in (root / "frontend").rglob("*"):
        if f.is_file():
            body = f.read_bytes()
            for token in (b"HONEYPHRASE-KESTREL-7719", b"HONEYPHRASE-MARLOWE-3308"):
                assert token not in body, f"honeytoken in {f}"


def test_sec2_secrets_and_personal_data_redacted(built, answer_key):
    db = built["db"]
    all_text = "\n".join(s["text"] for s in db.list_spans(built["project_id"]))
    for secret in answer_key["secrets"]:
        assert secret not in all_text, f"secret survived redaction: {secret[:12]}…"
    for item in answer_key["personal_data"]:
        assert item not in all_text, f"personal data survived redaction: {item}"


def test_sec2_redaction_markers_present_and_counted(built):
    db = built["db"]
    total = db.redaction_total(built["project_id"])
    assert total >= 5, f"expected redactions recorded, got {total}"


def test_sec3_injection_becomes_reviewer_item_and_changes_nothing(built, client):
    pid = built["project_id"]
    quar = client.get(f"/api/projects/{pid}/quarantine", headers={"X-Tether-Role": "reviewer"}).json()
    assert quar, "the planted instruction-like span must be quarantined"
    injection = [q for q in quar if "instruction-like" in (q.get("reason") or "")]
    assert injection, "quarantine reason does not name instruction-like text"
    # statuses, labels and roles are untouched; gate report shows exactly the same verdicts
    gates = client.get(f"/api/projects/{pid}/gates", headers={"X-Tether-Role": "reviewer"}).json()
    assert gates["gate1_labels"]["ok"] is True
    claims = client.get(f"/api/projects/{pid}/claims", headers={"X-Tether-Role": "reviewer"}).json()
    assert all("HONEYPHRASE" not in c["text"] for c in claims)
    # acting on quarantine requires a reviewer decision and is logged
    qid = injection[0]["id"]
    r = client.post(f"/api/quarantine/{qid}/act", headers={"X-Tether-Role": "reviewer"},
                    json={"action": "confirmed", "note": "instruction-like text in a source"})
    assert r.status_code == 200
    log = client.get(f"/api/projects/{pid}/log", headers={"X-Tether-Role": "admin"}).json()["rows"]
    assert any("quarantine.confirmed" == row["action"] for row in log)
