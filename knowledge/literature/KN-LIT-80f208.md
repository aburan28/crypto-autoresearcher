---
id: KN-LIT-80f208
type: literature
title: "Explicit bounds for generic decoding algorithms for code-based cryptography"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christiane Peters"
  - "Henk C. A. van Tilborg"
year: 2009
venue: "WCC"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, lower-bounds, cost-model]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Explicit bounds** for generic decoding algorithms — turning the ISD family's
cost analyses into stated bounds usable for code-based parameter selection,
rather than comparative asymptotics.

## Key claims (as reported)
- Explicit (non-asymptotic) bounds on the cost of generic decoding.
- Intended for code-based cryptography parameter choice.

## Relevance to this program
Part of the concrete-security tradition running through
[[KN-LIT-6503]] → [[KN-LIT-bb53c1]] → [[KN-LIT-6923]]: the recognition that a
cryptosystem's parameters must be justified by counted work, and that the
counting must be published in a form others can re-run.

This program's `docs/claims-and-verification.md` requires exactly that of its
own claims — a cost assertion that cannot be independently recomputed is not
evidence.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT verified.** The bibliography lists no online copy for this WCC
2009 paper and it was not found in IACR ePrint or Crossref during this sweep.
The bound statements are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
