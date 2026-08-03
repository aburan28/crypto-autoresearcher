---
id: KN-LIT-886c90
type: literature
title: "A timing attack against the secret permutation in the McEliece PKC"
authors:
  - "Falko Strenzke"
year: 2010
venue: "PQCrypto"
identifiers:
  eprint: null
  doi: "10.1007/978-3-642-12929-2_8"
  arxiv: null
  url: null
tags: [side-channel, code-based, classic-mceliece, implementation-attack, timing-attack, permutation, historical]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **timing attack against the secret permutation** in the McEliece PKC — early
evidence that the permutation, already known to be weak as a mathematical
hiding mechanism ([[KN-LIT-0f43ad]]), also leaks through implementation
behaviour.

## Key claims (as reported)
- Timing variation during decryption reveals information about the secret permutation.

## Relevance to this program
Notable for attacking **the same component the mathematics had already
discounted**. Support splitting says the permutation is not the security
argument; timing analysis says the implementation leaks it anyway. Two
independent routes to the same conclusion, from different disciplines.

The transferable habit: when a component is known to be non-load-bearing
mathematically, that is not a reason to stop protecting it — and when a
component is known to be weak by one method, other methods are likely to reach
it too.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-642-12929-2_8).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The attack's requirements and effectiveness are NOT recorded here. No online
copy listed.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
