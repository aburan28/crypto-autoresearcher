---
id: KN-LIT-ef4327
type: literature
title: "Concrete time/memory trade-offs in generalised Stern's ISD algorithm"
authors:
  - "Sreyosi Bhattacharyya"
  - "Palash Sarkar"
year: 2023
venue: "Indocrypt"
identifiers:
  eprint: "iacr:2023/1940"
  doi: "10.1007/978-3-031-56232-7_15"
  arxiv: null
  url: "https://eprint.iacr.org/2023/1940"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, stern, time-memory-tradeoff, concrete-security]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Concrete time/memory trade-offs in a **generalised Stern ISD algorithm** —
Stern's algorithm ([[KN-LIT-fb9047]]) being the birthday-based refinement of
Lee–Brickell that all later ISD improvements build on. The emphasis is
concrete rather than asymptotic.

## Key claims (as reported)
- A generalisation of Stern's algorithm with an explicit family of time/memory trade-off points.
- Concrete rather than asymptotic accounting.

## Relevance to this program
Concrete-over-asymptotic is the correct posture for parameter selection, and
this program's evidence records are required to be concrete in the same way:
scoped to tested parameters, with the cost model stated.

The Stern lineage is also the cleanest illustration of the ISD family's overall
shape — decades of refinement, each real, together moving the exponent very
little. Held as the calibration anchor for how much a "significant
cryptanalytic improvement" typically buys.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/1940 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-031-56232-7_15).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The trade-off curve and any claimed improvement over the Syndrome Decoding
Estimator's ([[KN-LIT-6923]]) numbers are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
