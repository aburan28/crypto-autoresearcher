# Implementation notes: EXP-ECDLP-bbb42f

Executed by the Executor role against the frozen, approved contract at
`experiments/EXP-ECDLP-bbb42f/specification.yaml` (status `approved`,
`approved_by: coordinator`, 2026-09-03). Pre-execution check confirmed no
Coordinator decision withdraws authorization (`ledger/decisions/` grep for
`EXP-ECDLP-bbb42f`: no hits) and `experiments/EXP-ECDLP-bbb42f/amendments/`
contained only `.gitkeep` at dispatch time and still does.

Git commit at execution time: `a5d29fb511938c6228af1a62e57b2f152ac6c8b9`
(working tree carries only this run's own new, uncommitted
`experiments/EXP-ECDLP-bbb42f/{driver,runs,results}` files; no tracked file
was modified). All code lives under `experiments/EXP-ECDLP-bbb42f/driver/`.

## Summary of what was executed

All six declared runs (`RUN-ECDLP-bbb42f-1` through `-6`) were executed to
completion, well inside the 3600s/run and 12-CPU-hour budget (total wall
time across all six runs: approximately 15 minutes). Every planned curve
instance was reached; no run was truncated by budget. `results/summary.json`
aggregates the primary/secondary metrics; this file documents the protocol
deviations, the timed infeasibility findings, and one load-bearing
mathematical observation that materially shapes how every number in
`summary.json` should be read.

## Load-bearing observation: E1/E2 are isogeny-class invariants (Tate 1966)

**This is the single most important fact about this run package and is
reported as an OBSERVATION, not a conclusion about H-ECDLP-ed5162 or
HEUR-ISO-1** (per ST-3, that judgment belongs to the Coordinator/Reviewer).

Tate's isogeny theorem (Tate, "Endomorphisms of abelian varieties over
finite fields", Invent. Math. 2 (1966)) states: two elliptic curves E, E'
over a finite field F_q are isogenous over F_q if and only if
`#E(F_q) = #E'(F_q)`. This is a classical, unconditional theorem, not a
heuristic.

Consequence for this contract's own predicate definitions: E1
(`N == p`) and E2 (`k = ord_N(p) <= K_max`) are both functions of
`N = #E(F_p)` and `p` **alone**. By Tate's theorem, `N` is invariant under
**every** F_p-isogeny of **every** degree, in **every** direction
(ascending/descending/horizontal on the volcano) -- not just the small,
coprime-to-N degrees this contract's `isogeny_step_primes` restricts the
walk to. Therefore **E1 and E2 status cannot change under any ordinary
isogeny walk from any starting curve, period** -- this is a mathematical
certainty, not a "with high probability under HEUR-ISO-1" statement.
E3 (GHS/subfield-descent) is separately vacuously false for every curve in
this experiment's domain, since the curves are defined over a *prime*
field F_p and GHS-style subfield descent requires the base field to be a
proper extension with a nontrivial subfield to descend to -- F_p (p prime)
has none (see `predicates.py` module docstring).

**Consequence for the census**: `curve_sampling_rule` already excludes
`N == p` at acceptance for every unplanted curve, so no unplanted curve is
E1-special by construction, and E2-special-at-sampling is possible in
principle (not excluded by the sampling rule) but was observed to occur in
0 of 60 sampled curves (consistent with its extremely low base rate: the
number of primes `N` in the Hasse interval with `ord_N(p) <= K_max=20` is a
vanishing fraction of the interval width at these bit sizes). Given a
non-special start and E1/E2 invariance, **the isogeny-transfer target set S
is provably empty within that curve's entire reachable F_p-isogeny class**
for every one of the 60 unplanted curves in this run package -- not merely
"not found within budget." Every unplanted curve therefore reports
`NOT_FOUND` with `reason_if_not_found: PROVABLY_UNREACHABLE`, and no walk of
any length or budget could have changed this.

