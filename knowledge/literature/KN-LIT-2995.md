---
id: KN-LIT-2995
type: literature
title: "Compact Ring-LWE Cryptoprocessor Sujoy Sinha Roy1 , Frederik Vercauteren1 , Nele Mentens1"
authors:
  - "Donald Donglong Chen"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we propose an efficient and compact processor for a ring-LWE based encryption scheme. We present three optimizations for the Number Theoretic Transform (NTT) used for polynomial multiplication: we avoid preprocessing in the negative wrapped convolution by merging it with the main algorithm, we reduce the fixed computation cost of the twiddle factors and propose an advanced memory access scheme.

## Key claims (as reported)
- These optimization techniques reduce both the cycle and memory requirements.
- Finally, we also propose an optimization of the ring-LWE encryption system that reduces the number of NTT operations from five to four resulting in a 20% speed-up.
- We use these computational optimizations along with several architectural optimizations to design an instruction-set ring-LWE cryptoprocessor.
- For dimension 256, our processor performs encryption/decryption operations in 20/9 μs on a Virtex 6 FPGA and only requires 1349 LUTs, 860 FFs, 1 DSP-MULT and 2 BRAMs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310183 (1).pdf`
- `downloads/87310183 (2).pdf`
- `downloads/87310183 (3).pdf`
- `downloads/87310183.pdf`
