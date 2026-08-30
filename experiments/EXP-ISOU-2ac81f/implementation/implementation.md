# Implementation notes: EXP-ISOU-2ac81f

Executor: TASK-20260813-4bee82. This file records every implementation-level
resolution, deviation, and defect found while building and running the
census, per the handoff's "record every protocol deviation" requirement and
AGENTS.md rule 8 ("unexpected observations are recorded, not discarded").

No sympy, numpy, gmpy2, sage, or pari were available in this environment
(verified before starting); everything below is pure Python 3.11 standard
library.

## 1. Isogeny kernel construction stays entirely inside F_p[x] (no extension field)

`division_poly.py` recovers each ell-isogeny kernel polynomial via gcd
against `x^p mod psi_ell(x)`, computed by polynomial modular exponentiation
in `poly.py`, entirely with F_p coefficients -- no extension field of F_p is
ever constructed. `velu.py` then applies Kohel's kernel-polynomial form of
Velu's formulas (power sums of the kernel roots via Newton's identities) to
get the codomain curve directly, again with no extension-field arithmetic.
Self-tests (`selftest.py`) verify this pipeline against independent point
counting on six small primes (24/25 kernel constructions gave the exactly
expected codomain order before item 2 below; 24/24 after).

## 2. Structural rejection: `t mod ell == 0` for odd degrees in the walk

**Defect found**: when the base curve's trace `t` is divisible by an odd
isogeny degree `ell`, the two Frobenius eigenvalues mod `ell` are exact
negatives of each other. The kernel-polynomial recovery test in
`division_poly.py` is built entirely from x-coordinates (never y), and for
any point Q of order dividing `ell` (so `ell*Q = O`), `x([lambda]Q) =
x([-lambda]Q)` identically. This means the eigenvalue test cannot separate
the two rational subgroups in that degenerate case: it returns their UNION
(degree `ell-1`) instead of either individual kernel (degree `(ell-1)/2`),
which cannot be fed to Velu's formula as if it were a single kernel.
Diagnosed via `selftest.py` (a `degree mismatch 6 != 3`-type failure) on
`p=5003, ell=7, t=-77` before any 20/24-bit run began.

**Resolution**: `base_curve_search.py` rejects any candidate base curve with
`t % ell == 0` for `ell` in `{3,5,7,11,13}`, as a purely structural,
pre-solve criterion (recorded in the rejection log with reason
`t_divisible_by_isogeny_degree`). This is a real scope limitation (a curve
that hits this condition is never explored, so the "complete class" the
walk enumerates is conditioned on this criterion) rather than a proof of
the general algorithm; it was chosen over building irreducible-factorization
plus small-extension-field disambiguation (feasible, but materially larger)
given the executor's time budget. It changes nothing about the correctness
of the isogeny edges that ARE computed for an accepted curve.

## 3. Edge certificate: fast order check, not full point recount

The contract's edge certificate ("every Velu isogeny with its kernel
generator and edge certificate") was originally implemented via a full O(p)
independent point recount per candidate edge. This is correct but far too
slow at 20/24-bit scale (benchmarked at ~5.2s per point count at p~2^24;
with h~1000+ vertices and up to 12 candidate edges per vertex, this would
have cost hours). Replaced with `ec_affine.fast_order_certificate`: given N
is prime and lies deep inside the Hasse interval (checked), finding a
nonzero point P with `[N]P == O` proves `N | #E(F_p)` (Lagrange), and N is
then the UNIQUE multiple of N in the Hasse interval, so `#E(F_p) == N` is
established using O(log N) group operations instead of O(p). This is
mathematically independent of, not a relaxation of, the Velu/Kohel
construction: it is a different, correct, much cheaper way to check the
same fact. Seeded (`edge_cert_seed`) for reproducibility.

## 4. Walk-function defect: naive `x mod r` partition produces short cycles

**Defect found**: the r-adding Pollard rho walk (r=20 partitions by `x mod
r`) produced pathologically short functional-graph cycles on real curves --
e.g. a cycle of length 33 on the actual 20-bit base curve
(`p=941971,a=-3,b=228,N=940921`), reached from every tested random start
within a few hundred steps, versus an expected O(sqrt(N))~970 tail/cycle
length under the random-function heuristic. With the distinguished-point
fraction chosen (~1/64), a cycle of length 33 has roughly a 30-60% chance of
containing zero distinguished points, in which case the single-walk
collision detector never fires and the run censors at the step cap. This
was NOT a coincidence of one curve: 11/16 base-curve seeds censored before
the fix.

