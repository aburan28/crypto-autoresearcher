# EigenX-v3 J4 robustness amendment: requested scope

Opening decision DEC-20261014-f6b6c7; BATCH-1f1d28; GOAL-SSI-2fa82a.
This is one explicitly authorized successor to NEXT-EIGENX-V3-J4-ROBUSTNESS.
All scientific, implementation, formalizer, benchmark and parameter-selection runs are zero.
The seven queued tasks do not imply that any work has run.

## Requirement-to-evidence contract

| Requested obligation | Producer artifact | Independent gate |
| --- | --- | --- |
| Choose ONE repair branch | formal-interface.yaml branch field and transform-proof.md justification | Sole-owner J4 |
| Formal adversarial-valid-ciphertext robustness game and exact query loss, preferred branch | formal-interface.yaml game; transform-proof.md loss | Independent query-by-query derivation |
| Pointwise alternative, only if actually justified | Explicit universal accepted-witness/all-coins theorem, not average honest correctness | Independent proof, zero errors only if proved |
| Exact byte-level strong-USS game | formal-interface.yaml | Same-components/new-proof control |
| Total parser, CRS validation, Verify and Dec | formal-interface.yaml algorithms | Exhaustive branch classification |
| Real two-component Dec / one-known-witness hybrid coupling | transform-proof.md | Independent coupling.md |
| Exact challenge-byte exclusion and controls | formal-interface.yaml and countermodels.md | J4 worked attacks |
| Quantifiers, assumptions, advantage and runtime accounting | formal-interface.yaml and transform-proof.md | Independent bound and composition comparison |
| Proof-search map and Lean decision | proof-search-map.yaml | Completeness/semantic gate |
| Source-linked report, editable diagram, SVG and PDF | Separate report task | Independent documentation review |
| Content custody, scoped disposition, additive history | Snapshot and ledger receipts | Git/hash verification |

## Exact formal-interface requirements

The producer must state exactly one chosen branch. Prefer ADVERSARIAL-VALID-CIPHERTEXT-ROBUSTNESS. No stronger pointwise claim may be assumed merely because the earlier packet mentioned ideal obfuscation. If choosing POINTWISE-CORRECTNESS, justify:
for every valid pp, every valid generated or externally embedded setup, every accepted R_CER witness W (including different bases), every allowed message m, and every explicit encryption coin string r for which Enc returns c, DX.Dec(ep,x,W,c)=m. State witness independence and exceptional key/setup handling. An unproved assumption must remain a named assumption; it is not a discharge.

For the preferred branch give the entire experiment, not just an epsilon symbol. Freeze the order of lambda, uniform adversary, setup/key distributions, accepted witnesses, auxiliary inputs, real/simulated CRS, challenge schedule, adaptive queries, and reduction selection. Define the actual mismatch between real Dec (both decryptions, bottom/length/equality checks) and SimDec_i (only the known witness). Explain whether robustness covers each fixed i/hybrid/key law, adaptive transcripts and simulated false challenge proofs. State adversary access and query limits. If using a one-selected-query robustness game, construct the exact query-index reduction and derive the q_D loss; if using a multi-query game, charge its actual global advantage without counting q_D twice. Account for inability to test the unknown witness in an executable reduction. Do not replace adaptive coverage with honest random-coin correctness. Show all admissible true-statement outputs, including both-bottom, one-bottom, wrong-length, unequal and equal plaintexts. Do not assume true equality alone ensures correct decryption.

Give bounded binary grammars with explicit tags, versions, field order, lengths/caps, integer encodings, full consumption and canonical re-encoding tests for pp, pk, sk, CRS, components and proofs. Primitive payloads may be opaque only if their bounded-domain parser/validator and total algorithms are explicitly formal parameters, with all necessary properties separately named. This does not instantiate those primitives or discharge global O2/O6. Reject truncated, nonminimal, duplicate, unknown-version, over-cap, trailing, cross-key, malformed CRS and invalid-witness strings with one bottom symbol. Bound allocations before calling primitives. Describe failure/abort for setup, simulated setup and challenge creation; parser or key failures cannot disappear by conditioning without an explicit probability term. Give total Verify/Dec semantics on every admitted byte string and both valid and invalid CRS.

