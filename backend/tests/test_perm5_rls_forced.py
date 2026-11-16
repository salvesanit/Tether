"""PERM-5 — PostgreSQL forced RLS applies to the non-bypass application role."""
import json
import os

import pytest

from backend.app.db import read_path as db


pytestmark = pytest.mark.skipif(
    not os.environ.get("TETHER_DATABASE_URL"),
    reason="PERM-5 requires the PostgreSQL CI service (TETHER_DATABASE_URL)",
)


def test_perm5_postgres_role_context_and_forced_policies(built, client):
    protected = ("sources", "spans", "claims", "evidence", "versions", "log", "version_views")
    with db.role_context("successor"):
        with db.get_conn() as conn:
            current_role = conn.execute("SELECT current_setting('app.role', true)").fetchone()["current_setting"]
            principal = conn.execute(
                "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user"
            ).fetchone()
            states = conn.execute(
                "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
                "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname=current_schema() AND c.relname IN (?,?,?,?,?,?,?)",
                protected,
            ).fetchall()
            visible = conn.execute("SELECT count(*) AS n FROM claims").fetchone()["n"]
            blocked = conn.execute(
                "SELECT count(*) AS n FROM claims WHERE label IN ('restricted','confidential')"
            ).fetchone()["n"]
            hidden_sources = conn.execute(
                "SELECT count(*) AS n FROM sources WHERE label='confidential'"
            ).fetchone()["n"]
            hidden_logs = conn.execute("SELECT count(*) AS n FROM log").fetchone()["n"]

    assert current_role == "successor"
    assert principal == {"rolsuper": False, "rolbypassrls": False}
    assert {row["relname"] for row in states} == set(protected)
    assert all(row["relrowsecurity"] and row["relforcerowsecurity"] for row in states)
    assert visible > 0
    assert blocked == 0
    assert hidden_sources == 0
    assert hidden_logs == 0

    with db.role_context("reviewer"):
        with db.get_conn() as conn:
            unrestricted = conn.execute(
                "SELECT count(*) AS n FROM claims WHERE label IN ('restricted','confidential')"
            ).fetchone()["n"]
    assert unrestricted > 0

    project_id = built["project_id"]
    restricted_text = "RLS_PRIVATE_VERSION_SENTINEL"
    payload = {
        "items": [
            {"label": "open", "type": "decision", "text": "Visible handover fact", "risk_estimate": 1},
            {"label": "confidential", "type": "decision", "text": restricted_text, "risk_estimate": 1},
        ],
        "gaps": [],
    }
    version = db.create_version(project_id, "v1.0", payload, "a" * 64, "reviewer")
    db.set_project_state(project_id, "shared")

    with db.role_context("successor"):
        with db.get_conn() as conn:
            base_payload = conn.execute(
                "SELECT payload FROM versions WHERE id=?", (version["id"],)
            ).fetchone()["payload"]
            visible_views = conn.execute(
                "SELECT audience, payload FROM version_views WHERE version_id=?", (version["id"],)
            ).fetchall()
    assert base_payload == "{}"
    assert len(visible_views) == 1
    assert visible_views[0]["audience"] == "successor"
    assert restricted_text not in visible_views[0]["payload"]
    assert json.loads(visible_views[0]["payload"])["_hidden_items"] == 1

    response = client.get(
        f"/api/projects/{project_id}/versions/latest", headers={"X-Tether-Role": "successor"}
    )
    assert response.status_code == 200
    assert restricted_text not in response.text
    assert response.json()["restricted_notice"] == "Some information is restricted for your role."
