# Validation report — `TASK-20260824-5b150a`

`GOAL-SSI-001` · `BATCH-eb0a7e` · independent Validator · `review-adversarial`
at `xhigh`

## Scope and review order

This report validates the snapshot-archived Executor package from commit
`9d003a7d27f1da41e4d2c638f9566891478d5e99`. The review is limited to arithmetic
on committed literals, code reading, artifact integrity, control capability,
anchor separation, and immutability. It is not an executed attack, certificate,
security assessment, standardized-parameter assessment, SQIsign/CSIDH claim,
or asymptotic-complexity result.

The corrected law was derived before opening the producer's conclusion. The
derivation used the frozen model's definition of full-memory time
(`specification.yaml:70`), its cap requirement (`specification.yaml:146-149`),
and the frozen implementation's executable expression (`cost_model.py:270`):
at full memory `w=M`, the vOW time must be `T_full`; reducing memory below `M`
must add a time penalty. Therefore, in the frozen log2 units, the corrected
law is

```text
log2 T_corr(w) = log2 T_full + c*sqrt(log2 p)
                  + 0.5*max(0, log2 M - log2 w)
```

Equivalently, before the overhead factor,

```text
T_corr(w) = T_full * sqrt(M / min(w, M)).
```

This is a ratio-anchored law: it equals `T_full` at `w=M` and increases as
memory is reduced. The frozen/null law instead subtracts a square root of a
memory count in log2 coordinates and fails the full-memory identity.

## Frozen law quotations

The three frozen artifact statements governing the defect are quoted verbatim:

1. Frozen implementation serialization:

   > `"T_w_vOW": "T_full / sqrt(min(w, M))",`

   Source: `experiments/EXP-WESOVOW-001/cost_model.py:236`.

2. Frozen run serialization:

   > `"T_w_vOW": "T_full / sqrt(min(w, M))",`

   Source: `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:13`.

3. Frozen specification cap requirement:

   > `description: At w = M, vOW time must equal T_full exactly (cap check).`

   Source: `experiments/EXP-WESOVOW-001/specification.yaml:149`.

The executable implementation agrees with the serialized implementation law:
`cost_model.py:270` computes
`log2T_w = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits`. The frozen
specification also requires monotonicity and equality to `T_full` at or above
the cap (`specification.yaml:146-147`). Thus the defect is localized to the
charging-law anchor, not to a disagreement between the frozen code and the
frozen raw serialization.

## Snapshot and artifact integrity

- The snapshot receipt is
  `coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/archives/TASK-20260824-e8f6b7/snapshot_commit_receipt.json`.
- Its five declared producer hashes match the files in the worktree and the
  blobs in snapshot commit `9d003a7d27f1da41e4d2c638f9566891478d5e99`.
- The snapshot commit changes exactly six paths: the five producer artifacts
  and the snapshot receipt. No path under `experiments/EXP-WESOVOW-001/` is in
  that commit.
- The receipt's `archive.commit_sha` is intentionally `null` because the
  receipt is itself hashed into its containing commit; the receipt records
  parent `bd47a3f5c6915ed7118f74e679c37e2f580fb95d` and the five source hashes.
  The authoritative archive commit is the verified Git commit named above.
- The snapshot commit is an ancestor of `HEAD`.
- The scoped worktree checks showed no modification under
  `experiments/EXP-WESOVOW-001/` and no modification to the snapshot-bound
  producer package before this report was written.

The five producer artifacts were read from the snapshot commit, not from an
unarchived sibling review or an independent producer working copy:

```text
defect_localization.md
corrected_charging.py
recomputed_table.json
control_report.md
anchor_sensitivity.md
```

## Independent law and table checks

The prior independent recomputation parsed the full snapshot-bound
`recomputed_table.json` and the frozen `raw-result.json`; it was not rerun in
this resumed turn. It found:

- 240 rows total, exactly 120 `fitted_opt` rows and 120 `PAPER_PAIRS` rows;
- complete field-size grid `{256, 384, 512, 576, 768}`;
- complete memory grid `log2(w) = {30, 40, 50, 60, 70, 80}`;
- complete overhead grid `c = {0.0, 0.5, 1.0, 2.0}`;
- zero mismatches above `2e-12` for corrected time, committed/null time,
  overhead bits, speedup, or crossover against the independently evaluated
  formulas.

The two anchors remain separate throughout:

| Anchor | Time source | Memory source |
|---|---|---|
| `fitted_opt` | `RUN-WESOVOW-001/raw-result.json`, each `per_field[log2p=*].optimal.log2T` | the corresponding `optimal.log2M` |
| `PAPER_PAIRS` | `experiments/EXP-WESOVOW-001/cost_model.py:60-65` | the corresponding second component of each committed pair |

