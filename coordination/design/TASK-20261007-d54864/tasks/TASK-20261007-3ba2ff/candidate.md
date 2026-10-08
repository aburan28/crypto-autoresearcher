# Saturation-filtered RWER: typed obstruction packet

Date: 2026-10-07  
Task: `TASK-20261007-3ba2ff`  
Candidate record: `IDEA-20261007-0024cc`  
Hypothesis record: `H-SSI-2c8bba`

## Outcome and scope

This packet attempts the smallest repair of random-walk endpoint relation
inversion (RWER): require repeated inverse images to yield non-scalar,
independent loops that generate the full maximal order. The repair fails at a
typed, quantitative arrow. It is therefore recorded as a **scoped
obstruction**, not as a candidate scheme and not as an impossibility result
for other EndRing interfaces.

The affected family consists only of interfaces in which public sampling
chooses explicit isogeny walks `x`, public evaluation publishes their endpoint
data `y = Eval_E(x)`, and inversion accepts any valid endpoint preimage. No
canonical selector, orientation, connecting ideal, endpoint ring, routing
table, planted basis alignment, or exact-preimage binding is available.

## Attempted repaired interface

For polynomially bounded `k,q,L`, let `Walk_L(E)` be validated encodings of
length-`L` walks of declared small prime degrees, starting at the bare curve
`E`.  A path encoding contains every edge kernel representation needed for
public evaluation and rejects malformed curves, kernels, degrees, or broken
incidence.

- `X_E = Walk_L(E)^k`.
- `Y_E` is the tuple of canonically serialized endpoint curves, degree words,
  and public validation tags.
- `Sample(E)` independently samples and validates `k` walks, with an explicit
  retry cap; it returns `abort` after the cap.
- `Eval(E,x)` evaluates the walks and emits their endpoint tuple.
- Ordinary inversion asks for any `x'` with `Eval(E,x') = y` under exact byte
  parsing and mathematical endpoint equality.

Given the hidden sampled `x` and an inverse `x'`, the reduction can form, for
each component with common endpoint, the evaluable loop

```text
alpha_i = dual(x'_i) o x_i in End(E).
```

The proposed saturation filter would accept only if the generated order from
the `alpha_i` has rank four and is the full maximal order. That predicate is
not a predicate of `(E,y,x')`: it depends on hidden `x`. Adding it changes
ordinary relation inversion into a new planted-collision game.

## Quantitative failure

Let an inverter `I` have ordinary endpoint-inversion success `epsilon`, make
at most `q` outputs across repeated calls, and let

```text
u_I = Pr[ SatFull({dual(I(y_j)) o x_j}_{j=1..q}) | all returned preimages valid ].
```

The ordinary game constrains only endpoint validity. It places no lower bound
on `u_I`. In particular, a deterministic selector `s(y)` may return the same
canonical or padded representative on every call. Nothing in public validity
rules out scalar loops, repeated loops, a rank-one span, or a proper suborder.
Hence the only uniform bound derivable from ordinary inversion success is

```text
Pr[complete evaluable End(E) basis extracted] = epsilon^q * u_I,
0 <= u_I <= 1,
and the proved lower bound is 0.
```

Increasing `q` does not repair this: correlated selector outputs need not add
rank. Four loops are not a rank-four certificate, and rank four is not
full-order saturation. Edge/dual-edge detours supply public rerandomization
but only known scalar loops. A positive `u_I` would therefore be a new
distributional/extraction assumption, not a consequence of EndRing hardness
or of endpoint inversion.

## Minimal selected-message adapter and first arrow

The minimal attempted one-bit PKE adapter is:

```text
KeyGen: publish E; retain a complete evaluable basis B of End(E).
Enc(E,m): x <- Sample(E); y <- Eval(E,x); return (y, m xor h(x)).
Dec(B,(y,z)): x_B <- Inv(B,y); return z xor h(x_B).
```

Correctness for every valid basis and every allowed inverse requires `h` to be
constant on every admitted fiber of `Eval`. If `h` is not fiber-constant,
different valid outputs of `Inv` decrypt differently. If `h` is replaced by a
Goldreich--Levin-style predicate of the sampled encoding, the same problem
remains. If `h` is fiber-constant, an IND distinguisher predicts a bit of the
fiber; no decision-to-search compiler has been supplied that turns that bit
prediction into any endpoint preimage, much less a saturation-producing one.

Thus the explicit two-hop accounting is:

```text
IND advantage delta
  -- A1: MISSING --> ordinary/strengthened interface inverter
  -- A2: lower bound 0 --> complete evaluable End(E) basis.
```

For any claimed compiler losses `L1,L2` and error `eta`, the desired bound
would have to take the form

```text
Succ_EndRing(B) >= (delta - eta)/(L1*L2).
```

No finite `L1` is established, and ordinary RWER gives no finite positive
`L2` because `u_I` may be zero. Runtime, query, and abort accounting therefore
cannot be completed. This is the earliest missing arrow in the selected-
message route; the loop-diversity failure is an independent second break even
if A1 is granted.

## Every-basis inversion

The attempted `Inv(B,y)` still requires a polynomial routing algorithm from
an arbitrary complete evaluable basis `B` to paths ending at each component of
`y`. No such algorithm is supplied. A basis change cannot be assumed to
preserve planted coordinates or a routing table. Therefore T2 also remains
open; changing `Inv` to return `B` would change the codomain of inversion and
would not return an element of `X_E`.

## Required controls

- **CEST/RWCT factorization:** endpoint outputs remain finite public
  observables. The attempted filter depends on the hidden original preimage
  and therefore does not repair public-observable factorization.
- **`GL_4(Z)` basis change:** no step may use coordinates in a planted basis;
  the missing routing algorithm persists after arbitrary unimodular change.
- **Leaked-output control:** revealing the sampled `x` makes the mask public
  and destroys the adapter; it does not create a confidentiality theorem.
- **Public-inversion control:** if a public inverter exists, decryption is
  public. If it returns a deterministic selector, loop saturation still need
  not follow.
- **Malformed inputs:** parsing rejects invalid curves, kernels, incidence,
  degree words, tuple lengths, and noncanonical serializations before path
  evaluation; rejection behavior supplies no diversity guarantee.

## Six obligations and successor condition

| Obligation | Status | Reason |
| --- | --- | --- |
| O1 | open | Ordinary RWER and the strengthened planted-collision game are distinct problems. |
| O2 | contradicted for this syntax | `Inv` lacks an every-basis routing algorithm. |
| O3 | contradicted for the adapter | Fiber-dependent masks do not decrypt through arbitrary valid inverses. |
| O4 | open | No secret-dependent recovery operation is supplied without a missing route/selector. |
| O5 | contradicted for this syntax | A1 is missing and A2 has uniform lower bound zero. |
| O6 | proposed discharge only | Encodings and controls are specified, but no independent review is claimed. |

A successor may revisit this family only with either (i) a public binding
mechanism that makes the relevant preimage unique while preserving efficient
every-basis inversion, plus a selected-message reduction, or (ii) a proved
conditional-fiber theorem giving non-scalar independence and maximal-order
saturation against arbitrary successful selectors. Either item is a new
load-bearing theorem; neither is assumed here.

