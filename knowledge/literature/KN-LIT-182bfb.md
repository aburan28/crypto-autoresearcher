---
id: KN-LIT-182bfb
type: literature
title: "Asymptotics and improvements of sieving for codes"
authors:
  - "Léo Ducas"
  - "Andre Esser"
  - "Simona Etinski"
  - "Elena Kirshanova"
year: 2024
venue: "Eurocrypt"
identifiers:
  eprint: "iacr:2023/1577"
  doi: "10.1007/978-3-031-58754-2_6"
  arxiv: null
  url: "https://eprint.iacr.org/2023/1577"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, sieving, asymptotics, nearest-neighbor]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Asymptotic analysis and improvement of **sieving for codes** — the transfer of
lattice sieving technique into the code setting, where the analogue of a short
lattice vector is a low-weight codeword. Establishes the asymptotic exponents
for the approach and improves on the first published versions.

## Key claims (as reported)
- Improved asymptotics for code sieving.
- Positioned as the asymptotic companion to the concrete sieving-style ISD algorithms ([[KN-LIT-01f731]]).

## Relevance to this program
The clearest available case study in **technique transfer between hard
problems** — sieving was developed for lattices and then carried to codes — and
therefore a direct precedent for the kind of cross-domain move this program's
idea generator is asked to attempt.

Two things are worth carrying: the transfer worked, and it did **not** produce
a break. The exponents moved; the parameter sets did not fall. That is the
realistic prior for a technique-transfer proposal, and it is the honest
counterweight to the temptation to present a successful transfer as a break.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/1577 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-58754-2_6).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific exponents claimed and the heuristics they rest on are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
