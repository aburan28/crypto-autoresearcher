---
id: KN-LIT-083
type: literature
title: Class number, a theory of factorization, and genera
authors: [Shanks Daniel]
year: 1971
venue: Proceedings of Symposia in Pure Mathematics, vol. 20, American Mathematical Society, pp. 415-440
identifiers:
  eprint: null
  doi: 10.1090/pspum/020/0316385
  url: https://doi.org/10.1090/pspum/020/0316385
tags: [baby-step-giant-step, bsgs, shanks, meet-in-the-middle, deterministic, generic, discrete-logarithm, baseline, memory, ecdlp]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The origin of the baby-step giant-step (BSGS) method. Shanks introduced the
meet-in-the-middle technique for computing class numbers and discrete
logarithms in finite abelian groups: build a sorted table of the m = ceil(sqrt(n))
"baby steps" i*P, then take "giant steps" Q - j*m*P until one lands in the
table. A match gives k = i + j*m.

## Key claims (as reported)
- Deterministic O(sqrt(n)) group operations and O(sqrt(n)) storage, with no
  heuristic assumption about walk randomness (proven).
- Works in any finite abelian group given only the group law and an equality
  test, and additionally computes group order / class number.
- The method is the deterministic counterpart to Pollard rho: same exponent,
  worse memory, no probabilistic failure mode.

## Relevance to this program
BSGS is the deterministic member of the generic-algorithm family and matters
here for two reasons. First, it fixes the *time-memory* corner of the baseline:
any claimed advantage that quietly assumes sqrt(n) storage is competing with
BSGS, not with rho, and BSGS is the reason unlimited-memory assumptions are
not free (see KN-LIT-094, where the full cost of BSGS is n^{2/3+o(1)} rather
than n^{1/2}). Second, BSGS is the standard finishing step for any mechanism
that localizes k to a short interval; several of this program's proposals
(e.g. the transfer-operator route, KN-OPEN-010) reduce to "shrink the interval,
then BSGS," so the residual interval length must be charged at its BSGS cost.
See KN-TECH-031.

## Not verified here
The 1971 volume was not fetched; author, title, venue, volume, and pages
1971/vol.20/415-440 were confirmed against the AMS DOI record and the MathSciNet
citation reproduced in the Shanks obituary (Math. Comp. 1997). The algorithm
statement above is textbook standard (hence confidence: established) and was
taken from secondary presentations, not from Shanks's original text.
