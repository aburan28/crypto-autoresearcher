# Paper intake → experiment pipeline

## Goal
Continuously discover newly released cryptography, computational number theory, algebraic geometry, finite-field, algorithms, complexity, SAT/Gröbner, GPU/ASIC, isogeny/endomorphism, and discrete-log research; deduplicate it; assess applicability to active research; and turn promising results into reproducible experiments.

## Pipeline
1. **Discover** — poll arXiv and other configured scholarly feeds by category/query. Store source URL, identifier, version, timestamps, authors, title, abstract, and retrieval provenance.
2. **Deduplicate/version** — canonicalize DOI/arXiv IDs and distinguish new papers from revisions.
3. **Triage** — score relevance against active research capabilities and bottlenecks, not keywords alone.
4. **Distill** — extract theorem/algorithm, assumptions, asymptotics, constants/caveats, required primitives, implementation clues, and claimed benchmarks. Never promote abstract-only claims as verified.
5. **Reduction matching** — compare the paper's accelerated primitive against a machine-readable graph of expensive kernels in active experiments. Search *backward* through reductions.
6. **Experiment proposal** — emit a bounded experiment manifest: hypothesis, baseline, changed primitive, datasets/curve IDs, metrics, stop conditions, verification, and expected failure modes.
7. **Execute** — enqueue only through existing experiment runners; preserve control runs and reproducibility metadata.
8. **Evaluate** — compare total cost, including preprocessing, misses/timeouts, duplicates, verification, and downstream rank/usefulness.
9. **Knowledge** — write positive and negative results back to the knowledge store with paper/version and experiment provenance.
10. **Escalate** — surface high-value results for review; never silently call a microbenchmark a cryptanalytic speedup.

## Priority topics
- ECDLP/index calculus, point decomposition, summation polynomials
- finite-field arithmetic and representation changes
- elliptic/hyperelliptic curves, Jacobians, covers, Weil descent
- endomorphisms, CM, isogenies and automorphisms
- Gröbner/F4/F5, SAT/FES, sparse linear algebra/Macaulay
- collision/search algorithms and time-memory tradeoffs
- sparse/rectangular matrix multiplication and fine-grained algorithms
- GPU/FPGA/ASIC arithmetic and systems work
- PQC cryptanalysis and reductions

## Relevance score
Score separately:
- semantic relevance to an active hypothesis;
- primitive/reduction match;
- plausible asymptotic effect;
- plausible practical effect;
- implementation readiness;
- evidence quality;
- novelty versus knowledge store.

Do not collapse these into a single opaque LLM confidence.

## Experiment manifest
Each candidate should record:
`paper_id`, `paper_version`, `retrieved_at`, `active_problem`, `matched_primitive`, `reduction_path`, `hypothesis`, `baseline`, `treatment`, `parameters`, `metrics`, `verification`, `budget`, `stop_conditions`, `artifacts`.

## Agent rules
- Search for algorithmic consequences, not merely papers mentioning cryptography.
- A theorem can matter through an indirect reduction.
- Separate proven applicability, plausible applicability, and analogy.
- Revisions must trigger re-triage when technical content changes.
- Negative experiments are durable knowledge.
- Never weaken experiment requirements to manufacture a win.
- Prefer small valid controls before expensive scaling.
