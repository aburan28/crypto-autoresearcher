# Ascending Volcano Self-Pairing Prototype

Date: 2026-06-02

## Result

Status: `OBSERVATION`

Evidence type: `TOY-EVIDENCE`

Candidate: exploit Frobenius/distorted Weil self-pairings on discriminant torsion to reduce the unknown action of an ascending vertical isogeny to a small square-root candidate set.

The implementation in `experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py` validates the computable core of Galbraith-Gilchrist-Robert's ascending-volcano approach on a toy ordinary volcano edge.

## Experiment Contract

Hypothesis: for a known ascending isogeny `phi:E0 -> E1`, with `m | disc(End(E1))` and `gcd(m,deg(phi))=1`, the distorted Weil pairings with `tau=2*pi-t` recover a finite candidate list for `a` satisfying `phi(tau(P0)) = a*tau(P1)`.

Null hypothesis: the actual scalar is not in the self-pairing candidate set, or the ascending kernel is not predicted by the canonical Frobenius-imaginary kernel in the theorem-covered case.

Parameters:
- field/curve family: ordinary curves over prime fields;
- toy instance: `p=13`, `E0:y^2=x^3+x+2`;
- vertical degree: `ell=2`;
- discriminants/conductors: `disc0=-48`, `conductor0=4`, `disc1=-12`, `conductor1=2`;
- self-pairing torsion: `m=3`;
- baseline: known Sage isogeny used only as a validation oracle.

Metrics:
- self-pairing candidate count;
- whether actual scalar is in candidate set;
- whether `ker(phi)` equals `E0[ell,omega]`;
- torsion extension degrees.

Positive control: the selected instance satisfies the theorem-covered even-top-discriminant case.

Negative/control branch: the first found toy instance `p=11`, `disc1=-7`, `ell=2` hit the paper's exceptional even-conductor/odd-top-discriminant case; the simple `E0[ell,omega]` kernel check failed there, matching the need for the separate Remark 3.2 treatment.

Reproduction command:

```bash
sage -python experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py --out experiments/ecdlp_isogeny/iso_ascending_self_pairing_result.json
```

## Evidence

The validated run wrote `experiments/ecdlp_isogeny/iso_ascending_self_pairing_result.json`.

Key output:
- `candidate_scalars=[1, 2]`;
- `actual_scalars=[2]`;
- `actual_in_candidates=true`;
- `ascending_kernel.kernels_equal=true`;
- self-pairing torsion extension degree `3`;
- ascending-kernel torsion extension degree `2`.

## Limitations

This is not a full implementation of the paper's isogeny-recovery algorithm. The high-dimensional Kani/interpolation reconstruction stage is still `OPEN`.

The experiment is toy-scale and uses Sage's known isogeny as a validation oracle. It does not claim deployment relevance, a SCALLOP break, or an ECDLP speedup.

## Red-Team Notes

The result measures the torsion-information step, not the full reconstruction cost.

The candidate set has size two because `m=3`; larger `m` with many prime factors can produce more square-root branches.

The search now filters out the known exceptional `ell=2`, odd `disc1` branch for the default positive control. That branch should be implemented separately using the paper's Remark 3.2 formula rather than counted as a failure of the main theorem.

## Handoff

### Claim or task
Validate the cyclic self-pairing torsion-recovery primitive for ascending volcano edges and preserve the next implementation step.

### Status
OBSERVATION

### Assumptions
- ordinary toy curves over `F_p`;
- theorem-covered vertical edge for the default run;
- known isogeny used as oracle only for validation;
- no Kani reconstruction yet.

### Evidence so far
- `iso_ascending_self_pairing_result.json` has `success=true`;
- self-pairing candidates contain the actual scalar;
- ascending kernel equals `E0[ell,omega]`.

### Failure modes
- exceptional `ell=2`, odd-top-discriminant branch needs the Remark 3.2 kernel formula;
- extension degree may be large even for small `m`;
- full recovery still needs Kani/interpolation machinery.

### Next concrete action
Implement a smooth-`n1` Kani/interpolation reconstruction stub and test the condition `n1^2*m > 4*deg(phi)` on toy vertical inputs.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py`
- `experiments/ecdlp_isogeny/iso_ascending_self_pairing_result.json`

---

## Round 2: Target-Free Prime-Degree Recovery

Date: 2026-07-13

Status: `OBSERVATION`

Evidence type: `TOY-EVIDENCE / MODEL-BOUND`

The prototype now constructs theorem-covered prime-degree ascending isogenies,
not only their self-pairing scalar candidates. The construction function accepts
`(E0,p,t,disc0,ell)`, computes `E0[ell,omega]`, descends its kernel polynomial
to `F_p`, and builds the Velu quotient. It records
`construction_oracle_calls=0`; neither the public target nor the withheld Sage
edge is a construction input. Target identification and secret-edge validation
run only after the kernel and quotient map are frozen.

The exact contract is in
`experiments/ecdlp_isogeny/iso_ascending_recovery_contract.md` and the run is in
`experiments/ecdlp_isogeny/iso_ascending_recovery_result.json`.

### Sweep Evidence

The main four-field sweep recovered all `4/4` cases:

| `p` | `D_K` | `ell` | source/target conductor | torsion degree `u` | result |
|---:|---:|---:|---:|---:|---|
| 13 | -3 | 2 | 4/2 | 2 | exact kernel and map match |
| 19 | -3 | 5 | 5/1 | 20 | exact kernel and map match |
| 29 | -20 | 2 | 2/1 | 2 | exact kernel and map match |
| 31 | -3 | 5 | 5/1 | 10 | exact kernel and map match |

A primary robustness stratum excluding `D_K in {-3,-4}` recovered `3/3`
additional cases over `p in {29,37,41}`. A separate odd-degree non-special-CM
stratum recovered a degree-3 ascent over `p=67`, `D_K=-7`. Every accepted case
had exact withheld-kernel equality and exact rational-map agreement up to an
explicitly enumerated target automorphism. Agreement on eight distinct source
points is retained as a secondary readable check.

The exceptional `p=11`, `ell=2`, `disc1=-7` negative control was rejected with
an orientation-kernel cardinality mismatch, as expected outside Corollary 3.4's
simple even-degree branch. This is a scoped negative result for that formula,
not for the Remark 3.2 construction.

The same target-free primitive also composes across a squarefree conductor in
the coprime-prime case. A three-field sweep over `p in {181,199,211}`, each with
Frobenius discriminant `-675` and source conductor `15`, tests both prime orders
`3 -> 5` and `5 -> 3`. All `6/6` paths recover a degree-15 map to conductor `1`.
Every composite has zero construction oracle calls and exact rational-map
equality with its withheld two-step path up to endpoint automorphism. Step
torsion degrees range from `3` through `20`.

This works because earlier distinct-prime ascent factors are units modulo the
next torsion prime, so the original `Z[pi]` imaginary generator defines the same
kernel as the newly saturated generator. It does not cover repeated prime
powers, where that multiplier is no longer invertible.

`RESTRICTED THEOREM`: if the old oriented generator satisfies
`omega_old=c*omega_new` on the current curve and `gcd(c,ell)=1`, then
`E[ell,omega_old]=E[ell,omega_new]`. Indeed, multiplication by `c` is an
automorphism of `E[ell]`, so the two kernels are equal. The composite control
applies this only to distinct odd prime factors of the conductor. Its disproof
boundary is a repeated prime, where `c` is zero-divisive modulo `ell` and the
argument no longer applies.

The composite timing fit is also diagnostic only. Over six cases in three
nearby fields, log wall time versus log `p` has slope `2.07` with `R^2=0.010`,
while the torsion proxy `sum(u_i^2)` has slope `1.42` with `R^2=0.708`. This is
consistent with the prime sweep's warning that extension behavior dominates
tiny runtimes; it is not an asymptotic estimate.

Widening the fixture search exposed a verifier hazard at `p=499`, `D_K=-8`:
the target-free `3 -> 5` construction succeeds and ends at a `j`-invariant where
the reduced maximal Hilbert class polynomial vanishes, while Sage reports the
conductor path `15 -> 5 -> 3` instead of the expected local path `15 -> 5 -> 1`.
This is recorded as `OBSERVATION / TOOLING-RISK`; conductor classification alone
must not be used as the acceptance gate when ring-class reductions collide.

### Baseline And Cost Interpretation

Each case records Sage rational prime-isogeny enumeration and a post-hoc Velu
construction from the withheld known kernel. These are the relevant toy
isogeny-recovery baselines; Pollard rho is not a baseline for this primitive.

Sage does not expose exact low-level field-operation counts here. The artifact
therefore records torsion samples, order calls, scalar projections, pairings,
orientation evaluations, kernel factors, extension degree, wall-clock, and raw
`ru_maxrss`. The four-point diagnostic fit gives slope `0.223` for log wall time
versus log `p` with `R^2=0.004`, and slope `0.617` versus the proxy `u^2+ell`
with `R^2=0.819`. These are `HEURISTIC / TOY-EVIDENCE` diagnostics over mixed
tiny regimes, not asymptotic estimates. The useful observation is narrower:
extension-field behavior is already more predictive than field size in this
sample and must be charged in the next sweep.

### Red-Team Boundary

Resolved in this round:

- construction is split from target identification and reports zero oracle use;
- exact kernel, degree, codomain isomorphism, and rational-map agreement are
  separate acceptance gates;
- target automorphisms are enumerated, including special-`j` cases;
- special-CM, non-special-CM, odd-degree, and exceptional negative strata are
  reported separately;
- relevant isogeny-recovery baselines and high-level operation counters are
  retained.

At the close of Round 2, still open:

- the source conductor/discriminant is supplied by Sage's endomorphism-order
  machinery in the harness;
- exact base-field-equivalent arithmetic and memory accounting is incomplete;
- tiny-field ring-class collisions can make Sage conductor classification an
  ambiguous verifier;
- distinct-prime squarefree ascent composes, but repeated prime powers and
  general orientation push-forward are not implemented;
- the exceptional `ell=2` Remark 3.2 formula is not implemented;
- self-pairing branches have not yet been connected to a working
  Kani/interpolation reconstruction.

### Handoff: prime-degree recovery to composite ascent

### Claim or task
Extend the validated squarefree composition to a repeated-prime ascent and
measure the cost of representing the divided/pushed-forward orientation.

### Status
OPEN

### Assumptions
- ordinary toy curves over prime fields;
- floor source with `End(E0)=Z[pi]` at the first step;
- factorized smooth conductor quotient;
- effective Frobenius orientation.

### Evidence so far
- `4/4` main, `3/3` non-special-CM, and `1/1` odd-degree non-special-CM cases
  recover exactly;
- both conductor-15 prime orders recover exact degree-15 composite maps;
- construction uses neither target curve nor secret edge;
- the unsupported exceptional formula is rejected by the negative control.

### Failure modes
- pushed-forward orientation may be expensive or unavailable;
- torsion extension degree may dominate composite paths;
- horizontal ambiguity can appear outside the strict prime floor ascent.

### Next concrete action
Generate a conductor divisible by `ell^2`, implement an effective representation
of the divided orientation after the first ascent, and recover the second
`ell`-kernel without Sage edge enumeration.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_ascending_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py`
- `experiments/ecdlp_isogeny/iso_ascending_recovery_result.json`
- `research/red_team_ascending_isogeny_recovery.md`
- `research/ascending_isogeny_recovery_theories.md`

