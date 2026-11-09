# One-line purpose: readers turn raw source files into quotable spans with locators. One reader per source kind.
import json
import re
import subprocess
import tempfile
from pathlib import Path


class SourceError(Exception):
    """Plain, user-facing error for empty or malformed input."""


def _para_blocks(text: str):
    """Yield (start_line, end_line, block_text) for blocks separated by blank lines."""
    lines = text.splitlines()
    start = None
    buf = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            if start is None:
                start, buf = i, []
            buf.append(line)
        else:
            if start is not None:
                yield start, i - 1, "\n".join(buf)
                start, buf = None, []
    if start is not None:
        yield start, len(lines), "\n".join(buf)


def read_notes(rel_path: str, content: str) -> list:
    """Markdown notes: one span per paragraph, locator file:{path}#P{n} (and L{start}-{end} accepted)."""
    if not content.strip():
        raise SourceError(f"{rel_path}: file is empty")
    spans = []
    for n, block in enumerate(_para_blocks(content), 1):
        s0, s1, text = block
        spans.append({
            "locator": f"file:{rel_path}#P{n}",
            "line_locator": f"file:{rel_path}#L{s0}-{s1}",
            "text": text,
            "ceiling": "file",
        })
    if not spans:
        raise SourceError(f"{rel_path}: no paragraphs found")
    return spans


def read_code_file(rel_path: str, content: str) -> list:
    if not content.strip():
        raise SourceError(f"{rel_path}: file is empty")
    spans = []
    for s0, s1, text in _para_blocks(content):
        spans.append({
            "locator": f"file:{rel_path}#L{s0}-{s1}",
            "text": text,
            "ceiling": "file",
        })
    return spans


def read_git_bundle(bundle_path: str, rel_name: str = "repo.bundle") -> list:
    """Git bundle (or bare repo): commit messages as commit:{sha} spans, files at HEAD as L{start}-{end}."""
    if Path(bundle_path).stat().st_size == 0:
        raise SourceError(f"{rel_name}: bundle is empty")
    spans = []
    with tempfile.TemporaryDirectory(prefix="tether-repo-") as tmp:
        clone = Path(tmp) / "work"
        try:
            subprocess.run(["git", "clone", "--quiet", bundle_path, str(clone)],
                           check=True, capture_output=True, timeout=60)
        except subprocess.CalledProcessError as e:
            raise SourceError(f"{rel_name}: not a readable git bundle ({e.stderr.decode().strip()[:120]})")
        log = subprocess.run(
            ["git", "log", "--reverse", "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%B%x1e"],
            cwd=clone, check=True, capture_output=True, timeout=60,
        ).stdout.decode("utf-8", "replace")
        for rec in log.split("\x1e"):
            rec = rec.strip("\n")
            if not rec.strip():
                continue
            parts = rec.split("\x1f", 4)
            if len(parts) < 5:
                continue
            sha, author, email, date, body = parts
            text = f"{body.strip()}"
            if text:
                spans.append({
                    "locator": f"commit:{sha}",
                    "text": text,
                    "ceiling": "commit",
                    "meta": {"author": author, "email": email, "date": date},
                })
        files = subprocess.run(["git", "ls-files"], cwd=clone, check=True,
                               capture_output=True, timeout=60).stdout.decode().splitlines()
        text_ext = {".md", ".txt", ".js", ".ts", ".py", ".yml", ".yaml", ".env", ".json", ".sh", ".sql", ".html", ".css"}
        for rel in files:
            p = clone / rel
            if p.suffix.lower() not in text_ext or p.stat().st_size > 200_000:
                continue
            try:
                content = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if not content.strip():
                continue
            for s0, s1, text in _para_blocks(content):
                spans.append({
                    "locator": f"file:{rel}#L{s0}-{s1}",
                    "text": text,
                    "ceiling": "file",
                })
    return spans


