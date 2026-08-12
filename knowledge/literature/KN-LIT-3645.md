---
id: KN-LIT-3645
type: literature
title: "Efficient Updatable Public-Key Encryption from Lattices"
authors:
  - "Calvin Abou Haidar"
  - "Alain Passelègue"
  - "Damien Stehlé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Updatable public key encryption has recently been introduced as a solution to achieve forward-security in the context of secure group messaging without hurting efficiency, but so far, no efficient latticebased instantiation of this primitive is known. In this work, we construct the first LWE-based UPKE scheme with polynomial modulus-to-noise rate, which is CPA-secure in the standard model.

## Key claims (as reported)
- At the core of our security analysis is a generalized reduction from the standard LWE problem to (a stronger version of) the Extended LWE problem.
- We further extend our construction to achieve stronger security notions by proposing two generic transforms.
- Our first transform allows to obtain CCA security in the random oracle model and adapts the Fujisaki-Okamoto transform to the UPKE setting.
- Our second transform allows to achieve security against malicious updates by adding a NIZK argument in the update mechanism.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438198 (1).pdf`
- `downloads/14438198.pdf`
