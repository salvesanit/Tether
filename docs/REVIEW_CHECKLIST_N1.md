# N1 review checklist — used at every checkpoint

A checkpoint = the end of a phase; N1 walks this against the running app and the reports, not against the diff alone. Any line answered "no" blocks sign-off.

1. **Connect.** Open the app cold. Is the next step obvious without reading a manual (≤5 minutes to Gate 1)?
2. **Gate 1.** Are all sources labelled, and the two excluded channels shown `not read` with reasons? Try Clear labels with one source unlabelled → must refuse 409 and log `gate.refused`.
3. **Rebuild.** Do the counts in the UI match `reports/check_report.json` for the same commit? spans 165 · candidates 82 · kept 60 · dropped 21 · conflicts 6 · gaps 6 · quarantine 1.
4. **Spot-check three claims.** Open each citation. Is the quote highlighted at the exact locator? Is the label right under HR-2?
5. **Review.** Confirm one claim · edit one (history kept) · reject one (needs a reason) · park one (needs a reason). Does each action write its own log row?
6. **Conflict.** Both sides visible on all six? Pick one — does the loser stay visible as decided? Does code ever pick one (must be never)?
7. **Unsigned gate.** Sign with one conflict undecided → 409 naming the gate; then decide and sign → v1.0 with a hash; does the version render for reviewer and 403/404 for successor before share?
8. **Handover as successor.** Six sections? Risk order? Citations clickable? Restricted shows only the one plain notice (no title, no count)?
9. **Receipt.** Diya logs receipt; state becomes received; the loop is closed on the leaver's side.
10. **Leak pass.** Run `pytest backend/tests/test_perm1_leak_successor.py -q` and open the signed handover; confirm zero restricted/confidential text; open [leak_test_report.md](../reports/leak_test_report.md) for the route-by-route table.
11. **Reports.** Each carries commit SHA + date + model mode + "measured on the synthetic project". Counts only.
12. **Honesty sweep.** Search the repo for `TODO|FIXME|lorem ipsum|% captured|loss rate` — all must be absent or explicitly documented as absent.
13. **Sign-off boundary.** N1 confirms only what N1 can verify: the checks, the gates, the filters. The model's opinions are never the artifact; only the person's decisions are.
