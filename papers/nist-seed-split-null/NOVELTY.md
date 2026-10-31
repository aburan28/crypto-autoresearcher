# Novelty audit (2026-10-31)

The paper README's checklist owed this audit. Its question: has anyone tested
small-prime split counts, Elkies or Atkin primes, the CM discriminant or class
number, or L(1, χ) on the published NIST/ANSI seed curves against the omitted
candidates?

## Sources checked

| Source | Provenance | What it covers | Tests these properties? |
|---|---|---|---|
| Anthropic Frontier Red Team, <https://www.anthropic.com/research/ecdsa-curve-origins> (16 Oct 2026) | retrieved 2026-10-31 | `lrand48` seeds from 1997–98 timestamps; FreeLIP base points; omitted candidates (P-256 #876; 3 at P-224; 7 in the two ANSI runs); no break | **No.** Covers seed generation and the skipped candidates only |
| F. Valsorda, <https://words.filippo.io/seeds-solved/> | retrieved 2026-10-31 | about twice as many valid seeds as published; one undocumented rule (order bit length > field bit length → reject), the rest unexplained; "barely 30 bits of freedom" | **No.** The bit-length rule is the only property discussed |
| Bernstein et al., "How to manipulate curve standards" (SSR 2015, BADA55) | recalled; DOI from search | seed search lets a standard select rare properties | Generic threat model; no test on these curves |
| SafeCurves, <https://safecurves.cr.yp.to> | retrieved via search | requires CM discriminant \|D\| > 2¹⁰⁰; P-224 and P-256 pass | A threshold check, not a published-vs-omitted comparison |
| Shparlinski–Sutherland, FoCM 2014 (arXiv:1112.3390); LMS JCM 2015 (arXiv:1404.0399) | retrieved via search | Elkies and Atkin primes in equal proportion on average; enough small Elkies primes for SEA | Theory only; no NIST curves |
| Benoist–Kieffer, "Distribution of Elkies primes" (orbilu preprint) | listing seen; PDF returned HTTP 503 | Gaussian limit for the Elkies-prime count | Theory; not cited until verified |

Searches covered: the seed recovery and the omitted candidates; Elkies and
Atkin prime distribution together with NIST and statistical tests;
prime239v1 together with Elkies, split primes and small isogenies; and class
numbers and CM discriminants of the NIST curves. None found an earlier test of
split counts or L(1, χ) on these curves.

## Conclusion

- **New, as far as these searches reach:** the split-count statistic under
  a prime-order Chebotarev null, the cutoff sweep with its look-elsewhere
  correction, the held-out test, and the L(1, χ) follow-up.
- **The result is negative,** so the contribution is methodological: a
  frozen held-out test of a retrospective pattern.
- **Interaction with Valsorda:** 15 of the 42 held-out curves are
  `order_too_wide_only`, so his bit-length rule explains why they were
  passed over. That doesn't change the test, which compares published
  against unpublished draft-eligible curves. `paper.tex` §2 now says so.
- **Added to the paper:** a related-work paragraph in §1 citing the
  Anthropic post, Valsorda, BADA55, SafeCurves and Shparlinski–Sutherland.

## Limits

- Web search only. No database search (MathSciNet, ePrint full text) was run.
- The Benoist–Kieffer PDF could not be retrieved.
- Secondary news coverage of the Anthropic post was ignored in favour of the
  primary post.
