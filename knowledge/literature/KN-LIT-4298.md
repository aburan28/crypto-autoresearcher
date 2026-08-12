---
id: KN-LIT-4298
type: literature
title: "How to Record Quantum Queries, and Applications to Quantum Indifferentiability"
authors:
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The quantum random oracle model (QROM) has become the standard model in which to prove the post-quantum security of random-oracle-based constructions. Unfortunately, none of the known proof techniques allow the reduction to record information about the adversary’s queries, a crucial feature of many classical ROM proofs, including all proofs of indifferentiability for hash function domain extension.

## Key claims (as reported)
- In this work, we give a new QROM proof technique that overcomes this “recording barrier”.
- We do so by giving a new “compressed oracle” which allows for efficient on-the-fly simulation of random oracles, roughly analogous to the usual classical simulation.
- We then use this new technique to give the first proof of quantum indifferentiability for the MerkleDamgård domain extender for hash functions.
- We also give a proof of security for the Fujisaki-Okamoto transformation; previous proofs required modifying the scheme to include an additional hash term.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940107 (1).pdf`
- `downloads/116940107.pdf`
