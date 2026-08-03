---
id: KN-LIT-ced593
type: literature
title: "On the complexity of some cryptographic problems based on the general decoding problem"
authors:
  - "Thomas Johansson"
  - "Fredrik Jönsson"
year: 2002
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/isit.1998.709047"
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, complexity, general-decoding, lpn]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Studies the complexity of cryptographic problems based on the **general decoding
problem** — the hardness assumption underlying code-based cryptography, treated
as a problem in its own right rather than as an attack target for one scheme.

## Key claims (as reported)
- Complexity analysis of general-decoding-based cryptographic problems.
- Problem-level rather than scheme-level.

## Relevance to this program
Held for the problem-versus-scheme distinction, which this program is required
to maintain: a result about the ECDLP is not the same as a result about a
particular curve or a particular protocol, and evidence records must say which
they establish.

Code-based cryptography's clean separation — one hard problem (syndrome
decoding), many schemes, plus a *separate* structural assumption that Goppa
codes are indistinguishable from random — is the model of that discipline. The
attacks in section 2 of this bibliography hit the second assumption, not the
first, which is only legible because the two were kept apart.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/isit.1998.709047).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific complexity results are NOT recorded here. No online copy is listed
in the bibliography.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
