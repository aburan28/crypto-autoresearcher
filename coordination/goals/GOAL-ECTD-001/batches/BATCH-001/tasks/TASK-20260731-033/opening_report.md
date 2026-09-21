# TASK-20260731-033 — GOAL-ECTD-001 BATCH-001 opening report

**Role:** coordinator  
**Requested policy:** `coordinator-orchestration-code`  
**Resolved model:** Cursor Grok 4.5 (session inherit; `fallback_used: true` relative to policy alias)  
**Independent session:** false (Coordinator open)  
**Date:** 2026-07-31

## Bound records

| Record | Path | Status |
|---|---|---|
| GOAL-ECTD-001 | `ledger/goals/GOAL-ECTD-001.yaml` | `draft` (activation deferred to TASK-20260731-032) |
| RQ-ECTD-001 | `ledger/questions/RQ-ECTD-001.yaml` | `active` |
| Secondary briefing | `inputs/ECTD-TESKE-20260731/briefing.md` | unverified synthesis |
| Dispatch queue | `coordination/goals/GOAL-ECTD-001/batches/BATCH-001/dispatch_queue.json` | validated |

## Objective (one sentence)

Determine whether a Teske-style trapdoor can exist for ordinary curves over generic prime fields via a secret isogeny to a rare endpoint-specific ECDLP (or trapdoor-DDH) weakness that is **not** a public isogeny-class invariant.

## Literature gate (blocks experiment design)

No experiment may be designed until TASK-20260731-027 has either:

1. upgraded `KN-LIT-7261` (Teske) beyond title-only against a fetched primary source, and filed `KN-LIT-7630..7636` (or honest redirect stubs) for Galbraith / Jao–Miller–Venkatesan / De Feo / Dent–Galbraith / Kutas–Petit–Silva / Fried–Gaudry–Heninger–Thomé / Jacobson–Kushwaha; or
2. recorded exact fetch obstructions so the Coordinator can pause rather than design on unverified summaries.

Already in corpus (do not duplicate): `KN-LIT-007` (GHS), `KN-LIT-3748` (extending GHS), `KN-LIT-5102` (Seurin trapdoor DDH; cites Dent–Galbraith). Local `downloads/teske.pdf` referenced by `KN-LIT-7261` is **missing**.

## Deprioritized paths (do not make primary IDEA mechanisms)

- Hiding anomalous / low-embedding-degree / smooth-order / supersingular endpoints behind an \(\mathbb{F}_p\)-isogeny (class invariants).
- Secret GLV/CM endomorphism alone as a “trapdoor” (fixed-factor only).

## Prioritized endpoint families for ideation (TASK-20260731-029)

1. Secret isogeny-aligned factor bases / Semaev–Gröbner heavy tails  
2. Large-conductor vertical volcano traps  
3. Hidden correspondences to other algebraic groups  
4. Trapdoor DDH first (weaker intermediate)

At least two of three IDEA records must come from families (1)–(2).

## Separation from related ledger work

| Record | Relation |
|---|---|
| GOAL-ECDLP-001 / RQ-ECDLP-002 | Broad charged breakthrough search — complementary campaign; do not merge evidence IDs |
| IDEA-20260731-008 | Attacker-side **public** isogeny-transfer cost gate to special families — dual question, not a designer trapdoor |
| H-ISO-001 (`rejected_scoped`) | Short \(\ell\)-neighbor Semaev \(d_{\mathrm{reg}}\)/yield homogeneity negative — does **not** close heavy-tail / conductor-barrier / private-factor-base search |
| IDEA-20260726-009 | Min-height / weak-model reachability in the class (representation-sensitive) |

## Completion criteria (goal-level)

Either a constructive trapdoor candidate with private sub-rho or SNFS-style precomputation/individual-log advantage and public path/detection ≥ matched rho; **or** a scoped barrier naming an obstruction per prioritized family with forward guidance (inventor-protocol closure standard). Three-model quorum required for `completed`.

## Pause conditions

Budget exhausted; primary sources unobtainable after fetch order; decisive compute exceeds budget after cheaper gates; infrastructure blocker; user pause.

## Campaign budget

`maximum_batches: 8`, `total_wall_clock_seconds: 28800`, `max_concurrent: 3`.

## BATCH-001 plan (after this snapshot)

1. TASK-20260731-034 — protocol snapshot archive  
2. TASK-20260731-027 — literature curation  
3. TASK-20260731-028 — literature snapshot  
4. TASK-20260731-029 — three IDEA-20260731-016..018  
5. TASK-20260731-030 — ideation snapshot  
6. TASK-20260731-031 — independent red-team review  
7. TASK-20260731-032 — ledger archive; `draft` → `active` if literature gate holds

## Status transition

**None.** Goal remains `draft` until TASK-20260731-032.
