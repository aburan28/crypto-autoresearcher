# TASK-20260731-113 — Derivation / protocol check for PA-DS-001-v2-ctrl-ci-identity

**Report:** `RT-20260731-113` (path + task id).
**Reviewed snapshot:** `07232da808339b424f1d7fc21c37fdea86a093b0` (TASK-20260731-112; parent `6b3fffde`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Open decision:** DEC-20260731-030 opens BATCH-026 and selects CI-IDENTITY as highest-EVPI residual after DEC-029 structure-null honest fail (does not authorize Executor run).
**Prior disposition:** DEC-20260731-029 closed BATCH-025 structure-null-r2 as inconclusive (EV-DS-008; honest `structure_direction_fail`). RT047-B2 / RT079-B6 / RT101-B6 remained blocking on CI honesty.
**Exact object under review:** PA-DS-001-v2-ctrl-ci-identity / CTRL-RT025-CI-IDENTITY as admitted at `07232da8` for possible `RUN-DS-001-ctrl-ci-identity` authorization by TASK-114.
**Session:** Independent `review-adversarial` (`fresh_session_after_stall: true`); `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the package. Raced TASK-111 task_report IT prose ignored per task card.

**Question:** Is the frozen CI-IDENTITY addendum executable and reviewable such that TASK-114 may APPROVE a CI-identity control run?

## Verdict

**PASS.** RT047-B2 / RT079-B6 / RT101-B6 residual is addressed at protocol level:

1. **Executable status** — Both PA and CTRL set `status: executable` (not `abandoned_before_archive`, not `cancelled_before_approval`).
2. **CI semantics encoded** — `cost_identity_R`, `ci_of_cost_identity_R`, `ci_contains_point_estimate`, `ci_identity_pass`, and `ci_identity_fail` are defined in CTRL and listed in PA `executable_markers.required_semantics_present`.
3. **Honest fail** — Wrong-quantity CI or point R outside CI ⇒ `ci_identity_fail` (not infra; not lane death / `reject_scoped`).
4. **Hygiene** — Toy ceiling; parent v2 immutable; SPARSE deferred; no EXP-IT launder; no STR; no H-IC/H-STR edits; `no_run_authorized_until_approval: true`; RC-26 one-cycle cap documented.

Toy ceiling and deferred SPARSE / IDEA-008 naming hold. No measurement; no approval issued here. TASK-114 should APPROVE (this reviewer does not).

## Snapshot binding

| Path | sha256 at `07232da8` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_ci_identity.yaml` | `4c88e08b382bb4a594f953811926abb14306d820e1a1cc5380736f2fc1fd8ea2` | executable PA |
| `experiments/EXP-DS-001/controls/CTRL-RT025-CI-IDENTITY.yaml` | `a8e25016ae1e9c967ad20f23e89cbf35224714a166dd275031e9a072cd256a62` | executable CTRL |
| `ledger/decisions/DEC-20260731-030.yaml` | `1627ab8f1a793d72c4a2aeee002ec2f88f69380c5b1f4979e5f91b9602f81aa3` | batch open |
| `…/BATCH-026/SCOPE-DECISION.md` | `aaef0fd7896c4e59e5b3dc137d1eac31de6bc2e9589bcb59e99a8a97e10a543b` | scope + dominated_by |
| `…/BATCH-026/QUEUE-AMEND-20260731-015.md` | `fddf655be9146f4c59bf2a4eddbea3471e248c646bc15fb19e629d97b601ada1` | RC-26 amend |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta |

Commit name-only list excludes all `specification*.yaml`, H-IC/H-STR, and EXP-IT/H-IT freeze paths. Receipt `source_path_sha256` matches recomputed blobs; receipt `commit_sha` is `null` (informational process note I-1, not REVISE-forcing).

## Anti-tautology derivation (why PASS)

### RT047-B2 → CI-identity control

EV-DS-003 at cell 20/64/4/101 recorded R≈0.028 with bootstrap CI computed on a wall-ratio proxy that failed to contain the reported point estimate (point-outside-CI pathology). RT047-B2, RT079-B6, and RT101-B6 name this as blocking: any R-based quantitative reading on H-DS-001 is unreadable while CI honesty claims use a non-identity quantity.

`CTRL-RT025-CI-IDENTITY` encodes exactly that fix: require `ci_of_cost_identity_R` (CI on the same yield-charged R as the point estimate), check `ci_contains_point_estimate`, and allow honest `ci_identity_fail` when the driver still uses a proxy or point lies outside CI. Required report fields make the check Validator-decidable without post-freeze invention.

That is the scientific fix RT047-B2 demanded, encoded as decidable pass/fail bits. Empirical discharge still needs an APPROVED run — and under EV-DS-003 priors, `ci_identity_fail` is the expected scientific outcome if the pathology persists, not an infra failure.

### vs structure-null closure

DEC-029 closed structure-null with honest fail; CI honesty is the named next_action with highest EVPI. SPARSE total-cost accounting remains open but is dominated_by CI-IDENTITY because every R-based reading (including sparse) is corrupted if CIs are not of cost-identity R. IDEA-008 / EXP-IT re-entry is similarly dominated_by (DEC-028 closed IT RC-25b NOT APPROVED).

### Decision / scope

DEC-030 vocabulary: approve opens BATCH-026 and the executable addendum for independent RC-26 review — not Executor run, not H-DS-001 support, not lane death. SCOPE-DECISION / QUEUE-AMEND-015 agree. H-DS-001 remains analyzed.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | `status: executable` on PA and CTRL | **met** |
| 2 | `cost_identity_R` / `ci_of_cost_identity_R` / `ci_identity_pass` / `ci_identity_fail` present | **met** |
| 3 | Honest `ci_identity_fail` allowed (not infra / lane death) | **met** |
| 4 | Discharges RT047-B2 / RT079-B6 / RT101-B6 | **met** |
| 5 | Toy ceiling; SPARSE deferred; no EXP-IT launder; no STR; no H-IC/H-STR edits | **met** |
| 6 | `no_run_authorized_until_approval`; parent v2 not in commit delta | **met** |
| 7 | RC-26 one-cycle; REVISE ⇒ non-execution understood | **met** |

## Scope of this check

Pre-execution review of the admitted CI-IDENTITY snapshot only. No cells measured. No approval issued. No Executor authorization. Companion `contract_review.yaml` carries the full gate ledger. Protocol PASS does not assert empirical CI honesty success.

## Coordinator handoff

On PASS: TASK-20260731-114 should record `APPROVAL_DETERMINATION: APPROVED` and may authorize `RUN-DS-001-ctrl-ci-identity` only against `CTRL-RT025-CI-IDENTITY` into `results/ctrl_ci_identity`. Mark TASK-113 completed and regenerate the BATCH-026 plan outside this write_scope. Do not alter H-IC-001 / H-STR-002. Do not launder EXP-IT. Do not touch EXP-IT / BATCH-027.
