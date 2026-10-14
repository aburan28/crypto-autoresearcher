---
title: "Conductor-gap panel: NIST K curves and standardized controls"
date: 2026-10-14
geometry: margin=0.72in
fontsize: 10pt
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Result in one page

This evidence-reduction round measures **43 certified prime conductor
directions** across **20 finite-field trace/isogeny classes** (17
twist-deduplicated conductor geometries), comprising **38 distinct prime
degrees**.  Expanding every squarefree conductor gives **102
exact endomorphism-order levels** and **131 conditional adjacent-level
placements**.  Those 131 placements are repeated algebraic contexts, not 131
independent hardness observations.  The machine-readable record is
[`panel.json`](panel.json); the flattened direction, level, adjacency,
construction, and measured-effect tables are the CSV files beside this report.
The independent arithmetic and transcription receipt is
[`verification.json`](verification.json), produced by
[`verify_panel.py`](verify_panel.py).

The main findings are:

1. **Large conductor gaps correlate with a derived direct-kernel ambient-field
   burden, not an ECDLP discount by themselves.**  Across the 43 structural rows,
   `Spearman(log2 ell, log2(m*k)) = 0.9462` (derived, descriptive only), where
   `k` is the least exponent for which q-Frobenius acts as `+/-1` on an
   ell-kernel generator.  For 41 rows, `m*k` is an ambient extension upper
   bound rather than a certified exact abstract-representative x-orbit.  Rows
   are clustered in only 20 classes, so this is
   not a significance test or a causal estimate; three twist pairs also share
   the same conductor geometry.  The panel is purposive, all non-control gap
   rows use the `Q(sqrt(-7))` Koblitz mechanism, and no cross-panel discovery
   cost relationship was measured.
2. **The scalar-orbit degree `k` materially changes the ranking.**  K-283's
   degree-1,697 direction has an exact derived absolute x-orbit degree of
   239,984 for the certified abstract representative, while K-163's larger
   degree-45,641 direction has exact degree 3,260 for a retained concrete
   kernel x-coordinate witness.  Absolute-Frobenius matrix certificates
   establish both abstract minima, and the K-163 replay binds one certificate
   to the sampled prime-order kernel line; degree alone misses their 74-fold
   difference.  Neither certificate constructs a point map.
3. **The existing same-action level experiments do not show a multi-bit
   conductor effect.**  The admitted ECDLP evidence comprises nine comparison
   rows: all eight conditional edges at `m=37` and `m=41`, whose pointwise 95%
   intervals contain zero, plus the accepted `m=51` degree-271 same-`tau^17`
   estimate of `+0.005763` bit with 95% interval
   `[-0.032170,+0.043374]`.  A separate four-level `m=51` run has point
   estimates within 0.0264 bit, but its A/A gate failed, so those four rows'
   inferential labels are withheld.  These 9 admitted and 4 withheld ECDLP
   rows are separate from the 43 directions, 102 levels, and 131 placements.
4. **The three-to-four-bit scale appears only in the modeled action
   comparison.**  A NIST K source has a derived ideal signed-Frobenius rho
   discount of 3.674 to 4.579 bits relative to negation.  That belongs in the
   source baseline arm;
   it is not evidence that a conductor floor is weak.  A claimed 3-bit weak
   endpoint must have a multiplicity-adjusted one-sided lower confidence bound
   above 3 bits after map, solve, recovery, failures, and verification are all
   charged.
5. **No NIST row yet reaches the transfer gate.**  The five K curves provide
   15 exact prime directions, but zero rows currently have a certified
   point-evaluable map, dual, subgroup transport, planted-scalar recovery, and
   fully charged transfer cost together.  Therefore no NIST weakness assertion
   is eligible in this panel.

\scriptsize

| requested scope | current status | evidence in this round |
|---|---|---|
| Dozens of vertical geometries | verified exact | 43 prime directions, 102 levels, 131 conditional placements |
| Direct-kernel x-coordinate orbit degrees | partial | 1 exact concrete-kernel minimum, 1 exact abstract-only minimum; 41 certified `m*k` upper bounds |
| Per-level ECDLP effects | partial | 9 admitted comparison rows: 8 at `m=37`/`m=41` plus 1 accepted `m=51` edge; 4 later `m=51` rows are control-gated |
| K-163/K-283 map, dual, and transfer | blocked/unrun | full K-163 producer implemented but unexecuted; no complete map-plus-dual transfer artifact for either curve |
| Horizontal K/P/B/`sect113r1` paths | not assessed | zero horizontal rows |

