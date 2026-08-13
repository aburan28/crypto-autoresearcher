# TASK-20260804-5ea2da — Validation Notes
## Gauss Sieve Final Control (BATCH-e87ab3, Batch 6 of 6)

**Validator task:** TASK-20260804-5ea2da  
**Producer task:**  TASK-20260804-478b74  
**Snapshot commit (receipt):** `891f85dd6060ef55e3c9b87e91c38e851c0e6c89` ← incorrect full SHA  
**Actual snapshot commit:**    `891f85dd655854515eefb665ec65c8c8ce05cc08` (prefix match only)  
**Validated at:** 2026-08-05  
**Verdict:** `accept_with_qualifications`

---

## Summary

The run is admissible. All five artifact SHA256 hashes are verified, all reported statistics
recompute to full floating-point precision, scope constraints are satisfied, and the RC-3
correlation is correctly recorded. Two qualifications must reach the Coordinator before
inference is drawn.

---

## CHK-1: Hash Check

**Result: pass** (with Q-1 qualification on receipt metadata)

All 5 artifact hashes verified from disk and from within the actual snapshot commit:

| File | SHA256 | Status |
|------|--------|--------|
| `gauss_test.py` | `f693d480...` | MATCH |
| `gauss_results.json` | `9decdb90...` | MATCH |
| `receipt.json` | `5b84b09a...` | MATCH |
| `report.md` | `8ec1408c...` | MATCH |
| `rebuild_transcript.txt` | `f48a8d37...` | MATCH |

The actual snapshot commit `891f85dd655854515eefb665ec65c8c8ce05cc08` is reachable from HEAD,
staged exactly these 5 files, and their git-tree hashes match the receipt.

### Q-1: Receipt metadata SHA fabrication

The snapshot receipt records:

```json
"commit_sha": "891f85dd6060ef55e3c9b87e91c38e851c0e6c89"
"parent_sha":  "61f668c99b1d9ef35f96d3148e5abe8a023f6803"
```

Neither SHA exists in the repository:

```
$ git cat-file -t 891f85dd6060ef55e3c9b87e91c38e851c0e6c89
fatal: git cat-file: could not get object info

$ git cat-file -t 61f668c99b1d9ef35f96d3148e5abe8a023f6803
fatal: git cat-file: could not get object info
```

The actual objects with these 9-char prefixes are:

| Receipt field | Receipt value | Actual full SHA |
|--------------|--------------|----------------|
| `commit_sha` | `891f85dd6060ef55e3c9b87e91c38e851c0e6c89` | `891f85dd655854515eefb665ec65c8c8ce05cc08` |
| `parent_sha` | `61f668c99b1d9ef35f96d3148e5abe8a023f6803` | `61f668c99b73c640ff0da81302b081d39ad8f5d4` |

Additionally, the receipt's `parent_sha` prefix `61f668c99` resolves to the **GOAL-MLKEM-004
BATCH-1be68e ledger commit** — which is NOT the actual parent of the snapshot commit. The
actual parent of the snapshot commit is `7a6adc14d8c08e316e1ba26ed56e722a780131b4` (BATCH-090
Discrete Morse research commit).

This indicates that both SHA fields were likely derived from abbreviated forms padded with
incorrect digits, rather than read from git. This is a metadata fabrication under AGENTS.md
rule 9. The artifact content is intact and verified independently; the receipt cannot serve
as a standalone verifiable commit binding without manual reconciliation.

**Coordinator action required:** Supersede or annotate the snapshot receipt with the correct
full SHAs before this receipt is used in downstream binding checks.

---

## CHK-2: Variance Arithmetic

**Result: pass**

All statistics recomputed from the 50 `TN_values` in `gauss_results.json`:

| Statistic | Stated | Recomputed | Match |
|-----------|--------|-----------|-------|
| `empirical_var_TN` (ddof=1) | 17896.107291 | 17896.107291 | ✓ |
| `independence_predicted_var` (N_run0 × sv_run0) | 6474.640214 | 6474.640214 | ✓ |
| `variance_ratio` | 2.764031158244 | 2.764031158244 | ✓ |
| `chi2_stat` | 135.437527 | 135.437527 | ✓ |
| `p_value` | 4.9167e-10 | 4.9167e-10 | ✓ |
| `ci_95_ratio[0]` | 1.928694 | 1.928694 | ✓ |
| `ci_95_ratio[1]` | 4.292121 | 4.292121 | ✓ |

