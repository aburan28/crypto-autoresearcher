---
id: KN-LIT-4733
type: literature
title: "Limits of Constructive Security Proofs"
authors:
  - "Michael Backes"
  - "Dominique Unruh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The collision-resistance of hash functions is an important foundation of many cryptographic protocols. Formally, collisionresistance can only be expected if the hash function in fact constitutes a parametrized family of functions, since for a single function, the adversary could simply know a single hard-coded collision.

## Key claims (as reported)
- In practical applications, however, unkeyed hash functions are a common choice, creating a gap between the practical application and the formal proof, and, even more importantly, the concise mathematical definitions.
- A pragmatic way out of this dilemma was recently formalized by Rogaway: instead of requiring that no adversary exists that breaks the protocol (existential security), one requires that given an adversary that breaks the protocol, we can efficiently construct a collision of the hash function using an explicitly given reduction (constructive security).
- In this paper, we show the limits of this approach: We give a protocol that is existentially secure, but that provably cannot be proven secure using a constructive security proof.
- Consequently, constructive security—albeit constituting a useful improvement over the state of the art—is not comprehensive enough to encompass all protocols that can be dealt with using existential security proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500293 (1).pdf`
- `downloads/53500293 (2).pdf`
- `downloads/53500293 (3).pdf`
- `downloads/53500293.pdf`