---

## Round 3: Repeated-Prime Orientation Division

Date: 2026-07-14

Status: `OBSERVATION`

Evidence type: `TOY-EVIDENCE / MODEL-BOUND`

The repeated-prime boundary from Round 2 is now implemented. After `r` prior
ascending `ell`-steps, the harness evaluates the divided saturated orientation
on `P in E_r[ell]` by enumerating lifts `Q in E_r[ell^(r+1)]` with
`[ell^r]Q=P` and computing the original Frobenius-imaginary endomorphism
`omega_0(Q)`.

### Restricted Lemma

Assume the oriented order chain gives `omega_0=[ell^r]omega_r` in
`End(E_r)`, where `omega_r` is the saturated imaginary generator. For any lift
`Q` with `[ell^r]Q=P`,

```text
omega_0(Q) = [ell^r]omega_r(Q) = omega_r([ell^r]Q) = omega_r(P).
```

If `Q'` is another lift, then `Q-Q' in E_r[ell^r]`, so
`omega_0(Q-Q')=[ell^r]omega_r(Q-Q')=0`; the value is independent of the
lift. This is a `RESTRICTED THEOREM` under the stated integral normalization.
The code checks the identity empirically across every lift in each toy fixture.

### Experiment Evidence

The pre-registered contract is
`experiments/ecdlp_isogeny/iso_repeated_prime_orientation_contract.md`.

Two three-field strata pass:

| stratum | fields | total degree | largest lift torsion | largest extension degree | result |
|---|---|---:|---:|---:|---|
| conductor `9`, exponent `2` | `67,73,103` | 9 | 9 | 18 | `3/3` exact |
| conductor `27`, exponent `3` | `577,619,757` | 27 | 27 | 54 | `3/3` exact |
| non-special conductor `9`, exponent `2` | `163,211,223` | 9 | 9 | 9 | `3/3` exact |

All `9/9` constructions report zero target/secret-edge calls. Every projected
`E[3]` point has a lift-independent image in `E[3]`; every divided kernel has
exactly three points and a base-rational linear kernel polynomial. The final
degree-9 or degree-27 composite has exact rational-map equality with its
withheld ascending path up to an enumerated endpoint automorphism.

At exponent `3`, the final step enumerates all `729` points of `E[27]`. The
three lift-extension sequences are `(6,18,54)`, `(6,18,54)`, and `(3,9,27)`.
No lift inconsistencies were found.

The non-special-CM stratum has `D_K in {-8,-11}`. Because tiny-field conductor
classification is ambiguous there, its independent verifier enumerates all
rational length-two degree-3 paths and selects the unique endpoint whose `j`
zeros the reduced fundamental Hilbert class polynomial. Each field has depth
state counts `(1,4)`, exactly one selected path, and exact map agreement. Thus
the verifier does not use the recovered target or conductor labels to choose the
reference path.

### Negative Control

Directly evaluating `omega_0` on `E_r[3]` after the first ascent gives all nine
points as zeros, exactly as `omega_0=[3^r]omega_r` predicts. The harness records
`naive_direct_kernel_size=9` at every later step and rejects it; the lifted
predicate reduces this to the unique three-point ascending kernel. This is a
`NEGATIVE RESULT` for naive direct reuse, not for divided orientation recovery.

### Cost Boundary

This is currently a correctness algorithm, not a speed improvement. The toy
implementation constructs and enumerates full `ell^(r+1)` torsion, so point
count grows as `ell^(2r+2)` and the torsion extension can also grow with `r`.
Across the mixed nine-case sample, log wall time versus the proxy
`sum(u_i^2)` has slope `1.307` with `R^2=0.938`; log wall time versus log `p`
has slope `1.856` with `R^2=0.654`. These are diagnostic fits across tiny mixed
strata, not asymptotic evidence.

The next algorithmic question is whether one can obtain a single compatible
lift, or evaluate the divided endomorphism, without constructing the full
higher-power torsion. X-only division polynomials, pushed-forward orientation
representations, and higher-dimensional endomorphism division are the live
routes.

### Handoff: repeated-prime correctness to efficient division

### Claim or task
Replace exhaustive full-torsion lifting with a scalable effective division of
the orientation, while preserving target-free exact recovery.

### Status
OPEN

### Assumptions
- ordinary toy curves over prime fields;
- odd repeated prime `ell=3`;
- source orientation is primitive and its conductor factorization is known;
- exact target and secret edges remain verifier-only.

### Evidence so far
- exponent `2` and `3` strata pass `9/9` exact composite-map gates, including
  three non-special-CM cases;
- all lift choices agree in every enumerated fixture;
- naive direct orientation evaluation is correctly non-discriminating;
- extension degree and full-torsion point count already dominate the cost.

### Failure modes
- an efficient single-lift routine may cost as much as full torsion construction;
- integral normalization can fail in the exceptional `ell=2` branch;
- horizontal, descending, and wrong-level controls remain narrower than the
  positive evidence;
- no Kani/interpolation or deployment-scale speed claim follows from this.

