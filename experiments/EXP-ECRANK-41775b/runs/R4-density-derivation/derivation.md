# R4 derivation — EXP-ECRANK-41775b (T3)

Executor artifact, RUN-ECRANK-41775b-R4-density-derivation. Theoretical
density derivation from the committed lineage records. OBSERVATION-ONLY
scope: this derivation locates two counted quantities in the committed
records and exhibits the formal distinction between them; it selects no
branch (STRUCTURAL-SCOPE / SCARCITY-REVIVED / DEFECT), draws no
conclusion about HEUR-1's truth, changes no status, and validates
nothing. Branch selection is a Coordinator act at the independent review
round. Exact rational arithmetic throughout (fractions.Fraction); no
floating point in any checked statement. Recalled pointers stay marked
recalled-not-verified and are shown not to be load-bearing.

Citation provenance classes used below: `internal` (this program's own
committed records, read in this task), `recalled` (external pointer from
model memory; no agent in this program opened it — a pointer for a
reviewer, never support).

---

## (a) The parameter space of HEUR-1's statement

**Step 1.** HEUR-1's formal statement (citation:
`ledger/hypotheses/H-ECRANK-ee6e0e.yaml`, HEUR-1 block, provenance
`internal`): for a fixed generic n-tuple b of distinct rationals and
squarefree d with mixed signs, the set
`{u in W'(b) : every u_i a nonzero rational square}` has counting
function `~ C(b,d) * H^(5 - n/2)` as the height bound H grows, with
`C(b,d) > 0` iff the system is solvable at every local place.
W'(b) is the 5-dimensional subspace `D^-1 W(b)`, where W(b) is the
evaluation image of quartics at b (mechanism M3, same record,
provenance `internal`).

**Step 2.** What grows with H in that statement: the COUNTED SET is
`{u in W'(b) : every u_i a nonzero rational square, height(u) <= H}` —
a lattice-point count in a FIXED 5-dimensional rational subspace, whose
box grows with H. The random-model justification (citation:
`ledger/hypotheses/H-ECRANK-ee6e0e.yaml` HEUR-1
random_model_justification; restated in
`ledger/hypotheses/H-ECRANK-36d8d7.yaml` HEUR-1 block, provenance
`internal` for both) is: points of a fixed 5-dimensional rational
subspace of height <= H number ~ H^5 (subspace lattice count), and each
coordinate of size ~ X is a rational square with probability ~ X^(-1/2)
(square-counting), under square-class equidistribution of
subspace-point coordinates.

**Step 3.** Why the exponent has the form 5 - n/2 in that regime (desk
arithmetic over Step 2's model, exact Fractions; spot check
`spot_1_exponent_form` in spot-check.json): the H^5 factor is the
subspace lattice count (5 free coordinates), and the equidistribution
model applies a per-coordinate square probability ~ H^(-1/2) to each of
the n coordinates, giving n/2 decades of suppression:
`5 - n/2` exactly: n=6 -> 2, n=8 -> 1, n=10 -> 0 (spot check values,
exact Fractions "2", "1", "0").

**Step 4.** The draw-side search realizes this growing space directly
(citation: `experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/
raw-result.json`, provenance `internal`): each draw seeds 5
r-coordinates from a height-H sub-box (parameters S_fixed_indices
[0,1,2,3,4], T_solved_indices [5,6,7], H_schedule_per_draw
[100,100,100,1000,1000,1000,10000,10000]) and solves the remaining
n - 5 coordinates exactly. The committed stream data: 80,000 draws
across 3 streams (26,672 + 26,664 + 26,664), all solves_ok, square_ok
0, found_instances 0, ops 8,683,560, exhaustion null. The candidate
count per b therefore GROWS with H by construction of the sub-box.

**Step 5.** Recalled pointers, marked recalled-not-verified, and shown
not load-bearing:

