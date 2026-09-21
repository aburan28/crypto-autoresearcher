---
id: KN-LIT-e8eaf8
type: literature
title: "A designer's guide to KEMs"
authors:
  - "Alexander W. Dent"
year: 2003
venue: "Cirencester"
identifiers:
  eprint: "iacr:2002/174"
  doi: "10.1007/978-3-540-40974-8_12"
  arxiv: null
  url: "https://eprint.iacr.org/2002/174"
tags: [cca, kem, provable-security, code-based, kem-design, foundational, methodology]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**A designer's guide to KEMs**: the paper that established the KEM/DEM paradigm
as a design discipline — build a key encapsulation mechanism and a data
encapsulation mechanism separately, prove each, and compose.

## Key claims (as reported)
- KEM/DEM is a sound and practical framework for public-key encryption.
- Guidance for constructing KEMs with provable security, rather than one specific scheme.

## Relevance to this program
Held for the **abstraction move** rather than the cryptography. Before KEM/DEM,
public-key encryption schemes were analysed as wholes; afterwards the field had
an interface, and the two sides could be improved independently. Every scheme in
this bibliography's section 3 is downstream of that decomposition.

The parallel to this program's own architecture is exact and worth stating: the
value of separating question, hypothesis, experiment contract, run record,
evidence and decision is the same value — **each part is checkable on its own,
and the composition's guarantees follow from the parts'.**

## Not verified here
Citation verified against the IACR ePrint record for report 2002/174 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-540-40974-8_12).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The specific constructions and proofs in the paper are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
