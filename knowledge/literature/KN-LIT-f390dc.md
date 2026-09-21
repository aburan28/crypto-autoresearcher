---
id: KN-LIT-f390dc
type: literature
title: "A new algorithm for finding minimum-weight words in a linear code: application to McEliece's cryptosystem and to narrow-sense BCH codes of length 511"
authors:
  - "Anne Canteaut"
  - "Florent Chabaud"
year: 1998
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/18.651067"
  arxiv: null
  url: "https://www.rocq.inria.fr/secret/Anne.Canteaut/Publications/Canteaut_Chabaud98.pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, minimum-weight, canteaut-chabaud, bch-codes, algorithm]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An algorithm for finding **minimum-weight words in a linear code**, applied both
to McEliece's cryptosystem and to narrow-sense BCH codes of length 511. The
key device is to update the Gaussian elimination *incrementally* between
iterations — swapping one column rather than redoing the elimination — which
removes the dominant per-iteration cost of earlier ISD implementations.

## Key claims (as reported)
- An improved minimum-weight-word algorithm, with the incremental column-swap refinement of the information-set update.
- Applied to McEliece and to determining minimum weights of BCH codes of length 511 — a coding-theory result, not only a cryptanalytic one.

## Relevance to this program
Held for two reasons. It is the engine behind [[KN-LIT-7c6f53]], the attack on
the original parameters. And it is an unusually clean instance of a **pure
implementation-level insight producing a real cryptanalytic advance**: the
asymptotic algorithm did not change, the per-iteration cost did.

That is a genuine and under-rated route to an exponent-relevant result, and it
is one this program should treat as legitimate rather than as mere engineering
— while still reporting it, per rule 4, as the constant-factor improvement it
is.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/18.651067).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The complexity expressions and the BCH minimum-weight results are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
