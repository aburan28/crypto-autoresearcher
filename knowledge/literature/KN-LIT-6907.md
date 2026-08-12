---
id: KN-LIT-6907
type: literature
title: "SWIFFT: A Modest Proposal for FFT Hashing?"
authors:
  - "Vadim Lyubashevsky"
  - "Daniele Micciancio"
  - "Chris Peikert"
  - "Alon Rosen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, implementation, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose SWIFFT, a collection of compression functions that are highly parallelizable and admit very efficient implementations on modern microprocessors. The main technique underlying our functions is a novel use of the Fast Fourier Transform (FFT) to achieve “diffusion,” together with a linear combination to achieve compression and “confusion.” We provide a detailed security analysis of concrete instantiations, and give a high-performance software implementation that exploits the inherent parallelism of the FFT algorithm.

## Key claims (as reported)
- The throughput of our implementation is competitive with that of SHA-256, with additional parallelism yet to be exploited.
- Our functions are set apart from prior proposals (having comparable efficiency) by a supporting asymptotic security proof : it can be formally proved that finding a collision in a randomly-chosen function from the family (with noticeable probability) is at least as hard as finding short vectors in cyclic/ideal lattices in the worst case.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860052 (1).pdf`
- `downloads/50860052 (2).pdf`
- `downloads/50860052 (3).pdf`
- `downloads/50860052.pdf`
