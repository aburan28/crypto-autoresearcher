---
id: KN-LIT-5855
type: literature
title: "Practical Product Proofs for Lattice Commitments?"
authors:
  - "Thomas Attema"
  - "Vadim Lyubashevsky"
  - "Gregor Seiler"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, hash, lattice, mov-fr, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a practical lattice-based zero-knowledge argument for proving multiplicative relations between committed values. The underlying commitment scheme that we use is the currently most efficient one of Baum et al.

## Key claims (as reported)
- (SCN 2018), and the size of our multiplicative proof (9KB) is only slightly larger than the 7KB required for just proving knowledge of the committed values.
- We additionally expand on the work of Lyubashevsky and Seiler (Eurocrypt 2018) by showing that the abovementioned result can also apply when working over rings Zq [X]/(X d + 1) where X d + 1 splits into low-degree factors, which is a desirable property for many applications (e.g. range proofs, multiplications over Zq ) that take advantage of packing multiple integers into the NTT coefficients of the committed polynomial.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171294 (1).pdf`
- `downloads/12171294.pdf`
