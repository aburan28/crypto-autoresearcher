# Canonical staged admission and actual-message decoder repair

**Task:** `TASK-20261006-04e1d5`
**Date:** 2026-10-06
**Disposition:** positive, but only for the scoped interface theorem
**Runs:** scientific 0; implementation 0; formalizer 0; experiment 0

## Result and boundary

This note derives one repair mechanism: canonical exact encodings plus a
two-stage predicate. `PreAdmit` checks everything available before recipient
evaluation—models, exact orders, and an ordered torsion basis. Only after a
separate evaluator returns `A0=f(U), B0=f(V)` does `PostAdmitDecode` check image
orders and recover the selected message.

The repair is positive at that exact scope. It excludes the earlier `P=0` and
`V=0` fibers, makes the exact honest ciphertext relation injective in the
message, and makes decoding correct from a semantically correct evaluated pair.
It does **not** construct the exact recipient map or the uniform two-point
evaluator. It also leaves autonomous generation of the inherited complete
evaluable `End(E)` base object open. It is not a finalist or a security result.

## Exact parameter and encoding slice

Use `p>3`, `p=3 mod 4`, `q=p^2`,

`D=2^a`, `N=5^b`, `a>=2`, `b>=1`, `N>4D`,

with `v_2(p+1)=a` and `v_5(p+1)=b`. Represent the field as
`F_p[i]/(i^2+1)` and the source as the exact short-Weierstrass model
`E0:y^2=x^3+x`. Field elements are ordered residue pairs; curves carry full
field/model/coefficient bytes; points carry the complete curve tag and full
signed `(x,y)`. An x-coordinate, `j`-invariant, field size, alias, or digest is
not exact identity.

The public key binds an **ordered**, role-tagged `(U,V)`. Swapping the two in an
already frozen key fails literal equality. A new key that deliberately binds
the swapped tuple is a different valid key with a different slope convention.
The detailed serialization is in `exact-model-encodings.yaml`.

## Public pre-admission

For a point already checked on its labelled curve, prime-power exact order has
the efficient tests

- `ord(P)=N=5^b` iff `[N]P=O` and `[N/5]P!=O`;
- `ord(U)=D=2^a` iff `[D]U=O` and `[D/2]U!=O`.

Apply the first test to `P` and `X`, and the second to `U` and `V`. Compute the
exact Weil pairing `w=e_D(U,V)` by Miller double-and-add and require
`w^D=1`, `w^(D/2)!=1`. Relative to any basis of `E[D]`, the pairing is a
primitive `D`-th root raised to the coordinate determinant. Full order is
therefore equivalent to an odd determinant, so `(U,V)` is a basis over
`Z/DZ`. The individual tests are retained as explicit failure localizers.

`PreAdmit(pp,pk,ct)` then:

1. parses canonical `pp`, `pk=(E,P,U,V)`, and `ct=(C,X)`;
2. checks the parameter equations, exact source tag, curve nonsingularity, and
   `#C(F_(p^2))=(p+1)^2` by polynomial-time point counting;
3. checks exact order `N` for `P,X`;
4. checks exact order `D` and full-order pairing for the ordered `U,V`;
5. returns a receipt binding the full bytes.

No `f`, `f(U)`, `f(V)`, Hom module, connection, target frame/action/order,
orientation, sender map/dual, retained walk, advice, or preprocessing appears in
this stage.

## Honest generation compatibility

The base generator is stated rather than hidden: `BaseGen` must output the
exact parameter slice and a complete represented/evaluable `O=End(E0)`.
Constructing that inherited object and proving an asymptotic prime-family
sampler are outside this repair. Conditional on any valid `BaseGen` output, the
new admission conditions are efficiently sampleable.

Because the `p^2`-Frobenius on `E0` is `[-p]`,
`E0(F_(p^2))=E0[p+1]` and is isomorphic to `(Z/(p+1)Z)^2`. An exact uniform
point sampler is obtained by rejection from a `2(q+1)`-element index set; every
curve point, including infinity, has one accepting preimage. Its acceptance
probability is `(p+1)^2/(2(p^2+1))>1/2`, so `t_R` attempts fail with probability
at most `2^-t_R`.

Multiplication by `h_N=(p+1)/N` projects uniformly to `E[N]`; an output has
exact order `N` with probability `24/25`. Multiplication by
`h_D=(p+1)/D` projects uniformly to `E[D]`; a random ordered pair is a basis
with probability

`|GL_2(Z/2^a Z)| / 2^(4a) = (1-1/2)(1-1/4) = 3/8`.

With at most `t_P` point trials, `t_B` basis trials, and `t_R` attempts per
uniform-point call, the declared KeyGen failure is at most

`epsilon_base + (t_P+2t_B)2^-t_R + (1/25)^t_P + (5/8)^t_B`.

The conditional expected candidate counts are `25/24` and `8/3`.

