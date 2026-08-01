# Analysis: EXP-ECDLP-ENERGY-001

> **Interpretation amended 2026-07-17.** See `interpretation-amendment-v2.md`. Exact fivefold support supersedes sampled target ratios and the finite `binomial(B+4,5)` explanation below. The frozen no-promotion outcome remains valid; family-level persistence remains open.

## Status

`NEGATIVE RESULT`, `OBSERVATION`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

Both preregistered runs completed valid. `RUN-ECDLP-ENERGY-002` independently recomputed all three curve orders, seeded factor-base constructions, pair and triple counters, five-term witnesses, and 24 Pollard-rho walks from `RUN-ECDLP-ENERGY-001`.

No tested coordinate family met the joint promotion gate at any size. This rejects only `H-ECDLP-ENERGY-001` under the frozen one-seed, 15/17/19-field-bit protocol.

## Primary Results

| Field bits | `q` | `B` | Family | `E2/random` | Successful targets | Success/random | Offline ops/random |
|---:|---:|---:|---|---:|---:|---:|---:|
| 15 | 10,799 | 8 | random | 1.000 | 9/128 | 1.000 | 1.000 |
| 15 | 10,799 | 8 | x interval | 1.000 | 4/128 | 0.444 | 1.708 |
| 15 | 10,799 | 8 | square map | 1.000 | 9/128 | 1.000 | 1.342 |
| 15 | 10,799 | 8 | rational union | 1.000 | 7/128 | 0.778 | 1.237 |
| 17 | 9,851 | 8 | random | 1.000 | 9/128 | 1.000 | 1.000 |
| 17 | 9,851 | 8 | x interval | 1.000 | 7/128 | 0.778 | 3.652 |
| 17 | 9,851 | 8 | square map | 1.000 | 4/128 | 0.444 | 3.765 |
| 17 | 9,851 | 8 | rational union | 1.000 | 6/128 | 0.667 | 5.903 |
| 19 | 129,737 | 12 | random | 1.000 | 4/128 | 1.000 | 1.000 |
| 19 | 129,737 | 12 | x interval | 1.000 | 2/128 | 0.500 | 1.372 |
| 19 | 129,737 | 12 | square map | 1.000 | 2/128 | 0.500 | 1.325 |
| 19 | 129,737 | 12 | rational union | 1.000 | 5/128 | 1.250 | 1.512 |

The scalar-progression positive control behaved differently: pair energy rose to `1.762x`, `1.762x`, and `2.616x` random while the pair sumset compressed from `33/33/73` entries to `17/17/25`. It nevertheless covered only `0/128`, `1/128`, and `0/128` targets. Pair concentration is therefore not a sufficient objective for relation generation; it can reduce storage while collapsing the fivefold support needed for arbitrary targets.

## Model Correction

The preregistered ordered-tuple heuristic used

```text
lambda_ordered = B^5 / q
Pr[target covered] = 1 - exp(-lambda_ordered).
```

It predicted random-control target coverage of `95.19%`, `96.41%`, and `85.31%`, but the observed values were `7.03%`, `7.03%`, and `3.13%`. Ordered representations are not independent events: a single five-element multiset creates many permutations of the same relation.

The original post-run diagnostic

```text
lambda_unordered = binomial(B + 4, 5) / q
Pr[target covered] = 1 - exp(-lambda_unordered)
```

predicts `7.07%`, `7.73%`, and `3.31%`, which happened to be close to the 128-target samples. The red-team exact-support census showed that this finite explanation is incomplete for sign-complete sets because inverse-pair cancellations identify additional multisets. Retain `binomial(B+4,5)/q` only as a leading-order sizing heuristic pending a signed-coefficient occupancy model; do not use it as the explanation of these three samples.

## Interpretation

All three coordinate families sat on the same sparse pair-energy floor as the random control at every size. Their two-sum and three-sum advice sizes were also nearly identical. The tested predicates therefore exposed no coordinate-specific pair concentration under this schedule.

The rational union produced `5/128` successful targets versus `4/128` for random at the largest size, but it missed the `1.5x` threshold, did not repeat at smaller sizes, and cost `1.512x` as many offline group operations. This is not a positive signal under the frozen gate.

The fitted exponents in the raw result are not interpretable as scaling evidence. The accepted subgroup orders were `10,799`, `9,851`, and `129,737`; the first two are non-monotone and both use `B=8`. Every fitted value is retained as raw output but excluded from promotion and breakthrough reasoning.

`RUN-ECDLP-ENERGY-001` also captured six ExFAT AppleDouble metadata files as extra artifacts. Their bytes and hashes are preserved in Git. The wrapper was repaired after that run to remove only AppleDouble files before atomic publication; the independent verifier run contains only the five intended artifacts. This infrastructure observation did not change raw arithmetic data or verifier agreement.

## Scoped Conclusion

No improvement meeting the predefined threshold was observed for x intervals, square-map images, or the tested rational-map union over these three toy instances and this compute budget. This is a negative result for those exact representations and parameters, not for coordinate factor bases, compiled decomposition, fixed-curve preprocessing, or prime-field index calculus generally.

The next positive question is stricter and more useful:

> Can a coordinate family keep large fivefold expansion and near-random target support while allowing its intermediate two-/three-sum joins to be represented or queried below their explicit-table cost?

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m crypto_autoresearcher validate experiments
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

Canonical commands and environments are retained under `runs/RUN-ECDLP-ENERGY-001` and `runs/RUN-ECDLP-ENERGY-002`.
