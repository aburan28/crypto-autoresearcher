---
id: KN-LIT-d15818
type: literature
title: "FPGA-based Niederreiter cryptosystem using binary Goppa codes"
authors:
  - "Wen Wang"
  - "Jakub Szefer"
  - "Ruben Niederhagen"
year: 2018
venue: "PQCrypto"
identifiers:
  eprint: "iacr:2017/1180"
  doi: "10.1007/978-3-319-79063-3_4"
  arxiv: null
  url: "https://eprint.iacr.org/2017/1180"
tags: [classic-mceliece, code-based, implementation, hardware, fpga, niederreiter, goppa]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An **FPGA-based Niederreiter cryptosystem using binary Goppa codes** — the
Niederreiter dual of McEliece, implemented completely in hardware.

## Key claims (as reported)
- A complete FPGA implementation of Niederreiter with binary Goppa codes.

## Relevance to this program
Early full-hardware work in the line leading to [[KN-LIT-6565a8]]. Niederreiter
rather than McEliece is the right dual to implement, since Classic McEliece's
KEM is in fact Niederreiter-shaped.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2017/1180 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-319-79063-3_4).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Resource usage and performance are NOT recorded here. Note: the corpus holds
[[KN-LIT-3946]] ("FPGA-based **Key Generator** for the Niederreiter Cryptosystem
using Binary Goppa Codes"), a **different**, key-generation-only paper by
overlapping authors; the two were separated by hand during dedup after an
automated title match at 0.85.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
