#set page(paper: "a4", margin: (x: 17mm, y: 15mm))
#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9pt)
#set par(justify: true, leading: 0.6em)
#show heading.where(level: 1): set text(size: 13pt)
#show heading.where(level: 2): set text(size: 10.5pt)

= Decision report: DEC-20261018-3b4a32 (replicate)

*Decision* `replicate`. *Evidence* EV-SEMAEV-593b7a: direction supports (scoped), strength *preliminary*, claim tier toy. *Correction* CORR-20261018-d51221. Hypothesis H-SEMAEV-94dab2: approved → analyzed. Experiments EXP-SEMAEV-93d5cc and EXP-SEMAEV-6e9dcf → analyzed; EXP-SEMAEV-88c46c → failed\_infrastructure. Validation TASK-20261018-83a561 (VAL-20261024-c8a775): passed on all seven runs. Run report: `reports/run-20261018T2156Z/`.

== Scoped claim

The pre-2026-08-13 `s4_expr` (which drops x3) changed the recorded S4-dependent outputs of the archived runs where the polynomial was solved or analysed to completion, and left them unchanged where every solve hit its archived cap. Changed: every m4 invariant of RUN-ICINV-e0cd8f-m3class (`s4_support` 227/225/210 → 439/391; singular-locus degree 60 → 39 on all 552 records), the RUN-FIB-004 C16-1 bases (3–4 elements → 14–19) and costs (median 0.058 s legacy rerun → 3.68 s), and the RUN-FIB-006C C16-1 correlation (rho\_s −0.024 archived, −0.097 legacy rerun, −0.366 repaired). Unchanged: every frozen MTIC conclusion (regime (i), K\* infinite) and every FIB gate (correlation gate fail, cost gate pass, RUN-FIB-008 cancelled). RUN-SEMAEV-9cab7b, -3e69b6, -4be606, -894e27, -2a8498, -fcd67c and -0e5876.

#figure(image("figure-cells.svg", width: 92%), caption: [Per cell: legacy reproduction control; whether any S4-dependent output differs between the repaired and legacy arms (timing medians excluded; for fib-decision the timing-derived rho\_s and ratios, read against the 0.073 A/A spread); whether any frozen conclusion field differs from the archive. Data: `plot-data.json`, drawn by `chart.py`.])

== Observation · Comparison · Inference · Limitation

*Observation.* Recorded values as in EV-SEMAEV-593b7a O1–O6 and the run report. *Comparison.* C-defect (one factor, isolated): 552/552 ICINV tuples and 200/200 C16-1 basis tuples differ; capped cells identical. C-aa-legacy-archive: zero deterministic differences; timing spread C16-1 median 0.0279 → 0.0579 s, rho\_s 0.073. C-repaired-archive is confounded and decides nothing alone. *Inference.* The changes are attributable to the defect; in capped cells the archived numbers stand because the caps still bind. The ICINV CLASS-VARYING verdict (m3 only) is unaffected; its m4 secondaries are superseded. EXP-FIB-001's C16-1 "no association" reading was produced by the defect: with the exact S4 the association falls in the frozen inconclusive band (0.2 ≤ |rho| < 0.4), while the gate outcome stands. *Limitation.* Toy tier; one execution per arm for timing-derived values; host-dependent caps; the validator was a subagent of the producing session (procedure deviation), which caps strength at preliminary and is why the decision is replicate, not support.

#figure(image("figure-icinv.svg", width: 100%), caption: [ICINV m4 invariants (copied from the run report): RUN-ICINV-e0cd8f-m3class archived vs RUN-SEMAEV-9cab7b arms, 552 records.])

#figure(image("figure-fib.svg", width: 100%), caption: [FIB C16-1 (copied from the run report): per-target Groebner seconds, n = 200 per arm, and rho\_s against the frozen EXP-FIB-001 bands; RUN-FIB-004/006C vs RUN-SEMAEV-3e69b6/-894e27.])

== Next actions

Independent-session re-validation of the seven run records (then a decision may move H-SEMAEV-94dab2 to supported); Coordinator review of H-FIB-001 for the C16-1 band change; supersede KN-OPEN-5b3a08's numerical-impact question with these results, keeping Q2 open; decide whether EXP-DTREE-b93a15 is withdrawn as subsumed.

== Canonical graphs

Checked and left unchanged: no canonical graph under `knowledge/frontiers/ecdlp/` plots MTIC, FIB or ICINV m4 numbers (search for EXP-MTIC-001, EXP-FIB-001 and RUN-ICINV-e0cd8f-m3class in that tree). The corrected numbers live in CORR-20261018-d51221.
