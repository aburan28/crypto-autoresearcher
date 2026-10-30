# Small-prime splitting of the NIST/ANSI prime-field curves: a prime-order null, a cutoff sweep, and a held-out test

Anonymous. Draft of 29 October 2026, revised 30 October 2026 (Markdown, not typeset).

Every number below cites a committed artefact in
`crypto-autoresearcher:research/nist_seed_split_null_20261029/` (abbreviated
`S/` here) or in one of the studies named under "Data".

## Abstract

A retrospective observation holds that the published 1997–98 NIST/ANSI
prime-field curves have fewer *split* small primes than the eleven named
prime-order seed candidates passed over in the same generator streams. A split
prime is an odd prime ℓ ≤ 691 at which Δ = t² − 4p is a nonzero square. The
most extreme case is prime239v1, with 42 splits against 61–71 for the five
omitted 239-bit curves. We test three objections.

1. **Prime-order confound.** All nineteen curves have prime order, so no
   omitted curve gains forced splits from small factors of n. Under an exact
   Chebotarev null conditioned on prime order, the mean split count is
   59.7–60.2 (s.d. 5.5), not 62. The prime-order correction is 0.5–1.4
   splits, and small factors of the twist order contribute 0–4 forced splits
   per curve. Neither explains the gap.
2. **Cutoff choice.** On the nineteen curves, a within-field pair score of
   25/25 occurs only for B ∈ {691, 701, 709, 769}; elsewhere it is 19–23. A
   look-elsewhere correction over 655 prime cutoffs still leaves p ≈ 0.006.
3. **Replication.** We fixed the statistic at B = 691 in a protocol committed
   before the data. We then applied it to the 42 unpublished draft-eligible
   curves in the same streams that were *not* among the named eleven. The
   association **does not replicate**: held-out curves exceed published ones
   in 0.574 of 102 within-field pairs (one-sided permutation p = 0.29).

What survives is a single low outlier, prime239v1, at the 0.06th percentile.
Among the 61 eligible curves examined, a minimum that extreme has null
probability about 0.05. No known mechanism links rational small isogenies to
discrete-logarithm hardness. We find no evidence of a split-count selection
rule.

## 1. The claim under test

The recovered `lrand48`/SHA-1 seed streams behind the X9.62/NIST prime-field
curves contain prime-order candidates that were never published. Eleven of
them have been named as *omitted*: five 239-bit, three P-224, two 192-bit and
one P-256. They have been compared with the eight published curves of the
same fields (prime192v1–v3, secp224r1, prime239v1–v3, prime256v1).
`crypto-autoresearcher:problems/nist-seed-selection-rule-unexplained.md` lists
the many features already tested on these nineteen curves.

For a curve with trace t = p + 1 − n, the observation counts

  S(E) = #{ odd prime ℓ, 3 ≤ ℓ ≤ 691 : (Δ/ℓ) = +1 },  Δ = t² − 4p.

A split prime is an Elkies prime: Frobenius has eigenvalues in F_ℓ, and E has
two rational ℓ-isogenies. The reported pattern is that published curves have
smaller S in every same-field comparison. A critique raised three problems:
a prime-order confound, forking paths (the cutoff 691, the ramified
convention, a sign test over four fields), and the lack of a mechanism.

## 2. Data

- **Nineteen named curves.** Exact p, n and EC1 curve UIDs come from
  `crypto-autoresearcher:research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json`
  (SHA-256 `4a0df1de…48fe`). That study independently verified the Legendre
  symbols in Sage. Every n is prime.
- **Held-out cohort.**
  `crypto-autoresearcher:research/nist_seed_1997_acceptance_20261024/analysis.json`
  classifies 69 seed positions whose curves pass the November 1997 X9.62
  draft's numerical checks with certified prime order. Of these, 10 are
  published and 59 unpublished; the named eleven are a retrospective subset of
  the 59. The other 48 unpublished positions (`order_too_wide_only`,
  `opposite_root_only`) never entered the 691 observation. Of those, 42 lie in
  the four comparison fields and 6 in P-384.
- **Held-out p and n** come from the certified branches in
  `crypto-autoresearcher:research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`.
  The two square-root branches at one seed are isomorphic or quadratic twists
  (t → ±t), so they share Δ (asserted in `S/heldout.py`).

