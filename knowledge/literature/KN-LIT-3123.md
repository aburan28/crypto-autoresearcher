---
id: KN-LIT-3123
type: literature
title: "Constant-size Group Signatures from Lattices"
authors:
  - "San Ling"
  - "Khoa Nguyen"
  - "Huaxiong Wang"
  - "Yanhong Xu"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based group signature is an active research topic in recent years. Since the pioneering work by Gordon, Katz and Vaikuntanathan (Asiacrypt 2010), ten other schemes have been proposed, providing various improvements in terms of security, efficiency and functionality.

## Key claims (as reported)
- However, in all known constructions, one has to fix the number N of group users in the setup stage, and as a consequence, the signature sizes are dependent on N .
- In this work, we introduce the first constant-size group signature from lattices, which means that the size of signatures produced by the scheme is independent of N and only depends on the security parameter λ.
- More precisely, in our scheme, the sizes of signatures, public key and users’ see cret keys are all of order O(λ).
- The scheme supports dynamic enrollment of users and is proven secure in the random oracle model under the Ring Short Integer Solution (RSIS) and Ring Learning With Errors (RLWE) assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770286 (1).pdf`
- `downloads/10770286 (2).pdf`
- `downloads/10770286 (3).pdf`
- `downloads/10770286 (4).pdf`
- `downloads/10770286.pdf`
