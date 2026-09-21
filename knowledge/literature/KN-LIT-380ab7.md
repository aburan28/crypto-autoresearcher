---
id: KN-LIT-380ab7
type: literature
title: "Full key-recovery cubic-time template attack on Classic McEliece decapsulation"
authors:
  - "Vlad-Florin Drăgoi"
  - "Brice Colombier"
  - "Nicolas Vallet"
  - "Pierre-Louis Cayrel"
  - "Vincent Grosso"
year: 2025
venue: "CHES"
identifiers:
  eprint: "iacr:2024/1694"
  doi: "10.46586/tches.v2025.i1.367-391"
  arxiv: null
  url: "https://eprint.iacr.org/2024/1694"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, template-attack, key-recovery, decapsulation, complexity]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **full key-recovery cubic-time template attack** on Classic McEliece
decapsulation. Template attacks profile a device's leakage in advance and then
classify a target trace against the profile; "cubic-time" states the recovery's
computational cost explicitly.

## Key claims (as reported)
- Full key recovery from templated decapsulation leakage.
- Cubic-time post-processing — an explicit complexity claim, not merely 'efficient'.

## Relevance to this program
Held partly for the **stated complexity**. Side-channel papers often report
success on a device without pricing the post-processing; naming the exponent
makes the claim comparable and checkable, which is what
`docs/claims-and-verification.md` requires of cost claims here.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2024/1694 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.46586/tches.v2025.i1.367-391).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Profiling requirements, trace counts, and the target implementation are NOT
recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