## 3. A prime-order null

**Lemma.** Let ℓ be an odd prime with ℓ | n = p + 1 − t. Then t ≡ p + 1 and
Δ ≡ (p − 1)² (mod ℓ), so ℓ splits unless p ≡ 1 (mod ℓ), in which case it
ramifies. The same holds when ℓ divides the twist order p + 1 + t.

Both groups have prime n, so the lemma cannot separate them through n. The
twist orders do have small odd factors ≤ 691 on 18 of 19 curves (0–4 per
curve). The published curves have no fewer of these, averaging 2.0 against
1.7. Excluding those primes leaves the results unchanged (`S/runs/results.json`,
variant `split-twist`).

**Null.** For a random curve over F_p and a small ℓ ≠ p, Frobenius mod ℓ is
asymptotically distributed like a uniform matrix in GL₂(F_ℓ) with determinant
p (Castryck–Hubrechts). The number of 2×2 matrices over F_ℓ with trace u and
determinant d is ℓ² + ℓ·χ(u² − 4d). Prime order excludes the eigenvalue 1,
that is u ≡ 1 + d. Hence

  P_ℓ(split) = Σ_{u ≢ 1+d, χ(u²−4d)=1} (ℓ² + ℓ) / Σ_{u ≢ 1+d} (ℓ² + ℓ·χ(u² − 4d)).

Assuming independence across ℓ gives an exact Poisson-binomial law for S in
each field. A curve's position is its mid-percentile, 100·(P(X < S) + P(X = S)/2).

| Field | Mean, all curves | Mean, prime order | Shift | s.d., prime order |
|---|---:|---:|---:|---:|
| 192-bit | 61.08 | 59.70 | −1.38 | 5.51 |
| 224-bit | 60.62 | 60.08 | −0.53 | 5.53 |
| 239-bit | 61.12 | 59.72 | −1.40 | 5.51 |
| 256-bit | 60.69 | 60.18 | −0.51 | 5.54 |

Source: `S/runs/results.json`.

**Validation.**

- *48-bit sample.* PARI SEA counts of 1,500 prime-order curves
  y² = x³ − 3x + b over each of two random 48-bit primes matched the model:
  means 60.11 and 60.08 against 60.20 and 60.30, KS distances 0.023 against a
  5% critical value of 0.035 (`S/runs/validation48_stdout.log`). The
  first run kept only aggregates (deviation D2 in `S/DEVIATIONS.md`). A
  rerun with the same seed reproduced both output lines exactly and saved all
  3,000 rows (`S/runs/validation48_rows.jsonl.gz`). An independent audit
  recomputed every statistic from the rows and re-counted 100 curves with
  PARI, with 0 mismatches (`S/runs/validation48_audit.json`).
- *Real fields.* The 42 held-out curves give a second check, over the real
  fields (§5).
- *Not done.* A 10,000-curve SEA sample per real field remains open.

## 4. Exploratory analysis of the nineteen curves

Figure: `S/fig_null.svg`.

| Field | Omitted: S (percentile) | Published: S (percentile) |
|---|---|---|
| 192-bit | 61 (59.3), 62 (66.1) | v1 60 (52.2), v2 58 (38.0), v3 57 (31.3) |
| 224-bit | 53 (10.1), 56 (23.1), 59 (42.3) | secp224r1 50 (3.4) |
| 239-bit | 71 (97.9), 67 (90.6), 66 (87.2), 63 (72.3), 61 (59.2) | v1 **42 (0.06)**, v2 57 (31.2), v3 57 (31.2) |
| 256-bit | 58 (34.8) | prime256v1 57 (28.4) |

**Cutoff sweep.** Figure: `S/fig_sweep.svg`; data in
`S/runs/lookelsewhere.json` and `S/runs/permute.json`.

- The score reaches 25/25 only for B ∈ {691, 701, 709, 769}. At the other
  tabulated cutoffs (101, 251, 397, 997, 2003, 5003) it is 19–23, whether or
  not ramified primes or twist-forced splits are counted.
- prime239v1 is most extreme near B = 571, at the 0.009th percentile. It stays
  below 1% for 359 ≤ B ≤ 1367 and reaches 11% by B = 5003.

**Correcting for the choice of B** (over 655 prime cutoffs):