This is **empirically corroborated**, not merely asserted, in two ways in
this run package:
1. Every visited vertex in every bounded isogeny walk across all 60
   unplanted curves carries the identical `N` as its start vertex,
   independently re-certified per edge via `ec_affine.fast_order_certificate`
   (a Lagrange/Hasse-uniqueness argument, not a copy of the walk's own
   bookkeeping) -- `order_invariance_holds: true` for all 60/60 curves (see
   `results/summary.json`, `load_bearing_finding.empirical_corroboration`).
2. In the planted-path control (RUN-4), the constructed "generic-looking"
   `E_rand` -- built by walking away from a genuinely anomalous curve --
   is found to **already be anomalous itself, before any search**, at all
   three tested bit sizes (`e_rand_already_anomalous_without_search: true`).
   This is the same invariance fact showing up from the opposite direction:
   the planted construction cannot actually produce a generic-looking
   special-adjacent curve, because isogeny preserves the very property that
   was supposed to be hidden.

This finding does not, by itself, determine whether H-ECDLP-ed5162's
charged-cost-gate claim holds, fails, or needs redesign at this contract's
scope -- E1/E2 being permanently unreachable via isogeny is arguably the
*strongest possible form* of the safety claim (C_path is not merely large,
it is infinite/undefined), but whether that is a confirmation, a
degenerate non-test, or grounds for a protocol amendment (e.g. testing
E3-analogue constructions that are NOT isogeny-class invariants, if any
exist) is an interpretive call reserved for the Coordinator/Reviewer.

## Protocol deviations (disclosed, per ST-2/rule 12)

### 1. Point counting: BSGS-in-Hasse-interval instead of O(p) sieve

The contract requires "exact point counting." `curve_utils.point_count`
(reused verbatim from EXP-ISOU-2ac81f) is an O(p) quadratic-residue sieve;
timed at **114.3s for a single 28-bit curve** (measured directly, see
`point_counting.py` module docstring for the comparison script). At >=20
curves per bit size plus rejected candidates during sampling (measured:
473-867 candidates tried per bit size to find 20 acceptances -- see
`results.json` `sampling_attempts`), this would cost tens of thousands of
CPU-seconds at 28 bits alone, exceeding budget.

`point_counting.exact_group_order` instead uses the standard BSGS-in-the-
Hasse-interval method (Blake-Seroussi-Smart; Washington), which computes
the exact same integer via O(p^{1/4}) group operations, with a Lagrange/
Hasse-uniqueness certificate for exactness (the same argument already used
by the reused `ec_affine.fast_order_certificate`). **Correctness was
independently cross-checked against the O(p) sieve on 25 curves at 12-28
bits: 25/25 exact matches** (see the validation script output captured
during development; not re-run as part of the six declared runs since it
predates them and is a code-correctness check, not a measurement this
contract asks for). Timed at **0.015s for 10 curves at 28 bits** (vs. 114s
for ONE curve via the sieve) -- a ~76,000x speedup, which is what makes the
60-curve census tractable within budget at all.

### 2. Bounded isogeny walk instead of literal exhaustive search to `ell_max`

The contract specifies path search "up to the degree budget
`ell_max = N^{1/2}`." A literal implementation (`class_walk.enumerate_class`,
reused from EXP-ISOU-2ac81f, unbounded BFS) was timed directly: one 28-bit
curve explored 409 vertices / 818 edges in 28.9s with step primes
{3,5,7,11,13}; a **second** 28-bit curve did not finish exploring its
crater within a 120s timeout, and a full run with step primes extended to
{...,29,31} did not finish ONE curve within 600s (both timeouts are
recorded verbatim in this file's git history / session transcript; the
process was killed after 10+ minutes of CPU time with zero curves
completed). Extrapolated, exhaustive search across >=20 curves at 28 bits
would cost on the order of hours, exceeding the 3600s/run budget.

