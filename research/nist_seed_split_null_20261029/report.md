# Small-prime splitting of the NIST/ANSI prime-field curves: prime-order null, cutoff sweep, frozen held-out test

**Date:** 2026-10-29 UTC. **Report PDF:** [report.pdf](report.pdf) (source [report.typ](report.typ)). **Manuscript draft:** [`papers/nist-seed-split-null/`](../../papers/nist-seed-split-null/paper.tex). **Procedural deviations:** [DEVIATIONS.md](DEVIATIONS.md) (D1–D3).
**Question:** Do the published 1997–98 prime-field curves have fewer split small primes (`Δ = t²−4p` a nonzero square mod odd `ℓ ≤ 691`) than unpublished prime-order seed candidates, and does that survive the prime-order confound, the cutoff choice and a held-out sample?

**Result:**
- **Prime-order confound (derived, validated).** The confound exists but is small here. All 19 named curves have prime order. Conditioning the Chebotarev null on prime order moves the mean split count by 0.5–1.4, to 59.7–60.2 (s.d. 5.5). Small factors of the twist order force 0–4 splits per curve and don't separate the groups.
- **Cutoff (measured on the 19).** The 25/25 within-field score holds only for `B ∈ {691, 701, 709, 769}`. Corrected for choosing `B` over 655 prime cutoffs, `p ≈ 0.006` by random-curve Monte Carlo and by exact permutation. That correction doesn't cover the earlier choice of statistic, made after many features had been examined.
- **Frozen held-out test (confirmatory).** The protocol was committed before any data. On 42 unpublished draft-eligible curves outside the named eleven, held-out curves exceed published ones in **0.574 of 102 pairs, p = 0.29. The association does not replicate.**
- **What survives.** One low outlier, prime239v1, with 42 splits (0.06th percentile). Its null tail among the 61 eligible curves examined is about 0.05, and an unpublished 192-bit curve has 44.
- **Mechanism.** No ECDLP mechanism is known.

**Provenance:**
- Inputs `internal`: the 19-curve record SHA-256 `4a0df1de…48fe`, the 69-position acceptance classification, and 82 certified branches.
- Null model `derived` from GL₂(F_ℓ) counts. Checked against the 42 real-field held-out curves, with rows retained (KS D = 0.153, 5% critical value 0.210). A 2 × 1,500-curve PARI SEA check at 48 bits matches too (KS D = 0.023 against a 5% critical value of 0.035). Its rerun with rows kept reproduces the original output exactly and passes an independent audit (D2 resolved).
- No hypothesis status changes. The [selection-rule problem](../../problems/nist-seed-selection-rule-unexplained.md) stays open. No ECDLP frontier graph changes, because no attack, map or cost edge is involved.

| File | What |
| --- | --- |
| [PROTOCOL.md](PROTOCOL.md), [AMENDMENT.md](AMENDMENT.md) | held-out test as Markdown, pushed in `bd5d146bb` before data; post-run count-typo note |
| [protocol.json](protocol.json) | `experiment.protocol/v1` transcription; validates, but not frozen (D3) |
| [DEVIATIONS.md](DEVIATIONS.md) | D1 no resume checkpoint; D2 48-bit rows not kept (resolved: rows rerun and audited); D3 no frozen protocol record or conforming export; D4 the same for the 48-bit rerun |
| [analysis_lib.py](analysis_lib.py), [analysis.py](analysis.py) | null model; percentiles and coarse sweep → `runs/results.json` |
| [lookelsewhere.py](lookelsewhere.py), [permute.py](permute.py) | fine grid, look-elsewhere MC (n=20000, seed 20261029), exact permutation (4,480) |
| [heldout.py](heldout.py) | held-out test → `runs/heldout.json`; per-curve rows in `runs/rows.jsonl` |
| [validate48.py](validate48.py) | 48-bit SEA check of the null → `runs/validation48_stdout.log` (aggregates only) |
| [validate48_rows.py](validate48_rows.py), [RERUN_48BIT.md](RERUN_48BIT.md), [audit48.py](audit48.py) | rerun with rows → `runs/validation48_rows.jsonl.gz`, `runs/validation48_summary.json`; audit → `runs/validation48_audit.json` |
| [figures.py](figures.py) | `fig_null.svg`, `fig_sweep.svg`, `fig_heldout.svg` |

**Not done:**
- A real-field SEA null of at least 10,000 curves per field. Without PARI's `seadata` package, no prime-order count over these fields finished in 10 minutes on 4 cores; the run needs `isolab-eks`.
