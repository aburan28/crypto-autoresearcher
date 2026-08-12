---
id: KN-LIT-264
type: literature
title: "On the Necessary and Sufficient Assumptions for UC Computation"
authors:
  - "Ivan Damgård"
  - "Jesper Buus Nielsen"
  - "Claudio Orlandi"
year: 2009
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2009/247"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2009/247"
tags: [mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the necessary and sufficient assumptions for universally composable (UC) computation, both in terms of setup and computational assumptions. We look at the common reference string model, the uniform random string model and the key-registration authority model (KRA), and provide new results for all of them.

## Key claims (as reported)
- Perhaps most interestingly we show that: – For even the minimal meaningful KRA, where we only assume that the secret key is a value which is hard to compute from the public key, one can UC securely compute any poly-time functionality if there exists a passive secure oblivious-transfer protocol for the stand-alone model.
- Since a KRA where the secret keys can be computed from the public keys is useless, and some setup assumption is needed for UC secure computation, this establishes the best we could hope for the KRA model: any non-trivial KRA is sufficient for UC computation. – We show that in the KRA model one-way functions are sufficient for UC commitment and UC zero-knowledge.
- These are the first examples of UC secure protocols for non-trivial tasks which do not assume the existence of public-key primitives.
- In particular, the protocols show that non-trivial UC computation is possible in Minicrypt.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59780108 (1).pdf`
- `downloads/59780108 (2).pdf`
- `downloads/59780108 (3).pdf`
- `downloads/59780108.pdf`
