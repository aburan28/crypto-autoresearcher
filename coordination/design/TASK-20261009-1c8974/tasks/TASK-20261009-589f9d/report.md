# Frobenius and exceptional-automorphism sampler assessment

Task: `TASK-20261009-589f9d`  
Batch: `BATCH-12e6aa`  
Date: 2026-10-09  
Disposition: two scoped typed obstructions; no contract-passing sampler established

## Result

Both families have valid algebra after a connecting map is supplied, but neither
currently instantiates `Samp` on the frozen bare-curve law.

For F1, a separable

```text
phi : E -> E^(p)
```

would give the non-scalar endomorphism

```text
alpha = Frob_p o phi : E -> E^(p) -> E.
```

Its inseparable degree is `p`, so `INSEP_NOT_SQUARE` is a public certificate.
The missing step is not Frobenius evaluation; it is a public polynomial
construction of `phi` from the bare endpoint. The frozen sources give the
typing conditional on a supplied `phi`, not such a constructor. On the public
conjugation-isomorphism easy locus, `Canon(E^(p))=E` supplies an isomorphism and
the construction is deterministic, but the frozen packet gives no `D_ER` mass
bound for that locus.

For F2, the direct automorphisms at `j=0` and `j=1728` are valid deterministic
positive controls. Their good-set mass is exactly the exceptional-locus mass
under `D_ER`, which is unproved. The fact that there are two exceptional
geometric classes is not itself a probability bound for this walk endpoint
law. Transport to a general endpoint would require a public separable path

```text
phi : E -> X,             j(X) in {0,1728},
```

and then

```text
alpha = dual(phi) o u o phi : E -> E.
```

No such public polynomial path constructor is supplied. This is the earliest
failure of the intended transported route.

These are scoped route failures, not hardness results or universal
impossibility statements.

## Requirement-to-evidence status

| Requirement | Evidence and status |
| --- | --- |
| Exact `D_ER` / `DER-ENDO-v1` contract | Verified against the frozen `distribution-contract.yaml`; source-packet and receipt hashes match. |
| F1 source/target typing | Complete conditionally on a supplied separable `phi`; deterministic easy-locus candidate fully typed. |
| F2 source/target typing | Direct exceptional and conditional transported routes fully typed. |
| Public-only construction | F1 easy-locus and F2 direct core use only public data; both general connecting-map constructors are missing. |
| Exact byte and semantic law | Exact point-mass laws given for both public cores; exact pushforward formulas given for general routes, but their pathfinder laws are not instantiated. |
| Public non-scalarity | F1 uses `INSEP_NOT_SQUARE`; F2 direct uses `DEGREE_ONE_NOT_PM_ONE`; F2 transport uses `NONZERO_DISCRIMINANT`. |
| `q`, `nu`, retry and cost | Both cores have `q=1` on their good sets and deterministic one-attempt behavior. Their required `nu=1-mu` is not known negligible. Complete explicit polynomial `T/M` bounds are missing. General routes lack `q`, `nu`, law and path cost. |
| Support/enumeration | Both cores have a publicly enumerable singleton output per successful `E`, hence conditional min-entropy zero. General-route support is unresolved. |
| Frozen controls | All nine controls are addressed below and in `family-a.yaml`. |
| Earliest failed arrow | Intended F1: `P1`; F1 public core: `P4`. Intended F2 transport: `P1`; F2 direct core: `P4`. |
| Runs | Zero scientific, implementation, experiment, formalizer, benchmark, or parameter-selection runs. |

## Frozen contract used

The challenge is only `(Pi_lambda,E)`, with `E` drawn from the exact
nonbacktracking endpoint law `D_ER`. The endpoint walk, kernels, maps,
orientation, ideals, tags, torsion information, incoming-edge marker and ring
witnesses are erased. A candidate must return `0x00` or a canonical
`DER-ENDO-v1` byte string and must establish

