<!--
inference_stanza: this file is PROSE_REPORT, not SOURCE_CODE; the comment-block
inference stanza duty of SC-3 does not attach to it. It is covered by
object-enumeration.yaml's artifact_provenance list, which is this task's
designated covering manifest under SC-3.
-->

# RANK 2 ideation report — object-first candidate tracked objects for full-round AES single-key cryptanalysis

**Task:** TASK-20260810-d8835b, role idea-generator, GOAL-AES-002 / RQ-AES-002 / BATCH-2b0fd1.
**Covering manifest:** `object-enumeration.yaml` in this same directory (SC-3). This report is the prose companion; every scored field, the honest-accounting block, and the SC-1 budget stamps live in the covering manifest and are not repeated here in full — only summarized.

## What this is, and what it is not

This is an **object-first enumeration** under `docs/inventor-protocol.md` section 1: a search for candidate *tracked objects* — the thing followed through the AES computation — for single-key cryptanalysis of **full-round** AES-128/192/256 (10/12/14 rounds), with the established families (differential, linear, integral, impossible-differential, MITM/Demirci-Selcuk, boomerang, biclique, algebraic/XSL, yoyo, mixture-differential, subspace-trail, partial sums) declared **off-limits as the primary lens**, per RQ-AES-002.

**It is explicitly NOT a completion of GOAL-AES-002.** Per GOAL-AES-002 `non_completion_criteria (i)` and `docs/inventor-protocol.md` section 4, this enumeration — and any count of screened-and-rejected candidates it contains — is a **fatigue report**: a statement about *this session's search*, at this budget, with this generation procedure, in this environment, not a statement about AES. Its honest status is `unverified`, and it is recorded that way. Zero compute was requested or run under this task; nothing here asserts a key recovery, a distinguisher, a margin, or a barrier statement.

## Method

1. Read the task's full read scope: `AGENTS.md`, `agents/idea-generator.md`, `docs/inventor-protocol.md`, `docs/target-result-profile.md`, `docs/claims-and-verification.md`, `RQ-AES-002`, `GOAL-AES-002`, `DEC-20260810-ba50dc`, the batch record, `CM-1.yaml`, `protocol-amendment-GOAL-AES-002-001.yaml`, `adoption-amendment-005-partB.yaml`, `KN-FIND-028`, `KN-FIND-029`.
2. Read the three **unadopted 2026-08-01 working-tree artifacts** named in the task's inputs — two prior ideation passes and one red-team pass — as inputs only, not evidence, per `DEC-20260810-ba50dc` `OBS-BATCH-2b0fd1-PRIOR-WORKING-TREE-ARTIFACTS`. Nothing they name is recorded here as tried, screened, closed, or negative on their authority; they are cited by path with status attached in `object-enumeration.yaml` `prior_art_consulted`.
3. Attempted knowledge retrieval via the crypto-kb MCP tools. They are **not present in this session's tool surface** (Read, Grep, Glob, Write, WebSearch, WebFetch, SendMessage only — no MCP knowledge tool, no command execution). Substituted a repository content search (`Grep`) over `knowledge/` and `ledger/hypotheses/`, recorded query-by-query in `object-enumeration.yaml` `knowledge_retrieval`. This substitute search surfaced two **real, committed** ledger hypotheses under this exact question — `H-AES-ecf3ad` and `H-AES-8c2d07`, both `status: proposed` — which are genuine prior art in a stronger sense than the unadopted working-tree material, and one reduced-round hypothesis (`H-AES-77230c`) whose object is adjacent to one of this session's candidates. All three are read in full and cited.
4. Generated candidate tracked objects, applying the **lossy-projection test** (`docs/inventor-protocol.md` section 2) to each before proposing any compute, then the **deduplication check** against the off-limits list and against the cited prior art, then scored survivors on the three required axes.
5. Requested **zero compute**. Every argument in this report and in the covering manifest is a text derivation, checkable by a reader without running anything.

## The seven candidates, briefly

Full detail, including the exact lossy-projection argument, dedup argument, and axis scores, is in `object-enumeration.yaml`. Summarized here:

