#!/bin/sh
# Tether — the four-minute path, scripted end to end on a THROWAWAY database (DM-1 to DM-4).
# Rebuilds the synthetic demo, settles the queue through the real API, signs, shares,
# opens the successor's handover and confirms receipt. Never touches tether.db.
set -eu
cd "$(dirname "$0")/.."

WORK=$(mktemp -d /tmp/tether-walk.XXXXXX)
PORT="${PORT:-8124}"
export PORT TETHER_DB="$WORK/walk.db" TETHER_DATA="$WORK/var" LLM_MODE="${LLM_MODE:-replay}" DEMO_MODE=true
trap 'rc=$?; rm -rf "$WORK"; [ -n "${SRV:-}" ] && kill "$SRV" 2>/dev/null; exit $rc' EXIT HUP INT TERM

python3 scripts/seed.py > "$WORK/seed.log"
PID=$(grep 'Demo project loaded:' "$WORK/seed.log" | sed 's/.*: //')
API="http://127.0.0.1:$PORT"
P="$API/api/projects/$PID"
echo "DM-1 connect — project $PID loaded through the upload path (consent logged, manifest labels applied)"

python3 run.py > "$WORK/server.log" & SRV=$!
i=0; until curl -sf "$API/api/health" > /dev/null; do i=$((i+1)); [ $i -gt 60 ] && { echo "server did not start — see $WORK/server.log"; exit 1; }; sleep 0.5; done
say() { printf '  %s\n' "$1"; }

echo "== reviewer: clear the labels gate (Gate 1), then rebuild =="
curl -sf -X POST -H "X-Tether-Role: reviewer" "$P/gates/labels" > /dev/null && say "labels cleared → state=labelled"
curl -sf -X POST -H "X-Tether-Role: reviewer" "$P/runs" > "$WORK/run.json"
say "$(python3 -c "import json;c=json.load(open('$WORK/run.json'))['counts'];print('rebuilt: spans',c['spans'],'· candidates',c['candidates'],'· kept',c['kept'],'· dropped',c['dropped'],'· conflicts',c['conflicts'],'· gaps',c['gaps'])")"

echo "== DM-2 prove — open one citation, quote must appear at its locator =="
CHK=$(python3 - "$TETHER_DB" << 'PY'
import json, sqlite3, sys
con = sqlite3.connect(sys.argv[1]); con.row_factory = sqlite3.Row
row = con.execute("select span_id, quote from evidence order by rowid limit 1").fetchone()
span = con.execute("select text from spans where id=?", (row["span_id"],)).fetchone()
print(json.dumps({"span_id": row["span_id"], "quote_ok": row["quote"] in span["text"]}))
PY
)
SID=$(echo "$CHK" | python3 -c "import json,sys;print(json.load(sys.stdin)['span_id'])")
OK=$(echo "$CHK" | python3 -c "import json,sys;print(json.load(sys.stdin)['quote_ok'])")
curl -sf -H "X-Tether-Role: reviewer" "$API/api/spans/$SID" > /dev/null && say "citation resolves · quote found in span: $OK"

echo "== work the queue the review screen way (confirm claims · decide conflicts · assign gaps) =="
python3 - "$API" "$PID" << 'PY'
import json, sys, urllib.request
API, PID = sys.argv[1], sys.argv[2]
def req(path, role, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(API + path, data=data, method=("POST" if data is not None else "GET"),
                               headers={"X-Tether-Role": role, "Content-Type": "application/json"})
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read() or b"{}")
n = 0
for c in req(f"/api/projects/{PID}/claims?review_state=pending", "reviewer"):
    req(f"/api/claims/{c['id']}/review", "reviewer", {"action": "confirm"}); n += 1
print(f"  claims confirmed: {n}")
m = 0
for c in req(f"/api/projects/{PID}/conflicts?state=open", "reviewer"):
    value = c["claims"][0]["value"]
    req(f"/api/conflicts/{c['id']}/decide", "reviewer",
        {"value": value, "reason": "walkthrough: recorded first side shown; a real decision names the source of truth"}); m += 1
print(f"  conflicts decided: {m}")
g = 0
for gap in req(f"/api/projects/{PID}/gaps?state=open", "reviewer"):
    req(f"/api/gaps/{gap['id']}/assign", "reviewer",
        {"owner": gap.get("owner") or "Aarav Mehta (leaver)", "next_step": gap.get("next_step") or "Ask in week 1."}); g += 1
print(f"  gaps assigned: {g}")
PY

echo "== DM-3 correct — sign the version (Gate 3) =="
SIGN=$(curl -sf -X POST -H "X-Tether-Role: reviewer" "$P/versions/sign")
echo "$SIGN" | python3 -c "import json,sys;d=json.load(sys.stdin);print('  signed',d['number'],'items',d['items'],'sha256',d['sha256'][:16]+'…','by',d['signed_by'])"
curl -sf -X POST -H "X-Tether-Role: reviewer" "$P/share" > /dev/null && say "shared with the project"

echo "== DM-4 restrict — the successor opens the handover; restricted stays hidden =="
HO=$(curl -sf -H "X-Tether-Role: successor" "$P/handover")
echo "$HO" | python3 -c "
import json,sys
d = json.load(sys.stdin)
sections = [s['title'] for s in d['sections']]
print('  sections:', ' | '.join(sections))
print('  restricted notice shown to successor:', bool(d.get('restricted_notice')))
print('  receipt already recorded:', d.get('receipt'))"
CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "X-Tether-Role: successor" "$P/claims")
say "successor reading the review queue is refused with HTTP $CODE (role-filtered)"
curl -sf -X POST -H "X-Tether-Role: successor" "$P/receipt" > /dev/null && say "receipt confirmed → project state=received"

echo "== done — this run used a throwaway database; your demo is untouched =="
echo "verify the build yourself: make verify"