```text
Pr_E[ Pr_rho[valid(E,Samp(Pi,E;rho))] >= 1/q(lambda) ]
  >= 1 - nu(lambda).
```

The outer bad-instance mass and the inner coin failure are separate. Retrying
uses independent coins on the same `E`; it cannot resample or condition the
endpoint. Canonical syntax fixes bytes for a syntax tree, not uniqueness of a
semantic endomorphism.

The relied-on frozen source packet records the following source boundaries:

- `WESOLOWSKI26-FROZEN` supports the relative-Frobenius type and its
  non-scalarity once a separable `E -> E^(p)` map is supplied.
- `PW24-VOR` supports efficient representations, the two exceptional classes,
  dual identities, and `EndRing <= OneEnd_Lambda` under its exact oracle
  conditions.
- `DEFEO17-ALGEBRA` supports the Frobenius codomain, supplied-kernel quotient
  maps, duals and composition.

None supplies a public constructor for either connecting map in this report,
or a mass bound for either easy locus.

## F1 — relative Frobenius

### Intended route and its missing arrow

Given a valid separable descriptor

```text
phi       : E       -> E^(p),       deg(phi)=d, gcd(d,p)=1,
F_Ep,p    : E^(p)   -> E,           deg(F_Ep,p)=p,
alpha     : E       -> E,           alpha=F_Ep,p o phi,
```

the resulting total degree is `p*d` and the inseparable degree is exactly `p`.
The `DER-ENDO-v1` DAG appends a `REL_FROB_P` node to the typed `phi` nodes and
uses a `COMPOSE` root with Frobenius after `phi`. The root source and target are
both the supplied `E`. Since scalar multiplication has square inseparable
degree and prime `p` is not a square, `INSEP_NOT_SQUARE` proves non-scalarity.

The family is incomplete at `P1`. A procedure

```text
FindConjugate(Pi_lambda,E;rho_phi) -> phi:E->E^(p)
```

has not been supplied or sourced. A raw coordinatewise `p`-power map is not a
substitute: it is inseparable, and using it in both legs produces the rejected
central `p^2`-Frobenius slice. The erased endpoint path, orientation, an ideal,
torsion labels or a basis are also forbidden substitutes. Calling this missing
constructor a hard problem here would exceed the evidence; the precise result
is that it is the unsupplied public path in this family.

If a pathfinder law `K1_E` were later frozen, its exact byte law would be its
pushforward through the deterministic F1 encoder. Its semantic law would sum
the probabilities of every syntactically distinct `phi` for which
`F_Ep,p o phi` is the same endomorphism. At present `K1_E`, its coin length,
success and cost are absent, so this is an obligation rather than a sampler.

### Exact public core

There is an exact restricted candidate. Form `E^(p)` coefficientwise and run
public `Canon`. When it returns target bytes equal to `E` and an encodable
isomorphism

```text
c : E^(p) -> E,
```

set `phi=c^(-1)` and output

```text
alpha_1 = F_Ep,p o c^(-1) : E -> E.
```

The bytes contain, in order, the explicit inverse-isomorphism node, the
relative-Frobenius node, and the composition root. The declared total and
inseparable degrees are both `p`; the certificate is
`INSEP_NOT_SQUARE`.

Let `C1(E)` denote the public predicate that this construction and validation
succeed. With zero random coins, the exact conditional laws are

```text
bytes | E     = delta_Enc_F1core(Pi,E)  if C1(E), else delta_0x00,
semantic | E  = delta_alpha_1           if C1(E), else delta_FAIL.
```

Thus `q_1(lambda)=1` on `G1=C1`. If

```text
mu_1(lambda)=Pr_(E<-D_ER)[C1(E)],
```

then the exact required outer error is

```text
nu_1(lambda)=1-mu_1(lambda).
```

No frozen result proves this negligible. Retrying is immaterial: one attempt
succeeds on `C1`, and every same-curve attempt fails off `C1`. The non-FAIL
byte and semantic supports each have size one for a fixed successful `E`, so
they are publicly enumerable and have conditional min-entropy zero.

