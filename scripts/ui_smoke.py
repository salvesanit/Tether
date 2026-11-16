#!/usr/bin/env python3
"""UI smoke walk — drives the real browser through the golden path against a seeded demo.

Requires: server running on :8000 with a freshly seeded DB (`make seed && make run`),
and playwright installed (`pip install playwright && python -m playwright install chromium`).

Usage: python3 scripts/ui_smoke.py [--base-url http://127.0.0.1:8000]
Writes screenshots to reports/ui/ and prints a step-by-step PASS/FAIL log. Exits non-zero on failure.
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "reports" / "ui"
AXE_SCRIPT = ROOT / "node_modules" / "axe-core" / "axe.min.js"
SHOTS.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")
    log = []
    console_errors = []

    def step(name, ok, detail=""):
        log.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    def audit_screen(name):
        try:
            violations = page.evaluate("""async () => {
              const results = await axe.run(document, {
                runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] }
              });
              return results.violations
                .filter(v => v.impact === "critical" || v.impact === "serious")
                .map(v => `${v.id} (${v.impact}): ${v.nodes.length} node(s)`);
            }""")
            step(f"axe audit: {name}", not violations,
                 "zero critical/serious violations" if not violations else "; ".join(violations))
        except Exception as exc:
            step(f"axe audit: {name}", False, str(exc)[:240])

    def switch_role(role):
        page.locator(".role-trigger").click()
        page.locator(f".role-option[data-role='{role}']").click()
        page.wait_for_timeout(300)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        # 0. home
        page.goto(base + "/", wait_until="networkidle")
        step("home loads", page.locator("text=The handover that holds").count() >= 1)
        if AXE_SCRIPT.is_file():
            page.add_script_tag(path=str(AXE_SCRIPT))
            step("axe-core loaded", True)
        else:
            step("axe-core loaded", False, f"missing {AXE_SCRIPT}; run npm ci")
        page.screenshot(path=str(SHOTS / "01-home.png"), full_page=True)

        # 1. load demo as reviewer (default role)
        page.click("#cta-demo")
        page.wait_for_selector("text=Gate 1 — the reviewer clears the labels", timeout=20000)
        step("demo project loads on Connect", True)
        audit_screen("Connect")
        page.screenshot(path=str(SHOTS / "02-connect.png"), full_page=True)

        # 2. clear labels
        page.click("#clear-labels")
        page.wait_for_selector("text=Labels cleared — the rebuild may read", timeout=20000)
        step("label gate cleared", True)

        # 3. rebuild
        page.click("a.step-link[href$='/rebuild']")
        page.wait_for_selector("#run-rebuild", timeout=20000)
        page.click("#run-rebuild")
        page.wait_for_selector(".stat-tiles", timeout=60000)
        kept = page.locator(".stat-tile").nth(2).inner_text()
        step("rebuild completes with stat tiles", "61" in kept.replace("\n", " "), kept.splitlines()[0] if kept else "")
        audit_screen("Reconstruct")
        page.screenshot(path=str(SHOTS / "03-rebuild.png"), full_page=True)

        # 4. review — confirm every pending claim
        page.click("a.step-link[href$='/review']")
        page.wait_for_selector(".tabs", timeout=20000)
        confirmed = 0
        for _ in range(120):
            btn = page.locator(".claim-card:not(.decided) [data-act='confirm']").first
            if btn.count() == 0:
                break
            btn.click()
            page.wait_for_timeout(140)
            confirmed += 1
        step("pending claims confirmed", confirmed >= 1, f"{confirmed} confirmed via UI")
        page.screenshot(path=str(SHOTS / "04-review-claims.png"), full_page=True)
        audit_screen("Review Queue")

        # 4b. conflicts — pick first value + reason, decide
        page.click(".tab[data-tab='conflicts']")
        decided = 0
        for _ in range(12):
            card = page.locator(".conflict-card:not(.decided)").first
            if card.count() == 0:
                break
            card.locator("input[type=radio]").first.check()
            card.locator(".reason-input").fill("Decided by the reviewer after reading both quotes.")
            card.locator("[data-cact='decide']").click()
            page.wait_for_timeout(350)
            decided += 1
        step("conflicts decided", decided >= 1, f"{decided} decided via UI")
        page.screenshot(path=str(SHOTS / "05-review-conflicts.png"), full_page=True)

        # 4c. gaps — assign owner + next step
        page.click(".tab[data-tab='gaps']")
        assigned = 0
        for _ in range(12):
            card = page.locator(".gap-card:not(.decided)").first
            if card.count() == 0:
                break
            card.locator("[data-field='owner']").fill("Aarav Mehta (leaver)")
            card.locator("[data-field='next_step']").fill("Ask before the last day; log the answer.")
            card.locator("[data-gact='assign']").click()
            page.wait_for_timeout(300)
            assigned += 1
        step("gaps assigned & closed", assigned >= 1, f"{assigned} assigned via UI")
        page.screenshot(path=str(SHOTS / "06-review-gaps.png"), full_page=True)

        # 4d. quarantine — confirm injection (the span was instruction-like text)
        page.click(".tab[data-tab='quarantine']")
        qbtn = page.locator("[data-qact='confirmed']").first
        if qbtn.count():
            qbtn.click()
            page.wait_for_timeout(300)
        step("quarantine reviewed", True)
        page.screenshot(path=str(SHOTS / "07-review-quarantine.png"), full_page=True)

        # 5. sign
        page.click("a.step-link[href$='/signoff']")
        page.wait_for_selector(".gate-list", timeout=20000)
        gates_all = page.locator("text=ALL PASS").count() >= 1
        step("gate report shows all pass", gates_all)
        audit_screen("Sign-Off")
        if gates_all:
            page.click("#sign-btn")
            page.wait_for_selector("text=signed & frozen", timeout=20000)
            step("version signed", True)
            page.screenshot(path=str(SHOTS / "08-signed.png"), full_page=True)
            share = page.locator("#share-btn")
            if share.count():
                share.click()
                page.wait_for_timeout(400)
                step("shared with successor", True)

        # 6. successor opens handover + receipt
        switch_role("successor")
        page.click("a.step-link[href$='/handover']")
        page.wait_for_selector(".sections-grid", timeout=20000)
        restricted = page.locator(".restricted-notice").count() >= 1
        sections = page.locator(".section-card").count()
        step("successor sees the handover", sections >= 4, f"{sections} sections, restricted notice: {restricted}")
        audit_screen("Successor View")
        page.screenshot(path=str(SHOTS / "09-handover-successor.png"), full_page=True)
        receipt = page.locator("#receipt-btn")
        if receipt.count():
            receipt.click()
            page.wait_for_selector(".receipt-done", timeout=10000)
            step("receipt logged", True)

        # 7. admin: verify chain + export page renders
        switch_role("admin")
        page.click("a[href$='/admin']")
        page.wait_for_selector("#verify-chain", timeout=20000)
        page.click("#verify-chain")
        page.wait_for_selector(".toast", timeout=10000)
        toast = page.locator(".toast").last.inner_text()
        step("audit log chain verifies", "Chain intact" in toast, toast)
        page.screenshot(path=str(SHOTS / "10-admin.png"), full_page=True)

        browser.close()

    real_errors = [e for e in console_errors if "favicon" not in e.lower()]
    step("no console/page errors", not real_errors, "; ".join(real_errors[:4]))
    report = {"base_url": base, "steps": [{"name": n, "ok": o, "detail": d} for n, o, d in log],
              "console_errors": real_errors}
    (ROOT / "reports" / "ui_smoke.json").write_text(json.dumps(report, indent=2))
    ok = all(o for _, o, _ in log)
    print(f"\nUI smoke: {'ALL STEPS PASS' if ok else 'FAILURES PRESENT'} — report at reports/ui_smoke.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
