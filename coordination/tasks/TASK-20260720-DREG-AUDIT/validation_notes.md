# VAL-20260720-DREG-AUDIT — validation notes

Independent integrity/consistency audit of the immutable n=17 DREG receipt set for
H-DREG-001. This companion explains the grounding for each check. No official status
was changed and nothing was written outside this task directory. All six checks pass;
no material defect was found. Numbers only — no significance interpretation.

## What was verified against the raw files (not the task summary)

Every sha256 quoted in the manifests and the two partition-comparison JSONs was
recomputed with `shasum -a 256` and matched byte-for-byte (raw results, checkpoint
`state.json` files, instrument-result, parent checkpoint). Every terminal metric was
read from the run `raw-result.json` / `manifest.yaml` and, additionally, reconstructed
from the per-unit pivot ledger inside each `state.json` (`sum_k == rank`).

## Check 1 — SEM two-partition gate: PASS

- `runs/RUN-DREG-001-MEASURE-N17-SEM-A/raw-result.json` and `.../SEM-B/raw-result.json`
  both report `rank 125099`, `pred 126922`, `deficit 1823`, `ncols 314472`,
  `nrows 132719`, `system_hash 5f94c88f…9411082`. Identical across A and B.
- Committed values in the task match the files exactly.
- Both partitions processed all columns: `state.json` `next_col == ncols == 314472`;
  per-unit pivots sum to 125099 in both (A: 14 units; B: 16 units).
- `n17-sem-partition-comparison-v1.json`: `equal_result_fields` all `true`,
  `equal_code_fields` all `true`, `partitioning_independent: true`,
  `status: partition_replication_verified`, both partitions `verification: verified`.
  `terminal_metrics` block matches the committed numbers.

## Check 2 — NULL two-partition gate: PASS

- NULL-A (`chunk 24000`) and NULL-B-CONT-1 (`chunk 20000`) both report `rank 126922
  == pred 126922`, `deficit 0`, `ncols 384168`, `system_hash 5deee45d…c06471`.
  `null_partition_equal_fields` all `true`.
- Both processed all 384168 columns (`state.json` `next_col == 384168`; pivots sum
  to 126922). CONT-1 `raw-result.json` `processed_columns: 384168`, `n_units: 20`.
- The continuation lineage is genuine: CONT-1's `state.json` units 0–17 are byte-identical
  (same boundaries and timings) to the parent NULL-B units 0–17, then two additional
  units carry columns [360000,384168). Parent checkpoint sha256
  `2aabf51b…bd1e` in the CONT-1 manifest equals the NULL-B manifest `checkpoint_state`.
- Parent NULL-B is correctly excluded: `raw-result.json` `status: cancelled_by_budget`,
  `measurement_complete: false`, `evidence_admissible: false`,
  `processed_columns 360000 / 384168` (`remaining 24168`); manifest `result.valid: false`,
  `invalid_reason: full_column_acceptance_gate_unmet_after_budget_boundary`.
  Note its checkpoint rank telemetry already equaled 126922 at column 360000, yet it is
  still excluded because the full-column gate was unmet — correct discipline.
- `n17-null-partition-comparison-v1.json` records `status:
  continuation_and_null_partition_verified`, `parent.evidence_admissible: false`.

## Check 3 — deficit series consistency: PASS

- SEM D=5 full-exact series: deficit `1322 / 1862 / 1823 / 1999` at n = `12 / 15 / 17 / 18`.
- `deficit == sr_pred − rank` reproduces exactly at every n (e.g. 126922 − 125099 = 1823;
  29418 − 28096 = 1322; 70935 − 69073 = 1862; 145881 − 143882 = 1999).
- Relative deficit `deficit/rank`: 1322/28096 = 4.71%, 1862/69073 = 2.70%,
  1823/125099 = 1.46%, 1999/143882 = 1.39% — matches the committed percentages.
- Increments `+540 / −39 / +176`; non-monotone at the n=17 insert. n=17 is 39 below n=15
  and 176 below n=18, matching EV-DREG-003 verbatim.
