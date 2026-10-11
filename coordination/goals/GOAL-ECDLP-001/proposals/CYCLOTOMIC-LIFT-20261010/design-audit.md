# Cyclotomic complete-splitting lift audit

## Audit basis

- Idea: `IDEA-20261009-57140c`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `EXP-ECDLP-3e8403`, `KR-IC-cd159a`, and
  the global-nontorsion lifting obstruction in `KN-TECH-06bb4e`.

## Mathematical boundary

For prime `c` and `p = 2^c - 1`, Fermat's theorem gives `p = 1 mod c`, and
`ord_p(2) = c`; therefore `p` splits completely in `Q(zeta_c)`. This is a
valid field-splitting fact, but it does not by itself produce an ECDLP
relation mechanism. The displayed presentation
`F_p = Z[x]/(x^c - 1, p)` must be treated as shorthand for an evaluation at
`x = 2`; the evaluation kernel also contains `x - 2`, and the quotient by
`(p, x^c - 1)` is not itself `F_p`.

If `K` is a degree-`d` subfield in which `p` splits completely, a point
`P in E(K)` has reductions at the `d` primes above `p`, and the sum of the
conjugates is the reduction of `Tr_{K/Q}(P)`. That identity is useful only
after the reduction maps, prime ordering, curve model, and trace point are
certified. It does not imply that the `d` reductions lie in a chosen factor
base, are distinct, or provide independent relation columns.

## Load-bearing repairs

1. Define `K` exactly for every `(c,d)`, including its defining polynomial,
   discriminant, integral basis, embeddings, and prime ideals above `p`.
   Verify complete splitting by explicit residue-degree and factorization
   certificates rather than by the congruence alone.
2. Replace “one K-point gives `d` residues and one free relation” with a
   certified relation construction. Enumerate the conjugate reductions,
   require each to meet the declared factor-base membership rule, verify the
   group sum directly, and record whether the trace is the identity or a
   known torsion point after reduction.
3. Measure relation rank novelty, not only the ratio of listed relations to
   distinct residues. Conjugate points can repeat residues, trace relations
   can be dependent, and a large relation count can have little linear rank.
   Report construction cost, point-enumeration cost, reduction cost, and
   deduplication cost separately.
4. Define the target object and coverage statistic: subgroup/order, target
   distribution, factor-base size, allowed arity, ordered-pair convention,
   repeated and inverse points, identity handling, and whether a relation is
   counted only after direct point-addition verification.
5. A rank-0 curve over `Q` must carry independent rank and torsion
   certificates. The difference `rank E(K) - rank E(Q)` is not a proxy for
   useful relations; rank computations over degree-12 fields need explicit
   proof status and bounded-search versus certified-rank labels.
6. Match random-field controls on degree, discriminant, splitting at the
   same `p`, curve, factor-base rule, height/enumeration budget, and stopping
   rule. “Similar discriminant” is not a reproducible null. Bind all random
   fields and seeds before reading the special-arm results.
7. Correct the statistical contract: predeclare the relation-yield and
   covering contrasts, independent sampling units, interval construction, and
   multiple-cell correction. The filed `direction: different` conflicts with
   an expected ratio near one, and three seeds do not by themselves define
   replicated field/curve observations.

## Claim ceiling and disposition

A valid study could report finite, certified relation construction and
coverage measurements for the declared cyclotomic subfields and matched
random fields. It would not establish an asymptotic lifting method, a rank
formula, or a sub-square-root ECDLP algorithm. A positive finite signal would
remain conditional on complete splitting, factor-base membership, relation
rank novelty, and all charged costs.

Disposition: **retain proposed and revise; do not approve or dispatch as
filed.** The item needs an executable contract, exact field and reduction
certificates, a rank-novelty metric, matched null fields, and complete cost
accounting. The current goal-scoped selector has no ready row, and approval
capacity must be rechecked before any successor contract is considered.
