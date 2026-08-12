---
id: KN-LIT-4782
type: literature
title: "Lossy Algebraic Filters With Short Tags"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lossy algebraic filters (LAFs) are function families where each function is parametrized by a tag, which determines if the function is injective or lossy. While initially introduced by Hofheinz (Eurocrypt 2013) as a technical tool to build encryption schemes with key-dependent message chosen-ciphertext (KDM-CCA) security, they also find applications in the design of robustly reusable fuzzy extractors.

## Key claims (as reported)
- So far, the only known LAF family requires tags comprised of Θ(n2 ) group elements for functions with input space Zn p , where p is the group order.
- In this paper, we describe a new LAF family where the tag size is only linear in n and prove it secure under simple assumptions in asymmetric bilinear groups.
- Our construction can be used as a drop-in replacement in all applications of the initial LAF system.
- In particular, it can shorten the ciphertexts of Hofheinz’s KDM-CCA-secure public-key encryption scheme by 19 group elements.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420156 (1).pdf`
- `downloads/114420156.pdf`