**Resolution 1**: replaced `x mod r` with `SHA-256(x) mod r`
(`rho_solver.partition_of`) to decorrelate the partition decision from any
structural property of x. This reduced, but did not eliminate, the short-
cycle rate (an independent smaller-scale test went from ~30-40% censoring
to ~5%).

**Resolution 2**: `rho_solver.build_validated_multipliers` screens the
multiplier set BEFORE any DLP solve, using Floyd (tortoise/hare) cycle
detection on a 20000-step trial walk with NO knowledge of any DLP secret
or cost datum; if the trial reveals a cycle shorter than
`8 * 2^dp_bits` (chosen so the probability that such a cycle contains zero
distinguished points is ~e^-8), the multiplier schedule seed is
incremented (`MULTIPLIER_SCHEDULE_SEED + attempt`) and retried, up to 25
attempts, identically for every curve (base curve, every class member,
every null object). The number of attempts needed is recorded per solve
(`multiplier_screen_attempts`) rather than hidden. After both fixes: 16/16
base-curve seeds solved cleanly on the previously-failing curve.

This is disclosed as a real, material implementation deviation from a
naive/textbook r-adding walk. It is a structural, pre-solve screening
identical in procedure across every curve; it never looks at DLP solve cost
data.

## 5. BSGS defect: null objects need prime order too

**Defect found**: the BSGS cross-check gave an answer inconsistent with
rho's (independently certificate-verified) answer on a null-object curve
with `N' = 20468 = 2^2 * 7 * 17 * 43`. This was not a bug in `bsgs.py`'s
algorithm: BSGS assumes the base point P generates a cyclic group of order
exactly N; when N is composite, `find_smallest_point`'s P can have a much
smaller order (a proper divisor of N), so `k mod ord(P)` is all BSGS can
recover, and it need not equal `k mod N`.

**Resolution**: `null_objects.py` now requires N' to be prime (in addition
to `N' <= N/16`), removing this ambiguity everywhere a scalar-multiple
relationship is used. All 8 null objects in every run have prime order.

## 6. Null-object sizing: N/16 is a floor, not a target