\normalsize

![Prime conductor degree against the derived ambient kernel x-field degree.
The two starred rows have exact x-orbit minima: K-163 is bound to a concrete
kernel witness and K-283 to an abstract CM representative.  The other 41
values are ambient `m*k` upper bounds.  The left panel resolves the
operational range; the right retains all extreme rows.  Point count is 43,
with 20 trace/isogeny-class labels and 17 twist-deduplicated geometries; no
independence claim is made.](gap-landscape.png)

Editable vector: [`gap-landscape.svg`](gap-landscape.svg); generator:
[`build_panel.py`](build_panel.py).

# Objects and measurements

For each ordinary Koblitz crater

\[
  E_a: y^2+xy=x^3+a x^2+1\quad\text{over }\mathbb F_{2^m},
\]

the CM field is `K=Q(sqrt(-7))`, the named crater has `f_E=1`, and

\[
  t^2-4q=-7 f_\pi^2.
\]

Every prime `ell | f_pi` is a depth-one vertical conductor direction in this
panel.  If `tau^m=X+Y tau` and q-Frobenius is the scalar `c=X mod ell` on
`E[ell]`, the direct kernel-point route uses

\[
  k=\min\{j>0:c^j=\pm1\pmod\ell\},\qquad
  x(P)\in\mathbb F_{2^{mk}}.
\]

Thus `F_(2^(m*k))` is a derived ambient construction field.  Its degree is an
exact minimal absolute x-coordinate orbit period for a stated abstract
representative only when an absolute-Frobenius certificate rules out every
proper divisor of `m*k`; it is not thereby a concrete point or field
construction.  The structural vector retained per direction is

\[
 (\ell,\log_2\ell,\text{split type},k,mk,(\ell-1)/2,
   \text{packed kernel bytes},h(-7\ell^2)).
\]

For squarefree `f_pi`, every divisor is an exact possible order level and

\[
 h(-7 f_E^2)=\prod_{p\mid f_E}\left(p-\left(\frac{-7}{p}\right)\right).
\]

The packed-byte column is the derived dense coefficient payload
`ceil((((ell-1)/2)+1)*m/8)`.  It is not an observed file size, memory peak, or
evaluation cost.  Likewise, existence of a conductor-lattice adjacency does
not construct its rational map.

The panel keeps four notions separate:

- **Geometry:** exact conductor, splitting, q-relative scalar orbit, the
  evidence-qualified ambient/absolute field degree, kernel degree, and class
  number.
- **Construction:** an observed endpoint, census, kernel, map, or dual under a
  stated resource envelope.
- **Native action:** the best certified action available directly on each
  endpoint.
- **Transfer advantage:** the base-two log ratio of incumbent to fully charged
  candidate cost under a declared target count and common cost unit.

For a declared target count `H`, the bit-valued transfer estimand is

\[
A(H)=\log_2\!\left(
\frac{C_{\mathrm{inc}}(H)}
{C_{\mathrm{discover}}+C_{\mathrm{construct}}+C_{\mathrm{certify}}
 +H(C_{\mathrm{map}}+C_{\mathrm{solve}}+C_{\mathrm{recover}}
     +C_{\mathrm{verify}})+C_{\mathrm{failures}}}
\right).
\]

Positive `A(H)` means the fully charged candidate is cheaper.  Costs must use
one declared primitive or calibrated unit; a degree, byte count, or field
dimension cannot be inserted as if it were runtime.

![Exact conductor geometry is only the first of six gates required for a
weakness conclusion.](evidence-flow.png)

Editable vector: [`evidence-flow.svg`](evidence-flow.svg); source:
[`evidence-flow.dot`](evidence-flow.dot).

# NIST K curves

