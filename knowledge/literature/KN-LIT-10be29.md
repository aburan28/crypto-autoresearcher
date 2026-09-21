---
id: KN-LIT-10be29
type: literature
title: "An observation on the security of McEliece's public-key cryptosystem"
authors:
  - "Pil Joong Lee"
  - "Ernest F. Brickell"
year: 1988
venue: "Eurocrypt"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [isd, syndrome-decoding, code-based, mceliece, lee-brickell, algorithm, foundational]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
**Lee–Brickell**: the first substantial improvement on Prange's algorithm for
attacking McEliece. Prange guesses an error-free information set; Lee and
Brickell allow up to `p` errors inside the chosen set and search over those,
trading a more expensive per-iteration test for a much higher success
probability per iteration.

## Key claims (as reported)
- Allowing a small number `p` of errors within the information set improves the overall work factor over Prange's algorithm.
- An observation about McEliece's security — the system is not broken, the work factor is reduced.

## Relevance to this program
The first step of the sixty-year ISD sequence and the cleanest illustration of
its characteristic move: **relax a constraint the original algorithm imposed
for convenience, and pay for the relaxation with per-iteration work.** Nearly
every later improvement is a more elaborate version of the same trade.

Recorded also for its title. "An observation on the security of…" is a
proportionate description of a genuine but bounded improvement — the register
`docs/target-result-profile.md` asks this program's own deliverables to
maintain.

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** in ePrint or Crossref; no online copy is
listed for these Eurocrypt 1988 proceedings. The description of the algorithm
is the standard textbook account and is **recalled, not read from this
source**.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
