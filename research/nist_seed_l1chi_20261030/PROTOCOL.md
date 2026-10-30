# Frozen protocol: is prime239v1's L(1, χ) proxy extreme?

Written 2026-10-30 UTC. It was written **before** any target curve was
evaluated with these scripts. `protocol.json` holds the same design as an
`experiment.protocol/v1` record, with `analyze.py` and `calibrate.py` frozen
by SHA-256. Nothing runs until `scripts/checkpoint.sh gate` passes. This
corrects deviation D1 of `research/nist_seed_split_null_20261029`.

## Why

In `research/nist_seed_split_null_20261029`, prime239v1 had only 42 split
primes up to ℓ ≤ 691, at the 0.06th percentile under the prime-order null.
How extreme it looks depends on the cutoff B: it is lowest near B = 571
(0.009th percentile) and back at the 11th percentile by B = 5003. A count of
split primes is a crude version of the Euler product for L(1, χ_Δ). For ℓ
not dividing the conductor f, χ_Δ(ℓ) = χ_{D_K}(ℓ), so a persistently small
product means a CM field whose class number is small relative to √|D_K|.
That is the only reading of "few split primes" with a plausible generation
story, namely a CM-method generator. This test asks whether the low value
survives once the product is taken to ℓ ≤ 10⁶.

**Prediction, recorded before the run:** it will not. prime239v1's
percentile will be **at least 1%**. This prediction is only partly out of
sample. χ(ℓ) for ℓ ≤ 5003 has already been seen for this curve. Its
decisive scope is the terms for 5003 < ℓ ≤ 10⁶, which have never been
computed for it. The test is whether those terms restore an ordinary value.

## Population

There are 69 seed positions in
`research/nist_seed_1997_acceptance_20261024/analysis.json`: 10 published and
59 unpublished, all draft-eligible with certified prime order. Their p and n
come from `research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`.
Each position contributes one Δ = t² − 4p, and the script asserts that both
root branches agree. The target is prime239v1: stream `prime239v3`, index
2185, confirmed by matching n against the 19-curve record. The script fails
closed on a missing or uncertified row.

## Statistics

The cutoff is fixed at X = 10⁶, and the product runs over every prime
ℓ ≤ 10⁶, including ℓ = 2. For prime n over odd p, t is odd, so Δ ≡ 5
(mod 8) and χ(2) = −1 is the same for every curve.

- **Decisive statistic:**
  log P_Δ = Σ_{ℓ ≤ X} −log(1 − χ_Δ(ℓ)/ℓ),
  where χ_Δ is the Kronecker symbol of Δ, which is 0 at ℓ | Δ.
- **Descriptive statistic:** log P_DK is the same sum with χ_{D_K}. For each
  ℓ, the ℓ-part of the conductor is stripped first, by removing the largest
  ℓ^{2e} that leaves a discriminant. Doing this prime by prime gives the
  exact character without factoring Δ. log P_DK approximates
  log L(1, χ_{D_K}) to within the calibrated truncation error.

**Null for log P_Δ.** For each field p:

- Frobenius mod ℓ is uniform on GL₂(F_ℓ) with determinant p and no
  eigenvalue 1 (prime order), independently over ℓ.
- The closed-form split, inert and ramified probabilities are checked
  against brute force for every odd ℓ < 200 on each run (`self_test`).
- For odd ℓ ≤ 1000, the null is simulated by Monte Carlo with 10⁶ draws per
  field (seed 20261030).
- For 1000 < ℓ ≤ 10⁶, it is a Gaussian with the exact mean and variance.
- A curve's percentile is 100 × P(null < observed), computed by convolving
  the two parts.

## Controls

- **Instrument self-test (every run).** The closed-form null matches brute
  force, and the Kronecker and conductor-stripping identities hold.
- **Truncation calibration (`calibrate.py`, independent of the targets).**
  2,000 fundamental discriminants D in [−10¹³, −10¹²] (seed 20261030), with
  h(D) from PARI `quadclassunit` (GRH-conditional) and
  L(1, χ_D) = πh/√|D|. The tolerance τ is the largest |log P_X(D) − log L|.
- **Positive control.** secp256k1 has D_K = −3 and
  L(1, χ₋₃) = π/(3√3). Its log P_DK must lie within τ of
  log(π/(3√3)). If it doesn't, the verdict is `invalid_measurement`.
- **Negative control (descriptive).** The percentiles of the 59 unpublished
  curves are compared with a uniform distribution (KS).
- **A/A control: not applicable.** The arithmetic is exact and deterministic.

## Decision rule (one decisive test)

| prime239v1 percentile of log P_Δ | Verdict |
|---|---|
| below 1.0% | `extreme_persists` |
| 1.0% or above | `not_extreme` |
| positive control fails | `invalid_measurement` |

There is no multiplicity correction: this is one curve, chosen in advance.

**What each verdict means:**

- `extreme_persists` reopens the CM-field question only. A next protocol
  would then estimate h(D_K) and compare it with CM-method generation. It
  establishes no weakness.
- `not_extreme` closes the split-prime line: no small-L(1, χ) reading
  survives.

## Descriptive only

These outputs decide nothing:

- all 69 percentiles;
- log P_DK and the implied h ≈ √|D_K|·P_DK/π, wherever |D_K| is known;
- the within-field unpublished-over-published pair fraction, with a
  one-sided permutation p from 200,000 draws (seed 20261031).

The descriptive comparison is in-sample: 61 of the 69 curves were seen in
earlier studies.

## Inadmissible

- Changing X, the threshold, the target, the population or the null after
  any target value is computed.
- Reading the descriptive comparison as a test.
- Reading any verdict as an ECDLP weakness. No known attack uses L(1, χ) or
  the class number of a prime-order curve's CM field.

## Run (only after `scripts/checkpoint.sh gate` passes)

```
python3 calibrate.py runs/calibration.json
python3 analyze.py ../nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json \
  ../nist_seed_1997_acceptance_20261024/analysis.json \
  ../nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl \
  runs/calibration.json runs/results.json
```

Keep stdout, stderr, exit codes, wall times and `pip freeze` in `runs/`. The
estimated runtime is a few minutes for calibration and a few minutes for the
analysis, on one core.