### Next concrete action
Implement an x-only or division-polynomial lift for the second `ell=3` step and
compare its base-field-equivalent cost against full torsion enumeration and
degree-3 neighbor enumeration.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_repeated_prime_orientation_contract.md`
- `experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py`
- `experiments/ecdlp_isogeny/iso_ascending_recovery_result.json`
- `research/red_team_repeated_prime_orientation.md`

---

## Round 4: Pairing-Certified Efficient Lift Selection

Date: 2026-07-14

Status: `OBSERVATION / NEGATIVE RESULT`

Evidence type: `TOY-EVIDENCE / MODEL-BOUND`

Round 3 established correctness by enumerating all
`ell^(2r+2)` points of `E_r[ell^(r+1)]`. This round separates three ways to
obtain the one lift needed by the divided-orientation identity:

1. scalar-normalized random lift sampling;
2. projective selection from a randomly sampled torsion basis;
3. projective selection from Sage's algebraic `torsion_basis` backend.

The pre-registered contracts are:

- `experiments/ecdlp_isogeny/iso_repeated_prime_single_lift_contract.md`;
- `experiments/ecdlp_isogeny/iso_repeated_prime_basis_guided_contract.md`;
- `experiments/ecdlp_isogeny/iso_repeated_prime_algebraic_basis_contract.md`;
- `experiments/ecdlp_isogeny/iso_repeated_prime_wrong_level_contract.md`.

### Restricted Pairing Certificate

Assume `omega_0=[ell^r]omega_r` on `E_r`, and choose
`Q in E_r[ell^(r+1)]`. Define

```text
P = [ell^r]Q,       I = omega_0(Q) = omega_r(P).
```

If `e_ell(P,I)` has exact order `ell`, then `(P,I)` is a basis of
`E_r[ell]`. Under the primitive-orientation and nilpotent canonical-imaginary
normalization used by Corollary 3.4, `P` is an `R_r`-generator and `I`
generates `E_r[ell,omega_r]`, the ascending kernel. This is a
`RESTRICTED THEOREM`; the pairing alone does not certify ascent outside these
orientation, level, and normalization assumptions.

Given a basis `(U,V)` of `E_r[ell^(r+1)]`, the lifts
`U+cV` for `c in F_ell`, together with `V`, project onto all `ell+1` lines of
`E_r[ell]`. The implementation tests these four classes for `ell=3`, rejects
the one zero-image line, and freezes the first primitive-pairing class.

### Exact Evidence

All three efficient variants pass the existing nine-fixture gate. Across the
`21` algebraic-basis steps:

- every accepted basis point has exact order `ell^(r+1)` and every basis Weil
  pairing has that exact order;
- exactly four projective lift representatives are tested per step;
- exactly one zero-image line is rejected and three primitive lines are found;
- every cyclic kernel has three points and equals the exhaustive-control kernel;
- every degree-9 or degree-27 composite equals the independently withheld map
  exactly up to endpoint automorphism;
- construction target/secret-edge calls remain zero.

At each exponent-three final step, the algebraic method tests four projective
representatives rather than enumerating all `729` points of `E[27]`. It still
constructs the full torsion field, whose degree reaches `54`, and obtains two
full-order torsion points. The point-count reduction is not a claim that this
algebraic work disappeared.

### Negative Results

Scalar-normalized random sampling has an unbounded rejection tail in the tested
group representation. On the seeded `p=757` path it takes about `1.099` seconds,
while the algebraic-basis path takes about `0.119` seconds. Random-basis sampling
has the same structural bias because its point normalization can collapse onto
one primary invariant-factor line.

The algebraic backend is not a universal runtime improvement. On `p=577` it
takes about `7.099` seconds versus `7.142` exhaustive and `3.524` random
single-lift. It beats exhaustive in `9/9` seeded rows but only barely on that
fixture, and beats random single-lift in only `2/9`. Sage local degree-3
neighbor enumeration takes only milliseconds in every row, under a different
orientation-selection information model. These timings are diagnostic, not
asymptotic evidence.

### Wrong-Level Control

After each correct prefix with `r>0`, the harness deliberately retries the
algebraic projective selector with division power `r-1`. All `12/12`
under-division attempts inspect four classes, obtain four zero images, accept
no primitive pairing, make zero target-oracle calls, and raise the explicit
no-compatible-lift error. This resolves under-division selectivity for these
toy fixtures. Over-division, wrong orientation, horizontal/descending edges,
and the exceptional `ell=2` branch remain open.

### Handoff: torsion-field removal and reconstruction

### Claim or task
Remove or amortize full torsion-field and algebraic-basis construction, then
connect the recovered vertical action to the smooth-`n1` Kani/interpolation
reconstruction.

### Status
OPEN

### Assumptions
- ordinary prime-field curves with an effective Frobenius orientation;
- odd repeated prime `ell=3` and the integral divided-orientation identity;
- Sage algebraic torsion basis is currently a strong black-box primitive;
- exact targets and secret paths remain verifier-only.

### Evidence so far
- exhaustive, random single-lift, random-basis, and algebraic-basis paths all
  recover `9/9` exact composites;
- projective selection has a deterministic `ell+1` candidate bound once a
  torsion basis is available;
- all twelve under-division controls reject;
- full torsion-field degree, not projective representative count, remains the
  dominant unresolved cost.

### Failure modes
- `torsion_basis` may hide polynomial factorization and extension arithmetic
  that dominates deployment-size instances;
- over-division or a mis-normalized orientation may still pass an incomplete
  gate;
- local neighbor enumeration is much faster at these toy sizes;
- no horizontal bridge, Kani reconstruction, or ECDLP consequence follows.

### Next concrete action
Implement an x-only division-polynomial kernel evaluator or pushed-forward
effective orientation that avoids constructing the full `E[ell^(r+1)]` basis;
run over-division and wrong-orientation controls under the same exact-map gate.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_ascending_self_pairing.sage.py`
- `experiments/ecdlp_isogeny/iso_ascending_recovery_result.json`
- `research/red_team_efficient_repeated_prime_orientation.md`

## Round 5: Self-Pairing Torsion Interpolation

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

This round connects the paper's non-degenerate self-pairing conic to an actual
toy isogeny representation. The construction receives only public endpoint
curves, known degree `d`, trace/Frobenius orientation data, and a prime torsion
modulus `n` satisfying `n^2 >= 4d+1`. It samples cyclic `Z[pi]` generators,
computes the pairing norm `v`, enumerates

```text
a^2 + N(omega)b^2 = v (mod n),
```

and interpolates each candidate x-map as a rational function with numerator
degree `d` and denominator degree `d-1`. Base-field descent, a symbolic
source-to-target curve identity, and the proposed full torsion action are all
checked before any secret isogeny is loaded.

This is a direct rational-map interpolation backend. It is not the paper's
higher-dimensional Kani reconstruction and has no cryptographic-size cost
claim.

### Exact Evidence

The formal result covers four public fixtures over `F_13`, `F_19`, `F_29`, and
`F_31`, with degrees `2,5,2,5` and torsion primes `5,7,3,7`. The `F_29` case is
tight at `n^2 = 4d+1 = 9`. Across seeds `20260714..20260716`:

- all four construction paths make zero secret-isogeny evaluations;
- accepted branch counts are `2,6,2,6`, exactly the public target
  automorphism counts;
- every accepted branch lies in the post-hoc withheld map's target-automorphism
  orbit;
- oracle-provided torsion images reconstruct the withheld representative in
  all positive controls;
- all degree-`d-1` controls reject;
- the undersized control `n^2=25 < 4d+1=29` rejects before interpolation.

After Red Team review, the harness also runtime-blocks all four withheld-map
helpers during construction and hashes each serialized public construction
report before verifier entry. Degree-`d+1` and corrupted torsion-action controls
reject in every case. A verifier-only forced below-threshold control bypasses
the admission rule at `(p,d,n)=(43,7,5)` and obtains a `12 x 15` interpolation
matrix of rank `12` and nullity `3`, directly confirming underdetermination for
that fixture. Peak RSS is normalized to bytes/MiB on macOS rather than mislabeled
as kilobytes.

### Negative Results and Corrections

The first implementation assumed every endpoint model admitted a unit-scaling
normalized map. This failed on the degree-5 fixtures: Sage's withheld maps have
differential scalings `16` over `F_19` and `26` over `F_31`. The corrected
construction recovers the x-leading ratio, enumerates its two y-scaling roots,
checks the curve equation, and lets torsion action select the sign.

The first contract also required a unique map. That is too strong from norm
data: generic targets yield `phi` and `-phi`, while the `j=0` targets yield six
post-compositions by target automorphisms. The implementation now returns a
deterministic valid connecting map and records the complete public orbit.

### Handoff: Kani backend and composite degrees

### Claim or task
Replace the toy coefficient-size rational-map interpolator with a smooth-`n`
higher-dimensional Kani/interpolation backend, while preserving the same
secret-free construction audit.

### Status
OPEN

### Assumptions
- ordinary prime-field short-Weierstrass curves;
- prime torsion coprime to `p*d*Delta_pi`;
- effective Frobenius orientation;
- current fixtures use prime-degree ascending isogenies only.

### Evidence so far
- self-pairing conics provide sufficient torsion-action branches in all four
  toy fixtures;
- public interpolation and curve identities separate valid connecting maps;
- automorphism ambiguity is classified exactly;
- threshold, wrong-degree, oracle-boundary, and randomized-seed controls pass.

### Failure modes
- interpolation matrices have `2d+1` columns and are not a scalable substitute
  for the Kani machinery;
- full torsion fields are still constructed;
- composite-degree, degenerate-conic, and mixed `n1/n2` recovery are untested;
- no ECDLP or deployment-security consequence follows.

