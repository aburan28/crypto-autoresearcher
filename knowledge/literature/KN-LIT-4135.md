---
id: KN-LIT-4135
type: literature
title: "Group Encryption: Non-Interactive Realization in the Standard Model"
authors:
  - "Julien Cathalo ⋆"
  - "Benoı̂t Libert ⋆⋆"
  - "Moti Yung"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Group encryption (GE) schemes, introduced at Asiacrypt’07, are an encryption analogue of group signatures with a number of interesting applications. They allow a sender to encrypt a message (in the CCA2 security sense) for some member of a PKI group concealing that member’s identity (in a CCA2 security sense, as well); the sender is able to convince a verifier that, among other things, the ciphertext is valid and some anonymous certified group member will be able to decrypt the message.

## Key claims (as reported)
- As in group signatures, an opening authority has the power of pinning down the receiver’s identity.
- The initial GE construction uses interactive proofs as part of the design (which can be made non-interactive using the random oracle model) and the design of a fully non-interactive group encryption system is still an open problem.
- In this paper, we give the first GE scheme, which is a pure encryption scheme in the standard model, i.e., a scheme where the ciphertext is a single message and proofs are non-interactive (and do not employ the random oracle heuristic).
- As a building block, we use a new public key certification scheme which incurs the smallest amount of interaction, as well.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120171 (1).pdf`
- `downloads/59120171 (2).pdf`
- `downloads/59120171 (3).pdf`
- `downloads/59120171.pdf`
