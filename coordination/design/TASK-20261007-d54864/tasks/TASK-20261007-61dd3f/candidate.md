# Candidate B: random-walk endpoint routing (`RWER-Trap`)

Date: 2026-10-07  
Goal: `GOAL-SSI-2fa82a`  
Question: `RQ-SSI-1946c9`  
Producer: `TASK-20261007-61dd3f`  
Proposal: `IDEA-20261007-7625cc`  
Hypothesis: `H-SSI-125654`

## Outcome and claim boundary

`RWER-Trap` is a **typed obstruction packet**, not a trapdoor function, PKE,
security theorem, novelty result, or impossibility theorem. Its public side is
an explicit small-degree isogeny-walk endpoint map. Its required private side
would route from the source curve to a sampled endpoint using *any* complete
evaluable basis of the source endomorphism ring. No such polynomial routing
algorithm is supplied by the scoped sources. The earliest failed arrow is
therefore `Inv_from_complete_basis`, and the packet stops before building a PKE
wrapper.

No experiment, implementation, formalizer, benchmark, or parameter-selection
run was performed.

## Exact candidate interface

Let `p > 3`, let `E/F_{p^2}` be drawn from the exact curve-only EndRing
challenge distribution, and fix a constant prime `ell != p` and polynomially
bounded integers `L >= 1` and `L_max >= L + 2`.

`X_E` consists of validated encodings of separable `ell`-isogeny walks

```text
pi = (E = E_0, phi_0, E_1, ..., phi_{t-1}, E_t),  0 <= t <= L_max.
```

Each edge includes canonical source/target models and an explicit normalized
rational-map or kernel-polynomial certificate. `Y_E` is the canonical encoding
of the endpoint isomorphism class, initially `j(E_t)` with exceptional
automorphism cases tagged. Two paths are equivalent exactly when their
endpoints have the same validated canonical encoding.

```text
Trap_E(pi) = CanonicalEndpoint(E_t).
```

### Public `Sample(E)`

Starting from the bare input curve, enumerate the constant-degree cyclic
subgroups at each step over a deterministically represented splitting field,
canonically sort their edge encodings, sample an edge, compute its quotient,
and repeat for exactly `L` steps. This uses no orientation, torsion basis,
connecting isogeny, endomorphism, or ring basis. Finite-field factoring makes
the proposed sampler expected-polynomial for fixed `ell`; its exact retry and
normalization bounds remain open rather than being silently assumed.

### Public `Eval(E, pi)`

Parse and validate every curve and edge, verify source/target continuity and
degree `ell`, reject paths longer than `L_max`, and return the canonical
endpoint encoding. The path itself is the evaluation witness, so no hidden
ring-correlated public data is needed.

### Required private `Inv(E, B, y)`

Here `B = (beta_1,...,beta_4)` is any valid complete evaluable `Z`-basis of
`End(E)`, with rational-map evaluation and certificates for its full-order
span. The required algorithm must return some validated `pi' in X_E` with
`Trap_E(pi') = y` for every `y` in the honest sampler support, in polynomial
time and with an explicit negligible failure bound.

This algorithm is unavailable. In particular, the packet has no polynomial
procedure that derives the endpoint order, a connecting ideal, or a route from
the source basis alone. An algorithm that accepts only a planted quaternion
basis, an oriented curve, both endpoint rings, or a precomputed routing table
does not meet this type.

## Any-basis statement and basis-change audit

The quantifiers are deliberately ordered as

```text
for every sampled E,
for every valid complete evaluable basis B of End(E),
for every y in Supp(Trap_E(Sample(E))):
    Inv(E,B,y) returns a valid preimage except with epsilon(lambda).
```

If `B' = B U` for any `U in GL_4(Z)`, correctness and the output distribution
must remain within the same declared equivalence class. A preprocessing step
may compute basis-invariant multiplication and trace data, but it may not ask
for the basis used during key generation. No normalization-to-routing theorem
or algorithm is available, so this audit **breaks at T2**.

## Four cheap audits

