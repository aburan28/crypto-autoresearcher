---
id: KN-LIT-3706
type: literature
title: "Error Correction and Ciphertext Quantization in Lattice Cryptography"
authors:
  - "Daniele Micciancio"
  - "Mark Schultz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mov-fr, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recent work in the design of rate 1 − o(1) lattice-based cryptosystems have used two distinct design paradigms, namely replacing the noise-tolerant encoding m 7→ (q/2)m present in many lattice-based cryptosystems with a more efficient encoding, and post-processing traditional latticebased ciphertexts with a lossy compression algorithm, using a technique very similar to the technique of “vector quantization” within coding theory. We introduce a framework for the design of lattice-based encryption that captures both of these paradigms, and prove information-theoretic rate bounds within this framework.

## Key claims (as reported)
- These bounds separate the settings of trivial and non-trivial quantization, and show the impossibility of rate 1 − o(1) encryption using both trivial quantization and polynomial modulus.
- They furthermore put strong limits on the rate of constructions that utilize lattices built by tensoring a lattice of small dimension with Zk , which is ubiquitous in the literature.
- We additionally introduce a new cryptosystem, that matches the rate of the highest-rate currently known scheme, while encoding messages with a “gadget”, which may be useful for constructions of Fully Homomorphic Encryption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850272 (1).pdf`
- `downloads/140850272.pdf`
