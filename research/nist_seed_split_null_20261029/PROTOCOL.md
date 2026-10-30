# Frozen held-out test: small-prime split counts on unpublished draft-eligible curves

Written 2026-10-29 UTC, **before** any split count was computed on the
held-out curves below. Committed separately from its results so the git
history orders protocol before data. The exploratory analysis of the nineteen
named curves (`analysis.py`, `lookelsewhere.py`, `permute.py`) was done first
and motivates this test; it is not part of the test.

## Frozen statistic (no alternatives)

For a curve over F_p with trace t, let Delta = t^2 - 4p. The **split count**
S is the number of odd primes 3 <= l <= **691** with Delta a nonzero square
mod l (124 primes). Ramified primes count as not split. The cutoff 691 is the
one used in the critiqued claim and is not re-chosen; no other cutoff,
ramified convention, or twist exclusion enters the confirmatory test.

The **null** is the prime-order Chebotarev model in `analysis_lib.py`:
Frobenius mod l is uniform on GL2(F_l) matrices with det p and no eigenvalue
1, independent across l. A curve's **percentile** is its mid-percentile
P(X < S) + P(X = S)/2 under that field's exact Poisson-binomial law.

## Held-out population

From `research/nist_seed_1997_acceptance_20261024/analysis.json` (69 draft-
eligible seed positions), take every position labelled `order_too_wide_only`
or `opposite_root_only` (48 in the 192/224/239/256-bit fields; 6 in P-384).
Read p and n for each from
`research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`
by (target, index), requiring `order_certified` and `n_prime_pari` true. Both
root branches at one position have the same Delta (isomorphic or quadratic
twists), so use one value per position and assert the branches agree. The
eight published same-field controls and the eleven named omissions are the
rows of the nineteen-curve record; P-384 published (index 2688) is read from
the certificate file. Fail closed on any missing or uncertified row.

## Confirmatory test (one)

H_sel: published curves have lower split counts than unpublished eligible
curves of the same field.

Primary statistic: over all within-field (held-out, published) pairs in the
192/224/239/256-bit fields (21x3 + 8x1 + 9x3 + 4x1 = 102 pairs), the fraction
with S(held-out) > S(published); ties count one half. P-value: exact or
Monte Carlo (200,000 draws, seed 20261029) within-field label permutation
among published + held-out, holding the published count per field fixed;
one-sided, larger fraction is more extreme. **Replicates if p <= 0.05.**

## Secondary, descriptive (no decision)

1. Held-out percentiles against uniform (KS distance, n=48): a check that
   unpublished eligible curves look like random prime-order curves.
2. Named eleven vs held-out unpublished: within-field pair fraction with the
   named curve higher, and the permutation p-value computed the same way.
3. P-384: rank of the published curve among itself and its 6 held-out curves.
4. The same primary statistic at the exploratory cutoffs 101, 251, 397, 997,
   2003, 5003, reported as a sensitivity table only.

## Limits

The eight published curves are the same in exploration and test; the test
replicates only the *unpublished* side. A replication is a label association,
not an ECDLP weakness, and says nothing about mechanism or intent.
