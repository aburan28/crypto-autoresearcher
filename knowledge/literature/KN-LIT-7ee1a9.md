---
id: KN-LIT-7ee1a9
type: literature
title: "Understanding the new distinguisher of alternant codes at degree 2"
authors:
  - "Axel Lemoine"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2025/531"
  doi: "10.1007/s10623-025-01626-8"
  arxiv: null
  url: "https://eprint.iacr.org/2025/531"
tags: [code-based, mceliece, structural-attack, key-recovery, distinguisher, alternant-codes, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Explains the **new distinguisher of alternant codes at degree 2** — an
analysis paper clarifying why a recently discovered distinguisher works, rather
than introducing a new one. Alternant codes are the family containing Goppa
codes, so a distinguisher there bears directly on McEliece's structural
assumption.

## Key claims (as reported)
- An explanation of the mechanism behind the degree-2 alternant distinguisher.
- Understanding-oriented: the contribution is the reason, not the attack.

## Relevance to this program
Held for the genre as much as the content. Papers whose contribution is
**understanding why an existing attack works** are how a field converts a
surprising result into a predictive theory — and predictive theory is what tells
you which *other* parameters are affected.

This program has the same obligation in its own lifecycle: `/review-evidence`
requires the mechanism to be stated, not only the outcome, because an
unexplained empirical win cannot be scoped and therefore cannot be safely
generalised.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/531 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/s10623-025-01626-8).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The mechanism explained and its consequences for Goppa codes at Classic
McEliece parameters are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