- EV-DREG-002 and EV-DREG-003 agree on the n=17 triple (125099 / 126922 / 1823).
  EV-DREG-001 carries n=17 only as a prediction (sr_pred 126922, review-correction C1,
  explicitly censored/unmeasured at that time) — this is the pre-measurement state, not a
  contradiction with the later measured records.

## Check 4 — d_reg-not-reached caveat: PASS

- `nrows = 132719` for both arms at (n=17, D=5).
- SEM rank 125099 < 132719 (row deficit 7620); NULL rank 126922 < 132719 (row deficit 5797).
- Therefore the Macaulay matrix is **not** full row rank at D=5 for either arm, so the
  degree of regularity is **not reached** at D=5. The measured 1823 is a rank-deficit at a
  **fixed degree D=5**, not a measured difference in solving degree; `d_reg(sem) < d_reg(null)`
  is not evaluable from these cells. EV-DREG-002 states the same
  ("d_reg NOT reached at D=5 for either arm at n=17").

## Check 5 — sr_pred cross-validation: PASS

- The semi-regular prediction 126922 is corroborated empirically: the T11 support-matched
  null (constructed to be semi-regular) measures rank **exactly** 126922 (deficit 0) in
  both NULL-A and NULL-B-CONT-1 and in the null comparison JSON.
- The prediction is a computed formula, not a hard-coded constant:
  `code/h012_peel_rank.py` lines 50–67 (`semireg_rank_pred`) builds the truncated
  semi-regular Hilbert series over the Boolean ring from the equation degree multiset
  `eq_degs` and `nb=35`, truncating at the first non-positive coefficient, then
  `pred[D] = Σ_{d≤D} (C(nb,d) − HF[d])`.
- I did **not** independently re-derive 126922 from the Hilbert series: the equation degree
  multiset `eq_degs` is not exposed as a receipt field (it is produced inside the instrument),
  so re-derivation is not cheap from the receipts alone. Reliance is therefore placed on the
  exact null cross-check, which pins the prediction to the integer.

## Check 6 — hash/provenance integrity: PASS

- All nine recomputed sha256 values match their manifest/comparison-JSON claims
  (SEM-A/B raw + checkpoint, NULL-A raw + checkpoint, CONT-1 instrument-result +
  successor checkpoint + parent checkpoint). The CONT-1 parent checkpoint hash equals the
  NULL-B checkpoint hash, closing the continuation chain.
- Comparison JSONs: no field is marked unequal; `equal_result_fields`,
  `equal_code_fields`, and `null_partition_equal_fields` are uniformly `true`;
  `verification: verified`.
- Every run receipt carries the required provenance: `command.txt`, `commit`
  (+ dirty-status hash), `environment.json`, `seed=2026`, `raw-result.json`, a
  `validity_status` (`status` + `result.valid`), the instrument sha256 and four pinned
  dependency sha256 (identical across all five runs). No run dir is missing a required
  artifact.

## Non-blocking observations (not defects)

1. `n17-sem-partition-comparison-v1.json` `interpretation_status:
   "withheld_pending_null_A_and_B"` is a stale label from before the null arm completed;
   the same file's `status` already reads `partition_replication_verified`. Cosmetic lag
   only — no numeric field affected.
2. `carrier_files` differ between null_a (11) and CONT-1 (13) — an expected artefact of the
   different chunk sizes (24000 vs 20000); ranks identical.
3. The cancelled parent NULL-B appears in EV-DREG-002/003 `run_ids` but is uniformly
   documented as inadmissible checkpoint-lineage telemetry. Consistent, correct exclusion.
4. CONT-1 manifest self-discloses that its prelaunch hash-check receipt was serialized
   after launch (parent checkpoint immutable; no measurement/parameter/hash changed).
   Non-material to the exact rank; also noted in EV-DREG-003 boundaries.

## Overall

`receipt_integrity: verified`. The n=17 DREG receipts are internally consistent and
hash-clean: both two-partition gates pass, the deficit series and its three EV records
reconcile, the D=5 rank-deficit is correctly framed as a fixed-degree quantity (not a
solving-degree difference), and sr_pred = 126922 is exactly corroborated by the
semi-regular null.
