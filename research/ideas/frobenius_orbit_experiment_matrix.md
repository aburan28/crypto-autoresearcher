# Frobenius orbit experiment matrix

Companion execution matrix for the symmetry-aware ECDLP research slate.

## Immediate experiments

| Experiment | Question | Baseline | Primary metric | Kill condition |
| --- | --- | --- | --- | --- |
| EXP-FROB-ORBIT-1 | Do canonical-orbit or representative+index coordinates make decomposition cheaper? | RAW chained-S3/SAT | seconds per independent usable relation | no scaling improvement after dependency normalization |
| EXP-FROB-ORBIT-2 | Can normal-basis cyclic Frobenius structure compress solver constraints? | ordinary generated constraints | solver wall time and memory | clause/gate shrink without solver-time gain |
| EXP-FROB-ORBIT-3 | Which canonical orbit representative is cheapest and most stable? | no canonicalization | canonicalization overhead + downstream throughput | overhead is material relative to relation generation |
| EXP-FROB-ORBIT-4 | How many nominal orbit-derived relations are actually independent? | raw relation count | incremental rank per accepted relation | multiplicity collapses to scalar/Frobenius duplicates |
| EXP-FROB-FB-1 | Which nonlinear Frobenius-stable predicates maximize useful relation yield? | current factor base | cost per independent relation | decomposition cost outruns orbit/matrix saving |
| EXP-FROB-FB-2 | Does factor-base geometry matter at fixed cardinality? | matched-size conventional base | solve time and relation success | no significant difference across scaling ladder |
| EXP-FROB-SYM-1 | Does quotienting by Frobenius/permutation improve scaling? | raw coordinates | fitted growth of time/memory | exponent/growth unchanged or worse |
| EXP-TORUS-1 | Can alternate algebraic-group representations produce better factor bases? | current field representation | end-to-end projected work | setup/conversion erases gains |
| EXP-BRAUER-1 | Do local/global signatures expose scalar-class information? | randomized labels | held-out scalar-class advantage | signal disappears under controls |
| EXP-REP-1 | Are there non-index-calculus scalar observables? | planted/null observables | held-out deterministic dependency | correlation cannot be converted to exact relation |

## Required instrumentation

The Koblitz relation path should emit canonical orbit ID, orbit size, Frobenius exponent, normalized row hash, scalar/Frobenius dependency class, and incremental matrix-rank delta. Solver runs should emit variable/constraint counts, preprocessing time, solve time, memory high-water mark, timeout status, and decomposition verification outcome.

## Scaling ladder

Start at toy sizes where all arms can be exhaustively verified, then increase field size until at least one arm becomes timeout-censored. Use identical target seeds and budgets across arms. Report censored results rather than dropping them. Do not extrapolate a security claim from a short toy ladder.

## Comparison rule

Rank candidates using end-to-end projected work against the best applicable Pollard-rho baseline for that curve family, including known automorphism/Frobenius acceleration. A candidate does not advance merely because it shrinks a factor base, relation matrix, SAT instance, or Groebner system.

## Promotion gate

A candidate advances only if it:

1. beats the current representation/factor-base baseline on held-out toy parameters;
2. survives relation-independence normalization;
3. survives isomorphism/coordinate controls when applicable;
4. shows an identifiable mechanism for improved scaling rather than only a constant toy-size effect;
5. passes independent cost-model review.

No experiment in this matrix is itself evidence of an ECDLP break.