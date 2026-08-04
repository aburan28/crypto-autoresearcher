---
id: KN-LIT-7d6c98
type: literature
title: "Profiled side-channel attack on cryptosystems based on the binary syndrome decoding problem"
authors:
  - "Brice Colombier"
  - "Vlad-Florin Drăgoi"
  - "Pierre-Louis Cayrel"
  - "Vincent Grosso"
year: 2022
venue: null
identifiers:
  eprint: "iacr:2022/125"
  doi: "10.1109/tifs.2022.3198277"
  arxiv: null
  url: "https://eprint.iacr.org/2022/125"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, profiled-attack, syndrome-decoding, generic-attack]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **profiled** side-channel attack on cryptosystems based on the **binary
syndrome decoding problem** — stated against the problem class rather than
against one scheme, so it applies to any implementation performing binary
syndrome decoding.

## Key claims (as reported)
- Profiled leakage attacks apply generically to binary-syndrome-decoding cryptosystems.
- Scheme-agnostic within that class.

## Relevance to this program
The generalisation move again, this time on the attack side: framing the target
as **the computation performed** rather than the scheme name means the result
covers implementations that did not exist when it was written.

Worth copying. A result this program states about a computational step is more
durable, and more honestly scoped, than one stated about a particular
implementation of it — provided the step is what was actually tested.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/125 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1109/tifs.2022.3198277).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which implementations were tested, and the profiling requirements, are NOT
recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
