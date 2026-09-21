# QM-STOPPING host-independence reduction — BATCH-041 / TASK-20260730-135

- Goal: GOAL-SSI-001
- Idea: IDEA-20260729-001 (CSIDH-COLLIMATION-FC0-R2)
- Decision ref: DEC-20260730-038 · Evidence input: EV-SSI-040 · Red-team input: RT-20260730-133
- Role: executor (observations only; no state transition)
- Git revision at execution: 47a40c3360c76a7140fa27e2cadfe45fa3d9e58e

<!-- MACHINE-READABLE STATUS (harness-checked) -->
```yaml
REDUCTION_OUTCOME: neither_pause
reduction_exists: false
dependence_essential_scoped: false
named_obstruction: false
meets_inventor_protocol_s4: false
is_closure_claim: false
qm_stopping_lane: paused_pending_revisit
ninth_unverified_rerecord: false
tau_invented: false
joint_finiteness_established: false
verify_relativity_candidate_status: open_unresolved_not_refuted_not_proven
qm_stopping_control_result: FAIL
```

## 0. What this document is

This is the bounded zero-compute attempt, demanded by DEC-20260730-038 /
BATCH-040 §6 item-1, to decide whether **τ's finiteness reduces to a
host-independent property** (mixing-time / re-randomization /
collision-distribution of the sieve) **statable without the full `Verify`
body**, with an explicit falsifiable criterion.

Falsifiable criteria for the three admissible outcomes are pre-registered in
`falsifiable_criteria.yaml` (OUTCOME-R / OUTCOME-D / OUTCOME-N). Machine-checkable
ledger: `reduction_ledger.yaml`.

**Honest disposition of this batch: `neither_pause` (OUTCOME-N).** Neither a
reduction (OUTCOME-R) nor a scoped essential-dependence obstruction (OUTCOME-D)
is earned from committed in-repo structure. Per DEC-20260730-038, the QM-STOPPING
lane is **paused** with explicit revisit conditions — **not** re-recorded as
`unverified` a ninth time. This asserts no clearance, no breakthrough, no
completion, and invents no τ, mixing bound, or CollimationSieve API.

## 1. The reduction question (precise)

Let τ be the BATCH-018 source-compatible stopping time:

\[
\tau=\inf\{k\geq 1:\text{after invocation }k\text{ enters terminal success, residual-tail closure, or named }F\text{-exit}\},
\]

with Verify-relative terminal σ-algebra (success only when `Verify(x,k')=true`;
see BATCH-013 `recovery_spec.md`, BATCH-018 `stopping_law_artifact.md`).

**Question.** Does there exist a property `Prop` such that:

1. `Prop` does **not** quantify over the full cryptographic `Verify` predicate body;
2. `Prop` is **host-independent** (identical across admissible FC0-compatible host
   acceptance semantics, or independent of that body by construction);
3. `Prop` has an explicit **falsifiable** criterion;
4. `Prop` implies existence of finite source-compatible τ and/or joint Q/S/P/C(+H)
   finiteness in the BATCH-018 sense, within a stated scope;
5. `Prop` is **not** an inflation of a merely local collimation kernel into an
   end-to-end Verify-relative stopping law?

If yes → OUTCOME-R (refute Verify-relativity candidate). If instead one proves,
within an explicit scope S of admissible hosts, that **every** host in S fails to
admit such a τ (object-level, not availability) → OUTCOME-D (§4 obstruction).
Otherwise → OUTCOME-N (pause with revisit).

## 2. Candidate host-independent properties audited

| ID | Candidate | Committed status | OUTCOME-R? |
|----|-----------|------------------|------------|
| PROP-MIX | `independence_conditions` → `iid_or_mixing_hypothesis` | **null / not_supported** (BATCH-031 OBL-TI-independence_conditions) | No |
| PROP-KERNEL | end-to-end `transition_kernel` | **null** (BATCH-031 OBL-TI-transition_kernel; BATCH-018) | No |
| PROP-USB | `uniform_success_lower_bound` | **null**; C2 heavy-tail **NOT REJECTED** (BATCH-018/031) | No |
| PROP-LOCAL | BATCH-012 \(K_{v_1,v_2}\), \(p(v_1,v_2)\) | **local only**; explicitly not end-to-end τ | No (fails req. N) |
| PROP-HIST | history-uniform / summable-tail | **not_supported** (BATCH-030) | No |
| PROP-VERIFY-IFACE | BATCH-021/022 Verify freeze + scaffold | acceptance only; `invents_tau:false`; no-crypto token predicate | No |

### 2.1 Why PROP-LOCAL cannot be OUTCOME-R