The degree bound can be `Lambda_1(n)=n` because `deg(alpha_1)=p`. Runtime is
the sum of coefficient conjugation, `Canon`, inverse-isomorphism encoding and
`A_eval`; memory is the corresponding workspace plus output. The packet does
not instantiate explicit polynomial `T(lambda)` and `M(lambda)` for those
algorithms. Together with the missing outer-mass bound, this makes `P4` the
core's earliest failed arrow.

## F2 — exceptional automorphisms

### Exact direct core

For `p>3`, the frozen algebra packet provides the two positive controls

```text
j=1728:  u_4(x,y)=(-x,i*y),       i^2=-1,
j=0:     u_3(x,y)=(zeta*x,y),     zeta^2+zeta+1=0.
```

They have orders four and three, respectively. On a public canonical model,
the construction converts to the corresponding short model, conjugates by the
public model isomorphism, and flattens the result back to one canonically
reduced `EXPLICIT_MAP` root `E -> E`. Flattening matters: the frozen
`DEGREE_ONE_NOT_PM_ONE` certificate is stated for an explicit degree-one root,
not merely an unexamined composition program. A canonical field-root choice
fixes the bytes.

Let `C2(E)` mean that `j(E)` is exceptional, the public root/model/map
construction completes, and `A_eval` accepts. With zero random coins,

```text
bytes | E     = delta_Enc_F2direct(Pi,E)  if C2(E), else delta_0x00,
semantic | E  = delta_u_E                 if C2(E), else delta_FAIL.
```

The descriptor declares total and inseparable degree one and proves that its
reduced coordinate functions differ from `+1` and `-1`. Hence every non-FAIL
output is publicly non-scalar.

Here `q_2direct=1` and

```text
mu_exc(lambda) = Pr_(E<-D_ER)[C2(E)],
nu_2direct(lambda) = 1-mu_exc(lambda).
```

The source packet gives no bound on `mu_exc`. In particular, it does not prove
either that exceptional mass is negligible or that its complement is
negligible. The direct sampler is not allowed to replace `D_ER` by a
distribution conditioned on `j=0` or `1728`. It has one enumerable non-FAIL
output on each successful endpoint and conditional min-entropy zero. Same-curve
retries cannot extend its support.

Its degree bound is `Lambda_2direct(n)=0`. Its full runtime includes computing
`j`, a short-model transformation, canonical root selection, flattening,
rational-map reduction and verification. The packet does not freeze an exact
polynomial-time canonical root routine or explicit `T/M` polynomials. The
missing mass and runtime bounds make `P4` the direct core's earliest failure.

### Transported route and its missing arrow

For a supplied separable path

```text
phi       : E -> X,       deg(phi)=d,
u         : X -> X,
dual(phi) : X -> E,
```

define

```text
alpha_2t = dual(phi) o u o phi : E -> E.
```

This has degree `d^2` and inseparable degree one. Degree alone therefore does
not prove non-scalarity. Instead, let `t_u=0` for `u_4` and `t_u=-1` for
`u_3`. The dual identities and the quadratic equation for `u` give

```text
alpha_2t^2 - [d*t_u] alpha_2t + [d^2] = 0,
Delta = d^2(t_u^2-4) != 0.
```

`NONZERO_DISCRIMINANT` with signed payload `d*t_u` is therefore the correct
public certificate. This also exercises the immediate-backtrack control: if
`u=[1]`, the composition is `[d]` and the discriminant is zero.

The family fails first at `P1` because it has no public polynomial

```text
FindExceptionalPath(Pi_lambda,E;rho_phi) -> (X,phi:E->X).
```

Knowing the two targets and their automorphisms does not find the path. The
erased challenge walk and all hidden orientation, ideal, tag and torsion data
remain unavailable.