The table reports the cheapest direct kernel direction by derived `m*k` for
each named K curve.  Conductor, `k`, kernel degree, and packed-byte proxy are
exact derivations.  The parenthetical evidence label says whether `m*k` is
bound to a concrete kernel witness, certified only for an abstract CM
representative, or retained only as an ambient upper bound.  The status column
is the strongest archived endpoint evidence; none includes the complete
point-map/dual/transfer package.

\scriptsize

| curve | cheapest `ell` | type | `k` | `m*k` (x-orbit evidence) | kernel degree | packed bytes | endpoint status |
|---|---:|---|---:|---:|---:|---:|---|
| K-163 | 45,641 | split | 20 | 3,260 (exact concrete) | 22,820 | 464,978 | 6 historical + 2 fresh preflight endpoints; map not retained |
| K-283 | 1,697 | inert | 848 | 239,984 (exact abstract) | 848 | 30,034 | census implementation only; not run canonically |
| K-571 | 3,952,463 | split | 3,461 | 1,976,231 (upper) | 1,976,231 | 141,053,559 | structural only |
| K-233 | 5,610,641 | split | 12,040 | 2,805,320 (upper) | 2,805,320 | 81,704,975 | structural only |
| K-409 | 21,262,439,877,311 | inert | 2,126,243,987,731 | 869,633,790,981,979 (upper) | 10,631,219,938,655 | 543,521,119,363,788 | structural only |

\normalsize

The two exact labels come from independently rechecked CM line-orbit
certificates, not from a completed kernel construction.  On `E[ell]`, use the
absolute-Frobenius companion matrix

\[
 M=\begin{pmatrix}0&-2\\1&\mu\end{pmatrix}\pmod\ell,
 \qquad v=(1,0).
\]

For K-163/45,641, the line orbit is 163 and the q-relative x-orbit is 20;
they are coprime and `M^3260 v=-v`.  The images at exponents
`3260/2`, `3260/5`, and `3260/163` are respectively `(26313,0)`,
`(29773,0)`, and `(914,45014)`, none equal to `+/-v`.  For K-283/1,697,
the corresponding degrees are 283 and 848, `M^239984 v=-v`, and the
factor-exclusion images are `(1283,0)`, `(1368,0)`, and `(794,794)` for
divisors 2, 53, and 283.  These checks prove the exact minimal absolute
x-orbit degrees for the stated abstract non-horizontal torsion lines.  K-163
also has the concrete relative-tower binding described below; K-283 does not.
The CM checks by themselves do not supply coordinates, a field embedding, an
isogeny, or a cost measurement.  The complete machine-readable witnesses are in
[`verification.json`](verification.json).

The full exact factorizations are:

```text
K-163: 45641 * 82153 * 8610311 * 56498081
K-233: 5610641 * 85310626991 * 150532234816721999
K-283: 1697 * 162254089 * 1779143207551652584836995286271
K-409: 21262439877311 * 22431439539154506863
       * 57030553306655053533734286593
K-571: 3952463
       * 9021184135396238924389891945192676814518993645089807769277009849103733654828039
```

K-163 has the most developed retained construction path.  The archive retains six
degree-45,641 endpoints at 61--87 seconds each, six degree-82,153 endpoints at
842--989 seconds each, and six conditional degree-82,153 descents from the
45,641 floor with inner isogeny timers of 828--1,019 seconds plus a separately
logged 29-second embedding per run.  These timings construct endpoint
coefficients; they are not complete wall-clock or point-map evaluation
timings.  A fresh deterministic seed preflight took 56.09 seconds wall time
and 45,832 KiB peak RSS, producing an eighth endpoint orbit when combined
with the six historical samples and the separate relative-tower endpoint.
A separate endpoint certificate took 90.66 seconds and 33,368 KiB peak RSS;
it bound the fresh preflight coefficient, matched source and target orders,
rejected the wrong twist, and checked the degree-11 cycle and ring-class
invariants.  Both are pre-map/certificate workloads, not point-map
construction or evaluation.  This round repaired
the new degree-45,641 GP driver's silent startup exit and verified that it
parses through the expensive `ffembed` stage under a bounded diagnostic.  The
absolute-field producer has not completed.  No full forward-map producer has
completed, and no map artifact is claimed.
The separate relative-tower full producer contains an exact function-field
identity gate, backed by a passing small positive fixture and a wrong-endpoint
negative control, but remains unrun; implemented checks are not execution
evidence.

