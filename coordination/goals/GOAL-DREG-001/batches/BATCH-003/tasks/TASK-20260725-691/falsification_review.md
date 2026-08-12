# Falsification review — CTRL-B protocol freeze

Task `TASK-20260725-691` · Red Team · GOAL-DREG-001 BATCH-003  
Verdict: **REVISE** · report id `RT-20260725-691` · no official state change

Inference: requested policy `review-xhigh`; resolved model
`cursor-grok-4.5-high-fast`; fallback `true`; authorization
`AMEND-PATH-001-001`; independent session `true`. Fallback is policy/infra,
not mathematical evidence.

## Review basis

Durable producer evidence is the Coordinator snapshot archived by
`TASK-20260725-690` at commit `57adc3cf4afbc956d520d3ffbfd84cf07d3ca9ad`
(parent `ca42cbeb1c7648d0b8991b8dd3748c497c97ee9c`), reachable from review
`HEAD`. That commit changes exactly:

- `.../TASK-20260725-689/ctrl_b_protocol.yaml`
- `.../TASK-20260725-689/protocol_design_note.md`
- `.../archives/TASK-20260725-690/snapshot-receipt.json`

Producer SHA-256 values match the receipt
(`0c5a7b4e…` / `2b9586d8…`). The receipt still says
`pending_post_commit` with null commit metadata; Git binding is the durable
check. Working-tree-only producer edits were not used as evidence.

Context (not re-validated as new measurement): BATCH-002 `RT-N12D6.md`,
`decision.yaml` (`DEC-GOAL-DREG-001-B002`), `ledger/goals/GOAL-DREG-001.yaml`,
and `AMEND-PATH-001-001`.

## Falsification axes

| Axis | Result | Notes |
|---|---|---|
| CTRL-B as frozen reintroduces support-gap confound | **Not falsified** | Definition ranks null on sem support; metric is `deficit_genuine`, not raw vs `sr_pred`. |
| Quarantine predicates not machine-checkable | **Falsified** | Q1/Q3/Q4 are prose/regex hybrids without closed field checks or a named harness. |
| Protocol illicitly authorizes measurement | **Not falsified** (wording risk) | `review_only_freeze` forbids measurement now; `after_pass_*` wording needs split labels. |

## What survives

1. **CTRL-B math matches BATCH-002.** Restrict null to sem's 174035 columns,
   report `rank(null|sem_support) - 138573` in `[1931, 17947]`, keep raw
   `17947` quarantined, forbid unchunked host-unsafe instruments, require
   chunked `h012c_block_m4ri` — this is the RT-N12D6 CTRL-B card, not a
   return to cross-support `sr_pred` comparison.
2. **No measurement in BATCH-003.** Authorization and status are review-only;
   execution requires independent review PASS. Budgets / `write_root` are
   preparatory.
3. **Claim boundary is mostly right.** Toy/single-cell limits; no sub-rho;
   no rehabilitation of raw 17947; D5 series remains the honest pre-CTRL-B
   observable.

## What fails the freeze-as-executor-ready claim

### 1. Quarantine predicates are not machine-checkable (blocking)

- **Q1** — regex on `deficit_vs_sr_pred = 17947` plus "as a structural claim"
  is not a closed check. Paraphrases slip through; quarantine prose that must
  mention 17947 can false-positive.
- **Q3** — "{≥1931 lower bound} or clean D5 series; not 17947" pins neither the
  D5 tuple/run IDs nor a pre-/post-CTRL-B mode. Upper endpoint 17947 of
  `expected_interval` is a *possible* later `deficit_genuine`, so "not 17947"
  without a metric-id qualifier is inconsistent.
- **Q4** — `structural_d6_number == deficit_genuine` names no schema path and
  is undefined before a measured receipt.
- **Admission metric** `quarantine_predicates_Q1_Q4_hold` therefore cannot be
  evaluated by a deterministic harness as frozen.

### 2. `after_pass` wording (non-blocking for measurement now; blocking for clarity)

Design note: after PASS, "`deficit_genuine` becomes the admissible D6
structural number." That can be misread as structural admission at
**protocol-review** PASS. Correct split:

- protocol-review PASS → may schedule executor only;
- CTRL-B execution admitted → may cite measured `deficit_genuine`.

### 3. ncols-only support admission is insufficient

`restricted_ncols_equals_174035` alone does not prove the deleted set is
`null \\ sem`. Cheapest counterexample: delete any other 16016 null columns;
ncols still 174035; reported "genuine" deficit is not the BATCH-002 quantity.
Require deletion-set / sem-support hash pins from CTRL-A (or seed-rebuilt
hashes matching committed systems).

## Baseline / scope

Pure rank control (`certificate.kind=none`). No Pollard-rho/BSGS path is
opened. Any positive genuine deficit remains wrong-sign for the H-DREG-001 WIN
reading (`d_reg(sem) ≥ d_reg(null)=7`). This review does not pin
`deficit_genuine`, does not measure rank, and does not change H-DREG-001
status.

## Verdict

**REVISE** — not FAIL (core CTRL-B definition is sound and does not authorize
measurement now) and not PASS (stated machine-checks and after_pass/support-hash
admission are not executor-ready).

## Next concrete action

Revise `ctrl_b_protocol.yaml` (closed Q1–Q4 field checks; split after_pass
labels; support-hash admission metrics); re-snapshot; thin Red Team re-check;
only then dispatch chunked CTRL-B execution. Until then keep raw 17947
quarantined and use the committed support-matched D5 series as the honest
degree-axis observable.
