---
id: KN-LIT-5048
type: literature
title: "MuSig-L: Lattice-Based Multi-Signature With Single-Round Online Phase"
authors:
  - "Cecilia Boschini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, pqc, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-signatures are protocols that allow a group of signers to jointly produce a single signature on the same message. In recent years, a number of practical multi-signature schemes have been proposed in the discrete-log setting, such as MuSig2 (CRYPTO’21) and DWMS (CRYPTO’21).

## Key claims (as reported)
- The main technical challenge in constructing a multi-signature scheme is to achieve a set of several desirable properties, such as (1) security in the plain public-key (PPK) model, (2) concurrent security, (3) low online round complexity, and (4) key aggregation.
- However, previous lattice-based, post-quantum counterparts to Schnorr multi-signatures fail to satisfy these properties.
- In this paper, we introduce MuSig-L, a lattice-based multi-signature scheme simultaneously achieving these design goals for the first time.
- Unlike the recent, round-efficient proposal of Damgård et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070323 (1).pdf`
- `downloads/135070323.pdf`
