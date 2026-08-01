---
id: KN-LIT-4563
type: literature
title: "JIMU: Faster LEGO-based Secure Computation using Additive Homomorphic Hashes"
authors:
  - "Ruiyu Zhu"
  - "Yan Huang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
LEGO-style cut-and-choose is known for its asymptotic efficiency in realizing actively-secure computations. The dominant cost of LEGO protocols is due to wire-soldering — the key technique enabling to put independently generated garbled gates together in a bucket to realize a logical gate.

## Key claims (as reported)
- Existing wire-soldering constructions rely on homomorphic commitments and their security requires the majority of the garbled gates in every bucket to be correct.
- In this paper, we propose an efficient construction of LEGO protocols that does not use homomorphic commitments but is able to guarantee security as long as at least one of the garbled gate in each bucket is correct.
- Additionally, the faulty gate detection rate in our protocol doubles that of the state-of-the-art LEGO constructions.
- With moderate additional cost, our approach can even detect faulty gates with probability 1, which enables us to run cut- and-choose on larger circuit gadgets rather than individual AND gates.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240264 (1).pdf`
- `downloads/106240264.pdf`