A bounded relative-tower probe now supplies a sharper stopping-point
measurement for the K-163/45,641 route.  In 56.65 seconds wall time and 23,724
KiB peak RSS it produced an exact-order descending witness, enumerated all
22,820 half-kernel x-values in 90 inversion batches, and certified the endpoint
coefficient and its 163-element orbit.  It also certified concrete absolute
x-degree 3,260 by closure and exclusions at 1,630, 652, and 20 for every
nonzero multiple on the sampled prime-order kernel line.  The logged phases
were 17 ms for field setup, 4,628 ms for the witness including the nested
absolute-orbit/classification work, 62 ms for that nested absolute-orbit
subphase, and 51,995 ms for the endpoint and half-kernel work.  The 62 ms is
already included in the 4,628 ms and must not be added again.  It then
deliberately stopped before forming the kernel polynomial or a point map.  This
is measured pre-map work, not a completed isogeny or transfer; the full
transcript is
[`probe163_45641_relative_tower.out`](../ecc2k130_conductor_isogenies_20261007/analogues/probe163_45641_relative_tower.out).
A separate 0.36-second retained-input replay (21,248 KiB peak RSS; 29 ms field
setup and 321 ms verification), using the same x-only ladder
family, reconstructed the frozen coefficients, checked both field moduli,
reproduced the degree-3,260 exclusions, and rejected a truncated-coefficient
negative control.  It then derived that degree for all 45,640 nonzero
multiples by Frobenius/scalar commutation.  Its
[receipt](../ecc2k130_conductor_isogenies_20261007/analogues/verify163_45641_relative_witness.out)
labels that scope `DERIVED` and still certifies a kernel line, not an isogeny
map or ECDLP advantage.

A separate same-degree horizontal control evaluated
`alpha=51-160*tau`, its dual, and both degree-45,641 composition identities on
1,024 targets in 6.86 seconds wall time (16,140 KiB peak RSS; 6,845 ms for the
logged composition checks).  It verifies the endomorphism arithmetic on the
same curve only: it is explicitly not a vertical conductor transfer,
kernel-polynomial build, or weakness
measurement.  Its transcript is
[`control163_45641_horizontal_endomorphism.out`](../ecc2k130_conductor_isogenies_20261007/analogues/control163_45641_horizontal_endomorphism.out).
The two timings are therefore different workloads and cannot be divided into
a transfer speedup.  More generally, isogeny degree alone is not a cost proxy:
field representation, orbit length, construction phase, retained artifacts,
and map-evaluation workload must be measured separately.

K-283 has the smallest degree but not the smallest kernel field.  Its degree
1,697 kernel polynomial would contain only about 30 KB of densely packed base
field coefficients, while the certified non-horizontal line has exact
absolute x-orbit degree 239,984.  This algebraic certificate does not perform
the direct point construction.  The CM census can identify endpoints without
supplying the map, and its archived implementation remains unexecuted through
the canonical runner.

K-409's smallest direction is already far beyond the current direct route:
the derived packed kernel payload is about 543.5 TB (decimal), before language
or algebra-system overhead, and the direct route's ambient field upper bound
is about `8.70e14`.  No exact abstract-representative x-orbit minimum is
certified for that row.  This is a structural burden calculation, not a
bounded failure or an impossibility proof.

# Other standardized curves and controls

The NIST scan gives exact `f_pi=1` for P-192, P-256, P-384, P-521, B-163,
B-233, B-283, and B-409.  `sect113r1` also has fundamental Frobenius
discriminant and `f_pi=1`.  These are zero-vertical-gap controls: they rule out
this particular vertical-conductor mechanism, not horizontal isogenies,
special endpoint models, implementation defects, or other attacks.

P-224 has exact `f_pi=3`, with the prime ramified in its CM field.  Four
rational linear degree-3 kernels and codomains have been enumerated, but the
named curve's actual `f_E` remains unresolved in `{1,3}` and the edge
directions, closure, point map, and dual are not certified.  It is therefore a
potential direction, not one of the 43 certified Koblitz gap rows.

