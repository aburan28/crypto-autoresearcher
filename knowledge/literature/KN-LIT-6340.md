---
id: KN-LIT-6340
type: literature
title: "Rounded Gaussians Fast and Secure Constant-Time Sampling for Lattice-Based Crypto"
authors:
  - "Andreas Hülsing"
  - "Tanja Lange"
  - "Kit Smeets"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, implementation, lattice, pqc, protocol, provable-security, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper suggests to use rounded Gaussians in place of discrete Gaussians in rejection-sampling-based lattice signature schemes like BLISS or Lyubashevsky’s signature scheme. We show that this distribution can efficiently be sampled from while additionally making it easy to sample in constant time, systematically avoiding recent timing-based side-channel attacks on lattice-based signatures.

## Key claims (as reported)
- We show the effectiveness of the new sampler by applying it to BLISS, prove analogues of the security proofs for BLISS, and present an implementation that runs in constant time.
- Our implementation needs no precomputed tables and is twice as fast as the variable-time CDT sampler posted by the BLISS authors with precomputed tables.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770212 (1).pdf`
- `downloads/10770212 (2).pdf`
- `downloads/10770212 (3).pdf`
- `downloads/10770212 (4).pdf`
- `downloads/10770212.pdf`