### Next concrete action
Implement the balanced smooth-`n` Kani special case on a toy degree-`d` map
with `n^2 >= 4d+1`, using the same self-pairing branch data, then compare its
output and operation counts against this exact rational-map control.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_torsion_interpolation_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_torsion_interpolation_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_torsion_interpolation_recovery_result.json`
- `research/red_team_torsion_interpolation_recovery.md`

## Round 6: Balanced Kani Theta Split Gate

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

This round implements the first actual higher-dimensional quotient in the
self-pairing recovery line. The public fixture is

```text
p=43, d=7, N=8, x=1, N=d+x^2, N^2=64 >= 4d+1=29,
End(E0) conductor 7, End(E1) conductor 1.
```

For an `R=Z[pi]` generator `P`, the construction computes the full Frobenius
norm conic

```text
a^2 + t*a*b + p*b^2 = v (mod 8)
```

and forms the graph kernel generated by `(xP,gamma(P))` and
`(x*pi(P),gamma(pi(P)))`. Each candidate kernel is sent through a chain of
three `(2,2)` theta isogenies using the pinned authors' implementation. A
branch is accepted only when both kernel generators die and the quotient
splits into exactly one source-isomorphic and one target-isomorphic factor.

The theta splitting is not canonical enough to expose the original degree-7
matrix entries directly. Therefore the quotient is a split gate, while the
Round 5 rational-map interpolator independently serializes accepted maps. The
two branch selectors must agree; coefficient extraction is not attributed to
the theta quotient.

### Exact Evidence

Across seeds `20260714..20260716`, every run reports:

- public endomorphism conductors `7 -> 1` and torsion extension degree `12`;
- `12` norm-conic branches, all with isotropic graph kernels;
- `6` theta-accepted and `6` rejected branches;
- exactly the same `6` branches accepted by exact rational-map interpolation;
- all six per-seed basis transforms split for valid kernels and fail for invalid
  kernels (`36/36` in each class per seed);
- the first seed exhaustively checks all `1536` elements of `GL_2(Z/8Z)` on
  every branch: all `9216` valid branch/basis pairs pass and all `9216` invalid
  pairs fail;
- a deliberately non-isotropic mutation has pairing order `8` and is rejected
  before the theta constructor is called;
- zero withheld-helper calls during construction, a frozen pre-verifier hash,
  and post-hoc coverage of the six target automorphisms exactly once.

After Red Team review, interpolation was moved into
`iso_public_torsion_interpolation.py`, which contains no verifier or
secret-isogeny API; the balanced constructor no longer imports the earlier
mixed construction/verifier script.

The authoritative result passes deep JSON assertions and its recorded script
and public-helper SHA-256 values equal the current file hashes. Peak RSS is
`327.734375 MiB`; the complete three-seed run, including `18432` exhaustive
theta constructions, takes about `39.75 s` on the recorded machine.

### Red Team Disposition

The independent Red Team correctly identified that the first result only
tested six of the `1536` invertible basis changes and that `runpy` loaded a
helper module containing verifier APIs. Both issues are closed in the current
artifact by the exhaustive first-seed sweep and the public-only interpolation
module with a recorded forbidden-API marker scan.

The remaining objections stay `OPEN`: the target is the special `j=0`,
discriminant-`-3` endpoint with six automorphisms; there is no wrong-endpoint
same-trace control; and three seeds on one curve are replication, not a
parameter-family sweep.

### Negative Results and Corrections

Because `N=8` is even while `disc(Z[pi])=-147` is odd, the trace-zero element
`2*pi-t` generates an index-2 suborder locally. Its distorted pairing has
order `4` on both endpoints, so it cannot parameterize the full `8`-torsion
action. The corrected construction uses `pi` itself and its norm form.

The theta quotient proves a split-product property for this graph kernel, but
its chosen product splitting does not canonically recover the degree-7 map.
This is a negative result for direct coefficient extraction from the current
library interface, not for Kani reconstruction in general.

### Handoff: Mixed-torsion Kani recovery

### Claim or task
Generalize the balanced split gate from `N=8`, `N-d=1` to composite smooth
torsion and the paper's sums-of-squares or mixed `n1/n2` constructions.

### Status
OPEN

### Assumptions
- ordinary prime-field oriented curves with known degree and effective
  Frobenius orientation;
- public torsion fields and theta-compatible Montgomery models are available;
- the current evidence is one prime-degree ascent over one field;
- exact interpolation remains an independent toy verifier, not a scalable
  backend.

### Evidence so far
- the public conic supplies all twelve candidate actions;
- the balanced theta quotient separates the six valid automorphism branches;
- exhaustive `GL_2(Z/8Z)` basis transforms, non-isotropic mutation, the
  public-only helper boundary, oracle isolation, and three seeds pass;
- accepted explicit maps agree with the withheld orbit only after the public
  construction payload is frozen.

### Failure modes
- general auxiliary dimensions may require theta models not covered by the
  vendored `(2^e,2^e)` implementation;
- mixed `n1/n2` torsion introduces CRT branch growth and field composita;
- canonical projection tracking may cost as much as independent map recovery;
- full torsion fields and coefficient-size interpolation remain toy-scale
  bottlenecks;
- no asymptotic, deployment, SCALLOP, or ECDLP claim follows.

### Next concrete action
Implement a two-prime smooth-torsion fixture with an explicit sum-of-two-squares
auxiliary, measure incremental CRT branch rejection, and compare the complete
cost against the exact interpolation baseline.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_public_torsion_interpolation.py`
- `experiments/ecdlp_isogeny/vendor/two_isogenies_theta_sagemath/VENDORED_FROM.md`
- `research/red_team_balanced_kani_recovery.md`

## Round 7: Composite Degree-15 Balanced Recovery

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

The balanced split gate now covers a composite ascending isogeny and a generic
target automorphism group. The public fixture is

```text
F_619,
E0: y^2=x^3+64*x+333,  j(E0)=551,
E1: y^2=x^3+152*x+311, j(E1)=39,
t=1, t^2-4p=-2475=15^2*(-11),
d=15, N=16, N=d+1, N^2=256 >= 4d+1=61.
```

Ring-class cross-evaluation is the endpoint-level gate:
`H_-2475(551)=0`, `H_-11(551)!=0`, `H_-11(39)=0`, and
`H_-2475(39)!=0`. This certifies conductor `15 -> 1` without a secret path.
Sage 10.9 instead labels the target endomorphism order as conductor `15`, so
that label is recorded only as a diagnostic and preserved as `ISO-AR-NR-010`.

The public constructor uses the full Frobenius norm conic modulo `16`, builds
each graph kernel, and computes the `(16,16)` quotient as four `(2,2)` theta
steps. Exact maps are still serialized independently by the public-only
interpolator.

### Exact Evidence

Across seeds `20260714..20260716`:

- the measured torsion extension degree is `24` and both Frobenius pairings
  have order `16`;
- the trace-zero pairings have order `8`, confirming the index-2 correction;
- all `24` norm-conic branches give isotropic graph kernels;
- theta and interpolation independently accept the same `2` branches and
  reject the other `22`;
- each seed tests `64` deterministic invertible `GL_2(Z/16)` basis changes on
  every branch: the two valid branches pass all `128` valid pairs and the 22
  invalid branches produce zero accepts;
- the first seed additionally tests every one of the `1536` `GL_2(Z/8)`
  reduction classes via canonical lifts to `Z/16`, giving `3072` valid accepts
  and zero invalid accepts, and all `256` high-bit lifts of `16` deterministic
  reduction classes, giving `512` valid accepts and zero invalid accepts;
- the non-isotropic mutation is rejected before any theta constructor call;
- construction uses zero verifier helpers, excludes both path-degree fields,
  records `verifier_only_fixture_values_present=false`, and freezes a payload
  hash;
- post-hoc maps cover the target's two automorphisms exactly once;
- verifier-only paths `3 -> 5` (`551 -> 169 -> 39`) and `5 -> 3`
  (`551 -> 306 -> 39`) independently classify every accepted branch into the
  same target-automorphism orbit and every rejected branch outside it;
- truncated verifier paths `[3]`, `[5]` and repeated paths `[3,3]`, `[5,5]`
  all reject with explicit failure reasons.

The authoritative three-seed run takes `208.78 s`, peaks at `340.9375 MiB`,
and records script/helper hashes that match the current files.

### Red Team Disposition

The independent Red Team identified incomplete `GL_2(Z/16)` coverage,
asymmetric alternate-path verification, and missing wrong-path controls. The
current artifact closes the latter two completely and strengthens the first
with every reduction class modulo `8` plus a predeclared high-bit-lift stratum.
It does not claim exhaustive coverage of all `24576` elements of
`GL_2(Z/16)`. Wrong-endpoint constructor controls and a second composite
parameter family remain open.

### Handoff: Mixed-torsion or higher-dimensional auxiliary

### Claim or task
Move beyond the special balanced identity `N=d+1` and power-of-two theta
chains to mixed smooth torsion or a genuine sum-of-two-squares auxiliary.

### Status
OPEN

### Assumptions
- ordinary prime-field curves with effective Frobenius orientation;
- public ring-class endpoint certificates or another independent level test;
- the current theta backend handles only power-of-two `(2^e,2^e)` quotients;
- exact rational-map interpolation remains a toy serialization control.

### Evidence so far
- prime degree `7` and composite degree `15` both pass real theta split gates;
- special six-automorphism and generic two-automorphism targets are covered;
- both composite ascent orders agree only in the post-hoc verifier;
- fixed, exhaustive `GL_2(Z/8)`, sampled `GL_2(Z/16)`, and stratified
  mod-`8`-reduction/high-bit-lift basis controls pass;
