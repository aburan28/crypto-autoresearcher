---
id: KN-LIT-80202e
type: literature
title: "Quantum information set decoding algorithms"
authors:
  - "Ghazal Kachigar"
  - "Jean-Pierre Tillich"
year: 2017
venue: "PQCrypto"
identifiers:
  eprint: null
  doi: "10.1007/978-3-319-59879-6_5"
  arxiv: "1703.00263"
  url: "https://arxiv.org/abs/1703.00263"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, grover, quantum-walk, asymptotics]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
The foundational paper of the quantum ISD line: applies **quantum walks** and
Grover search to the MMT and BJMM algorithms, establishing the first quantum
speedups for advanced (not merely Prange-style) ISD.

## Key claims (as reported)
- Quantum versions of MMT/BJMM-style ISD with improved asymptotic complexity over classical.
- The speedup is well short of a full square root over the classical exponent — the gain comes from parts of the algorithm, not all of it.

## Relevance to this program
The reference point for the whole quantum-ISD cluster in this sweep. Its
standing lesson, consistent with [[KN-LIT-4144]], is that **quantising a
sophisticated classical algorithm yields far less than quantising a naive
one**: Grover's square root applies to the exhaustive search, and the
sophisticated algorithm had already replaced most of that search with structure.

Held as the general caution: a proposed quantum improvement must be computed
against the *best classical algorithm*, not against brute force.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the arXiv record for 1703.00263; citation verified against the Crossref record (DOI 10.1007/978-3-319-59879-6_5).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Exact exponents and the quantum cost model are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
