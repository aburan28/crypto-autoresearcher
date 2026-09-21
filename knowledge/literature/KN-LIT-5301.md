---
id: KN-LIT-5301
type: literature
title: "On Basing Search SIVP on NP-Hardness"
authors:
  - "Tianren Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The possibility of basing cryptography on the minimal assumption NP * BPP is at the very heart of complexity-theoretic cryptography. The closest we have gotten so far is lattice-based cryptography whose average-case security is based on the worst-case hardness of approximate shortest vector problems on integer lattices.

## Key claims (as reported)
- The state-of-the-art is the construction of a one-way function (and collision-resistant hash function) based on the hardness of the Õ(n)-approximate shortest independent vector problem SIVPÕ(n) .
- Although SIVP is NP-hard in its exact version, Guruswami et al (CCC 2004) showed that gapSIVP√n/ log n is in NP ∩ coAM and thus unlikely to be NP-hard.
- Indeed, any language that can be reduced to gapSIVPÕ(√n) (under general probabilistic polynomial-time adaptive reductions) is in AM ∩ coAM by the results of Peikert and Vaikuntanathan (CRYPTO 2008) and Mahmoody and Xiao (CCC 2010).
- However, none of these results apply to reductions to search problems, still leaving open a ray of hope: can NP be reduced to solving search SIVP with approximation factor Õ(n)?

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239203 (1).pdf`
- `downloads/11239203.pdf`