- independent primary and alternate orbit tables agree branch-by-branch, and
  all four predeclared wrong paths reject.

### Failure modes
- the current backend cannot express non-power-of-two theta kernels or the
  dimension-four product required by a two-square auxiliary;
- ring-class polynomial evaluation is not a scalable endomorphism-ring
  algorithm by itself;
- stratified `GL_2(Z/16)` controls are still not exhaustive over all `24576`
  transforms;
- wrong-endpoint constructor controls remain unimplemented;
- one composite fixture is replication, not a parameter-family sweep;
- no asymptotic, deployment, SCALLOP, or ECDLP conclusion follows.

### Next concrete action
Prototype the smallest dimension-four Kani quotient with `N-d=a^2+b^2`, or,
if no compatible theta backend is available, implement a mixed-torsion CRT
branch-and-bound contract that measures exactly which missing quotient API is
the blocking operation.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_composite_recovery_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_composite_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_public_torsion_interpolation.py`
- `research/red_team_balanced_kani_composite_recovery.md`

## Round 8: Non-One Square Auxiliary

Date: 2026-07-14

Status: `OBSERVATION / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND`

This round removes the specific `x=1`, `N=d+1` shape without claiming a
general sums-of-squares backend. The public fixture reuses the degree-7 ascent
over `F_43` but takes

```text
d=7, N=16, x=3,  N=d+x^2, gcd(x,N)=1.
```

Here `x=3` is non-one but is a unit modulo `16`. The graph generators are
`([x]P0,gamma(P1))` and `([x]pi(P0),pi(gamma(P1)))`. For a norm-conic branch,
their product pairing is `zeta^(x^2+d)=zeta^N=1`. A primitive source
projection pairing of order `16` certifies that the rank-two subgroup has order
`16^2`; target projection pairings also have order `16`.

### Exact evidence

Across seeds `20260714..20260716`:

- the torsion extension degree is `24` and the full-Frobenius pairings have
  order `16`;
- all `24` norm-conic graph kernels are full-rank and isotropic;
- theta and public interpolation accept the same `6` branches and reject the
  other `18`;
- all accepted interpolation systems have `129 x 15` shape, rank `14`,
  one-dimensional kernel, degree profile `7/6`, base-field descent, and one
  torsion-compatible scaling;
- all `232` actions outside the norm conic fail product isotropy in every seed;
- `64` deterministic `GL_2(Z/16)` transforms per seed give `384` valid accepts
  and zero invalid accepts;
- the first seed covers all `1536` modulo-8 reduction classes and `256`
  high-bit lifts, giving `9216+1536` valid accepts and zero invalid accepts;
- wrong auxiliary `x=1` rejects before theta, and the same-trace conductor-7
  endpoint `j=3` rejects at public constructor admission;
- construction oracle calls remain zero and the post-hoc verifier covers the
  six target automorphisms exactly once.

The final run takes `183.85 s`, peaks at `349.140625 MiB`, and pins the same
current script/helper hashes as the degree-7 and composite regressions.

### Scoped negative result

The all-residue sweep falsifies theta-only integer-lift identification. Exactly
`{3,5,11,13}` satisfy `x^2=9 mod 16`. Residues `{3,13}` select the six public
degree-7 interpolation branches, while `{5,11}` theta-split to a disjoint six
with empty interpolation intersection. Only nonnegative integer `x=3` satisfies
`16=7+x^2`.

Thus integer provenance is public parameter metadata, rank/isotropy are
admission invariants, and branch correctness comes from endpoint splitting
plus public interpolation. The initial stronger sweep expectation is preserved
as `iso_balanced_kani_non_one_auxiliary_residue_sweep_pilot_result.json` with
`success=false`; it was not overwritten.

### Red Team disposition

The independent Red Team closes the all-residue/all-branch and non-conic
controls for this fixture. Projection certificates, wrong-auxiliary evidence,
and verifier isolation are narrowed but remain model-bound. Admitted wrong
targets, exhaustive `GL_2(Z/16)`, process-level construction/verifier
separation, and another `N-d=x^2` family remain open.

### Handoff: Common-basis mixed CRT recovery

### Claim or task
Combine a theta-filtered `N1=16` action with an odd `n2=5` conic action through
one compatible `M=80` torsion basis, then interpolate only the CRT survivors.

### Status
HYPOTHESIS

### Assumptions
- ordinary `F_43` toy fixture with public Frobenius orientation;
- the dimension-two vendor remains the local 2-primary split gate;
- exact public interpolation is the global CRT discriminator;
- no ECDLP, asymptotic, deployment, or canonical theta-map claim.

### Evidence so far
- `ord_pi(16)=24`, `ord_pi(5)=8`, and `ord_pi(80)=24`;
- the local conics have `24` and `6` branches, while the direct modulus-80
  conic has `144`;
- the existing theta gate retains `6` modulo-16 branches, so CRT produces only
  `6*6=36` interpolation candidates, a fourfold branch-count reduction;
- the vendored backend is dimension-two and lacks the 16-coordinate theta
  structures required for a direct dimension-four `a^2+b^2` construction.

### Failure modes
- independently sampled local bases may not be CRT-compatible;
- eager `M=80` interpolation may dominate memory and wall time;
- the `j=0` six-automorphism orbit may hide a family-specific coincidence;
- partial local filtering may not survive a generic target replication.

### Next concrete action
Implement `iso_balanced_kani_mixed_crt_recovery.sage.py` with a common
`E[80]` basis, reductions to `16` and `5`, `36` CRT candidates, and the direct
`144`-branch interpolation baseline.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_nonunit_auxiliary_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_non_one_auxiliary_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_non_one_auxiliary_residue_sweep_pilot_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_recovery.sage.py`
- `research/red_team_balanced_kani_nonunit_auxiliary.md`

## Round 9: Common-Basis Mixed CRT Pruning

Date: 2026-07-14

Status: `OBSERVATION / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND`

This round implements the mixed-torsion fallback required because the vendored
theta backend is dimension two. One public Frobenius generator on `E[80]` is
reduced by `[5]` to `E[16]` and by `[16]` to `E[5]`. The local modulo-16 theta
gate and modulo-5 norm conic therefore act on compatible reductions of one
global basis rather than independently sampled torsion bases.

### Exact evidence

Across seeds `20260714..20260716`:

- Frobenius extension degrees are `u16=24`, `u5=8`, and `u80=24`;
- the modulo-16, modulo-5, and modulo-80 conics have `24`, `6`, and `144`
  branches;
- theta retains six modulo-16 branches and coefficientwise CRT creates 36
  distinct modulo-80 actions, all contained in the full conic;
- public interpolation accepts six CRT actions, rejects 30, and the modulo-5
  below-threshold control accepts no unique map;
- seed one directly interpolates all 144 branches, accepts the identical six
  coefficients and maps, and rejects the other 138;
- theta makes 144 constructor calls in `0.49..0.52 s` per seed;
- five GL2/shear, swap, Frobenius-orientation, and wrong-target-basis mutations
  fail the exact common-reduction validator while retaining full point and
  pairing orders in the recorded controls;
- direct Sage path/rational-map sentinels self-test twice and record zero
  construction calls; a restricted lexical audit pins 25 public/vendor files;
- construction serializes a canonical payload before a separate verifier
  process; valid payloads cover the six secret-map orbit elements exactly once,
  while tampered payloads reject before secret evaluation with zero secret
  calls.

The formal run is timestamped from `2026-07-14T00:05:23.501219Z` through
`2026-07-14T00:16:50.068563Z` (`PDT` locally), takes `686.60 s`, peaks at
`441.9375 MiB`, and pins script, verifier, interpolation-helper, vendor, and
per-seed payload hashes. The old one-seed direct pilot and the accepted
pre-timestamp formal run are retained as provenance; neither is the
authoritative artifact.

### Scoped negative result

Fourfold complete-orbit pruning is not automatically a universal first-hit
speedup. On seed one, CRT versus direct first-hit counts are `4 vs 24`
(canonical), `2 vs 24` (reverse), and `31 vs 139` (all rejections first). Across
32 deterministic shuffled orders, the medians are `4 vs 14.5`. Yet the direct
best case takes about `4.94 s`, slightly below CRT's `5.59 s` after its theta
preprocessing. The validated claim is safe branch pruning and a typical-order
first-hit benefit on this fixture, not an ordering-independent recovery win.

### Handoff: Generic-target mixed CRT replication

### Claim or task
Test whether common-basis mixed CRT pruning survives without the six-element
`j=0` target automorphism orbit and under a second coprime odd modulus.

### Status
OPEN

### Assumptions
- ordinary toy ascents with effective public Frobenius orientation;
- the power-of-two factor remains a dimension-two theta split gate;
- exact public interpolation remains the final map discriminator;
- process isolation and runtime sentinels are restricted-model evidence.

