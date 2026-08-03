---
id: KN-LIT-76ba49
type: literature
title: "Evaluation of Gaussian elimination using HLS for fast public key generation in the Classic McEliece"
authors:
  - "Masashi Kihara"
  - "Keisuke Iwai"
  - "Takashi Matsubara"
  - "Takakazu Kurokawa"
year: 2025
venue: "Bulletin of Networking, Computing, Systems, and Software"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "http://ww.bncss.org/index.php/bncss/article/view/186"
tags: [classic-mceliece, code-based, implementation, hardware, gaussian-elimination, hls, key-generation]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
Evaluation of **Gaussian elimination using high-level synthesis (HLS)** for fast
public key generation in Classic McEliece.

## Key claims (as reported)
- HLS-generated Gaussian elimination hardware for Classic McEliece key generation.

## Relevance to this program
Part of the key-generation cluster ([[KN-LIT-23ad7f]]), and of the HLS
sub-thread with [[KN-LIT-bfef5d]] — the recurring question being whether
high-level synthesis can approach hand-written RTL for this workload.

**Does not bear on the ECDLP.**

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

**Citation NOT independently verified** — not found in IACR ePrint or Crossref
during this sweep; the BNCSS URL is transcribed from the bibliography and was
not resolved. Results NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
