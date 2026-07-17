# Research Ledger

## Claim boundary

This ledger covers authorized toy experiments on generated prime-field curves. No entry is a deployed-key result, an exponent improvement, or a claim that prime-field ECDLP is exhausted.

## Open frontier questions

- [ ] Can a coordinate-defined factor base preserve near-random exact `m`-fold support while compressing a recursive split compiler?
- [ ] Can a fixed-curve coordinate relation compiler beat the generic preprocessing frontier after advice bytes, bandwidth, success probability, and all offline operations are charged?
- [ ] If a preflight family passes, does its relation matrix retain rank and admit an individual-log descent?
- [ ] Can the expansion/compression objective be given a coordinate-specific structured-group theorem or counterexample?
- [ ] Does a canonical recursive factor-base witness forest admit a valid structured-generic partial operation, and what constrained-label fraction and witness density does it induce?

## Active hypotheses

| ID | Hypothesis | Status | Owner | Next action |
|---|---|---|---|---|
| H-ECDLP-RECURSIVE-001 | A coordinate factor base retains at least `0.8x` random exact support while reducing matched-random functional-advice-byte `S*T^2/(epsilon*q)` to at most `0.8x`. | OBSERVATION, REVISE INTERPRETATION | coordinator | Preserve runs; transfer only the coverage signal into a repaired null-calibration successor. |
| H-ECDLP-RECURSIVE-002 | A coordinate family passes an exploratory eight-term finite-null and exact uniform-order frontier gate on distinct-field non-special curves. | HYPOTHESIS, v1 REVISE, v2 REVISE, v3 review required | executor and red team | Independently audit the v3 lock/receipt protocol; do not launch before third-audit GO and final lock/commit GO. |
| SGCP-EMBED-001 | A canonical recursive EC witness forest can instantiate the structured generic-group partial operation with nonvacuous constrained-label density. | OPEN, contract frozen | theory and red team | Implement the downward-closed injective prime-multiset label builder/verifier and run the 5-bit control preflight. |
| TH-ECDLP-SPLIT-001 | Useful factor bases may combine high final additive expansion with exact intermediate compression. | CONJECTURE | theory and red team | Formalize necessary expansion/compression inequalities and search for counterexamples. |
| TH-ECDLP-MAP-UNION-001 | Unions of compositional rational-map images may improve recursive support geometry without exceptional curves. | CONJECTURE | algorithm designer | Test only after the recursive preflight establishes a sound measurement surface. |

## Negative results

| ID | Ruled out | Scope | Evidence | Reusable lesson |
|---|---|---|---|---|
| EXP-ECDLP-ENERGY-001-V2 | Promotion of the frozen x-interval, square-map, or rational-union configurations. | Three generated toy curves, `B in {8,12}`, five-term sign-complete sums. Family-level behavior remains open. | Exact supports were random/x-interval/rational-union `456,456,2668`; square map `376,400,2622`; scalar progression `41,41,61`. | Ordinary multiset occupancy misses inverse-pair cancellations; use exact signed support and a construction-matched random-x control. |
| EXP-ECDLP-ENERGY-001-COST | Treating exhaustive representation census or counter-only storage as an online compiler cost. | Original frozen implementation only. | Independent red-team audit and interpretation amendment. | Stop at the first witness, retain functional witnesses, and separate diagnostic expansion from compiler work. |
| EXP-ECDLP-RECURSIVE-001-COMPRESSION | Promotion of split-compression for the frozen passing rows. | Sign-complete `m=8`, 12-16 bit run only; family-level coverage remains open. | Every passing row had generic-maximum four-term support and advice-byte ratio near one. | Separate expansion significance from compiler compression; do not let online coverage masquerade as smaller advice. |
| EXP-ECDLP-RECURSIVE-002-PREFLIGHT-V1 | Approval of the first successor protocol at commit `96fcc1b`. | Protocol/execution layer only; no canonical mathematical evidence run occurred. | Independent audit found unenforced command/budgets, nonbinding positive control, aggregate-only order checks, and uncharged coordinate arithmetic. | A correct arithmetic core is insufficient unless execution, controls, resource limits, and interpretation are mechanically bound. |
| EXP-ECDLP-RECURSIVE-002-PREFLIGHT-V2 | Approval of execution protocol v2 at commit `878acef`. | Harness provenance/resource layer only; arithmetic protocol v2 survived and no canonical run occurred. | Independent audit found mutable plan trust, forgeable predecessor provenance, descendant escape, absent post-run checks, and same-inode aliases. | External approval, exact Git transitions, strict receipts, post-run rechecks, and file identity belong in the evidence boundary. |
| EXP-ECDLP-RECURSIVE-002-V3A-DESCENDANTS | Claim that process-table sampling observes every detached descendant. | Twelve fast new-session children on the recorded macOS/Python runner preflight. | All 12 escaped observation and were reported quiescent before their 0.4-second sleep ended. | Sampling is defense in depth, not containment; frozen locked runs now forbid child creation with non-root `RLIMIT_NPROC=0`. |

