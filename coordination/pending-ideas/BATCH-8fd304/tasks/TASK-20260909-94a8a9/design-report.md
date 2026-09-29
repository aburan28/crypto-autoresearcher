# Bounded-fill relation design: concrete revision required

This is **authoring revision2** under the published pre-archive correction at `coordination/pending-ideas/BATCH-8fd304/admission/fill-lifecycle-authoring-correction-20260909.json`. The complete first-delivery files remain preserved losslessly in `coordination/pending-ideas/BATCH-8fd304/admission/fill-first-design-delivery-20260909.json.gz` (gzip SHA256 `7cac9e1a12b7369b74cb161c4bb0ac13012f62d48e94bb47c622accb800c25c9`). The parent observed a missing direct review-to-ledger route for the implementation/formal QA round. This revision changes only that unadmitted lifecycle and related metadata/hashes; it changes no scientific definition, count, control or determinant-source disposition.

TASK-20260909-94a8a9 prepared H-RELN-dee9ec and EXP-RELN-f3a133 with the full source ladder and a complete prospective lifecycle. DEC-20260909-40f3ad records **revise**. The experiment remains **review_required**, with **approved_by: null**. No implementation, formal or scientific stage is admitted by these files.

The exact source IDEA-20260906-f9f8c8 and candidate question RQ-RELN-b70054 retain the condition: “A cycle with coefficients whose determinant vanishes mod N must not yield an independent base relation.” The square matrix is not identified. The specification preserves this literal condition and records a material clarification prerequisite. It does not silently replace the condition or reject the underlying bounded-fill mechanism.

The design is bound to the actual published intake snapshot 91ae3c20f3f56bd9bfc5a46ff47a0e5a801659bd. The adopted card and matching epoch-1 claim were read directly; the parent supplied admission83cf9dbe72, claim publication0adcd42a26 and PR1072. The current parent-generated dispatch plan has all 11 gates true and this designer live. These are administrative observations, not scientific evidence.

## What the worked controls resolve

For original relation rows M=[A|B], A contains every auxiliary column and B contains every base column plus the known-G coordinate, fixed to1. A valid cancellation lambda satisfies lambda*A=0 and emits lambda*B, carrying its full original-row multiplier witness. Useful rank is the exact increase after reduction against previously accepted base constraints, with coefficient/augmented-known-column consistency checked. A graph cycle, a kernel dimension and an independent projected constraint are separate quantities.

The following are manual proposed controls over F_11, not executed or independently validated results. Take known cyclic labels G=1, L1=4, L2=5, D1=2 and D2=3.

- With A=[[1,1],[1,1]] and B=[[1,0,0],[0,1,-1]], the two original group equations are4+5+2=11 and4+5+3-1=11. The cancellation (1,-1) produces (1,-1,1), a nonzero projected base constraint when no prior constraint already contains it. The singular auxiliary determinant alone does not force zero projected rank.
- Keeping the same A but duplicating the first B row makes the same cancellation produce zero. Keeping the positive projected row in the prior rowspace instead makes its new rank increment zero. Every duplicated/discarded acquisition still costs work.
- Replacing the second A row by(1,2) keeps the same support graph but makes its determinant1 over F_11. The left cancellation kernel is then zero. This is a general modular/intermediate-row control, not a claimed raw arity-3 tuple.

A separately checked additive clarification must identify the intended determinant and the premise that makes its control valid. That clarification and independent protocol review are required before approval. The current seven-file task creates no amendment, no independently validated counterexample and no adverse scientific conclusion.

## Complete frozen scope

| Item | Frozen value |
|---|---|
| Prime-order size rungs | Every integer b=12,13,14,15,16,17,18,19,20 |
| Curves | One deterministic certified ordinary prime-order curve per rung; no curve was generated here |
| Base size B |16 at b12–14;32 at b15–17;64 at b18–20 |
| Auxiliary cardinalities |2B and4B, separately sampled, disjoint from the base and from known negation partners |
| Relation arity |3, with at least one base point and at most two auxiliary occurrences |
| Candidate fill thresholds |8,16,32, all fixed before both phases |
| Independent streams |20 per(rung,auxiliary setting), conditional on its fixed curve |
| Natural RUN units |360=9×2×20 |
| Candidate stream observations |1080=360×3, paired and correlated across f_max |
| Phases |160 calibration units at b12–15;200 holdout units at b16–20 |
| Target attempts |Exactly64B per natural unit, with every matching tuple retained |
| Policy/domain replays |21 per unit,7560 total; these are not independent RUN samples |
| Scientific companion files |12 exact files per unit,4320 total |
| Synthetic/calibration fixtures |390640, supplementing the ordinary ladder; none executed here |

