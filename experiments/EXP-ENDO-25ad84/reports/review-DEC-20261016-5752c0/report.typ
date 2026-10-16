#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#set par(justify: false)
#show heading: set text(size: 11pt)

= Decision report: DEC-20261016-5752c0 (EXP-ENDO-25ad84)

*Decision: weaken H-ENDO-5a33ae.* Evidence `EV-ENDO-fb5823`: direction weakens, strength preliminary, claim tier modelled, proof status certificate (for the adverse part). No ECDLP, rho or exponent claim changes.

== Identity
- Experiment `EXP-ENDO-25ad84`, run `RUN-ENDO-d7cb69`, hypothesis `H-ENDO-5a33ae`, idea `IDEA-20261016-15a6fc`, question `RQ-ENDO-476761`, goal `GOAL-ENDO-001`.
- Approval `DEC-20261016-5cd7e2`; executor `TASK-20261016-3a809b`; snapshot `TASK-20261016-cbf19d` at `2a8674d65`; independent validation `TASK-20261016-1b5210` (passed); ledger archive `TASK-20261016-5c0f78`.
- Analysis: `experiments/EXP-ENDO-25ad84/analysis.md`. Earlier run report: `reports/run-20261016T1709Z/report.pdf`.

== Scoped claim
On the 132 tested prime-field curves (at most 521 bits; ell ≤ 13, depth 2, at most 64 nodes; curvesweep M\_eq = M + S model at S = 1 M, 200 scalars, seed 20261016), a model change on a rational 5- or 25-isogenous neighbour lowers modelled one-shot variable-base k·P cost against E's best model and unit GLV on seven curves from five families (+6.70 % to +14.52 %), every route verified on points. On six of them, E's own chain 2-GLV is cheaper still. The arm-A statement that no population curve outside j = 0 / 1728 has |D#sub[K]| ≤ 20 is false on this population. No timing and no ECDLP statement.

== Graph
#figure(image("decision.svg", width: 100%), caption: [Left: arm M, recorded one-shot gains of the best route in RUN-ENDO-d7cb69 against the frozen baseline (blue; criterion > 0, prediction band (0, 15 %\] shaded) and against E's verified chain 2-GLV recomputed in RUN-ENDO-795989 (red). Modelled M\_eq, single deterministic pass, 200 scalars per cost; baseline sampling error 3.2–3.8 M\_eq (validator J4), below 0.2 percentage points. Right: arm A, certified |D#sub[K]| of 48 population curves against the frozen threshold 20; two rows whose root is not a j = 0 / 1728 crater fall below it.])

== Observation
- Controls all pass: control+model persistent +15.28 %, one-shot +14.46 %, verified 8/8; control+ascent D#sub[K] = −3 with crater GLV priced; NIST P-256 best persistent 0.0; Curve25519 best persistent 0.0; instrument check 136/136.
- Arm M: seven population curves have a verified route with one-shot gain above 0: Tom-384 +14.52 %, mnt5/2 and mnt5/3 +13.71 %, mnt3/1 and mnt3/3 +12.70 %, BADA55-VPR-224 +11.44 % (path 5·5), GOST 2001 test curve +6.70 %. They are five families: the mnt pairs share every figure.
- Arm A: bls/Bandersnatch (D#sub[K] = −8) and mnt/mnt1 (D#sub[K] = −19) have roots that are not j = 0 / 1728 craters; f#sub[E] unresolved.
- Against E's chain 2-GLV, the model change loses one-shot by 34.05 % (GOST), 25.24 % (mnt3), 26.50 % (mnt5) and 30.31 % (Tom-384).

== Comparison
- Arm M success criterion (one verified route with one-shot gain above 0): *met*. The predicted band (0, 15 %\] holds for all seven one-shot gains. "At most 0 on a = −3 and a = 0 curves": consistent.
- Arm A zero-hit prediction: *falsified as worded*, 2 hits against 0, under H-ENDO-5a33ae's own frozen definition ("own root is not a j = 0 or j = 1728 crater", the instrument's root\_crater flag). Under the validator's f#sub[E]-based reading the two rows are unresolved; no reading supports arm A.
- Against the index-calculus baseline and the matched rho: not applicable (known-scalar k·P cost).

== Inference
- Arm M holds as worded at the modelled tier. Its practical reach is one curve: other/BADA55-VPR-224 is the only positive that no known verified method on E beats within the scanned discriminant bound.
- Arm A is refuted by a checkable counterexample: the recorded identity t#super[2] − 4p = D#sub[K] f#sub[π]#super[2] with D#sub[K] ∈ {−8, −19}, and D#sub[K] ∉ {−3, −4} excludes j ∈ {0, 1728} on an ordinary curve. The independent recomputation of the identity is a gate of the ledger archive.
- One conjunct refuted and one holding: the hypothesis is weakened, not rejected.

== Limitation
- Modelled counts in one cost model; no timing. One seed; seven positives are five families.
- Scope: ell ≤ 13, depth 2, 64 nodes, |D#sub[K]| ≤ 2#super[20], prime fields of at most 521 bits.
- f#sub[E] is unresolved outside j = 0 / 1728. The baseline omits E's chain GLV by contract. Heuristics H1–H3 are not validated.

== Next actions (ranked, recommended, not approved)
+ Fix isoglv's one-shot input-format pricing (CORR-20261016-ac9fc8) and re-run the combined screen under a new contract.
+ Timed bench of the combined route on other/Tom-384 against GLV on E.
+ ecbench independent-runner replication of EXP-ENDO-33a1ee.
+ Lower: price E's own small-norm CM endomorphism GLV on Bandersnatch and mnt1, and certify f#sub[E], as an idea for /propose-ideas.

All four are constant-factor, known-scalar work and rank behind exponent-targeting work.

== Canonical graphs
Checked and left unchanged: `research/endosweep_curves_20261006/` (tables only; its GLV figures were reproduced exactly), and `knowledge/frontiers/ecdlp/` (no graph source; no ECDLP claim moves). No canonical graph changes.

== Files
`plot.py` draws `decision.svg` from `runs/RUN-ENDO-d7cb69/raw-result.json` and `../EXP-ENDO-7494e7/runs/RUN-ENDO-795989/raw-result.json` only.
