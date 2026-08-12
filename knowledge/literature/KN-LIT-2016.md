---
id: KN-LIT-2016
type: literature
title: "A Cookbook for Black-Box Separations and a Recipe for UOWHFs"
authors:
  - "Kfir Barhum"
  - "Thomas Holenstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new framework for proving fully black-box separations and lower bounds. We prove a general theorem that facilitates the proofs of fully black-box lower bounds from a one-way function (OWF).

## Key claims (as reported)
- Loosely speaking, our theorem says that in order to prove that a fully black-box construction does not securely construct a cryptographic primitive Q (e.g., a pseudo-random generator or a universal one-way hash function) from a OWF, it is enough to come up with a large enough set of functions F and a parameterized oracle (i.e., an oracle that is defined for every f ∈ {0, 1}n → {0, 1}n ) such that Of breaks the security of the construction when instantiated with f and the oracle satisfies two local properties.
- Our main application of the theorem is a lower bound of Ω(n/ log(n)) on the number of calls made by any fully black-box construction of a universal one-way hash function (UOWHF) from a general one-way function.
- The bound holds even when the OWF is regular, in which case it matches to a recent construction of Barhum and Maurer [4].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850659 (1).pdf`
- `downloads/77850659 (2).pdf`
- `downloads/77850659 (3).pdf`
- `downloads/77850659.pdf`
