---
id: KN-LIT-4945
type: literature
title: "Modular Hardware Architecture for Somewhat"
authors:
  - "Homomorphic Function Evaluation"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a hardware architecture for all building blocks required in polynomial ring based fully homomorphic schemes and use it to instantiate the somewhat homomorphic encryption scheme YASHE. Our implementation is the first FPGA implementation that is designed for evaluating functions on homomorphically encrypted data (up to a certain multiplicative depth) and we illustrate this capability by evaluating the SIMON-64/128 block cipher in the encrypted domain.

## Key claims (as reported)
- Our implementation provides a fast polynomial operations unit using CRT and NTT for multiplication combined with an optimized memory access scheme; a fast Barrett like polynomial reduction method; an efficient divide and round unit required in the multiplication of ciphertexts and an efficient CRT unit.
- These building blocks are integrated in an instruction-set coprocessor to execute YASHE, which can be controlled by a computer for evaluating arbitrary functions (up to the multiplicative depth 44 and 128-bit security level).
- Our architecture was compiled for a single Virtex7 XC7V1140T FPGA, where it consumes 23 % of registers, 50 % of LUTs, 53 % of DSP slices, and 38 % of BlockRAM memory.
- The implementation evaluates SIMON-64/128 in approximately 157.7 s (at 143 MHz) and it processes 2048 ciphertexts at once giving a relative time of only 77 ms per block.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930161 (1).pdf`
- `downloads/92930161.pdf`
