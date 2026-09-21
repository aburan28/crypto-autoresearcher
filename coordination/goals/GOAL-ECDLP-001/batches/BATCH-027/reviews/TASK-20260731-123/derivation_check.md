# Derivation check — TASK-20260731-123 / RT-20260731-123

**Verdict: PASS**  
**Amend freeze:** `d65c5e21` (EXP-IT-001 v3 + PA-IT-001-v3-rc27-b5-b8)  
**Prior REVISE:** RT-20260731-109 @ `285e533e`; BATCH-025 non-execution `1cb3c6c4` / DEC-028  
**Queue amend:** QUEUE-AMEND-20260731-016 / DEC-032 / RC-27  
**Recommendation to TASK-124:** APPROVED (Executor of v3 at toy; this task does not approve)

## Scope of this check

Independent re-review of the RC-27 protocol amendment freeze only. Bind via
`git show` at `d65c5e21`. No cells measured. No approval issued. No Executor
authorization. Companion `contract_review.yaml` carries the full gate ledger.
This session did not author the amend.

Out of scope: v1/v2 rewrite; structure-null-r2; H-DS-001 reopen; STR;
BATCH-026 CI cancel; crypto-scale extrapolation; inventing repairs.

## B-5–B-8 discharge (B-1 retained)

| Prior blocker | Result |
| --- | --- |
| **B-1** F_hit / d / H_min pre-registration | **Retained discharged** — d=3, H_min, tree-ball F_hit, pre-search schema |
| **B-5** N* / cofactor uniqueness | **Discharged** — N_MAP-IT-001-v3; h_max=256; N*=min(Cand); detectors on N* |
| **B-6** R_xfer aggregation | **Discharged** — min over certificates; BFS by increasing j; MITM min if used |
| **B-7** null graph algorithm | **Discharged** — NULL-IT-NEIGHBOR-v1 XOR 3-regular; failure @10000; id in hash |
| **B-8** plant_detected predicate | **Discharged** — raw-ledger packaging check; plant_injected cell named |

## Integrity binds

- Snapshot `d65c5e21` ancestor of HEAD; v3/PA sha256 match TASK-122 receipt
- v1 `303ae797` and v2 `285e533e` blobs untouched
- Toy ceiling; D-1 `approved_by: null`; no H-DS/STR reopen; BATCH-026 CI left alone

## Disposition

TASK-124 should archive this PASS and record **APPROVED** for Executor of
`specification.v3.yaml` at toy ceiling. RC-27 cycle-cap non-execution does not
fire. This session did not author the amend and does not author approval.
