# TASK-20260905-282872 -- producer report (SAT/SMT relation finding, RQ-ECDLP-f0a7b0)

> Provenance note (Coordinator, 2026-09-05): the idea-generator subagent's `Write` of this file was
> refused by the runtime ("Subagents should return findings as text"), so the producer returned the
> report in its final message and the Coordinator transcribed it here verbatim. Nothing below was
> altered, added or removed by the Coordinator; `ideas.yaml` and `sources.json` were written by the
> producer directly. The producer's own words follow.

## Deliverables written

- `/home/user/crypto-autoresearcher/coordination/ecdlp-ideas-20260905-23ec69/tasks/TASK-20260905-282872/ideas.yaml` — six complete records (Coordinator's mid-run update applied: GOAL-SATIC-c49b77 in every `goal_ids` with an applicability sentence, RQ-SATIC-1ae57a in every `question_ids`, BATCH-1a527c named in each novelty screen with the exact difference).
- `/home/user/crypto-autoresearcher/coordination/ecdlp-ideas-20260905-23ec69/tasks/TASK-20260905-282872/sources.json` — every local record and external retrieval with provenance, including the GOAL-SATIC files actually read.
- `report.md` — **NOT written**: the harness refused the Write ("Subagents should return findings as text"). Its full content is below; the Coordinator will need to file it from this message if the completion gate requires the file.

## Ideas (assigned ids, in order; IDEA-20260905-1226bf unused)

| id | one-line title | stage / target | priority |
|---|---|---|---|
| IDEA-20260905-24d827 | Prime-field SATIC ceiling analogue: bit-blasted and finite-field-theory CDCL(T) at ms − log2 m! bits; an IPASIR-UP root-finding propagator at (m−1)s + m − 1 bits; nothing below (m−1)s | decomposition / exponent (ceiling) | high |
| IDEA-20260905-a6f98e | Two certificates of non-decomposability: LRAT length = leaf count (no compression) vs Nullstellensatz degree D_NS by exact rank; proof-size dichotomy as the implementation-free SAT-vs-Groebner number | certification / certifiability | high |
| IDEA-20260905-3de445 | Learned clauses as elimination-ideal elements: block-support histogram of CDCL proof traces predicted full; D_elim(m−1, e) above tested degrees | decomposition + algebraic step / exponent (obstruction) | high |
| IDEA-20260905-a94b5f | Automorphism census of the encoded system: exactly S_m, torsion translation syntactically invisible | factor-base design + decomposition / constant (bits of |G|) | medium |
| IDEA-20260905-79112a | Incremental assumption-based multi-target solving amortises nothing; batched enumeration row 2^n/m! at memory m!·2^l dominates (factor m·m! below 96c4f3's row) | decomposition / amortised constant | medium |
| IDEA-20260905-3993c3 | Projected model counting for coverage: hashed calls cost ≥ ceiling; dominated ≥100× by enumeration; conservation as calibrator | yield measurement / fidelity (priced negative) | low |

## Recommended first test

**IDEA-20260905-3de445, Stage 1 at l = 3, m = 3 then Stage 2 at l = 4..6.** Cadical/kissat are present, proof traces are native output, the GF(2) rank engine exists (EXP-DREG-001), so the block-support histogram plus the brute-force elimination ideal costs seconds and separates three explanations at once (nothing narrow derivable / solver misses derivable structure / solver finds structure the algebra hides). The known-false object (l redundant cross-block linear relations) must show narrow clauses and D_elim = 1 before any null is reported; N0 must collide. a6f98e Stage 1 reads the same proof trace and should share the session.

## Report content (honest accounting, inventor-protocol §5)

**Directions enumerated / three-axis scores (new, testable, survival; 0–3):** (1) prime-field SMT 2/3/2 → 24d827; (4) proof-producing UNSAT 3/3/2 → a6f98e; (7) learned clauses → Macaulay 3/3/2 → 3de445; (5) symmetry detection 2/3/1 → a94b5f; (2) incremental across targets 1/3/1 → 79112a; (3) model counting 1/3/0 → 3993c3 (priced negative); (6) cube-and-conquer 0/3/1 — not filed: refuted-cube count is a truncation of 3c7a91's complete conflict-depth histogram (repackaging under §2); (8) SAT/ILP/MaxSAT over factor-base choice 1/1/0 — not filed: KN-FIND-007 refutes any mean-yield proxy on sight; admissible proxies (|Aut|, coverage) are outputs of a94b5f/3993c3, so it is an open successor; (9) PB encodings 0/2/1 — folded into 24d827's (BV) arm (a mod-p PB form is bit-blasting in another syntax); (10) point-domain CSP with group-law propagator 1/3/1 — folded into 24d827 as arm (UP), its exact node count being the floor/known-ceiling control.

**Objects:** depth-indexed refutation count (F_p); (L_res, D_NS) certificate pair; block-support histogram and D_elim; syntactic automorphism group; assumption-dependence histogram; hash-level cost curve; plus the batched-relation row (arithmetic).

**Depth of verified structure:** nothing verified (proposal-only). Derivation-level content new to the corpus: (i) batched enumeration of all m-multisets against a hash set of T targets costs C(|B|+m−1, m)+T = 2^n/m! at l = n/m, a factor m·m! (18 at m = 3) below 96c4f3's m·2^n at memory m!·2^l, still ≈ 2^{n/2}/(0.886·m!) above rho; rests on KN-FIND-007's double count and 96c4f3's Poisson half; very likely folklore. (ii) D_NS ≥ d_ff on the digit system from e1e38b. (iii) the elimination ideal I ∩ F_2[blocks 1..m−1] contains affine elements by dimension count, so the obstruction is derivability (D_elim), not existence.

**dominated_by (session):** every proposal is dominated as an algorithm by Pollard rho / vOW (0.886·N^{1/2}, poly memory); on the pdp step by the (m−1)-fold enumeration (96c4f3; arm (UP) of 24d827 ties it), target-keyed MITM, the 2^{2l}-table row, BSGS, kangaroo, S·T² = N, Groebner F4 (reported; dominated by enumeration under da1428's null), generic CDCL, crossbred/hybrid (fc5e3e, da1428, dcf857); on relation collection by the batched row derived in 79112a. All rows checked; no `null`. Certification/measurement deliverables carry `n/a (no result claimed)` on that axis.

**sota_delta (session):** zero on every attack axis. Quantified deliverables if predictions hold: prime-field ceiling ms − log2 m! bits with band and the factor 2^{s−m+1}/m (21.3× at s = 8, m = 3) to the propagator tier; every UNSAT verdict certified, L_res = leaves ± 20 %, per-cell sign of log2 Ncols(ml, D_NS) − (ml − log2 m!); zero narrow learned clauses and a D_elim table; syntactic symmetry budget exactly log2 m!; SAT amortisation 0 ± 5 % and the corrected row 2^n/m!; flat hash-level curve and ≥ 100× counting disadvantage.

**Enumerated closures (with mechanism):** cube-and-conquer — repackaging of the complete conflict-depth histogram; mean-yield factor-base optimisation — closed by conservation, successors named (|Aut|, coverage); PB encodings — syntax variant of bit-blasting. All scoped to tested encodings and `unverified` until run.

**Open directions:** UNSAT-side Groebner filter before search if a6f98e outcome (I) gives D_NS ≪ ml; a propagator using any exhibited elimination element (3de445); FHJRV torsion-invariant re-modelling as a SAT model for the m − 1 bits a94b5f predicts are syntactically invisible; a factor-base optimiser over log2|Aut| + log2 coverage-ratio once a94b5f validates the proxy; VeriPB proof logging for XOR-aware solvers.

**Ranking (information gain vs cost):** a6f98e > 3de445 > 24d827 > a94b5f > 79112a > 3993c3, for the reasons in the table and the first-test paragraph.

## Constraints not satisfied

1. **`report.md` could not be written** — the harness blocked the Write; content is above.
2. **GOAL-SATIC batch files named by the Coordinator do not exist**: `.../BATCH-1a527c/intake.md` and `benchmark-obligations.json` are declared artifacts of TASK-20260905-53d333 but are absent from the tree (also under `tasks/TASK-20260905-53d333/`); I cited the goal record, `contracts/design-intake.json` and `launch.md` instead and said so in every affected novelty screen and in `sources.json`.
3. Several externals reached only at abstract or search-snippet level (BreakID and cube-and-conquer PDFs unreadable; Gocht–Nordström, CaDiCaL-LRAT, IPASIR, LPAR-24 snippets); marked as such and load-bearing on nothing. cvc5's finite-field procedure internals not read (treated as H3 in 24d827).
4. `H-DREG-152cff` read to line 120 only; `KN-LIT-7607` cited through 84cdb7's verified reading, not reopened.
5. `search_knowledge` unavailable throughout; all six records are `novelty_status: unverified`.
