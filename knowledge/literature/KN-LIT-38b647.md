---
id: KN-LIT-38b647
type: literature
title: "Reduction from sparse LPN to LPN, Dual Attack 3.0"
authors:
  - "Kévin Carrier"
  - "Thomas Debris-Alazard"
  - "Charles Meyer-Hilfiger"
  - "Jean-Pierre Tillich"
year: 2024
venue: "Eurocrypt"
identifiers:
  eprint: "iacr:2023/1852"
  doi: "10.1007/978-3-031-58754-2_11"
  arxiv: null
  url: "https://eprint.iacr.org/2023/1852"
tags: [code-based, mceliece, structural-attack, key-recovery, lpn, dual-attack, statistical-decoding, reduction]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Dual Attack 3.0**: a reduction from **sparse LPN to LPN**, continuing the
statistical-decoding line ([[KN-LIT-b66899]], [[KN-LIT-6796]]) that recasts
decoding as a learning problem.

## Key claims (as reported)
- A reduction from sparse LPN to standard LPN.
- Third generation of the dual-attack framing for decoding.

## Relevance to this program
Two things make this worth holding. First, the **reduction** form: converting
one problem into another whose algorithms are better developed is the highest-
leverage move available when direct attack stalls, and it is a form this
program's proposals are explicitly encouraged to attempt.

Second, the version number. "Dual Attack 3.0" is a public admission that
versions 1 and 2 needed replacing — and the lattice-side dual attack has an
active dispute about whether its heuristics hold at all (`KN-TECH-039`).
Held as a caution: **a technique family under active revision is not a stable
foundation to build a claim on**, and citing its current version as settled
would misrepresent it.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/1852 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-58754-2_11).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The reduction's parameters, tightness, and consequences for code-based
parameter sets are NOT recorded here. Whether the heuristic concerns raised
about lattice dual attacks apply to this code-side line is likewise not assessed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
