# Non-Generic Transfer / Decomposition Channel Search

Date: 2026-06-10

## Candidate

Exploit a corresponding object, not the original prime-field x-line, to expose a factor base, relation source, endomorphism, Jacobian transfer, or decomposition channel hidden on the original curve.

This is not the question "can Semaev beat rho on prime fields?"  The question is whether an isogenous object, twist, Weil restriction, cover, Kummer/Jacobian model, or class-group/endomorphism representation exposes a non-generic channel that the original curve presentation hides.

## Claim status

`HYPOTHESIS` for the broad search.

`NEGATIVE RESULT / MODEL-BOUND` for same-field isogeny transfer into a weak destination on ordinary prime-order prime-field curves under named attacks.

`OBSERVATION` for the quadratic-twist positive control: an extension-field-isogenous object can have a different `F_p` group order and therefore a different ECDLP cost.  This is the invalid-curve/twist-security channel, not a break of the original subgroup.

`OPEN` for genuinely new Jacobian/correspondence relation engines that do not factor through the scalar x-line Semaev relation.

## Assumptions

- Field family: elliptic curves over prime fields, with prime-order target subgroup unless explicitly stated.
- Baseline: Pollard rho with negation map, about `0.886*sqrt(n)` group operations.
- Same-field isogenies are `F_p`-rational and preserve Frobenius trace, hence preserve `#E(F_p)`.
- Extension-field correspondences may change the visible object; their result must state whether they solve the original subgroup or only an adjacent/twist subgroup.
- Scalar Weil restriction means an `F_p`-linear basis split of the same `F_{p^e}` Semaev relation; intrinsic Kummer/Jacobian laws are separate.

## Literature map

- Shoup generic-group lower bounds apply only to generic encodings, so they do not close this search.  They are the baseline barrier, not a non-generic impossibility theorem.
- MOV/Frey-Rueck and Smart/Satoh-Araki/Semaev anomalous attacks are real transfer channels, but their predicates are functions of order, trace, or embedding degree and are invariant inside an `F_p`-isogeny class.
- GHS/Weil descent and later GLS/GHS work show that extension-field curves can transfer to Jacobians where index calculus and endomorphisms matter.  This is relevant to `E/F_{q^e}`, not directly to a curve natively over `F_p` with no proper base field.
- Tian's cover attack transfers some prime-order ECDLP instances over `F_{q^3}` through an `F_q`-rational isogeny from a Weil restriction to a genus-3 Jacobian, giving a concrete model for the kind of channel we want.  The missing analogue for `E/F_p` is a nontrivial descent base or a replacement correspondence.
- Diem/Gaudry-style index calculus in fixed genus Jacobians gives a factor-base target once a DLP is honestly in such a Jacobian.  A prime-field EC attack needs the transfer, relation projection, and individual-log descent to beat `sqrt(n)`, not just a map into a larger Jacobian.
- Smith's genus-3 isogeny transfer shows that isogenies between Jacobians can move DLP instances to a representation with faster index calculus.  This supports searching corresponding objects, but it starts from Jacobians, not an ordinary prime-field elliptic curve.

## Evidence so far

### Same-field isogeny class

Prior artifacts:

- `research/p256_isogeny_class_invariance.md`
- `research/ISO_GOAL_isogenous_weak_curve.md`
- `experiments/ecdlp_prime_field/round018_results.md`
- `experiments/ecdlp_prime_field/round019_results.md`

Status: `NEGATIVE RESULT / MODEL-BOUND`.

The same-field isogeny channel is structurally closed for named weaknesses.  The order, trace, anomalous predicate, supersingular predicate, embedding-degree input, and CM field are class-invariant.  The remaining coefficient-level Semaev/gated-meter probes on flat-volcano toy classes found no neighbor with a lower solving degree or gate-meaningful fall.  This does not close unknown non-Semaev mechanisms, but it says the isogeny bridge alone does not expose a weak destination.

### Quadratic twist / extension-field isogeny

Prior artifact:

- `research/ISO_GOAL_FOUND_p224_twist.md`

Status: `OBSERVATION`.

