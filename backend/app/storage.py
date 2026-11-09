# One-line purpose: where source bytes are kept between upload and rebuild. Never committed to git.
import os
import re
from pathlib import Path


def data_dir() -> Path:
    d = Path(os.environ.get("TETHER_DATA", str(Path(__file__).resolve().parents[2] / "var")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def uploads_dir(source_id: str) -> Path:
    d = data_dir() / "uploads" / source_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name) or "source.bin"


def save_upload(source_id: str, filename: str, data: bytes) -> Path:
    path = uploads_dir(source_id) / safe_name(filename)
    path.write_bytes(data)
    return path


def find_upload(source_id: str) -> Path | None:
    d = uploads_dir(source_id)
    files = [p for p in d.iterdir() if p.is_file()]
    return files[0] if files else None
