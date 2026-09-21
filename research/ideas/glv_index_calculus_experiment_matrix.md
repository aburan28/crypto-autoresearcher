# GLV-aware index-calculus experiment matrix

Date: 2026-09-18
Scope: j = 0 prime-field curves with the order-3 GLV automorphism, with secp256k1 as the motivating deployed curve.
Status: design only. This file adds no result, approval, run, evidence record, or hypothesis transition.

## Why this batch exists

For a j = 0 curve E: y^2 = x^3 + b over F_p with p = 1 mod 3, let beta be a nontrivial cube root of unity and phi(x,y) = (beta*x,y). On a prime-order phi-stable subgroup G = <P>, phi acts as multiplication by a public eigenvalue lambda with lambda^2 + lambda + 1 = 0 mod N.

The repository already contains the exact informative-rank folding predecessor EXP-EQLA-164b34 and literature intake showing that endomorphism-invariant factor bases, orbit representatives, and eigenvalue-weighted relation coefficients are prior art. The experiments below therefore do not claim novelty for orbit quotienting itself. They ask whether the symmetry lowers charged cost at specific stages of the index-calculus pipeline.

## Wave 1 — direct GLV structure

| experiment | question | treatment | primary comparison |
|---|---|---|---|
| EXP-GLVFB-5f287d | Does a GLV-closed factor base reduce end-to-end relation plus sparse-LA cost after the density tradeoff is charged? | store one log unknown per phi-orbit and encode orientation by 1, lambda, lambda^2 | full GLV base vs same-size generic base vs generic quotient-size base |
| EXP-GLVCAN-468fb2 | How much repeated solver and storage work is eliminated by canonicalizing target and relation GLV orbits? | solve/store one canonical representative and carry orientation metadata | raw orbit-expanded pipeline vs canonical pipeline |
| EXP-GLVF-8dee36 | Can the C3 grading of the orbit-lifted j=0 Semaev system reduce actual F4/Macaulay work? | character-grade monomials by total GLV weight mod 3 and eliminate blockwise | identical system through vanilla F4, plus wrong-grading and generic-j controls |
| EXP-GLVINV-94a550 | Does quotienting the diagonal C3 action into invariant coordinates reduce PDP solver cost after degree/syzygy overhead? | derive and solve an exact quotient ideal; rational chart u_i=x_i/t, v=t^3 is only a candidate representation | raw orbit-lifted system vs quotient system with exact solution bijection checks |

## Wave 2 — integrate GLV into the rest of the pipeline

| experiment | question | treatment | primary comparison |
|---|---|---|---|
| EXP-GLVFF-3b7a1c | Can GLV character blocks and fixed-span elimination push the function-first H | L_V solver beyond its current scaling wall? | complete-orbit H, exact C3 coefficient action, blockwise fixed-span elimination, quotient-space rank updates | GLV function-first vs current function-first vs matched Semaev |
| EXP-GLVSAT-71d2e8 | Can exact prime-field SAT/bit-vector encodings exploit GLV without losing the cost advantage to modular arithmetic encoding? | validated prime-field CNF/SMT encoding plus GLV canonical constraints and GLV-aware branching | raw SAT vs GLV SAT vs matched F4 |
| EXP-GLVPRE-4c9f62 | Does GLV make more target-independent solver state reusable across many non-equivalent targets? | cache certified character blocks, row templates, and function-first fixed spans | cold vs generic preprocessing vs GLV preprocessing vs exact orbit cache |
| EXP-GLVLP-8a5d31 | Can GLV compress one/two-large-prime relation graphs without creating false cycles? | quotient LP vertices by C3 and attach Z/3 edge voltages; accept only zero-voltage cycles | full LP graph vs voltage quotient vs deliberately naive quotient |

## Shared rules