The P-224 quadratic twist is isomorphic to P-224 over `F_{p^2}` and therefore isogenous over `F_{p^2}`, but over `F_p` it has order `p+1+t`, not the base order `p+1-t`.  Its twist order has a 118-bit largest prime factor, so Pohlig-Hellman plus rho costs about `2^58.6` instead of the base curve's `2^111.8`.  This is a real corresponding-object channel and a required positive control, but it only applies when an implementation accepts off-curve/twist points.  It does not solve the original P-224 subgroup.

### Scalar Weil restriction / Kummer charts

Prior artifacts:

- `experiments/ecdlp_prime_field/round009_exp017_abelian_surface_result.md`
- `experiments/ecdlp_prime_field/round012_exp028_theta_kummer_surface_result.md`
- `experiments/ecdlp_prime_field/round015_exp030b_theta_redo_result.md`
- `research/proofs_Dreg_conservation_weil_invariance.md`

Status: `NEGATIVE RESULT` for scalar pullbacks and tested level-2 theta/Kummer-line charts; `OPEN` for a genuinely new Jacobian/correspondence relation engine.

Scalar restriction faithfully transports the target into a larger object, but the `F_p`-linear basis split preserves the Semaev per-variable degree and adds variables.  The tested theta/Kummer-line chart did not produce a gate-meaningful fall.  The untested direction must avoid factoring through the elliptic x-line Semaev relation.

### Ascending isogeny / self-pairing

Prior artifact:

- `research/ascending_isogeny_self_pairing_note.md`

Status: `OBSERVATION / TOY-EVIDENCE`.

The self-pairing prototype recovers torsion action information for a toy ascending volcano edge.  This is useful for isogeny finding and vectorization, but not yet an ECDLP decomposition channel.  The next useful test is the smooth-`n1` Kani/interpolation reconstruction stub already named in the handoff.

## Experiment contract

# Experiment Contract: non-generic transfer channel sieve

## Hypothesis

At least one corresponding object attached to a prime-field EC target exposes a cheaper factor base or DLP carrier than the original curve, below the Pollard-rho baseline.

## Null hypothesis

Same-field isogeny classes preserve all named weak-destination predicates; scalar Weil/Kummer pullbacks factor through the original x-line relation; extension-field twist positives are adjacent invalid-curve channels rather than original-subgroup solvers.

## Parameters

- field/curve family: standard P-224/P-256 parameters plus generated toy prime-order curves;
- sizes: toy primes `101, 211, 431, 809, 1601, 4099`;
- seeds: `20260610..20260615`;
- factor base: not used in the sieve; this is a channel-discovery prefilter;
- relation shape: same-field isogeny invariants, quadratic-twist order factorization, scalar-Weil diagnostic;
- baseline: rho exponent `log2(0.886*sqrt(n))`.

## Metrics

- group operations: rho exponent and twist Pohlig-Hellman exponent;
- field operations: not measured in this prefilter;
- memory: not measured in this prefilter;
- relation probability: not measured in this prefilter;
- rank: not measured in this prefilter;
- solver degree: inherited from prior scalar-Weil/Kummer experiments;
- wall-clock: factorization time in the JSON artifact.

## Positive control

A smooth quadratic twist should be reported as a positive corresponding-object channel.

## Negative control

Same-field isogenous curves should remain closed for order-based channels because the trace and order do not change.

## Success criterion

Find a channel that solves or decomposes the original subgroup with expected cost at least 10 bits below rho, or else produce a positive-control adjacent channel with scope explicitly bounded.

## Falsification criterion

If every positive is a twist/invalid-curve or extension-field subgroup effect, and every original-subgroup transfer either preserves degree or lands in a harder Jacobian/group, then the current search narrows to non-scalar Jacobian/correspondence construction.

## Reproduction command

```bash
sage experiments/ecdlp_isogeny/non_generic_transfer_sieve.sage > experiments/ecdlp_isogeny/non_generic_transfer_sieve_result.json
```

## Results

Run completed in `experiments/ecdlp_isogeny/non_generic_transfer_sieve_result.json`.

