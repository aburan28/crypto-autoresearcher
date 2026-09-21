---
id: KN-LIT-6161
type: literature
title: "Realizing Chosen Ciphertext Security"
authors:
  - "Generically in Attribute-Based Encryption and"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide generic and black box transformations from any chosen plaintext secure Attribute-Based Encryption (ABE) or One-sided Predicate Encryption system into a chosen ciphertext secure system. Our transformation requires only the IND-CPA security of the original ABE scheme coupled with a pseudorandom generator (PRG) with a special security property.

## Key claims (as reported)
- In particular, we consider a PRG with an n bit input s ∈ {0, 1}n and n · ` bit output y1 , . . . , yn where each yi is an ` bit string.
- Then for a randomly chosen s the following two distributions should be computationally indistinguishable.
- In the first distribution rsi ,i = yi and rs̄i ,i is chosen randomly for i ∈ [n].
- In the second distribution all rb,i are chosen randomly for i ∈ [n], b ∈ {0, 1}.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940363 (1).pdf`
- `downloads/116940363.pdf`
