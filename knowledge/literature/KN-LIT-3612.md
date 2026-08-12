---
id: KN-LIT-3612
type: literature
title: "Efficient Pseudorandom"
authors:
  - "Lisa Kohl"
  - "Peter Scholl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, lattice, mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure multiparty computation can often utilize a trusted source of correlated randomness to achieve better efficiency. A recent line of work, initiated by Boyle et al.

## Key claims (as reported)
- (CCS 2018, Crypto 2019), showed how useful forms of correlated randomness can be generated using a cheap, one-time interaction, followed by only “silent” local computation.
- This is achieved via a pseudorandom correlation generator (PCG), a deterministic function that stretches short correlated seeds into long instances of a target correlation.
- Previous works constructed concretely efficient PCGs for simple but useful correlations, including random oblivious transfer and vector-OLE, together with efficient protocols to distribute the PCG seed generation.
- Most of these constructions were based on variants of the Learning Parity with Noise (LPN) assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171401 (1).pdf`
- `downloads/12171401.pdf`