def read_chat_export(rel_name: str, raw: bytes, excluded_channels: list) -> list:
    """Slack-style export: {channels: [{name, kind, messages: [{ts, user, text}]}]} or {channel: [messages]}."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise SourceError(f"{rel_name}: chat export is not valid JSON ({e})")
    if isinstance(data, dict) and "channels" in data:
        chans = data["channels"]
    elif isinstance(data, dict):
        chans = [{"name": k, "messages": v} for k, v in data.items()]
    else:
        raise SourceError(f"{rel_name}: unrecognised chat export shape (expected an object of channels)")
    excl = {c.lower().lstrip("#") for c in excluded_channels}
    spans = []
    for ch in chans:
        name = str(ch.get("name", "")).lstrip("#")
        if name.lower() in excl:
            continue  # excluded channels are dropped in memory and never stored
        msgs = ch.get("messages", [])
        if not isinstance(msgs, list):
            raise SourceError(f"{rel_name}: channel #{name} messages must be a list")
        for m in msgs:
            ts = str(m.get("ts", "")).strip()
            text = str(m.get("text", "")).strip()
            if not ts or not text:
                continue
            spans.append({
                "locator": f"chat:#{name}@{ts}",
                "text": text,
                "ceiling": "chat",
                "meta": {"user": m.get("user", ""), "channel": name},
            })
    if not spans:
        raise SourceError(f"{rel_name}: no readable messages (all channels excluded or empty)")
    return spans


def _items_iter(data, rel_name: str):
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        return data["items"]
    raise SourceError(f"{rel_name}: expected a JSON list (GitHub API shape)")


def read_issues(rel_name: str, raw: bytes) -> list:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise SourceError(f"{rel_name}: issues export is not valid JSON ({e})")
    spans = []
    for item in _items_iter(data, rel_name):
        if "number" not in item:
            raise SourceError(f"{rel_name}: an entry has no issue number")
        n = item["number"]
        title = str(item.get("title", "")).strip()
        body = str(item.get("body") or "").strip()
        if title or body:
            spans.append({
                "locator": f"issue:{n}#body",
                "text": (title + "\n\n" + body).strip(),
                "ceiling": "issue_comment",
                "meta": {"state": item.get("state")},
            })
        for k, c in enumerate(item.get("comments", []) or [], 1):
            ctext = str(c.get("body") or "").strip()
            if not ctext:
                continue
            spans.append({
                "locator": f"issue:{n}#c{k}",
                "text": ctext,
                "ceiling": "issue_comment",
                "meta": {"user": (c.get("user") or {}).get("login", "") if isinstance(c.get("user"), dict) else c.get("user", "")},
            })
    if not spans:
        raise SourceError(f"{rel_name}: no issues or comments found")
    return spans


def read_prs(rel_name: str, raw: bytes) -> list:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise SourceError(f"{rel_name}: PR export is not valid JSON ({e})")
    spans = []
    for item in _items_iter(data, rel_name):
        if "number" not in item:
            raise SourceError(f"{rel_name}: an entry has no pull request number")
        n = item["number"]
        merged = bool(item.get("merged_at") or item.get("merged"))
        title = str(item.get("title", "")).strip()
        body = str(item.get("body") or "").strip()
        if title or body:
            spans.append({
                "locator": f"pr:{n}#body",
                "text": (title + "\n\n" + body).strip(),
                "ceiling": "merged_pr" if merged else "unmerged_pr",
                "meta": {"merged": merged, "state": item.get("state")},
            })
        for k, c in enumerate(item.get("comments", []) or [], 1):
            ctext = str(c.get("body") or "").strip()
            if not ctext:
                continue
            spans.append({
                "locator": f"pr:{n}#c{k}",
                "text": ctext,
                "ceiling": "pr_comment",
                "meta": {"user": (c.get("user") or {}).get("login", "") if isinstance(c.get("user"), dict) else c.get("user", "")},
            })
    if not spans:
        raise SourceError(f"{rel_name}: no pull requests or comments found")
    return spans


def git_module_stats(bundle_path: str) -> dict:
    """Return {module: top-author ratio} for src/<module>/ in the bundle. Used only for the risk estimate."""
    stats = {}
    with tempfile.TemporaryDirectory(prefix="tether-stats-") as tmp:
        clone = Path(tmp) / "work"
        try:
            subprocess.run(["git", "clone", "--quiet", bundle_path, str(clone)],
                           check=True, capture_output=True, timeout=60)
        except subprocess.CalledProcessError:
            return {}
        log = subprocess.run(
            ["git", "log", "--format=%x1f%an", "--name-only"],
            cwd=clone, check=True, capture_output=True, timeout=60,
        ).stdout.decode("utf-8", "replace")
        module_authors = {}
        author = None
        for line in log.splitlines():
            if line.startswith("\x1f"):
                author = line[1:].strip()
                continue
            line = line.strip()
            if not line or author is None:
                continue
            parts = line.split("/")
            if len(parts) >= 2 and parts[0] == "src":
                module = parts[1].split(".")[0]
                module_authors.setdefault(module, {})[author] = module_authors.setdefault(module, {}).get(author, 0) + 1
        for module, counts in module_authors.items():
            total = sum(counts.values())
            stats[module] = max(counts.values()) / total if total else 0.0
    return stats


def sniff_json_kind(rel_name: str, raw: bytes) -> str:
    """Best-effort kind detection for judge uploads without a manifest."""
    try:
        data = json.loads(raw)
    except Exception:
        return "unknown"
    name = rel_name.lower()
    if isinstance(data, dict) and ("channels" in data or any(
        isinstance(v, list) and v and isinstance(v[0], dict) and "ts" in v[0] and "text" in v[0]
        for v in data.values()
    )):
        return "chat"
    if isinstance(data, list):
        if any(isinstance(i, dict) and (i.get("pull_request") or "merged_at" in i) for i in data):
            return "prs"
        if "pr" in name:
            return "prs"
        if "issue" in name:
            return "issues"
        if any(isinstance(i, dict) and "number" in i for i in data):
            return "issues"
    return "unknown"
