# prime239v1's L(1, χ) proxy stays extreme, but only through primes already seen

> **Consolidated with `research/nist_seed_lvalue_20261030/`** (see [CROSSCHECK.md](CROSSCHECK.md)).
> That study is the canonical measurement (x = 10⁸, exact D_K); this one is an independent replication.
> On the 61 curves they share, log L at 10⁶ agrees to 2.9 × 10⁻¹⁴, and prime239v1 is at the 0.246th/0.247th
> percentile in both.

**Date:** 2026-10-30 UTC. **Report PDF:** [report.pdf](report.pdf) (source [report.typ](report.typ)).
**Protocol:** [PROTOCOL.md](PROTOCOL.md) and [protocol.json](protocol.json), frozen with sha256
`039665e8…` and merged in PR #2763 before any target curve was evaluated. The
checkpoint gate passed before each run.

## Result

- **Positive control (measured): passes.** secp256k1 (D_K = −3) gives
  log P_DK = −0.503074 against the exact log(π/(3√3)) = −0.503189. That is
  inside τ = 8.65 × 10⁻⁴, the maximum truncation error over 2,000 calibrated
  discriminants (`runs/calibration.json.gz`).
- **Decisive result (measured).** prime239v1 has log P_Δ = −1.4020 over all
  primes ℓ ≤ 10⁶. That is the **0.246th percentile** of the prime-order null,
  so the frozen verdict is **`extreme_persists`**.
  - The author's recorded prediction (`not_extreme`) failed.
  - prime239v1 is the lowest of the 69 eligible curves. Next come two
    unpublished curves (1.31%, 1.53%) and published P-384 (1.69%).
- **Post-hoc, descriptive and not preregistered** (`posthoc.py` →
  `runs/posthoc.json`):
  - **Decisive scope.** The never-seen terms 5003 < ℓ ≤ 10⁶ are ordinary:
    z = −0.26, about the 40th percentile. All terms above ℓ = 1000 are at the
    72nd percentile. The extreme comes entirely from the ℓ ≤ 5003 terms
    already seen in `nist_seed_split_null_20261029`. The run reproduces that
    signal but adds no new evidence for it.
  - **Why the prediction failed.** It extrapolated the unweighted split-count
    percentile; the 1/ℓ-weighted product is dominated by small ℓ.
  - **Selection effect.** prime239v1 was selected as the minimum of 61 curves.
    The null probability that the minimum of 69 is at or below 0.246% is 0.16.
  - **Class number.** D_K = Δ: the conductor is 1, the endomorphism ring is
    maximal, and |D_K| ≈ 2²⁴¹. L(1, χ) ≈ 0.246 gives h ≈ 2^116.8, against
    about 2^118.8 at L = 1. That is about 4 times below typical and nowhere
    near the tiny class numbers a CM-method generator produces.
  - **Published versus unpublished (in-sample).** 0.699 of 133 within-field
    pairs, one-sided permutation p = 0.045. The 59 unpublished percentiles fit
    uniform: KS D = 0.118 against a 5% critical value of 0.177.

**Interpretation.** The frozen rule reopens only the CM-field question, and the
class-number estimate settles it: prime239v1's CM field is not small in any
sense relevant to curve generation. No known ECDLP attack uses L(1, χ) or h
at this scale. The [selection-rule problem](../../problems/nist-seed-selection-rule-unexplained.md)
stays open, and no hypothesis status changes. This study creates no attack,
map or cost edge, so no ECDLP frontier graph changes.

| File | What |
| --- | --- |
| `analyze.py`, `calibrate.py` | frozen scripts (hashes in `protocol.json`) |
| `runs/results.json` | all 69 rows, decisive verdict, descriptive comparison |
| `runs/calibration.json.gz` (+ `.sha256` of the uncompressed file) | truncation calibration |
| `runs/environment.txt`, `runs/*_stdout.log`, `runs/*_exit.txt` | Python 3.13, numpy 2.5.3, PARI 2.17.2; commit `9339f214`; calibration 196 s, analysis 78 s |
| `posthoc.py` → `runs/posthoc.json` | the post-hoc checks above |
| `export.json`, `runs/rows.jsonl` | `experiment.export/v1` bundle (`from-rows`); remaining `check-export` findings in [EXPORT_DEVIATION.md](EXPORT_DEVIATION.md) |
| `figures.py` → `fig_null.svg` | null density per field with all 69 curves |
| [CROSSCHECK.md](CROSSCHECK.md), `crosscheck.py` → `runs/crosscheck.json` | per-curve agreement with `nist_seed_lvalue_20261030` |
