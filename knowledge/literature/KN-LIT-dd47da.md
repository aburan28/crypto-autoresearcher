---
id: KN-LIT-dd47da
type: literature
title: "Optimizing BJMM with nearest neighbors: full decoding in 2^{2n/21} and McEliece security"
authors:
  - "Leif Both"
  - "Alexander May"
year: 2017
venue: "WCC"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://web.archive.org/web/20201127050037/https://www.cits.ruhr-uni-bochum.de/imperia/md/content/may/paper/bjmm+.pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, bjmm, nearest-neighbor, asymptotics, mceliece-security]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
Combines BJMM ([[KN-LIT-3367]]) with nearest-neighbour search
([[KN-LIT-5324]]), reported as achieving full decoding in `2^{2n/21}` and
drawing the consequence for McEliece security. The `2n/21 ≈ 0.0952n` exponent
is the headline figure of the classical ISD state of the art for full decoding.

## Key claims (as reported)
- Full decoding in time `2^{2n/21}` for the worst-case error weight.
- An explicit consequence drawn for McEliece parameter security.

## Relevance to this program
The concrete anchor for how little the ISD exponent moved across sixty years.
Prange ([[KN-LIT-6a786b]], 1962) and the best known classical algorithm here
differ by a modest constant in the exponent — the entire literature in section 1
of this bibliography, roughly, bought that difference.

This program cites that record when judging its own proposals against
`docs/target-result-profile.md`: an exponent-moving result on a central hard
problem is rare and hard-won, and a proposal claiming one cheaply should expect
the corresponding scrutiny.

**Does not bear on the ECDLP.**

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation not independently verified** — the archived PDF URL the bibliography
gives for this WCC 2017 paper is the *same* URL it gives for May–Meurer–Thomae
(Asiacrypt 2011, [[KN-LIT-3368]]). The Classic McEliece page appears to carry a
link error here; the entry records the bibliography's own note. The `2^{2n/21}`
figure is taken from the title as listed and has NOT been checked against the
paper.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
