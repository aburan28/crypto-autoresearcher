# TASK-20260820-affeff — Independent red team on the frozen BCP-2 + runner certificate kind

Batch: BATCH-312472 (GOAL-MD5-001, RQ-MDFIVE-6870c1) — batch 2 of 7
Rank/role: independent review · red-team
Policy: `review-adversarial`, effort `xhigh`, INDEPENDENT SESSION
Opened by: DEC-20260820-cc9f95 · Depends on: TASK-20260820-513ea9 (frozen snapshot)
Runs concurrently with TASK-20260820-047039 (sibling reviewer — no reading each other's reports; attestation says so).
Archived by: TASK-20260820-19ae68
Declared budget: 450 s, 2 GB, 1 run
Ledger handoff: `ledger/handoffs/TASK-20260820-affeff.yaml`
**Governing review plan (committed before this task may run):**
`coordination/goals/GOAL-MD5-001/batches/BATCH-312472/review-plan/review-plan-affeff.yaml`

## What you attack (per the plan — prior, joints J1-J6, proves-too-much A/B/C, blind rederivation)

- **J1** the pinned canonical serialization (uniqueness, decidability, cross-session stability).
- **J2** certificate independence enforceability (the comparison logic AND the pin mechanism).
- **J3** the null-object decision table (every outcome row labelled; tolerance not vacuous).
- **J4** firewall regression vs BCP-1 (element by element; a loosening is a batch-halting finding).
- **J5** evidential asymmetry (confound caveat required-field or advisory; failure direction intact).
- **J6** charging independence (wrapper-measured wall_seconds on every new-run code path).
- **Proves-too-much:** Object A (known non-collision → verified:false), Object B (known CONSUMPTION manifest — the MANIFEST's sha256, never the payload → invalid, never a weaker pass), Object C (one logical path block, four serializations → exactly one canonical).
- **Blind rederivation (required):** the CONSUMPTION predicate from BCP-2's blind scoring rule section ONLY; blind_from: BCP-2's self_report section + both producers' cards and handoffs. Attest.

## Hard rules
- Single-reviewer round: do NOT read TASK-20260820-047039's report (sibling); `read_sibling_reports: false` in the attestation.
- **NEVER READ the quarantined payload.** Synthetic objects only; Object B uses the MANIFEST's sha256.
- Read the COMMITTED tree at the snapshot commit, not uncommitted working state.
- Any claim that BCP-2 still cannot host a blind calibration carries a NAMED OBSTRUCTION and an argument, not a tally (docs/inventor-protocol.md).
- Write only under `reviews/TASK-20260820-affeff/`. Never commit.

## Deliverable
`red-team-report.yaml`: per-joint entries (succeeded/failed/untested with basis — no untested route presented as closed), the object results, the blind rederivation + attestation, the overall dispatchability verdict (dispatchable / dispatchable-with-named-gaps / not-dispatchable, reasoned), the residual-risk judgement in both directions, and concrete ranked amendments with how much of the guarantee each recovers.

## STANDING CONSTRAINTS
SC-1 FABRICATE NOTHING · SC-2 CLAIM CEILING (assert nothing about MD5) ·
SC-4 BUDGET OUTCOMES NEVER EVIDENCE ABOUT MD5 · SC-5 OPEN AND UNATTEMPTED STAY
NAMED · SC-6 NO STATUS CHANGE / APPROVAL / PROMOTION / EDIT TO A COMMITTED
RECORD — report findings; the disposition is the Coordinator's ·
SC-7 HALT AT THE DECLARED CEILING, REPORTED TRUTHFULLY · SC-8 NEVER USE
AMAZON BEDROCK.
