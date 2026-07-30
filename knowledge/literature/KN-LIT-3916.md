---
id: KN-LIT-3916
type: literature
title: "Flush, Gauss, and Reload – A Cache Attack on the BLISS Lattice-Based Signature Scheme"
authors:
  - "Leon Groot Bruinderink"
  - "Andreas Hülsing"
  - "Tanja Lange"
  - "Yuval Yarom"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, lattice, pqc, protocol, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first side-channel attack on a lattice-based signature scheme, using the Flush+Reload cache-attack. The attack is targeted at the discrete Gaussian sampler, an important step in the Bimodal Lattice Signature Schemes (BLISS).

## Key claims (as reported)
- After observing only 450 signatures with a perfect side-channel, an attacker is able to extract the secret BLISS-key in less than 2 minutes, with a success probability of 0.96.
- Similar results are achieved in a proof-of-concept implementation using the Flush+Reload technique with less than 3500 signatures.
- We show how to attack sampling from a discrete Gaussian using CDT or Bernoulli sampling by showing potential information leakage via cache memory.
- For both sampling methods, a strategy is given to use this additional information, finalize the attack and extract the secret key.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130193 (1).pdf`
- `downloads/98130193.pdf`