- Hasse-Minkowski local-global principle for quadratic forms in >= 5
  variables (citation as recorded in
  `ledger/hypotheses/H-ECRANK-ee6e0e.yaml` structural_ingredients:
  "J.-P. Serre, A Course in Arithmetic, Ch. IV", provenance `recalled`,
  verified_by null). NOT LOAD-BEARING for this derivation: it anchors
  only the n=6 local-solvability EXISTENCE reading of the parent
  hypothesis's P0 ("near-rigorous" label), which this experiment neither
  tests nor relies on. Steps 1-4 use only the internal records' own
  parameter counts and the committed draw-side bytes. Nothing in this
  derivation's conclusion chain passes through Hasse-Minkowski.
- The Schinzel-type / Nagao-style / Birch-type literature genre pointers
  in EV-ECRANK-8b35bb's resource_check (provenance `recalled` there):
  not used here at all; the random-model justification relied on is the
  internal one quoted in Step 2.

## (b) The construct arm's parameter count, from the bound bytes

**Step 6.** The construct arm's per-tuple candidate generation (citation:
`experiments/EXP-ECRANK-73275e/source/construct.py` at sha256
a16f903d7e7c3e381ad5e43d56dd272c467bf4f12d7ca664043fc7b5138f0581,
provenance `internal`; machine-verified by this experiment's R2 trace):
at n=6, g is linear with the monic normalization g = [t, 1] — 2
coefficients with 1 fixed by monicity, hence ONE free parameter t. The
ellipticity condition (the x^5 coefficient of delta*g^2 mod p vanishing)
is ONE quadratic condition in t: A t^2 + B t + C = 0 with (A, B, C)
computed from (b, dpat) alone (NF.d1_quadratic_coeffs or _n6_quad,
bound lines 74-75, 98-111). `_quad_rational_roots(A, B, C)` (bound lines
114-124) returns the COMPLETE rational root set of that single
univariate quadratic: at most 2 roots (Bezout), with NO H input. The R2
machine-checked trace (this experiment, R2-structural-trace/
trace-report.json) confirms: in solve_n6 (bound lines 65-95), H appears
ONLY at line 86, the post-solve admission filter `if h > H:`
(rejection with the exact height recorded), and in no
candidate-generation expression.

**Step 7.** Parameter count, exact: 1 free parameter (t), 1 quadratic
condition -> 0-dimensional solution set over the algebraic closure,
with at most 2 rational points per (b, dpat) tuple. The candidate
multiset per tuple is FIXED and H-INDEPENDENT; H enters only as the
admission filter on the already-computed root heights.

**Step 8.** Formal distinction between the two counted quantities:

- HEUR-1's quantity (Steps 1-4): a count over a POSITIVE-dimensional
  parameter space (the 5-dimensional subspace W'(b), or equivalently the
  draw-side H-growing sub-box of 5 seeded coordinates), whose box grows
  with H; the H^(5-n/2) law is a statement about that growing box.
- The construct arm's quantity (Steps 6-7): a count over a
  0-dimensional slice (at most 2 rational roots of one univariate
  quadratic per tuple, H-independent), taken over a FIXED b-sample
  (10^4 committed tuples); the cumulative count N_6(H) over the frozen
  sample is the cumulative height-distribution function of a FIXED
  finite multiset (kept roots plus re-admissible height-rejected roots),
  bounded above by 2 per tuple with >= 1 rational root, independent of H.

These are formally distinct counted quantities. The construct-side
cumulative count saturates at its finite ceiling by arithmetic (the
committed R3 measurement of this experiment records the ceiling exactly:
33 over the recoverable subset); the H^(5-n/2) law concerns the growing
parameter space of Steps 1-4 and is not testable by a count that is
bounded by a fixed finite multiset. This is a statement about the two
counted quantities as defined in the committed records; it is not a
verdict on HEUR-1's truth in its own regime.

## (c) CANDIDATE heuristic HEUR-1-C (text only; status proposed; never
validated here)

**Step 9.** The construct-side count law that IS testable on this arm,
per the frozen protocol's reformulation instruction, stated as a
CANDIDATE heuristic for future pre-registration only:

