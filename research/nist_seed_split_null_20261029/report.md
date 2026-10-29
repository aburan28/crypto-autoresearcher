# Small-prime splitting of the NIST/ANSI prime-field curves: prime-order null, cutoff sweep, frozen held-out test

**Date:** 2026-10-29 UTC. **Paper:** [paper.pdf](paper.pdf) (source [paper.typ](paper.typ)).
**Question:** Do the published 1997–98 prime-field curves have fewer split small primes (`Δ = t²−4p` a nonzero square mod odd `ℓ ≤ 691`) than unpublished prime-order seed candidates, and does that survive the prime-order confound, the cutoff choice and a held-out sample?

**Result:**
- **Prime-order confound (derived, validated).** The confound exists but is small here. All 19 named curves have prime order. Conditioning the Chebotarev null on prime order moves the mean split count by 0.5–1.4, to 59.7–60.2 (s.d. 5.5). Small factors of the twist order force 0–4 splits per curve and don't separate the groups.
- **Cutoff (measured on the 19).** The 25/25 within-field score holds only for `B ∈ {691, 701, 709, 769}`. Corrected for choosing `B` over 655 prime cutoffs, `p ≈ 0.006` by random-curve Monte Carlo and by exact permutation. That correction doesn't cover the earlier choice of statistic, made after many features had been examined.
- **Frozen held-out test (confirmatory).** The protocol was committed before any data. On 42 unpublished draft-eligible curves outside the named eleven, held-out curves exceed published ones in **0.574 of 102 pairs, p = 0.29. The association does not replicate.**
- **What survives.** One low outlier, prime239v1, with 42 splits (0.06th percentile). Its null tail among the 61 eligible curves examined is about 0.05, and an unpublished 192-bit curve has 44.
- **Mechanism.** No ECDLP mechanism is known.

**Provenance:**
- Inputs `internal`: the 19-curve record SHA-256 `4a0df1de…48fe`, the 69-position acceptance classification, and 82 certified branches.
- Null model `derived` from GL₂(F_ℓ) counts. Checked against 2 × 1,500 PARI SEA counts at 48 bits (`measured`) and the 42 real-field held-out curves (KS D = 0.153, 5% critical value 0.210).
- No hypothesis status changes. The [selection-rule problem](../../problems/nist-seed-selection-rule-unexplained.md) stays open. No ECDLP frontier graph changes, because no attack, map or cost edge is involved.

| File | What |
| --- | --- |
| [PROTOCOL.md](PROTOCOL.md), [AMENDMENT.md](AMENDMENT.md) | frozen held-out test (commit `bd5d146bb`, before data); post-run count-typo note |
| [analysis_lib.py](analysis_lib.py), [analysis.py](analysis.py) | null model; percentiles and coarse sweep → `runs/results.json` |
| [lookelsewhere.py](lookelsewhere.py), [permute.py](permute.py) | fine grid, look-elsewhere MC (n=20000, seed 20261029), exact permutation (4,480) |
| [heldout.py](heldout.py) | frozen test → `runs/heldout.json` |
| [validate48.py](validate48.py) | 48-bit SEA check of the null → `runs/validation48_stdout.log` |
| [figures.py](figures.py) | `fig_null.svg`, `fig_sweep.svg`, `fig_heldout.svg` |

**Not done:** 10,000 real-field SEA counts per field. Without PARI's `seadata` package, no prime-order count over these fields finished in 10 minutes on 4 cores; the run needs `isolab-eks`. The S3 resume checkpoint was not pushed because this container has no upload token. The work is analytic, takes seconds, and is recorded in git.