BATCH-012 `process_extraction.md` pins an explicit **local** collimation/retry
kernel and one-attempt progress probability. It states that the extraction is
implementation-compatible for the **local recursive sieve only** and is **not**
an invented completion of the missing end-to-end process; it provides **no**
uniform progress/tail bound and **no** end-to-end stopping law. Using
\(K_{v_1,v_2}/p(v_1,v_2)\) as a host-independent global τ bound would violate
OUTCOME-R requirement N and the pre-registered falsifier for local inflation.
Prior controls (BATCH-018/031) already refuse that inflation.

### 2.2 Why PROP-MIX / PROP-KERNEL / PROP-USB cannot be OUTCOME-R without invention

BATCH-031 records the ingredients that would most naturally serve as
host-independent probabilistic laws for τ finiteness — and records them as
**null / not_supported**. Inventing an iid geometric retry model, a transition
kernel, or a uniform success lower bound in this batch would fabricate the
missing Prop rather than reduce to a committed one (AGENTS.md rule 9; DEC-038
constraints).

### 2.3 Mixing mentions elsewhere are out of scope

BATCH-002/003 Ramanujan / VW-walk mixing concerns isogeny **baselines**, not
FC0 QUERY_MEMORY / Verify-relative τ. They are not cited as Prop candidates here.

## 3. OUTCOME-D (essential Verify-dependence) audit

To earn a named inventor-protocol §4 obstruction one must discharge
`∀ admissible hosts in S, ¬∃ finite source-compatible τ` as a statement about the
**object**, with forward guidance.

| Requirement | Status in this bounded step |
|-------------|-----------------------------|
| Explicit scope S | Not constructible without inventing host semantics (BATCH-020 `no_admissible_pin`) |
| ∀-hosts discharged | **Untouched** (BATCH-040 §4 quantifier-order audit retained) |
| Object-level (not availability) | **Fails**: BATCH-019/020 host gap and absent Verify body remain availability facts (AGENTS.md rule 5) |
| Forward-guidance class map | Not earned (obstruction unproven) |

The Verify-relativity **candidate** from BATCH-040 therefore remains an **open
hypothesis** — neither refuted (OUTCOME-R) nor proven (OUTCOME-D). This batch does
**not** elevate it to a §4 closure, and does **not** re-label the obstruction
analysis as a ninth `unverified` fatigue record as its primary disposition.

## 4. Outcome selection

**Selected: OUTCOME-N (`neither_pause`).**

- `reduction_exists: false`
- `dependence_essential_scoped: false`
- `named_obstruction: false`
- `meets_inventor_protocol_s4: false`
- `qm_stopping_lane: paused_pending_revisit`
- `ninth_unverified_rerecord: false`
- `verify_relativity_candidate_status: open_unresolved_not_refuted_not_proven`
- QM-STOPPING **control_result FAIL retained** (open problem; lane paused, not cleared)

### Revisit conditions (concrete)

1. **REV-1:** An admissible CollimationSieve pin that can host FC0 Verify/lifetime
   semantics without inventing APIs (superseding BATCH-020 `no_admissible_pin`).
2. **REV-2:** A committed host-independent mixing-time / re-randomization /
   collision-distribution result meeting OUTCOME-R (P,I,F,B,N).

Either revisit unblocks a fresh bounded attempt; until then, do not spend further
batches merely retaining FAIL / re-recording unverified on this lane.

## 5. Controls retained (non-claims)

- Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`
- QM-MEMORY-MAP: `numeric_composition_operator_protocol_toy_partial` (**retained**, not advanced)
- QM-ERROR: `f_union_ledger_partial`
- BATCH-020: `no_admissible_pin`; CollimationSieve@`6f9188e4` APIs **not** invented
- BATCH-022 scaffold **unmodified**; BATCH-014 **not** equated
- τ **not** invented; joint finiteness **not** established; no fake-τ gate B; toy
  peak-byte width lane **not** iterated; EXP-SSI-001 **not** launched
- No QUERY_MEMORY clearance, numeric-security, breakthrough, completion, or
  PIN_COMPLETE claim

## 6. Pareto honesty

- **`dominated_by`:** the GOAL-SSI-001 cryptanalytic frontier (supersingular
  isogeny / QUERY_MEMORY reconciliation). This document adds no time/memory/data
  frontier row for the hard problem.
- **`sota_delta`:** no attack; analysis-only — records a checked neither/pause for
  the host-independence reduction with revisit conditions.

## 7. Forward guidance (outside the paused lane)

With QM-STOPPING paused pending REV-1/REV-2, remaining QUERY_MEMORY blockers that
are still open under the same disposition include QM-ERROR (`f_union_ledger_partial`)
and the pin-blocked width-lane source-locate (still forbidden to invent values).
Coordinator next action is set at ledger archive; this producer does not choose
official state.
