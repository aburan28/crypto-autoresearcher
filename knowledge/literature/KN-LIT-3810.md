---
id: KN-LIT-3810
type: literature
title: "Fast Practical Lattice Reduction through Iterated Compression [0000−0001−5846−2046]"
authors:
  - "Keegan Ryan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new lattice basis reduction algorithm with approximation guarantees analogous to the LLL algorithm and practical performance that far exceeds the current state of the art. We achieve these results by iteratively applying precision management techniques within a recursive algorithm structure and show the stability of this approach.

## Key claims (as reported)
- We analyze the asymptotic behavior of our algorithm, and show ω 1+ε that the heuristic running time is O(n (C + n) ) for lattices of dimension n, ω ∈ (2, 3] bounding the cost of size reduction, matrix multiplication, and QR factorization, and C bounding the log of the condition num ω 1+ε ber of the input basis B .
- This yields a running time of O n (p + n) for precision p = O(log ∥B∥max ) in common applications.
- Our algorithm is fully practical, and we have published our implementation.
- We experimentally validate our heuristic, give extensive benchmarks against numerous classes of cryptographic lattices, and show that our algorithm signi cantly outperforms existing implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850234 (1).pdf`
- `downloads/140850234.pdf`
