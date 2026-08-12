---
id: KN-LIT-fb9047
type: literature
title: "A method for finding codewords of small weight"
authors:
  - "Jacques Stern"
year: 1989
venue: "Coding Theory and Applications"
identifiers:
  eprint: null
  doi: "10.1007/bfb0019850"
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, stern, birthday, algorithm, foundational]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Stern's algorithm**: finds low-weight codewords by splitting the information
set into two halves, searching for partial collisions on a window of `l`
syndrome coordinates, and combining. The birthday structure it introduced is
the basis of essentially every subsequent ISD improvement — Dumer's variant,
MMT ([[KN-LIT-3368]]), BJMM ([[KN-LIT-3367]]), and the sieving-style algorithms
([[KN-LIT-01f731]]) all descend from it.

## Key claims (as reported)
- A probabilistic algorithm for finding small-weight codewords, substantially faster than Lee–Brickell and Leon.
- The improvement comes from a birthday/meet-in-the-middle search inside the information set, at the cost of memory for the lists.

## Relevance to this program
The single most-cited algorithm in this bibliography's first section and the
right anchor for the family. Two properties matter to this program.

**The improvement is structural, not parametric.** Stern did not tune
Lee–Brickell; he replaced its inner search with a different algorithmic
primitive. That is the move `docs/inventor-protocol.md` asks proposals to
identify.

**It introduced the memory cost** that every later variant inherits and that
[[KN-LIT-5677ae]], [[KN-LIT-b8a8be]] and [[KN-LIT-f51628]] spend their effort
containing. A speedup bought with memory is a trade, not a gain, until the
memory is priced — the discipline this program applies to its own solver
claims.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/bfb0019850).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Contents unread; no online copy listed. The complexity statements here are the
standard textbook account of Stern's algorithm and are **recalled, not read
from this source**.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