No row uses a time value from one anchor with a memory value from the other.
Every row carries an anchor label and a corresponding source string.

## RG-1, RG-2, and RG-3 control capability

The following are concrete hypothetical failing inputs. They were not applied
to the immutable artifacts; they demonstrate that each control has a reachable
negative branch.

### RG-1 — committed-law reproduction

Verdict: `CONFIRMED`.

The control recomputes all 120 frozen/null cells and fails on a missing cell or
on any absolute difference greater than `1e-9`. For a concrete failing input,
change only

```text
raw.per_field["log2p=256"].van_oorschot_wiener["w=2^30"]["c=0.0"].log2T_w
```

from the committed `93.73088958800618` to `93.73089058800618`. The expected
value is unchanged and the difference is `1e-6`, which is greater than the
declared tolerance, so RG-1 would return `FAIL` and stop before writing a
corrected table. The observed snapshot value reproduces the committed law
exactly under the stated tolerance.

RG-1 is a reproduction gate, not a proof that the reproduced law is the right
law. That semantic role is supplied by RG-2 and RG-3.

### RG-2 — cap control at `w=M`

Verdict: `CONFIRMED WITH CAVEAT`.

The control evaluates both laws at exact `log2(w)=log2(M)` for both anchors
and all five field sizes. It would return `FAIL` on a finite, concrete input
such as changing the `PAPER_PAIRS` memory anchor for `log2(p)=256` from `92.5`
to `0.0`: at the resulting `w=M`, the committed/null law equals `T_full`, so
`committed_null_detected_as_non_cap` becomes false and the overall RG-2 status
fails. It would also fail if a corrected-law cap value differed from `T_full`
at any row.

The caveat is structural: because RG-2 passes the same `log2M` value as both
the anchor and the exact cap input, the corrected identity is algebraically
built into `corrected_law`. RG-2 discriminates the frozen wrong law from the
cap requirement, but it does not independently validate the provenance or
correctness of the numerical `log2M` anchor.

The observed result is consistent with the control report: 10 rows checked,
the corrected law equals full time in all rows, and the frozen/null law is
distinct from full time in all rows.

### RG-3 — null-law discrimination

Verdict: `CONFIRMED`.

RG-3 compares the corrected law with the frozen/null law at its fixed probe
`log2(w)=30`, `c=0`, for both anchors and all five field sizes. It would return
`FAIL` on a concrete input with any one anchor's `log2M=0.0`: at the probe,
both laws then equal `log2T_full`, making their difference exactly zero, which
is at or below the `1e-12` rejection threshold. A non-discriminating output is
therefore reachable and is explicitly rejected by the control.

The observed ten-row result discriminates in every row. RG-3 is a null
discrimination control at one low-memory probe; it is not, by itself, a proof
that every point of the full grid has been independently discriminated.

## Rounding robustness

The full-grid recomputation used the committed literal values rather than
displayed rounded summaries. The closest absolute corrected speedup margin in
the 240 rows is `0.2` bits (`PAPER_PAIRS`, `log2(p)=384`, `log2(w)=70`,
`c=0.0`), and there were no sign changes after rounding the speedups to one or
two decimal places. Replacing fitted-opt anchor values by their two-decimal
execution-report renderings also produced no sign changes.

At the specifically prohibited P=512 endpoint, `log2(w)=80`, `c=0`, the
corrected speedups are approximately:

```text
fitted_opt:  -0.821813076553 bits
PAPER_PAIRS: +1.150000000000 bits
```

The opposite signs are therefore not a rounding artifact. They arise from the
different committed anchors; neither anchor is silently substituted for the
other.

## Frozen experiment immutability

No file under `experiments/EXP-WESOVOW-001/` was modified by this batch. The
immutability check is supported by all of the following read-only evidence:

1. The snapshot commit's exact path diff contains no experiment path.
2. The frozen experiment subtree was clean in the scoped worktree status/diff
   check before this report was created.
3. The producer script reads the frozen raw result and writes only to its
   declared task directory; the frozen experiment implementation, specification,
   and run artifacts remain unchanged.

## Per-deliverable verdicts

The verdict strings below are exactly the task-card vocabulary.