- *Random-curve null.* We drew 20,000 synthetic sets of nineteen prime-order
  curves (seed 20261029). The grid maximum of the pair score has null
  0.50, 0.90 and 0.99 quantiles of 18, 22 and 24, and P(max ≥ 25) = 0.0055.
- *Exact label permutation* (4,480 allocations). p = 0.0065 for the grid
  maximum, and 1/4480 at B = 691.
- *Without prime239v1.* The remaining 20 pairs score 20/20 on the same
  plateau, with a median of 15/20 over the grid.

These corrections do not cover the choice of statistic, which was formed after
many features had been examined on the same nineteen curves. They are
exploratory and had no protocol.

## 5. Held-out test

**Protocol.** `S/PROTOCOL.md` was committed and pushed (`bd5d146b`) before any
held-out curve was computed. It fixes:

- the statistic: S at B = 691 under the prime-order null;
- the population;
- one confirmatory test: within-field (held-out, published) pairs, the
  fraction with the held-out curve higher (ties count ½), and a one-sided
  within-field label-permutation p from 200,000 draws;
- the decision rule: the association replicates if p ≤ 0.05.

`S/AMENDMENT.md` corrects a count typo (48 for 42). `S/protocol.json`
transcribes the protocol into `experiment.protocol/v1`. It validates but could
not be frozen, because the script was not hash-frozen before the data
(deviation D3). The run also launched without the required resume checkpoint
(D1).

**Primary result.** Held-out curves exceed published ones in **0.574 of 102**
pairs, with permutation p = 0.29. **The association does not replicate.**
Figure: `S/fig_heldout.svg`; rows in `S/runs/rows.jsonl`.

**Secondary results (descriptive).**

- The 42 held-out percentiles are consistent with uniform: KS D = 0.153
  against a 5% critical value of 0.210.
- The named eleven exceed the held-out curves in 0.630 of 115 pairs
  (p = 0.13).
- Published P-384 (54 splits, 14.5th percentile) ranks lowest of the 7
  eligible curves in its field.
- At the other six cutoffs the held-out-over-published fraction is 0.66–0.71.
  This is reported, not tested.

## 6. Discussion

**What the objections change.**

- *Prime order.* The objection is right in principle but negligible here.
- *Forking paths.* This objection is borne out. Once the statistic is frozen
  and applied to curves it was not tuned on, the published-versus-unpublished
  difference is indistinguishable from chance.

**What survives.** prime239v1 alone, with P(X ≤ 42) = 8.3 × 10⁻⁴. The minimum
over the 8 published curves has null probability about 0.0066. Over all 61
eligible curves examined in the four fields it is about 0.049, before any
correction for B. An unpublished 192-bit curve reaches 44.

**Mechanism.** None is known.

- No attack on prime-order curves, whether generic or rho, MOV/Frey–Rück,
  anomalous, Weil descent or index calculus, depends on how many rational
  small isogenies a curve has.
- Within an isogeny class, ECDLP difficulty is uniform up to polynomial-time
  isogeny walks (Jao–Miller–Venkatesan).
- Elkies primes make SEA point counting *faster* (Shparlinski–Sutherland). A
  designer avoiding slow counts would therefore favour *more* splits, the
  opposite of the observed direction.

**The CM field.** The only process story with any traction goes through the
CM field K. Write Δ = f_π² D_K with D_K fundamental. For ℓ ∤ f_π,
(Δ/ℓ) = χ_{D_K}(ℓ), so S counts the primes ℓ ≤ 691 that split in K. One might
read a low S as a small L(1, χ_{D_K}), and so a small class number, of the
kind a CM-method generator would produce. The L-value is in fact low, but
not in a way that supports the generator story.

- *The direct test is |D_K|, and it fails.* A CM-method generator yields
  |D_K| of a few million at most. The exact conductor census
  (`crypto-autoresearcher:research/nist_seed_exact_conductor_census_20261023/`)
  factors Δ for all nineteen curves. It finds f_π ∈ {1, 3, 5} and a smallest
  |D_K| of about 2^192.4 (an omitted 192-bit curve). prime239v1 has f_π = 1,
  so D_K = Δ and |D_K| ≈ 4p ≈ 2^241. An L-value cannot close this gap. Under
  GRH, L(1, χ) lies within a factor of about (log log|D_K|)^{±1} of 1
  (Littlewood). That is roughly 0.1 to 18 here, so
  h = √|D_K|·L(1, χ)/π stays within about 2^5 of √|D_K|/π. A gap of about
  2^200 is out of reach. The class-group 2-ranks of the same nineteen fields
  overlap between published and omitted curves
  (`crypto-autoresearcher:research/nist_seed_genus_rank_20261023/`).
