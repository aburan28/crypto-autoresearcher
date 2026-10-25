---
id: KN-LIT-2d30ef
type: literature
title: "A new index calculus algorithm for the elliptic curve discrete logarithm problem and summation polynomial evaluation (full text read): Groebner O(p^{omega-omega/m}), evaluation O(p log^2 p), sum-(m-1)-and-test O(p); all worse than rho"
authors:
  - "Gary McGuire"
  - "Daniela Mueller"
year: 2017
venue: "IACR ePrint 2017/1262 (received 2017-12-31, revised 2018-08-08)"
identifiers:
  eprint: "iacr:2017/1262"
  arxiv: null
  doi: null
  url: null
tags: [index-calculus, prime-field, groebner-free, summation-polynomial, random-factor-base, enumeration-oracle, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

Takes the random known-log factor base of Amadori–Pintore–Sala
(KN-LIT-1e6270) and compares three ways of finding the one needed relation:
Groebner bases (Algorithm 2.5 = APS), evaluating `S_m` on every multiset of
base x-coordinates (Algorithm 3.1), and summing `m − 1` base points and
testing membership of the result in the base (Algorithm 4.1). Gives a fast
resultant-recursion evaluation of `S_m` and concludes every variant is
exponential and worse than Pollard rho. Supersedes the abstract-only stub
KN-LIT-6966ea.

## Key claims (verified from the full text)

- §1, §2.3: "Our algorithms in this paper are aimed at prime order fields";
  on Semaev's small-x base: "nobody knows how to find these small points
  efficiently"; "a feature of all the algorithms under discussion in this
  paper is that the factor base is chosen randomly".
- Theorem 2.2 (restating Semaev): `S_n` is symmetric, of degree `2^{n−2}` in
  each variable, total degree `(n−1)·2^{n−2}`, absolutely irreducible.
- Lemma 5.1 (PROVEN, fixed m): `S_m` can be evaluated at a point in
  `O(log^2 p)` via the Sylvester-determinant recursion `S_m = Res_X(S_3(x_1,x_2,X),
  S_{m−1}(x_3,…,x_m,X))`; "This method even allows us to evaluate S_9 and
  S_10". The speed-up is a property of the recursion, not of the base.
- Heuristic Result 6.5/6.6: the Groebner basis of the APS system in grevlex
  is bounded by `O(p^{ω−ω/m})` (Macaulay bound `D ≤ (m−1)2^{m−2} + s − m`);
  Remark 6.4: the base must be regenerated `m^m/2^{m−1}` times on average,
  "so ... several Groebner basis computations and not only one as is claimed
  in [APS18]"; Remark 6.9: `O(p^2)` at m = 3, ω = 3, "roughly agrees with our
  experiments".
- Heuristic Result 6.10: Algorithm 3.1 costs `O(p log^2 p)`; Heuristic Result
  6.12: Algorithm 4.1 costs `O(p)` for `s ≥ (m−2) log^2 p`.
- Verdict (§1): "The algorithms have exponential complexity, which one would
  expect with a randomly chosen factor base. Our analysis shows that all these
  algorithms are worse than the well known square-root algorithms such as
  Pollard-Rho. Nevertheless, we claim that Algorithm 4.1 is the best index
  calculus algorithm for prime order fields at the present time."
- §7 (EXPERIMENTAL, Magma V2.21-6): p = 30 056 657, m = 3, s = 311: Groebner
  96 384 s / 4 555 MB versus evaluation 42.62 s versus sum-in-F 14.08 s;
  Algorithm 4.1 at p ≈ 2^35, m = 3, s = 3 595: 6 848 s.
- §3/§6 barrier remark: the Groebner approach "treats the polynomials f_i (or
  f) as input polynomials to find their common roots with S_m even though we
  already know their complete factorisation".

## Relevance to this program

Algorithm 4.1 is the enumeration oracle (`subtract` / pair-table `mitm`) of
the prime-field pipeline in aburan28/crypto (`RESEARCH_PRIME_FAST_ECDLP.md`,
`RESEARCH_SEMAEV_ROOTFIND_VS_GROEBNER.md`): that pipeline is this paper's
"best index calculus algorithm for prime order fields" with native constants
and the MITM pair table the paper did not use. See `KR-IC-dbf1b0`.

## Not verified here

No erratum was found; the only published critique (Hu, ePrint 2024/1923,
unrefereed) does not engage with the analysis. Mueller's UCD thesis could not
be located.

## Provenance

Full text read on 2026-10-24 by a delegated literature lane of the session
recorded in DEC-20261025-48232f (`docs/reports/aps-prime-field-review-20261025/lanes/prime_field_barriers.md`).
