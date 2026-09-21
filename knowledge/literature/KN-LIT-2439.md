---
id: KN-LIT-2439
type: literature
title: "Amortized Functional Bootstrapping in less than 7ms, with Õ(1) polynomial multiplications"
authors:
  - "Zeyu Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Amortized bootstrapping offers a way to refresh multiple ciphertexts of a fully homomorphic encryption scheme in parallel more efficiently than refreshing a single ciphertext at a time. Micciancio and Sorrell (ICALP 2018) first proposed the technique to bootstrap n LWE ci1 phertexts simultaneously, reducing the total cost from Õ(n2 ) to Õ(3ε n1+ ε ) for arbitrary ε > 0.

## Key claims (as reported)
- Several recent works have further improved the asymptotic cost.
- Despite these amazing progresses in theoretical efficiency, none of them demonstrates the practicality of batched LWE ciphertext bootstrapping.
- Moreover, most of these works only support limited functional bootstrapping, i.e. only supporting the evaluation of some specific type of function when performing bootstrapping.
- In this work, we propose a construction that is not only asymptotically efficient (requiring only Õ(n) polynomial multiplications for bootstrapping of n LWE ciphertexts) but also concretely efficient.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438086 (1).pdf`
- `downloads/14438086.pdf`
