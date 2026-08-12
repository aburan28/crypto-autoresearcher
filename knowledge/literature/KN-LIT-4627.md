---
id: KN-LIT-4627
type: literature
title: "Large Message Homomorphic Secret Sharing from DCR and Applications"
authors:
  - "Lawrence Roy"
  - "Jaspal Singh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, hash, lattice, mov-fr, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first homomorphic secret sharing (HSS) construction that simultaneously (1) has negligible correctness error, (2) supports integers from an exponentially large range, and (3) relies on an assumption not known to imply FHE — specifically, the Decisional Composite Residuosity (DCR) assumption. This resolves an open question posed by Boyle, Gilboa, and Ishai (Crypto 2016).

## Key claims (as reported)
- Homomorphic secret sharing is analogous to fully-homomorphic encryption, except the ciphertexts are shared across two non-colluding evaluators.
- Previous constructions of HSS either had non-negligible correctness error and polynomialsize plaintext space or were based on the stronger LWE assumption.
- We also present two applications of our technique: a two server ORAM with constant bandwidth overhead, and a rate-1 trapdoor hash function with negligible error rate.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826388 (1).pdf`
- `downloads/12826388.pdf`