| Deliverable or bound artifact | Verdict | Basis |
|---|---|---|
| `defect_localization.md` | `CONFIRMED` | Correctly identifies the single count-versus-ratio anchor defect, quotes the three frozen statements, and preserves the arithmetic-only scope. |
| `corrected_charging.py` | `CONFIRMED` | Implements the independently derived ratio-anchored law, keeps both anchors separate, and contains reachable failure branches for RG-1/RG-2/RG-3. |
| `recomputed_table.json` | `CONFIRMED` | All 240 rows and all reported formulas independently recompute from committed literals with zero mismatch above `2e-12`. |
| `control_report.md` | `CONFIRMED WITH CAVEAT` | The recorded control values and verdicts are arithmetically consistent and the controls can fail, but this validation did not rerun the producer command or independently attest to its historical wall-clock execution. RG-2's corrected-cap identity is also algebraically constructed from its cap input. |
| `anchor_sensitivity.md` | `CONFIRMED` | Anchor definitions, crossover values, endpoint signs, and full-grid sensitivity agree with the independently checked table. |
| `snapshot_commit_receipt.json` | `CONFIRMED` | Its declared source hashes and parent binding agree with the verified snapshot commit; the null self-commit field is explained by the receipt's self-hash construction. |

## Concrete objections and limitations

1. RG-2 does not independently validate the `log2M` measurements: it tests a
   law at an input constructed to be exactly `w=M`. A wrong memory anchor could
   still make the corrected cap identity pass.
2. RG-3 probes only `log2(w)=30`; its reachability and ten-row discrimination
   do not alone establish a universal control over the six-budget grid.
3. The two anchors give materially different P=512 crossover behavior. The
   arithmetic package therefore cannot choose which anchor should support a
   citation or official interpretation.

These are objections to the strength and scope of the validation, not
refutations of the corrected arithmetic. No attack, security, standardized
parameter, or asymptotic conclusion follows from this package.

## P=512 citation boundary and recommendation

The prohibition is preserved verbatim:

> The `P=512` crossover value and its `w=2^80` sign are **NOT citation-eligible**. This task does not lift that prohibition. Only a committed Coordinator decision on independently reviewed evidence can lift it.

Recommendation only: do **not** lift the P=512 prohibition at this stage.
The reason is the independently confirmed anchor separation and the opposite
`w=2^80,c=0` signs (`-0.8218` versus `+1.15` bits), not a rounding issue.
This is a Validator recommendation and is not a Coordinator decision or a
research-state transition.

## Validation summary

```yaml
validation_report:
  id: VAL-20260824-5b150a
  task_id: TASK-20260824-5b150a
  run_ids:
    - RUN-WESOVOW-001
  artifact_checks:
    - snapshot_commit_9d003a7d27f1da41e4d2c638f9566891478d5e99_verified
    - five_producer_hashes_match_snapshot_receipt
    - snapshot_diff_contains_no_frozen_experiment_path
    - frozen_experiment_subtree_clean_before_report
  metric_recomputations:
    - 240_rows_recomputed_from_committed_literals
    - zero_formula_mismatches_above_2e-12
    - fitted_opt_and_PAPER_PAIRS_anchor_sets_kept_disjoint
    - rounding_checks_produced_no_sign_changes
  control_checks:
    - RG-1: CONFIRMED
    - RG-2: CONFIRMED WITH CAVEAT
    - RG-3: CONFIRMED
  heuristic_validation_checks: []
  cost_model_checks:
    - arithmetic_only
    - no_attack_or_security_claim
    - P=512_citation_prohibition_preserved
  proof_architecture_checks: []
  verdict: passed
  limitations:
    - RG-2_cap_identity_is_algebraically_constructed_at_the_supplied_log2M
    - RG-3_uses_one_low_memory_probe
    - P=512_behavior_is_anchor-dependent_and_not_citation-eligible
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md
```

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260824-5b150a
  joints_owned:
    - snapshot and frozen-artifact integrity
    - corrected charging-law arithmetic
    - RG-1/RG-2/RG-3 capability to fail
    - fitted_opt versus PAPER_PAIRS separation
    - rounding robustness and P=512 boundary
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - docs/task-lifecycle.md
    - docs/dynamic-subagent-dispatch.md
    - docs/claims-and-verification.md (relevant refutation-artifact sections)
    - templates/research-records.md (review-attestation section)
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/task-cards/TASK-20260824-5b150a.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/batch.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/dispatch_queue.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/dispatch/plan.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/dispatch/report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/archives/TASK-20260824-e8f6b7/snapshot_commit_receipt.json
    - snapshot commit 9d003a7d27f1da41e4d2c638f9566891478d5e99: five producer artifacts under TASK-20260824-dd5b5c
    - experiments/EXP-WESOVOW-001/cost_model.py
    - experiments/EXP-WESOVOW-001/specification.yaml
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/manifest.yaml
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/execution_report.yaml
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/stdout.txt
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/stderr.txt
    - ledger/corrections/CORR-20260808-c792f8.yaml
    - ledger/evidence/EV-WESO-001.yaml
  read_sibling_reports: false
  blind_from_respected: null
  verdict: holds
```
