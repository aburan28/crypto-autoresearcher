---
id: KN-LIT-6611
type: literature
title: "SiBIR: Signer-Base Intrusion-Resilient Signatures"
authors:
  - "Gene Itkis"
  - "Leonid Reyzin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new notion of signer-base intrusion-resilient (SiBIR) signatures, which generalizes and improves upon both forwardsecure [?,?] and key-insulated [?] signature schemes. Specifically, as in the prior notions, time is divided into predefined time periods (e.g., days); each signature includes the number of the time period in which it was generated; while the public key remains the same, the secret keys evolve with time.

## Key claims (as reported)
- Also, as in key-insulated schemes, the user has two modules, signer and home base: the signer generates signatures on his1 own, and the base is needed only to help update the signer’s key from one period to the next.
- The main strength of intrusion-resilient schemes, as opposed to prior notions, is that they remain secure even after arbitrarily many compromises of both modules, as long as the compromises are not simultaneous.
- Moreover, even if the intruder does compromise both modules simultaneously, she will still be unable to generate any signatures for the previous time periods.
- We provide an efficient intrusion-resilient signature scheme, provably secure in the random oracle model based on the strong RSA assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420501 (1).pdf`
- `downloads/24420501 (2).pdf`
- `downloads/24420501.pdf`
