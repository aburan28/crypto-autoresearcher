---
id: KN-LIT-f1eb40
type: literature
title: "Algebraic key-recovery side-channel attack on Classic McEliece"
authors:
  - "Michaël Bulois"
  - "Pierre-Louis Cayrel"
  - "Vlad-Florin Drăgoi"
  - "Vincent Grosso"
year: 2025
venue: "SAC"
identifiers:
  eprint: null
  doi: "10.1007/978-3-032-10536-3_20"
  arxiv: null
  url: "https://sacworkshop.org/SAC25/preproceedings/sac2025-2-paper13.pdf"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, key-recovery, algebraic, profiling]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An **algebraic key-recovery side-channel attack on Classic McEliece**: physical
leakage supplies partial information, and algebraic techniques complete the key
from it. The pairing of measurement with algebra is what distinguishes this
generation of attacks from earlier purely statistical ones.

## Key claims (as reported)
- Full secret key recovery from side-channel measurements on Classic McEliece.
- Algebraic post-processing does the completion work.

## Relevance to this program
Belongs to the largest coherent cluster in this sweep — a sustained,
multi-year, multi-group campaign of physical attacks on Classic McEliece
implementations. The theoretical basis is [[KN-LIT-fbc2c8]]: **partial knowledge
of a structured secret collapses the rest.**

The standing observation for this program is that the *mathematical* target has
survived sixty years while the *implementations* are attacked successfully year
after year. When this program states a conclusion about a mathematical problem,
that conclusion must not be read as a statement about any system realising it —
a distinction rule 4's scoping requirement enforces.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-032-10536-3_20).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The measurement setup, trace counts, target implementation and success rate are
NOT recorded here. The SAC preproceedings PDF was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