B-571 remains unresolved in the archived NIST scan and is not silently counted
as an `f_pi=1` control.  The retained partial-factorization bound is still
useful: `|D_K| >= 4.114e46` (164.82 bits), implying no non-scalar endomorphism
below degree `1.029e46` under that archived derivation.

The published full `sect113r1` discrete-log computation is a real weak-size
calibration, but it is not evidence for a conductor-gap mechanism: this panel
computes no vertical conductor direction for that curve.

**Horizontal-scope status:** zero horizontal candidate-endpoint or discovery
directions were enumerated or timed for the P, B, and `sect113r1` controls.
The 6.86-second K-163 degree-45,641 same-curve endomorphism control is excluded
from the 43 vertical direction rows and is not a horizontal discovery scan.
In particular, `f_pi=1` rules out a vertical conductor descent, not horizontal
isogenies within the maximal-order class.  Horizontal endpoint/action
discovery remains a separate unmeasured requirement for the P, B, and
`sect113r1` controls.

# What changes at each measured volcano level

The strongest same-action evidence is the accepted 160,000-solve `m=37/m=41`
replication.  Each number is `log2(child mean / parent mean)` in counted
operations, so positive means more work on the child.  These comparisons use
native negation at both levels and do not charge an isogeny transfer.

| class | factor | other factor absent, bits [95% CI] | other factor present, bits [95% CI] |
|---|---:|---:|---:|
| m=37 | 73 | +0.002917 [-0.020485,+0.026585] | -0.017605 [-0.038453,+0.003022] |
| m=37 | 2,663 | +0.008627 [-0.018443,+0.035801] | -0.011895 [-0.027377,+0.003650] |
| m=41 | 409 | -0.001430 [-0.049462,+0.044956] | -0.002297 [-0.040039,+0.036423] |
| m=41 | 1,721 | +0.016988 [-0.030100,+0.062547] | +0.016121 [-0.022858,+0.055663] |

All eight intervals contain zero.  The three `m=37` level-versus-crater
simultaneous 90% ratio intervals satisfy the frozen +/-3% equivalence margin.
The global six-level assertion is false because the `m=41` intervals are too
wide, not because a nonzero effect was detected.

The accepted `m=51`, degree-271 comparison holds both levels to signed
`tau^17`: `+0.005762506` bit with fixed-orbit 95% interval
`[-0.032170483,+0.043374391]`.  A separate later discovery scan certifies 42
bottom-to-parent endpoint pairs across
`f_E=271*120871 -> f_E=120871`; it does not serialize a point map or dual.

The subsequent four-level `m=51` native-negation run completed all 20,480
solves.  Its four local-edge point estimates range from -0.02635 to +0.02633
bit.  However, the A and B held-out A/A intervals crossed the frozen +/-0.15
bit margin by 0.00304 and 0.00904 bit.  The run is an intact observation with
status `aa_alert_labels_withheld`; its diagnostic intervals cannot be used to
claim equivalence, an effect, or absence of an effect.

These results directly address the proposed “large prime conductor gap”
heuristic: in the measured same-action arms, adding the larger factors 2,663,
1,721, or 120,871 did not produce a resolved multi-bit shift.  The evidence
does not generalize to NIST-sized gaps or to a best-action endpoint comparison.

# Why the modeled 3--4 action bits matter, but do not establish weakness

For a prime-order Koblitz subgroup with a certified signed action of size
`2m`, the ideal random-map collision discount relative to negation is

\[
  \frac12\log_2(m)\ \text{bits}.
\]

The derived ideal values are 3.674 (K-163), 3.932 (K-233), 4.072 (K-283),
4.338 (K-409), and 4.579 (K-571); they are not measured NIST runtimes.  The
`m=37` and `m=41` proxy measurements observe 2.487 counted-operation bits
(pointwise 95% interval `[2.454,2.521]`) and 2.685 bits
(`[2.631,2.741]`) for native signed `tau` versus native negation,
respectively.  The floor-level same-negation differences are near zero by
comparison.

