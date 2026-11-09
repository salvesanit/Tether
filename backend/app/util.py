# One-line purpose: small shared helpers — ids, hashing, timestamps.
import hashlib
import secrets
from datetime import datetime, timezone


def new_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(8)}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def file_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
