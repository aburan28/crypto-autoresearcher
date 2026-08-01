# TASK-20260731-020 — Derivation / protocol check for EXP-DS-001 v2

**Report:** `RT-20260731-020` (path + task id).
**Reviewed snapshot:** `66c4ae905b49a81e2262b162b498dead46744d29` (TASK-20260731-019).
**Prior review:** `RT-20260731-016` REVISE (B-1, B-2).
**Amendment:** `PA-DS-001-v1-to-v2` / `QUEUE-AMEND-20260731-001`.
**Question:** Does v2 discharge B-1 and B-2 with no new blocking protocol holes?

## Verdict

**PASS.** B-1 and B-2 are discharged. M-1..M-4 are prefer-discharged. Residuals R-1 / R-2 / m-2 are non-blocking. No measurement; no approval issued here.

## Snapshot binding

| Path | sha256 at `66c4ae90` | Notes |
|---|---|---|
| `experiments/EXP-DS-001/specification.v2.yaml` | `898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a` | matches working tree |
| `experiments/EXP-DS-001/amendments/v1_to_v2.yaml` | `c02af4873fc561a000671462784dd62b77706aae97e9b67a171ce2222ec48881` | PA-DS-001-v1-to-v2 |
| `experiments/EXP-DS-001/specification.v1-frozen-df613af6.yaml` | `c1792bf1733e56f631b04585f50272c9a3342302459daa62a64d1e5fdc4c3889` | byte-identical to live v1 |

`git merge-base --is-ancestor 66c4ae90 HEAD` succeeds.

## B-1 discharge (HEUR-DS-1 decidable)

| Required repair (RT-016) | v2 location | Status |
|---|---|---|
| Smoothness / LPF stats, not degree-CDF vs ρ | `heur_ds_1_decision_rule.sampled_quantity` | met |
| Freeze D / u* before sampling | `D_formula`, `u_star_formula`, `d_half` | met |
| Numeric KS and/or rate band + constant factor | `RATE-DS-1` (c=8), `KS-DS-1` threshold | met |
| Quantitative TAIL | `TAIL-DS-1`: fail iff `p_ext * n < 1` | met |
| Executable F3 | `F3_trigger` ↔ `bit_size_pass` | met |

## B-2 discharge (structure-gate middle band)

When `R < 0.5`:

| `R_null` | v1 label | v2 label |
|---|---|---|
| `>= 0.9` | S1-eligible | S1-eligible (unchanged) |
| `< 0.5` | F2 | F2 |
| `in [0.5, 0.9)` | **none** | **F2** (aligned with S1 gate) |

## What still re-derives cleanly

1. Toy claim ceiling; no asymptotic support path from this contract alone.
2. IDEA-20260731-011 null machinery with planted-bug and honest-rho controls.
3. Matched rho / BSGS baselines.
4. D-1 `approved_by: null`; approval only via TASK-20260731-021.
5. Immutable v1 blob preserved; Executor (if approved) binds to `specification.v2.yaml`.

## Non-blocking residual (R-1)

If two bit sizes meet S1’s null conjunct while another `R<0.5` cell meets F2, disposition priority is not spelled out. Implied adjudication: **any F2 cell overrides S1** (`structure_gate_failed`). Not a reopen of B-2.

## Scope of this check

Pre-execution protocol re-review only. No cells measured. No approval issued. Companion `contract_review.yaml` carries the full discharge ledger.

## Coordinator handoff

On PASS: TASK-20260731-021 should record `APPROVAL_DETERMINATION: APPROVED` and authorize Executor only against `specification.v2.yaml`. Do not open a second amendment cycle (RC-17). This task’s `write_scope` excludes the dispatch queue; Coordinator must mark TASK-020 completed and regenerate the BATCH-017 plan.
