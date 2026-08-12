---
id: KN-LIT-2999
type: literature
title: "Compact Zero-Knowledge Proofs for Threshold ECDSA with Trustless Setup"
authors:
  - "Tsz Hon Yuen"
  - "Handong Cui"
  - "Xiang Xie"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, dlp, ecdsa, fhe, number-theory, pairing, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold ECDSA signatures provide a higher level of security to a crypto wallet since it requires more than t parties out of n parties to sign a transaction. The state-of-the-art bandwidth efficient threshold ECDSA used the additive homomorphic Castagnos and Laguillaumie (CL) encryption based on an unknown order group G, together with a number of zero-knowledge proofs in G.

## Key claims (as reported)
- In this paper, we propose compact zero-knowledge proofs for threshold ECDSA to lower the communication bandwidth, as well as the computation cost.
- The proposed zero-knowledge proofs include the discrete-logarithm relation in G and the well-formedness of a CL ciphertext.
- When applied to two-party ECDSA, we can lower the bandwidth of the key generation algorithm by 47%, and the running time for the key generation and signing algorithms are boosted by about 35% and 104% respectively.
- When applied to threshold ECDSA, our first scheme is more optimized for the key generation algorithm (about 70% lower bandwidth and 85% faster computation in key generation, at a cost of 20% larger bandwidth in signing), while our second scheme has an all-rounded performance improvement (about 60% lower bandwidth, 46% faster computation in key generation without additional cost in signing).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110161 (1).pdf`
- `downloads/127110161.pdf`
