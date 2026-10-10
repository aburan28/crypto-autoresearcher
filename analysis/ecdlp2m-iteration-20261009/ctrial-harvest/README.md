# c_trial(m, n, l): per-attempt point-decomposition cost, harvested and fitted

## Files
- `harvest.py` rebuilds `ctrial.csv` (411 rows) and `ctrial_targets.csv` (1554 per-target values) from the repository.
- `fit.py` produces `fit_results.json` and `fit_tables.md`. It uses the standard library only, with seed 20261009, and two runs give byte-identical output.
- `external/` holds the external solver summaries. Their sha256 values match those recorded in EV-ICPERF-10c5fc.
- `stranded_refs.txt` and `stranded_runs.txt` list the unmerged branches that were searched. Those branches add no per-attempt cost data.

## Sources
- **Main:**
  - EV-ICPERF-390707 / -433fa5 / -784b25 / -10c5fc
  - EV-ICI-001
  - EV-ALBIN-001
  - EV-SEMBIN-c6e9ad / -702d1d
  - EV-CERTBIN-6c3e0a
- **Published, not reproduced here:** Trimoska et al. Tables 2–4 and the CP 2020 slide (KN-LIT-92b022, -102cdb), transcribed with line numbers from `inputs/SATIC-TRIMOSKA-2019/`.
- **Censored cells** stay marked as censored; nothing is imputed. Censoring biases every fit in favour of index calculus.

## Result: extrapolated log2 cost per attempt at n=131 (ECC2K-130), in rho steps

The rho step used here is 2^-22.42 s (KR-RHO-18cc42 rate). Using an alternative IC-generous step (the EXP-ICI-001 Sage rho step) lowers every figure by 7.85 bits and changes no verdict. The budget lines are plain (KN-FIND-aa2efc), LP (H-BINSTD-555991) and 2LP (an analogue, unverified).

| m | family | cost at budget l | budget lines (plain / LP / 2LP) | verdict |
|---|---|---|---|---|
| 3 | WDSat with symmetry breaking, UNSAT | 100.7 [100.2, 101.3] | −15.55 / 8.71 / 2.6 | outside, by ≥ 91 bits |
| 3 | Riemann–Roch L(4O) oracle, measured at n=131 | 64.7 [63.7, 65.8] | (same lines) | outside, by ≥ 55 bits |
| 4 | MITM t=4 chained S3 | 78.4 [74.4, 82.5] | 11.01 / 22.34 / 11.7 | outside, by ≥ 52 bits |
| 5, 6 | (none) | no usable cells | — | indeterminate from data; outside only through the system-size floor |

## Supporting law checks
- **UNSAT conflicts.** WDSat's UNSAT conflict count equals 2^(3l)/3! to within 0.03–1% for l = 5..11. The fitted slope is 2.9985 bits per unit l [2.9979, 2.9992].
- **The repository's container.** Its conflict counts reproduce the paper's at (17,6) and (19,6) to within 0.2%.
- **Required versus measured growth.** At m=3 the budgets need −1.7 to −3.1 bits per unit l, against a measured +3.36. At m=4 they need −0.12 to −0.61, against a measured +2.32 for MITM.

## Gaps
1. No SAT solver has ever been run at m ≥ 4; the m=4 S_5 ANF export is not implemented (b94ec8).
2. m=5 and m=6 have no usable cell.
3. The extrapolations are long: at m=3 from l = 11 to l = 29–44.
4. Most of the m=3 data are published values, not reproductions.
5. The data mix several hosts.

## Cheapest tightening measurements
1. WDSat at m=3 run directly at n=131, l in {6, 7, 8}. About 1.5 CPU-hours.
2. The first m=4 SAT cells on S_5, at n in {19, 23} and l in {3, 4, 5}. Minutes.
3. msolve on chained S3 with t = m in {5, 6}, at small n.
