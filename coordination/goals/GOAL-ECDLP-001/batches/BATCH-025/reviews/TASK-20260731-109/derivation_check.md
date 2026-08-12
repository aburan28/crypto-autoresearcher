# Derivation check — TASK-20260731-109 / RT-20260731-109

**Verdict: REVISE**  
**Amend freeze:** `285e533e` (EXP-IT-001 v2 + PA-IT-001-v2-rc25b-b1-b4)  
**Prior REVISE:** RT-20260731-105 @ `303ae797`; NOT APPROVED `7dc2b39b` / DEC-026  
**Queue amend:** QUEUE-AMEND-20260731-014  
**Recommendation to TASK-110:** NOT APPROVED (no Executor; second REVISE ⇒ design-path non-execution)

## Scope of this check

Independent re-review of the RC-25b protocol amendment freeze only. Bind via
`git show` at `285e533e`. No cells measured. No approval issued. No Executor
authorization. Companion `contract_review.yaml` carries the full gate ledger.
This session did not author the amend.

Out of scope: v1 rewrite; structure-null-r2; H-DS-001 reopen; STR; crypto-scale
extrapolation; inventing repairs.

## B-1–B-4 discharge

| Prior blocker | Result |
| --- | --- |
| **B-1** F_hit / d / H_min pre-registration | **Discharged** — d=3, H_min hops RV, tree-ball F_hit algorithm, pre-search table schema |
| **B-2** detectors + density universe | **Not fully discharged** — detectors decidable; density N/cofactor uniqueness missing (**B-5**) |
| **B-3** cost ledger vs matched rho | **Not fully discharged** — component formulas decidable; R_xfer path/endpoint aggregation missing (**B-6**) |
| **B-4** IDEA-011 isogeny null | **Not fully discharged** — identities/gate/hash present; null graph algorithm + plant detector incomplete (**B-7**, **B-8**) |

## What holds

- Amend snapshot committed; v2/PA hashes match TASK-108 receipt; v1 untouched at `303ae797`
- Toy claim ceiling; planted-path F2; matched rho/BSGS; F1/F2/F3 shape; H-DS deferral; D-1 `approved_by: null`
- HEUR-ISO-1 CDF is now pre-registered and independently recomputable (B-1)

## What blocks APPROVE

1. **B-5** — `rho_special` universe does not uniquely designate N per retained class.
2. **B-6** — `R_xfer` lacks a frozen min/first-path aggregation rule (gate manipulable).
3. **B-7** — null 3-regular graph construction deferred to builder receipt (not closed).
4. **B-8** — CTRL-NULL-IT-PLANT detection predicate not frozen.

## Disposition

TASK-110 should archive this REVISE and record **NOT APPROVED**. Under RC-25b,
this second REVISE is **BATCH-025 design-path non-execution** — no further
amend cycle on this path, no Executor. This session did not author the amend
and does not author repairs.