> HEUR-1-C (proposed): over a growing b-sample of affine-normal-form
> tuples (b_1 = 0, b_2 = 1, b_3..b_n distinct integers in the declared
> box), the expected number of kept construct instances grows as
> C * (b-sample size), where C = (feasible-tuple fraction) x (average
> multiplicity of kept roots per feasible tuple), with multiplicity
> bounded by Bezout at <= 2 per tuple at n = 6 (one univariate
> quadratic) and <= 8 at n = 8 (three quadratics). The b-box scaling —
> not an H-scaling — is the growth direction this arm can measure;
> C(b,d) > 0 is inherited from HEUR-1's local-solvability condition.

Committed data bearing on the constants at the tested scope (citation:
R12 raw bytes, provenance `internal`): feasible_tuples 22 of 10^4
declared tuples; found 33; multiplicity histogram {1: 12, 2: 11} (12
tuples with 1 kept root, 11 with 2); max multiplicity 2 (equal to the
Bezout bound at n=6). Status: PROPOSED. Nothing in this experiment
validates or refutes HEUR-1-C; validation would require a new frozen
contract with growing b-samples.

## (d) PROVES-TOO-MUCH control (P5 / C4) on the draw-side committed data

**Step 10.** The structural argument of Steps 6-8 (fixed H-independent
candidate multiset per tuple -> cumulative counts saturate) is applied
to the draw-side committed data of
`experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/`
(provenance `internal`) — the F1 regime of EV-ECRANK-8b35bb where growth
was measured.

**Step 11.** The explicit diverging step (machine-recorded in
proves-too-much-control.json): on the draw side, the candidate set per b
is NOT a fixed root set — each draw selects 5 r-coordinates from a
height-H sub-box (S_fixed indices 0..4; T_solved 5..7), and the sub-box
lattice size GROWS with H by construction (H_schedule_per_draw
[100,100,100,1000,1000,1000,10000,10000]). The number of distinct
candidate points per b grows with H, so the saturation premise (a FIXED
finite candidate multiset independent of H) is FALSE on the draw side.

**Step 12.** Control outcome: the structural argument does NOT predict
draw-side saturation — its premise fails at the sub-box selection step.
The committed draw-side data (square_ok 0 of 80,000 draws;
found_instances 0; growth measured on a growing search space per
EV-ECRANK-8b35bb F1) is not an object the argument addresses, and the
argument does not predict it saturates. NO DEFECT is recorded on this
control; the derivation readings of Steps 1-9 stand as recorded
observations.

---

## Provenance table (every citation with its class)

| Step | Citation | Provenance class |
|------|----------|------------------|
| 1, 2, 3, 5 | ledger/hypotheses/H-ECRANK-ee6e0e.yaml (HEUR-1 block, M3, structural_ingredients) | internal |
| 2 | ledger/hypotheses/H-ECRANK-36d8d7.yaml (HEUR-1 block, random_model_justification) | internal |
| 4, 10, 11, 12 | experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json | internal |
| 10, 12 | ledger/evidence/EV-ECRANK-8b35bb.yaml (F1 regime, obstruction block) | internal |
| 5, 9, 11 | ledger/evidence/EV-ECRANK-d7e05f.yaml (TENSION-REAL, N2R ratios) | internal |
| 6, 7 | experiments/EXP-ECRANK-73275e/source/construct.py at the frozen hash | internal |
| 6 | experiments/EXP-ECRANK-73275e/source-v2/n2r.py (conventions A/B) | internal |
| 9 | experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json | internal |
| 5 | Serre, A Course in Arithmetic, Ch. IV (Hasse-Minkowski) | recalled (NOT load-bearing; Step 5) |
| 5 | Schinzel/Nagao/Birch genre pointers (as recorded in EV-ECRANK-8b35bb resource_check) | recalled (not used here) |

Every numbered step's checked arithmetic is exact rational (Fraction);
spot checks are in spot-check.json; the control record is in
proves-too-much-control.json. This derivation records and locates
quantities; it adjudicates nothing.
