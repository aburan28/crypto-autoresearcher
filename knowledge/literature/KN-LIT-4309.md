---
id: KN-LIT-4309
type: literature
title: "How to Thwart Birthday Attacks against MACs via Small Randomness"
authors:
  - "Kazuhiko Minematsu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of randomized message authentication code, MAC for short, is typically depending on the uniqueness of random initial vectors (IVs). Thus its security bound usually contains O(q 2 /2n ), when random IV is n bits and q is the number of MACed messages.

## Key claims (as reported)
- In this paper, we present how to break this birthday barrier without increasing the randomness.
- Our proposal is almost as efficient as the well-known Carter-Wegman MAC, uses n-bit random IVs, and provides the security bound roughly O(q 3 /22n ).
- We also provide blockcipher-based instantiations of our proposal.
- They are almost as efficient as CBC-MAC and the security is solely based on the pseudorandomness of the blockcipher.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470235 (1).pdf`
- `downloads/61470235 (2).pdf`
- `downloads/61470235 (3).pdf`
- `downloads/61470235.pdf`
