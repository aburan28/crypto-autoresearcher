# Research Ledger

## Claim boundary

This ledger covers authorized toy experiments on generated prime-field curves. No entry is a deployed-key result, an exponent improvement, or a claim that prime-field ECDLP is exhausted.

## Open frontier questions

- [ ] Can a coordinate-defined factor base preserve near-random exact `m`-fold support while compressing a recursive split compiler?
- [ ] Can a fixed-curve coordinate relation compiler beat the generic preprocessing frontier after advice bytes, bandwidth, success probability, and all offline operations are charged?
- [ ] If a preflight family passes, does its relation matrix retain rank and admit an individual-log descent?
- [ ] Can the expansion/compression objective be given a coordinate-specific structured-group theorem or counterexample?

## Active hypotheses

| ID | Hypothesis | Status | Owner | Next action |
|---|---|---|---|---|
| H-ECDLP-RECURSIVE-001 | A coordinate factor base retains at least `0.8x` random exact support while reducing matched-random functional-advice-byte `S*T^2/(epsilon*q)` to at most `0.8x`. | HYPOTHESIS, v1 REVISE, v2 review required | executor | Fresh independent audit of v2 revision closure. |
| TH-ECDLP-SPLIT-001 | Useful factor bases may combine high final additive expansion with exact intermediate compression. | CONJECTURE | theory and red team | Formalize necessary expansion/compression inequalities and search for counterexamples. |
| TH-ECDLP-MAP-UNION-001 | Unions of compositional rational-map images may improve recursive support geometry without exceptional curves. | CONJECTURE | algorithm designer | Test only after the recursive preflight establishes a sound measurement surface. |

## Negative results

| ID | Ruled out | Scope | Evidence | Reusable lesson |
|---|---|---|---|---|
| EXP-ECDLP-ENERGY-001-V2 | Promotion of the frozen x-interval, square-map, or rational-union configurations. | Three generated toy curves, `B in {8,12}`, five-term sign-complete sums. Family-level behavior remains open. | Exact supports were random/x-interval/rational-union `456,456,2668`; square map `376,400,2622`; scalar progression `41,41,61`. | Ordinary multiset occupancy misses inverse-pair cancellations; use exact signed support and a construction-matched random-x control. |
| EXP-ECDLP-ENERGY-001-COST | Treating exhaustive representation census or counter-only storage as an online compiler cost. | Original frozen implementation only. | Independent red-team audit and interpretation amendment. | Stop at the first witness, retain functional witnesses, and separate diagnostic expansion from compiler work. |

## Positive signals

| ID | Signal | Parameter regime | Evidence | Next validation |
|---|---|---|---|---|
| CTRL-ECDLP-ENERGY-001 | Scalar progression compresses intermediate/final support as expected. | Same frozen toy instances. | Exact support `41,41,61`, well below random. | Retain as a positive compression/negative expansion control. |
| INFRA-ECDLP-RECURSIVE-001 | Generator and independent verifier exactly replay source hashes, curves, factor bases, supports, split witnesses, counters, rho trials, and promotion logic. | Reduced noncanonical test config. | Eight repository tests pass; verifier self-test passes 18 hash, parser, mutation, gate, and replay tests. | Fresh pre-run review, then canonical immutable generator and verifier runs if approved. |

## Baselines

| Algorithm | Family | Time | Memory | Notes |
|---|---:|---:|---:|---|
| Pollard rho | Generic prime-order group | `Theta(sqrt(q))` expected group operations | Small | Measured on every experiment curve as an arithmetic scale; not yet an end-to-end comparison with the compiler. |
| BSGS | Generic prime-order group | `Theta(sqrt(q))` group operations | `Theta(sqrt(q))` points | Reference time-memory baseline; not claimed as the online fixed-curve frontier. |
| Split support compiler | Fixed curve, coordinate-specific | Measured offline support construction plus first-witness online scan | Functional witness maps measured by deep bytes | Candidate preflight only; rank, relation collection, linear algebra, and descent are absent. |

## Literature map

| Topic | Closest work | Claim | Gap |
|---|---|---|---|
| Generic lower bounds | Shoup-style generic-group bounds and preprocessing tradeoffs | Restrict generic algorithms, not coordinate-specific non-generic structure. | Instantiate a useful barrier or loophole for actual elliptic-coordinate predicates and recursive circuits. |
| EC index calculus | Semaev, Gaudry, Diem, Joux-Vitse, Faugere-Perret-Petit-Renault | Point decomposition can be encoded algebraically, with known solver and density bottlenecks. | A compiled batch decomposition sieve that is not generic Groebner elimination. |
| Rational-map factor bases | Petit, Kosters, and Messeng line of work | Rational-map factor bases are established, so the family itself is not novel. | Measure exact recursive expansion, witness-bearing advice, and online cost under matched controls. |
| Structured generic groups | Recent structured-group models | Give high-level density constraints. | Concrete additive-combinatorial expansion results for `L(x)=0`, recursive addition laws, and batch decomposition. |

## Durable artifacts

- `experiments/EXP-ECDLP-ENERGY-001/interpretation-amendment-v2.md`
- `experiments/EXP-ECDLP-ENERGY-001/red-team-audit.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `notes/ecdlp_recursive_expansion_literature_map_20260717.md`
- `notes/ecdlp_unordered_occupancy_split_support_theory_20260717.md`
- `notes/coordinate_decomposition_theories_20260717.md`
