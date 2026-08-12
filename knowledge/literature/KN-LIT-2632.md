---
id: KN-LIT-2632
type: literature
title: "Authenticated Key Exchange and Signatures with Tight Security in the Standard Model"
authors:
  - "Shuai Han"
  - "Tibor Jager"
  - "Eike Kiltz"
  - "Shengli Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first authenticated key exchange protocols that achieve tight security in the standard model. Previous works either relied on techniques that seem to inherently require a random oracle, or achieved only “Multi-Bit-Guess” security, which is not known to compose tightly, for instance, to build a secure channel.

## Key claims (as reported)
- Our constructions are generic, based on digital signatures and key encapsulation mechanisms (KEMs).
- The main technical challenges we resolve is to determine suitable KEM security notions which on the one hand are strong enough to yield tight security, but at the same time weak enough to be efficiently instantiable in the standard model, based on standard techniques such as universal hash proof systems.
- Digital signature schemes with tight multi-user security in presence of adaptive corruptions are a central building block, which is used in all known constructions of tightly-secure AKE with full forward security.
- We identify a subtle gap in the security proof of the only previously known efficient standard model scheme by Bader et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826398 (1).pdf`
- `downloads/12826398.pdf`
