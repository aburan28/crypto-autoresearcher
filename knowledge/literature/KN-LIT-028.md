---
id: KN-LIT-028
type: literature
title: A new efficient algorithm for computing Grobner bases without reduction to zero (F5)
authors: [Faugere Jean-Charles]
year: 2002
venue: ISSAC 2002, ACM, pp. 75-83
identifiers:
  eprint: null
  doi: 10.1145/780506.780516
  url: https://dl.acm.org/doi/10.1145/780506.780516
tags: [groebner-basis, f5, faugere, signature-based, regular-sequence, solving, point-decomposition]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Introduces a *signature-based* criterion (the "F5 criterion") that predicts,
before computing, which S-polynomial reductions would reduce to zero, and skips
them. Signatures track each polynomial's module provenance; the algorithm is
incremental (adds one generator at a time).

## Key claims (as reported)
- For a *regular sequence* F5 avoids all reductions to zero -- the dominant waste
  in Buchberger/F4 -- giving record computations (e.g. cryptographic HFE
  systems).
- Caveat (honest): F5's termination for arbitrary inputs is subtle and was the
  subject of later analysis; the strong "no reduction to zero" guarantee is tied
  to (semi-)regularity assumptions, which need not hold for structured systems.

## Relevance to this program
The state-of-the-art solver whose cost is driven by how many degrees it must
process before termination -- so its behavior on (semi-)regular sequences is
precisely what the ECDLP index-calculus complexity debate models (KN-LIT-029,
KN-OPEN-002). Semaev systems are *structured*, so whether they behave
semi-regularly (making F5's cost predictable) is exactly the open question; a
measured deviation is a legitimate finding.

## Not verified here
Full paper not read; the signature criterion and the regularity caveat relayed
from the abstract and standard secondary analyses (hence confidence: reported).
Bibliographic fields confirmed against the ACM DL DOI record via search, not by
fetching the primary page.