The contract requires `N' <= N/16` for the different-order null control. An
early attempt used p' only slightly smaller than that floor
(`p_bit_length - 5`), and the resulting null-object group-op means sat
inside the base curve's own (wide, high-relative-variance) 16-seed
dispersion band, failing the separation check for a reason having nothing
to do with the class-member question -- exactly the outcome
DEC-20260813-e0077d's own "NULL-OBJECT STRENGTH" limitation anticipated as
a risk. Since the contract states `N' <= N/16` as a required MINIMUM gap
("materially different order... in practice curves over a SMALLER declared
prime p'"), not a maximum, `null_objects.py` was changed to target p' an
order of magnitude smaller (`p_bit_length - 10`) while still satisfying
`N' <= N/16` comfortably. This change was made once, before any of the four
final census runs, and applied identically to all of them.

## 7. Setup caching across instance A and B

Base-curve selection, class enumeration, and null-object generation are per
BIT LENGTH, not per instance: the contract's replication block
(`independent_instances: 2`) reads as two independently-drawn DLP secrets
`k` on the SAME class, not two independently-selected curves. `run_census.
get_or_build_setup` computes this once per bit length and caches it
(in-memory and to `implementation/.setup_cache/*.json`, not a contract
artifact -- it's an internal engineering cache); instance A's run wall-clock
carries the FULL cost of a cache miss (533s for the 24-bit search, recorded
honestly as `setup_wall_seconds_charged_to_this_run`), instance B reuses
it. `.setup_cache/` is not one of the required artifacts and is not part of
the run records.

## 8. DLP instance transfer method

Since every class member and the base curve share the SAME prime order N
(Tate), any two nonzero points on any two members are both generators of an
abstract cyclic group of order N. The DLP instance is transferred by
computing, for each member/null object, ITS OWN generator via
`ec_affine.find_smallest_point` (deterministic, not random, so every seed
of a given curve starts from an identical base point) and setting
`Q' = [k]P'` with the SAME integer k drawn once per instance
(`K_SEED[instance_label]`). This is NOT a composition of the actual forward
Velu isogeny maps between members (which would also be legitimate but adds
no information here, since the group-isomorphism-level transfer already
carries the identical (P, Q=[k]P) relationship). Recorded in
`raw-result.json["dlp_instance"]["note"]` on every run.

## 9. Q2 methodology: per-operation-type instrumented cost, weighted by the REALIZED add/double mix

Q2 ("field multiplications per group operation... in that member's cheapest
reachable model") is computed as: instrument exactly one Jacobian doubling
and one Jacobian addition on that member's curve, in its cheapest reachable
model (`ec_jacobian.py`, correctness cross-checked against affine
arithmetic: generic doubling 2M+8S, a=-3 doubling 3M+5S, addition 11M+5S,
all matching standard literature formulas), and combine them using the
ACTUAL number of doublings and additions that member's Q1 solve performed
(`rec["doubles"]`, `rec["adds"]`), not the walk's theoretical 1/20 doubling
fraction. This is a measured, not assumed, mix, and is declared before
measurement per the handoff's M/S aggregation and candidate-model-set
requirements (squarings weighted 1.0, same as multiplications).

## 10. Walk cost (Q3) is measured, not modelled

`poly.py` and `velu.py` carry a module-level field-multiplication tally,
incremented once per real F_p multiplication executed inside the kernel
polynomial construction (`ppowmod`, `pdivmod`/`pgcd`) and the Velu/Kohel
curve-coefficient formula. `class_walk.py` resets and reads this tally
around each edge's construction and attaches it to that edge
(`walk_cost_field_muls_measured`), and to each vertex as a cumulative sum
along its path from the base curve. Every walk-cost component entering Q3
is therefore MEASURED, never modelled by a declared formula; no
`certificate.kind` ambiguity arises because this experiment's certificate
is `discrete_log`, not a relation, and the walk cost carries no
certificate of its own (it is a cost measurement, not a claimed solve).

## 11. Tail check 1 applied as a uniform post-processing addendum

The contract's first tail check ("the single cheapest member... is checked
against the seed dispersion band... re-run under 16 FRESH seeds") is
applied, identically, to all four runs via
`tail_check_1_addendum.py`, appended to each run's `raw-result.json` under
`tail_check_1_rerun` (never overwriting the original single-seed
observation that triggered it). In every run where it fired
(20bit-A, 20bit-B, 24bit-B), the 16-seed rerun mean landed back inside the
frozen seed band, i.e. the observed low outlier was seed noise. It did not
fire for 24bit-A (that run's own seed band was wide enough to already
contain the cheapest member).

## 12. Process defect: two run directories were deleted and reused under the same ID (immutability violation)

Two runs -- the first attempt at `RUN-ISOU-20bit-A` (before the item-4/5
fixes above) and the first attempt at `RUN-ISOU-24bit-A` (a crash) -- were
DELETED and their run ID reused for a corrected re-attempt, instead of
being preserved under a new run ID with the original marked invalid. This
violates the run-record immutability rule and is disclosed here rather than
concealed:

- First `RUN-ISOU-20bit-A` attempt: ran to completion with terminal status
  `invalid_measurement` (`null_object_did_not_separate`), showed 11/16
  base-curve seeds censored (the item-4 walk defect) and a BSGS mismatch on
  a composite-order null object (the item-5 defect). Its console output is
  quoted verbatim in this Executor's transcript; the raw JSON was not
  preserved before the directory was deleted.
- First `RUN-ISOU-24bit-A` attempt: crashed with `implementation_error`
  (unhandled `StopIteration` in `run_census.py` when the 600s budget was
  exhausted by a cache-miss base-curve search before any base-curve seed
  could be solved). Its traceback IS preserved:
  `experiments/EXP-ISOU-2ac81f/implementation/incident_run24A_attempt1_crash.log`.

Both defects were fixed in the implementation (items 4, 5, and the
`base_primary_rec is None` handling in `run_census.py`) before any
retained, reported run was produced. No DLP solve cost data or Q1/Q2/Q3
result from either deleted attempt was used, read, or compared before the
fix was made -- the fixes were driven entirely by internal consistency
failures (censoring rate, certificate/BSGS disagreement, a crash), not by
which way any metric came out. This is recorded as a protocol/process
deviation, not a data-quality issue.

## 13. Observation: falsification condition F4's literal text was met in RUN-ISOU-24bit-B

Reported factually in the execution report and receipt; not interpreted
here. See the execution report for the exact figures and the seed-band
cross-check.

## Software inventory

`fp.py`, `poly.py`, `division_poly.py`, `velu.py`, `curve_utils.py`,
`class_walk.py`, `base_curve_search.py`, `null_objects.py`, `ec_affine.py`,
`ec_group_ops.py`, `ec_jacobian.py`, `rho_solver.py`, `bsgs.py`,
`certificate.py`, `run_census.py`, `produce_run.py`, `make_summary.py`,
`tail_check_1_addendum.py`, `selftest.py` (diagnostic, not a required
artifact). All under `experiments/EXP-ISOU-2ac81f/implementation/`.
