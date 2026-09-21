---
id: KN-LIT-4865
type: literature
title: "Master-Key KDM-Secure IBE from Pairings"
authors:
  - "Sanjam Garg"
  - "Romain Gay"
  - "Mohammad Hajiabadi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Identity-based encryption (IBE) is a generalization of publickey encryption (PKE) by allowing encryptions to be made to user identities. In this work, we seek to obtain IBE schemes that achieve keydependent-message (KDM) security with respect to messages that depend on the master secret key.

## Key claims (as reported)
- Previous KDM-secure schemes only achieved KDM security in simpler settings, in which messages may only depend on user secret keys.
- An important motivation behind studying master-KDM security is the application of this notion in obtaining generic constructions of KDMCCA secure PKE, a primitive notoriously difficult to realize.
- We give the first IBE that achieves master-KDM security from standard assumptions in pairing groups.
- Our construction is modular and combines techniques from KDM-secure PKE based from hash-proof systems, together with IBE that admits a tight security proof in the multichallenge setting, which happens to be unexpectedly relevant in the context of KDM security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110219 (1).pdf`
- `downloads/12110219.pdf`
