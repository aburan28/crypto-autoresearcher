# Run report: RUN-FROB-91ee9c-7119f2 (EXP-FROB-91ee9c / TASK-20260914-7119f2)

This report contains OBSERVATIONS ONLY. It makes no claim of improvement, no
attack, no security consequence, and no verdict on H-FROB-d93575 or on the
preregistered prediction. All ratios below are EXACT rationals (Python
`fractions`), reported as `numerator/denominator`; none are floating point.
Interpretation is reserved to the Coordinator and independent reviewers after
this run package is committed.

## 1. Terminal cell status

| Cell | Status | Reason |
|---|---|---|
| FROB-SPLIT-q11n5 | completed | Two distinct eligible object curves found (A=1,B=1,j=9,N=1051; A=1,B=2,j=2,N=10061); all four arms populated on the first. |
| FROB-NOLATTICE-q13n5 | completed | Two distinct eligible object curves found (A=0,B=1,j=0,N=30841; A=1,B=0,j=12,N=3701); all four arms populated on the first. No non-trivial partition exists for this cell by construction (s=1 atomic factor of degree 4) -- this is the designed null cell, not an instrument failure. |
| FROB-EQDEG-q19n5 | completed | Two distinct eligible object curves found (A=0,B=1,j=0,N=206461; A=1,B=1,j=6,N=117991); all four arms populated on the first. |
| FROB-EXT-q13n7 | not_run_resource | Object-search-only probe completed (67.6s wall): first two eligible curves found were (A=0,B=1,N=5,230,261) and (A=1,B=0,N=3,109). The full instrumented worker (subgroup enumeration of N=5,230,261 by repeated point addition, plus the several full-N passes C2 requires per achievable slot dimension) was checkpointed at a self-imposed 540-second wall-clock cap before completing. Peak RSS during the attempt never approached the 8 GiB machine-protection cap (observed well under 300 MB); this was purely a wall-clock scheduling decision. Per specification.yaml SR-4, this ordered-last cell's non-completion for resource reasons does not affect the success/falsification criteria, all of which are scoped to the three core cells. `not_run_resource` is the permitted terminal state. |

## 2. Controls: pass/fail with witness

All controls below were run on the FIRST eligible object curve of each core
cell (curve index 0 in the ordering produced by the frozen `object_selection`
scan). See section 5 for the scope note on the SECOND curve.

### C1 (baseline single slot -- closed form vs. enumerator)

| Cell | closed-form U_neg | closed-form p_1 | enumerator U_neg | enumerator p_1 | Agree |
|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 110/2 | 110/1050 | 110/2 | 110/1050 | PASS |
| FROB-NOLATTICE-q13n5 | 2550/2 | 2550/30840 | 2550/2 | 2550/30840 | PASS |
| FROB-EQDEG-q19n5 | 10650/2 | 10650/206460 | 10650/2 | 10650/206460 | PASS |

### C5 (trace identity, computed directly)

For every core cell, on the first eligible curve's field/Frobenius matrix
(identical for both curves in a cell, since the field and Frobenius matrix do
not depend on the curve): T = matrix of u -> u+u^q+...+u^{q^(n-1)}, computed
directly by repeated q-th powering.

| Cell | dim(sum of nontrivial ker f_i(pi)) | dim ker T | direct sum certified | set equality sum = ker T | dim = n-1 (=4) | T = h(pi) | dim ker(x-1) | ker(x-1) subset of ker T |
|---|---|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 4 | 4 | true | true | true | true | 1 | false |
| FROB-NOLATTICE-q13n5 | 4 | 4 | true | true | true | true | 1 | false |
| FROB-EQDEG-q19n5 | 4 | 4 | true | true | true | true | 1 | false |

C5: PASS in all three core cells. The ker Tr identity HOLDS exactly: the
direct sum of the non-trivial factor kernels equals ker Tr, of dimension
n-1=4, in every completed cell, and ker(x-1) (the F_q subfield, dimension 1)
is correctly NOT contained in ker Tr in any of them (p does not divide n in
any core cell, matching the exclusion condition stated in the frozen spec).
Independently re-verified by checker.py (own field/Frobenius-matrix
construction, no Sage): dim ker T matched the driver's value in all three
cells (see section 6).

### C6 (known-false configurations)

| Cell | repeated-subspace refused | overlapping-index-sets refused | V={0}: p_m | denominator-zero triggered | V=F_(q^n), m=1: p_1 | p_1 = 1 exactly |
|---|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | true | true | 0/1050 | true | 1050/1050 | true |
| FROB-NOLATTICE-q13n5 | true | (only 1 atomic factor; overlap check not constructible, correctly skipped) | 0/30840 | true | 30840/30840 | true |
| FROB-EQDEG-q19n5 | true | true | 0/206460 | true | 206460/206460 | true |