### Evidence so far
- the `F_43`, degree-7 fixture preserves all six valid maps under `144 -> 36`
  complete-orbit pruning;
- direct and CRT accepted serialized maps agree exactly;
- first-hit improvements depend on branch ordering;
- a generic target was already validated for the pure power-of-two composite
  gate, but not for this mixed-CRT construction.

### Failure modes
- the `j=0` orbit may create unusually symmetric accepted residue classes;
- another odd modulus may increase extension degree enough to erase pruning;
- first-hit distributions may not improve after theta overhead;
- exact interpolation remains non-scalable in `d`.

### Next concrete action
Search the existing ordinary fixture catalogue for a generic-automorphism
ascending pair admitting `N1=d+x^2` and a small coprime odd torsion factor, then
prelog and run the same complete-orbit and first-hit contract.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_verifier.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_result.json`
- `research/red_team_balanced_kani_mixed_crt.md`

## Round 10: Generic-Target Mixed CRT Replication

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

The common-basis construction now passes on a generic target. Over `F_137`,
the source `[120,70]` has `j=83`, discriminant `-539`, and conductor `7`; the
target `[45,18]` has `j=112`, discriminant `-11`, conductor `1`, and exactly
two automorphisms. Sage endomorphism-order checks, cross-evaluation of the two
ring-class polynomials, and `Phi_7(83,112)=0` independently certify the
degree-7 vertical edge.

For `N1=16`, `n2=5`, and `M=80`, the Frobenius torsion degrees are `12/4/12`
and the conic branch counts are `24/4/96`. Across seeds
`20260714..20260716`, theta retains two local branches, CRT creates eight
global branches, and public interpolation accepts exactly two. Seed one's
direct all-96 baseline accepts the identical serialized coefficient/map set.
The complete-orbit candidate ratio is `12x`; measured interpolation is
`131.40 s` direct versus `14.13 s` after pruning.

All five basis mutations, the below-threshold odd-only control, runtime oracle
sentinels, 25-file source audit, separate hashed-payload verifier, and
tamper-before-secret control pass. Each verifier classifies the two accepted
maps as the target-automorphism orbit exactly once.

The performance boundary remains explicit. Fixed canonical, reverse, and
adversarial orderings plus the shuffled median strongly favor CRT, but direct
best-case is `3.105 s` versus CRT `3.300 s` including preprocessing. This is
safe complete-orbit pruning and an ordering-specific first-hit signal on a
second toy fixture, not a universal recovery speedup.

### Handoff: Second odd-modulus replication

### Claim or task
Test whether the generic-target mixed-CRT reduction is stable when the odd
torsion modulus changes while the degree-7 ascent and modulo-16 theta gate stay
fixed.

### Status
OPEN

### Assumptions
- ordinary toy ascent with effective public Frobenius orientation;
- one common full-torsion generator reduces exactly to both local bases;
- exact public interpolation remains the final map discriminator;
- direct-map APIs remain unavailable to construction.

### Evidence so far
- two fixtures preserve their complete valid-map orbits under local theta plus
  CRT pruning;
- the generic fixture removes the special six-automorphism target;
- the odd factor `5` has only been tested once on each fixture;
- full-orbit gains do not imply an ordering-independent first-hit gain.

### Failure modes
- another odd modulus may raise the full torsion extension enough to erase the
  candidate reduction;
- local conic branches may combine less selectively;
- basis normalization may not survive a different cofactor;
- one fixed ascent does not establish a parameter family.

### Next concrete action
Prelog the `F_137` fixture with odd modulus `3`, derive `u3`, `u48`, and exact
conic counts, then run the same three-seed CRT/direct accepted-set contract.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_generic_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_generic_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_generic_verifier.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_generic_result.json`
- `research/red_team_balanced_kani_mixed_crt_generic.md`

## Round 11: Odd-Modulus-3 Replication

Date: 2026-07-14

Status: `OBSERVATION / NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND`

The second odd-modulus contract passes on the generic `F_137` degree-7 ascent.
For `N1=16`, `n2=3`, and `M=48`, the prelogged Frobenius extension degrees are
`12/2/12` and the conic branch counts are `24/2/48`. Across seeds
`20260714..20260716`, theta retains two local branches, CRT creates four global
branches, and interpolation accepts exactly two. Seed one's direct all-48
baseline accepts the identical serialized maps and rejects 46.

The candidate ratio is `12x`, while measured complete-orbit interpolation is
`27.02 s` direct versus `2.98 s` after pruning (`9.07x`). Canonical, reverse,
adversarial, and shuffled-median first-hit counts favor CRT. Direct absolute
best case is still slightly faster (`1.157 s` versus `1.281 s` including theta),
so the ordering-independent speed claim remains rejected.

Two preflight failures are preserved as `ISO-AR-NR-013`: the copied modulo-5
harness retained `u5=4` and hardcoded odd basis order `5`. Both failed before
conic construction. The final port derives the odd point/pairing orders from
`n2=3`; exact cofactor identities and primitivity gates then pass, and all five
mutations still reject.

Endpoint/ring-class/`Phi_7`, runtime sentinel, 25-source audit, separate hashed
verifier, orbit coverage, and tamper-before-secret controls pass. This removes
dependence on odd modulus `5` for one toy ascent, not dependence on the
endpoint, favorable `u3=2`, exact interpolation, or class-number-one crater.

### Handoff: Independent endpoint and torsion-cost stress

### Claim or task
Test mixed-CRT orbit preservation on an independent generic endpoint with a
larger crater or an odd torsion factor whose Frobenius extension is not
exceptionally small.

### Status
OPEN

### Assumptions
- ordinary toy ascending edge with effective public Frobenius orientation;
- a common full-torsion basis supports exact local reductions;
- dimension-two theta remains the power-of-two local gate;
- exact public interpolation remains the final map discriminator.

### Evidence so far
- `n2=5` and `n2=3` preserve the complete two-map orbit on the generic
  `F_137` endpoint;
- the special `F_43`, `j=0` fixture also preserves its six-map orbit;
- both generic odd choices yield `12x` complete-orbit candidate pruning;
- the modulo-3 torsion degree `u3=2` is unusually favorable.

### Failure modes
- a larger crater may require endpoint guessing that dominates local pruning;
- an inert or higher-order odd factor may make basis generation dominant;
- a different endpoint may have theta survivors that do not prune;
- exact interpolation remains non-scalable in degree.

### Next concrete action
Search/prelog a second generic degree-7 or composite ascent whose target class
number exceeds one or whose small odd torsion order is near the worst case;
require complete direct/CRT accepted-set equality on the first seed.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_verifier.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_preflight_failure.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_mod3_basis_preflight_failure.json`
- `research/red_team_balanced_kani_mixed_crt_mod3.md`

## Round 12: Class-Number-Two Generic Target

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

The mixed-CRT construction now passes on an independent ordinary ascent with a
nontrivial crater. Over `F_431`, source `[359,383]` has `j=304`, discriminant
`-1715`, and conductor `7`; target `[70,86]` has `j=57`, discriminant `-35`,
conductor `1`, class number `2`, and two automorphisms. Ring-class
cross-evaluation, `Phi_7`, and the unique ascending degree-7 edge certify the
endpoint.

For `N1=16`, `n2=3`, and `M=48`, Frobenius orders are `24/2/24`. The actual
pairing-derived norm values vary between seeds, while all-unit conic counts stay
`24/2/48`. Across seeds `20260717..20260719`, theta retains two branches, CRT
creates four, and public interpolation accepts exactly two. Seed one's direct
all-48 baseline accepts the identical serialized maps.

Complete-orbit pruning is `12x`; interpolation time is `41.68 s` direct versus
`5.00 s` filtered (`8.33x`). Canonical, reverse, adversarial, and shuffled
first-hit counts favor CRT, while direct best case remains lower after theta
overhead. All endpoint, five basis-mutation, runtime-sentinel, source-audit,
hashed-verifier, orbit, and tamper controls pass.

The narrow positive result is removal of class-number-one dependence for one
directly-above toy edge. It does not include finding the correct crater endpoint
among two classes. The next algorithmic obligation is therefore to charge that
selection cost rather than treating the endpoint as already known.

### Handoff: Charge crater endpoint selection

### Claim or task
Integrate class-number-two crater candidate selection with vertical mixed-CRT
recovery and measure total work against direct per-candidate recovery.

### Status
OPEN

### Assumptions
- ordinary toy isogeny class with effective public Frobenius orientation;
- both crater candidates can be enumerated from public ring-class data;
- the directly-above vertical degree remains known;
- exact interpolation is retained as verifier-backed map extraction.

### Evidence so far
- the correct directly-above endpoint admits `48 -> 4 -> 2` safe pruning;
- the target crater contains two classes rather than one;
- local/global torsion field degree is `24`, twice the prior generic fixture;
- direct and CRT accepted sets agree exactly on the contracted seed.

### Failure modes
- running recovery on both crater candidates may erase the local timing gain;
- the wrong crater endpoint may produce ambiguous or costly interpolation;
- class-number-two behavior does not predict larger crater scaling;
- crater walk and endpoint enumeration costs are not yet instrumented.

### Next concrete action
Prelog both roots of `H_-35` over `F_431`, run the public recovery pipeline
against each candidate without secret path access, and charge endpoint
enumeration plus both attempts before declaring the correct vertical map.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_class_number_two_candidate_certificate.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_class_number_two_candidate_certificate_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_class_number_two_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_class_number_two_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_class_number_two_verifier.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_mixed_crt_class_number_two_result.json`
- `research/red_team_balanced_kani_mixed_crt_class_number_two.md`