All 387 additional reservations are bound to published allocation file fill-extra-ids-20260909.json, SHA256 b3b9c91674428e5fe70befd2b881b0993477cafed1022ea935ae76ececfdbe79. It contains360 RUN IDs,22 allocated future TASK IDs,4 DEC IDs and1 EV ID with their actual canonical allocation/check receipts. Together with the existing scientific handoff TASK-20260909-6e7bba, there are23 reserved workflow identities:21 are selected and2 remain unadmitted and unused. ID reservation is not task admission or a run observation.

The curve constructor, exhaustive point count and primality certificates, distinction between p and N, point-set/target law, complete tuple-domain enumeration, seed-key bytes/counters and unavailable-construction outcomes are frozen in specification.inputs. It makes no unobserved assertion that the first candidate succeeds. All constructor/search/precompute work, including rejected candidates and unused dictionary entries, is charged.

## Policies and cost comparisons

BF8/BF16/BF32 pay to compute exact predicted output-row nonzeros, use a fixed tie order and retain original-row/reconstruction witnesses. Unsupported pivots defer; unresolved final cores are retained but receive no projected rank credit. ALL is the exact infinite-fill identity. FULL is the no-partial/no-pivot projection control. FIXED is the separate coefficient-aware cycle-triggered comparator. MST is an additional explicitly costed sparse-filtering adaptation. All share the complete acquired input, exact arithmetic, certificate rules and8GiB cap.

H1's **at least80% retained informative rank** and **at least40% reduction in committed elimination nonzeros** are evaluated separately from **total weighted work at most80% of FIXED**. Total comparison requires full useful base rank B and verified target descent for every paired stream. It charges all acquisition, rejected pivots, discarded components, final LA, descent, independent checks, stored data and IO. The explicit W8 score and18 sensitivity settings are fixed before data; they are not CPU cycles or a claimed timing speedup.

Each cell retains its entire20-stream distribution, all completion/invalidity outcomes, descriptive bootstrap uncertainty and worst-decile costs. Rungs, auxiliary sizes, fill settings, null domains and SAT/UNSAT strata are never pooled. A zero denominator is undefined. A runtime interruption cannot become a completed negative, and no unsuccessful stream is replaced to manufacture20 successful cases.

Both source null controls remain: nonzero coefficient randomization on exactly matched row support/component sizes, and the same group-valid row pool under a frozen random arrival permutation. The algebraic null need not be group-valid or affine-consistent and receives no ordinary scientific or descent success credit. A later group-information claim would require a separate equal-acquisition relabelled cyclic-group control; this design makes no such claim.

The source loss L is tied to the exact affine-assignment fiber and discarded constraint dimension, with reconstruction/nullspace witnesses. Branching b counts verified legal policy successors. Neither quantity is treated as information about the actual discrete-log secret or as a full-translation quotient.

## Sources and ownership

