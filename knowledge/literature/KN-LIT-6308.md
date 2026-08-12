---
id: KN-LIT-6308
type: literature
title: "Rotational Cryptanalysis of ARX Revisited Dmitry Khovratovich1 , Ivica Nikolić2 , Josef Pieprzyk3"
authors:
  - "Przemyslaw Sokolowski"
  - "Ron Steinfeld"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Rotational cryptanalysis is a probabilistic attack applicable to word oriented designs that use (almost) rotation-invariant constants. It is believed that the success probability of rotational cryptanalysis against ciphers and functions based on modular additions, rotations and XORs, can be computed only by counting the number of additions.

## Key claims (as reported)
- We show that this simple formula is incorrect due to the invalid Markov cipher assumption used for computing the probability.
- More precisely, we show that chained modular additions used in ARX ciphers do not form a Markov chain with regards to rotational analysis, thus the rotational probability cannot be computed as a simple product of rotational probabilities of individual modular additions.
- We provide a precise value of the probability of such chains and give a new algorithm for computing the rotational probability of ARX ciphers.
- We use the algorithm to correct the rotational attacks on BLAKE2 and to provide valid rotational attacks against the simplified version of Skein.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400125 (1).pdf`
- `downloads/85400125.pdf`