| Curve | Base rho | Twist largest prime | Twist PH/rho cost | Verdict |
|---|---:|---:|---:|---|
| NIST P-256 | `2^127.83` | 241 bits | `2^120.45` | `twist_not_meaningfully_easier`; only `7.37` bits below base rho |
| NIST P-224 | `2^111.83` | 118 bits | `2^58.55` | `positive_twist_channel`; `53.28` bits below base rho |
| Toy `F_101` | `2^3.20` | 7 bits | `2^3.30` | not easier |
| Toy `F_211` | `2^3.73` | 7 bits | `2^3.03` | not meaningfully easier |
| Toy `F_431` | `2^4.24` | 6 bits | `2^2.60` | not meaningfully easier |
| Toy `F_809` | `2^4.62` | 4 bits | `2^1.73` | not meaningfully easier |
| Toy `F_1601` | `2^5.15` | 11 bits | `2^5.33` | not easier |
| Toy `F_4099` | `2^5.85` | 12 bits | `2^5.98` | not easier |

Interpretation: the sieve found exactly the intended positive control.  A corresponding object can be easier when the visible `F_p` group order changes, as in the P-224 quadratic twist.  The same evidence does not produce an original-subgroup break: same-field isogeny remains closed for order-based channels, scalar Weil restriction remains diagnostic-only, and the twist result is an adjacent invalid-curve/twist-security channel.

## Red-team interpretation

- A twist positive is a valid transfer/correspondence signal, but it does not recover the original subgroup scalar unless the protocol accepts twist points.
- An isogeny-finding improvement is a bridge improvement, not a DLP improvement, unless the destination object has a strictly easier DLP carrier.
- A map into a Jacobian is not enough.  The relation collection, matrix rank, quotient projection, and individual-log descent must all be charged against rho.
- A scalar Weil restriction is mostly a change of coordinates; the search must prioritize native Jacobian/Kummer/correspondence relations that do not pull back to the original Semaev relation.

## Handoff: Non-generic transfer frontier

### Claim or task
Search corresponding objects for a hidden factor-base/relation/endomorphism/Jacobian channel.

### Status
HYPOTHESIS

### Assumptions
- ordinary prime-field target;
- public/toy controlled instances;
- rho with negation map is the baseline;
- no deployment claim without parameter mapping.

### Evidence so far
- same-field isogeny weak-destination channel closed for named attacks;
- first `PO-transfer-001` horizontal slice found invariant `m=3/S4` decomposition metrics and rank-deficient public relations on a flat-volcano toy class;
- `PO-transfer-002` produced target-coupled relations and recovered the original toy target scalar, but only at `178x` to `317x` rho with large meet-in-the-middle memory, so target coupling alone is baseline-lost;
- twist/extension-field channel is a real positive control but adjacent to the original subgroup;
- scalar Weil/Kummer pullbacks tested so far do not lower exploitable solving degree;
- cover/Jacobian transfers exist in extension-field and Jacobian settings, but no prime-field analogue has been constructed here.

### Failure modes
- overreading invalid-curve/twist positives as original-subgroup breaks;
- solving the wrong DLP carrier in a larger Jacobian;
- ignoring relation-matrix and target-descent cost;
- treating isogeny-finding/vectorization leakage as EC-DLP leakage.

### Next concrete action
Replace raw divisor-list meet-in-the-middle with a structure-bearing native correspondence/Jacobian relation or a public prefilter that predicts target-coupled rank gain before materializing the full divisor table.

### Artifact paths
- `research/non_generic_transfer_search_20260610.md`
- `experiments/ecdlp_isogeny/non_generic_transfer_sieve.sage`
- `experiments/ecdlp_isogeny/non_generic_transfer_sieve_result.json`
- `experiments/ecdlp_isogeny/po_transfer_001_correspondence_suite.sage`
- `experiments/ecdlp_isogeny/po_transfer_001_result.json`
- `experiments/ecdlp_isogeny/po_transfer_002_target_coupled_suite.sage`
- `experiments/ecdlp_isogeny/po_transfer_002_result.json`

## PO-transfer-003 update: native bielliptic relation source

Date: 2026-07-13