This designer personally read the required primary passages in [Cavallar's CWI report](https://ir.cwi.nl/pub/4456/04456D.pdf) and [Sutherland's 2019 Lecture14](https://math.mit.edu/classes/18.783/2019/LectureNotes14.pdf). The first supplies filtering-comparator context in F2/NFS; the second supplies the p>3 ordinary-curve count criterion. No paper supplies the proposed20% gain. The source audit records exact reading scope and the failed direct raw-PDF fetch without inventing received bytes or hashes.

Future file-only reviewers have a real prerequisite: TASK-20260909-90c398 must deliver both complete PDFs and readable full text, with retrieval/extraction/hash provenance, and TASK-20260909-a7e015 must snapshot/publish them. A URL, abstract or producer summary cannot discharge that gate.

IDEA-20260905-1a8cb3 retains its rank/entropy replay ownership and unvalidated broad ceilings. H-ICEX-87ad66/EXP-ICEX-e0c85b retains the LP-1 exchange-rate comparison, which explicitly excludes LP-2/cycle behavior. This new design measures the bounded-fill two-auxiliary selection/verification policy. RELN/SDEG/ICEX certificate, activation, useful-rank and end-to-end gates remain separate. Novelty and the complete time-memory-data/query frontier remain unresolved.

## Prospective lifecycle

1. TASK-20260909-90c398 — executor: Deliver complete local primary sources.
2. TASK-20260909-a7e015 — coordinator: Archive TASK-20260909-90c398.
3. TASK-20260909-766300 — validator: Independently review bounded-fill protocol.
4. TASK-20260909-86249c — coordinator: Archive TASK-20260909-766300.
5. TASK-20260909-1047a7 — coordinator: Dispose of actual independent protocol review.
6. TASK-20260909-6b6568 — coordinator: Archive TASK-20260909-1047a7.
7. TASK-20260909-dc8d2c — executor: Implement complete bounded-fill instrument and checker.
8. TASK-20260909-cedcf2 — coordinator: Archive TASK-20260909-dc8d2c.
9. TASK-20260909-46ab71 — executor: Attempt exact finite-field projection formal target.
10. TASK-20260909-ed2de8 — coordinator: Archive TASK-20260909-46ab71.
11. TASK-20260909-4babab — validator: Independently qualify source-bound instrument and formal semantics.
12. TASK-20260909-32cfd1 — coordinator: Archive independent QA and record experiment-specific readiness.
13. TASK-20260909-38fc2d — coordinator: Freeze actual360-unit lock and launch activation.
14. TASK-20260909-85ac5d — coordinator: Archive TASK-20260909-38fc2d.
15. TASK-20260909-6e7bba — executor: Execute the full frozen bounded-fill relation ladder.
16. TASK-20260909-6447a8 — coordinator: Archive TASK-20260909-6e7bba.
17. TASK-20260909-a962e6 — coordinator: Freeze actual safe claim and answer-free review packet.
18. TASK-20260909-6b9521 — coordinator: Archive TASK-20260909-a962e6.
19. TASK-20260909-b8e29f — validator: Validate exact run integrity and scoped metrics.
20. TASK-20260909-f81958 — red-team: Blindly derive projection quantity and challenge full cost scope.
21. TASK-20260909-595c9f — coordinator: Archive TASK-20260909-b8e29f, TASK-20260909-f81958.

Every selected non-archive producer has exactly one archive. Both review_required producers TASK-20260909-dc8d2c and TASK-20260909-46ab71 retain their separate source snapshots and direct independent QA successor TASK-20260909-4babab. That QA now goes directly to **ledger TASK-20260909-32cfd1**, which freshly authors DEC-20260909-3d3dae and commits exactly these four paths:

- coordination/pending-ideas/BATCH-8fd304/fill-execution/tasks/TASK-20260909-4babab/qa-review.json
- coordination/pending-ideas/BATCH-8fd304/fill-execution/tasks/TASK-20260909-4babab/source-read-log.json
- ledger/decisions/DEC-20260909-3d3dae.yaml
- coordination/pending-ideas/BATCH-8fd304/fill-execution/archives/TASK-20260909-32cfd1/snapshot.json

No earlier QA-report snapshot or separate readiness producer commits these same files. Launch activation TASK-20260909-38fc2d depends on this actual completed QA ledger and reads its readiness DEC; a completed revise ledger still cannot authorize launch. The separate launch producer/snapshot and final postrun Validator/Red Team ledger remain unchanged.

TASK-20260909-823a3c and TASK-20260909-bd569b remain **reserved, unadmitted and unselected**. They have no fabricated execution, output or commit. Their initial planned cards remain in the preserved first-delivery bundle. TASK-20260909-32cfd1 is explicitly repurposed from the former QA snapshot into the required decision-only review ledger. All21selected future cards remain unadmitted.

The current Validator role permits approved run_commands for synthetic QA/audits and has no web_search capability. The complete local primary-source gate supplies source access; it does not prohibit otherwise approved synthetic QA commands. This Coordinator correction itself runs no commands, tests or scientific work.

The formal stage concerns the exact finite-field cancellation statement and its missing-premise control. An abstract theorem does not certify a computed kernel, ordinary-curve instance or observed rank. Actual toolchain/source/axiom receipts and independent semantic QA are required. The postrun Red Team receives only an answer-free standalone handoff, raw-input packet and local primary sources; its blind numerical unit is fixed in advance as RUN-RELN-825820. Missing input or audit capability remains explicitly unverified. No source/global receipt needs to be read merely to discover packaging instructions.

## Exact prepared records

| Canonical path | Bytes | SHA256 |
|---|---:|---|
|ledger/hypotheses/H-RELN-dee9ec.yaml|27115|a8108e7a75be7d80a8106eb03863c681c35f66bdc4bcdfe6014556abf13cb174|
|experiments/EXP-RELN-f3a133/specification.yaml|1053849|3d96072d7cbd7b14617d834578d680b09fddf9ee7e3fb5bfe7e4ca80de1c05a7|
|ledger/handoffs/TASK-20260909-6e7bba.yaml|1293021|b917799e4c116ad216d62ab5e85c6195a6d878abf7196a4f26fb004f90564799|
|coordination/pending-ideas/BATCH-8fd304/tasks/TASK-20260909-94a8a9/proposed-execution-chain.json|6554185|4fe9d91ddd2cf74c89ca13718abf93aa57e4d3785362c17f08c377d615045935|
|coordination/pending-ideas/BATCH-8fd304/tasks/TASK-20260909-94a8a9/source-audit.json|230771|1845e54c0d0aa3ac505d5479015832fa581e23cca3220afceb36d08b9ebfb0ed|
|ledger/decisions/DEC-20260909-40f3ad.yaml|30312|25678c1dd96625cacc6a86abd3f5cc67d28d989f7bc1130d30293fb380c6ef65|

This Markdown report intentionally has no self-hash. The source audit binds the first four records; the readiness decision binds that audit; this report binds the six other prepared files. Exact seven-file hashes and the actual final stopped timestamp are returned externally after exclusive temporary creation/readback.

The initial producing session was 01a086c5-68f0-73c3-b229-fa3e785ac0af, native OpenAI/gpt-6-astra at literal ultra. Its parent-read metadata was observed at2026-09-09T17:23:13.875762+00:00; model_verified remains false because no serving probe ran. No shell command, implementation, test, numerical/symbolic kernel, formal check, scientific run or child delegation occurred in this design.

All seven corrected output bytes are delivered under the explicitly authorized revision-2 root /private/tmp/swarm-design-TASK-20260909-94a8a9/revision-2/, mirroring the same seven canonical paths. The original staged and canonical files are not overwritten by this writer. Parent checks every original before-hash before any replacement. Parent exclusive copy, validation, actual release and the separate TASK-20260909-f6307e eight-path design snapshot/publication remain pending. Future commit/parent/publication values remain null.

The next action is parent validation/delivery and that separate design archive. After custody, the Coordinator separately scopes/checks the additive determinant clarification and local-source delivery before fresh independent protocol review and any approval. Knowledge promotion is empty because this is an unrun design with a material unresolved definition.

The correction runs under nonforced epoch3, owner coordinator-pending-ideas-swarm-20260907, controller 01a07e0d-9f07-7382-a7d3-e2f0b4cf08de, and native session 01a086c5-68f0-73c3-b229-fa3e785ac0af. Parent-observed current metadata at 2026-09-09T23:58:50.999737+00:00 records OpenAI/gpt-6-astra/ultra and model_verified:false, with no serving probe. Epoch2 was released abandoned after transport; its failure and the original dispatcher error remain recorded. The parent confirmed claim publication eac16769bb after a failed first push and successful retry.

Static metadata inspection confirms the direct common ledger for every review_required producer, unique source/archive ownership, no duplicate expected commit paths and unchanged scientific content. **The actual corrected prospective dispatcher check is still pending parent execution.** The current authoring-plan11gate pass is a different administrative observation. The hypothesis and standalone science handoff remain byte-identical to the first delivery; only the EXP QA metadata, prospective lifecycle and related audit/decision/report metadata and hashes change.
