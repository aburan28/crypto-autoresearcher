---
id: KN-LIT-b03de7
type: literature
title: "Non-binary information set decoding and an attack on BCH-McEliece: A tale of two approaches to code-based cryptanalysis"
authors:
  - "Freja Elbro"
year: 2025
venue: "PhD thesis, Technical University of Denmark (DTU)"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://backend.orbit.dtu.dk/ws/portalfiles/portal/429438711/PhD_Thesis_FE.pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, non-binary-isd, bch-codes, thesis, algebraic-cryptanalysis]
confidence: reported
citation_verified: false
added: "2026-08-03"
superseded_by: null
---

## Contribution
PhD thesis covering two complementary approaches to code-based cryptanalysis:
**non-binary information set decoding**, and a **structural attack on
BCH-McEliece** (McEliece instantiated with BCH rather than Goppa codes). The
subtitle — "a tale of two approaches" — sets the generic-decoding and the
algebraic/structural lines against each other, which is the same split the
Classic McEliece bibliography itself uses for its first two sections.

## Key claims (as reported)
- Contributions to ISD over non-binary alphabets, where the value-recovery step has no binary shortcut.
- An attack on McEliece instantiated with BCH codes. The published companion result on BCH-McEliece is Elbro–Majenz ([[KN-LIT-2d9edb]]).

## Relevance to this program
The thesis is the long-form version of two entries already held from this
sweep ([[KN-LIT-1321dc]] on non-binary ISD, [[KN-LIT-2d9edb]] on BCH-McEliece),
so it is the reference to reach for when either short paper's argument needs
its full derivation.

The structural half is the more transferable one: it is another instance of the
pattern where **replacing the code family for efficiency destroys the security
argument**, which is the code-based analogue of choosing a curve with extra
structure. That failure mode is the direct concern of this program's
lossy-projection test (`docs/inventor-protocol.md`).

**Does not bear on the ECDLP.**

## Not verified here
**Citation NOT independently verified.** The paper was not found in IACR ePrint, arXiv or Crossref during this sweep, so the reference rests on the Classic McEliece bibliography alone and `citation_verified` is `false`.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Thesis not obtained. Chapter structure, the precise BCH parameter ranges
attacked, and the non-binary ISD complexity claims are all unread. The DTU
repository URL is recorded from the bibliography and was NOT resolved during
this sweep.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
