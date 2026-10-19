# Pre-registration: the unexplained ~2x skip filter

Written 2026-10-16 ~19:27 UTC, **before** any curve order from the census
(`out/`) was inspected. Only the published seeds' own parameters (b, n, G)
had been looked at, and only for the b-root and Gy-sign checks.

## Population

The "accepted" candidates are the ones Filippo's `seeds.go` accepts:
X9.62 c from SHA-1, a = -3, b = the Go `ModSqrt` root ((-27/c)^((p+1)/4) when p ≡ 3 mod 4),
prime order, `bitlen(n) <= bitlen(p)` and the MOV check. Labels: the 10 published
(P) and the 11 skipped (S) candidates, at the indices in the blog post.

The census first has to reproduce that accepted list exactly. If it does not, the
analysis stops there and the mismatch is what gets reported.

## Hypotheses (deterministic features of the curve)

- H1 Elkies coverage (an Elkies-only SEA that gives up). Let E(L) = sum of log2(l) over
  odd primes l <= L with kronecker(t^2-4p, l) != -1, and need = log2(4 sqrt p).
  Feature: E(L) - need for L in {50, 100, 150, 200, 300}. Also the number of
  Elkies primes <= 100, and the smallest L at which the Elkies product exceeds 4 sqrt p.
- H2 Twist smoothness: smallest prime factor of the twist order p+1+t; twist order
  free of primes < 2^8, < 2^16 (trial division).
- H3 Structure of n-1 and n+1: 2-adic valuation of n-1; smallest odd prime factor
  of n-1 and of n+1; "safe-ish" ((n-1)/2^v free of primes < 1000).
- H4 Residues: t mod 3, t mod 4, t mod 8, n mod 3, n mod 4, n mod 8, sign(t);
  kronecker(t^2-4p, l) for l = 3, 5, 7, 11.
- H5 b and c: b < p/2, b odd, top bit of b, bitlen(b) == bitlen(p), c odd,
  kronecker(c, p), kronecker(b, n).
- H6 Seed bytes: top bit of the seed, seed parity, the first seed byte < 0x80.
  (Controls: these should not separate unless the program filtered on them.)

## Decision rule

- A binary feature explains the filter only if it separates P from S perfectly
  (all 10 P on one side and all 11 S on the other, or the reverse). By chance that
  happens with probability about 2 x 2^-21 ~ 1e-6 per balanced feature; with about 60
  features, the family-wise false positive rate stays below 1e-4.
- A continuous feature: Mann-Whitney U, reported with an exact p-value and a
  Bonferroni correction over all continuous features. A threshold that splits P and S
  perfectly is reported as a candidate, and is then tested on held-out data: the
  accepted-but-unpublished candidates past each run's last published index should,
  under the hypothesis, all fail the same threshold, unless the program had stopped
  by then.
- A pattern that is not perfect is reported as "not explained". Partial
  separations are listed, but not claimed.

## Amendment (added 19:35 UTC, after the P-192 run reproduced but before any feature was evaluated)

- POSTHOC: the normalized trace |t|/(2 sqrt p), for a too-tight Hasse-bound sanity check.
  It is marked post hoc in every output.
