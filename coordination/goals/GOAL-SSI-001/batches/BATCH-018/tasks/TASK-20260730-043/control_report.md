# Control report — TASK-20260730-043 (BATCH-018)

## Method

Zero-compute literature/accounting control. One worksheet. No curve, isogeny,
or quantum-circuit execution. No numeric security bits invented.

1. Restate the QM-STOPPING pass rule: a Verify-relative stopping time \(\tau\)
   covering recursive discards, retries, recovery runs, residual entry, and
   \(F_{\mathrm{stop}}\); plus jointly finite
   \(\mathbb{E}\sum Q\), \(\mathbb{E}\sum S\), \(\mathbb{E}\sum P\),
   \(\mathbb{E}[\sum C+H]\) on one probability space.
2. Reuse pinned Peikert source facts from BATCH-011
   (`TASK-20260730-009`) and the CollimationSieve@6f9188e4 report-only pin;
   do not re-fetch PDF bytes or re-run sieve code.
3. Incorporate BATCH-013 `recovery_spec.md` only as type obligations
   (`Verify`, \(F\), \(F_{\mathrm{stop}}\)).
4. Bound ttm-v2 panel scope from BATCH-016: retain finite ideal-choice
   one-retry horizon observations; refuse inflation to a global stopping law,
   HashDRBG model, or Verify-relative \(\tau\).
5. Score each Q/S/P/C(+H) field as
   `instantiated_source | partial_local | not_instantiated` in
   `joint_qspc_ledger.yaml`.
6. Record PASS/FAIL honestly. Do not clear QM-MEMORY-MAP or QM-ERROR.

Git revision at execution: `6147617350209909f733a3afabd6690221ad9ea2`
(launch tip). Inference: requested `executor-terra`, resolved Cursor Grok,
`fallback_used: true` under
`inference-amendment-TASK-20260730-043.yaml`.

## Relation to prior batches

| Prior | Role here |
|---|---|
| BATCH-011 TASK-009 | Prior FAIL control; pass rule and Peikert page anchors reused; C2 remains NOT REJECTED |
| BATCH-013 recovery_spec | Supplies Verify-relative \(F\) / \(F_{\mathrm{stop}}\) type obligations sharpening \(\tau\); not an instantiation |
| BATCH-016 ttm-v2 panel | Supplies bounded one-retry ideal-choice horizon only; explicitly not HashDRBG / not global stopping / not QUERY_MEMORY clearance; not equated to BATCH-014 |
| BATCH-017 + RT-041 | Lifetime/error gate executed; MEMORY/ERROR still open; “gate ≠ clearance”; QM-STOPPING still needed a separate artifact — this task |
| DEC-20260730-015 / EV-SSI-017 | Authorize this stopping-law artifact; keep MEMORY/ERROR open; retain UNRECONCILED |

## QM blocker status after this control

| Blocker | Status | Rationale |
|---|---|---|
| QM-STOPPING | **open** | Control executed and **FAILED**: \(\tau\) and joint finiteness not source-instantiated |
| QM-MEMORY-MAP | **open** | Out of clearance scope; BATCH-017 maps remain unimplemented |
| QM-ERROR | **open** | Out of clearance scope; Verify / \(F_*\) inclusions remain unimplemented |

Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.

## Claim boundary

Supported observation only:

> Relative to pinned Peikert extraction (BATCH-011), CollimationSieve@6f9188e4,
> recovery_spec type obligations, and ttm-v2’s finite ideal-choice one-retry
> panel, no source-compatible Verify-relative stopping time \(\tau\) and no
> jointly finite Q/S/P/C(+H) expectations are instantiated. The separate
> stopping-law control therefore **FAIL**s; QM-STOPPING stays open.

Excluded (not claimed):

- invented joint finiteness or security bits;
- HashDRBG equivalence;
- global history-uniform stopping from ttm-v2;
- Verify implementation or \(F\) probability bounds;
- QM-MEMORY-MAP / QM-ERROR clearance;
- BATCH-014 equivalence;
- numeric / breakthrough / goal-completion claims;
- QUERY_MEMORY clearance.

## Artifacts

- `stopping_law_artifact.md`
- `joint_qspc_ledger.yaml`
- `control_report.md` (this file)
- `mutation_status.yaml`
- `classification.yaml`

No git commit performed by the Executor.
