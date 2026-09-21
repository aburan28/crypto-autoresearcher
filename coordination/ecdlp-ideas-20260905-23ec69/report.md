# ECDLP proposal intake BATCH-23ec69

Two user-directed avenues (instruction of 2026-09-05) under GOAL-ECDLP-001, each opened as a
research question and populated by one idea-generator task, then snapshot-archived and
independently red-teamed. **Eleven proposals filed**, all `status: proposed`,
`novelty_status: unverified`, claim tier toy, no exponent claimed. No experiment, hypothesis,
approval or status change. The [Coordinator decision](../../ledger/decisions/DEC-20260905-b3d10c.yaml)
ranks and returns.

| Avenue | Question | Producer | Records |
|---|---|---|---|
| Exotic point representations | RQ-ECDLP-623a32 | [TASK-20260905-a6ea8a](tasks/TASK-20260905-a6ea8a/report.md) | 5 (one candidate withdrawn as a repackaging) |
| SAT/SMT technology for relation finding | RQ-ECDLP-f0a7b0 | [TASK-20260905-282872](tasks/TASK-20260905-282872/report.md) | 6 |

Snapshot archive [TASK-20260905-8443e4](archives/TASK-20260905-8443e4/snapshot.md) at commit
`de6ca2d52251e363677f4909749f302fae705f79` (parent `49c6f3f9412ad0251a1d57b91cd66fd9cb661304`),
content_first, 18 path hashes, verified by the Red Team at 18 of 18. Receipts live in
[dispatch_queue.json](dispatch_queue.json).

## Red Team verdicts (RT-20260905-ac087e, six joints)

J1 mechanism distinctness, J2 lossy projection or pipeline stage, J3 hidden assumptions and
omitted costs, J4 Pareto honesty, J5 controls, J6 recalled citations. Full report:
[tasks/TASK-20260905-ac087e/red_team_report.yaml](tasks/TASK-20260905-ac087e/red_team_report.yaml).

| Rank | Record | Class | J1 | J2 | J3 | J4 | J5 | J6 | Disposition |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | [IDEA-20260905-d0fee4](../../ledger/proposals/IDEA-20260905-d0fee4.yaml) | mechanism | holds | holds | breaks | holds | holds | breaks | returned for additive revision, then first design candidate (Stage 1 counting loop) |
| 2 | [IDEA-20260905-24d827](../../ledger/proposals/IDEA-20260905-24d827.yaml) | control | holds | holds | breaks | holds | holds | inconclusive | ready for design ranking (two encodings, node counts separate) |
| 3 | [IDEA-20260905-a6f98e](../../ledger/proposals/IDEA-20260905-a6f98e.yaml) | measurement | breaks | holds | breaks | holds | holds | holds | ready for design ranking, certificate-two arm only |
| 4 | [IDEA-20260905-3de445](../../ledger/proposals/IDEA-20260905-3de445.yaml) | mechanism | holds | breaks | holds | holds | breaks | holds | returned (histogram by length; known-false object that can fire) |
| 5 | [IDEA-20260905-ab4a6e](../../ledger/proposals/IDEA-20260905-ab4a6e.yaml) | representation | holds | holds | holds | holds | breaks | breaks | returned (norm ball for the CM control; open recalled in-repo citations) |
| 6 | [IDEA-20260905-24b41a](../../ledger/proposals/IDEA-20260905-24b41a.yaml) | control | holds | breaks | holds | holds | holds | breaks | returned ((T3) balance condition; (T2) quadratic biextension case) |
| 7 | [IDEA-20260905-579fcc](../../ledger/proposals/IDEA-20260905-579fcc.yaml) | control | holds | holds | breaks | holds | holds | breaks | returned (narrow (M4); open recalled supports) |
| 8 | [IDEA-20260905-79112a](../../ledger/proposals/IDEA-20260905-79112a.yaml) | control | holds | holds | breaks | breaks | holds | holds | returned (add multi-target rho row) |
| 9 | [IDEA-20260905-a94b5f](../../ledger/proposals/IDEA-20260905-a94b5f.yaml) | measurement | holds | holds | inconclusive | inconclusive | breaks | breaks | returned (gadget-aware null; quantify FHJRV bits) |
| 10 | [IDEA-20260905-3993c3](../../ledger/proposals/IDEA-20260905-3993c3.yaml) | control | holds | holds | breaks | inconclusive | holds | holds | returned (declare call count; restate magnitudes as measurements) |
| 11 | [IDEA-20260905-0e0982](../../ledger/proposals/IDEA-20260905-0e0982.yaml) | representation | holds | holds | holds | holds | holds | holds | ready, lowest; one contract with H-ECDLP-f9a627 |

A `holds` records the absence of a break on that joint in this review; it certifies neither
mathematical correctness beyond the reviewer's re-derivations nor global novelty.

**Prior outcome.** The Coordinator's prior, recorded in the handoff before the round, stands on
its headline (no exponent-moving survivor in either set) and is overturned on two sub-claims:
the representation set does not fail mainly as PGL_2 reparametrisations, and the sharpest SAT
break is a metric-definition blindness (3de445) the prior did not anticipate.

**Batch-level objections adopted.** (1) In-repository records cited as `recalled` in 579fcc
and ab4a6e must be opened or dropped. (2) Five SAT records assert BATCH-1a527c's intake files
were absent; they exist at the snapshot commit (merged from main after the producer looked);
the substantive differences survive. (3) a6f98e (B) and 3de445 (B) measure one obstruction,
counted once. (4) GOAL-SATIC-c49b77 in goal_applicability is a pointer, not an acceptance.

**Cheapest decisive test.** d0fee4 Stage 1 at p about 2^12 on three prime-order curves, f in
{x, y, r o x}, reporting both the point count and the count of distinct value-carrying window
entries, with the adaptive-window known-false object and the PGL_2 and translation-conjugate
nulls, and four contradictory point predictions pre-registered (2e14f7's d*B, d0fee4's B, the
Bezout ratio 2 of 5f5ace and EXP-MODEL-5c4f24, d0fee4's 4.5). A counting loop with no solver.

## Process notes

- Both producers and the Red Team were cut off by API session rate limits (resets at 21:00
  and 02:00 UTC) and resumed, or had already written their deliverable; infrastructure only.
- The runtime refused subagent writes of `report.md`; each producer's report is a verbatim
  Coordinator transcription with a provenance note inside the file.
- `docs/object-frame-ideation.md` was adopted on main during the run; its declarations were
  supplied to the representation producer as an additive Coordinator message.
- The crypto-kb MCP server was unpopulated in this session; the Coordinator built a
  file-backed index (15,000 records) and ran probes that surfaced ten unnamed nearest
  neighbours, which the producers cited before filing. Make the index available to producers
  before they write novelty screens.
- PR #750 (batch opening) merged; the proposals, archives and this report travel in PR #772.
