---
id: KN-LIT-1d7668
type: literature
title: "Classic McEliece key generation on RAM constrained devices"
authors:
  - "Rainer Urian"
  - "Raphael Schermann"
year: 2022
venue: null
identifiers:
  eprint: "iacr:2022/1613"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1613"
tags: [classic-mceliece, code-based, implementation, key-generation, ram-constrained, embedded]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Classic McEliece **key generation on RAM-constrained devices** — the hardest
combination in this scheme's deployment story, since key generation is both the
most expensive operation and the most memory-hungry.

## Key claims (as reported)
- Classic McEliece key generation is feasible on RAM-constrained devices.

## Relevance to this program
A feasibility result on the scheme's worst case. Held with [[KN-LIT-4a6dd5]] and
[[KN-LIT-082ca9]] as the memory-constrained cluster, and as an example of the
useful research move of **attacking the case everyone assumes is impossible**
rather than improving the case that already works.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/1613 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The RAM bound achieved and the platform are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
