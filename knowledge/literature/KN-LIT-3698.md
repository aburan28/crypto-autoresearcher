---
id: KN-LIT-3698
type: literature
title: "EpiGRAM: Practical Garbled RAM"
authors:
  - "David Heath"
  - "Vladimir Kolesnikov"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Garbled RAM (GRAM) is a powerful technique introduced by Lu and Ostrovsky that equips Garbled Circuit (GC) with a sublinear cost RAM without adding rounds of interaction. While multiple GRAM constructions are known, none are suitable for practice, due to costs that have high constants and poor scaling.

## Key claims (as reported)
- We present the first GRAM suitable for practice.
- For computational security parameter κ and for a size-n RAM that stores blocks of size w = Ω(log2 n) bits, our GRAM incurs amortized O(w · log2 n · κ) communication and computation per access.
- We evaluate the concrete cost of our GRAM; our approach outperforms trivial linear-scan-based RAM for as few as 512 128-bit elements.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760117 (1).pdf`
- `downloads/132760117.pdf`