For a later frozen path law `K2_E`, the exact byte law is its pushforward
through the normalized path/automorphism/dual-path encoder, while the semantic
law sums the probabilities of all distinct paths producing the same
`dual(phi) o u o phi`. Currently `K2_E`, `R`, `q`, `nu`, the path-degree bound,
`T`, `M`, retries and support enumeration are all missing. Their absence is
not evidence that no such constructor exists.

## Controls

| Frozen control | F1 outcome | F2 outcome |
| --- | --- | --- |
| Scalar `[a]` | Square inseparable degree; rejected by the F1 certificate. | Direct `+/-1` fails; transported scalar has zero discriminant. |
| Immediate `dual(phi) o phi` | Scalar control, not a relative-Frobenius candidate. | With identity middle map it is `[d]` and is rejected. |
| Central `p^2`-Frobenius | Arises if inseparable `Frob_p` is smuggled into the separable `phi` slot; rejected. | Not used; frozen verifier rejects it. |
| Lone `p`-Frobenius | Target is `E^(p)`, not `E`; F1 supplies an explicit return leg. | Not used; frozen verifier rejects it. |
| Exceptional positive control | Accepted by the verifier but not emitted by F1. | Exactly the direct `u_3/u_4` construction. |
| Leaked path/orientation/ideal/torsion/basis | Forbidden; cannot instantiate `FindConjugate`. | Forbidden; cannot instantiate `FindExceptionalPath`. |
| Conditioned easy locus | Core returns `FAIL` outside `C1`; `D_ER` is unchanged. | Direct core returns `FAIL` outside `C2`; `D_ER` is unchanged. |
| Enumerable proper witness family | F1 core is a singleton per successful `E`. | Direct exceptional family and its singleton output are enumerable. |
| Two programs, one semantic map | Byte law is recorded first; semantic probabilities aggregate collisions. | Same, especially for distinct transport paths. |

## Proof-search disposition

| Arrow | F1 | F2 |
| --- | --- | --- |
| `P0` law and grammar | Pass | Pass |
| `P1` public-only dependency | General route fails; core passes | Transport fails; direct core passes |
| `P2` typing and bytes | Conditional pass | Conditional pass |
| `P3` non-scalarity | Conditional pass | Conditional pass |
| `P4` law, cost, success and bad mass | Core lacks mass and explicit `T/M`; general route lacks all bounds | Direct core lacks mass and explicit `T/M`; transport lacks all bounds |
| `P5` `Samp -> OneEnd` | Local conditional pass for every accepted bounded output | Local conditional pass for every accepted bounded output |
| `P6` `OneEnd -> EndRing` | Not established | Not established |
| `P7` support/enumeration | Core enumerated; extension unresolved | Direct core enumerated; transport unresolved |
| `P8` method ceiling | Respected | Respected |

The family-level earliest failed arrow is `P1` in both cases. The narrower
public cores pass `P1`--`P3` and first fail at `P4`.

## OneEnd boundary

Any accepted descriptor above, after campaign framing is forgotten, is a
bounded OneEnd answer for that same curve, provided its declared degree bound
is met. This local implication does not turn either family into a sampler on
`1-negligible` `D_ER` mass.

It also does not automatically instantiate the `PW24-VOR` reduction. That
algorithm queries its bounded-OneEnd oracle on curves from its own internal
walks. The frozen `D_ER` statement gives neither every-query coverage nor a
distribution-preserving bridge. No EndRing reconstruction or break follows.

## Provenance and limits

The assessment uses only the frozen source/distribution packet archived by
`TASK-20261009-cd4cf5`. Its three source artifacts and the snapshot receipt
matched their recorded SHA-256 values before analysis. Algebraic claims above
are either explicitly supported by source IDs recorded in that packet or are
the displayed derivations from the frozen dual and automorphism identities.

No PKE, public binding, message recovery, security, novelty, parameter,
hardness, complete-ring reconstruction, or universal impossibility claim is
made.
