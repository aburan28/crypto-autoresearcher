# Run report: EXP-CERTBIN-ddfe75 / RUN-CERTBIN-6ebb0e (N-CONV)

Observations only. No hypothesis status is changed and no heuristic is declared supported or refuted.

Validity status: **completed_valid**. Task TASK-20260924-7c1fb2; archived by TASK-20260924-40b2ca.

## Claim tier and scope (verbatim from the specification)

Claim tier: toy. Closure measurements on synthetic Boolean systems derived from one cell: n = 17, f = t^17 + t^3 + 1, m = 2, l = 9, V = {deg < 9} (polynomial basis), curve A = 97044, B = 126251 (#E = 4 * 32603). The targets are the 144 archived x_R of RUN-CERTBIN-c417e0 (sets U62, S62, C20; all x(2E) subgroup targets). The closures are M_4, W_4 and their ell-substituted counterparts, as defined below.

sota_delta: zero on every ECDLP cost axis (time, memory, data). dominated_by: oracle A (2^9 = 512 quadratic root-findings over V per attempt at m = 2) and parallel Pollard rho (about 160 group operations at q = 32603). No cost claim. Nothing here transfers to n = 19, other curves or V, or off-x(2E) targets without measurement.

## Primary verdicts (NC-DR-9)

- NC-DR-1: **TENSOR**. L1 (uncertified counted as not refuted): w = 144, n_C = 144, CP95 [0.974708, 1.0], label TENSOR. L2 (uncertified excluded): w = 144, n_C = 144, label TENSOR. Uncertified: 0. E-TENSOR falsified (w <= floor(n_C/2)): False; E-LINEAR falsified (w > floor(n_C/2)): True.
- NC-DR-4: **CONVOLUTION TENSOR**. N-CONV ABOVE N-ELL144: True; N-CONV ABOVE NULL-F262: True. N-CONVL level: TENSOR-level. Appended N-CONV17 reading: CONVOLUTION FORMS SUFFICE WITHOUT THE COKERNEL FALL.

## Secondary verdicts

- NC-DR-2: AT S_3's RATE (N-CONV CP95 [0.974708, 1.0] vs 386/386 CP95 [0.990489, 1.0]); against in-run S_3 (82): AT S_3's RATE.
- NC-DR-3 ladder (W_4, verified wdag-v1, CP95):
  - N-CONV: 144/144, CP95 [0.974708, 1.0]
  - N-CONVL: 144/144, CP95 [0.974708, 1.0]
  - N-CONV17: 144/144, CP95 [0.974708, 1.0]
  - N-ELL144: 0/144, CP95 [0.0, 0.025292]
  - NULL-F262: 0/62, CP95 [0.0, 0.057763]
  - NULL-AFF62 [one affine draw]: 0/62, CP95 [0.0, 0.057763]
  - S_3 (82): 82/82, CP95 [0.956011, 1.0]
  - ABOVE relations: N-CONV ABOVE N-ELL144; N-CONV ABOVE NULL-F262; N-CONV ABOVE NULL-AFF62 [one affine draw]; N-CONVL ABOVE N-ELL144; N-CONVL ABOVE NULL-F262; N-CONVL ABOVE NULL-AFF62 [one affine draw]; N-CONV17 ABOVE N-ELL144; N-CONV17 ABOVE NULL-F262; N-CONV17 ABOVE NULL-AFF62 [one affine draw]; S_3 (82) ABOVE N-ELL144; S_3 (82) ABOVE NULL-F262; S_3 (82) ABOVE NULL-AFF62 [one affine draw]; every other ordered pair NOT DISTINGUISHED.
- NC-DR-5 (descriptive; label on unsatisfiable systems):
  - S3-U62 (unsat): 0/62 reference profile -> FAILS; T5_applicable 0/62
  - S3-C20 (unsat): 0/20 reference profile -> FAILS; T5_applicable 0/20
  - S3-S62 (all): 0/62 reference profile -> FAILS; T5_applicable 0/62
  - NULL-AFF62 (unsat): 62/62 reference profile -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable 0/62
  - NULL-F262 (unsat): 62/62 reference profile -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable 0/62
  - NELL-A20 (unsat): 20/20 reference profile -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable 20/20
  - N-CONV (unsat): 0/144 reference profile -> FAILS; T5_applicable 0/144
  - N-CONVL (unsat): 0/144 reference profile -> FAILS; T5_applicable 0/144
  - N-CONV17 (unsat): 0/144 reference profile -> FAILS; T5_applicable 0/144
  - N-ELL144 (unsat): 144/144 reference profile -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable 144/144
- NC-DR-6: N-CONV M_4 NOT AT STAGE-1 RATE. M_4 per arm: S3-U62 0/62; S3-C20 20/20; NULL-AFF62 0/62; NULL-F262 0/62; NELL-A20 0/20; N-CONV 144/144; N-CONVL 105/144; N-CONV17 143/144; N-ELL144 0/144; S_3 (82) 20/82. N-CONV W_4 among M_4-unrefuted: 0/0.
- NC-DR-7 (recorded, Coordinator decides after review): the n = 19 cell quotes S_3-specificity against an N-CONV-type arm (same-support nulls insufficient).
- NC-DR-8: all instrument checks pass: True.

## Instrument checks

- C-ENGINE: PASS (INV-1)
- C-SRC: PASS (INV-2)
- C-SELF: PASS (INV-3)
- C-FIX: PASS (INV-3)
- C-CONSTRUCT: PASS (INV-3)
- C-SUPPORT: PASS (INV-3)
- C-REG: PASS (INV-4)
- C-ELL: PASS (INV-8)
- C-TOP: PASS (INV-8)
- C-T4: PASS (INV-8)
- C-WDAG: PASS (INV-8)
- C-ORACLE2: PASS (INV-7)
- C-DRAW: PASS (INV-7)
- C-PS: PASS (INV-5 (and INV-7 if a satisfiable-control certificate verifies))
- C-CERT: PASS (INV-6)
- C-VERIFIER: PASS (INV-6)
- C-DET: PASS (INV-9)

## Predictions PN-1..PN-5 (H-CERTBIN-be6cbd), mechanical reading

- PN-1: w = 144 of n_C = 144: E-TENSOR threshold met.
- PN-2 (L-TOP, P equal to S_3's at the same x_R; N-CONV17 one P): held (864 systems checked).
- PN-3 (T4 on every substituted system; T5 where applicable): held (T4 1028 systems, T5 308).
- PN-4 (0 refuted satisfiable controls): held (0 refutations).
- PN-5 (N-ELL144 refuted 0 times where T5 applies with the semi-regular profile): N-ELL144 W_4 engine refutations 0/144; see NC-DR-5 for the T5/profile fractions.

## Coordinator prior (a)-(g): observed outcome against the modal expectation

- (a) N-CONV modal TENSOR: observed TENSOR.
- (b) N-CONV M_4 rate at least S_3's Stage-1 rate (324/386 = 0.839): observed 144/144.
- (c) N-CONV substituted profiles non-semi-regular on >= 90%: observed reference (semi-regular) profile on 0/144.
- (d) N-CONVL TENSOR-level: observed TENSOR-level (144/144).
- (e) N-CONV17 (no confident prior): observed TENSOR-level (144/144).
- (f) N-ELL144 refuted 0 times: observed 0 engine refutations.
- (g) every W_4 refutation gets a verified wdag-v1: uncertified W_4 refutations 0; failed certificates 0.

## E_hex bit layout

A system is 17 rows (f_0..f_16). Row k is a 172-bit integer written as lowercase hex without prefix; bit j (least significant first) is column j of mu_order(2, 18): column 0 the constant, columns 1..18 v_0..v_17, columns 19..171 the 153 pairs (a, b), a < b, in ascending tuple order. E_sha256 = sha256(json.dumps(E_hex)). Assignments and solutions are 18-bit integers with bit i = v_i.

## Independence disclosure

The engine crypto_autoresearcher.gf2 (pinned at 934bee5, _kernels.c sha256 c8f79d5961fffaf80428cdd29d0a53bfcc1e6d32ab07022931e3aacd926ca745) was written by the dispatching session, not by this executor and not by any reviewer. impl/ and verifier/ were both written by this executor in one session. The verifier is code-independent of the engine and of impl/ (it imports neither and re-derives every system, draw stream, satisfiability count and certificate check with its own code), but it is NOT author-independent of impl/. Author-independent verification is the review round's (claim_tier_and_review joints 1-3).

## Artifacts

manifest.yaml, command.txt, environment.json, stdout.log, stderr.log, raw-result.json, cell-summary.json, decision-rules.json, instrument-checks.json, engine-provenance/, selftest.json, inputs.json, support.json, draws-*.jsonl.gz, instances.jsonl.gz, predictions-t5.jsonl.gz, closures.jsonl.gz, certificates.jsonl.gz, certificate-verification.json, construction-verification.json, draw-replay-verification.json, negative-controls-certificates.jsonl.gz, negative-controls-verification.json, determinism.json, phase-log.jsonl, implementation.md, checkpoint/.

