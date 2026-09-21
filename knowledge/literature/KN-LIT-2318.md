---
id: KN-LIT-2318
type: literature
title: "Acyclicity Programming for Sigma-Protocols"
authors:
  - "Masayuki Abe"
  - "Miguel Ambrona"
  - "Andrej Bogdanov"
  - "Miyako Ohkubo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cramer, Damgård, and Schoenmakers (CDS) built a proof system to demonstrate the possession of subsets of witnesses for a given collection of statements that belong to a prescribed access structure P by composing so-called sigma-protocols for each atomic statement. Their verifier complexity is linear in the size of the monotone span program representation of P.

## Key claims (as reported)
- We propose an alternative method for combining sigma-protocols into a single non-interactive system for a compound statement in the random oracle model.
- In contrast to CDS, our verifier complexity is linear in the size of the acyclicity program representation of P, a complete model of monotone computation introduced in this work.
- We show that the acyclicity program size of a predicate is polynomially equivalent to the branching-program size of its monotone dual and hence polynomially incomparable to its monotone span program size.
- We additionally present an extension of our proof system, with verifier complexity linear in the monotone circuit size of P, in the common reference string model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130420157 (1).pdf`
- `downloads/130420157.pdf`
