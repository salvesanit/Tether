# Accepted upload formats

Upload goes through one consent box (untickable-until-ticked); the tick is logged before any byte is stored. All formats are text; everything is stored with provenance, minus redactions.

| Kind | File | Shape | Notes |
|---|---|---|---|
| Repository | `.bundle` or `.zip` | a real git bundle (`git bundle create`) or a repository zip | read via `git`/`zipfile`; file contents split per file with `file:{path}#L{start}-{end}` locators; ~60 commits in the demo bundle |
| Issues | `issues.json` | GitHub REST list items `[{number, title, body, comments: [{id, body, user, created_at}], state}]` | locator `issue:{n}#c{k}` |
| Pull requests | `prs.json` | same shape, plus `merged_at` (merged ⇒ 0.95 cap, unmerged ⇒ 0.70) | locator `pr:{n}#c{k}` |
| Meeting notes | `notes/*.md` | Markdown; one paragraph per section | locator `file:notes/{name}.md#P{n}` |
| Chat export | `chat.json` | `{channel: [{ts, user, text}]}` Slack-style (as in the demo) | locator `chat:#{channel}@{ts}`; single message caps confidence at 0.60 |
| Labels & exclusions | `manifest.json` | `{sources: [{path, label}], exclude_channels: {chat.json: ["hr-leave","private-aarav"]}, exclude_reasons: {…}}` | what a person sets in the Connect screen; excluded channels are never read and show `not read` |

## Small examples

```json
// chat.json (trimmed)
{"general": [{"ts": "1760702400.006", "user": "aarav", "text": "Payments cutover happens on 2026-11-20."}]}
```

```json
// manifest.json (trimmed)
{"sources": [{"path": "notes/2026-10-02.md", "label": "restricted"}],
 "exclude_channels": {"chat.json": ["hr-leave", "private-aarav"]},
 "exclude_reasons": {"hr-leave": "HR channel — excluded by policy", "private-aarav": "private channel — not ours to read"}}
```

## Rejected

Empty files, unparseable JSON, unknown extensions and files over the upload ceiling return 400/413 with a plain sentence — never a stack trace, never partial ingestion (RD-2 covers the readers; the upload path is exercised by `scripts/seed.py` on every demo load).

Uploaded files land in `var/uploads/`; spans land in `tether.db` as locators + text (redacted) + SHA-256. The upload path is the only ingest path — the demo loads through it (no private route).