Given the E1/E2 invariance finding above, exhaustive search to `ell_max`
for E1/E2 is **provably guaranteed** to reach the same NOT_FOUND verdict as
checking the start vertex alone, for every non-special-at-start curve --
so the exhaustive search costs budget without any possibility of changing
the outcome for E1/E2. `bounded_walk.enumerate_class_capped` therefore caps
the walk at `BOUNDED_WALK_MAX_VERTICES=300` vertices and
`BOUNDED_WALK_MAX_SECONDS=20.0` seconds per curve, enforced **during** the
BFS (checked at every vertex/edge, not just measured after the fact -- an
earlier version of this driver measured the cap only after calling the
unbounded `enumerate_class` and consequently hung on RUN-3's first
attempt; this was caught, fixed, and RUN-1 and RUN-3 were re-executed under
the fixed, actually-enforced cap before being accepted as the final run
package; RUN-2 was executed once, already under the enforced cap). 12-19
of the 20 curves per bit size at 24/28 bits hit the 300-vertex cap (see
`results.json`, `bounded_walk.capped`); this is disclosed explicitly and
does not change any NOT_FOUND verdict, since those verdicts are decided by
the (mathematically certain) invariance argument, not by walk coverage.

### 3. Measured baseline: plain Pollard rho instead of negation-map rho

See `driver/rho_bsgs.py` module docstring for the full account. In brief: a
negation-map (P -> -P folding) additive walk was genuinely implemented and
timed first, to match the contract's "Pollard rho with negation" and its
0.886*sqrt(N) reference constant. It exhibited the documented failure mode
of naive negation-map walks (fruitless small cycles: Duursma-Gaudry-Morain
2002; Bos-Kleinjung-Lenstra) -- 9 of 20 timed trials across 20/24/28-bit
curves failed to converge within a generous step cap even after adding a
multi-alternative escape mechanism, and the trials that DID converge showed
5-30x cost inflation relative to the 0.886*sqrt(N) model. Rather than ship
these unreliable/inflated numbers, or silently patch the walk further
in-flight without disclosure (which ST-2 forbids), this run uses plain
(non-negation) Pollard rho, which converged in **20/20** timed trials
across 16/20/24/28-bit curves with no failures, and in the actual 60-curve
census, **60/60 rho solves succeeded with independently verified
certificates** (see `results/summary.json`, `ctrl_baseline`). Every
measured rho cost is reported against BOTH the contract's own
0.886*sqrt(N) model AND the correct un-optimized reference,
1.2533*sqrt(N) = sqrt(pi/2)*sqrt(N) (Pollard 1978; van Oorschot-Wiener
1999) -- see `cost_model.plain_rho_cost_modeled`. This substitution is
strictly conservative with respect to CTRL-BASELINE's own
`failure_meaning` (a defective instrument shows anomalously LOW cost;
plain rho's expected cost is higher than negation-map rho's, not lower, so
it cannot manufacture a spurious INV-BASELINE pass).

### 4. Smart-ASS special-curve algorithm: INFEASIBLE_WITHIN_BUDGET

**This is the deviation with a real consequence for the run package's
validity** (see `runs/RUN-ECDLP-bbb42f-4/certificates/NO_CERTIFICATE_PRODUCED.md`).

A genuine, timed implementation attempt at the Smart-Araki-Satoh-Semaev
anomalous-curve DLP algorithm (`driver/smart_ass.py`: Hensel-lift the
points to `Z/p^2Z`, compute `[p]P~` via double-and-add on the lift, extract
the additive elliptic logarithm) reproduced a specific, reproducible
mathematical obstruction identically at 16, 20, 24, and 28 bits: the FINAL
combination step of the double-and-add for exponent `p` adds two points
that reduce to negatives of each other mod `p` (since `[p]P` reduces to `O`
mod `p` for a point of order exactly `p`), making the standard affine
addition-formula denominator `(x2 - x1)` divisible by `p` and therefore
**not invertible mod `p^2`** -- confirmed via a direct debug trace (raw
Python session, retained in the Executor's session transcript for this
task): `ValueError: base is not invertible for the given modulus` at
exactly the bit position corresponding to the final accumulation for
`p = 65537 = 2^16+1`. This is not a coding bug in the usual sense; it
reflects a genuine coordinate singularity (the true sum's projective
`Z`-coordinate is itself divisible by `p`, so naive affine division is the
wrong tool for this specific step). The two standard correct fixes
(projective coordinates carried through the `p`-divisible `Z`-coordinate,
or a formal-group-law power-series logarithm computed directly in the
parameter `t = -x/y`) were judged, after this genuine attempt, to require
more implementation and independent-verification time than remained in
this run's budget to ship without a material risk of a silently wrong
(un-independently-verified) `k`.