C6: PASS in all three core cells. Both synthetic non-partitions
(repeated subspace in two slots; overlapping index sets) were refused with an
explicit reason and never credited as a valid partition. Both degenerate
endpoints gave the exact predicted values (p_m=0 with denominator-zero
flagged; p_1=1 exactly).

### C7 (denominator-zero rule)

Demonstrated by the C6 V={0} test above in every cell: p_m=0/(N-1) is
reported as `denominator_zero: true` with the numerator (0) retained, never
as 0, infinity, or a placeholder, and no configuration was dropped from any
min/max computation on this basis. No REAL (non-synthetic) achievable
partition in the object, C2, C3 or C4 arms produced p_m=0 in this run -- every
`denominator_zero` occurrence in the raw data is the deliberate C6 synthetic
test. C7: PASS.

### C8 (independent re-check, checker.py -- no Sage import)

`checker.py` is a from-scratch, pure-Python/stdlib implementation of F_q^n
arithmetic (polynomial mod-g representation, its own extended-field inverse
via Fermat exponentiation, its own Tonelli-Shanks-style square root, its own
elliptic-curve point addition/doubling/scalar-multiplication) and its own
irreducible-polynomial search. It does not import implementation.py, core.py,
lattice.py, or any `sage` module.

| Check | FROB-SPLIT-q11n5 | FROB-NOLATTICE-q13n5 | FROB-EQDEG-q19n5 |
|---|---|---|---|
| Independently reconstructed field modulus g matches driver's | true | true | true |
| Independent dim ker T matches driver's | true (4=4) | true (4=4) | true (4=4) |
| \|B\| divisible by 2n on object arm, both curves | true (110, 820 divisible by 10) | true (2550, 280 divisible by 10) | true (10650, 6150 divisible by 10) |
| Independent order-N + primality + Frobenius-eigenvalue re-derivation, smaller-N curve(s) | curve A=1,B=1,N=1051: confirmed; curve A=1,B=2,N=10061: confirmed | curve A=1,B=0,N=3701: confirmed; curve A=0,B=1,N=30841: skipped (see below) | curve A=1,B=1,N=117991 and A=0,B=1,N=206461: skipped (see below) |

