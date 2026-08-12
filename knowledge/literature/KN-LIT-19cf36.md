---
id: KN-LIT-19cf36
type: literature
title: "On insecurity of cryptosystems based on generalized Reed-Solomon codes"
authors:
  - "Vladimir M. Sidelnikov"
  - "Sergey O. Shestakov"
year: 1992
venue: "Discrete Mathematics and Applications"
identifiers:
  eprint: null
  doi: "10.1515/dma.1992.2.4.439"
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, grs-codes, niederreiter, polynomial-time, variant-break, foundational]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Sidelnikov–Shestakov**: generalised Reed–Solomon codes are unsuitable for
McEliece/Niederreiter — their structure can be recovered in polynomial time from
the public key. GRS codes are MDS and therefore the most efficient choice
available, which is exactly why they had been proposed.

## Key claims (as reported)
- Polynomial-time recovery of the GRS structure from a public generator/parity-check matrix.
- A complete structural break of GRS-based instantiations, not a parameter weakening.

## Relevance to this program
The founding result of this bibliography's second section, and the origin of the
principle everything after it repeats: **the most efficient code family was the
most structured, and the structure was recoverable.**

Its consequence is visible in the design of Classic McEliece thirty years later,
which pays a megabyte-scale public key rather than take structural risk. That
is a design trade this program should recognise when evaluating proposals:
efficiency gained from structure is a **loan against the security argument**,
and the burden of proof sits with the borrower.

Held with [[KN-LIT-33d2bd]] and [[KN-LIT-49a052]], which record the failed
attempts to repair GRS-based schemes.

## Not verified here
citation verified against the Crossref record (DOI 10.1515/dma.1992.2.4.439).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The attack's complexity and its exact requirements are NOT recorded here. No
online copy listed for this Discrete Mathematics and Applications paper.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
