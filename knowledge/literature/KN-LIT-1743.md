---
id: KN-LIT-1743
type: literature
title: "Module Lattice Security (Part IV): Probabilistic Polynomial Quantum Attack on Module-LWE over 2-Power Cyclotomics"
authors:
  - "Ming-Xing Luo"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.17412"
  url: "https://arxiv.org/abs/2605.17412"
tags: [cryptanalysis, dlp, factoring, lattice, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a quantum attack on ML-KEM and related 2-power cyclotomic lattice schemes. Combining with Parts I-III, we provide an algorithm and verify the resulting approximation factor satisfies γ ≤ 21 < q/2 = 1665 for ML-KEM-1024, with a success probability ≥ 0.99.

## Key claims (as reported)
- We apply a tower decomposition of the Principal Ideal Problem (PIP) through the chain Q ⊂ Q(ζ8 ) ⊂ · · · ⊂ Q(ζ2k ) which yields a polynomial-time quantum algorithm costing O(n3 log2 n) gates, O(n2 log n) qubits, and poly(n) classical bit operations.
- We extend the analysis to Falcon, Hawk, and NTRU over 2-power cyclotomic rings.
- This means that ML-KEM, Falcon, Hawk, NTRU-HPS, and NTRU-HRSS with all standardized parameter sets are broken under quantum attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.17412v1.pdf`