1. No experiment may count phi-transforms of one relation as independent relations. After orbit folding, transported rows are scalar multiples.
2. Semaev x-coordinate systems already quotient point negation. The additional symmetry under study is the order-3 GLV action, not a fresh factor six.
3. Every end-to-end comparison includes the relation-density cost, canonicalization/preprocessing cost, solver cost, sparse-linear-algebra cost, and memory.
4. Every comparison reports the applicable automorphism-adjusted Pollard-rho baseline from KN-TECH-018. None of these constant-order symmetries is treated as an exponent improvement.
5. Solver experiments also report against the maintained ICPERF boundary RQ-ICPERF-94c86e where the instance family is comparable. A smaller polynomial, matrix, factor base, CNF, quotient graph, or cache is not a win unless charged cost per verified relation or charged solve cost improves.
6. Toy runs use j = 0 curves with p = 1 mod 3 and a prime-order phi-stable subgroup. secp256k1 constants may be used for exact algebraic sanity checks, but no cryptographic-scale relation-collection claim follows from toy data.
7. Every relation accepted by an experiment is independently re-added on the curve and checked against its scalar/right-hand side.
8. Any quotient representation must prove exact reconstruction. Losing GLV orientation is an invalid compression, not a speedup.
9. Multi-target preprocessing reports cold, warm, setup, storage, and break-even target count separately. No free offline work.
10. SAT/UNSAT instances, successful/failed extractions, and liftable/nonliftable large-prime cycles are separate strata and may not be pooled into one favorable average.

## Existing records this batch must not duplicate

- EXP-EQLA-164b34: exact informative-rank folding and the B/3 unknown space.
- EXP-JINV-dd60d3: j = 0 has smaller S3 monomial support at toy scale, but the measured Groebner time did not improve because factor-base constraints dominated.
- RQ-EQJ-001 / KN-LIT-031: generic character/isotypic decomposition of equivariant polynomial systems.
- coordination/intake/cm-factor-base-20260905/source-context.md: retrieved prior art on endomorphism-invariant factor bases and orbit representatives.
- RQ-SATIC-1ae57a: binary/low-degree-extension SAT lane; it explicitly does not establish prime-field transfer.
- IDEA-20260731-012 / H-ICEX-87ad66: incumbent EC large-prime relation-graph formulation.
- KN-TECH-018: automorphism-adjusted rho baseline.
- RQ-ICPERF-94c86e and EXP-ICPERF-66fd51: maintained point-decomposition performance boundary.

## Priority order

### Tier 1 — cheap, decisive measurements

1. EXP-GLVFB-5f287d.
2. EXP-GLVCAN-468fb2.
3. EXP-GLVFF-3b7a1c.

These directly test whether the symmetry survives charged relation and function-first costs without requiring a new quotient ideal or prime-field SAT compiler.

### Tier 2 — solver structure

4. EXP-GLVF-8dee36.
5. EXP-GLVPRE-4c9f62.
6. EXP-GLVLP-8a5d31.

The F4 experiment establishes whether C3 character structure moves actual Macaulay work; preprocessing asks whether that structure is reusable across targets; the LP voltage graph tests the relation-combination stage independently of relation generation.

### Tier 3 — higher implementation risk

7. EXP-GLVINV-94a550.
8. EXP-GLVSAT-71d2e8.

EXP-GLVINV-94a550 runs only after the quotient map, saturation policy and inverse checks pass exhaustive truth. EXP-GLVSAT-71d2e8 runs only after two independent prime-field encoders agree with exhaustive curve truth. Favorable timings before those correctness gates have no scientific standing.

## Cross-experiment promotion gates

- If GLV helps only matrix size but not verified-relation cost, keep it as an engineering/memory result.
- If EXP-GLVFF-3b7a1c extends the largest completed bit rung, rerun the new rung against Semaev and the unmodified function-first baseline before increasing size again.
- If EXP-GLVF-8dee36 or EXP-GLVINV-94a550 appears to lower solving degree, replicate on at least three curve instances and a support-matched C3 null before discussing a scaling effect.
- If EXP-GLVPRE-4c9f62 reports a low break-even target count, repeat on fresh non-GLV-equivalent targets; exact orbit cache hits do not establish cross-target algebraic reuse.
- If EXP-GLVLP-8a5d31 appears to improve relation yield, replay the identical immutable edge stream. A benefit that disappears under replay came from harvesting, not graph quotienting.
- Any result apparently crossing the applicable automorphism-adjusted rho baseline requires independent adversarial review before interpretation.
