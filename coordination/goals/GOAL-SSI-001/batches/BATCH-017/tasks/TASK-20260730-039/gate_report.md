# BATCH-017 recovery / object-lifetime gate report

Task `TASK-20260730-039` · GOAL-SSI-001 · IDEA-20260729-001  
Authority: `DEC-20260803-5d30b6` / `EV-SSI-016`  
Pinned process: `CollimationSieve@6f9188e4` via BATCH-012 `process_extraction.md`  
Schedule source: BATCH-013 `recovery_spec.md`

## Method

Control/derivation gate only (zero curve, isogeny, quantum-circuit, or
simulator computation; `maximum_runs: 1` symbolic package).

1. Read the unimplemented end-to-end recovery and common-error specification
   from BATCH-013 (`recovery_spec.md`).
2. Cross-check every named object class and stage live set against the pinned
   BATCH-012 process extraction of `src/Main.hs`.
3. For each `F_*` constituent, record inclusion status into common operational
   failure event `F`, Verify-predicate status, and any `F_sim → F` map.
4. Produce `lifetime_trace.yaml` and `component_to_F_map.yaml` as symbolic
   schedules — not numeric widths, probabilities, or security bits.
5. Update mutation/blocker status without clearing QUERY_MEMORY and without
   inventing a stopping-law artifact.

Inference: requested `executor-terra`; resolved Cursor Grok with
`fallback_used: true` under the Coordinator amendment
`inference-amendment-TASK-20260730-039.yaml`.

## Findings

### Object lifetimes (QM-MEMORY-MAP)

`recovery_spec` requires birth, last-use, cleanup precondition, and peak-stage
membership for `B_input`, `B_attempt`, `W_label`, `R_label`, `W_sieve`,
`R_sieve`, `B_sieve`, accepted transcript, `B_post`, `B_recovery`, `M_tail`,
and `B_candidate`, with stage live sets preparation / sieve attempt /
recovery / tail-verification.

Against the pinned report-only sieve:

- All twelve FC0 object classes remain **unimplemented / spec-only**.
- The only implemented analogue is the BATCH-012 **lexical**
  `PhaseVector` reference trace inside `sieve'`/`collimate` (C3 lexical
  subcase). That trace is explicitly not an FC0 `W`/`R`/`B`/`M_tail`
  schedule and supplies no widths or hard cleanup facts.
- Peak accounting therefore cannot convert retry counts into a global memory
  bound; the required cleanup facts are still missing.

### Error map (QM-ERROR)

Common event `F` is defined by true `Verify(x,k')` under a declared stopping
policy. The pinned artifact:

- does **not** implement `Verify(x,k')`;
- ends in a statistics report (`F_sim` / report-only completion), which
  `recovery_spec` classifies as failure relative to `F`, not success;
- has **no** implementation-derived `F_sim → F` implication;
- leaves every constituent
  `F_input ∪ F_oracle ∪ F_cleanup ∪ F_stop ∪ F_recovery ∪ F_tail ∪ F_verify ⊆ F`
  as a **checklist only**.

This matches — and does not soften — BATCH-012/013 honesty that the common
operational error map is uninstantiated.

### Stopping (QM-STOPPING)

No stopping-law artifact was produced in this batch. Local discard/retry in
the sieve is not an end-to-end stopping policy relative to `Verify`.
**QM-STOPPING remains open.**

## Relation to ttm-v2 panel (BATCH-016)

Retain the BATCH-016 / `EV-SSI-016` finite ideal-choice ttm-v2 panel
observations (including the red-team occupancy qualification: zp index
outcomes vs unique decide keys) as a separate, already-confirmed control
result under `DEC-20260803-5d30b6`.

- Do **not** equate BATCH-014 (`definitions_differ_not_equated` stands).
- Closing or failing this recovery/lifetime gate does not rewrite panel
  metrics; the panel neither supplies nor is replaced by W/R/B/M_tail or
  component-to-`F` maps.
- TTM-RETURN-MODULUS and TTM-REQUESTED-LENGTH remain closed as specification
  blockers only; they are not QUERY_MEMORY clearance.

## QM blocker status after this gate

| Blocker | Status after TASK-20260730-039 |
| --- | --- |
| QM-MEMORY-MAP | **Remains open** — gate executed; FC0 lifetimes still unimplemented against the pinned source |
| QM-ERROR | **Remains open** — gate executed; no Verify, no constituent inclusions, no `F_sim→F` map |
| QM-STOPPING | **Remains open** — no stopping-law artifact this batch |

QUERY_MEMORY remains unreconciled.
Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.

## Claim boundary

Supported statement (narrowest):

> Relative to `recovery_spec` and pinned `CollimationSieve@6f9188e4` process
> extraction, the recovery/object-lifetime gate produces a complete symbolic
> lifetime checklist and component-to-`F` residual-gap map showing that FC0
> W/R/B/M_tail lifetimes and common-error inclusions are still
> unimplemented/spec-only. Finite ideal-choice ttm-v2 panel observations are
> retained unchanged and are not equated with BATCH-014.

Excluded:

- numeric widths, peak-memory bounds, probabilities, security bits;
- HashDRBG equivalence or concrete-schedule reachability;
- global history-uniform stopping / finite joint Q/S/P/C;
- breakthrough, NIST-level, parameter recommendation, or goal completion;
- illicit QUERY_MEMORY clearance.
