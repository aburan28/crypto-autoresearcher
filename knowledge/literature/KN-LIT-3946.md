---
id: KN-LIT-3946
type: literature
title: "FPGA-based Key Generator for the Niederreiter Cryptosystem using Binary Goppa Codes"
authors:
  - "Wen Wang"
  - "Jakub Szefer"
  - "Ruben Niederhagen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, dlp, factoring, implementation, isogeny, lattice, pqc, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a post-quantum secure, efficient, and tunable FPGA implementation of the key-generation algorithm for the Niederreiter cryptosystem using binary Goppa codes. Our key-generator implementation requires as few as 896,052 cycles to produce both public and private portions of a key, and can achieve an estimated frequency Fmax of over 240 MHz when synthesized for Stratix V FPGAs.

## Key claims (as reported)
- To the best of our knowledge, this work is the first hardware-based implementation that works with parameters equivalent to, or exceeding, the recommended 128-bit “post-quantum security” level.
- The key generator can produce a key pair for parameters m = 13, t = 119, and n = 6960 in only 3.7 ms when no systemization failure occurs, and in 3.5 · 3.7 ms on average.
- To achieve such performance, we implemented an optimized and parameterized Gaussian systemizer for matrix systemization, which works for any large-sized matrix over any binary field GF(2m ).
- Our work also presents an FPGA-based implementation of the Gao-Mateer additive FFT, which only takes about 1000 clock cycles to finish the evaluation of a degree-119 polynomial at 213 data points.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529219 (1).pdf`
- `downloads/10529219.pdf`
