# RUN-CERTBIN-c417e0 -- EXP-CERTBIN-e94b27 (RC-1) run report

Task TASK-20260924-41c7be. Validity status: **completed_valid**. Observations only; no hypothesis status, evidence record or knowledge entry is written or implied here.

## Claim tier and scope (verbatim from the specification)

- claim_tier: toy
- statement: Refutation-degree measurement on archived instances of one cell: n = 17, f = t^17 + t^3 + 1, m = 2, l = 9, polynomial V = {deg < 9}, curve A = 97044, B = 126251 (#E = 4 * 32603), subgroup targets, under the closures M_4, W_4, M_5 and W_5 as defined below.
- sota_delta: zero on every ECDLP cost axis
- dominated_by: Per attempt at m = 2: oracle A (2^9 = 512 quadratic root-findings) decides satisfiability and returns the solutions; it dominates every closure measured here (a D = 5 elimination is 16796 x 12616 over F_2). For the DLP: parallel Pollard rho (about 160 group operations at q = 32603). FES GPU exhaustive search (KN-LIT-287) and WDSat not compared.
- affected_vs_safe: No deployed or standardized curve is touched or affected.

## Independence disclosure (EX-10)

The same executor wrote the closure engine (impl/) and the verifier (verifier/). Their independence is code-level only: verify_cert.py imports nothing from impl/ or EXP-CERTBIN-4e92d7/impl/, rebuilds f_0..f_16 by evaluating S_3 at all 2^18 points with its own F_{2^17} arithmetic plus a Moebius transform, and runs as a separate process. It is NOT author-independent; the author-independent second verification belongs to the review round.

## Instrument checks

- C-SRC: PASS
- C-SELF: PASS
- C-FIX: PASS
- C-BASE: PASS
- C-ORACLE: PASS
- C-MONO: PASS
- C-PS1: PASS
- C-CERT: PASS
- C-VERIFIER: PASS
- C-NULLS: PASS
- C-DET: PASS
- X-CONSISTENCY (informational, not a spec control): PASS

## Primary metrics (verified certificates only)

- MR1 a = 62/62, CP95 [0.942237365570709, 1]
- MR2 b = 62/62, CP95 [0.942237365570709, 1]
- MR3 r = 62/62, CP95 [0.942237365570709, 1]; U62 labels: {"W4": 62}
- MR4 N-AFF62: W_4 0/62 CP95 [0, 0.0577626344292909]; M_5 62/62 CP95 [0.942237365570709, 1]; W_5 0/0 CP95 [None, None]
- MR4 N-F262: W_4 0/62 CP95 [0, 0.0577626344292909]; M_5 62/62 CP95 [0.942237365570709, 1]; W_5 0/0 CP95 [None, None]
- MR5 refuted satisfiable controls (S62): {"W_4": 0, "M_5": 0, "W_5": 0} of {"W_4": 62, "M_5": 62, "W_5": 10}; certificates {"submitted": 268, "verified": 268, "failed": 0, "uncertified": 0}

## Decision rules (applied mechanically)

- RC1-DR-1: ARTIFACT (predominant)
- RC1-DR-2: CLEAN (L1 = CLEAN, L2 = CLEAN); residue idx: []
- RC1-DR-3: M_5 SUFFICES
- RC1-DR-4: W_4: S_3-SPECIFIC at W_4; M_5: NOT DISTINGUISHED at M_5
- RC1-DR-5: PASS
- RC1-DR-6: RC1-DR-2 returned CLEAN; clean_or_near_clean = True (recorded, not decided here)
- RC1-DR-7: primary verdicts: {"RC1-DR-1": "ARTIFACT (predominant)", "RC1-DR-2": "CLEAN"}

## Pre-registered predictions PA-1..PA-3 (H-CERTBIN-5e71c9 C1): threshold readings

- PA-1: a = 62. held (a >= 56, E-A threshold). E-G threshold (a <= 6): not met; E-G falsified by the frozen rule (a >= 32): True.
- PA-2: r = 62; label CLEAN (CLEAN iff r = 62; NEAR-CLEAN iff 59 <= r <= 61; RESIDUE iff r <= 58).
- PA-3: refuted satisfiable controls = 0; held.

## Coordinator prior (a)-(d): which parts the observations contradict

- (a) modal expectation a in [15, 50] (MIXED): observed a = 62 -> overturned (observed outside the modal range).
- (b) b >= 56 and D <= 5 picture CLEAN or NEAR-CLEAN: observed b = 62, DR-2 CLEAN -> consistent.
- (c) 'NOT DISTINGUISHED at M_5' expected, observed 'NOT DISTINGUISHED at M_5'; nulls near 0 at W_4 and, if a >= 10, 'S_3-SPECIFIC at W_4' expected; observed null W_4 counts [0, 0], 'S_3-SPECIFIC at W_4' -> consistent.
- (d) every W_4 / M_5 refutation certifies: failed = 0, uncertified = 0 -> consistent.

## Secondary observations

- 2 x 2 (W_4 verified refutation) x (M_5 verified refutation): {"U62": {"W4+M5+": 62, "W4+M5-": 0, "W4-M5+": 0, "W4-M5-": 0}, "N-AFF62": {"W4+M5+": 0, "W4+M5-": 0, "W4-M5+": 62, "W4-M5-": 0}, "N-F262": {"W4+M5+": 0, "W4+M5-": 0, "W4-M5+": 62, "W4-M5-": 0}}
- Plain-Macaulay D* of the F-S3 unsat arm extended to D = 5: {"4": 324, "5": 62, ">5": 0} (a reading; no verdict on HEUR-CERTBIN-TS4)
- Combined unsat-arm rates at the Stage-1 cell: W_4 386/386; any closure at D <= 5 386/386 (324 inherited via monotonicity, checked on C20)
- U62: iteration at which 1 first appears in W_4: {"1": 62}; ell in W_4 cap B_<=1 on 62/62
- Certificate sizes per closure: {"W_4": {"count": 82, "min": 1296, "median": 1359.5, "max": 1542, "max_deg_mu_max": 3, "max_deg_mu_distribution": {"2": 20, "3": 62}}, "M_5": {"count": 186, "min": 1296, "median": 4908.0, "max": 5091, "max_deg_mu_max": 3, "max_deg_mu_distribution": {"3": 186}}, "W_5": {"count": 0, "min": null, "median": null, "max": null, "max_deg_mu_max": null, "max_deg_mu_distribution": {}}}

## Scope

Toy tier. One cell: n = 17, f = t^17 + t^3 + 1, m = 2, l = 9, V = {deg < 9}, curve A = 97044, B = 126251, archived subgroup targets of RUN-CERTBIN-3b7e05. Nothing here transfers to other n, other curves, F4 step degrees or Semaev's Assumption 1. A non-refutation at W_5 concerns derivations of a-priori degree <= 5 only. No discrete logarithm and no relation is claimed; sota_delta zero; oracle A and parallel rho dominate.