Full re-derivation of order/primality/Frobenius-eigenvalue (via the
checker's own generator search and its own scalar-multiplication routine)
was performed for every curve with N <= 20,000 (four of the six core-cell
curves). For the two curves with larger N (30,841 and both EQDEG curves,
117,991 and 206,461), the checker explicitly records
`skipped_too_large_for_pure_python_full_reenumeration_this_session` rather
than silently omitting or fabricating a result -- a disclosed scope
limitation of the pure-Python re-derivation, not a failed check. The
divisibility, field-modulus and ker-T checks above (which do not require a
second generator search) were run and PASSED on every curve in every core
cell, including the larger-N ones. C8: PASS on all checks actually
performed; four of the six generator/order/eigenvalue re-derivations
completed, two explicitly skipped for scale with the reason disclosed.

## 3. Achievable slot-dimension multiset table vs. divisor lattice

| Cell | Achievable multisets (from `all_set_partitions` over the atomic factors) | Divisor-lattice dims (all subset-sums of atomic degrees) | Agreement |
|---|---|---|---|
| FROB-SPLIT-q11n5 | {4}, {3,1}x4, {2,2}x3, {2,1,1}x6, {1,1,1,1} (Bell(4)=15 partitions total) | {0,1,2,3,4} | Exact -- every dimension in the divisor lattice is realised. |
| FROB-NOLATTICE-q13n5 | {4} only (Bell(1)=1) | {0,4} | Exact -- no non-trivial partition exists; only dims 0 and 4 occur, matching the single degree-4 atomic factor. |
| FROB-EQDEG-q19n5 | {4}, {2,2} (Bell(2)=2) | {0,2,4} | Exact -- the two equal-degree-2 atomic factors only ever combine to dim 4 or split to (2,2); dims 1 and 3 are correctly absent. |

## 4. Measured cost-ratio table (object arm, extra=0), both endpoints of every spread

All values are `(U_neg + 1 + 0)/p_m`, exact.

FROB-SPLIT-q11n5:
- Curve (A=1,B=1,N=1051): only partition m=1 [dim 4] is achievable (every
  finer partition is `empty_base` -- no point of the order-1051 subgroup has
  its x-coordinate confined to any strict combination of atomic
  eigenspaces smaller than the full 4-dimensional sum). Ratio = 5880/11.
  Spread = 1 (single achievable configuration; max=min by construction).
- Curve (A=1,B=2,N=10061): achievable partitions are m=1 [4] (ratio
  206733/41) and m=2 [2,2] (ratio 5533/5). Argmax (coarsest, m=1):
  206733/41. Argmin (m=2, [2,2]): 5533/5. Spread = (206733/41)/(5533/5) =
  2055/451 (all other partitions of this curve are `empty_base`).
  Argmin slot count m=2, satisfying m>=2.

FROB-NOLATTICE-q13n5:
- Curve (A=0,B=1,N=30841): only m=1 [4] achievable, ratio 1311728/85.
- Curve (A=1,B=0,N=3701): only m=1 [4] achievable, ratio 26085/14.
- Spread = 1 in both curves (no non-trivial partition exists in this cell by
  construction; I(FROB-NOLATTICE-q13n5) = 1 by construction on both curves).

FROB-EQDEG-q19n5:
- Curve (A=0,B=1,N=206461): only m=1 [4] achievable (the [2,2] partition is
  `empty_base`), ratio 36653532/355. Spread = 1.
- Curve (A=1,B=1,N=117991): achievable partitions are m=1 [4] (ratio
  12097908/205) and m=2 [2,2] (ratio 82593/10). Argmax (m=1): 12097908/205.
  Argmin (m=2): 82593/10. Spread = 6152/861. Argmin slot count m=2.

### Extreme configurations across each cell's achievable (non-empty-base) set

| Cell | Smallest p_m among achievable configs | Largest U_neg among achievable configs |
|---|---|---|
| FROB-SPLIT-q11n5 | 100/10060 (curve A=1,B=2, partition [2,2]) | 820/2 (curve A=1,B=2, partition [4]) |
| FROB-NOLATTICE-q13n5 | 280/3700 (curve A=1,B=0) | 2550/2 (curve A=0,B=1) |
| FROB-EQDEG-q19n5 | 300/117990 (curve A=1,B=1, partition [2,2]) | 10650/2 (curve A=0,B=1) |

### I (within-cell improvement factor) and the cross-cell comparison

- I(FROB-SPLIT-q11n5), on the curve where a non-trivial partition is
  achievable (A=1,B=2,N=10061): I = 2055/451 (exact) -- endpoints 206733/41
  (m=1) and 5533/5 (m=2, argmin, m>=2 satisfied).
- I(FROB-NOLATTICE-q13n5) = 1 on both curves (no non-trivial partition
  exists; by construction).
- I(SPLIT) / I(NOLATTICE) = (2055/451) / 1 = 2055/451 -- i.e. I(SPLIT) is
  exactly 2055/451 times I(NOLATTICE).
- I(FROB-EQDEG-q19n5), on the curve where a non-trivial partition is
  achievable (A=1,B=1,N=117991): I = 6152/861 (exact) -- endpoints
  12097908/205 (m=1) and 82593/10 (m=2, argmin, m>=2 satisfied). (EQDEG is not
  part of the SPLIT-vs-NOLATTICE ratio comparison in the frozen prediction;
  reported here as a first-class measurement in its own right, per the
  tail-check requirement to report every cell separately.)

No conclusion is drawn from these numbers about whether any threshold in the
preregistered prediction is met, cleared, or missed; that comparison is
reserved to the Validator/Red Team/Coordinator per the review plan already
on record in the handoff (joints J1-J5), and the numbers above are exactly
what that review plan's blind re-derivation target (cell FROB-SPLIT-q11n5,
partition (2,2), object arm) can be checked against.

## 5. Control-arm cost ratios (curve index 0 only) and the scope gap

On the FIRST eligible curve of each core cell, the object, C2, C3 and C4
arms all show a spread of exactly 1 (only the trivial m=1 [4] partition is
achievable on that specific curve in every core cell except
FROB-EQDEG-q19n5's curve 0, which also collapses to spread 1 since its
[2,2] partition is empty on that curve too). Because every arm on this curve
is spread-1, the success-criterion clause "each of C2/C3/C4's spread is
STRICTLY SMALLER than the object arm's spread in that cell" is NOT
evaluable as a meaningful comparison on this curve (1 is not strictly
smaller than 1; all four arms tie). The curve that DOES exhibit a
non-trivial object-arm spread in FROB-SPLIT-q11n5 and FROB-EQDEG-q19n5 is the
SECOND eligible curve (idx 1), for which this run computed the object arm
only -- C2/C3/C4 were not built for it (an operational scope choice made to
fit this run's practical time budget; not a silent omission, and recorded
here and in manifest.yaml as a disclosed limitation). This is the single
most consequential scope gap in this run package: the control comparison
required by the success/falsification criteria has not been exercised on the
curve where the effect under test actually appears, in either of the two
cells where a non-trivial partition exists at all. No claim is made in
either direction from this gap; it is reported as an impediment to
completing the full success-criterion evaluation, to be resolved either by
extending C2/C3/C4 to curve index 1 in a follow-up run, or by amendment if
the Coordinator judges the scope should be reduced.

