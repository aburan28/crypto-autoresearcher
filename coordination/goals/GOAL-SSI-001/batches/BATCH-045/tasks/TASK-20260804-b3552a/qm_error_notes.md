# TASK-20260804-b3552a: QM-ERROR Advance (Lane B, BATCH-045)

**Goal:** GOAL-SSI-001 | **Batch:** BATCH-045 | **Lane:** QM-ERROR  
**Prior state:** `f_union_ledger_partial` (BATCH-025, TASK-20260730-071)  
**Proposed next state:** `f_union_exhaustive_obligation_registered_partial`

---

## Summary

A genuine zero-compute ledger advance exists for QM-ERROR. The advance has two
components:

1. **Coverage equality F = U** (derivable from recovery_spec)
2. **Explicit residual obligation register** (five named blockers classified)

---

## 1. The Coverage Advance (F = U)

### Current state

The f_union_ledger (BATCH-025) records:

- `U = F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ F_tail ∪ F_verify`
- Rule R2: `U ⊆ F` (soundness: every named channel IS a failure mode)
- Status: `f_union_ledger_partial`

What is **not** recorded: whether `F ⊆ U` (coverage: every failure IS in some
named channel). This gap matters because bounding Pr[F] via Pr[U] is invalid if
F contains uncovered failure modes.

### The derivation

recovery_spec.md (line 19-20) states:

> "All exits are typed either `success` (a true verification result) or a named
> failure constituent of `F`."

Combined with the six-stage enumeration (stages 1-6, each with one named
failure constituent), the argument is:

1. F = { non-success exits } (by definition, line 14-17)
2. All non-success exits are named failure constituents (by the typing
   constraint, line 19-20)
3. The named failure constituents are exactly F_input through F_verify (stages
   1-6)
4. These are the seven members of U (f_union_ledger.yaml)
5. Therefore F ⊆ U
6. Combined with R2 (U ⊆ F): **F = U**

### What this buys

- Confirms the seven-channel decomposition is **exhaustive** (no missing channel)
- Makes probability composition *valid in principle*: Pr[F] = Pr[U] exactly,
  so union-bounding U bounds F with no residual leakage
- Is a logical prerequisite for future OB-PROB / OB-BOUND discharge

### What this does NOT buy

- Does not assign probability weights
- Does not clear QM-ERROR
- Does not implement Verify
- Does not resolve QM-STOPPING

---

## 2. Residual Obligation Register

After recording F = U, five obligations remain between the current state and
QM-ERROR clearance:

| ID | Name | Type | Blocker |
|---|---|---|---|
| OB-PROB | Per-channel probability bounds | needs computation/literature | No distributional model |
| OB-BOUND | Union probability bound | ledger (once OB-PROB done) | OB-PROB |
| OB-STOP-PROB | F_stop probability (tau) | blocked by other lane | QM-STOPPING (REV-1/REV-2) |
| OB-VERIFY | Verify body / instantiation | needs implementation or pin | No crypto Verify body |
| OB-INSTANTIATE | End-to-end trace | needs implementation | No implementation exists |

### Key findings

- **No further zero-compute ledger advance exists** beyond the coverage equality
  and this register. Every remaining obligation requires computation,
  implementation, or resolution of a blocked lane.
- **OB-STOP-PROB** is structurally gated by QM-STOPPING (paused, REV-1/REV-2
  unmet). It cannot advance until either REV-1 (admissible CollimationSieve pin)
  or REV-2 (host-independent collision/mixing result) is met.
- **OB-VERIFY** is the only obligation flagged as *pin-seekable*: a committed
  Verify-like construct in CollimationSieve@6f9188e4 could serve without API
  invention. Pin-seeking was not attempted in this step.
- **OB-BOUND** is the only obligation that becomes ledger-satisfiable after
  its predecessor (OB-PROB) is discharged.

---

## 3. Dependency Assumption Update

The four BATCH-025 dependency assumptions are reclassified:

| Assumption | Ledger-dischargeable? | Blocker |
|---|---|---|
| scaffold_no_crypto_Verify_token_semantics | No | OB-VERIFY |
| symbolic_stopping_policy_halt_without_verify_true | No | OB-STOP-PROB |
| batch024_path_justified_on_scaffold_prior | Not a gap | (lineage marker) |
| overlaps_among_F_star_permitted_without_independence_claim | Not a gap | (conservative; feature) |

---

## 4. Constraints Verification

All constraints respected:
- Zero-compute only (pure definitional derivation from recovery_spec)
- QM-STOPPING not re-queued (REV-1/REV-2 remain unmet)
- Toy peak-byte width not iterated
- Fake-tau gate B not attempted
- FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED retained
- No CollimationSieve API invention
- No curve computation, no experiment, no implementation

---

## 5. Recommendation to Coordinator

The proposed advance (F = U coverage + obligation register) is the **maximal
zero-compute ledger step** available for QM-ERROR. If accepted:

1. Record the coverage equality as a new rule (e.g. R6: F ⊆ U) in the
   f_union_ledger lineage
2. Record the obligation register as the explicit residual gap
3. Advance QM-ERROR state to `f_union_exhaustive_obligation_registered_partial`
4. Note that no further zero-compute advance exists for this lane

**Next actionable directions** (for Coordinator decision):
- Pin-seeking in CollimationSieve@6f9188e4 for a Verify-like construct (OB-VERIFY)
- Distributional literature search for channel failure rate bounds (OB-PROB)
- Both require non-zero compute or source analysis, not further ledger steps

---

## 6. Disposition

- **QM-ERROR**: `f_union_exhaustive_obligation_registered_partial` (proposed)
- **QM-STOPPING**: paused_pending_revisit (untouched)
- **QM-MEMORY-MAP**: numeric_composition_operator_protocol_toy_partial (untouched)
- **QUERY_MEMORY**: FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED (retained)
- Not breakthrough, not clearance, not completion
