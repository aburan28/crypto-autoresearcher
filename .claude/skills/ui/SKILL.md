---
name: ui
description: "Build or maintain the crypto-autoresearcher dashboard, curve traits, receipt comparisons, provenance views and static exports. Use for reader bugs, UI features, benchmark imports and local previews. Use curve for identities, bench for comparison meaning and pr for publishing changes."
---

# Research UI

Read `ui/README.md`, `ui/payloads.py`, and the relevant reader module. Preserve the shared live/static data contract.

1. Trace the source record through parsing, pins/adapters, payload and renderer. Keep source-reported values, verification states, unknowns and declared versus observed dates distinct.
2. Change the reader or import adapter within the requested scope. Do not add ledger-authoring or research execution controls to a read-only dashboard.
3. Preserve exact global curve/candidate/workload identities, large integers, trait parameter sets and source links. Use curve and bench for data/semantic checks.
4. Exercise affected Python payload tests and JS reader tests; use the documented browser smoke test when layout/navigation changes warrant it. Do not run experiments to populate a preview.
5. Use `python3 -m ui` for the local reader and `python3 -m ui.build` for a requested static export after checking current flags. Bind source links to the public repo or immutable revision; do not expose credential-bearing origin URLs.
6. Return the changed behavior, preview/test evidence and missing data. Building a static output is not deployment; publish only within the user's requested scope.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
