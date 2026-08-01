---
id: KN-LIT-5615
type: literature
title: "On Valiant’s Conjecture Impossibility of Incrementally Verifiable Computation from Random Oracles"
authors:
  - "Mathias Hall-Andersen⋆"
  - "Jesper Buus"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In his landmark paper at TCC 2008 Paul Valiant introduced the notion of “incrementally verifiable computation” which enables a prover to incrementally compute a succinct proof of correct execution of a (potentially) long running process. The paper later won the 2019 TCC test of time award.

## Key claims (as reported)
- The construction was proven secure in the random oracle model without any further computational assumptions.
- However, the overall proof was given using a non-standard version of the randomoracle methodology where sometimes the hash function is a random oracle and sometimes it has a short description as a circuit.
- Valiant clearly noted that this model is non-standard, but conjectured that the standard random oracle methodology would not suffice.
- This conjecture has been open for 14 years.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004170 (1).pdf`
- `downloads/14004170.pdf`
