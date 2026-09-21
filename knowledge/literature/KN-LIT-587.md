---
id: KN-LIT-587
type: literature
title: "Adaptively Secure Distributed PRFs from LWE?"
authors:
  - "Benoît Libert"
  - "Damien Stehlé"
  - "Radu Titiu"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/927"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/927"
tags: [complexity-theory, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In distributed pseudorandom functions (DPRFs), a PRF secret key SK is secret shared among N servers so that each server can locally compute a partial evaluation of the PRF on some input X. A combiner that collects t partial evaluations can then reconstruct the evaluation F (SK, X) of the PRF under the initial secret key.

## Key claims (as reported)
- So far, all non-interactive constructions in the standard model are based on lattice assumptions.
- One caveat is that they are only known to be secure in the static corruption setting, where the adversary chooses the servers to corrupt at the very beginning of the game, before any evaluation query.
- In this work, we construct the first fully non-interactive adaptively secure DPRF in the standard model.
- Our construction is proved secure under the LWE assumption against adversaries that may adaptively decide which servers they want to corrupt.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-927 (1).pdf`
- `downloads/2018-927.pdf`