| ID | Tracked object | Lossy-projection | Dedup verdict | Fate |
|---|---|---|---|---|
| C1 | Decision-diagram (Nerode-equivalence) residual width of the key-recovery predicate, built round by round | PASSES | REDISCOVERY (search-principle-level rediscovery of MITM/Demirci-Selcuk/biclique — a positive finding here *is* one of those constructions by another name) | Scored; low novelty, low testability at full scale, predicted low survival |
| C2 | Paired-independent-key data-path Hamming-distance histogram between two unrelated keys on one plaintext, round by round | PASSES | **not a rediscovery** — distinct from every off-limits family and from every cited prior-art object | Scored; medium novelty, high testability, predicted null but flagged with reduced confidence |
| C3 | Structured-key-set sharing-cost object `mu(F,d)` (the red-team's own named gap, generalized) | PASSES | REDISCOVERY — the generic accounting question MITM/biclique/partial-sums each specialize | Killed at dedup |
| C4 | Kolmogorov-complexity / compressibility of `(K,P,C)` | PASSES | not a rediscovery | Killed at **testability** (uncomputable in general; a computable proxy has no derived link to attack cost) |
| C5 | Walsh-Hadamard spectral eigenstructure of the round function | PASSES | REDISCOVERY — literal name match to the off-limits "linear" family | Killed at dedup |
| C6 | Mutual-information / entropy dependence statistic | PASSES | REDISCOVERY-adjacent — reduces to the same joint-frequency table linear/differential already build | Killed at dedup |
| C7 | Tower-field (GF((2^4)^2)) representation of the S-box for the algebraic lens | **FAILS** | not reached — killed at lossy-projection | Killed at lossy-projection (invertible linear change of basis; Macaulay rank is basis-invariant) |

**Coverage summary** (fatigue report, honest status `unverified`, not a closure of anything):

- 7 objects enumerated.
- 1 killed at the lossy-projection test (C7).
- 4 deduplicated as rediscoveries (C1, C3, C5, C6).
- 1 failed concrete testability after passing both prior screens (C4).
- 2 candidates survive lossy-projection and dedup (C2, C4); of those, 1 (C2) is also concretely testable.
- **0** of the 7 are predicted, at this session's confidence, to retain exploitable structure at the FULL round-count survival target (10/12/14 rounds).

This matches GOAL-AES-002's own stated overwhelming prior. It is not presented as a closure: no obstruction is measured here with error bars over C1–C7 as a set, and "no eighth object class exists" is explicitly **not** claimed — per `docs/inventor-protocol.md`, that would be exactly the premature-closure failure mode the protocol exists to prevent. A short, honestly screened list was chosen over a padded one, per the task's own instruction.

## Why C2 is the one candidate worth carrying forward as an idea

C2 (paired-independent-key data-path Hamming-distance histogram) is the only candidate that (a) passes the lossy-projection test, (b) is not a rediscovery of any off-limits family or of any object named in the two real `RQ-AES-002` hypotheses or the three unadopted working-tree reports, and (c) has a directly definable one-step propagation that fits the resource envelope this campaign has declared (pure C, no AES-NI required, no numpy, well within a 4-core/15 GB budget at the sample counts involved). Its predicted outcome is a controlled null (the paired trajectories should look like two independent random permutations' outputs by round ~2–4) — but that prediction is stated with **reduced confidence**, because this exact campaign's own cited prior art (`H-AES-77230c`, a real committed `RQ-AES-001` hypothesis, `status: proposed`) found that the AES-128 key schedule does **not** reach full bit-influence saturation even at round 10 (density stuck at 0.78125, never 1.0) — a demonstrated instance, in this program, of a naive full-diffusion expectation being measurably wrong. Whether the data path under two *unrelated* keys (rather than a single bit flip in one key) shows any analogous non-saturation is exactly the open question C2 would resolve, and it has never been measured in this program at any round count. This is named as the most promising open direction; it is **not dispatched, approved, or assigned** by this task — only the Coordinator may do that, and this task requests zero compute.

C1 (the decision-diagram width object) is included and scored because its *instrument* (build-and-measure rather than hand-construct) is not literally named in the off-limits list, but its honest dedup verdict is that any positive finding it could produce *is*, by construction, a rediscovery of meet-in-the-middle/Demirci-Selcuk/biclique-style state compression. It is recorded for completeness and because a toy-scale version of it would give this program its first *measured* (rather than argued) reading on how fast the treewidth/separator argument's predicted blow-up actually happens — a validation-ladder instrument, not a fresh escape.

## Prior art discipline

Two distinct tiers of prior art were consulted and are treated with different weight:

- **Unadopted 2026-08-01 working-tree artifacts** (two ideation passes, one red-team pass under `coordination/goals/GOAL-AES-002/`): read, deduplicated against, cited by path with their unadopted status attached in every citation. Nothing they name is recorded here as tried, screened, closed, or negative on their authority — per the task's binding instruction, since they carry no dispatched card, no budget, no stamps, no snapshot, and no review.
- **Real committed ledger hypotheses** (`H-AES-ecf3ad`, `H-AES-8c2d07` under this exact question; `H-AES-77230c` under the adjacent reduced-round question): these are genuine prior art in the ordinary sense — committed records with real IDs, `status: proposed`. They were read in full and every candidate in this enumeration was checked against them explicitly for object-level duplication. None of C1–C7 duplicates `H-AES-ecf3ad`'s univariate GF(2^8) interpolation-coefficient/co-degree object or `H-AES-8c2d07`'s L0 null-object-control pattern (the latter is instead *borrowed as a sanity-check design pattern* for C1's testability discussion, cited, not duplicated).

## Section 5 honest-accounting block (`docs/inventor-protocol.md` section 5)

- **Object(s) studied:** C1–C7, listed above; full detail in `object-enumeration.yaml`.
- **Depth of verified structure:** none measured. Zero compute was run. C7's lossy-projection failure is a checkable algebraic derivation (Macaulay-matrix rank invariance under an invertible linear change of basis); every other verdict is a text argument, independently re-derivable, not a measurement.
- **`dominated_by`:** `unresolvable in this environment: no primary source reachable; every recalled frontier row is unverified-from-memory` — set to this exact string, never `null`, per SC-4/R5, because `null` would assert a row-by-row Pareto check against the published frontier that cannot be performed in this environment.
- **`sota_delta`:** DEFINITIONAL-REFERENCE DELTA — 0 bits: no candidate in this enumeration claims any cost figure, so under CM-1 the charged cost is not computed for any candidate, against the DEFINITIONAL exhaustive-key-search reference of `2^(k-1)` AEU-k at the stated key size, and the comparison against the published state of the art is **UNADJUDICABLE in this environment in both directions** (R5, same sentence). PUBLISHED-FRONTIER DELTA — unadjudicable, asserted in neither direction.
- **Enumerated closures:** none, at the `docs/inventor-protocol.md` section 4 standard (named obstruction with a measured value and error bars, a checkable argument, and forward guidance). C1/C3/C5/C6/C7's dedup or lossy-projection verdicts are screening results on individual candidates, not obstruction measurements over a named object class; the task's own constraints state explicitly that no closure is being asked for here.
- **Open directions for the next session:**
  1. C2 is the concretely testable, non-duplicated candidate; no compute has been requested for it here, and dispatching it is a Coordinator decision.
  2. A toy-scale C1 instrument would give this program its first measured (not argued) reading on state-merging-width blow-up.
  3. Whether the key schedule's demonstrated non-saturation (`H-AES-77230c`) has a data-path analogue is the specific question C2 targets.
  4. Naming an eighth object class is **open and unattempted** — this session did not attempt exhaustive enumeration, and that is a statement about this session's search, never a statement that no further object exists.

## R5 anti-laundering compliance

This report states no margin and no cost figure for any candidate. R5's same-sentence duty (name the reference as exhaustive key search under CM-1, and declare the published-state-of-the-art comparison unadjudicable, in the same sentence as any stated margin) is therefore **satisfied vacuously**, and is recorded as such rather than left for a reviewer to infer, per SC-7. The one place this report states anything resembling a delta (`sota_delta` above) carries the R5 clause in the same sentence, as required.

## Knowledge retrieval — exact record

Attempted; the crypto-kb MCP tools are unavailable in this session's tool surface. A substitute repository content search was performed instead (10 distinct `Grep` queries, `KS-1` through `KS-10`, exact patterns/paths/match counts recorded in `object-enumeration.yaml` `knowledge_retrieval.searches`). No absence, novelty, prior-non-testing, or non-novelty inference is drawn from any of it in either direction. The substitute search's one substantive yield — discovery of `H-AES-ecf3ad`, `H-AES-8c2d07`, and `H-AES-77230c` as real committed prior art — materially shaped the dedup arguments above and in the covering manifest.

## Scope and claim tier

No claim about AES security at any round count is made or implied anywhere in this report or the covering manifest. No distinguisher, no key recovery, no speedup, no measured structural excess, no barrier statement, no universal impossibility claim, and no statement about deployed AES. No official state is changed, no evidence strength is assigned, no hypothesis status is touched, no experiment is approved, and no work is assigned to the Executor — those remain the Coordinator's authority alone. Zero compute was run; the SC-1 budget stamps (null clock fields, defect recorded against the campaign's instrumentation, not against this producer) are in `object-enumeration.yaml` `budget`.
