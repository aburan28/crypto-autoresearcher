# TASK-20260731-056 — Derivation / protocol check for PA-DS-001-v2-ctrl-theater-repair

**Report:** `RT-20260731-056` (path + task id).
**Reviewed snapshot:** `98fa35db18e49cc65f977392bbbd925990e9a05b` (TASK-20260731-055; parent `839c308c`).
**Parent contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable; sha256 `898304bf…a5636a`; **not** in snapshot commit).
**Prior disposition:** DEC-20260731-012 inconclusive on CTRL-RT025-UNPLANTED (EV-DS-003 / reminted chain toward EV-DS-004–005); RT-20260731-047.
**Exact next action under review:** BATCH-021 theater repair — PLANT-INDEPENDENT + RHO-CALIB + NULL-SPLIT-COMPOSITION; CI-IDENTITY and SPARSE-P-SUCCESS deferred.
**Session:** Independent `review-adversarial`; `resolved_model_id` cursor-grok-4.5; `fallback_used: true`; xhigh not claimable. Prior `6f4bcb84` failed_infrastructure ignored. This session did not author the addendum. Any prior PASS text at this path (including that cited by TASK-057 APPROVED) is superseded by this REVISE.
**Question:** Do the frozen control protocols scientifically discharge RT047-B3 / residual RT038-B3 theater (not cosmetic synth-OR removal alone), with decidable plant / rho / null-split gates, toy ceiling, and no silent S1_met — so TASK-057 may APPROVE?

## Verdict

**REVISE.** Two blocking protocol holes remain:

1. **RT056-B1** — `CTRL-RT025-NULL-SPLIT-COMPOSITION` soft-passes without demonstrating `R_null < 0.9`.
2. **RT056-B2** — `CTRL-RT025-PLANT-INDEPENDENT` leaves an `"equivalent non-arithmetic FLAG"` escape that can reintroduce echo-class tautology under a new name.

Toy ceiling, v2 immutability, deferred CI/SPARSE naming, and no S1_met promotion hold. Rho anti-hardcode is encoded with audit-schema limitations (RT056-M1). No measurement; no approval issued here. Under RC-21, REVISE ⇒ BATCH-021 theater-repair non-execution.

## Snapshot binding

| Path | sha256 at `98fa35db` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/amendments/v2_ctrl_theater_repair.yaml` | `ae045b81d37c6449b1f5774e5b3e47cc24511c1bb3b9936b0970adc3b4452ab8` | PA-DS-001-v2-ctrl-theater-repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-PLANT-INDEPENDENT.yaml` | `19975ff578fde57e99453aa9a36b3e43cb04eec985c621409c3a2514257d946b` | plant repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-RHO-CALIB.yaml` | `c43d30b7cc90b9d22457e637bff67b884df77ddc7f4131ef282c9708ba7bab6b` | rho repair |
| `experiments/EXP-DS-001/controls/CTRL-RT025-NULL-SPLIT-COMPOSITION.yaml` | `483a2432cabb8282ef081568ff22badd6c7d34ffeef9c4e89df03f186356affa` | null-split repair |
| `ledger/decisions/DEC-20260731-014.yaml` | `20f9353438399a7cf959c9742d2527600e166e54af3aafb3c28b93630cc5c253` | opens BATCH-021 theater repair |
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | **not** in snapshot commit; parent pin matches |

`git merge-base --is-ancestor 98fa35db HEAD` succeeds. Snapshot path list excludes all `specification*.yaml` and hypothesis records. Working-tree blobs for the four freeze paths match `98fa35db` (`git diff` empty).

## Anti-tautology derivation (why REVISE, not PASS)

### 1. Plant — RT047-B3 residual → RT056-B2

RT047 verified that `live_plant_detect` defines `R_plant = (cost_split/4)/cost_naive`, then “detects” `|R_plant - R/4| < ε`. That conjunct is true by construction; a control that cannot return false has no detection power. Synth-OR removal was cosmetic.

`CTRL-RT025-PLANT-INDEPENDENT` makes real progress: inject `/4` into harvest/reporting **before** the gate reads costs; forbid named `null_gate_echo_factor` alone; forbid synth and hardcoded `planted_bug_detected`.

It does **not** close the tautology *class*. `require_detection_path` still allows `"or equivalent non-arithmetic FLAG"` without defining equivalence or banning FLAGS entailed by detector-applied plant arithmetic. `falsifies_if` only names the literal echo factor / hardcoded / synth. An renamed echo conjunct would again pass. That is the same failure mode RT047 called cosmetic when only the synth OR-path was removed.

### 2. Rho — RT038-B3 / RT047 facet → PASS_WITH_LIMITATIONS

Hardcoded `rho_calib_ratio_*=1.0` cannot fail. The new control requires measured real/null rho wall/gop (or documented measured proxy), writable as non-1.0; forced 1.0 is a protocol violation. Infra measurement failure is not a mathematical negative (AGENTS rule 5). Limitation: no required raw fields and no explicit ±0.15 band bind/defer (RT056-M1) — not alone blocking.

### 3. Null-split — RT047-M2 / inventor-protocol destroy → RT056-B1

Asymmetric non-composing half-keys make `R_null ≫ 1` near-automatic whenever `R < 0.5`. Composition under the same claw/join machinery is the right repair.

But amendment/control **purpose** says demonstrate `R_null` can fall below 0.9, while **pass_condition** only requires documenting composition and recording destroy-attempt behavior. The OR arm (“honestly report cannot drive below 0.9”) is a valid observation of *failure of falsifiability*, yet is treated as a soft PASS. RT047-M2: if `R_null` cannot be driven down after composition repair, the gate must be redesigned — not discharged. Co-required theater discharge is therefore not decidable from the pass bit.

## Card checklist

| # | Requirement | Status |
|---|---|---|
| 1 | Plant: forbid echo / divide-then-echo; inject-before-gate; non-echo FLAG | **PARTIAL** — RT056-B2 |
| 2 | Rho: measured fail-able ratios, not hardcoded 1.0 | met (RT056-M1 limitations) |
| 3 | Null-split: compose half-keys + destroy check `R_null` can go &lt;0.9 | **PARTIAL** — RT056-B1 |
| 4 | No full 54-cell; CI-IDENTITY / SPARSE-P-SUCCESS deferred (named); no v2 edit | met |
| 5 | Toy ceiling; no run until TASK-057; no H-IC-001 / H-STR-002; no silent S1_met; RC-21 | met (REVISE path) |

## Process residual

- **RT056-P1:** TASK-057 archive (`ebbeccbe`) already recorded `APPROVAL_DETERMINATION: APPROVED` citing a prior PASS at this path. This independent REVISE supersedes that review attestation. Coordinator must remint NOT APPROVED / no run (outside this write_scope).

## Scope of this check

Pre-execution control-addendum review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full gate ledger and required fixes.

## Coordinator handoff

On REVISE: TASK-20260731-057 should record `APPROVAL_DETERMINATION: NOT APPROVED` and must **not** authorize `RUN-DS-001-ctrl-theater`. RC-21 ⇒ BATCH-021 theater-repair non-execution (no second cycle in this batch). Remint any prior APPROVED archive. Leave `_session_6f4bcb84_infrastructure_failed.json` in place. Mark TASK-056 completed and regenerate the BATCH-021 plan outside this write_scope.
