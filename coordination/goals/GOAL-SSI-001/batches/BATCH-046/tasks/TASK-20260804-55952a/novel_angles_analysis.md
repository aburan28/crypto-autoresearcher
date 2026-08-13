# Novel Angles Analysis: Average-Case, Compositional, Type-Number, and Hecke

**Verdict**: ALL FOUR ANGLES FAIL. p^{1/3} is both worst-case AND average-case tight.

## Summary of closure

| Angle | Obstruction |
|-------|------------|
| Average-case distribution | Concentrated at p^{1/3}; Wesolowski's 10^5-sample data shows no exploitable tail |
| Compositional (k-way splits) | Birthday scaling: k>2 gives worse collision probability; 2-way is optimal |
| Type number structure | Circular: classifying type ≡ computing End(E) ≡ the original problem |
| Hecke eigenvalue navigation | Ramanujan expansion kills local-to-global information transfer |

## Why p^{1/3} is tight (independent structural facts)

1. **Object size**: Rank-3 Minkowski on traceless sublattice → minimum ~p^{1/3}
2. **Search cost**: Smooth-integer counting → table size ~p^{1/3+o(1)}
3. **Information**: Ramanujan mixing → no poly-time hint correlates with path distance

Breaking below p^{1/3} classically requires defeating ALL THREE simultaneously.

## The conditional impossibility argument

IF:
- The minimum of (P_O, Nrd/p) is concentrated at p^{1/3} (Wesolowski data: yes)
- The supersingular graph is Ramanujan (proven: Pizer 1990, Eichler)
- No poly-time invariant correlates with graph distance (consequence of mixing)

THEN: Any Deuring-transferred lattice method requires Ω(p^{1/3-o(1)}) operations.

## The only surviving theoretical direction

A framework that does NOT reduce to short-vector-finding in quaternion lattices.
No such framework is currently known. This is a genuine open problem.