## Round 13: Role-Blind Charged Crater Queue

Date: 2026-07-14

Status: `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`

The class-number-two endpoint is no longer supplied as a construction oracle.
Each replication enumerates both roots of `H_-35`, freezes the public attempt
order `[274,57]`, and runs the same mixed-CRT construction against both models
with the same literal seed. Roles and expected survivor/map counts were removed
from construction parameters and serialized payloads after the initial Red
Team review. The queue hashes a public selection manifest before invoking any
secret verifier.

Across seeds `20260720..20260722`, the wrong-first `j=274` target has no theta
survivor and no map, while `j=57` retains `2` theta branches, creates `4` CRT
branches, and reconstructs the complete two-map automorphism orbit. Direct
all-48 interpolation on both targets and all seeds accepts the identical sets.
The charged queue therefore reduces `96` direct branches to `4` filtered
branches; direct interpolation versus theta-plus-CRT time is lower by
`12.30x..12.69x` on this fixture.

This is a real endpoint-selection component for one two-root toy crater, not a
blind large-crater algorithm or scaling result. The public roots and curve
models are still a bounded fixture, exact interpolation is degree-7 only,
construction isolation is a lexical audit plus five runtime sentinels, and the
wall-clock run overlapped the separate `n2=11` feasibility worker.

The initial role-blind artifact was not sufficiently isolated:
`endomorphism_order()` transitively evaluated the degree-7 modular polynomial.
The final construction removes that call and blocks/self-tests five direct and
transitive APIs; exact endomorphism labels and the `0/237` `Phi_7` values are
computed only by the selected-candidate verifier. The transitive leak remains
preserved as `ISO-AR-NR-015`, not erased by the corrected run.

### Handoff: stress torsion field or crater size

### Claim or task
Decide whether the next recovery stress should increase odd torsion cost to
`n2=11` or increase the number of crater candidates, without weakening the
role-blind manifest and all-seed direct-set controls.

### Status
OPEN

### Assumptions
- ordinary toy curves with effective public Frobenius orientation;
- public ring-class enumeration supplies candidate crater models;
- theta filtering remains the modulo-16 local gate;
- exact public interpolation remains the final map extractor.

### Evidence so far
- a dynamically enumerated two-root crater is processed and charged end to end;
- the wrong root rejects at theta before interpolation on all three seeds;
- the correct root preserves the complete direct map orbit;
- public selection is hashed before separate secret verification.

### Failure modes
- a larger crater may contain wrong candidates with nonempty theta/CRT branches;
- `u176=120` may make basis construction dominate all pruning;
- current wall-clock ratios were measured under concurrent load;
- exact interpolation and parent-only RSS remain non-scalable boundaries.

### Next concrete action
Complete the prelogged `n2=11` feasibility run; launch full `M=176` recovery
only if exact order, conic, wall-time, memory, mutation, and source-audit gates
all pass, otherwise move directly to a second crater family.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_contract.md`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_recovery.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_verifier.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_pre_enumeration_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_post_selection_preflight_failure.json`
- `research/red_team_balanced_kani_crater_queue.md`

## Round 14: Theta-Only, Certified Helper, And n2=11 Boundary

Date: 2026-07-14

Status: `OBSERVATION / NEGATIVE RESULT / HYPOTHESIS / TOY-EVIDENCE / MODEL-BOUND`

### Claim, Scoped Carefully

The completed Round14 work strengthens the local ascending-isogeny recovery
component on the fixed `F_431` class-number-two toy fixture, but it does not
produce a Pollard-rho comparison, ECDLP break, deployment claim, or
parameter-family theorem. The strongest positive claim is that theta-only
`N1=16` filtering preserves the same canonical degree-7 maps as the Round13
direct/CRT queue while the certified minimal-row helper reproduces the
unchanged interpolation helper for the fixed degree-7/6 x-coordinate ansatz.

The next active recovery experiment is a separately contracted `N=8`
minimal-modulus test. The `n2=11,M=176` branch is preflight-feasible but remains
lower priority on this fixture because it only projects `20` inherited
filtered candidates, while theta-only `N1=16` already leaves exactly `2`.

### Evidence Summary

- `ISO-AR-POS-014` (`OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`): certified
  minimal-row interpolation is accepted for the fixed direct-helper ansatz only.
  Result SHA-256:
  `98047221fd87211bdadd3e4ad198574ffbcdaf521c3b66dfe80201d0206721b1`.
  Helper, harness, and current contract hashes:
  `4127c2306588045ea0eac3484262056f1c3e07dc950741aec2cc59dcdc7c9600`,
  `7d29800c1ea325f4cf01e3f8445fe65a7238cc6354f3c5992c3a1b5c0ad847bf`,
  `5d9f26a83f574d47f52669686467a1e18b925aa9cc785dba0f875d736af21328`.
  Red Team accepted `23/23` assertions, `288/288` certificates, `44`
  certificate mutations, and six accepted-report replays of `2303/2303`
  nonzero torsion points.
- `ISO-AR-POS-015` (`OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`): theta-only
  `N1=16` result SHA-256:
  `3f761d3d11c515e4d4e4d7b14990d0707aa8e609ac55a72c1c126116ecc41773`.
  Harness and contract hashes:
  `93f77694b0232aadaf4addb69f253d3ef0bf31622111423242b79c1df0e1f0fe`,
  `0572173374e91f422912563491110d556569c58ec1f16441e59807fecf1433e1`.
  All three seeds charge both targets, select only `j=57`, and produce
  `48` direct candidates, `2` theta candidates, and `2` accepted maps. Accepted
  direct/theta reports have exact `255/129/1` coverage, actual reversed
  execution passes, and all six frozen-bundle mutations reject.
- `ISO-AR-POS-016` (`OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`): `n2=11,M=176`
  is public-preflight feasible only. Result SHA-256:
  `4c86944f34af164d94a8d5262fe41e218111d17a5baae7168ca7ae7c61f03282`.
  Harness and contract hashes:
  `5877703e454ac77fe97dec0a937975238f2d48c94d1b55907e64c2d59f1320ed`,
  `7adf98ad47acb011864cdef18e1c4212bee0cdcbbe6de4ea23b01a69954109de`.
  It measures `u16/u11/u176 = 24/10/120`, conics `24/10/240`, max child RSS
  `266.828125 MiB`, max worker wall `3.76651875 s`, and projected filtered
  candidates `20`; it runs no theta split, interpolation, recovery, verifier,
  target descent, or ECDLP baseline.

### Assumptions And Limitations

All accepted evidence is restricted to one toy ordinary fixture: source
`j=304`, crater roots `[57,274]`, target `j=57`, degree `7`, and the audited
source/result hashes above. Lexical audits and monkeypatch sentinels are
restricted-model controls, not semantic noninterference proofs. Canonical map
equality means exact helper serialization in the fixed public Weierstrass
models. Verifier-orbit coverage is post-hoc from the hash-stable Round13
artifact and is not a secret-free public verifier rerun.

### Baseline Comparison

The baseline is direct all-branch interpolation and exact accepted-set equality.
Certified interpolation matches the unchanged direct helper on the Round13
`M=48` branches while avoiding the full `1153 x 15` row matrix under the fixed
ansatz. Theta-only `N1=16` matches Round13 canonical map bodies with
`48 -> 2` candidate filtering on the selected target. The `n2=11` result is
not comparable because it never enters recovery.

### What Failed Or Worked

`ISO-AR-NR-016` (`NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND`): strict
cross-run raw `(a,b)` branch-coordinate equality failed and remains preserved
as
`iso_balanced_kani_theta_only_raw_branch_coefficient_mismatch_result.json`,
SHA-256
`7e914f5e1440fae045a63d274576f775ead87c7f883faebbb771a09481253c28`.
The failure is scoped: those coefficients are basis-relative across runs. The
canonical maps are equal, and within-run direct/theta branch equality remains
mandatory where the sampled basis is shared.

The self-correction is now explicit: the earlier strict cross-basis label gate
was too strong; the replacement gate is canonical map-body equality plus
post-hoc Round13 orbit coverage, with raw labels retained as diagnostics.

### New Hypotheses Generated