## Positive signals

| ID | Signal | Parameter regime | Evidence | Next validation |
|---|---|---|---|---|
| CTRL-ECDLP-ENERGY-001 | Scalar progression compresses intermediate/final support as expected. | Same frozen toy instances. | Exact support `41,41,61`, well below random. | Retain as a positive compression/negative expansion control. |
| INFRA-ECDLP-RECURSIVE-001 | Generator and independent verifier exactly replay source hashes, curves, factor bases, supports, split witnesses, counters, rho trials, and promotion logic. | Six canonical toy instances and 216 configurations. | Both immutable runs completed valid; generator/verifier raw hashes are recorded in evidence. | Reuse the verification pattern while adding anomalous/special-curve rejection. |
| SIG-ECDLP-RECURSIVE-001 | Three coordinate families showed verified sign-complete `m=8` coverage/first-witness gate crossings. | Frozen 12-16 bit instances, including one anomalous curve and one draw per null. | Counts `4,3,3`, but no family passed three instances against both random controls. | Estimate null percentiles and remove order/special-curve confounds before family promotion. |

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
| Structured generic groups | Corrigan-Gibbs-Kogan preprocessing bounds; Corrigan-Gibbs-Henzinger-Wu structured model | Fixed-generator `ST^2` is tight under random generic encodings; the structured bound adds a `delta*T` escape term. | A unary predicate `L(x)=0` does not itself define the model's partial operation or `delta`; construct or refute a valid EC witness embedding. |
| Split joins | 3SUM-Indexing and Dinur-Golovnev application-specific compiler | A materialized `4F + 4F` target query is an abelian-group 3SUM-Indexing instance. | Test whether integer subfunction decomposition/hashing and witness recovery transfer to EC groups without hiding source storage. |

## Durable artifacts

- `experiments/EXP-ECDLP-ENERGY-001/interpretation-amendment-v2.md`
- `experiments/EXP-ECDLP-ENERGY-001/red-team-audit.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/contract.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/result-red-team.md`
- `experiments/EXP-ECDLP-RECURSIVE-001/evidence.json`
- `experiments/EXP-ECDLP-RECURSIVE-001/decision.json`
- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-audit-v1.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/revision-response-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-audit-v2.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/revision-response-v3.md`
- `experiments/EXP-ECDLP-RECURSIVE-002/pre-run-adversarial-probe-v3a.md`
- `notes/sgcp_embed_001_contract_20260717.md`
- `notes/ecdlp_recursive_expansion_literature_map_20260717.md`
- `notes/structured_group_coordinate_predicates_literature_20260717.md`
- `notes/ecdlp_unordered_occupancy_split_support_theory_20260717.md`
- `notes/coordinate_decomposition_theories_20260717.md`
