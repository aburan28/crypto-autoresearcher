# Low-Hamming x-rank overlap audit

## Audit basis

- Idea: `IDEA-20261007-1a61b9`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Relevant baselines: `KR-RHO-13bf67` and `KR-RHO-ea34b8`.

## Scientific boundary

The proposal measures whether the points whose integer x-coordinates are
small overlap unusually with points whose scalar labels have low binary
Hamming weight, on two small ordinary prime-order subgroups. It is a finite
rank-correlation census. It does not provide a coordinate membership test,
enumerate a low-Hamming discrete-log algorithm, or change the generic
time-space frontier.

The distinction between the instrument and the hoped-for algorithm must stay
explicit: constructing the scalar table and the x-ranked set uses the
discrete-log labels and is an offline measurement. A measured overlap cannot
be charged as a usable x-only predicate unless a separate algorithm actually
decides membership in the ranked set without the scalar table.

## Load-bearing orbit definition

The current contract is ambiguous at the negation quotient. The x-coordinate
identifies `k` and `N-k`, but low Hamming weight generally does not: one of
`k` and `N-k` can lie in `W` while the other does not. The repaired contract
must choose one of these distinct objects before counting:

1. scalar-level `W` with a point-level or orbit-level `B`, defining whether an
   orbit is a hit when either representative is in `W`;
2. a canonical orbit set `W_orb = {[k] : k in W or N-k in W}`; or
3. a representative-dependent set using a declared canonical scalar rule.

The denominator, numerator, and size of `B` must use the same object. “Do the
negation quotient before the counts” is insufficient because quotienting can
change both membership and cardinality. The control must report `|W|`,
`|W_orb|`, the number of singleton/two-element orbits, and both possible
orbit conventions if they differ.

The phrase “the `|W|` subgroup points of smallest x” must be replaced by an
unambiguous orbit ranking. If the ranked object is a set of x-values, count
each x fibre once; if it is a set of points, define how the two points above
one x are handled. Ties and the possible final partial x-fibre must be
specified. The scalar-ranking positive control must be evaluated under the
same orbit convention, not assumed to recover overlap one by construction.

## Null and statistical contract

A single random subset is not a null distribution. The repaired design needs
many deterministic, independent matched subsets of exactly the same orbit or
point cardinality, with the same tie and quotient rules, and must report the
full overlap distribution, expectation, variance, and a predeclared
interval or tail criterion. The hypergeometric expectation applies only after
the population and subset sizes are fixed; it does not imply independence
between scalar labels and x ranks.

The two selected curves must be chosen before reading their overlap, with
complete prime, ordinaryness, subgroup-order, generator, and point-count
certificates. The excluded curve must remain an exclusion rule rather than a
post-hoc comparison. The scalar table must independently verify every
`[k]G`, and the x-ranking code must be independent of that table so that the
control does not reuse the same ordering implementation.

## Claim ceiling and disposition

A valid result could establish only the finite overlap and its matched-null
distribution under the selected curves, subgroup orders, orbit convention,
and Hamming threshold. An excess at or below the proposed threshold does not
prove the absence of a coordinate test. An excess above it would motivate a
new search for such a test, but would not itself provide one or imply a
sub-square-root ECDLP method.

Disposition: **keep proposed as a conditional finite measurement; do not
approve it as an algorithmic direction as filed.** Repair the negation-orbit
semantics, x-fibre/tie handling, matched-null ensemble, and scalar/control
certificates. If the repaired contract remains useful, attach it to the
low-Hamming representation study; otherwise leave it unexecuted while the
readiness selector has no admitted row and the resource guard is unfavorable.
