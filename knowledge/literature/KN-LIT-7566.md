---
id: KN-LIT-7566
type: literature
title: The use of information sets in decoding cyclic codes
authors: [Prange Eugene]
year: 1962
venue: IRE Transactions on Information Theory, 8(5):5-9
identifiers:
  eprint: null
  doi: 10.1109/TIT.1962.1057777
  url: https://doi.org/10.1109/TIT.1962.1057777
tags: [code-based, information-set-decoding, isd, syndrome-decoding, baseline, foundational, cryptanalysis]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Introduces information set decoding: guess a set of k coordinates (an
information set) that is error-free, invert the corresponding submatrix, and
check the resulting candidate's weight. Repeat until a guess is clean. Every
subsequent generic decoding algorithm for random linear codes -- and therefore
every generic attack on every code-based scheme -- is a refinement of this loop.

## Key claims (as reported)
- Decoding reduces to a search over information sets, each iteration costing one
  Gaussian elimination.
- The resulting complexity is exponential with a small constant in the exponent:
  reported worst-case ~2^{0.1207n} for full-distance decoding of a random binary
  code, ~2^{0.058n} for half-distance decoding.

## Relevance to this program
This is the baseline of code-based cryptanalysis in exactly the sense that
Pollard rho (KN-TECH-001) is the baseline of ECDLP: the generic attack that any
claimed improvement must be measured against. Sixty-four years of refinement
have moved the half-distance exponent from ~0.058 to ~0.047 (KN-TECH-057,
KN-OPEN-019) -- a far smaller relative movement than the target-result-profile
exemplar achieves, which is what makes the ISD exponent an interesting target
and a hard one.

## Not verified here
Primary PDF not fetched. Author, title, venue, volume/issue/pages, year, and DOI
confirmed via search against DBLP and DOI records. The exponent figures are
relayed from secondary sources (modern ISD papers quoting Prange), not derived
or checked here; see KN-TECH-057 for how they are used and hedged.
