---
id: KN-LIT-1d8337
type: literature
title: "Masking large keys in hardware: a masked implementation of McEliece"
authors:
  - "Cong Chen"
  - "Thomas Eisenbarth"
  - "Ingo von Maurich"
  - "Rainer Steinwandt"
year: 2015
venue: "SAC"
identifiers:
  eprint: "iacr:2015/924"
  doi: "10.1007/978-3-319-31301-6_18"
  arxiv: null
  url: "https://eprint.iacr.org/2015/924"
tags: [classic-mceliece, code-based, implementation, hardware, masking, countermeasure, side-channel-resistance, large-keys]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Masking large keys in hardware**: a masked implementation of McEliece. Masking
splits secret values into randomised shares so that no single measured value
depends on the secret; the difficulty here is that McEliece's secret is very
large, and masking cost scales with it.

## Key claims (as reported)
- A masked hardware implementation of McEliece.
- Addresses the specific difficulty of masking a large key.

## Relevance to this program
The **defensive** entry that pairs with the side-channel section, and an example
of a countermeasure whose cost is driven by an unusual property of the scheme.
Masking is routine for schemes with small secrets; McEliece's key size turns it
into a research problem.

Held as an instance of a general pattern this program should expect: **a
standard technique's cost model can change qualitatively when a parameter moves
far outside its usual range** — which is why a technique validated in one regime
is not automatically applicable in another.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2015/924 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-319-31301-6_18).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The masking scheme, its order, and its overhead are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