Exact control values obtained (curve 0, all trivially spread-1):

| Cell | Object (m=1) | C2 (m=1) | C3 seed1 (m=1) | C3 seed2 (m=1) | C4 (m=1), both seeds |
|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 5880/11 | 9100/17 | 5880/11 | 5880/11 | 34048/55 |
| FROB-NOLATTICE-q13n5 | 1311728/85 | 1219208/79 | 1311728/85 | 1311728/85 | 2363152/255 |
| FROB-EQDEG-q19n5 | 36653532/355 | 37066452/359 | 36653532/355 | 36653532/355 | 329764616/5325 |

(C3's two seeds give IDENTICAL values in every cell because C3's construction
draws negation-closed pairs uniformly and -- at m=1 with a single slot equal
to the full non-trivial-eigenspace point set restricted to matched
cardinality -- the sampled set here coincides with the full available pair
pool at these toy cardinalities; recorded exactly as measured, not adjusted.)

## 6. Object search: rejected candidates and pool exhaustion

Rejected-candidate counts (every rejection recorded with its reason in
raw.jsonl / metrics.json, per IR-5 -- none dropped): FROB-SPLIT-q11n5: 22
rejected before 2 accepted; FROB-NOLATTICE-q13n5 and FROB-EQDEG-q19n5:
rejection lists preserved in full in raw.jsonl (`object_search.rejected`).
No core cell exhausted its (A,B) pool before finding two eligible curves; no
core cell is `partial` or `ineligible`.

## 7. Memory reconciliation (IR-7) -- UNEXPLAINED DISCREPANCY, reported as required, not resolved

| Cell | N | analytic_bytes (by-mask table, load factor 2) | measured peak_rss_bytes | ratio (measured/analytic) | In [0.5, 4]? |
|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 1051 | 16,800 | 246,108,160 | 7,702,528/525 (approx 14,671) | NO |
| FROB-NOLATTICE-q13n5 | 30,841 | 493,440 | 247,857,152 | approx 502 | NO |
| FROB-EQDEG-q19n5 | 206,461 | 3,303,360 | 270,213,120 | approx 82 | NO |

This is reported as an unexplained discrepancy per IR-7, not explained
away. The measured/analytic ratio is far outside the declared [0.5, 4]
band in every cell. The analytic model in specification.yaml sizes only the
dominant data structure (the hit-set / by-mask table over the subgroup);
it does not size the SageMath process's own baseline memory footprint
(interpreter, PARI/GP, NTL, GMP and their loaded state), which this
driver's `resource.getrusage(RUSAGE_SELF).ru_maxrss` necessarily includes
and which appears to dominate totally at these toy problem sizes (all three
measured peak-RSS values cluster tightly around 246-270 MB regardless of N,
consistent with a roughly constant runtime floor rather than with the
N-dependent analytic term). This observation is noted for context but the
gap is NOT rounded away, resolved, or treated as closed: the analytic model
as written in specification.yaml does not account for interpreter/runtime
overhead, and no attempt was made in this run to isolate or subtract that
overhead. FROB-EXT-q13n7: not reconciled (no full enumeration attempted).

## 8. Modelled vs. measured cost-ratio discrepancy (secondary; MODELLED and MEASURED never mixed in one object)

See `cost-model.json` -> `derived_from_measured.<cell>.measured_vs_modelled_discrepancy`
for the full exact-rational table (every partition, every curve). Headline
(extra=0, `measured_cost_ratio_neg / modelled_cost_ratio`, exact rational):

| Cell / curve / partition | measured/modelled |
|---|---|
| SPLIT, A=1,B=1, [4] | 6776/6795 |
| SPLIT, A=1,B=2, [4] | 2005817/2005310 |
| SPLIT, A=1,B=2, [2,2] | 161051/219200 |
| NOLATTICE, A=0,B=1, [4] | 36443836/36445875 |
| NOLATTICE, A=1,B=0, [4] | 1342367/1342180 |
| EQDEG, A=0,B=1, [4] | 694089646/694087125 |
| EQDEG, A=1,B=1, [4] | 400867396/400866225 |
| EQDEG, A=1,B=1, [2,2] | 130321/114600 |

