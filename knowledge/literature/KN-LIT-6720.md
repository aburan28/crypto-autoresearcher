---
id: KN-LIT-6720
type: literature
title: "SNARGs and PPAD Hardness from the Decisional Diffie-Hellman Assumption"
authors:
  - "Yael Tauman Kalai"
  - "Alex Lombardi"
  - "Vinod Vaikuntanathan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct succinct non-interactive arguments (SNARGs) for bounded-depth computations assuming that the decisional DiffieHellman (DDH) problem is sub-exponentially hard. This is the first construction of such SNARGs from a Diffie-Hellman assumption.

## Key claims (as reported)
- Our SNARG is also unambiguous: for every (true) statement x, it is computationally hard to find any accepting proof for x other than the proof produced by the prescribed prover strategy.
- We obtain our result by showing how to instantiate the Fiat-Shamir heuristic, under DDH, for a variant of the Goldwasser-Kalai-Rothblum (GKR) interactive proof system.
- Our new technical contributions are (1) giving a T C 0 circuit family for finding roots of cubic polynomials over a special family of characteristic-2 fields (Healy-Viola, STACS 2006) and (2) constructing a variant of the GKR protocol whose invocations of the sumcheck protocol (Lund-Fortnow-Karloff-Nisan, STOC 1990) only involve degree 3 polynomials over said fields.
- Along the way, since we can instantiate the Fiat-Shamir heuristic for certain variants of the sumcheck protocol, we also show the existence of (sub-exponentially) hard problems in the complexity class PPAD, assuming the sub-exponential hardness of DDH.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004112 (1).pdf`
- `downloads/14004112.pdf`
