---
id: KN-LIT-d1a453
type: literature
title: "Recognizing the structure of permuted reducible codes"
authors:
  - "Raphael Overbeck"
year: 2007
venue: "WCC"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [code-based, mceliece, structural-attack, key-recovery, permuted-codes, reducible-codes, structural-recognition]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
Recognising the structure of **permuted reducible codes** — detecting that a
code presented in permuted form decomposes, which breaks constructions relying
on the permutation to hide a reducible structure.

## Key claims (as reported)
- Reducible structure survives permutation and can be recognised.

## Relevance to this program
A clean statement of the general principle underlying every structural attack
in this section: **permutation hides less than it appears to.** Invariants that
do not depend on coordinate order — dimensions of subcode intersections, hulls,
Schur/square-code dimensions, syzygies — pass straight through the
permutation.

The design consequence, and the reason this program should care: if the trapdoor
is "the structured object is hidden by a relabelling", the relevant security
question is **which invariants are relabelling-independent**, not how large the
relabelling space is. That question generalises well beyond codes.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — not found in ePrint or Crossref, and
no online copy listed. The recognition algorithm and its cost are NOT recorded
here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
