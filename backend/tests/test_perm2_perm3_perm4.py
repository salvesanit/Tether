# PERM-2 — Unsigned versions 403 for every unsigned version.
# PERM-3 — Weakest source (HR-2): a claim backed by an open and a restricted source is restricted.
# PERM-4 — One read path: every SQL statement lives in db/read_path.py.
import os
import re
import tempfile
from pathlib import Path

from backend.app.db import read_path as db
from backend.app.pipeline import run as pipeline_run
from backend.app.storage import save_upload

ROOT = Path(__file__).resolve().parents[2]


def test_perm2_unsigned_version_403_for_everyone(built, client):
    pid = built["project_id"]
    for role in ("successor", "leaver", "reviewer", "admin"):
        r = client.get(f"/api/projects/{pid}/versions/v9.9", headers={"X-Tether-Role": role})
        assert r.status_code in (403, 404), (role, r.status_code)
    # successor (and leaver) may not open the handover before signature either
    for role in ("successor", "leaver"):
        r = client.get(f"/api/projects/{pid}/handover", headers={"X-Tether-Role": role})
        assert r.status_code == 403


def test_perm3_weakest_source_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("TETHER_DB", str(tmp_path / "perm3.db"))
    monkeypatch.setenv("TETHER_DATA", str(tmp_path / "var"))
    db.init_db()
    sentence = "The database is PostgreSQL, chosen over MongoDB to keep table joins."
    project = db.create_project("PERM-3 — weakest source", "Aster")
    db.seed_users(project["id"])
    a = db.create_source(project["id"], "notes", "notes/open-copy.md", "internal", "pending", "")
    b = db.create_source(project["id"], "notes", "notes/restricted-copy.md", "restricted", "pending", "")
    save_upload(a["id"], "2026-08-12.md", sentence.encode())
    save_upload(b["id"], "2026-08-13.md", sentence.encode())
    db.set_project_state(project["id"], "labelled")
    pipeline_run.run_rebuild(project["id"], actor="pytest", role="reviewer")
    claims = [c for c in db.list_claims(project["id"]) if c["text"] == sentence]
    assert claims, "the merged claim was not built"
    for c in claims:
        assert c["label"] == "restricted", f"HR-2 violated: claim backed by restricted source is labelled {c['label']}"
        assert len(db.list_evidence(c["id"])) == 2


def test_perm4_sql_lives_only_in_read_path():
    offenders = []
    sql = re.compile(r"\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|DROP\s+TABLE|ALTER\s+TABLE)\b", re.I)
    for path in (ROOT / "backend/app").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if path.name == "read_path.py":
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            code = line.split("#", 1)[0]
            if sql.search(code):
                offenders.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:80]}")
    assert offenders == [], f"SQL outside db/read_path.py: {offenders}"