Status: `NEGATIVE RESULT / POSITIVE MECHANICAL SIGNAL / TOY-EVIDENCE / MODEL-BOUND`.

`PO-transfer-003` constructed the split genus-2 cover

```text
C: y^2 = x^6 + A*x^2 + B
```

and pushed principal divisors of `y-v(x)` to the original elliptic quotient
`E1: Y^2=U^3+A*U+B`.  A cubic interpolated through a lift of `-lambda*Q` and
three factor-base lifts leaves a quadratic residual.  This is a native
function-field relation source rather than the raw signed-divisor MITM used in
`PO-transfer-002`.

The direct source was rank-deficient on the shared `F_4099` anchor.  A
one-large-prime variant repaired rank, and online rank plus target-first
streaming recovered the original target in all four cells.  A cap of nine
unmatched large-prime rows gave the selected anchor:

- public rank `16/16`;
- verifier-independent recovery `137*G=Q`;
- peak memory `3.90*sqrt(n)`;
- charged optimistic accounting floor `3375.96x` rho;
- adverse four-cell attempts/rank toy fit `n^1.687`.

An independent verifier reconstructed every interpolation and large-prime
cancellation, replayed 46 public rows, recomputed all four matrix ranks, and
checked all recovered public targets.  No factor-base logs are generated or
consumed by the collector or verifier.

The broad ingredients overlap Semaev summation relations, rational-map factor
bases, cover attacks, and split-Jacobian transfers.  Novelty is `OPEN`; the
exact local combination is not claimed novel.  After projection, the row may
still collapse to a known six-point Semaev/Petit-style relation.

### Narrow result

BNIT proves that an auxiliary split Jacobian can expose a mechanically valid,
target-coupled native relation source for the original prime-field quotient.
The tested direct, large-prime, streaming, and bounded-cache algorithms do not
turn that source into a rho improvement.

### PO-transfer-004 closeout

`PO-transfer-004` implemented the Plucker-pair batch incidence gate.  Its
determinant/wedge equivalence is exact after shared-index and repeated-abscissa
filters, but orthogonality is a hyperplane query rather than an equality hash.

The final blind-target sweep covers eight curves and 24 factor-base
configurations.  Five hundred random controls cover every target and
configuration; every planted control uses four actual factor-base lifts and
replays through the production relation path.  The independent verifier checks
1,603 final rows and 2,973 primitive cubic witnesses.

The lane closes negative under the tested model:

- every normalized pair plane is unique;
- base incidence/null ratios are `0.927..1.110`;
- base incidence/random-control ratios are `0.886..1.150`;
- charged work is `8652.33..115587.62x` rho on base cells;
- the unimplemented oracle floor is `132.67..451.81x` rho;
- base memory is `68.3..200.6 sqrt(n)`;
- charged and oracle-floor toy exponents are `0.958` and `0.561`.

This is a negative result for BNIT's explicit Plucker quotient, not for
auxiliary-object transfer.

### Next concrete action

Build `PO-transfer-005` around the harder representation question: lift the
original target into the quotient

```text
E(F_{p^m}) / ker(Tr_m) ~= E(F_p),  m in {2,3},
```

and test whether a public extension-field factor base plus a real algebraic
decomposition solver can exploit trace-fiber representatives more cheaply than
direct search on the pushed-forward factor base.  Coset multiplicity alone is
not a claimed gain; the first proof obligation is the quotient-collapse lemma,
and the first experiment must compare structured extension solving against the
exact pushed-forward multiset and random-coset controls.

### Artifacts

- `research/PO_transfer_003_contract.md`
- `research/PO_transfer_003b_contract.md`
- `research/PO_transfer_003c_contract.md`
- `research/PO_transfer_003d_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage`
- `experiments/ecdlp_isogeny/po_transfer_003_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_003_result.md`
- `experiments/ecdlp_isogeny/po_transfer_003{,b,c,d}_result.json`
- `experiments/ecdlp_isogeny/po_transfer_003d_verify.json`
- `research/PO_transfer_004_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_004_plucker_incidence_gate.sage`
- `experiments/ecdlp_isogeny/po_transfer_004_result.md`
- `experiments/ecdlp_isogeny/po_transfer_004_result.json`
- `experiments/ecdlp_isogeny/po_transfer_004_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_004_verify.json`

