# SSI refinement duplication/knowledge audit — `TASK-20260809-53689c`

Date: 2026-08-09  
Candidate: `IDEA-20260806-9c2f80`  
Successor under preparation: `EXP-SSI-1d0f36`  
Scope: repair of the already-admitted design contract, not a new novelty claim

## Audit boundary

This is a current-corpus refresh for the refinement batch. It checks the
candidate's committed neighbours and the corrected catalogue paths, and it
records the prior duplication findings that remain binding. It does not claim
that the full published literature has been searched: the configured
knowledge-retrieval MCP tool was not available in this session, so no absence
of a knowledge result is treated as evidence of novelty.

The immutable proposal and prior reports remain the authorities for admission:

- `ledger/proposals/IDEA-20260806-9c2f80.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/tasks/TASK-20260806-fd3518/duplication_audit.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-f68c05/tasks/TASK-20260809-b28c39/duplication_knowledge_audit.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-4f52ab/reviews/TASK-20260809-83623a/red_team_report.md`

## Current read-only checks

The following read-only searches were run from the isolated worktree:

```text
rg -n 'IDEA-20260806-9c2f80|EXP-SSI-2d8583|EXP-SSI-1d0f36' ledger ideas experiments coordination
rg -n -i 'advice|preprocess|non-uniform|amortiz|quantifier|fiber' \
  ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/S1.md \
  ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/S2.md \
  ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/Q3.md
```

Observed current-corpus facts:

1. `IDEA-20260806-9c2f80` is explicitly referenced by S1, S2, and Q3 as the
   classical per-prime advice/preprocessing frontier. Those references route
   the advice question to the candidate; they do not instantiate a second
   classical OneEnd frontier.
2. `S2-4` is recorded in `DEDUP.md` as paired with the candidate, but S2-4 is
   a quantum coset-state pooling object with no per-prime classical advice
   string. It is a scope neighbour, not an identical mechanism.
3. The catalogue directory spelling is
   `ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/`. The prior BATCH-4f52ab
   queue used `ssi-ssiq`; the successor task uses the committed `ssi-ssqi`
   paths and records this as a provenance correction.
4. Q3 repeatedly states that instance-independent preprocessing is advice and
   must be charged separately/additively. This supports retaining a separate
   `T_build` axis; it does not validate any frontier exponent.
5. The prior BATCH-b3c87f and BATCH-f68c05 audits admitted the candidate while
   leaving its classical novelty and heuristic assumptions conditional. This
   refinement preserves that status and makes no fresh novelty promotion.

## Decision from this audit

`duplication_status: admitted_candidate_refinement_only`

No new duplicate or contradiction is asserted from the searches above. The
useful result is a repaired scope map: classical advice, quantum pooling, and
other instance-independent preprocessing are not silently merged. The next
review must still challenge whether the typed branches are genuinely distinct
and whether their controls and cost axes are complete.

## Knowledge and claim boundary

- No `KN-FIND` or `KN-OPEN` record is created by this audit.
- No paper theorem is cited as verified here.
- No security, attack, exponent, or all-advice lower-bound claim follows.
- The exact successor specification, not the older proposal's stale
  `numpy-only` implementation note, governs any future executor handoff.

## Required successor checks

The accompanying `EXP-SSI-1d0f36` contract must carry the following forward:

- fixed `A_p` versus random-set diagnostic quantifiers;
- typed order-tagged and membership-only B branches;
- unique output-producing `R_t(A)` union accounting;
- explicit H-ADV-4 pair-law status and pair null;
- byte-level matched random-advice and shuffled-fiber controls;
- separate build/query/physical-byte/break-even axes; and
- corrected `ssi-ssqi` catalogue paths.
