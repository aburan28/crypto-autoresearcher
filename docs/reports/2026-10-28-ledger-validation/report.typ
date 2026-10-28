#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "Libertinus Serif", size: 10pt)
#set heading(numbering: "1.")

= Current full-ledger validation gap

Observation, 2026-10-28. This is a mechanical integrity report, not a scientific verdict, Lean proof, or performance result. The full-ledger validator gate is failing.

Two hosted `ledger` jobs, on PR #2609 head `64da2f5...` and PR #2655 head `a94a304...`, each reported 65 unsuppressed errors across 22 paths. The normalized error lists are identical: zero added and zero removed. Source jobs: `https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40624063556/job/122604839789` and `https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40627808095/job/122616982776`.

#image("categories.svg", width: 100%)

The count describes validator messages, not false experiment results. Handoff review plans account for 30 messages in 12 paths; run manifests, 30 in five paths; proposal prior art, four in four paths; and an AUXIN draft specification, one in one path. The current log separately reports 1,210 grandfathered suppressed errors and 578 advisories.

The source-linked path inventory and exact messages are in `errors.json`. Reproduce the comparison with `generate.py` and the two downloaded job logs. The normalized sorted set SHA-256 is `dd067769a634991c71a34c58f2630dc57ea37f098444d2ae9286d1c6b4f2807d`.

Next: review source evidence and actual reviewer assignments record by record; use hash-bound supersession only where justified; adjudicate the AUXIN draft category; rerun the complete-tree validator after corrections. Do not change sealed run bytes or add baseline suppressions. No canonical performance graph or numerical research result was changed here.