## PO-transfer-005/006 pivot: from multiplicity to complementary labels

Date: 2026-07-13

The trace-quotient audit produced an exact restricted theorem: for a finite
abelian-group homomorphism `tau:H->G`, tuples in `tau^-1(Q)` are exactly the
weighted tuples whose images sum to `Q`.  Full kernel fibers multiply successes
and trials equally, and repeated images are duplicate base-group columns.  Raw
trace-fiber multiplicity is therefore not a relation-probability or rank gain.

The only surviving `PO-transfer-005` loophole is solver time in genuine
extension coordinates.  That loophole must be compared against the older
scalar Weil-restriction evidence (`PO-004`/`NR-022`) before execution; it is not
currently the highest-value transfer experiment.

A review of the stalled `round016_exp030c_theta_settle.sage` found that it is not
a faithful Kummer/theta transfer object:

- it models `E x E` over `F_p`, not `Res_{F_{p^2}/F_p}(E)`;
- its accumulated Hadamard-square product is not a verified differential
  addition chain;
- summand membership is incomplete and the auxiliary difference point receives
  only a Segre row;
- its `auto_descent` is an unrelated direct discrete-log call;
- the first production cell is positive-dimensional (`12` variables and `8`
  equations) and consumed about 2.9 GB in the Macaulay rank step before the run
  was stopped.

No negative result about true theta/Kummer transfer is inferred from that
script.

### Harder active goal

`PO-transfer-006` replaces the surrogate with the exact generic degree-3 maps
of a `(3,3)`-split genus-2 curve.  The complementary quotient labels each lift
of an `E1` point.  A complete `phi2` fiber pushes to a constant-sum ternary
relation on `E1`, so a lift of a public target exposes up to three cofiber
decompositions.

The hard gate is not relation correctness.  It is whether this ternary
cofiber hypergraph has non-random factor-base completion or rank overlap versus
relation-valid generic triples.  Fixed degree alone supplies only constant
multiplicity.  A selected subgraph with `t` rows and `B` columns has
`rank <= t`, so reusable logs require at least `t >= B-1`; zero relations that
continually introduce fresh columns do not count as progress.

### Status

`NEGATIVE RESULT / POSITIVE MECHANICAL SIGNAL / TOY-EVIDENCE /
UNRAMIFIED-AFFINE / MODEL-BOUND`.

The exact-map sweep completed on ordinary prime-order targets at
`p=101,211,431` and independently replayed successfully.  All 114 complete
cofibers push to `O`, but production rows/rank/columns are only
`6/6/18`, `34/34/78`, and `74/74/174`.  Every two-core is empty, and matched
EC-addition triples reproduce the ranks exactly.  No tested factor base reaches
`B-1` rank or recovers a blind target.  The optimistic full-affine-enumeration
floor is already `26.92x,56.16x,80.33x` rho and has adverse toy fit `n^1.188`.

This closes fixed-degree unramified affine cofiber multiplicity under the tested
model.  It does not close exceptional/projective fibers or labels with genuine
norm/factorization semantics.

### Next concrete action

Write `PO-transfer-007` around a cyclic cover `X_d:z^d=h(P)`.  Target-couple a
principal divisor of `z-v`, factor its norm, merge duplicate pushed `E` images,
and compare actual norm smoothness/solver cost against the same relation built
directly in the elliptic function field.  Do not credit `d` preimages; require a
measured label-conditioned factorization advantage, reusable rank, and blind
descent.

### Artifacts

- `research/PO_transfer_005_contract.md`
- `research/PO_transfer_006_contract.md`
- `research/PO_transfer_006_theory.md`
- `experiments/ecdlp_isogeny/po_transfer_006_trielliptic_cofiber.sage`
- `experiments/ecdlp_isogeny/po_transfer_006_result.json`
- `experiments/ecdlp_isogeny/po_transfer_006_result.md`
- `experiments/ecdlp_isogeny/po_transfer_006_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_006_verify.json`
