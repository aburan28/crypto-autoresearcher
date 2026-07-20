# ECDLP-IDEA-019 — Target-dependent Kummer-cover zeta decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `proposed_unapproved`
- Revision: independent red-team cover-recipe, collision, genus, and point-count-cost findings incorporated
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; computing a zeta function or separating one toy coset is not a break.

## Falsifiable hypothesis

There is a deterministic bounded-conductor construction `R -> C_R` from a marked point on
a generic ordinary prime-field curve to a cyclic/Kummer cover whose Frobenius polynomial
separates scalar cosets. A frozen low-index subgroup chain and cohomological point-counting
recover `x` from `Q=[x]P` with collisions, comparison covers, conductor, genus, and memory
all charged below exponent `1/2`.

## Mechanism-new operation

Encode the public target into a cyclic cover and use its **Frobenius/zeta fingerprint as a
scalar-coset decoder**. This differs from idea 011's orbit-period evaluation and idea 006's
sequence shift: the observable is the cohomology of an auxiliary target-twisted curve. It
is not a post-hoc selector because the cover family, chain, and comparison rule are frozen.

## Assumptions

1. `<P>` has known prime order `N≈p`; the cover equations are computable from `E,P,R` without a logarithm.
2. Conductor/genus and every extension field are explicit and charged.
3. Fingerprints are canonical under allowed coordinate choices and have a measured collision law.
4. Child comparison covers can be generated without an explicit table of scalar multiples of square-root size.
5. Point-counting precision, failed covers, branching, and residual search are retained.
6. Scaling is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`marked_point_to_cyclic_Kummer_cover | bounded_conductor_Artin_L_function | Frobenius_scalar_coset_fingerprint | recursive_collision_charged_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates bypassing point decomposition.
2. `ledger/H-REP-001.yaml` — distinguishes an auxiliary cohomology object from a curve-model rewrite.
3. `ledger/H-ISO-001.yaml` — the covers are fingerprints, not same-field neighbors.
4. `ledger/H-FB-001.yaml` — child cosets are not an ordinary factor-base shape.
5. `ledger/SYNTHESIS-20260716.md` — supplies the complete-cost and red-team boundary.

## Closest primary literature

- Adolphson and Sperber, [Character sums in finite fields](https://www.numdam.org/item/CM_1984__52_3_325_0/), develops multiplicative-character-sum L-functions and their Kummer-cover interpretation; algorithmic use here is an inference.
- Kedlaya, [Counting points on hyperelliptic curves using Monsky–Washnitzer cohomology](https://arxiv.org/abs/math/0105031), supplies the cohomological point-counting baseline.
- Gonçalves, [A Point Counting Algorithm for Cyclic Covers of the Projective Line](https://arxiv.org/abs/1408.2095), gives the nearest explicit cyclic-cover algorithm.

These sources do not establish a scalar-separating bounded-conductor cover family. Novelty
remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is the frozen list of child-coset representatives and
cover fingerprints at each subgroup-chain level.

1. Factor `N-1`, freeze a low-index subgroup chain, cover recipe, canonicalization, and collision policy.
2. Construct `C_Q`, compute its Frobenius polynomial, and certify genus/conductor and precision.
3. Generate only the preregistered child representatives of the current scalar coset and compute their cover fingerprints.
4. Retain every matching child and continue until the candidate list is sub-square-root or singleton.
5. Exhaustively test the charged residual list on `E` and return only a scalar satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Freeze public `T` and covers `C_R^(r): z^r=(x-x(R))/(x-x(T))` for `r in {2,3}`.
Let reciprocal recipe availability be `N^zeta`, canonical/isomorphism cost `N^chi`, cover
construction `N^a`, number of refinement levels `N^ell`, child branching `N^gamma`,
reciprocal collision-removal density `N^delta`, genus `G=N^(eta_g+o(1))`, conductor
`N^eta_c`, and point-count exponent `q(eta_g,phi,pi)` for extension degree `N^phi`
and precision `N^pi`. The frozen degree-2/3 recipe has `eta_g=eta_c=0`. With
isomorphism comparison `N^i`, residual list `N^u`, verification `N^v`, and storage
`N^s`, rho costs `N^1/2` and BSGS costs `N^1/2` time/memory. The candidate has
time exponent `lambda=max(zeta,chi,a,ell+gamma+delta+q(eta_g,phi,pi),i,u+v)` and
memory exponent `mu=max(s,2*eta_g+phi+pi,eta_c,gamma,u)`. Enumerating a square-root-sized scalar table fails the
claim before point counting.

## Likely fatal obstruction

Extracting enough scalar information may force genus, conductor, number of child covers,
or fingerprint precision to grow as `N^(1/2)` or worse. Isogenous/translated targets can
also have identical zeta data, leaving massive collisions. Cheap point counts can therefore
coexist with rho-hard labeling.

## Proof track

Construct the cover family, prove canonical scalar-coset separation and bounded collision
rate, and bound genus, point counting, comparisons, and residual search so
`lambda,mu<1/2`.

## Disproof track

Exhibit large cosets with identical Frobenius polynomials, prove separating conductor/genus
or comparison count is at least square-root scale, or show construction needs scalar-orbit
enumeration.

## Positive and negative controls

- Positive control: cyclic covers with a planted coefficient-to-zeta fingerprint.
- Positive instrumentation control: exhaustive scalar orbits and zeta data on tiny curves.
- Negative control: random covers matched by genus, conductor, and coefficient distribution.
- Orbit control: idea 011's period invariant on the same subgroup chain.
- Leakage control: prohibit target-selected cover parameters and known-log comparisons.

## Quantitative promotion and falsification gates

The first gate exhausts 8–11-bit groups and samples 64 preregistered blinded marked points
per curve at 12–14 bits for the frozen degree-2 and degree-3 recipe, computes exact zeta
functions with a declared cyclic-cover cohomology routine, canonicalizes covers, and
measures scalar partitions. Brute force is a truth control only through 9 bits.
Promotion only to a scaling study requires canonical fingerprints, zero wrong labels,
collision-adjusted information gain at least 0.5 bits per charged comparison, no scalar
table in construction, and upper 95% `a<=0.35`,
`ell+gamma+delta+q(g,phi,pi)<=0.45`, `u<=0.20`, `lambda<=0.45`, and
`mu<=0.45`. Falsify if all fingerprints are scalar-independent or isomorphic, any label
is wrong, or genus/conductor/comparison lower bounds reach exponent `0.50`.

## Artifact plan

- `ideas/contracts/ECDLP-EXP-CONTRACT-019_kummer_cover_partition_preflight.yaml`
- `ideas/artifacts/ECDLP-IDEA-019/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-019/kummer_zeta_decoder.sage`
- `ideas/artifacts/ECDLP-IDEA-019/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-019/runs/<run_id>/covers.jsonl`
- `ideas/artifacts/ECDLP-IDEA-019/runs/<run_id>/fingerprints.jsonl`
- `ideas/artifacts/ECDLP-IDEA-019/analysis.md`

## Interpretation boundary

All evidence is toy, heuristic, model-bound, and novelty-unverified. A correct point count
or one separated coset is not an ECDLP break; the complete collision-charged descent must
beat rho/BSGS.

## Exactly one next executable action

1. Execute the blinded degree-2/3 Kummer-cover zeta-partition preflight in `ideas/contracts/ECDLP-EXP-CONTRACT-019_kummer_cover_partition_preflight.yaml` after coordinator approval.
