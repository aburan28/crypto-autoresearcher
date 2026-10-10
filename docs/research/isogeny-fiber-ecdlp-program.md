# Isogeny-fiber algebraic structure for ECDLP: systematic literature search and experimental program

Status: research hypothesis; no ECDLP speedup claimed. Owner: CryptoAutoResearcher research pipeline.

## Research question
Can the algebraic/Galois structure of fibers of separable isogenies reduce *total verified independent relation cost* in ECDLP index calculus compared with matched baselines, after accounting for isogeny construction, transfer, solver cost and failures?

## Mathematical invariants and guardrails
For a separable isogeny phi:E->E' of degree ell, a geometric fiber phi^{-1}(Q)=R+ker(phi) has ell points. For a rational Q, Frobenius acts on a cyclic prime-order kernel by i -> ai+b (mod ell), given pi(T)=[a]T and pi(R)=R+[b]T. The affine parameters depend on choices of R,T. A rational fiber need not contain ell rational points. For target subgroup order r coprime to ell, phi is injective on r-torsion, so fiber size does not reduce the ECDLP scalar search space. Distinguish geometric, rational and extension-field points. Verify all identities in Sage before claiming new effects.

## Exhaustive search tracks
1. Fiber polynomials, kernel polynomials, division polynomials, rational maps, Vélu/Kohel formulas, dual isogenies, preimage enumeration and root finding.
2. Galois modules, Frobenius affine actions, torsors, factorization of fiber polynomials, splitting fields and orbit compression.
3. Isogeny volcanoes, conductor strata, endomorphism orders, class groups, horizontal/ascending/descending edges, and large prime-degree isogenies.
4. Semaev summation polynomials, Gröbner F4/F5, degree of regularity, Hilbert series, SAT/XL, sparse elimination, and factor-base membership.
5. Cover and decomposition index calculus, Weil descent, Jacobian correspondences, low-genus covers and subgroup-preserving transfers.
6. Prior negative results and lower bounds: random self-reducibility, isogeny reductions, generic-group bounds, torsion restrictions, and preprocessing tradeoffs.
7. Related cryptanalytic ideas: orbit quotient factor bases, phase-aware Frobenius encoding, multi-fiber intersections, algebraic correspondences and elimination of kernel-index variables.

Search sources: arXiv, IACR ePrint, Google Scholar/Crossref, MathSciNet/zbMATH (where available), HAL, Journal of Number Theory, Mathematics of Computation, ANTS, ISSAC, EUROCRYPT, CRYPTO, ASIACRYPT, PQCrypto and authors' publication pages. Record DOI/arXiv/ePrint identifiers, version, publication date, authors, exact theorem, assumptions, proof status, code and reproducibility.

Example queries (run synonyms and citation expansion): 
- "isogeny fiber" polynomial factorization Frobenius elliptic curves
- elliptic isogeny preimages torsor Galois action
- kernel polynomial isogeny index calculus factor base
- isogeny volcano conductor discrete logarithm relation generation
- isogeny summation polynomial Gröbner degree regularity
- isogeny descent elliptic curve discrete logarithm cover decomposition
- fiber product correspondence elliptic curve index calculus

## Evidence table schema
paper_id, title, authors, year, venue, doi, arxiv_id, eprint_id, url, retrieved_at, research_track, theorem_statement, hypotheses, field_characteristic, curve_family, kernel_degree, computational_complexity, implementation_link, data_link, direct_fiber_relevance, ecdlp_relevance, negative_result, reproducibility_status, reviewer_notes, confidence, followup_ids.
Deduplicate by DOI then arXiv/ePrint then normalized title; maintain citations and source provenance. Do not fabricate references or benchmark measurements.

## Candidate hypotheses
H1: affine Frobenius action gives a compressed fiber representation that lowers total per-relation cost.
H2: fiber-polynomial factorization statistics correlate with factor-base relation yield after controlling for field, trace and solver settings.
H3: adding fiber constraints lowers F4/F5 degree of regularity or SAT search effort without exceeding preprocessing cost.
H4: conductor stratum predicts reproducible fiber-solving differences within an isogeny class.
H5: multiple compatible fibers/cover maps yield lower-cost decompositions than standard Semaev equations.
For each hypothesis store predicted mechanism, null hypothesis, falsification test, prerequisite proof, and measured cost.

## Experiment matrix
Families: ordinary binary Koblitz and non-Koblitz, ordinary prime fields, prime-field extensions. Check m=31,51,53,83 when mathematically valid; use smaller toy fields first for exhaustive ground truth. Degree choices ell=3,5,7,11 and larger primes only when certified maps exist. Compare same trace/order, varying conductor; matched same-level controls; isomorphic-model negative controls. Avoid degree-2 separability assumptions in characteristic 2.

Baselines: conventional factor base + Semaev F4/F5; SAT variant; Frobenius-orbit factor base; canonical lifted r-torsion points; rho control. Treatment: fiber coset encoding; orbit-compressed fiber equations; elimination with kernel-index variables; multiple-fiber constraints. Same random seeds, target sets, rank goals, time budgets, solver versions, CPU/GPU pinning and memory caps.

Measurements: map construction and evaluation, fiber polynomial construction, factorization, orbit computation, factor-base generation, failed targets, solver timeouts, duplicate/dependent relations, verified independent relations, rank progression, LA, final ECDLP verification, peak RAM and wall-clock. Primary endpoint = total wall-clock / newly independent verified relation; secondary endpoint = total end-to-end solved instance cost. Bootstrap paired log-cost ratios with confidence intervals; report censored runs. Require >=2x improvement on larger valid instances, not only microbenchmarks.

## Implementation artifacts and acceptance criteria
- docs/research/isogeny-fiber-literature.csv (bibliographic evidence with checked links)
- docs/research/isogeny-fiber-evidence.md (annotated review, negative results, novelty matrix)
- schemas/isogeny_fiber_experiment.schema.json (strict inputs, outputs, provenance)
- tools/isogeny_fiber_sweep (Sage reference generator and reproducible CLI)
- benchmarks/isogeny_fiber (paired baseline/treatment harness)
- tests: small-field fiber cardinality, affine Frobenius action, dual identity, rationality, kernel intersection, relation verification, no data leakage.
- reports: reproducibility manifests, plots, per-family summary, counterexamples, hypotheses accepted/rejected.

Milestones: (1) collect and verify >=50 directly or indirectly relevant papers, with backward/forward citation snowballing and explicit search log; (2) proof-checked toy reference cases; (3) baseline and treatment parity; (4) paired small/medium benchmark; (5) generalization across families; (6) paper-ready claims only after independent reproduction.

## Paper outline
Introduction and prior art; algebraic structure of fibers; Frobenius affine-action theorem and limitations (known mathematics unless novelty proven); algorithms; complexity model; experimental methodology; results; negative findings; isogeny-transfer analysis; reproducibility appendix.

## Immediate research tasks
- Perform systematic literature review and fill evidence table with verified references.
- Identify strongest known results and closest published approaches; produce novelty/overlap assessment before claiming a new paper.
- Build Sage toy examples and prove/verify affine-action equations.
- Design factor-base fiber encoding and compare against canonical lift control.
- Report whether any advantage survives end-to-end accounting.
