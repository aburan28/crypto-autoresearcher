---
id: KN-LIT-e530e8
type: literature
title: "Side channels in the McEliece PKC"
authors:
  - "Falko Strenzke"
  - "Erik Tews"
  - "H. Gregor Molter"
  - "Raphael Overbeck"
  - "Abdulhadi Shoufan"
year: 2008
venue: "PQCrypto"
identifiers:
  eprint: null
  doi: "10.1007/978-3-540-88403-3_15"
  arxiv: null
  url: null
tags: [side-channel, code-based, classic-mceliece, implementation-attack, timing-attack, foundational, historical]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Side channels in the McEliece PKC** — the earliest entry in this
bibliography's side-channel section, identifying that the decryption procedure
leaks through timing and power behaviour.

## Key claims (as reported)
- The McEliece decryption procedure exhibits exploitable side channels.

## Relevance to this program
The start of a seventeen-year, ongoing campaign. What that record shows is worth
stating plainly: **the mathematics has held since 1978, and the implementations
have been attacked continuously since 2008 and are still being attacked in
2025.**

This program works on mathematical problems, and this asymmetry is the reason
its conclusions are scoped the way rule 4 requires. A result about the hardness
of a problem is not a result about the security of anything built on it, and
this bibliography is the empirical case for that separation being real rather
than pedantic.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-540-88403-3_15).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific channels identified are NOT recorded here. No online copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
