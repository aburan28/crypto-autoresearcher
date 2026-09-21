---
id: KN-LIT-4388b3
type: literature
title: "Hybrid decoding – classical-quantum trade-offs for information set decoding"
authors:
  - "Andre Esser"
  - "Sergi Ramos-Calderer"
  - "Emanuele Bellini"
  - "José Ignacio Latorre"
  - "Marc Manzano"
year: 2022
venue: "PQCrypto"
identifiers:
  eprint: "iacr:2022/964"
  doi: "10.1007/978-3-031-17234-2_1"
  arxiv: null
  url: "https://eprint.iacr.org/2022/964"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, hybrid, cost-model, resource-estimation]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Hybrid decoding**: classical-quantum trade-offs for ISD, in which part of the
search runs on classical hardware and part on quantum hardware, with the split
chosen to optimise total cost under a constraint on quantum resources.

## Key claims (as reported)
- A family of ISD algorithms parameterised by how much work is given to the quantum device.
- Trade-off framing: the optimum depends on the assumed relative cost and availability of quantum resources.

## Relevance to this program
The hybrid framing is the honest one whenever quantum hardware is limited, and
it is the same shape as the hybrid attacks that dominate concrete lattice
estimates (`KN-TECH-082`). Held as the code-side instance of that pattern.

The transferable discipline is that **a hybrid cost is only meaningful with the
resource-availability assumption stated**; a hybrid claim without it is
unfalsifiable, which is precisely what this program's protocol forbids.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2022/964 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-17234-2_1).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The trade-off curve and the assumed quantum cost model are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
