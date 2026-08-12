---
id: KN-LIT-6634
type: literature
title: "Signatures from Sequential-OR Proofs"
authors:
  - "Marc Fischlin"
  - "Patrick Harasser"
  - "Christian Janson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
OR-proofs enable a prover to show that it knows the witness for one of many statements, or that one out of many statements is true. OR-proofs are a remarkably versatile tool, used to strengthen security properties, design group and ring signature schemes, and achieve tight security.

## Key claims (as reported)
- The common technique to build OR-proofs is based on an approach introduced by Cramer, Damgård, and Schoenmakers (CRYPTO’94), where the prover splits the verifier’s challenge into random shares and computes proofs for each statement in parallel.
- In this work we study a different, less investigated OR-proof technique, highlighted by Abe, Ohkubo, and Suzuki (ASIACRYPT’02).
- The difference is that the prover now computes the individual proofs sequentially.
- We show that such sequential OR-proofs yield signature schemes which can be proved secure in the non-programmable random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105351 (1).pdf`
- `downloads/12105351.pdf`
