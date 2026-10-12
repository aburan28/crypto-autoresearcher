# Candidate B: bounded-degree endomorphism evaluation binding (BDEB)

Task: `TASK-20261008-896b35`  
Idea: `IDEA-20261008-71a5ca`  
Hypothesis: `H-SSI-68351d`  
Disposition: **typed obstruction**, not a PKE construction or security result

## Result first

BDEB gives a public relation whose honest fibers are genuinely binding and
whose message mask is invariant under every accepted representation. It is
materially different from a walk-endpoint/parity-mask wrapper: the output is a
full-point evaluation transcript of a bounded-degree self-endomorphism of the
source curve, and equivalence is equality as a rational map.

The same definition defeats the intended trapdoor claim. On the only uniform
polynomial bare-curve sampler supplied here, the sampled endomorphism is a
small public scalar map `[a]`. A polynomial inverse enumerates those scalars
without reading the supplied basis of `End(E)`. Thus the complete ring is not
necessary, the selected message is publicly recoverable, and the required
preimage-to-complete-ring reduction has no supplied final arrow. This is a
typed obstruction for this exact scalar-supported transcript family. It says
nothing about other public-binding relations.

No scientific, implementation, benchmark, formalizer, or parameter-selection
run was performed.

## Exact problem and parameter slice

Let `lambda` be the security parameter, `p=p(lambda)>3`, `q=p^2`, and let
`D_ER(lambda)` be the exact declared bare-EndRing challenge distribution over
canonical short-Weierstrass encodings

```text
E/F_q : y^2 = x^3 + A x + B.
```

The challenge contains only `(p,F_q,E)` and canonical encoding rules. It
contains no orientation, torsion basis, ideal, connecting isogeny, hidden tag,
or planted basis. A solution is four canonical evaluable rational maps forming
a saturated `Z`-basis of the complete ring `End(E)`, with exact equality,
addition, composition, trace, and degree checks. Hardness of this exact
distribution and representation is not established here.

Fix a publicly encoded integer `D=D(lambda)` polynomial in `lambda`, let
`A_D=floor(sqrt(D))`, and set `M=4D+1`. Require
`M < #E(F_q)-1`; otherwise parameter validation returns `PARAM_FAIL`.

`X_E` contains canonical pairs of rational functions encoding an evaluable
endomorphism `alpha:E->E` of degree at most `D`. Fractions are reduced, their
denominators are monic, and coefficient arrays have public degree-derived
lengths. `Y_E` contains

```text
y = (version, D, Q_1,...,Q_M, Z_1,...,Z_M),
```

where the `Q_i` are distinct nonzero points of `E(F_q)` and `Z_i` are canonical
points of `E(F_q)`. Point equality is exact affine/projective canonical byte
equality after validation.

## Public relation and equivalence

`R_E(x,y)=1` exactly when:

1. `x` strictly parses as an endomorphism `alpha_x:E->E` with
   `deg(alpha_x)<=D`;
2. `y` strictly parses, has the same public `D`, and its `Q_i` are distinct,
   nonzero points on `E`;
3. for every `i`, evaluating `x` gives `alpha_x(Q_i)=Z_i`; and
4. complete projective evaluation succeeds at every `Q_i`; an affine
   denominator zero that represents the point at infinity is encoded as the
   canonical `O`, while an actually ill-defined map encoding rejects.

The decision algorithm performs polynomial arithmetic in the rational-map
encoding length and in `M`; because `D` is polynomial in `lambda`, its runtime
is polynomial. Malformed inputs return `0`, never a partially parsed value.

Define `x ~_E x'` iff their evaluated rational maps are equal on `E`; this is
checked by reduced-fraction cross multiplication and the curve equation. Let
`CanMap_E(x)` be the unique reduced, monic-denominator encoding of that map.

### Binding derivation

If `R_E(x,y)=R_E(x',y)=1`, then `delta=alpha_x-alpha_x'` kills all `M`
distinct `Q_i`. The positive-definite degree norm gives

```text
deg(delta) <= (sqrt(deg(alpha_x))+sqrt(deg(alpha_x')))^2 <= 4D.
```

A nonzero endomorphism has at most `deg(delta)` geometric kernel points,
including in the inseparable case when counted without multiplicity. Since
`M=4D+1`, `delta=0`; hence `x ~_E x'` and
`CanMap_E(x)=CanMap_E(x')`.

