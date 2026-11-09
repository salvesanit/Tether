# REV-1 — Gates: each skipped state returns 409 and writes a log row. Signing with an undecided conflict is refused with the reason.
import json

from backend.app.db import read_path as db


def _fresh_project(tmp_path, monkeypatch):
    monkeypatch.setenv("TETHER_DB", str(tmp_path / "rev1.db"))
    monkeypatch.setenv("TETHER_DATA", str(tmp_path / "var"))
    db.init_db()
    p = db.create_project("REV-1 — gates", "Aster")
    db.seed_users(p["id"])
    return p


def test_rev1_rebuild_refused_before_labels_with_log_row(tmp_path, monkeypatch, client):
    p = _fresh_project(tmp_path, monkeypatch)
    r = client.post(f"/api/projects/{p['id']}/runs", headers={"X-Tether-Role": "reviewer"})
    assert r.status_code == 409
    rows = db.list_log(100)
    assert any(row["action"] == "run.refused" for row in rows)


def test_rev1_sign_refused_before_review_with_log_row(tmp_path, monkeypatch, client):
    p = _fresh_project(tmp_path, monkeypatch)
    r = client.post(f"/api/projects/{p['id']}/versions/sign", headers={"X-Tether-Role": "reviewer"})
    assert r.status_code == 409
    rows = db.list_log(100)
    assert any(row["action"] == "sign.refused" for row in rows)


def test_rev1_share_refused_before_sign_with_log_row(tmp_path, monkeypatch, client):
    p = _fresh_project(tmp_path, monkeypatch)
    r = client.post(f"/api/projects/{p['id']}/share", headers={"X-Tether-Role": "reviewer"})
    assert r.status_code == 409
    rows = db.list_log(100)
    assert any(row["action"] == "share.refused" for row in rows)


def test_rev1_approve_with_open_conflict_is_refused(built, tmp_path, monkeypatch, client):
    """On the built project: an undecided conflict must refuse the signature with the reason."""
    pid = built["project_id"]
    open_conflicts = [c for c in db.list_conflicts(pid) if c["state"] == "open"]
    if not open_conflicts:  # someone may have decided them earlier in the session
        import pytest
        pytest.skip("no open conflicts left on the shared fixture")
    r = client.post(f"/api/projects/{pid}/versions/sign", headers={"X-Tether-Role": "reviewer"})
    assert r.status_code == 409
    body = r.json()
    flat = json.dumps(body)
    assert "gate2_conflicts" in flat or "conflict" in flat.lower()
    rows = db.list_log(1000)
    assert any(row["action"] == "sign.refused" for row in rows)


def test_rev1_leaver_cannot_sign(built, client):
    pid = built["project_id"]
    r = client.post(f"/api/projects/{pid}/versions/sign", headers={"X-Tether-Role": "leaver"})
    assert r.status_code == 403
