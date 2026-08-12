---
id: KN-LIT-6262
type: literature
title: "Revisiting Post-Quantum Fiat-Shamir"
authors:
  - "Qipeng Liu"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Fiat-Shamir transformation is a useful approach to building non-interactive arguments (of knowledge) in the random oracle model. Unfortunately, existing proof techniques are incapable of proving the security of Fiat-Shamir in the quantum setting.

## Key claims (as reported)
- The problem stems from (1) the difficulty of quantum rewinding, and (2) the inability of current techniques to adaptively program random oracles in the quantum setting.
- In this work, we show how to overcome the limitations above in many settings.
- In particular, we give mild conditions under which Fiat-Shamir is secure in the quantum setting.
- As an application, we show that existing lattice signatures based on Fiat-Shamir are secure without any modifications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940207 (1).pdf`
- `downloads/116940207.pdf`
