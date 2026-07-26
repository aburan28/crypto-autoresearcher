---
id: KN-LIT-5424
type: literature
title: "On the Amortized Complexity of Zero-knowledge Protocols"
authors:
  - "Ronald Cramer"
  - "Ivan Damgård"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, fhe, mpc, pairing, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a general technique that allows improving the complexity of zero-knowledge protocols for a large class of problems where previously the best known solution was a simple cut-and-choose style protocol, i.e., where the size of a proof for problem instance x and error probability 2−n was O(|x|n) bits. By using our technique to prove n instances simultaneously, we can bring down the proof size per instance to O(|x| + n) bits for the same error probability while using no computational assumptions.

## Key claims (as reported)
- Examples where our technique applies include proofs for quadratic residuosity, proofs of subgroup membership and knowledge of discrete logarithms in groups of unknown order, and proofs of plaintext knowledge for various types of homomorphic encryptions schemes.
- The generality of our method stems from a somewhat surprising application of black-box secret sharing schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770175 (1).pdf`
- `downloads/56770175 (2).pdf`
- `downloads/56770175 (3).pdf`
- `downloads/56770175.pdf`
