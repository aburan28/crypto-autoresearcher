---
id: KN-LIT-7568
type: literature
title: "A New Algorithm for Finding Minimum-Weight Words in a Linear Code: Application to McEliece's Cryptosystem and to Narrow-Sense BCH Codes of Length 511"
authors: [Canteaut Anne, Chabaud Florent]
year: 1998
venue: IEEE Transactions on Information Theory, 44(1):367-378
identifiers:
  eprint: null
  doi: null
  url: https://www.rocq.inria.fr/secret/Anne.Canteaut/Publications/Canteaut_Chabaud98.pdf
tags: [code-based, information-set-decoding, isd, mceliece, cryptanalysis, parameter-selection]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Refines Stern-style information set decoding with an iterative update that
reuses the previous iteration's Gaussian elimination instead of recomputing it,
substantially lowering the per-iteration cost. Applies the result to McEliece's
original parameters and to minimum-weight-word search in BCH codes of length
511.

## Key claims (as reported)
- Improves on all previous attacks against code-based public-key cryptosystems
  known at the time.
- Points out concrete weaknesses in McEliece's original (1978) parameter choice
  -- the historical reason modern parameter sets are much larger than the
  original proposal.

## Relevance to this program
This is the paper that made "the original McEliece parameters are too small" a
quantitative statement rather than a suspicion, and it is a clean instance of a
pattern the program cares about: an attack that moves no asymptotic exponent at
all, yet changes deployed parameters, because it removes a large polynomial
factor. Recorded in KN-TECH-057 and KN-TECH-061 as the reason concrete
estimators -- not asymptotics -- govern parameter selection.

## Not verified here
Primary PDF not fetched. Authors, title, venue, volume/issue/pages, and year
confirmed via search against DBLP and Semantic Scholar records; DOI not
confirmed and left null. The URL is an author-hosted copy located via search and
not retrieved.
