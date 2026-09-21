# Validation Notes — TASK-20260804-b1a981

**Validator task:** TASK-20260804-b1a981  
**Producer task:** TASK-20260804-ff2c2b  
**Snapshot commit:** 4d5defb29cbdc012dfe9180827b7f397f6bde135  
**Validated at:** 2026-08-04

---

## CHK-1 — Hash Check (PASS)

All 6 artifacts in `TASK-20260804-ff2c2b/` were hashed with `sha256sum` and compared
against the receipt in `TASK-20260804-752e83/snapshot_receipt.json`.

| File | Hash match |
|------|------------|
| null_control_results.json | ✓ |
| null_variance_test.py | ✓ |
| outlier_rerun_results.json | ✓ |
| rebuild_transcript.txt | ✓ |
| receipt.json | ✓ |
| report.md | ✓ |

Git commit `4d5defb2` is reachable from HEAD, has parent `87ac359c` as declared in
the snapshot receipt, and the commit diff changes exactly the 6 declared files.

---

## CHK-2 — Null Variance Arithmetic (PASS)

Recomputed from the 50 `TN_null_values` in `null_control_results.json` using
`numpy` (ddof=1) and `scipy.stats.chi2`.

All values agree to full floating-point precision:

| Metric | Reported | Recomputed | Match |
|--------|----------|------------|-------|
| empirical_var | 12262.225820492231 | 12262.225820492231 | ✓ |
| null_predicted_var | 7997.993269383342 | 7997.993269383342 | ✓ |
| variance_ratio_null | 1.5331628081549598 | 1.5331628081549598 | ✓ |
| chi2_stat | 75.12497759959302 | 75.12497759959302 | ✓ |
| p_value_null | 0.00958945247464682 | 0.009589452474647 | ✓ |
| CI lower | 1.069814803909017 | 1.069814803909017 | ✓ |
| CI upper | 2.3807693387011173 | 2.3807693387011173 | ✓ |

The chi2 test uses `chi2_stat = (n-1) × empirical_var / null_predicted_var` and the
right-tail p-value, which is the standard one-sided test for variance inflation.
The 95% CI uses the pivot `[chi2_stat / chi2.ppf(0.975, 49), chi2_stat / chi2.ppf(0.025, 49)]`.

---

## CHK-3 — Outlier Seed Reproducibility (PASS)

Cross-referenced the batch-3 reference values from
`BATCH-68471b/tasks/TASK-20260804-52cc2b/variance_results.json` (the original
batch-3 executor output):

| Seed | Batch-3 T_N | Rerun T_N | Delta |
|------|-------------|-----------|-------|
| 2941775225 | 7789.567405817314 | 7789.567405817314 | 0.000 |
| 26883012 | 7791.775311646041 | 7791.775311646041 | 0.000 |
| 2418421570 | 7789.812131511126 | 7789.812131511126 | 0.000 |
| 1873347320 | 7420.548667265 | 7420.548667265 | 0.000 |

All four seeds reproduce to floating-point identity. The QEMU linux/amd64 environment
is confirmed deterministic given the same g6k version, seeds, and LWE instance.

---

## CHK-4 — Wrong-Secret T_N Plausibility (PASS WITH NOTE)

Wrong-secret T_N values [4167.083, 4433.895, 4238.163, 4178.842] compared against
the null distribution from Test A (n=50, mean=4175.508, std=110.735):

| Seed | T_N_correct | T_N_wrong | Z vs null | Plausible? |
|------|-------------|-----------|-----------|------------|
| 2941775225 | 7789.567 | 4167.083 | −0.08 | ✓ |
| 26883012 | 7791.775 | 4433.895 | +2.33 | ✓ (high end, plausible) |
| 2418421570 | 7789.812 | 4238.163 | +0.57 | ✓ |
| 1873347320 | 7420.549 | 4178.842 | +0.03 | ✓ |

All T_N_wrong << T_N_correct (ratio 1.76–1.87), confirming the elevated batch-3 values
are specific to correct-secret scoring. Per-vector cosine for wrong secret ≈ 0.233 vs
≈ 0.435 for correct secret. The wrong secret (23/25 coordinates differing) scrambles
phases effectively, pulling T_N down to the null distribution range.

**Qualification Q-1 flagged:** The `interpretation_note` in `outlier_rerun_results.json`
states:

> "T_N_wrong is a null object control: expected near batch-3 T_N mean (~7551) if
> wrong-secret scores are unstructured."

This is **inverted**. If wrong-secret scores are unstructured (no residual signal),
T_N_wrong should be near the **null mean (~4175)**, not the correct-secret mean (~7551).
A T_N_wrong close to 7551 would indicate the wrong secret is *not* being distinguished
from the correct one — a suspicious bug condition, not the expected unstructured behavior.

The observed data (T_N_wrong ≈ 4200, near null mean) is **correct and expected**.
The misstatement is in the descriptive note only and does not affect any computed metric.

---

## CHK-5 — Scope Check (PASS WITH NOTE)

- `states_a_finding = false` in all three JSON files. ✓
- `compared_against_matzov_nf = false` in all three JSON files. ✓
- No MATZOV or Nf comparison content found in any artifact. ✓
- `report.md` explicitly states "No finding is stated." in both test sections. ✓
- `receipt.json` carries `rule12_status: UNMET and UNWAIVED`. ✓

**Qualification Q-2 flagged:** `receipt.json` field `mean_TN_null = 4163.0` differs
from the computed mean in `null_control_results.json` (4175.508). The report labels
this "~4163", signalling an estimate. The discrepancy is 12.5 and does not affect
any reported test statistics (variance_ratio, chi2, p-value, CI are all computed from
empirical_var / null_predicted_var, not from the mean). `null_control_results.json`
is the authoritative source.

---

## Summary of Findings

| Check | Result |
|-------|--------|
| CHK-1: Hash check | **PASS** — all 6 hashes match |
| CHK-2: Null variance arithmetic | **PASS** — exact agreement |
| CHK-3: Outlier seed reproducibility | **PASS** — floating-point identity confirmed |
| CHK-4: Wrong-secret T_N plausibility | **PASS WITH NOTE** — Q-1: inverted description in metadata |
| CHK-5: Scope | **PASS WITH NOTE** — Q-2: rounded mean in receipt.json |

**Verdict: `accept_with_qualifications`**

Both qualifications (Q-1 inverted description; Q-2 rounded mean) are minor
metadata issues that do not affect any computed metric. All data, statistics,
and test outputs are arithmetically verified and consistent. The artifact set
is admissible as an evidence input for Coordinator assessment.

---

## Interpretation Note (for Coordinator)

This validation confirms the arithmetic integrity of the run. It does not interpret
the scientific significance of variance_ratio_null = 1.5332 (p = 0.0096, n=50).
That assessment — specifically whether the null control's variance inflation is
comparable to the correct-secret inflation in batch-3 — belongs to the Coordinator
and Reviewer. The 95% CI overlap between null [1.07, 2.38] and batch-3 correct
[1.12, 1.77] is substantial, as noted in the report.