Thus, the multi-bit signal is presently **action availability**, not conductor
size.  Descending from a Koblitz crater often removes a cheap self-action; that
would make a floor less attractive for rho, unless the floor supplies a
different certified attack or a transfer strategy whose complete cost beats
the source's signed-Frobenius incumbent.  A transported action

\[
 [d^{-1}]\circ\phi\circ\tau\circ\widehat\phi
\]

must charge the dual, source action, forward map, inverse-degree scalar,
canonicalization, and conversions every time it is used.  One-time return to
the Koblitz source is a mandatory dominance control.

# Statistical confidence and weak-curve gate

Exact identities receive independent arithmetic verification, not p-values.
For runtime, construction success, or solver work:

1. Use the hierarchy `isogeny class -> conductor edge -> parent orbit ->
   endpoint orbit -> target/process block`.  Twists and Galois conjugates are
   matched or nested observations, not extra classes.
2. Pair source and candidate by planted scalar, seed, host, and process block.
   Freeze equal-curve or equal-orbit weighting before execution; also examine
   endpoint tails because a level mean can hide a rare weak representative.
3. For this purposively selected fixed panel, cluster or resample only the
   nested edge/orbit/target units and scope inference to these curves; do not
   treat the 20 class labels as population draws.  A future cross-family claim
   must preregister its sampling frame and exchangeability assumptions.  Use
   max-|T| simultaneous intervals (Holm as fallback), untouched endpoint
   orbits, and target streams to confirm any selected outlier.
4. Keep timeouts right-censored for time-to-certificate and failures for a
   fixed-budget success probability.  Treat OOM as failure under that memory
   envelope; invalid certificates are failures, never censoring.
5. Preserve A/A, coordinate-isomorphism, same-action, positive-map, and
   zero-gap controls.  A failed mandatory control withholds the dependent
   inference rather than erasing the observations.
6. Report cold-start `H=1`, the declared multi-target workload, and break-even
   `H`.  Do not amortize discovery or construction without naming `H`.  Size a
   future confirmatory run from a preregistered minimum detectable effect and
   target power before looking at candidate outcomes.

A weak-representative verdict requires exact endpoint identity, an applicable
verified attack, full accounting, planted-scalar recovery, and a family-wise
one-sided 95% lower bound above a material margin predeclared by that future
experiment.  A source-transfer
verdict additionally requires public (or explicitly advice-scoped) map/dual
reconstruction and subgroup recovery.  A class-wide verdict requires a
uniform invariant or construction over the declared class.

For a specifically predeclared three-bit reduction claim, the simultaneous
lower bound on fully charged advantage must exceed **3 bits**.  A 3--4 bit
point estimate, ideal orbit formula, kernel degree, or conductor ratio is
insufficient.

# Next discriminating executions

1. **K-163 / 45,641:** finish the repaired deterministic forward-map build;
   retain the full kernel polynomial and exceptional-input behavior.  Add the
   algebraic dual, both composition identities, standard-subgroup transport,
   and planted recovery before benchmarking.
2. **m=37 / 73 positive control:** the new retained
   [`map73_dual_control.gp`](../isogeny_volcano_rho_20261005/map73_dual_control.gp)
   and [receipt](../isogeny_volcano_rho_20261005/map73_dual_control.out)
   construct the forward map and algebraic dual; both compositions, all 1,024
   inverse-degree recoveries, and the planted recovery pass.  The cold control
   took 26.39 seconds wall time and 39,708 KiB peak RSS; its logged phases were
   530 ms for forward construction, 24,604 ms for dual construction, and 556 ms
   for target checks.  This construction measurement validates the local proxy
   plumbing only, not a NIST transfer or ECDLP comparison.  Next compare one-time
   return with the transported-action arm before admitting a full-size K-163
   cost run.
3. **K-283 / 1,697:** first admit and canonically execute the existing CM census
   to certify the 1,698-model floor.  Then stage the forward-map route as
   separate bounded gates: field embedding plus an exact-order torsion witness;
   enumeration and descent of the 848 half-kernel abscissae into a retained
   base-field polynomial; and codomain, exception, subgroup, planted-log, and
   homomorphism checks.  Construct and certify the dual separately.  Census
   success alone is not a transfer.
