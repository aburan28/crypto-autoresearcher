---
id: KN-LIT-2249
type: literature
title: "A Synthetic Indifferentiability Analysis of Interleaved Double-Key Even-Mansour Ciphers"
authors:
  - "Chun Guo"
  - "Dongdai Lin⋆⋆"
year: null
venue: "IACR Cryptology ePrint Archive"
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
Iterated Even-Mansour scheme (IEM) is a generalization of the basic 1-round proposal (ASIACRYPT ’91). The scheme can use one key, two keys, or completely independent keys.

## Key claims (as reported)
- Most of the published security proofs for IEM against relate-key and chosen-key attacks focus on the case where all the round-keys are derived from a single master key.
- Whereas results beyond this barrier are relevant to the cryptographic problem whether a secure blockcipher with key-size twice the block-size can be built by mixing two relatively independent keys into IEM and iterating sufficiently many rounds, and this strategy actually has been used in designing blockciphers for a long-time.
- This work makes the first step towards breaking this barrier and considers IEM with Interleaved Double independent round-keys: IDEMr ((k1 , k2 ), m) = ki ⊕ (Pr (. . . k1 ⊕ P2 (k2 ⊕ P1 (k1 ⊕ m)) . . .)), where i = 2 when r is odd, and i = 1 when r is even.
- As results, this work proves that 15 rounds can achieve (full) indifferentiability from an ideal cipher with O(q 8 /2n ) security bound.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520173 (1).pdf`
- `downloads/94520173.pdf`
