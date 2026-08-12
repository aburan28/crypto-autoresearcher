# TASK-20260731-065 — Derivation / protocol check for PA-DS-001-v2-ctrl-theater-r2

**Report:** `RT-20260731-065` (path + task id).
**Reviewed snapshot:** `9c94d866948526d5f27dc17705d02000defcf9dc` (TASK-20260731-064; parent `78ce4f79`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit delta).
**Prior disposition:** DEC-20260731-015 paused BATCH-021 theater-repair as RC-21 non-execution after RT-20260731-056 REVISE (RT056-B1/B2); DEC-20260731-016 opens BATCH-022 fresh amend for RC-22 review only.
**Exact next action under review:** BATCH-022 theater-r2 — PLANT-CLOSED-PATH + RHO-CALIB-AUDITED + NULL-SPLIT-HARD-DESTROY; CI-IDENTITY and SPARSE-P-SUCCESS deferred.
**Session:** Independent `review-adversarial`; `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. This session did not author the addendum. Unauthorized `RUN-DS-001-ctrl-theater` ignored as non-binding.
**Question:** Do the frozen CTRL-RT056-* protocols discharge RT056-B1 (hard `destroy_demonstrated` iff `R_null<0.9`) and RT056-B2 (closed detection_path; no equivalent-FLAG echo), and address RT047-B3 scientifically, with toy ceiling and no silent S1_met — so TASK-066 may APPROVE?

## Verdict

**PASS.** The RT056-B1 and RT056-B2 protocol holes are closed in the fresh freeze:

1. **RT056-B1 discharged (protocol)** — `CTRL-RT056-NULL-SPLIT-HARD-DESTROY` requires `destroy_demonstrated` iff measured `R_null < 0.9`; `falsifiability_failed` is terminal non-discharge; soft-pass forbidden.
2. **RT056-B2 discharged (protocol)** — `CTRL-RT056-PLANT-CLOSED-PATH` closes `detection_path` to `{null_gate_f2_shape}` only; forbids equivalent-FLAG escape and echo-entailment class; requires `echo_entailment_check=false`.

RT047-B3 is addressed scientifically at protocol level (inject-before-gate + closed non-echo path + entailment ban). Rho audit fields address RT056-M1. Toy ceiling, v2 immutability, deferred CI/SPARSE, rejected BATCH-021 freeze untouched, and no S1_met promotion hold. No measurement; no approval issued here. TASK-066 should APPROVE.

## Snapshot binding

| Path | sha256 at `9c94d866` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_theater_r2.yaml` | `0ebef5e2ddbcdef2da67fa9f9f0ee78d1a2deea469b7a37d4156c641aabfc10f` | PA-DS-001-v2-ctrl-theater-r2 |
| `experiments/EXP-DS-001/controls/CTRL-RT056-PLANT-CLOSED-PATH.yaml` | `db0419cb7b12b9fd29d155fd820b1259c8295288faff0e323d3a3ac25933e27d` | plant closed path |
| `experiments/EXP-DS-001/controls/CTRL-RT056-RHO-CALIB-AUDITED.yaml` | `ef72f0857a97505631d95cc6ffd19082431a822eb35fd5db681ddbd5942a8e3b` | rho audited |
| `experiments/EXP-DS-001/controls/CTRL-RT056-NULL-SPLIT-HARD-DESTROY.yaml` | `9208411a63d0132e35fdc52b2fde8fb68206eab2f904b8eba4cfaea8a2512816` | null-split hard destroy |
| `ledger/decisions/DEC-20260731-016.yaml` | `984fe20612f630a8d4b0b7884b258d00ea83553df6dbbc697fb4f9cba14dbfea` | opens BATCH-022 for review |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in commit delta; parent pin matches |

`git merge-base --is-ancestor 9c94d866 HEAD` succeeds. Snapshot path list excludes all `specification*.yaml` and hypothesis records. Working-tree freeze paths match `9c94d866` (`git diff` empty). Rejected BATCH-021 freeze vs `98fa35db` is unchanged.

## Anti-tautology derivation (why PASS)

### 1. Plant — RT047-B3 / RT056-B2 → closed

RT047 showed `live_plant_detect` divides reported split costs by 4 in-process then “detects” factor-4 — true by construction. RT056-B2 required closing the open `"equivalent non-arithmetic FLAG"` escape left in the rejected BATCH-021 plant protocol.

`CTRL-RT056-PLANT-CLOSED-PATH` does that: inject `/4` (or equivalent cost inflation) into harvest/reporting **before** the gate; allow only `detection_path=null_gate_f2_shape`; forbid echo-entailment FLAGS (truth entailed by detector-applied plant arithmetic on the same costs); require `injection_site`, `costs_as_read_by_gate`, `echo_entailment_check=false`. The control can return false. That is the scientific fix RT047 demanded, encoded as a decidable pass bit.

### 2. Rho — RT056-M1 → encoded

Hardcoded `rho_calib_ratio_*=1.0` cannot fail. The audited control requires measured real/null rho wall/gop (or documented proxy), writable as non-1.0, with raw fields; ±0.15 band deferred to post-run interpretation. Anti-hardcode theater is protocol-encoded.

### 3. Null-split — RT056-B1 / inventor-protocol destroy → hard

RT056-B1 rejected soft-passing when composition is repaired but `R_null` cannot be driven below 0.9. The new control hard-requires `destroy_demonstrated` (iff measured `R_null < 0.9` with raw costs) for package PASS; `falsifiability_failed` is terminal non-discharge / redesign, not a soft PASS. Composition under the same claw/join remains required; asymmetric crippling remains forbidden.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | RT056-B2: closed `{null_gate_f2_shape}`; no equivalent-FLAG / echo entailment | **met** |
| 2 | RT056-B1: `destroy_demonstrated` iff `R_null<0.9`; soft-pass forbidden | **met** |
| 3 | RT047-B3 addressed scientifically (protocol-level) | **met** (empirical pending run) |
| 4 | Rho: measured fail-able ratios + raw fields; band deferred | **met** |
| 5 | No full 54-cell; CI/SPARSE deferred; no v2 edit; rejected freeze untouched | **met** |
| 6 | Toy ceiling; no run until TASK-066; no H-IC/H-STR; no silent S1_met; RC-22 | **met** |

## Scope of this check

Pre-execution control-addendum review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full gate ledger. Protocol PASS does not assert empirical plant detection or destroy demonstration.

## Coordinator handoff

On PASS: TASK-20260731-066 should record `APPROVAL_DETERMINATION: APPROVED` and may authorize `RUN-DS-001-ctrl-theater-r2` only. Ignore unauthorized `RUN-DS-001-ctrl-theater`. Mark TASK-065 completed and regenerate the BATCH-022 plan outside this write_scope.