Define strong-USS as an explicit byte-level oracle experiment: SimSetup outputs public CRS and private simulation state; adversary may obtain polynomially many adaptive simulated proofs including false statements; transcript records exact returned (statement_bytes,proof_bytes) pairs. Win requires a fresh pair, Verify=1 and the statement outside L_EQ, including the same previously simulated false statement with different proof bytes. Declare transcript membership, canonical bytes, number of simulation queries, input caps, auxiliary law, advantage, uniformity and reduction runtime. Ordinary soundness or a game excluding every simulated statement is insufficient. State separate real/simulated setup indistinguishability and adaptive ZK games. L_EQ binds exact full pk bytes and both components with explicit equal-message encryption coins.

Define IND-CCA2 with advantage abs(Pr[b'=b]-1/2), exact fixed message domain, classical oracle access and adversarial byte queries both before and after challenge. Exclude ONLY the exact complete challenge ciphertext bytes after challenge. Same component bytes with different proof bytes remain legal; alternate encodings, related ciphertexts and other-key bytes are not added to the exclusion set. Define prechallenge queries, challenge failure, replay, and malformed queries totally.

## Producer proof requirements

List every hybrid in order, its exact public-key/setup/challenge distribution, which witness is known, oracle algorithm and exclusion bytes. Couple real and simulated transcripts with the same coins until a named bad event. Cover every pre/postchallenge query and all parser/CRS/Verify/Dec branches. Separate false-equality accepting queries (strong-USS), true-equality decryption mismatches (robustness), setup/rejection failures and core distinguishability. The transition switching oracle behavior may require separate i=0 and i=1 charges and multiple robustness games; derive the exact coefficient and advantage-convention factors rather than guessing q_D times one epsilon. Account for queries during all relevant hybrids, query selection, aborts, probabilities, reduction uniformity, time, memory and simulation calls.

Keep K0, real EndRing law, EI-DXWE, relation-specific xO, ZK, strong-USS, parser/CRS assumptions and robustness distinct. State correctly directed reductions and quantify solver and adversary dependence. No new hardness, cost, novelty or quantum claim follows. A proof using a stronger new robustness assumption must say the implication is conditional and that this assumption is uninstantiated.

Include a proves-too-much object: a secure-looking core with a publicly selectable negligible subset of bad Enc coins. Honest uniform-coin error is negligible, but a true L_EQ proof on one bad and one normal same-message component yields real bottom and simulated plaintext. Exhibit the quantifiers and actual transcript. Also weaken the strong-USS freshness rule to exclude simulated statements and build a same-components/different-proof query demonstrating the missing guard. Compare canonical versus accepted alternate encodings; do not silently reject a proof variant merely to evade the game.

## Proof-search map and formalization

Before any further implementation or compute, record the four cheap audits: exact archived baseline syntax and its scoped J4 break; observation collision holding public syntax fixed while changing bad coins/witness behavior; explicit forall/exists order; method ceiling and nearby-object controls. Decompose parsing, language membership, robust response equality, false-proof rejection, query union/selection loss and hybrid assembly into single-responsibility lemmas.

Identify a precise smallest decision-changing Lean target with frozen definitions, assumptions, quantifiers, module/name, toolchain/dependencies and known-false control, OR state the exact missing definitions/library dependency that makes Lean premature and a checkable revisit trigger. An acceptable reason is that formal-interface byte grammar, adaptive oracle semantics, robustness event and hybrid probability spaces are not yet frozen; revisit after those exact definitions and independent semantic correspondence are supplied. Generic arithmetic union bounds alone cannot certify this transform. No Lean execution is authorized in this zero-run round.

## Review and outcome limits

Only TASK-20261014-82b3ef owns J4. Its fresh session receives formal-interface.yaml as the statement and parameters alone; that file must contain no proposed final aggregate bound, proof steps, verdict or producer attack analysis. It independently derives the query loss and coupling and writes review.yaml and coupling.md. Producer transform-proof.md, proof-search-map.yaml and countermodels.md remain blind. The Coordinator compares the independent derivation to those producer artifacts at composition; disagreement leaves the submitted amendment contradicted or inconclusive without changing the owner's verdict.

J4 holds can remove only the scoped transform contradiction and only under the exact reviewed conditional assumptions. It cannot promote EigenX-v3 or change J1/J2/J3/J5, K0, EI-DXWE/xO, R_CER verifier/saturation/necessity, NIZK instantiation, setup, cost, novelty, PQ/QROM, Category-5 or deployability status. O1/O2/O3/O4/O6 remain open; a scoped transform repair does not globally discharge O5. Breaks/inconclusive preserves the incomplete candidate. BATCH-3e1bfd and its endpoint-fiber verdicts are preserved separately. Stop after the bounded ledger archive and lane close; no automatic successor.
