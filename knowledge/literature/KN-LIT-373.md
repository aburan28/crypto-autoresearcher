---
id: KN-LIT-373
type: literature
title: "Secure Identity-Based Encryption in the Quantum Random Oracle Model?"
authors:
  - "Mark Zhandry"
year: 2012
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2012/076"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2012/076"
tags: [hash, lattice, mov-fr, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give the first proof of security for an identity-based encryption scheme in the quantum random oracle model. This is the first proof of security for any scheme in this model that requires no additional assumptions.

## Key claims (as reported)
- Our techniques are quite general and we use them to obtain security proofs for two random oracle hierarchical identity-based encryption schemes and a random oracle signature scheme, all of which have previously resisted quantum security proofs, even using additional assumptions.
- We also explain how to remove the extra assumptions from prior quantum random oracle model proofs.
- We accomplish these results by developing new tools for arguing that quantum algorithms cannot distinguish between two oracle distributions.
- Using a particular class of oracle distributions, so called semi-constant distributions, we argue that the aforementioned cryptosystems are secure against quantum adversaries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170753 (1).pdf`
- `downloads/74170753 (2).pdf`
- `downloads/74170753 (3).pdf`
- `downloads/74170753.pdf`
