---
id: KN-LIT-71d1a0
type: literature
title: "The syzygy distinguisher"
authors:
  - "Hugues Randriambololona"
year: 2025
venue: "Eurocrypt"
identifiers:
  eprint: "iacr:2024/1193"
  doi: "10.1007/978-3-031-91095-1_12"
  arxiv: null
  url: "https://eprint.iacr.org/2024/1193"
tags: [code-based, mceliece, structural-attack, key-recovery, distinguisher, syzygy, commutative-algebra, alternant-codes, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**The syzygy distinguisher.** Uses syzygies — the relations among generators of
a module, a standard object of commutative algebra — to distinguish algebraic
codes from random ones. Eurocrypt 2025.

## Key claims (as reported)
- A distinguisher for algebraic codes built from syzygy computations.
- Applies to the alternant/Goppa family relevant to McEliece.

## Relevance to this program
The strongest single example in this sweep of the move
`docs/inventor-protocol.md` is built around: **import a mature object from a
neighbouring area of mathematics and ask what it computes about the target.**
Syzygies come from commutative algebra and free-resolution theory, not from
coding theory, and the distinguisher exists because someone asked what they say
about a code.

The idea generator should treat this as a template. The corresponding ECDLP
question — which established algebraic-geometry or commutative-algebra
invariants have not been computed against curve-side objects — is exactly the
kind this program is meant to generate and then test cheaply before committing
compute.

Held together with [[KN-LIT-7ee1a9]], [[KN-LIT-4c8135]] and [[KN-LIT-2127]] as
the modern distinguisher cluster.

**Does not bear on the ECDLP**, but is the sweep's best methodological exemplar
alongside [[KN-LIT-7965a1]].

## Not verified here
Citation verified against the IACR ePrint record for report 2024/1193 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-91095-1_12).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The construction, its complexity, the code families and rates for which it
succeeds, and whether it reaches Classic McEliece parameters are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