1. **CEST/RWCT regression.** This map is not a tuple of point evaluations and
   does not use planted noncommutative words. Nevertheless, merely deriving it
   during a KeyGen that knows `End(E)` would again prove provenance, not
   necessity. The regression therefore rejects any argument of the form
   “KeyGen used the ring, so endpoint routing requires the ring.”
2. **Collisions and smaller witnesses.** For every admitted path `pi` with
   room for two edges, appending an edge and its dual gives a distinct encoding
   with the same endpoint. Thus the map is explicitly many-to-one. A
   target-specific connecting path is a smaller witness for that target; a
   polynomial routing data structure, an endpoint order plus connecting ideal,
   or bounded torsion-action data are further candidate factorization objects.
   No non-factorization theorem rules them out, and no theorem reconstructs a
   complete source ring from any one of them. T3 is open.
3. **Quantifier order.** The desired inverter must accept every complete basis,
   not one aligned with a planted path or quaternion presentation. The missing
   basis-invariant router is the earliest failed arrow.
4. **Known-false control and ceiling.** If `Y_E` is changed to contain the full
   path, inversion is public while the historical KeyGen provenance could
   still mention `End(E)`. The audit correctly refuses a trapdoor conclusion.
   These symbolic checks can expose this candidate's missing arrows and exact
   collisions; they cannot prove that no EndRing-based trapdoor interface
   exists.

## Correctly directed security route

The first intermediate game would be relation inversion: sample
`pi <- Sample(E)`, give `(E, Trap_E(pi))`, and ask for *any* valid path to the
same endpoint. Two required reductions are absent:

```text
selected-message IND attacker
    -X-> endpoint-relation inverter
    -X-> complete evaluable End(E) basis.
```

The second arrow has a concrete proof-search lead: when a reduction knows the
sampled path `pi` and an inverter returns `pi'`, composing `dual(pi')` with
`pi` yields an endomorphism of `E`. Repetition might yield enough independent
endomorphisms to reconstruct and saturate the full order. But no scoped source
proves a nontrivial-collision probability, rank-four generation, saturation,
runtime, or robustness to an inverter that returns a canonical path. This is a
lemma obligation, not a reduction.

The first arrow is also missing. Because the endpoint map is many-to-one, an
arbitrary inverse need not preserve any path-dependent hardcore predicate;
there is no selected-message-correct PKE compiler in this packet. Adding a
path hash or canonical-preimage selector would introduce a new assumption or
an unavailable public selector.

## O1--O6 precursor status

| Obligation | Status | Reason |
| --- | --- | --- |
| O1 | `open` | Curve-only EndRing input and output type are stated, but no primary equivalence source was read and exact challenge sampling remains inherited. |
| O2 | `contradicted` for this packet | Public `Sample/Eval` are specified prospectively; polynomial any-basis `Inv` is absent. |
| O3 | `open` | No PKE is built. Relation correctness would be conditional on the missing inverter. |
| O4 | `open` | The proposed recipient operation is exactly the missing router. |
| O5 | `open` | Both attacker-to-inverter and inverter-to-full-ring reductions lack required lemmas and bounds. |
| O6 | `open` | Collisions and the leaked-path control are covered, but the complete scheme view does not exist. |

## Smallest next lemma

Before any wrapper is proposed, either construct

```text
Route(E, B, y) -> pi
```

with polynomial bounds and the stated every-basis quantifier, or give a scoped
counterexample showing that source-ring data alone cannot supply the missing
endpoint information for this exact interface. Only after that should the
collision-loop reconstruction lemma be attempted. This candidate does not
warrant an implementation run in its present form.

## Prior-art and dominance boundary

The scoped literature records are abstract-level pointers only. They describe
Séta's torsion-attack trapdoor, SiGamal's auxiliary-point hidden-isogeny
assumption, a SIDH-oriented key-updatable construction, and LIT-SiGamal's
diagram construction. None was read at primary-source depth here. Therefore
`RWER-Trap` has `novelty_status: unverified`; no non-duplication, security, or
performance comparison is asserted.

`dominated_by` is unresolved. `sota_delta` is not numerically available: the
target is polynomial time and memory in `lambda` and `L`, while the packet
does not establish any inverter at all.
