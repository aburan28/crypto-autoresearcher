---
id: KN-LIT-4280
type: literature
title: "How to Fake Auxiliary Input"
authors:
  - "Dimitar Jetchev"
  - "Krzysztof Pietrzak⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Consider a joint distribution (X, A) on a set X × {0, 1}l . We show that for any family F of distinguishers f : X × {0, 1}l → {0, 1}, there exists a simulator h : X → {0, 1}l such that 1. no function in F can distinguish (X, A) from (X, h(X)) with advantage ε, 2. h is only O(23l ε−2 ) times less efficient than the functions in F.

## Key claims (as reported)
- For the most interesting settings of the parameters (in particular, the cryptographic case where X has superlogarithmic min-entropy, ε > 0 is negligible and F consists of circuits of polynomial size), we can make the simulator h deterministic.
- As an illustrative application of our theorem, we give a new security proof for the leakage-resilient stream-cipher from Eurocrypt’09.
- Our proof is simpler and quantitatively much better than the original proof using the dense model theorem, giving meaningful security guarantees if instantiated with a standard blockcipher like AES.
- Subsequent to this work, Chung, Lui and Pass gave an interactive variant of our main theorem, and used it to investigate weak notions of ZeroKnowledge.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83490145 (1).pdf`
- `downloads/83490145 (2).pdf`
- `downloads/83490145 (3).pdf`
- `downloads/83490145.pdf`