- Conservative: `N=8` minimal modulus may preserve the same canonical accepted
  maps without the odd CRT branch or `N1=16` overhead.
- Representation change: an explicit `GL_2(Z/16Z)` basis-transition or
  canonical generator certificate should explain the raw label mismatch and
  make branch coordinates portable across artifacts.
- High-risk: a ramified `n2=5` cyclic quotient degree-35 route may expose a
  different quotient construction whose bottleneck is not raw basis-relative
  label instability.

### Concrete Next Steps

1. Execute the separately contracted `N=8` minimal-modulus experiment first.
2. Add a `GL_2(Z/16Z)` basis-transition/canonical-generator certificate before
   any future cross-run branch-label gate.
3. Keep the `n2=11` one-filtered `M=176` pilot as justified by Red Team but
   lower priority here; if run, require its own filter manifest, direct
   baseline, interpolation/rank counters, and verifier isolation.
4. Do not claim Pollard-rho, ECDLP, deployment, or asymptotic progress from
   any Round14 artifact.

### Handoff: N8 minimal modulus

### Claim or task
Test whether `N=8` is already sufficient to preserve the accepted canonical
degree-7 maps on the fixed `F_431` class-number-two fixture.

### Status
OPEN

### Assumptions
- the fixture remains source `j=304`, crater roots `[57,274]`, target `j=57`,
  and degree `7`;
- exact serialized map equality is the cross-run invariant;
- raw branch labels are basis-relative until a basis-transition certificate is
  emitted;
- no direct Sage isogeny, rational-map oracle, or Round13 verifier data is
  available before the public manifest freezes.

### Evidence so far
- theta-only `N1=16` reduces the selected target from `48` direct branches to
  `2` theta candidates without losing either canonical map;
- certified fixed-ansatz interpolation matches the unchanged helper;
- `n2=11,M=176` is preflight-only feasible and does not measure recovery.

### Failure modes
- `N=8` may not preserve both accepted maps or may weaken coverage;
- the result may stay same-fixture only;
- without a `GL_2(Z/16Z)` certificate, branch labels remain nonportable;
- exact interpolation may stay the dominant map-extraction bottleneck.

### Next concrete action
Run the separate `N=8` minimal-modulus contract and promote only if the exact
accepted canonical map set, coverage checks, reverse execution, and mutation
controls all pass.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_certified_minimal_sample_interpolation_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_theta_only_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_theta_only_raw_branch_coefficient_mismatch_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_n2_11_feasibility_result.json`
- `research/red_team_certified_minimal_sample_interpolation.md`
- `research/red_team_balanced_kani_theta_only.md`
- `research/red_team_balanced_kani_n2_11_feasibility.md`

## Round 15: N8 Minimal Modulus Accepted

The final N8 gate is accepted as `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`
with no P0/P1 finding. Result/harness/contract SHA-256 are
`b7e007ed9414aea05f0e0a24b10c59c8ce95a9755fd7d5c99e707851b519e51a`,
`94a6911db76dded5a9c4e7c2f47f086cf1314e4c4bb6826c6672514a5eb33695`,
and `4f18c75c2b9f2a351fcec8f087224e2b435fa54ae5c4cb16c28c4cc9b0f36ed2`.
For every seed and each target there are `12` conic branches; aggregate work is
`24` direct -> `2` theta candidates -> `2` accepted maps, selecting only
`j=57`. Exact accepted coverage is `63/33/1`. Six mutations, reversed
`[57,274]` execution, five sentinel selftests with `0` construction calls,
all `27` stable source paths, and exact canonical equality with N16 and
Round13 all pass.

The boundary remains strict: N8 sufficiency is observed only on this fixed
fixture and is not a family theorem, asymptotic result, deployment claim,
Pollard-rho improvement, or ECDLP breakthrough. The `n2=11,M=176`
one-filtered recovery pilot is deferred on this fixture because it projects
`20` filtered candidates and `u176=120`, versus `2` candidates and `u8=12`
for N8. This is a scheduler priority decision, not a negative result for
`n2=11` generally.

## Handoff: Certify independent Frobenius bases

### Claim or task
Explain the Round13/N16/N8 raw branch-label differences with an explicit
public `GL_2(Z/16Z)` basis-transition and canonical-generator certificate.

### Status
OPEN

### Assumptions
- canonical serialized map bodies are the cross-artifact invariant;
- raw `(a,b)` labels are coordinates in independently sampled torsion bases;
- certificate inputs and normalization rules must be public and prelogged.

### Evidence so far
- N8 preserves both canonical accepted maps of N16 and Round13 on three seeds;
- N8 passes exact `63/33/1` action coverage, reversal, mutation, sentinel, and
  source-stability controls;
- raw cross-basis labels differ while canonical maps remain equal.

### Failure modes
- generator normalization may remain ambiguous under public scan order;
- a valid transition may be fixture-specific;
- transition generation or verification may cost more than it saves.

### Next concrete action
Produce a prelogged public `GL_2(Z/16Z)` certificate that emits and verifies
the Round13-to-N16-to-N8 basis transitions, generator normalization,
Frobenius-action transport, and canonical-map preservation before selecting a
second curve family or the `n2=5` cyclic quotient route.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_balanced_kani_n8_minimal_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_theta_only_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_crater_queue_result.json`
- `research/red_team_balanced_kani_n8_minimal.md`

## Round 16: Public Basis-Transition Accepted

Claim, scoped carefully: `ISO-AR-015` is accepted as `OBSERVATION /
TOY-EVIDENCE / MODEL-BOUND` on the fixed public `F_431`, trace-`3`, degree-7
class-number-two fixture. Public `R/nR` unit basis transitions explain the
raw branch labels across Round13 `M=48`, theta-only `N=16`, and minimal `N=8`
artifacts while preserving the exact canonical map bodies.

Evidence summary: result/harness/contract SHA-256 are
`7a884d3b779c5bbf7e5a2b0823bd488e611a5ab9b6e09ba40fb6327db379ec99`,
`d3bf3e1f0d083d0701b40a890df33bf23a8253479aea75b1e32198758fb1e415`,
and `2bafd1e6f0cd807338ab096f858374fe8e273255e863ac4818d01c1997c93f83`.
The accepted audit records `3` seeds, `12` embeddings, `75` lanes, `150`
lane-side unit certificate records, `150` transports, and `30` reconstructed
module certificates. All controls, primary artifact hashes, and start/end
contract and harness source hashes pass.

Assumptions and limitations: this remains a hash-bound local Sage field-model
certificate. It is not new isogeny recovery, not `N=8` generality, not an
asymptotic result, not ECDLP evidence, not Pollard-rho evidence, and not
deployment evidence.

Baseline comparison: the baseline invariant remains canonical serialized map
equality plus independent direct/theta/CRT accepted-set checks. Round16 does
not compare against Pollard rho and does not claim a recovery-speed result.

What failed or worked: literal raw `(a,b)` equality failed and remains
preserved as `ISO-AR-NR-016`. What worked is the narrower replacement:
basis-relative public unit transport reconciles the raw labels while canonical
map bodies stay equal.

New hypotheses generated: the certificate may transfer to a second nontrivial
crater family if future artifacts export machine-parsable field and point
metadata instead of depending on display-string reconstruction.

Concrete next steps: prelog the second-family certificate with the same count,
control, hash, raw-mismatch, and canonical-transport requirements. Keep the
`F_137` minimal-N8 rerun likely pending the separate Round16 branch decision.

## Handoff: Second-family basis-transition certificate

### Claim or task
Run the accepted public basis-transition certificate shape on a second
nontrivial crater family with machine-parsable field and point metadata.

### Status
OPEN

### Assumptions
- Round16 is fixed-fixture `OBSERVATION / TOY-EVIDENCE / MODEL-BOUND`;
- canonical map-body equality remains the cross-artifact invariant;
- raw labels must be transported by explicit public unit certificates before
  they can be compared across independently sampled bases.

### Evidence so far
- `3` seeds, `12` embeddings, `75` lanes, `150` lane-side unit certificate
  records, `150` transports, and `30` module certificates all pass.
- All controls and source hashes pass.
- The preserved raw mismatch is explained as basis-relative label transport,
  not as a new map or an isogeny-recovery result.

### Failure modes
- a second family may have multiple valid unit witnesses per lane;
- machine-parsable metadata may expose nonportable local field assumptions;
- the `F_137` minimal-N8 rerun may need a separate Round16 branch decision
  before it can serve as the next certificate family.

### Next concrete action
Write the second-family contract with explicit field defining polynomials,
coefficient arrays, source/target point metadata, and the Round16 count and
control requirements, then run the same public unit-transport verifier.

### Artifact paths
- `experiments/ecdlp_isogeny/iso_public_basis_transition_result.json`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_contract.md`
- `experiments/ecdlp_isogeny/iso_public_basis_transition_certificate.sage.py`
- `research/red_team_public_basis_transition_prelaunch.md`
- `research/red_team_public_basis_transition_result.md`
