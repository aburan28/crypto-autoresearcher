---
id: KN-LIT-23ad7f
type: literature
title: "RISC-V based Vectorization of Classic McEliece Key Generation"
authors:
  - "Mahnaz Namazi Rizi"
  - "Nusa Zidaric"
  - "Lejla Batina"
  - "Nele Mentens"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/523"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/523"
tags: [classic-mceliece, code-based, implementation, risc-v, vectorization, key-generation]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
RISC-V based **vectorisation of Classic McEliece key generation** — key
generation being the operation whose cost dominates Classic McEliece's practical
profile, since it requires Gaussian elimination on a large matrix.

## Key claims (as reported)
- Vector instruction extensions on RISC-V speed up Classic McEliece key generation.

## Relevance to this program
One of eleven entries in this sweep attacking key generation specifically
([[KN-LIT-d5b1a7]], [[KN-LIT-19691d]], [[KN-LIT-89d5df]], [[KN-LIT-76ba49]],
[[KN-LIT-b46f62]], [[KN-LIT-1d7668]] and others). That concentration is the
signal: when a research community spends this much effort on one operation, the
operation is the bottleneck.

The transferable discipline is section 8's exact-bottleneck requirement
(`KN-TECH-080`): identify what actually dominates before optimising, and
reproduce the baseline honestly. This literature identified its bottleneck
unambiguously and then swarmed it.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2026/523 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Speedup figures, the RISC-V configuration, and the baseline compared against are
NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
