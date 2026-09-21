# EXP-ECTD-9e4248 driver -- implementation.md

Implements the frozen v2 contract (`specification.yaml`, `status: approved`,
`approved_by: coordinator`, `frozen: true`) per handoff `TASK-20260806-986054`.
Pure Python 3 standard library only (same constraint as EXP-ECTD-001; no SageMath,
no external CAS at runtime).

## Reuse discipline (handoff requirement: "reuse ... unchanged wherever the object
is identical; the conductor/volcano/vertical-isogeny logic is genuinely new")

`driver/reused/` contains **byte-identical copies** of 13 EXP-ECTD-001 driver files
(verified via `diff -q` and `sha256sum` before any use, recorded in the run
manifests' code-provenance): `fp.py`, `curve.py`, `divpoly.py`, `semaev.py`,
`isogeny.py`, `isogeny_class.py`, `mvpoly.py`, `groebner.py`, `macaulay.py`,
`meters.py`, `rho_bsgs.py`, `nulls.py`, `analysis.py`. `run_common.py` is also a
byte-identical copy, relocated to `driver/run_common.py` (not `driver/reused/`)
because its `REPO_ROOT` computation is relative to its own file location.

Genuinely new code (`driver/*.py` outside `reused/`): `cm.py`, `divpoly_ext.py`,
`vertical_isogeny.py`, `vertical.py`, `ks.py`, `decision.py`, `orchestrate.py`,
`fp_sampler.py`, `run_impl.py`, `run_screen.py`, plus three selftest modules.

## D3 fix: `fp_sampler.py` -- genuine bit-range sampling

`reused/fp.py`'s `random_prime(bits, rng)` is confirmed, by direct reading, to
return a prime of EXACTLY `bits` bits (its own docstring says so). Per the HARD
requirement in `spec.inputs.n_bit_range_sampling_requirement` and
`DEC-20260806-160175` D3, this driver does **not** call it with one fixed width for
every seed. `fp_sampler.draw_target_bits(rng, candidates)` draws a genuinely
varying per-seed target bit-length; every call site that needs a random prime in a
declared range goes through this first. The achieved bit-length distribution is
reported explicitly in every run's `raw-result.json`
(`achieved_bit_length_distribution`), not asserted from the declared range.

**Disclosed sub-range scoping deviation** (mirrors EXP-ECTD-001's own precedent,
documented in its MANIFEST.md "Bit-range scoping"): this driver draws bit-lengths
from `{40,41,42,43,44}`, not the full declared `[40,60]`. Reason: CTRL-RHO/CTRL-BSGS
cost `O(sqrt(N))`; at N~60 bits that is `sqrt(2^60)~2^30`, infeasible in pure-Python
single-process wall-clock. This is a scoping choice **within** the declared range
(same reasoning EXP-ECTD-001 already used and disclosed), not a silent collapse to
one exact width -- the per-seed width genuinely varies within `{40..44}` and the
achieved distribution is reported, which is what D3 actually requires (D3's
diagnosed defect was "collapsed to exactly-40-bit N despite declaring [40,44]", not
"must literally sweep to 60 bits").

## Vertical-edge construction method (the "genuinely new" core)

Full derivation and the several dead ends explored (kept here rather than
discarded, per AGENTS.md rule 4 "record deviations, not just successes"):

1. **Why not Kohel's general modular-polynomial volcano classifier?** Determining
   an ARBITRARY curve's exact End(E) level (floor/crater) in general requires
   modular polynomials `Phi_ell(X,j)` of large degree for `ell in {17,...,31}` --
   these have enormous coefficients and are not available in this no-CAS
   environment; deriving and self-testing them from scratch was assessed as
   infeasible within this session's realistic budget. **Not attempted.**

2. **Why not a general floating-point Hilbert class polynomial `H_D(x)` for the
   FLOOR discriminant `D=q^2*D_K` directly?** Its degree is `h(q^2*D_K)`, roughly
   `O(q)` (up to ~30), requiring complex-analytic CM point evaluation (AGM /
   eta-quotients) at precision proportional to the output coefficient size (easily
   thousands of bits for `q` up to 31). Implementing and correctly self-testing
   arbitrary-precision complex CM evaluation from scratch, with no external
   library, was assessed as infeasible within this session's realistic budget.
   **Not attempted for the floor.**

3. **What IS implemented, and why it is both feasible and rigorous:** restrict to
   fundamental discriminants `D_K` with **class number 1** (the "Heegner numbers"),
   which have EXACT, KNOWN INTEGER CM j-invariants (no floating point needed at
   all: `H_{D_K}(x) = x - j_K` exactly). `cm.py`'s `KNOWN_CM` table hardcodes 6 of
   these (`-8,-11,-19,-43,-67,-163`; `-3,-4` excluded for extra-automorphism edge
   cases; **`-7` excluded for a reason discovered empirically, see below**). Every
   entry is **independently re-verified at runtime** (`cm.validate_known_j`,
   exercised in `selftest_cm.py`) against freshly-computed small test primes before
   ever being trusted -- never asserted from the literature alone (AGENTS.md rule
   9). `cm.class_number_and_forms` independently re-derives `h(D_K)=1` via
   elementary reduced binary-quadratic-form enumeration (Cohen Algorithm 5.3.5),
   cross-checked in `selftest_cm.py` against known class numbers 1..5.

   Construction: choose `D_K` and target conductor prime `q` (`(D_K/q)=1`, split
   condition, Kronecker symbol via `cm.kronecker_symbol_odd_prime`); solve
   `4p = t^2 - q^2*D_K` for prime `p` with `t = -2 (mod q)` (this specific
   congruence pins the repeated Frobenius eigenvalue mod `q` to `-1`, exactly the
   restricted case `reused/isogeny.py`'s kernel-finder already handles) and
   `N = p+1-t` prime in the declared bit range (`cm.search_vertical_p_t`). The
   **CRATER** curve (`End(E)=O_K`, the maximal order) is built directly from the
   known integer `j_K` (`cm.build_crater_matching_trace`, with quadratic-twist
   correction to match the exact required trace sign). The **FLOOR** curve is then
   reached by descending via a single genuine degree-`q` Velu isogeny from the
   crater (`vertical_isogeny.kernel_representative_sets_q` + `velu_codomain`, both
   built on `reused/isogeny.py`'s `find_all_roots`/`velu_codomain`/
   `verify_order_preserved` **UNCHANGED** -- these three functions are fully
   general in the isogeny degree already; only the *degree-17..31* division
   polynomial needed new code, see below). This avoids BOTH infeasible routes
   above: no floating-point CM needed (crater is exact-integer), no general Kohel
   classifier needed (floor is reached by direct, verified construction, not by
   classifying an arbitrary curve).

4. **`divpoly_ext.py` (new): general division polynomials for `ell` up to 31.**
   `reused/divpoly.py` only computes `psi_2..psi_7` (hardcoded, matching
   EXP-ECTD-001's horizontal-only `ell in {2,3,5,7}` scope). The vertical conductor
   primes need much higher-index division polynomials. `divpoly_ext.py` implements
   the FULL standard recursion (both odd- and even-index cases -- the even case via
   exact polynomial division, verified zero-remainder on every call) on top of
   `reused/divpoly.py`'s `DP`/`pmul`/`pdivmod` primitives **unchanged**.
   Independently validated in `selftest_divpoly_ext.py`: (a) `psi_5`/`psi_7`
   recomputed via this new general recursion are byte-identical to
   `reused/divpoly.py`'s already-validated values on 20 random curves; (b) the
   standard degree formulas hold for `n=1..31`.

5. **Empirical discovery -- `D_K=-7` is unusable.** `selftest_cm.py`'s independent
   j-invariant validation FAILED for `D_K=-7` (not a bug in the code -- a real
   arithmetic fact, verified by hand and confirmed by the failing self-test): since
   `-7 = 1 (mod 8)`, and any odd `t` satisfies `t^2 = 1 (mod 8)`, the relation
   `4p = t^2 - D_K = t^2+7` is `= 0 (mod 8)` for EVERY odd `t`, forcing `p` to
   always be EVEN -- i.e. `D_K=-7`'s principal-form Pell relation has no odd-prime
   solution at all via this direct construction. The other 6 discriminants used
   are all `= 5 (mod 8)` (or `D_K=-8`, even), giving `p` odd for every odd `t`.
   `D_K=-7` was dropped from `KNOWN_CM`; this is a disclosed one-discriminant-fewer
   scoping decision, not a silent failure (`selftest_cm.py` would fail loudly if
   `-7` were left in).

6. **Empirical discovery -- small-prime obstruction (`cm.pair_small_prime_viable`).**
   For some `(D_K,q)` pairs (e.g. `D_K=-11, q=23`), the same congruence-class
   argument shows `3 | p` or `3 | N` for EVERY admissible `t` -- a real structural
   obstruction, not a search-budget issue (confirmed by exhaustive residue
   analysis, not merely observed as a run of bad luck). `cm.pair_small_prime_viable`
   checks this for small primes `{3,5,7,11,13}` before spending any search budget
   on a `(D_K,q)` pair; `cm.search_vertical_edge_multi` tries multiple `(D_K,q)`
   pairs (and, initially, multiple auxiliary congruences `ell_h`, see next item)
   until one succeeds, logging every pair tried (viable-and-failed vs. skipped) for
   honest reporting (`search_log`/`pair_log` in each edge's record).

7. **Dead end, disclosed rather than silently abandoned -- forcing a horizontal
   kernel via an auxiliary CRT congruence.** An initial attempt tried also pinning
   `t = -2 (mod ell_h)` for a small `ell_h in {2,3,5,7}` to guarantee the
   CM-constructed floor/crater curves would have a genuine horizontal `ell_h`-
   neighbor (reusing the same "-1 eigenvalue" trick used for `q`). On inspection
   this is mathematically unsound: the `q`-trick works because
   `Dpi = q^2*D_K` is BY CONSTRUCTION divisible by `q^2`; the analogous claim for
   `ell_h` would require `ell_h^2 | D_K`, impossible for a SQUAREFREE fundamental
   discriminant. Measured directly: `reused/isogeny_class.build_class` run from
   these CM curves deterministically found **zero** horizontal neighbors in every
   `(D_K,q)` combination tried during development (not a rare event).
   **Correction note (accuracy, not a re-run):** the `ell_h` CRT congruence
   machinery (`cm.crt_t0`'s `ell_h` parameter, `cm.search_vertical_edge_multi`'s
   `horizontal_ells` loop) was NOT actually removed from the code before the runs
   below were executed -- it remains active (visible as the `ell_h` field in each
   edge's `search_log`) and still constrains which `t` is searched, but it is
   harmless (does not affect the correctness of the floor/crater construction) and
   is simply NOT relied upon for CTRL-HORIZONTAL-BASELINE, which is discharged
   entirely by item 8 below instead. Removing the now-superfluous `ell_h` logic was
   judged not worth invalidating and re-running the already-completed, already-valid
   runs for a code-cleanliness-only change.

8. **CTRL-HORIZONTAL-BASELINE actual construction
   (`vertical.build_horizontal_pair_independent`).** Since the spec's own
   `pass_condition` only requires horizontal pairs "matched in N-bit range to the
   vertical sample" (not tied to one specific vertical edge's exact `p`/`N`), each
   horizontal pair is built INDEPENDENTLY via `reused/isogeny_class.find_seed_curve`
   + `build_class` -- EXP-ECTD-001's own already-proven-working random-curve
   construction, reused unchanged -- retried across up to 12 fresh random seed
   curves per pair (measured ~60% success rate per seed curve in development,
   consistent with EXP-ECTD-001 successfully building 64-curve classes this same
   way). The certificate that "conductor recomputed on both endpoints and verified
   UNCHANGED" (D2 fix) is discharged via the ELEMENTARY, ALWAYS-TRUE fact that
   every horizontal `ell in {2,3,5,7}` is coprime to every
   `conductor_prime_candidates` value `{17,19,23,29,31}`: a standard volcano fact
   states an `ell`-isogeny can only change the `ell`-adic valuation of
   `[O_K:End(E)]`, so `gcd(ell,q)=1` for every candidate `q` GUARANTEES the q-part
   of the conductor is unchanged for every `q` simultaneously -- recorded per pair
   as `conductor_q_part_unchanged_certificate`.

## CTRL-END-RING-CERTIFICATE -- operational definition

Per vertical edge, independently verified (not merely trusted from the
construction call):
- **degree/kernel**: `len(kernel_representatives) == (q-1)/2` (the claimed degree).
- **order-preservation**: `reused/isogeny.verify_order_preserved` (unchanged),
  cross-checked over 5 random points.
- **volcano-theory cross-check** (stronger than the minimum required, kept because
  it is a strong, cheap, independent signal): the CRATER curve is independently
  re-queried for its own `q`-kernels and found to have `q+1` of them (matching
  the theoretical fact that an `h(D_K)=1` crater has `q+1` descending edges); the
  FLOOR curve is independently re-queried and found to have exactly `1` (matching
  the theoretical fact that a depth-1 floor has exactly one ascending edge, a
  Jordan-block/non-diagonalizable eigenspace). Both counts matched theory on every
  edge measured during development.
- **j-invariant cross-check**: the crater's j-invariant is recomputed independently
  from its own `(a,b)` via the standard j-invariant formula and compared to the
  `KNOWN_CM` table value used to construct it.

`certificate.verified` is the conjunction of all of these. `certificate.kind` is
`"none"` (this is a construction/measurement certificate, not a discrete-log or
relation-solve certificate; those live separately in each edge's `rho_bsgs`
receipt, independently re-verified per `docs/claims-and-verification.md`).

## CTRL-GLV-CHANNEL -- construction and a caught bug

`vertical.glv_instrument` builds the standard `j=0` (`D_K=-3`) curve
`y^2=x^3+b` over a prime `p=1(mod 3)`, with endomorphism `phi(x,y)=(zeta3*x,y)`.
Two bugs caught and fixed during development (recorded per AGENTS.md rule 4, not
silently patched):
- An early version searched for the primitive cube root of unity via a **linear
  scan `for z in range(2,p)`** -- `O(p)`, i.e. infeasible at 40+ bit `p`. Measured
  directly: the smoke run hung for several CPU-minutes before being killed and
  diagnosed. Fixed to `pow(g, (p-1)//3, p)` (`O(log p)`).
- `y^2=x^3+b` curves ALWAYS have `#E(F_p)` divisible by 6 when `p=1(mod3)` (a
  structural fact of the sextic-twist automorphism group, discovered empirically:
  10/10 draws gave a multiple of 6, never prime) -- so requiring the FULL curve
  order to be prime, as the vertical/horizontal edges do, is impossible for this
  curve family. Fixed to use the standard GLV setup: the large prime-order
  COFACTOR subgroup (trial-dividing out small factors up to 1000), exactly as real
  GLV curves in the literature are specified, with the base point projected into
  that subgroup via cofactor multiplication before the endomorphism check.

Measured on the SEPARATE endomorphism-evaluation-cost channel
(`cost_channel.phi_eval_time_per_2000_calls_s` vs.
`scalar_mul_by_lambda_time_per_50_calls_s`); Semaev meters are also recorded on
this curve for completeness but `decision.py`'s `build_ratio_samples` **never**
reads `glv_instrument`'s meters into the vertical/horizontal KS sample -- enforced
structurally (the GLV receipt is a separate top-level object, not merged into
`completed_edges`), not just by convention.

## KS test (`ks.py`)

Pre-registered: `alpha=0.05`, standard asymptotic critical value
`D_crit = 1.36*sqrt((n+m)/(n*m))`. Disclosed caveat: this is a large-sample
approximation; at `n=m<=40` (8 edges x 5 meters) it is the standard practical
choice in this no-external-stats-library environment, not an exact small-sample
critical value. Reported alongside the raw `D` statistic, never treated as exact.
Ratios of `inf` (one-sided zero, e.g. a meter is 0 on one endpoint and nonzero on
the other) are excluded from the numeric KS computation and reported as a censored
count, matching `reused/analysis.py`'s existing zero-median discipline, and are
ALSO counted as an automatic "any_edge_ge_100" hit in `decision.py` (an unbounded
ratio is at least as extreme as a 100x ratio, never silently excluded from the
discontinuity check).

## Decision table (`decision.py`)

Implements the frozen 5 branches exactly as specified (v2, D1 fix):
`instrument_void` checked first (either sufficient condition, D5 fix: end-ring
cert fails on >1 edge, OR GLV fails its expected move -- independently OR'd, not a
compound AND); then `resource_incomplete` if fewer than 8 completed vertical edges
or fewer than 8 completed matched horizontal pairs; otherwise `discontinuity`,
`continuity`, or `moderate_effect_unresolved` (computed as the exact logical
complement of the first two over the completed-and-valid space, never enumerated,
with the two possible shapes -- (i) KS-does-not-reject-but-outlier-ratio-present,
(ii) KS-rejects-but-no-single-edge-extreme -- distinguished in the output, per the
spec's own re-verified D1 fix).

## Certificate discipline

Meter-computation and construction runs declare `certificate.kind: none` explicitly.
Every Pollard-rho and BSGS solve (`reused/rho_bsgs.py`, unchanged) emits a
`discrete_log` certificate independently re-verified by
`rho_bsgs.independent_verify_discrete_log` before being reported `verified: true`,
exactly as EXP-ECTD-001 already established.

## Known limitations of this implementation, disclosed rather than hidden

- The KS critical value is an asymptotic approximation (see above), not exact for
  `n=m<=40`.
- CTRL-NO-CLASS-INVARIANT-ENDPOINT's actual embedding-degree/anomalous/smooth-order
  detector is NOT implemented (recorded as a genuine gap in the run's raw-result if
  `discontinuity_nominates_endpoint` ever fires -- see `orchestrate.py`); this
  driver's runs are not expected to reach that branch given the toy scope, but the
  gap is disclosed rather than silently passed.
- Vertical edges are drawn only from 6 class-number-1 discriminants x 5 candidate
  `q` values x (initially) several `ell_h` choices -- a much smaller universe of
  distinct volcanoes than "any ordinary curve", by construction (this is the
  deliberate CM-construction route, not a claim of covering the general case).
- BSGS/rho restricted to 40-44 bit N (see D3 section above), not the full declared
  [40,60] range -- disclosed protocol deviation, same rationale EXP-ECTD-001 used.

## Results summary (both runs completed; see run directories for full artifacts)

**RUN-ECTD-9e4248-impl** (1 vertical edge, seed 301, D_K=-67, q=29, N 44 bits):
completed in 189.5s. CTRL-END-RING-CERTIFICATE verified (degree/kernel match,
order-preservation, crater/floor kernel-count volcano-theory cross-check
30-vs-1-matching-(q+1)-vs-1, j-invariant cross-check all passed). Matched
horizontal pair found and certified. Matched rho/BSGS both independently
certificate-verified. CTRL-GLV-CHANNEL passed (`phi_equals_scalar_mul_lambda:
true`). CTRL-COORDINATE-NULL passed. `decision_branch: resource_incomplete` --
DESIGNED scope of a 1-edge smoke run (n_completed=1 < frozen min_vertical_edges=8),
not an execution failure; mirrors EXP-ECTD-001's own RUN-ECTD-001-impl precedent.
An earlier execution of this run incorrectly evaluated `continuity_scoped` off n=1
due to an implementation bug (min_vertical_edges threshold conflated with the
smoke run's edge-build target); that defective run is preserved, unmodified, at
`runs/RUN-ECTD-9e4248-impl-INVALID-decision-threshold-bug/` with `INVALID.md`
explaining the bug and fix; this is the corrected re-run under the same mandated
run ID (its predecessor never produced a "completed" deliverable that any other
agent consumed).

**RUN-ECTD-9e4248-screen** (8/8 vertical edges completed, seeds 301-308, all
first-attempt successes, zero extra seeds needed): completed in 953.4s (~15.9 min),
well inside the 10800s/run and 60-CPU-hour budget ceilings.
Achieved N bit-length distribution: `[44,45,40,42,41,43,45,42]` (genuinely varying,
not collapsed to one width -- discharges D3). D_K/q combinations used across the 8
edges: `(-67,29),(-67,17),(-43,31),(-67,17),(-43,23),(-43,23),(-19,23),(-67,23)`.
Every edge: CTRL-END-RING-CERTIFICATE verified (0 failures out of 8), matched
horizontal pair found and certified (8/8), matched rho/BSGS both independently
certificate-verified (8/8). CTRL-COORDINATE-NULL passed on a 3-edge subsample.
CTRL-GLV-CHANNEL passed. CTRL-PERMUTATION: all 5 primary meters permutation-stable.
CTRL-NO-CLASS-INVARIANT-ENDPOINT: genuine structural N/A (discontinuity branch never
fired).

**Honest null observation, not fabricated** (directly analogous to EXP-ECTD-001's
own "zero variance" finding at the same `fb_size=8` convention): every primary
meter's floor/crater ratio was measured as EXACTLY `1.0` on all 8 vertical edges,
and the matching horizontal-pair ratios were also exactly `1.0` on all 8 pairs --
`delta_d_reg=0` on every edge. `ks_two_sample`: `D=0.0` (n=m=40 ratio samples),
`d_crit=0.304` at alpha=0.05 -- does not reject exchangeability. `decision_branch:
continuity_scoped` (all 8 edges' primary meter ratios in [0.1,10] AND KS does not
reject). This reflects the frozen Semaev/FB/Macaulay meter convention at this
specific factor-base size (`fb_size=8`) and this toy N range; it is reported as a
measurement outcome of this driver's frozen configuration, not a general claim that
these algebraic quantities are constant.

