---
id: KN-LIT-bbd0e9
type: literature
title: "A probabilistic algorithm for computing minimum weights of large error-correcting codes"
authors:
  - "Jeffrey S. Leon"
year: 1988
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/18.21270"
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, leon, minimum-weight, algorithm, historical]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Leon's algorithm**: a probabilistic method for computing minimum weights of
large error-correcting codes, adding a zero-window restriction to the
information-set search. Written as a coding-theory tool for computing minimum
distances, it became a standard cryptanalytic building block and is the
immediate predecessor of Stern's algorithm ([[KN-LIT-fb9047]]).

## Key claims (as reported)
- A probabilistic minimum-weight algorithm practical for large codes.
- Uses a window of coordinates constrained to zero to filter candidates cheaply before full evaluation.

## Relevance to this program
The purest example in this bibliography of a **tool built for one purpose
becoming a weapon for another**: Leon wanted minimum distances of large codes,
and supplied cryptanalysis with one of its standard primitives.

This program's corpus policy follows from exactly this: material with no
cryptanalytic framing is worth holding, because the transfer direction cannot
be predicted from the paper's own stated purpose.

The zero-window idea is also still live — [[KN-LIT-f51628]] is a 2024 sieving
method built on the same device.

## Not verified here
citation verified against the Crossref record (DOI 10.1109/18.21270).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Contents unread; no online copy listed. The description of the zero-window
mechanism is the standard account and is **recalled, not read from this
source**.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
