---
id: KN-LIT-2653
type: literature
title: "Bandwidth-efficient threshold"
authors:
  - "Federico Savasta"
  - "Ida Tucker"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hash, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold Signatures allow n parties to share the power of issuing digital signatures so that any coalition of size at least t+1 can sign, whereas groups of t or less players cannot. Over the last few years many schemes addressed the question of realizing efficient threshold variants for the specific case of EC-DSA signatures.

## Key claims (as reported)
- In this paper we present new solutions to the problem that aim at reducing the overall bandwidth consumption.
- Our main contribution is a new variant of the Gennaro and Goldfeder protocol from ACM CCS 2018 that avoids all the required range proofs, while retaining provable security against malicious adversaries in the dishonest majority setting.
- Our experiments show that – for all levels of security – our signing protocol reduces the bandwidth consumption of best previously known secure protocols for factors varying between 4.4 and 9, while key generation is consistently two times less expensive.
- Furthermore compared to these same protocols, our signature generation is faster for 192-bits of security and beyond.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110174 (1).pdf`
- `downloads/12110174.pdf`