---

## CHK-3: N-Variability Adjustment (Critical)

**Result: pass** (computation verified; finding is a major qualification)

Unlike `bgj1_sieve` (which always produced N=17919), `gauss_sieve` produced
variable N across runs:

| N_vectors | Runs |
|-----------|------|
| 18098 | 2 (runs 16, 38) |
| 18469 | 31 |
| 18848 | 17 |
| **mean_N** | **18613.34** |
| **var_N (ddof=1)** | **45919.21** |

### Law-of-total-variance adjustment

$$\text{Var}[T_N] = \mathbb{E}[N] \cdot \text{Var}[s_i] + \text{Var}[N] \cdot (\mathbb{E}[s_i])^2$$

Using:
- E[N] = 18613.34
- Var[s_i] = 0.350568 (within-environment single-score variance from run 0)  
- E[s_i] ≈ mean_TN / mean_N = 7635.720 / 18613.34 = 0.41023
- Var[N] = 45919.21

$$\text{Var}_\text{total} = 18613.34 \times 0.350568 + 45919.21 \times (0.41023)^2$$
$$= 6525.24 + 7727.62 = 14252.86$$

N-variability contributes **54.2%** of the total expected variance.

### N-corrected ratio

| Ratio | Value | chi2(49) | p-value |
|-------|-------|----------|---------|
| Raw (N_run0-normalized) | **2.764** | 135.44 | 4.9×10⁻¹⁰ |
| N-corrected (Var_total) | **1.256** | 61.52 | 0.108 |

The N-corrected ratio is **not statistically significant** at α=0.05.

### Implications for cross-algorithm comparison

The `bgj1_sieve` batches produced constant N=17919. Their variance ratios (1.39 and 1.53)
have no N-variability component in the denominator. The apparent "larger" gauss ratio
(2.764) is substantially explained by N variability rather than score correlation.
After N-correction, gauss_sieve's ratio (1.256, p=0.108) is lower than bgj1's values
(1.39, p=0.0011; 1.53, p=0.0096) and is not statistically significant.

**This is an observation for the Coordinator.** The executor correctly flagged the
N-variability as a protocol deviation requiring Coordinator attention. This validator
confirms quantitatively that accounting for it reverses the apparent inference.

---

## CHK-4: Scope

**Result: pass**

- `states_a_finding: false` in both `gauss_results.json` and `receipt.json` ✓
- `compared_against_matzov_nf: false` in both files ✓
- `rule12_status: "UNMET and UNWAIVED"` in both files ✓
- `report.md` contains only observations with explicit "See coordinator decision for interpretation" ✓

---

## CHK-5: RC-3 Cross-Run Correlation

**Result: pass**

`rc3_cross_run` block verified in `gauss_results.json`:

| Statistic | Stated | Recomputed | Match |
|-----------|--------|-----------|-------|
| `r_even_vs_odd` | 0.302518176888 | 0.302518176888 | ✓ |
| `p` | 0.141603034358 | 0.141603034358 | ✓ |
| `n_pairs` | 25 | 25 | ✓ |

r=0.303, p=0.14 — not significant at α=0.05. Consistent with cross-run independence.

---

## Verdict

**`accept_with_qualifications`** — run is admissible as a research receipt.

### Qualifications requiring Coordinator action

1. **Q-1 (moderate):** Snapshot receipt contains fabricated full SHAs for `commit_sha`
   and `parent_sha`. The actual snapshot commit exists and is verified, but the receipt
   cannot serve as a standalone binding reference without correction. Supersede or annotate
   before downstream binding checks.

2. **Q-2 (moderate):** The headline raw ratio (2.764, p=4.9×10⁻¹⁰) is not the appropriate
   statistic for inference about algorithm-dependent score correlation because gauss_sieve's
   N variability contributes ~54% of the expected variance. The N-corrected ratio is 1.256
   (p=0.108), which is not statistically significant. Any Coordinator decision about
   whether the gauss result "confirms" or "contradicts" algorithm-independence of score
   correlation must use the N-corrected value.