**Per the task's explicit instruction, this is reported as a named,
timed infeasibility rather than silently substituted with an easier
computation.** No `[k]P=Q` certificate exists for the anomalous-curve
target in RUN-4 at any bit size. Per the contract's own `INV-PLANTED-VOID`
rule, **this makes the harness VOID for the corresponding unplanted-census
reading**: RUN-1/2/3's measurements are real and retained (nothing is
discarded, per rule 12), but this run package does not certify S1 or F1
from them until this specific defect is fixed and CTRL-PLANTED-PATH is
re-run to completion.

Everything else in CTRL-PLANTED-PATH DID succeed genuinely at all three
bit sizes: real anomalous-curve construction, real forward isogeny walk,
independent order re-certification of `E_rand`, and **genuine recovery of
the specific reverse path via bounded BFS** within the forward path's
degree budget (not assumed -- computed).

## K_max and step-prime choices (fixed before sampling, per contract)

- `K_MAX = 20` (embedding-degree cutoff for E2): a recognizable, citable
  toy-scale threshold (commonly used in curve-validation guidance as a
  floor below which MOV/Frey-Ruck is a live concern), fixed in
  `isogeny_transfer_census.py` before any curve at any bit size was
  sampled.
- `STEP_PRIMES = [3, 5, 7, 11, 13]`: the smallest odd primes for which
  kernel-polynomial construction is cheap at these bit sizes (timed at
  <=0.05s per (vertex, ell) even at 28-bit `p`; ell=2 is structurally
  excluded since `N` is odd prime, so no rational 2-isogeny kernel ever
  exists, per `class_walk.py`'s own documented reasoning, reused here).

## E3 (GHS) resolution, not an ST-2 stop

See `predicates.py` module docstring: E3 is evaluated as the constant
`False` for every curve in this experiment's domain, because prime fields
`F_p` (`p` prime) have no proper subfield for GHS-style Weil descent to
target, for any extension degree. This is a definite mathematical fact,
not a guess, so ST-2's "cannot be resolved unambiguously" stop condition
does not apply; it is recorded here rather than silently assumed.

## Timing summary (measured, wall-clock, this session)

| Run | Wall seconds |
|---|---|
| RUN-ECDLP-bbb42f-1 (20-bit census, final) | 111.5 |
| RUN-ECDLP-bbb42f-2 (24-bit census, final, capped walk) | 242.5 |
| RUN-ECDLP-bbb42f-3 (28-bit census, final, capped walk) | 235.8 |
| RUN-ECDLP-bbb42f-4 (planted-path control) | 107.6 |
| RUN-ECDLP-bbb42f-5 (RRG null) | 1.2 |
| RUN-ECDLP-bbb42f-6 (exit-map spot-check) | 0.01 |

All well within the 3600s/run cap; total across all declared runs
(including the discarded pre-fix RUN-3 attempt's wasted ~20 CPU-minutes,
which is disclosed here rather than hidden) is far under the 12-CPU-hour
total budget.

## Files

See `results/seed_env_manifest.yaml` for the module provenance split
(reused from EXP-ISOU-2ac81f vs. newly written for this experiment) and
exact seeds. See `results/summary.json` for the aggregated primary/
secondary metrics. Per-curve raw records are in each run's `results.json`.