This is an internal derivation, not a formalized or independently reviewed
theorem. `FORMAL-BDEB-1` blocks promotion until the degree triangle bound,
kernel-cardinality step in characteristic `p`, rational-map parser semantics,
and canonicalization lemma are machine-checked or independently proved.

## Algorithms from bare `E`

### `PointList(E,M;rho_Q)`

Read independent uniform `x` coordinates from `rho_Q`. When
`x^3+A x+B` is a square, choose the canonical square root and retain the
resulting nonzero point if its encoding is new. Stop after `M` points or after
the public cap `T` trials. Return the list or `POINT_FAIL`. Hasse's lower bound
gives a public lower bound

```text
rho_E >= 1/2 - 1/p - M/q
```

on a new usable x-coordinate at each unfinished step. The declared failure
bound is the conservative binomial tail

```text
delta_pts <= sum_{j=0}^{M-1} binom(T,j) rho_E^j (1-rho_E)^(T-j).
```

No concrete `p,D,T` is selected in this zero-run packet.

### `Sample(E;rho_a,rho_Q)`

1. Strictly validate `E,D,M,T`.
2. Sample `a` uniformly from
   `S_D={a in Z: 1<=|a|<=A_D}`.
3. Construct the canonical multiplication map `x=[a]` using division
   polynomials; `deg(x)=a^2<=D`.
4. Run `PointList`; on failure return `SAMPLE_FAIL`.
5. Return `(x, Eval(E,x,Q_1,...,Q_M))`.

This uses only bare `E` and public coins. It samples only the public scalar
subring `Z[1]`; complete-ring provenance is absent.

### `Eval(E,x,Q_1,...,Q_M)`

Strictly validate the map and points, evaluate `Z_i=x(Q_i)`, and return `y`.
Runtime and output length are `poly(D,log q)`. No endpoint selector, path,
orientation, quotient lift, `BaseGen`, or `Eval2` is used.

### `Inv(E,B,y)` for every complete basis

Validate that `B` is a complete evaluable basis, but do not use its elements.
Enumerate `a=-A_D,...,-1,1,...,A_D`, construct `[a]`, and return the first
canonical map satisfying `R_E([a],y)=1`; return `NO_PREIMAGE` if none does.
For every honest output, the sampled `[a]` is found, and binding makes its map
unique. The runtime is

```text
O(A_D * M * C_mul(D,log q)) = poly(lambda).
```

Therefore the any-basis condition holds for the wrong reason: `Inv` is a
public inverse and works even when `B` is deleted.

## Actual-message adapter and invariance

The minimal PKE-shaped adapter would define

```text
K = XOF("BDEB-mask" || encode(E) || CanMap_E(x) || encode(y), |m|)
ct = (y, z=m xor K).
```

Decryption runs `Inv(E,B,y)` and unmasks. If `x'` is any accepted
representative, the binding derivation gives `CanMap_E(x')=CanMap_E(x)`, so
every accepted representative returns the actual selected message `m`.
Representation changes cannot change the mask.

But the public inverse computes the same `x'` without `B`, so anyone recovers
`m`. BDEB consequently does not supply confidential recipient functionality.
This failure is stronger than a missing proof and narrower than an
impossibility theorem: it is an explicit public algorithm against this honest
support.

## Repeated-use semantics

The scoped adversary is classical PPT. It sees `(p,F_q,E,D,M,T)`, all parser
rules, every `Q_i,Z_i`, every mask `z`, validation/rejection results, and the
public hash/XOF specifications. It may adaptively choose equal-length messages
and obtain at most `q_S(lambda)` accepted encryptions. Each call samples an
independent scalar `a_i` and independent point-list coins. The scheme and
inverse are stateless; no coins are coupled across calls. A `SAMPLE_FAIL`
returns the public failure symbol before a ciphertext exists and contributes
at most `q_S*delta_pts` by union bound.

For every accepted call the public scalar enumerator recovers the unique map.
Across calls, the sufficient witness is the list of small integers
`(a_1,...,a_q)` or their canonical scalar maps; it remains inside the rank-one
subring `Z[1]`. Adaptive history does not turn it into a saturated rank-four
basis of `End(E)`.

## Smaller-witness and correctly directed reduction audits

The smallest known sufficient witness is one scalar `a` per honest transcript;
equivalently, the single canonical map `[a]`. The interface factors as

