# EXP-MONO-12ce1c implementation notes

Executor: Claude Code, policy `executor-implementation`, effort `medium`, per
handoff `TASK-20260830-a1cb32`. Frozen contract:
`experiments/EXP-MONO-12ce1c/specification.yaml` (approved by coordinator,
2026-08-30). This document records HOW the contract was implemented, every
interpretation made where the frozen text left a genuine ambiguity, every
protocol deviation, and every unexpected finding. No hypothesis, experiment
or goal status is changed here; no verdict on H-MONO-45183a is rendered.

## Source layout

- `implementation/seed.py` — literal SHA-256 seed-derivation rule (`inputs.seed_derivation_rule`).
- `implementation/fields.py` — F_p and F_{p^2} arithmetic, square roots, Frobenius (conjugation).
- `implementation/curve.py` — prime/curve/factor-base construction (`inputs.prime_construction`, `curve_construction`, `factor_base_construction`), plus a same-order-companion-curve search used only by `measured_null_1`.
- `implementation/panel.py` — the 8-curve panel builder.
- `implementation/path1.py` — Path 1 of the dual-path cross-check: direct signed-sum construction in F_{p^2}, Frobenius-based observed permutation, and the H-MONO-45183a-A3 predicted permutation.
- `implementation/semaev_path2.py` — Path 2: S_4/S_5 via the resultant recursion (sympy), with a fast lambdify-based evaluation path (see "Performance note" below), plus the S_3-vanishing fixture check.
- `implementation/sublocus.py` — Stage 3 factor-base-sublocus signed-sum construction (real F_p arithmetic, reusing the F_{p^2} code with the imaginary part fixed at 0).
- `implementation/controls.py` — positive_control_1 (quartics vs Chebotarev), positive_control_2 (planted collision), measured_null_1 (cross-curve).
- `implementation/run_experiment.py` — orchestrator; writes `raw-result.json` per run.

## Interpretations of underspecified contract text (disclosed, not improvised silently)

1. **Domain split for replication.** `inputs.master_seed`/`domain` name a single
   fixed domain string, but `replication.seeds` lists TWO seeds, and
   `replication.interpretation` requires the categorical metrics to be
   identical across runs while the frequency metrics vary. A single fixed
   domain would make the two runs bit-for-bit identical (no replication at
   all). Resolution (documented, following the precedent in
   `experiments/EXP-MONO-a20e48/runs/*/manifest.yaml`, whose `domain` field
   embeds its run's seed): prime/curve-a/curve-b draws (panel construction)
   use the FIXED `panel_domain = "EXP-MONO-12ce1c/v1"` so both runs share the
   IDENTICAL 8-curve panel; every sampled draw (`spec-x`, `fb-x`, `quartic`,
   `crosscurve`, `plant`) uses `sampling_domain = "EXP-MONO-12ce1c/v1/run-<seed>"`,
   which does vary. Verified: both runs' panels are byte-identical (checked
   programmatically); M1/M2 are identical (0 and 1.000) across both runs;
   M3/M4 numbers differ slightly as expected from different sampling.

