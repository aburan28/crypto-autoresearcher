---
id: KN-LIT-6332
type: literature
title: "Round-Optimal Oblivious Transfer and MPC from Computational CSIDH"
authors:
  - "Saikrishna Badrinarayanan"
  - "Daniel Masny"
  - "Pratyay Mukherjee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, isogeny, lattice, mpc, pqc, provable-security, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the first round-optimal and plausibly quantumsafe oblivious transfer (OT) and multi-party computation (MPC) protocols from the computational CSIDH assumption – the weakest and most widely studied assumption in the CSIDH family of isogeny-based assumptions. We obtain the following results: – The first round-optimal maliciously secure OT and MPC protocols in the plain model that achieve (black-box) simulation-based security while relying on the computational CSIDH assumption. – The first round-optimal maliciously secure OT and MPC protocols that achieves Universal Composability (UC) security in the presence of a trusted setup (common reference string plus random oracle) while relying on the computational CSIDH assumption.

## Key claims (as reported)
- Prior plausibly quantum-safe isogeny-based OT protocols (with/without setup assumptions) are either not round-optimal, or rely on potentially stronger assumptions.
- We also build a 3-round maliciously-secure OT extension protocol where each base OT protocol requires only 4 isogeny computations.
- In comparison, the most efficient isogeny-based OT extension protocol till date due to Lai et al.
- [Eurocrypt 2021] requires 12 isogeny computations and 4 rounds of communication, while relying on the same assumption as our construction, namely the reciprocal CSIDH assumption.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940032 (1).pdf`
- `downloads/13940032.pdf`
