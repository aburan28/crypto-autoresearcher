---
id: KN-LIT-5656
type: literature
title: "Optimal Randomness Extraction from a Diffie-Hellman Element"
authors:
  - "Céline Chevalier"
  - "Pierre-Alain Fouque"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, finite-field, hash, pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study a quite simple deterministic randomness extractor from random Diffie-Hellman elements defined over a prime order multiplicative subgroup G of a finite field Zp (the truncation), and over a group of points of an elliptic curve (the truncation of the abscissa). Informally speaking, we show that the least significant bits of a random element in G ⊂ Z∗p or of the abscissa of a random point in E (Fp ) are indistinguishable from a uniform bit-string.

## Key claims (as reported)
- Such an operation is quite efficient, and is a good randomness extractor, since we show that it can extract nearly the same number of bits as the Leftover Hash Lemma can do for most Elliptic Curve parameters and for large subgroups of finite fields.
- To this aim, we develop a new technique to bound exponential sums that allows us to double the number of extracted bits compared with previous known results proposed at ICALP’06 by Fouque et al.
- It can also be used to improve previous bounds proposed by Canetti et al.
- One of the main application of this extractor is to mathematically prove an assumption proposed at Crypto ’07 and used in the security proof of the Elliptic Curve Pseudo Random Generator proposed by the NIST.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790573 (1).pdf`
- `downloads/54790573 (2).pdf`
- `downloads/54790573 (3).pdf`
- `downloads/54790573.pdf`