2. **Panel construction assignment.** The contract specifies HOW to construct
   a random-ordinary curve, a j=0 curve, a j=1728 curve, and CM curves, but
   not which of the 5 field_bits primes each panel slot uses. Built: RO1..RO4
   at the four smallest primes (t=0 accepted immediately at each, per the
   run's own transcript in `raw-result.json` `panel.curves[*].t_used`); J0
   and J1728 both at the 9-bit prime (421 — the only field_bits prime
   satisfying BOTH p=1 mod 3, needed for a non-supersingular j=0 curve, and
   p=1 mod 4, needed for a non-supersingular j=1728 curve; verified by direct
   search over the field_bits list, not assumed); two CM curves continuing
   the curve-a/curve-b stream at the smallest (7-bit) prime after RO1,
   tested against `curve.CM_FUNDAMENTAL_DISCRIMINANTS` (a declared list of
   small class-number fundamental discriminants — both hits landed on D=-11).
   Resulting panel (identical both runs):

   | role  | p    | A   | B   | N (=#E(F_p)) | trace | Z | tau | note |
   |-------|------|-----|-----|-----|-------|---|-----|------|
   | RO1   | 103  | 1   | 71  | 115 | -11   | 0 | 1   | random ordinary |
   | RO2   | 191  | 80  | 27  | 212 | -20   | 1 | 2   | random ordinary |
   | RO3   | 421  | 263 | 192 | 456 | -34   | 3 | 4   | random ordinary |
   | RO4   | 569  | 536 | 531 | 531 | 39    | 0 | 1   | random ordinary |
   | J0    | 421  | 0   | 192 | 381 | 41    | 0 | 1   | j=0 |
   | J1728 | 421  | 263 | 0   | 394 | 28    | 1 | 2   | j=1728 |
   | CM1   | 103  | 31  | 4   | 108 | -4    | 1 | 2   | CM, disc -11 |
   | CM2   | 103  | 23  | 27  | 100 | 4     | 3 | 4   | CM, disc -11 |

   **tau-coverage precondition MET**: {1, 2, 4} all present (RO1/RO4/J0 give
   tau=1; RO2/J1728/CM1 give tau=2; RO3/CM2 give tau=4). Stage 3 runs on the
   full panel. `cm_minimum: 2` and `j0_required`/`j1728_required` are all
   satisfied; `random_ordinary_minimum: 4` is satisfied.

3. **Path 2's factorization-based classifier speed.** Naive `sympy.Poly.subs`
   substitution into the fully-expanded S_4/S_5 templates costs ~75ms per
   specialization (measured), which at the required minimum of 2000
   specializations per (curve, m in {4,5}) across 8 curves would cost
   ~20 minutes on its own. Replaced with `sympy.lambdify` on the T-degree
   polynomial's coefficients (each a small polynomial in x1,x2,x3,A,B),
   giving numeric coefficient evaluation in native Python, then
   `sympy.Poly(..., modulus=p).factor_list()` only on the resulting small
   integer coefficient list. Measured: ~0.4ms/spec for S_4, ~6ms/spec for
   S_5 (both ~100-200x faster). Spot-checked to produce IDENTICAL
   factorizations to the slow `.subs`-based path on 594 specializations
   (0 disagreements) before being adopted as the production Path 2.

4. **`measured_null_2`'s "pre-treatment commitment" tension.** The contract's
   own text (`arms_and_controls.measured_null_2`) defines this null as
   "Same code path, same tuple count, same construction as the tau >= 2
   arms" for the tau=1 Stage-3 cells — i.e. it IS a subset of the Stage-3
   treatment output, not an independently drawable prior artifact. This is
   in tension with `ordering_control`'s "both measured nulls...committed by
   SHA-256 BEFORE any treatment specialization is classified." Resolution
   (disclosed, not decided silently): `measured_null_1` and both positive
   controls ARE independently drawn and SHA-256-committed strictly before
   any Stage-2/3 treatment draw (see `raw-result.json`
   `stage4_pretreatment.ordering_control`); `measured_null_2` is read off
   the tau=1 curves' own Stage-3 output after the fact, because the frozen
   contract text defines it that way. Flagged for reviewer as a genuine,
   unavoidable ambiguity in the frozen text, not resolved by this Executor
   beyond disclosure.

5. **`n_admissible` and a third, undocumented exclusion stratum
   ("nondistinct_roots").** The contract names exactly two exclusion strata
   at Stage 2 (ramified: f(x_i)=0; diagonal: repeated x_i). Constructing a
   well-defined PERMUTATION (needed for Frobenius cycle-type classification)
   additionally requires that the 2^{m-2} signed-sum x-coordinates be
   PAIRWISE DISTINCT for a given tuple — a genuinely third possible failure
   mode the contract does not name (nor does EV-MONO-a0a89c's boundary note
   "no analogue at m>=4" anticipate it, since it is an m>=4-only phenomenon:
   at m=3 there are only 2 roots, and their coincidence is already the
   Stage-0-scoped ramified/degree-drop case). This Executor added a THIRD,
   separately-counted exclusion (`n_nondistinct_roots_anomaly`, plus
   `n_infinity_anomaly` for a signed sum hitting the point at infinity, and
   `n_no_frobenius_match_anomaly` for an internal consistency check that
   never fired in either run), reported per-cell and NEVER pooled into
   M1/M2/M3's numerators or denominators, per the contract's own
   "never pooled" principle extended to this necessary addition. See the
   FINDING below: this exclusion is NOT statistically neutral with respect
   to M3, and that is disclosed prominently rather than hidden.

## Findings (measured, not interpreted as a verdict on H-MONO-45183a)

### Finding 1 — `measured_null_1` (cross-curve null) FAILS to show 4-cycles/3+1 types, and this appears to be forced by the math, not a classifier bug

Built exactly as specified: P_1, P_2 on curve E (RO3: p=421, A=263, B=192,
N=456); P_3' on a DIFFERENT curve E' of the SAME order N (found by exhaustive
search, `curve.find_same_order_curve`: A'=1, B'=45); the degree-4 polynomial's
roots x(eps_1 P_1 + eps_2 P_2 + eps_3 P_3') computed via the identical
chord-tangent addition code used everywhere else in this experiment (E's own
A only enters the doubling branch, essentially never hit by distinct-x
draws). Over 5000 trials/run (4986 and 4762 valid trials respectively), the
observed cycle-type histogram contains ONLY the two Kummer-allowed types
(identity, pure-2) — **zero 4-cycles, zero 3+1 splits, in either run.** This
contradicts the contract's own declared forced value
("4-cycles and 3+1 types appear at nonzero rate... If they do not, the
classifier is reporting an artifact of the construction... and Stage 2 is
void").

Before treating this as a classifier bug, this Executor checked the
algebra: Frobenius (the p-th power map on F_{p^2}/F_p) is a ring
automorphism fixing F_p, so it commutes with ANY rational function with
F_p-coefficients — in particular with the chord-tangent addition formula
itself, REGARDLESS of whether the points being combined lie on a common
curve. And for ANY point (x, y) with y^2 in F_p (whether or not (x,y) lies
on curve E specifically), Frobenius(y) = chi(y^2) * y exactly (a pure
square-root fact, independent of curve membership). Composing these two
facts shows Frob(Q_eps) = Q_{eps'} with eps'_i = eps_i * chi_i for EVERY
constituent point regardless of which curve (if any) it "belongs to" — so
the sign-torsor mechanism this contract's Part A relies on is a property of
the ADDITION FORMULA acting on square-root-valued points in general, not a
curve-specific fact. This Executor verified this reasoning against the
measured data (the observed cycle type distribution in the cross-curve
construction, `{(2,2): ~62%, (1,1,1,1): ~38%}` in run 1, matches a
mixed-character sign-torsor prediction using chi_3 = the quadratic character
of f_{E'}(x_3) rather than f_E(x_3) — i.e. STILL exactly the sign-torsor
structure, just with one generator's character measured against a different
cubic).

**Disposition applied literally per the contract's own text**: Stage 2's
results are flagged `stage2_void_by_measured_null_1: true` in every run's
`raw-result.json`, and this finding is reported prominently rather than
suppressed or silently reinterpreted. This Executor does NOT decide whether
this renders the contract's own forced-value claim mis-specified (an
interesting possibility this finding raises: the null may be
UNSATISFIABLE BY CONSTRUCTION rather than failed by classifier defect) —
that judgment is left to the Validator/Red Team/Coordinator, per the
handoff's "record observations only, no verdict" instruction.

### Finding 2 — Stage 2's M3 (split-completely frequency) shows large, curve-dependent deviations from the naively-extrapolated forced formula at m=4,5, traced to a selection-bias mechanism, NOT a classifier defect

M1 (categorical violation count) is exactly 0 and M2 (per-instance match to
the H-MONO-45183a-A3 predicted permutation) is exactly 1.000 across EVERY
(curve, m) cell in BOTH runs — the CORE categorical claim of Part A. But M3
(measured split-completely frequency vs. the preregistered
`(S^{m-1}+N_ns^{m-1})/p^{m-1}` formula) shows sigma-deviations up to ~24 at
m=5 on the smallest-order curves (CM2, N=100: measured 0.0419 vs forced
0.1121), while agreeing closely (sigma < 3) at m=3 and on larger-order
curves.

Diagnosis (measured, reported for transparency): the `nondistinct_roots`
exclusion (Interpretation 5 above) is NOT statistically neutral. When ALL
m-1 characters agree (the identity/split-complete case), every constituent
point is genuinely F_p-rational, so the 2^{m-2} signed sums all land inside
the SMALL finite group E(F_p) of order N — with N as small as 100 on this
toy panel and up to 8 combinations (m=5), a birthday-paradox-style
accidental x-coordinate coincidence among the 8 sums has probability of
order C(8,2)/N, non-negligible for N~100-500. When the characters are
MIXED, the relevant points live in the much larger group of order
~(p+-1)(p-+1)-ish over F_{p^2}, making such accidental collisions far
rarer. Since a coincidence triggers exclusion (`n_nondistinct_roots_anomaly`)
BEFORE the split-complete count is tallied, split-complete (identity-type)
instances are excluded from `n_admissible` at a MUCH HIGHER rate than
mixed-type instances, on small-N curves, biasing M3_measured DOWNWARD.
Measured support: the two curves with by far the worst M3 deviations (CM1,
N=108; CM2, N=100) also have by far the highest
`n_nondistinct_roots_anomaly` rates at m=5 (11.4% and 24.2% of all draws,
vs 0.7%-7.4% on the other six curves); full per-curve table in
`raw-result.json` and reproduced in `execution_report.yaml`.

This is reported as a TOY-SCALE INSTRUMENT LIMITATION (small p relative to
the 2^{m-2} combinatorial count at m=5), not a mathematical claim about the
Galois group, and not evidence for or against H-MONO-45183a's M3 prediction
— the M1/M2 categorical results, which do not depend on well-defined
frequency conditioning in the same way, are the load-bearing measurement of
Part A and are unaffected.

### Finding 3 — the fixed-sign and random-sign sublocus arms are EXACTLY equal, per tuple, by a provable invariance (not by sampling luck)

Every Stage-3 (curve, m, sign-convention) cell's `mean_D`,
`P_at_least_one_collision`, and `max_D_observed` are IDENTICAL between the
`fixed` and `random` sign conventions, in both runs. This is not a bug (the
underlying factor-base x-coordinates and the sequence of tuple-index draws
are the same for both conventions by construction, since the sign choice
does not affect the SET of factor-base x-values); the mathematical content
is that flipping a point's sign (P_i -> -P_i) merely relabels which
sign-vector maps to which resulting sum, leaving the MULTISET of resulting
x-coordinates (hence the collision count D) exactly invariant. Consequence:
HEUR-KUM-1's sibling assumption HEUR-COIN-1's stated falsification
condition ("the fixed-sign and random-sign sampling arms disagreeing")
appears to be UNSATISFIABLE BY CONSTRUCTION for this specific collision
statistic, for the same reason Finding 1's null cannot show 4-cycles: the
addition-formula's functorial behavior under sign flips is a property of
the construction itself, not a sampling accident this measurement could
have caught. Reported for reviewer attention; not a verdict on HEUR-COIN-1.

## Protocol deviations (summary; each also appears above with detail)

1. Domain split for replication (Interpretation 1) — no seed_derivation_rule
   change, only which fixed string plays the role of `domain` for panel vs.
   sampling draws.
2. Panel-slot-to-prime assignment (Interpretation 2) — a concrete, documented
   choice within the algorithm the contract specifies exactly.
3. Path 2 lambdify optimization (Interpretation 3) — same resultant, same
   factorization, ~150x faster; spot-checked against the slow path.
4. `measured_null_2` read off Stage-3 output rather than independently
   pre-committed (Interpretation 4) — an unavoidable tension in the frozen
   text, disclosed rather than silently resolved either way.
5. A third exclusion stratum (`nondistinct_roots`) not named by the contract,
   required for a well-defined permutation at m>=4 (Interpretation 5) —
   reported separately, never pooled, and shown (Finding 2) to bias M3.

## Trial counts

All FULL contract-required minima were used — no proportional reduction was
needed (measured full-run wall time ~123s and ~121s, respectively, against a
7200s budget cap):

| quantity | count |
|---|---|
| Stage 2 specializations per (curve, m) | 20,000 |
| Stage 3 sublocus tuples per (curve, m, sign-arm) | 20,000 |
| Dual-path cross-check subsample per (curve, m in {4,5}) | 2,000 |
| positive_control_1 quartics | 20,000 |
| positive_control_2 planted trials per (curve, m) | 1,000 |
| measured_null_1 cross-curve trials | 5,000 |

## Dual-path cross-check summary

Fixture checks (both runs, identical since seed-free): `deg_T S_4 == 4` as a
FULLY SYMBOLIC identity (x1,x2,x3,T,A,B all symbolic) — the strongest
possible form of this check, done once, not per curve. `deg_T S_5 == 8` was
checked operationally (per the contract's own framing as "a fixture check",
not a new theorem) across the dual-path cross-check's own S_5 instances;
every instance observed degree exactly 8 (no drop). `S_3` vanishing at
x(P+Q) and x(P-Q) verified on real curve points from 3 panel curves (12
point-pairs total), 0 failures.

Cross-check totals (both runs): **32,000 specializations checked
(2,000 x 8 curves x 2 m-values), 0 disagreements**, in both runs.

## Environment

Pure Python 3.13.1 + sympy 1.14.0 (available in this session, contradicting
the contract's stale 2026-08-05 note that recorded sympy's absence — the
contract's actual requirement is "no CAS needed," which this implementation
also satisfies for Path 1 and the classification logic; sympy is used only
in `semaev_path2.py` for Path 2's resultant/factorization, exactly as the
handoff permits). No numpy, no Sage.
