---
id: KN-LIT-2886
type: literature
title: "Chosen-Ciphertext Secure Dual-Receiver Encryption in the Standard Model Based on Post-Quantum Assumptions"
authors:
  - "Laurin Benz"
  - "Wasilij Beskorovajnov"
  - "Sarai Eilebrecht"
  - "Roland Gröll"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Dual-receiver encryption (DRE) is a special form of public key encryption (PKE) that allows a sender to encrypt a message for two recipients. Without further properties, the difference between DRE and PKE is only syntactical.

## Key claims (as reported)
- One such important property is soundness, which requires that no ciphertext can be constructed such that the recipients decrypt to different plaintexts.
- Many applications rely on this property in order to realize more complex protocols or primitives.
- In addition, many of these applications explicitly avoid the usage of the random oracle, which poses an additional requirement on a DRE construction.
- We show that all of the IND-CCA2 secure standard model DRE constructions based on post-quantum assumptions fall short of augmenting the constructions with soundness and describe attacks thereon.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602003 (1).pdf`
- `downloads/14602003.pdf`