For encryption choose uniform `r<2^(a-k)`, set `s=m+2^k r`, and
`K=U+[s]V`. Its `U` coefficient is the unit `1`, so `K` has exact order `D`.
Factor the quotient by `<K>` into `a` normalized degree-two Velu steps,
transporting `P`. This costs `O(a)` degree-two operations and returns exact
`C` and `X=f_s(P)`. Since `gcd(D,N)=1`, `f_s` is injective on `E[N]`, hence
`ord(X)=N`. The chain/map is erased; it is not recipient advice.

## Injectivity of the exact honest relation

First, exact `P` order activates the retained uniqueness lemma. If degree-at-
most-`D` maps `f,g:E->C` on the same exact models agree on `P`, then a nonzero
`h=f-g` kills `<P>`, so `N<=deg(h)`. The degree norm gives
`deg(f-g)<=2deg(f)+2deg(g)<=4D`, contradicting `N>4D`. Thus `f=g`.

Now suppose two honest `(m,r)` and `(m',r')` relations produce exactly the same
ciphertext bytes `(C,X)`. Their maps are equal by the preceding lemma, so

`<U+sV>=<U+s'V>`.

Equality of these order-`D` cyclic subgroups gives
`U+sV=z(U+s'V)` for a unit `z mod D`. Basis-coordinate comparison gives
`z=1`, then `s=s' mod D`. Both slopes use the canonical range `[0,D)`, hence
they are equal as integers; the mixed-radix expansion
`s=m+2^k r` is unique. Therefore both `m=m'` and `r=r'`.

This is exact-public-relation injectivity, not encryption security. With only
`x(X)`, the maps `f` and `-f` collide, so full signed `X` is load-bearing.

## Image order and actual-message decoding

Let an exact homomorphism have kernel `<U+sV>`. If `[n]f(V)=O`, then
`nV=z(U+sV)`. Comparing the `U` coordinate in the admitted basis gives `z=0`,
then comparing the `V` coordinate gives `n=0 mod D`. Thus `f(V)` has exact
order `D`. Also `f(U)=-[s]f(V)`.

Only after the separate evaluator returns `A0,B0` does `PostAdmitDecode`:

1. bind both full signed points to the exact admitted `C`;
2. check `[D]A0=O` and `ord(B0)=D`;
3. set `H=[2^(a-k)]B0`, `G=-[2^(a-k)]A0` and check `ord(H)=2^k`;
4. recover the `k` binary digits of `t` from `G=[t]H`, rejecting a digit test
   that is neither `O` nor `[2^(k-1)]H`;
5. recheck `[t]H=G` and return `t`.

For a correct evaluator,

`G=[s]H=[m]H`,

because the `2^k r` term kills `H`. Exact order of `H` makes the scalar in
`[0,2^k)` unique, so the returned value is the selected message `m`. Naive
cost is `O(a+k^2)` group operations after the two evaluations.

Local order/shape checks do not certify that arbitrary `A0,B0` came from the
right map. Semantic correctness of `Eval2` remains an explicit theorem premise.

## Failure partition and controls

- `MALFORMED_*`: noncanonical bytes, invalid field elements, off-curve or
  x-only points, trailing data.
- `ADMISSION_*`: parameter, tag, curve-order, `P/X/U/V` order, or pairing
  failures.
- `EVALUATOR_*`: missing evaluator, tagged evaluator failure, wrong output
  model, or an unverified semantic relation.
- `DECODER_*`: `A0/B0/H` order failures, nonbinary digit step, or failed final
  equality.
- `WRONG_KEY_*`: receipt/key mismatch or another detectable relation failure.
  This interface is not authenticated encryption; plausible wrong-key inputs
  that pass local checks have no universal rejection promise.

Symbolic controls and their exact separating conjuncts are enumerated in
`attack-gates.yaml`: `P=0`, lower-order `P`, `V=0`, dependent/nonbasis pairs,
weakened pairing and image orders, swapped/retagged inputs, x-only `X`, and a
supplied evaluator. The supplied-evaluator control deliberately decodes and
therefore demonstrates only the conditional decoder, not an evaluator.

## Proof ceiling and scheme obligations

The strongest result here is an efficiently decidable staged interface,
conditional honest sampling over valid base parameters, exact honest-relation
injectivity, and actual-message decoding from correct evaluated images.
`proof-search-map.yaml` records the baseline reproduction, collision fibers,
quantifier order, constructive transforms, and nearby controls.

All scheme obligations O1--O6 remain open in `scheme-obligation-delta.yaml`.
In particular, an EndRing solver plus a future evaluator plus this decoder is a
solver-to-decrypt attack upper bound. It is not the correctly directed
IND-CPA-adversary-to-EndRing reduction.

## Exact unresolved interfaces

1. `BaseGen`: autonomous generation of the complete represented/evaluable
   `End(E)` distribution for the parameter family.
2. Exact calibrated recipient-map construction on the admitted `(E,C,P,X)`.
3. A uniform bit-polynomial `Eval2` returning exactly `f(U),f(V)`, including
   preprocessing, memory, output, success, and failure bounds.

No security, novelty, practicality, deployment, finality, family closure, or
universal EndRing-PKE possibility/impossibility claim is made. The hypotheses
`H-SSI-072490`, `H-SSI-1ed6df`, and `H-SSI-4a0c67` are untouched.