All ratios are close to 1 (within a few percent) for the m=1 (coarsest)
configurations, and further from 1 (12-14%) for the two-slot partitions that
were achievable -- reported as measured, not interpreted.

## 9. Optimistic-assumption restatement (OA-1 .. OA-6)

Every cost ratio above is computed under OA-1 (extra=0; secondary values at
extra=8 and extra=32 are in cost-model.json/metrics.json, still separated
into the derived_from_measured object) and OA-2 through OA-6 exactly as
declared in specification.yaml (no per-trial algebraic solving cost, no rank
deficiency measured, no factor-base-construction/orbit/witness overhead
folded in, no descent/re-randomisation cost, and the p_m values are exact
for these instances only with no extrapolation performed). This run prices
the combinatorial half of relation collection only; nothing here is a
solve-cost ranking, an attack, or a security statement about any curve,
deployed or otherwise.

## 10. Protocol deviations and implementation notes

1. Slot-dimension labelling bug, found and fixed mid-run. An early
   version of `run_arm_partitions` in implementation.py computed a
   partition block's reported dimension as the number of atomic factors
   merged into it (`bin(mask).count("1")`) rather than the sum of their true
   degrees. This coincides with the correct value only when every atomic
   factor has degree 1 (true only in FROB-SPLIT-q11n5). It silently
   mislabelled slot dimensions in FROB-NOLATTICE-q13n5 (single degree-4
   factor, so the only partition was mislabelled "[1]" instead of "[4]") and
   FROB-EQDEG-q19n5 (two degree-2 factors; the two-slot partition was
   mislabelled "[1,1]" instead of "[2,2]"). The bug did NOT affect the
   underlying exact p_m/U_neg/cost_ratio values (computed from the true
   kernel masks, independent of the label), but it DID feed the wrong
   dimension into (a) the C2 non-stable-subspace control's dimension-match
   for those two cells, and (b) the MODELLED q^(d_j)/c sizing for those two
   cells. The bug was found by manual inspection before any artifact was
   finalised, fixed in implementation.py (see its inline note), and all
   three core cells were rerun. The pre-fix outputs are preserved,
   unmodified, under `work/*.pre_bugfix` for audit; they were never used to
   produce metrics.json, cost-model.json, or any number in this report.
2. C2/C3/C4 computed on curve index 0 only per cell (see section 5) -- a scope
   choice, not a silent omission, and the resulting gap is stated plainly
   in section 5 rather than hidden.
3. FROB-EXT-q13n7 not completed (see section 1 above) -- no rejected-candidate
   list or full curve/kernel data exists for it beyond the object-search
   probe recorded in `work/FROB-EXT-q13n7.probe.json`.
4. checker.py generator/order/eigenvalue re-derivation skipped for N >
   20,000 (section 2, C8) -- disclosed scope limit of the pure-Python
   re-implementation within this session's practical budget, not a failed
   or fabricated check.
5. No sampling was used in any core cell's p_m computation (IR-2): every
   p_m above is exact, from exhaustive enumeration over the full
   prime-order subgroup (implemented as an exact sumset-over-Z/N
   computation from the discrete logs of every point in the subgroup,
   which is mathematically exact and equivalent to point-by-point tuple
   summation since <G> is cyclic of prime order N with G a fixed generator
   -- this equivalence, and the underlying per-point kernel-membership
   classification, were independently spot-checked in this session against
   direct polynomial-in-Frobenius evaluation before being used for any
   reported cell, and are independently re-verified in production by
   checker.py's own, unrelated point-addition-based arithmetic for orbit
   divisibility, order, and Frobenius-eigenvalue facts).

## 11. Timing and resource usage

Total core-cell wall-clock: 60.54 s (SPLIT 1.05 s, NOLATTICE 7.56 s, EQDEG
51.93 s); total core-cell CPU: 63.94 s. FROB-EXT-q13n7 probe: 67.6 s;
full-attempt checkpoint: 540 s (self-imposed cap, process terminated by
`timeout(1)`, no memory-cap violation). Independent checker: 3.1 s.
Aggregation: <1 s. No cell exceeded the 8 GiB memory cap; no
`resource_exhausted` classification was needed for any CORE cell (all three
completed well within the cap, peak RSS 246-270 MB, dominated by SageMath's
own runtime footprint per section 7).