- *S is not an Euler product.* log L(1, χ) ≈ Σ_ℓ χ(ℓ)/ℓ is weighted by 1/ℓ,
  so the smallest primes dominate it. S is an unweighted count, so the primes
  near the cutoff dominate it. Across the 61 eligible curves,
  corr(S(691), log L̂) = 0.46, while the weighted partial log-Euler product
  E(691) = −Σ_{3≤ℓ≤691} log(1 − χ(ℓ)/ℓ) has corr(E(691), log L̂) = 0.95.
- *prime239v1's L-value is low (measured).* A follow-up study
  (`crypto-autoresearcher:research/nist_seed_lvalue_20261030/`, protocol
  frozen before data) estimates L(1, χ_{D_K}) by the Euler product to
  x = 10⁸. Against exact class numbers of 20 random fundamental
  discriminants of 80–110 bits, this estimator is within 4 × 10⁻⁵ in log L.
  Under GRH the truncation error at |D_K| ≈ 2^241 is expected to be about
  10⁻³; this is not a proved bound. For prime239v1, L̂ = 0.246, at the
  0.25th percentile of the prime-order null and the lowest of the 61 curves.
  Its partial log-Euler product is −0.998 over 3 ≤ ℓ ≤ 691 and only +0.002
  over ℓ > 691, so the first 124 odd primes carry essentially all of it.
  E(B) stays between the 0.22nd and 0.25th percentile for 691 ≤ B ≤ 5003.
  An independent study with separate code and a frozen protocol record
  (`crypto-autoresearcher:research/nist_seed_l1chi_20261030/`) reproduces
  it: on the 61 shared curves log L̂ at x = 10⁶ agrees to 3 × 10⁻¹⁴, and
  prime239v1 is again at the 0.25th percentile and the lowest
  (`CROSSCHECK.md` there).
  Over the same range, the split-count percentile rises from 0.06 to 11
  (§4). That rise is an artefact of the unweighted count, not a sign of an
  ordinary L-value.
- *It is the same anomaly, not new evidence.* prime239v1 was singled out
  because its S was extreme, and E(691) tracks log L̂ closely. If nothing had
  been selected, some curve among 61 would reach the 0.25th percentile with
  probability 1 − (1 − 0.0025)^61 ≈ 0.14 (about 0.02 among the 8 published
  curves). The median log-L percentiles are 39 for the 8 published curves,
  49 for the 11 omitted and 52 for the 42 held-out curves. The 42 held-out
  percentiles fit the null (KS D = 0.066). The implied class number,
  h ≈ 2^116.8, is within a factor of 2 of the null median. No known ECDLP
  method depends on L(1, χ) or on h.

**Limitations.**

- The null assumes independence across ℓ and exact equidistribution.
- The eight published curves are shared between the exploration and the test.
- Monte Carlo p-values carry binomial error.
- L̂ is a truncated Euler product, conditional on GRH for its expected accuracy; exact class numbers at 2^241 were infeasible (§6).

## References

- W. Castryck, H. Hubrechts. The distribution of the number of points modulo an integer on elliptic curves over finite fields. *Ramanujan J.* 30 (2013).
- R. Schoof. Counting points on elliptic curves over finite fields. *J. Théor. Nombres Bordeaux* 7 (1995) 219–254.
- I. E. Shparlinski, A. V. Sutherland. On the distribution of Atkin and Elkies primes. *Found. Comput. Math.* (2014).
- D. Jao, S. D. Miller, R. Venkatesan. Expander graphs based on GRH with an application to elliptic curve cryptography. *J. Number Theory* 129 (2009) 1491–1504.
- J. E. Littlewood. On the class-number of the corpus P(√−k). *Proc. London Math. Soc.* (2) 27 (1928) 358–372.
- ANSI X9.62 working draft, 17 November 1997, §F.3.2.
