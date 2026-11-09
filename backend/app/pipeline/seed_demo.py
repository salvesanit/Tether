# One-line purpose: load the Aster demo project through the same upload path a judge uses.
import json
from pathlib import Path

from ..db import read_path as db
from ..pipeline import run as pipeline  # noqa: F401  (kept for parity with the app factory)
from ..storage import save_upload
from ..util import now_iso

DEMO_DIR = Path(__file__).resolve().parents[3] / "data" / "demo_project"


def load_demo_project(name=None, role="reviewer"):
    """Create a project and upload the demo sources via the shared service, exactly as POST /sources does."""
    manifest = json.loads((DEMO_DIR / "manifest.json").read_text())
    project = db.create_project(name or manifest["project"]["name"], manifest["project"].get("codename", "Aster"))
    db.seed_users(project["id"])
    excluded = manifest.get("excluded_channels", [])
    for s in manifest["sources"]:
        path = DEMO_DIR / s["path"]
        data = path.read_bytes()
        display_name = s["path"] if s["kind"] == "notes" else path.name
        src = db.create_source(project["id"], s["kind"], display_name, s["label"], "pending", s.get("sha256", ""),
                               excluded_channels=s.get("excluded_channels", []))
        save_upload(src["id"], path.name, data)
    for ch in manifest.get("excluded_channels", []):
        reason = manifest.get("exclude_reasons", {}).get(ch, "excluded — not read")
        db.create_source(project["id"], "chat", f"chat.json · #{ch}", None, "not read", "", reason)
    user = db.user_by_role(project["id"], role)
    actor = user["name"] if user else role
    db.append_log(actor, role, "consent.ticked", project["id"],
                  "demo project loaded through the upload path; consent from manifest")
    db.append_log(actor, role, "project.created", project["id"], {"name": project["name"], "sources": len(manifest["sources"])})
    return db.get_project(project["id"])