4. **Replication panel:** add independent conductor lattices, not merely more
   targets within `m=37`, `m=41`, or `m=51`.  Use the exact 43-row panel for
   stratification by `log2 ell`, evidence-qualified `log2(m*k)`, and split
   type, with held-out classes for confirmation.  Do not mix the 41 ambient
   upper bounds with exact abstract-representative x-orbit values without an explicit
   interval/censoring model.

# Evidence and provenance

All quantitative statements above are `internal` repository evidence or
derived from it.  The builder records SHA-256 hashes for every controlling
source in `panel.json`.  The fail-closed rerun commands, source/output hashes,
resource receipts, rejected direct/fault/missing-sentinel controls, and exact
claim boundary are retained in
[`rerun_provenance.json`](../ecc2k130_conductor_isogenies_20261007/analogues/rerun_provenance.json).
`panel.json` is a structural panel plus selected archived
effects, not an exhaustive performance warehouse; the linked source analyses
remain authoritative for statistics not copied here.

- NIST identities and Frobenius conductors: [internal
  scan](../endosweep_nist_20261006/nist.json).
- Binary conductor survey, CM floors, K-163 endpoints, and second level:
  [internal survey archive](../ecc2k130_conductor_isogenies_20261007/).
- Four-level exact proxy replication: [internal
  results](../isogeny_volcano_level_replication_20261013/results.json).
- Accepted degree-271 result: [internal
  analysis](../isogeny_volcano_m51_rho_20261013/analysis.json).
- Deep `m=51` [discovery](../isogeny_volcano_m51_deep_scan_20261013/) and
  [gated native-rho observation](../isogeny_volcano_m51_deep_rho_20261013/).
- Open transfer obligations: [Koblitz maps](../../problems/koblitz-vertical-isogeny-maps-not-persisted.md)
  and [P-224 maps](../../problems/p224-degree3-point-maps-not-certified.md).
- Independent factor, minimal-order, lattice, source-transcription, and gate
  checks: [`verify_panel.py`](verify_panel.py) and
  [`verification.json`](verification.json).

Primary background references:

- D. Kohel, *Endomorphism rings of elliptic curves over finite fields*, PhD
  thesis, UC Berkeley, 1996, <https://hdl.handle.net/1721.1/10973>.
- NIST SP 800-186, *Recommendations for Discrete Logarithm-based
  Cryptography: Elliptic Curve Domain Parameters*, 2023,
  <https://doi.org/10.6028/NIST.SP.800-186>.
- Standards for Efficient Cryptography Group, *SEC 2: Recommended Elliptic
  Curve Domain Parameters*, version 2.0, 2010, section 3.2.1 (`sect113r1`),
  <https://www.secg.org/sec2-v2.pdf>.
- G. Wiener and R. Zuccherato, *Faster Attacks on Elliptic Curve
  Cryptosystems*, SAC 1998, <https://doi.org/10.1007/3-540-48892-8_15>.
- E. Wenger and P. Wolfger, *Harder, better, faster, stronger: elliptic curve
  discrete logarithm computations on FPGAs*, J. Cryptographic Engineering 6
  (2016),
  <https://doi.org/10.1007/s13389-015-0108-z>.

# Reproduction

\scriptsize

```sh
MPLCONFIGDIR=/tmp/conductor-gap-panel-mpl \
XDG_CACHE_HOME=/tmp/conductor-gap-panel-cache \
python3 -B research/conductor_gap_panel_20261014/build_panel.py

python3 -B research/conductor_gap_panel_20261014/verify_panel.py

dot -Tsvg research/conductor_gap_panel_20261014/evidence-flow.dot \
  -o research/conductor_gap_panel_20261014/evidence-flow.svg
dot -Tpng research/conductor_gap_panel_20261014/evidence-flow.dot \
  -o research/conductor_gap_panel_20261014/evidence-flow.png

pandoc research/conductor_gap_panel_20261014/REPORT.md \
  --from=markdown+raw_tex+tex_math_single_backslash \
  --pdf-engine=xelatex \
  --resource-path=research/conductor_gap_panel_20261014 \
  -o research/conductor_gap_panel_20261014/report.pdf
```

\normalsize

This rebuilds derived views only.  It does not rerun the archived scientific
trials or promote any claim.