```text
complete basis B --delete--> no secret
                    public scalar enumeration --> [a] --> message.
```

No non-factorization theorem is possible for this sampler. No theorem
reconstructs a complete ring from one or polynomially many sampled scalars;
the samples span only `Z[1]`.

For the relation one-way game, the public adversary succeeds on every accepted
honest output, so

```text
Succ_BDEB-OW(A_pub) = 1.
```

For the IND-CPA adapter, it recovers the challenge message and wins with
probability `1`, hence advantage `1/2` under the repository convention. The
required reduction would need

```text
Adv_IND-CPA(A) <= L(lambda) * Succ_EndRing(B_A) + delta(lambda).
```

No `B_A` is supplied. With polynomial `L` and negligible `delta`, applying the
claim to `A_pub` would assert a nonnegligible EndRing solver from a public
scalar enumerator. That is exactly the missing and proves-too-much extraction
step, not evidence that EndRing is easy. The valid arrow is only

```text
attacker -> scalar preimage/message,
```

and the required `scalar preimage -> complete EndRing basis` arrow is absent.

## Obligation and completion status

| Gate | Status | Reason |
|---|---|---|
| O1 | proposed discharge | Exact bare problem and complete evaluable output are stated; hardness and distribution sourcing remain unreviewed. |
| O2 | open | Binding-interface algorithms are explicit, but no polynomial trapdoored `KeyGen` for `(E,B)` on the exact bare challenge distribution is supplied. |
| O3 | proposed discharge | Every accepted representative gives the same mask and actual message, conditional on the internal binding derivation. |
| O4 | contradicted in this family | The recipient operation is publicly executable and ignores `B`. |
| O5 | contradicted for the proposed chain | Public success yields only a scalar/map, not a complete ring; no quantitative extractor exists. |
| O6 | open | Repeated-use/public view is specified, but no independent review or implementation-side-channel analysis exists. |
| C1 | open | Only abstract/first-page corpus pointers were read; primary specifications and novelty are unverified. |
| C2 | contradicted for promotion | The PKE-shaped adapter is publicly decryptable and no efficient exact-distribution trapdoor key generator is supplied. |
| C3 | open | Symbolic correctness has no implementation or independent validation. |
| C4 | contradicted for this chain | Correctly directed EndRing reduction stops at a scalar preimage. |
| C5 | open | No parameter/cost table or primary-source non-duplication review. |
| C6 | open | Independent T1--T5 review has not yet occurred. |

## Controls, method ceiling, and next action

- **Leaked/public inverse:** BDEB intentionally triggers this control; deleting
  `B` does not change output.
- **Ordinary many-to-one transcript:** use `M<=4D`; the kernel-count binding
  derivation no longer forces equality.
- **Equivalent encodings:** unreduced fractions must normalize to the same
  `CanMap`; noncanonical bytes reject.
- **UTTK/CEST finite witness:** a single evaluated endomorphism or scalar is a
  smaller witness; no complete-ring necessity is inferred.
- **Oriented/torsion nearby object:** adding an orientation or torsion basis
  changes the public problem and is not a repair inside BDEB.
- **Method ceiling:** this family can certify fiber binding and
  representation-invariant message recovery. It cannot, with scalar honest
  support, certify recipient secrecy or complete-ring necessity.

The next action is not an experiment. Formalize `FORMAL-BDEB-1`, then search
for a bare-`E`, polynomial sampler whose honest support escapes every publicly
generated proper subring while retaining the same binding proof. If no such
sampler is specified, retain this typed obstruction and do not wrap it in
another PKE mask.

## Requirement-to-artifact accounting

| Requested item | Status | Location |
|---|---|---|
| Relation/equivalence/inverse | complete at proposed symbolic scope | this file; `binding-interface.yaml` |
| Bare-E `Sample/Eval` | complete for scalar honest support | algorithms above |
| Every-basis `Inv` | complete but publicly factorized | algorithm above |
| Actual-message invariance | complete conditional derivation | message adapter above |
| Repeated use and smaller witnesses | complete at declared game scope | sections above |
| Correct reduction | blocked at preimage-to-ring reconstruction | reduction audit above |
| Formalization | not attempted; named blocker | `FORMAL-BDEB-1` |
| Experiments/implementation/parameters | not attempted by instruction | zero-run accounting |

