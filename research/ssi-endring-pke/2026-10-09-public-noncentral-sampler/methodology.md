# Public noncentral-endomorphism sampler feasibility

Date: 2026-10-09

Goal: `GOAL-SSI-2fa82a`

Question: `RQ-SSI-1946c9`

Batch: `BATCH-12e6aa`

Opening decision: `DEC-20261009-00e7ac`

## Purpose

This bounded zero-run round investigates the exact continuation selected by
`BATCH-fc23a6`: whether a bare supersingular curve admits a polynomial public
sampler for a non-scalar evaluable endomorphism. It remains before public
binding, message recovery, complete-ring reconstruction, and PKE.

The decision-changing tension is explicit. If a public algorithm receives only
`E` and returns an efficiently represented element of `End(E) \ Z`, then it
appears to solve `OneEnd`. Whether that implication and a further
`OneEnd -> EndRing` reduction cover the exact distribution, representation,
degree, success, and assumption profile must be read from primary sources and
independently re-derived. The opening does not treat a literature summary as a
theorem.

## Frozen bare-curve distribution

For security parameter `lambda`, freeze public parameters

```text
Pi_lambda = (p_lambda, F_{p_lambda^2}, E0_lambda,
             ell, L_lambda, Canon, A_eval).
```

Starting from the public supersingular `E0_lambda`, the challenge sampler takes
an exact uniform nonbacktracking `ell`-isogeny edge at each of
`L_lambda` declared steps, respecting the frozen edge-multiplicity convention.
It canonically encodes the endpoint `E` and erases the walk, kernels, maps,
orientation, ideals, torsion labels, and endomorphism-ring witness. The
algorithm under study receives only `Pi_lambda`, `E`, and fresh coins.

This is a campaign-defined endpoint law inherited from the UTTK predecessor.
It is not asserted to be a standard EndRing hardness distribution. Establishing
or denying that bridge is outside the definition and must be sourced.

## Frozen sampler question

Does there exist a PPT algorithm

```text
Samp(Pi_lambda, E; rho) -> FAIL or D_alpha
```

where `D_alpha` has canonical serialized syntax for an efficient evaluator and
passes a public verifier proving that it denotes

```text
alpha : E -> E,       alpha in End(E) \ Z?
```

The packet must provide an explicit polynomial `q`, negligible `nu`, and the
bound

```text
Pr_{E <- D_ER}[
  Pr_rho[Verify(E,D_alpha)=1] >= 1/q(lambda)
] >= 1 - nu(lambda).
```

It must separate bad-curve mass from per-curve coin failure. Average success
cannot silently become per-curve success, and retries cannot silently resample
the challenge curve. The unconditional byte-level output law, runtime, memory,
retry cap, aborts, and failure symbol are part of the question.

Canonical serialization means an unambiguous frozen byte grammar. It does not
by itself prove uniqueness among every program representing the same map; that
semantic equality issue is audited separately.

## Four proposal families

### F1 — relative Frobenius and the conjugate curve

Attempt to construct a separable `phi:E -> E^(p)` and compose it with relative
Frobenius `E^(p) -> E`. The prime-field locus is accounted for separately.
Coordinatewise `p`-power with target `E^(p)` is not accepted as an endomorphism
of `E` unless the return map is supplied and typed.

### F2 — exceptional automorphism transport

Use a public nontrivial automorphism directly at `j=0` or `1728`, or transport
one to a general curve as `dual(phi) o u o phi`. The analysis charges the mass
of exceptional endpoints and the cost of finding and representing `phi`. A
special-key distribution is not substituted for the frozen law.

### F3 — short nonbacktracking cycles

Sample or enumerate bounded-length small-degree isogeny cycles returning to
`E`, compose their normalized maps, and certify non-scalarity. The producer
must provide an exact return probability and total cost; random-regular-graph
intuition or a mixing heuristic is not a success bound.

### F4 — bounded map or interpolation search

Sample a canonical bounded rational-map, evaluation-program, or interpolation
descriptor; verify the curve equation and source/target; and reject scalar
maps. The complete coefficient or transcript sampling space and its acceptance
probability are charged.

The two producers are mutually blind until their bytes are frozen. Their
packets are theory artifacts, not automatically `IDEA-*` records.

## Controls

The following controls are mandatory:

- scalar multiplication `[a]`;
- an immediate dual backtrack `dual(phi) o phi=[deg(phi)]`;
- the applicable central `p^2`-Frobenius slice;
- `p`-Frobenius with codomain `E^(p)` rather than `E`;
- a supplied exceptional automorphism as a positive typing control;
- a leaked walk, orientation, ideal, tag, torsion label, or complete basis;
- conditioning on exceptional or prime-field loci;
- a polynomially enumerable proper witness family; and
- two distinct evaluator programs representing one semantic map.

A noncentrality test that accepts a scalar or immediate backtrack fails. A
sampler that needs secret-correlated data is an augmented problem. Absence of a
known public enumerator is not proof that none exists.

## Quantifier and proof-search discipline

The order is:

1. freeze the parameter family, law, grammar, evaluator, candidate route, and
   bounds;
2. sample `E`;
3. run only on `Pi_lambda`, `E`, and independent coins;
4. prove the conditional success bound for good curves;
5. bound bad-curve mass;
6. derive the retry cap;
7. verify every accepted descriptor as a non-scalar self-map;
8. derive `Samp -> OneEnd`; and only then
9. apply a primary-source `OneEnd -> EndRing` reduction if every premise
   matches.

The proof-search map is `P0` exact distribution and representation, `P1`
public-only dependency, `P2` map typing, `P3` non-scalarity, `P4` law and cost,
`P5` sampler-to-OneEnd, `P6` OneEnd-to-EndRing, `P7` support/enumeration, and
`P8` the method ceiling.

## Review and stopping rule

The review plan is frozen before production. J1 owns distribution and sources;
J2 owns typing and non-scalarity; J3 owns success and cost; J4 blindly
re-derives the hard-problem implication; J5 owns enumeration and auxiliary
data. J6 is the post-report documentation gate. Reviewers do not read one
another, and composition is not a vote.

One reserved correction may be admitted only when one source or typing repair
could change one family disposition without changing the challenge distribution
or adding auxiliary data. Otherwise it is skipped. The batch stops after the
initial evaluation or that one scoped re-evaluation.

All scientific, implementation, formalizer, experiment, benchmark, and
parameter-selection run budgets are zero. Read-only source retrieval,
administrative validation, archival checks, and document rendering do not
constitute scientific runs.

## Claim boundary

The strongest permissible result is a typed route, a scoped obstruction for a
named family, or a reviewed source-backed implication from the frozen sampler
interface to OneEnd and possibly EndRing. The batch cannot establish a secure
or novel PKE, IND security, concrete parameters, EndRing hardness, an EndRing
break from an unreviewed implication, complete-ring reconstruction, or a
universal impossibility theorem for EndRing-based encryption.
