---
id: KN-LIT-6bdee9
type: literature
title: "Side-channel attacks on the McEliece and Niederreiter public-key cryptosystems"
authors:
  - "Roberto M. Avanzi"
  - "Simon Hoerder"
  - "Dan Page"
  - "Michael Tunstall"
year: 2011
venue: "Journal of Cryptographic Engineering"
identifiers:
  eprint: "iacr:2010/479"
  doi: "10.1007/s13389-011-0024-9"
  arxiv: null
  url: "https://eprint.iacr.org/2010/479"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, niederreiter, survey, foundational, countermeasures]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Side-channel attacks on **both** the McEliece and Niederreiter cryptosystems —
an early systematic treatment covering the pair rather than one scheme, in the
Journal of Cryptographic Engineering.

## Key claims (as reported)
- Side-channel vulnerabilities are identified in McEliece and Niederreiter implementations.
- Systematic treatment across the two dual constructions.

## Relevance to this program
Early and broad, so useful as the entry point to the section's history. Treating
McEliece and Niederreiter together is also correct in substance — they are dual
formulations of the same trapdoor, and a leakage result about one usually maps
onto the other.

Held as a reminder to check whether a result about an object applies
automatically to its dual before treating the two as separate findings.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2010/479 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/s13389-011-0024-9).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific vulnerabilities and countermeasures are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
