# Run report: EXP-CERTBIN-060020 / RUN-CERTBIN-a3fc60

Validity status: **completed_valid**. Failed instrument checks: none.

Observations only. No hypothesis status, evidence record or decision is implied.

## Claim tier and scope (verbatim from the specification)

Claim tier: toy. Refutation-degree measurement at one cell: n = 19, f = t^19 + t^5 + t^2 + t + 1, m = 2, l = 10, polynomial V = {deg < 10}, one curve A = 46693, B = 306147 (#E = 2 * 261823, h = 2), subgroup (= x(2E)) targets plus uniform-x_R strata, under M_3, M_4, W_4 and the substituted R'_3, R'_4, W'_4 as defined below. n = 17 enters only as quoted references and as a regression slice. sota_delta: zero on every ECDLP cost axis. Dominated by oracle A (2^10 quadratic root-findings per attempt) and, for the DLP at q = 261823, by parallel Pollard rho.

## Decision rules (mechanical)

- N19-DR-1 (primary): w = 400 / N = 400, CP95 ['0.99082019541633473656', '1.0']; label L1 = PERSISTS, label L2 = PERSISTS (N_L2 = 400); verdict: PERSISTS. E-PERSIST falsified (L1): False; E-DECAY falsified (L1): True. n = 17 comparison: NO DETECTABLE DROP FROM n = 17 (the n = 17 figure imports 304 Stage-1 flags (82 RC-1-certified plus 304 Stage-1 flags) and the cells differ in curve, cofactor (h = 4 vs h = 2) and subgroup-target class (x(4E) vs x(2E))).
- N19-DR-2: M_4 m = 0 / 400, CP95 ['0.0', '0.0091798045836652634413']; verdict LOWER against [0.799, 0.875]. M_3 count 0. W_4 rate on systems M_4 does not refute: 400/400 CP95 [0.9908, 1.0000].
- N19-DR-3 (primary): N_b = 400; sigma > 0: 400, sigma = 0: 0, sigma < 0: 0; FULL (1160): 0 (fraction 0.0); verdict NON-SEMI-REGULAR PERSISTS. Profiles: {'[0, 1, 156, 1124, 3180]': 196, '[0, 0, 156, 1124, 3180]': 174, '[0, 0, 151, 1119, 3175]': 2, '[0, 1, 154, 1122, 3178]': 8, '[0, 1, 155, 1123, 3179]': 1, '[0, 1, 150, 1118, 3174]': 1, '[0, 0, 154, 1122, 3178]': 3, '[0, 0, 152, 1120, 3176]': 3, '[0, 2, 156, 1124, 3180]': 5, '[0, 0, 155, 1123, 3179]': 1, '[0, 4, 158, 1126, 3182]': 2, '[0, 0, 122, 1090, 3146]': 1, '[0, 3, 156, 1124, 3180]': 1, '[0, 1, 152, 1120, 3176]': 2}. Not substituted: {}.
- N19-DR-4 vs N-F219: W_4 S_3 ABOVE X (X: 0/200 CP95 [0.0000, 0.0183]); M_4 NOT DISTINGUISHED (X: 0/200 CP95 [0.0000, 0.0183]).
- N19-DR-4 vs N-AFF19: W_4 S_3 ABOVE X (X: 0/200 CP95 [0.0000, 0.0183]); M_4 NOT DISTINGUISHED (X: 0/200 CP95 [0.0000, 0.0183]).
- N19-DR-4 vs N-ELL19: W_4 S_3 ABOVE X (X: 0/200 CP95 [0.0000, 0.0183]); M_4 NOT DISTINGUISHED (X: 0/200 CP95 [0.0000, 0.0183]).
- N19-DR-5: N-CONV19 W_4 200 / 200: TENSOR-LEVEL; AT S_3's RATE: True; ABOVE N-ELL19: True; ABOVE N-F219: True; paired 2x2: {'M_4': {'S3+ CONV+': 0, 'S3+ CONV-': 0, 'S3- CONV+': 0, 'S3- CONV-': 200}, 'W_4': {'S3+ CONV+': 200, 'S3+ CONV-': 0, 'S3- CONV+': 0, 'S3- CONV-': 0}}.
- N19-DR-6 at M_4: table {'X2E': [0, 200], 'pooled XE-NOT-2E + TWIST': [0, 400]}, one-sided Fisher p None, SATURATED (not evaluable); RANDX X2E REPLICATES PRIMARY: True.
- N19-DR-6 at W_4: table {'X2E': [200, 0], 'pooled XE-NOT-2E + TWIST': [400, 0]}, one-sided Fisher p None, SATURATED (not evaluable); RANDX X2E REPLICATES PRIMARY: True.
- N19-DR-7 S3-U400: 0/400 with substituted [0, 0, 18, 360, 3267] -> FAILS; T5_applicable fraction 0.000.
- N19-DR-7 S3-SAT100: 0/100 with substituted [0, 0, 18, 360, 3267] -> FAILS; T5_applicable fraction 0.000.
- N19-DR-7 N-CONV19: 0/250 with substituted [0, 0, 18, 360, 3267] -> FAILS; T5_applicable fraction 0.000.
- N19-DR-7 N-ELL19: 250/250 with substituted [0, 0, 18, 360, 3267] -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable fraction 1.000.
- N19-DR-7 N-F219: 250/250 with unsubstituted [0, 0, 19, 399, 3819] -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable fraction 0.000.
- N19-DR-7 N-AFF19: 250/250 with unsubstituted [0, 0, 19, 399, 3819] -> SEMI-REGULAR TRANSFER HOLDS; T5_applicable fraction 0.000.
- N19-DR-7 F-RANDX19: 0/600 with substituted [0, 0, 18, 360, 3267] -> FAILS; T5_applicable fraction 0.000.
- N19-DR-8: failed checks none; voids {'run_void': False, 'refutation_counts_void (INV-6)': False, 'arm_metrics_void (INV-7)': False, 'x2E_split_void': False, 'control_comparisons_void (C-NULLS)': False}.
- N19-DR-9: m = 3 pricing flag ELIGIBLE (the Coordinator decides after review).
- N19-DR-10: primary verdicts are N19-DR-1 and N19-DR-3.

## Pre-registered predictions PP-1..PP-6 (H-CERTBIN-e3ac93), as observed

- PP-1 (w; E-PERSIST vs E-DECAY): L1 PERSISTS, L2 PERSISTS; E-PERSIST falsified: False; E-DECAY falsified: True
- PP-2 (sigma): N19-DR-3 NON-SEMI-REGULAR PERSISTS
- PP-3 (M_4 vs n = 17): N19-DR-2 LOWER
- PP-4 (null / N-ELL19 W_4 refutations): N-F219: 0/200 CP95 [0.0000, 0.0183]; N-AFF19: 0/200 CP95 [0.0000, 0.0183]; N-ELL19: 0/200 CP95 [0.0000, 0.0183]; C-PRED pass
- PP-5 (soundness): refuted satisfiable controls M_3 0, M_4 0, W_4 0 of 300; codim >= s on 300; C-PS pass
- PP-6 (L-TOP): C-TOP19 pass (250 systems compared)

## Coordinator prior (a)-(g): which parts the observations overturn

- (a) N19-DR-1 prior PERSISTS 55 / PARTIAL 30 / DECAYS 15: observed PERSISTS (a probability prior is not overturned by one outcome; the most-likely label was PERSISTS)
- (b) N19-DR-2 prior LOWER 50 / CONSISTENT 40 / HIGHER 10: observed LOWER
- (c) N19-DR-3 prior NON-SEMI-REGULAR PERSISTS 80; FULL on most 40: observed NON-SEMI-REGULAR PERSISTS; FULL fraction 0.0
- (d) nulls and N-ELL19 at 0 W_4 refutations; N19-DR-7 HOLDS: N-F219: W_4 0/200 CP95 [0.0000, 0.0183]; N-AFF19: W_4 0/200 CP95 [0.0000, 0.0183]; N-ELL19: W_4 0/200 CP95 [0.0000, 0.0183]; DR-7: S3-U400: FAILS, S3-SAT100: FAILS, N-CONV19: FAILS, N-ELL19: SEMI-REGULAR TRANSFER HOLDS, N-F219: SEMI-REGULAR TRANSFER HOLDS, N-AFF19: SEMI-REGULAR TRANSFER HOLDS, F-RANDX19: FAILS
- (e) N19-DR-5 TENSOR-LEVEL 50: observed TENSOR-LEVEL
- (f) N19-DR-6 at M_4 MODULATED or WEAK 60; W_4 SATURATED if (a) PERSISTS: M_4: SATURATED (not evaluable), W_4: SATURATED (not evaluable)
- (g) every W_4 refutation certified 80; C-NONREF non-vacuous 45: uncertified W_4 refutations: none; ann-v1 submitted 15

## Instrument checks

- C-ENGINE: pass
- C-SRC: pass
- C-SEED: pass
- C-SELF: pass
- C-FIX: pass
- C-CURVE: pass
- C-ELL0: pass
- C-SLICE17: pass
- C-TR19: pass
- C-ELL: pass
- C-AFF19: pass
- C-SUPPORT: pass
- C-ORACLE: pass
- C-ORACLE2: pass
- C-DRAW: pass
- C-TOP19: pass
- C-T4: pass
- C-PRED: pass
- C-WDAG: pass
- C-MONO: pass
- C-PS: pass
- C-CERT: pass
- C-NONREF: vacuous
- C-VERIFIER: pass
- C-BACKEND: pass
- C-LIT: pass
- C-DET: pass
- C-NULLS: pass

## E_hex bit layout

A system is a 19 x 211 F_2 matrix E; row k is f_k (the coefficient of t^k). Column j is the j-th monomial of mu_order(2, 20): degree ascending, then ascending sorted index tuple (column 0 = 1, columns 1..20 = v_0..v_19, columns 21..210 = the pairs (i, j), i < j, in lexicographic order). E_hex is a list of 19 lowercase hex integers, bit j (LSB first) = column j. E_sha256 = sha256 of the compact JSON list of the 19 E_hex strings. Assignment integers u have bit i = v_i (x_1 = u mod 2^10, x_2 = u >> 10).

## Independence disclosure

The engine (src/crypto_autoresearcher/gf2, pinned 934bee5) was written by the dispatching session. impl/ and verifier/ were written by this executor. The verifier imports nothing from impl/, from crypto_autoresearcher or from any archived impl/ or review directory (asserted at start and exit); it is code-independent of both the engine and impl/, but NOT author-independent of impl/. Author-independent verification is the review round's (claim_tier_and_review joint 1).

## Sizes, shortfalls, output bound

- kept sizes: {'F-RANDX19': 600, 'N-AFF19': 250, 'N-CONV19': 250, 'N-ELL19': 250, 'N-F219': 250, 'S3-SAT100': 100, 'S3-U400': 400}; by role: {'F-RANDX19': {'sat': 0, 'unsat': 600}, 'N-AFF19': {'sat': 50, 'unsat': 200}, 'N-CONV19': {'sat': 50, 'unsat': 200}, 'N-ELL19': {'sat': 50, 'unsat': 200}, 'N-F219': {'sat': 50, 'unsat': 200}, 'S3-SAT100': {'sat': 100, 'unsat': 0}, 'S3-U400': {'sat': 0, 'unsat': 400}}; F-RANDX19 strata: {'TWIST': 200, 'X2E': 200, 'XE-NOT-2E': 200}.
- shortfalls / exhausted: {'F-RANDX19': {'TWIST': 0, 'X2E': 0, 'XE-NOT-2E': 0}, 'N-AFF19': {'1': {'sat': 0, 'unsat': 0}, '2': {'sat': 0, 'unsat': 0}, '3': {'sat': 0, 'unsat': 0}, '4': {'sat': 0, 'unsat': 0}, '5': {'sat': 0, 'unsat': 0}}, 'N-CONV19_exhausted': [], 'N-ELL19': {'sat': 0, 'unsat': 0}, 'N-F219': {'sat': 0, 'unsat': 0}, 'S3-PRIMARY': {'S3-SAT100': 0, 'S3-U400': 0}}.
- ann-v1 output bound applied: False (0 S3-U400 ann-v1 files not archived).

All counts above are measured on this run. Runtime and memory figures are in manifest.yaml (measured).

