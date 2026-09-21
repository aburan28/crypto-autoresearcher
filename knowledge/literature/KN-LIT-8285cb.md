---
id: KN-LIT-8285cb
type: literature
title: "Information-set decoding with hints"
authors:
  - "Anna-Lena Horlemann"
  - "Sven Puchinger"
  - "Julian Renner"
  - "Thomas Schamberger"
  - "Antonia Wachter-Zeh"
year: 2021
venue: "Code-Based Cryptography"
identifiers:
  eprint: "iacr:2021/279"
  doi: "10.1007/978-3-030-98365-9_4"
  arxiv: null
  url: "https://eprint.iacr.org/2021/279"
tags: [code-based, mceliece, structural-attack, key-recovery, isd, hints, partial-information, side-channel-theory]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Information-set decoding with hints**: incorporating partial side information
about the error vector into ISD, so that leakage of any kind can be converted
into decoding speedup.

## Key claims (as reported)
- ISD algorithms can be adapted to exploit partial information about the error vector.
- The framework is generic in the hint type rather than tied to one leakage source.

## Relevance to this program
The decoding-side companion to [[KN-LIT-fbc2c8]], and the theoretical machinery
behind the side-channel-assisted ISD attacks in section 4 of this bibliography
([[KN-LIT-6614]], [[KN-LIT-fab214]]).

The abstraction is what makes it valuable: **"hint" as a generic interface**
between a physical measurement and an algebraic algorithm. That separation —
leakage model on one side, algorithm on the other — is good research design and
is worth copying whenever this program models partial information.

## Not verified here
Citation verified against the IACR ePrint record for report 2021/279 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-030-98365-9_4).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The hint models supported and the speedups obtained are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
