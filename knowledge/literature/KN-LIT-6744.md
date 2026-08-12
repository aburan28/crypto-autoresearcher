---
id: KN-LIT-6744
type: literature
title: "Solving the Hidden Number Problem for CSIDH and CSURF via Automated Coppersmith"
authors:
  - "Jonas Meers"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdsa, elliptic-curve, isogeny, lattice, pairing, pqc, protocol, quantum, side-channel, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define and analyze the Commutative Isogeny Hidden Number Problem which is the natural analogue of the Hidden Number Problem in the CSIDH and CSURF setting. In short, the task is as follows: Given two supersingular elliptic curves EA , EB and access to an oracle that outputs some of the most significant bits of the CDH of two curves, an adversary must compute the shared curve EAB = CDH(EA , EB ).

## Key claims (as reported)
- We show that we can recover EAB in polynomial time by using Coppersmith’s method as long as the oracle outputs 13 + ε ≈ 54% (CSIDH) and 24 31 + ε ≈ 76% (CSURF) of the most significant bits of the CDH, where 41 ε > 0 is an arbitrarily small constant.
- To this end, we give a purely combinatorial restatement of Coppersmith’s method, effectively concealing the intricate aspects of lattice theory and allowing for near-complete automation.
- By leveraging this approach, we attain recovery attacks with ε close to zero within a few minutes of computation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438104 (1).pdf`
- `downloads/14438104.pdf`
