---
id: KN-LIT-7421
type: literature
title: "Updatable and Universal Common Reference Strings with Applications to zk-SNARKs"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
By design, existing (pre-processing) zk-SNARKs embed a secret trapdoor in a relation-dependent common reference strings (CRS). The trapdoor is exploited by a (hypothetical) simulator to prove the scheme is zero knowledge, and the secret-dependent structure facilitates a linear-size CRS and linear-time prover computation.

## Key claims (as reported)
- If known by a real party, however, the trapdoor can be used to subvert the security of the system.
- The structured CRS that makes zk-SNARKs practical also makes deploying zk-SNARKS problematic, as it is difficult to argue why the trapdoor would not be available to the entity responsible for generating the CRS.
- Moreover, for pre-processing zk-SNARKs a new trusted CRS needs to be computed every time the relation is changed.
- In this paper, we address both issues by proposing a model where a number of users can update a universal CRS.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993314 (1).pdf`
- `downloads/10993314.pdf`
