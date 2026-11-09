# PERM-1 — Leak test as the successor: every API route, direct IDs and exports. No restricted or confidential text appears.
import json

import pytest


def _needles(built, answer_key, client):
    """The strings that must never cross the successor's boundary."""
    db = built["db"]
    pid = built["project_id"]
    needles = list(answer_key["secrets"]) + list(answer_key["personal_data"]) + list(answer_key["honeytokens"])
    # confidential and restricted claim text + their evidence quotes (fetched as reviewer)
    r = client.get(f"/api/projects/{pid}/claims", headers={"X-Tether-Role": "reviewer"})
    for c in r.json():
        if c["label"] in ("restricted", "confidential"):
            needles.append(c["text"])
            needles.append(c["value"] or "")
            for e in c["evidence"]:
                if len(e["quote"]) >= 12:
                    needles.append(e["quote"])
    return [n for n in needles if n]


def test_perm1_successor_never_sees_restricted_or_confidential_text(built, answer_key, client):
    pid = built["project_id"]
    needles = _needles(built, answer_key, client)
    probes = [
        ("GET", "/api/projects"), ("GET", f"/api/projects/{pid}"),
        ("GET", f"/api/projects/{pid}/sources"), ("GET", f"/api/projects/{pid}/claims"),
        ("GET", f"/api/projects/{pid}/claims?status=verified"),
        ("GET", f"/api/projects/{pid}/conflicts"), ("GET", f"/api/projects/{pid}/gaps"),
        ("GET", f"/api/projects/{pid}/quarantine"), ("GET", f"/api/projects/{pid}/gates"),
        ("GET", f"/api/projects/{pid}/runs/latest"), ("GET", f"/api/projects/{pid}/dropped"),
        ("GET", f"/api/projects/{pid}/export"), ("GET", f"/api/projects/{pid}/log"),
        ("GET", f"/api/projects/{pid}/handover"),  # 403 before sign — fine, scanned anyway
    ]
    leaks = []
    for method, path in probes:
        r = client.get(path, headers={"X-Tether-Role": "successor"})
        body = r.text
        for n in needles:
            if n in body:
                leaks.append((path, n[:40]))
    # direct span IDs from restricted/confidential evidence (fetched as reviewer)
    db = built["db"]
    for c in db.list_claims(pid):
        if c["label"] in ("restricted", "confidential"):
            for e in db.list_evidence(c["id"]):
                r = client.get(f"/api/spans/{e['span_id']}", headers={"X-Tether-Role": "successor"})
                assert r.status_code == 403, f"successor read span for {c['label']} claim"
    assert leaks == [], f"restricted material reached the successor: {leaks}"


def test_perm1_leaver_never_sees_confidential(built, answer_key, client):
    pid = built["project_id"]
    db = built["db"]
    r = client.get(f"/api/projects/{pid}/claims", headers={"X-Tether-Role": "leaver"})
    assert r.status_code == 200
    assert all(c["label"] != "confidential" for c in r.json())
