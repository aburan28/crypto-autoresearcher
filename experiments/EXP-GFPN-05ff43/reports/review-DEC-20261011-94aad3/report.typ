#set page(paper: "us-letter", margin: (x: 0.62in, y: 0.58in))
#set text(font: "Arial", size: 10pt)
#set par(leading: 0.55em)
#show heading: set text(fill: rgb("#17212c"))

= GFPN RDL-1 admission decision
#text(size: 9pt, fill: rgb("#526173"))[DEC-20261011-94aad3 · EXP-GFPN-05ff43 · BATCH-e409ca · 2026-10-11]

*Scope.* This is a procedural scheduling decision for `TASK-20260925-23c435`. Its claim tier is none. It does not score an ECDLP result or change the status of `H-GFPN-9a29be` or `HEUR-GFPN-DFLAT`.

#figure(image("gate.svg", width: 100%), caption: [Frozen R2b gate, from `TASK-20260925-23c435` DP-2/DP-3/DP-4. Package observations come from `RUN-GFPN-4d1ac0`, `RUN-GFPN-d98707`, `RUN-GFPN-347fde`, `RUN-GFPN-0037fb`, and the immutable R2-r5 execution report.])

== Observation

The content-first receipt under `TASK-20261010-0fda2f` verifies 771 unchanged source paths in five commits (337 + 319 + 13 + 101 run files and one report). Its receipt-only commit is `0080cca50e6e80cea55062a57e96a33c680c1c99`. The old `TASK-20260925-0ed1be` Phase B has no post-run receipt and remains incomplete.

The original report records G1, G2, and G4 as `completed_valid` with `gate_pass: true`. G3 is `failed`, `infrastructure_error`, `gate_pass: false`. G4 was launched after G3 failed and is retained as a sequencing deviation.

== Frozen-predicate comparison

DP-2 requires the old Phase-B receipt, which is absent. DP-3 requires *all four* gate packages to be `completed_valid`, `gate_pass: true`, and checker exit 0, plus REG-1 PASS. G3 fails that conjunction on its raw status and gate value. DP-4 requires an unblocking queue revision, which has not been made. RDL-1 therefore stops R2b-r5 before any run directory is created.

#pagebreak()
== Diagnostic and limits

A fresh isolated checker replay in the custody receipt passes G1, G2, and G4 but fails G3 on `missing artifact certificates`; the original execution report recorded G3 checker PASS. A scratch reconstruction from exactly the 13 tracked G3 files gives checker exit 1 without `certificates/` and exit 0 after adding only an empty `certificates/` directory. All 13 tracked bytes remain hash-equal. `diagnostic.json` preserves the commands, environment, hashes, stdout, stderr, and exits. The control establishes sufficiency in the scratch copy; it cannot establish the production-time directory state or make G3's raw gate pass.

== Scheduling disposition

All eleven IDs in the frozen `trial-plan-v2-a1-r5.json` remain *not_attempted*: `RUN-GFPN-ba6fbe`, `2f652c`, `460cbc`, `b0461a`, `588be4`, `d68f02`, `4da222`, `027369`, `8eaa60`, `ad9594`, and `ce0dfe`. The final two are contingency IDs; their R-12 trigger was never reached.

G4 remains a preserved package and cannot serve as a valid post-failed-gate sample for this admission decision. No R2b package, reviewer, or scientific trial is dispatched. This disposition makes no claim about the mathematical hypothesis or curve security.

== Evidence and next gate

- Frozen dispatch contract: `ledger/handoffs/TASK-20260925-23c435.yaml`, DP-2, DP-3, DP-4 and R5BP-2.
- Source observations: `experiments/EXP-GFPN-05ff43/execution-report-v2-r5.yaml`, four `RUN-GFPN-*` packages, and `TASK-20261010-0fda2f/content-first-receipt.json`.
- Scratch control: `diagnostic.json`, reconstructed from G3 source commit `61004685f4750553a59bc4ee7a776cb5e69754f2`.

Before any claim-changing interpretation of G3, G4, G1/G2, or the heuristic, the Coordinator must commit a review plan with a recorded prior, independent joint owners, blind rederivation, and a known-false post-failed-gate control. The relevant canonical frontier graphs were checked: this procedural stop changes no measured bound or claim tier, so no canonical graph content changes.
