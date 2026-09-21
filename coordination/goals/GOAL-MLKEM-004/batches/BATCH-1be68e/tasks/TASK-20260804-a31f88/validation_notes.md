# Validation Notes — TASK-20260804-a31f88

**Validating:** TASK-20260804-cbf6e2 (paired correlation test, BATCH-1be68e, GOAL-MLKEM-004)
**Snapshot commit:** `8b446af26e5658346ba25804e2f1f3181a533d4c`
**Validator session:** independent, `review-adversarial` (fallback: `amazon-bedrock/us.anthropic.claude-sonnet-4-6`)

---

## CHK-1: Hash Check — PASS

All 5 artifacts in `TASK-20260804-cbf6e2/` match their SHA-256 values in `TASK-20260804-75a516/snapshot_receipt.json` exactly:

| File | SHA-256 | Status |
|---|---|---|
| `paired_results.json` | `429cd19c...ff4c` | ✓ MATCH |
| `paired_test.py` | `009e99d8...fb5` | ✓ MATCH |
| `rebuild_transcript.txt` | `153f14ed...53d` | ✓ MATCH |
| `receipt.json` | `70eefd89...f05` | ✓ MATCH |
| `report.md` | `6f92206a...3ba` | ✓ MATCH |

Git verification: commit `8b446af2` is reachable from `HEAD`, has parent `8ccb165e` as declared, and introduces exactly these 5 files (5 files changed, 2264 insertions, 0 deletions). No other paths touched.

---

## CHK-2: Correlation Arithmetic — PASS

Independently loaded `TN_correct` and `TN_null` (50 values each) from `paired_results.json` and ran:

```
numpy.corrcoef(TN_c, TN_n)[0,1]  = 0.4394530638
scipy.stats.pearsonr:  r = 0.4394530638  p = 0.0014082291
scipy.stats.spearmanr: ρ = 0.4647779112  p = 0.0006727091
```

Against reported values:

| Statistic | Reported | Computed | Match |
|---|---|---|---|
| Pearson r | 0.4394530637542311 | 0.4394530638 | ✓ (< 1e-10) |
| Pearson p | 0.0014082291343110618 | 0.0014082291 | ✓ (< 1e-10) |
| Spearman ρ | 0.46477791116446576 | 0.4647779112 | ✓ (< 1e-10) |
| Spearman p (json) | 0.000672709105558213 | 0.0006727091 | ✓ (< 1e-10) |

**Minor discrepancy noted:** `receipt.json` records `spearman_p = 0.0006734396882165793`, which differs from `paired_results.json` and the independently computed value. Logged as Q-1. Does not affect any reported conclusion.

---

## CHK-3: Variance Arithmetic — PASS

All three variances recomputed from the raw arrays (ddof=1):

| Statistic | Reported | Computed | Match |
|---|---|---|---|
| Var[TN_correct] | 9096.83305821533 | 9096.83305822 | ✓ (< 1e-5) |
| Var[TN_null] | 14058.60224355432 | 14058.60224355 | ✓ (< 1e-5) |
| Var[TN_diff] | 13216.069451054067 | 13216.06945105 | ✓ (< 1e-5) |

Predicted Var[TN_diff] re-check: `17919 × (0.32933744 + 0.44572439) = 13888.333002` matches reported 13888.333002093548 ✓. Ratio 0.9516 confirmed ✓.

---

## CHK-4: Scope — PASS

- `states_a_finding: false` confirmed in `paired_results.json` and `receipt.json`
- `compared_against_matzov_nf: false` confirmed in both
- `rule12_status: "UNMET and UNWAIVED"` in both
- `report.md` §Interpretation states "This is an observation. The Coordinator assesses the implication."
- No claim, breakthrough, or MATZOV/Nf comparison present anywhere

The observed r = 0.4395 falls in the intermediate zone between both pre-registered thresholds (r ≥ 0.8 for H1; r ≤ 0.3 for H2). The experiment correctly records this as inconclusive and defers interpretation to the Coordinator.

---

## CHK-5: Variance-Identity Consistency — PASS

Using the identity `Cov[c,n] = (Var[c] + Var[n] - Var[diff]) / 2`:

```
Cov = (9096.833 + 14058.602 - 13216.069) / 2 = 4969.683
r   = 4969.683 / sqrt(9096.833 × 14058.602) = 0.4394530638
```

This matches the directly computed Pearson r to 10-digit precision. The variance triangle is fully consistent: no rounding artifact or post-hoc adjustment is present.

---

## Structural Observations (for Coordinator, not a validator determination)

The run reveals an interesting asymmetry: `Var[TN_correct] = 9097 < Var[TN_null] = 14059`. The executor's report correctly notes this runs counter to naive H2 expectations (genuine signal → more structure in the correct channel → higher variance), and flags it as an observation for the Coordinator. The positive covariance (Cov ≈ 4970, r ≈ 0.44) is inconsistent with pure H1 (environmental artifact would drive r → 1) but also inconsistent with pure H2 (wrong-secret decorrelation would drive r → 0). These are observations; their research interpretation is outside the Validator's remit.

---

## Summary

| Check | Result |
|---|---|
| CHK-1: Hash verification | ✓ PASS |
| CHK-2: Correlation arithmetic | ✓ PASS |
| CHK-3: Variance arithmetic | ✓ PASS |
| CHK-4: Scope (no finding asserted) | ✓ PASS |
| CHK-5: Variance-identity consistency | ✓ PASS |

**Verdict: `accept_with_qualifications`**

One minor qualification (Q-1: Spearman p discrepancy in receipt.json does not affect any metric). Run is admissible as an evidence record.
