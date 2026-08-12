# Falsification review — TASK-20260730-035

## Verdict

**CONFIRM.** Durable ttm-v2 preregistration precedes the panel audit; the
return-modulus and requested-length repairs are total and used; real
frame-by-frame all-zero-tape traces exist (including S=5 on `[1,2,5,8]`);
finite ideal-choice S=2 metrics recompute; BATCH-014 is not equated; and
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` remains supported. Non-blocking
qualifications only: published `zero_progress_occupancy: 946` counts index
outcomes (558 unique decide keys), and the
`jointly_reachable` / `recurrent` booleans are audit-operationalized rather
than formally defined in the preregistered text.

Inference: requested `review-xhigh`; resolved **Cursor Grok 4.5** with
`fallback_used: true` because review-xhigh was unavailable (API limit /
policy unavailable); `independent_session: true` (this session did not
originate TASK-20260730-031 or TASK-20260730-033).

## Durable ordering and panel

Git independently establishes that
`1801e2a512158c803d424d480eb15f6417ac01a3` is an ancestor of both
`3b90c3cd3ab667187f7797bc2cc21820a207c488` and review-bind HEAD
`56104051ae1f1470c1b941d986a81ad3b037b96f`. The preregistration commit
changes exactly:

- `schedule_panel.yaml`
- `tape_machine_spec_v2.md`
- `preregistration_manifest.yaml`
- the TASK-20260730-032 snapshot receipt

No analysis result is present. Receipt SHA-256 values recomputed from
`git show` match. Both receipts still say `pending_post_commit` with null
`commit_sha`, but direct ancestry, changed-path, and hash checks establish
the two reviewed snapshots. Audit-path hashes in TASK-20260730-034 also
match.

Schedule arithmetic under the pinned construction yields `[1,2,4]` and
`[1,2,5,8]` as preregistered.

## Attack surface results

| Attack | Result |
|---|---|
| Incomplete reduce-mod-parent | **Falsified.** Spec is total; traces and explorer apply it on every labeled keep-return (0 coercion mismatches). |
| Incomplete requested-length vs ttm-v2 | **Falsified.** Left/right propagation and length-indexed BaseDraw counts match the frozen text, including empty-draw `(0)`. |
| Fake / aggregate-only traces | **Falsified.** 53 / 114 real stack events with history, phase, tape position, symbols, and return stores. |
| Missing S=5 frames on `[1,2,5,8]` | **Falsified.** Four enter frames at `r=2`, `modulus=5` appear between S=2 and base S=8. |
| Illicit global-tail inference | **Not detected.** C2 remains live; finite-panel labels exclude global stopping. |
| Premature QUERY_MEMORY clearance | **Not detected.** Disposition retained with QM-STOPPING / QM-MEMORY-MAP / QM-ERROR. |
| Numeric / breakthrough / completion / parameter creep | **Not detected.** |
| Prereg not ancestor / contains analysis | **Falsified.** Ancestor relation holds; no analysis paths in 1801e2a5. |
| Disposition unsupported | **Falsified.** Disposition supported. |
| Row metrics equated to BATCH-014 | **Falsified.** `definitions_differ_not_equated` with honest rationale. |

## Metric recompute

Independent `TTMV2.audit_row()` recomputation matches committed results for
both rows, including pair counts, zp index-outcomes, keep minima, and the
boolean reachability flags. For `[1,2,5,8]`, zp index-outcomes = 946 while
unique `(ell, rc, v1, v2, q, v)` keys = 558 (also reported as
`S2_states_with_at_least_one_discarding_index_outcome`).

## Why CONFIRM rather than REVISE

BATCH-015 required REVISE because the producer sold a static modulus
checker as recursive execution and omitted the S=5 frame. Those defects are
repaired under preregistered ttm-v2. Remaining issues are wording
qualifications for the Coordinator ledger archive, not blockers of the
finite-panel claim or of the continued QUERY_MEMORY disposition.

## Scope and disposition

No Pollard-rho, BSGS, or specialized-baseline resource comparison is
admissible. Peikert's CollimationSieve remains the closest specialized
baseline, unchanged by this auxiliary formalization. KN-TECH-051 /
KN-OPEN-014 remain the locus of CSIDH quantum-security dispute; this panel
supplies no security number.

Recovery, source recovery, target descent, relation/rank analysis,
object-lifetime tracing, and final verification remained out of scope and
were not performed.

## Narrowest supported conclusion

The two-row panel and ttm-v2 were durably preregistered before analysis.
Under that machine, both rows have real recursive zero-tape traces and
finite ideal-choice S=2 metrics as reported, with zp occupancy understood
as index-outcome count (946) beside 558 unique decide keys on the second
row. BATCH-014 is not equated. QUERY_MEMORY remains unreconciled; no
broader cryptanalytic or completion conclusion follows.

## Recommended Coordinator action

Ledger-archive CONFIRM: adopt the scoped finite observations, quote the
occupancy qualification, retain
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`, keep recovery/object-lifetime as
a separate gate, and make no numeric-security, breakthrough, or
GOAL-SSI-001 completion claim.
