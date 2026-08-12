---
id: KN-LIT-6338
type: literature
title: "Round-optimal Verifiable Oblivious Pseudorandom Functions from Ideal Lattices"
authors:
  - "Martin R. Albrecht"
  - "Alex Davidson"
  - "Amit Deo"
  - "Nigel P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, pqc, protocol, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Verifiable Oblivious Pseudorandom Functions (VOPRFs) are protocols that allow a client to learn verifiable pseudorandom function (PRF) evaluations on inputs of their choice. The PRF evaluations are computed by a server using their own secret key.

## Key claims (as reported)
- The security of the protocol prevents both the server from learning anything about the client’s input, and likewise the client from learning anything about the server’s key.
- VOPRFs have many applications including password-based authentication, secret-sharing, anonymous authentication and efficient private set intersection.
- In this work, we construct the first round-optimal (online) VOPRF protocol that retains security from well-known subexponential lattice hardness assumptions.
- Our protocol requires constructions of non-interactive zero-knowledge arguments of knowledge (NIZKAoK).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110128 (1).pdf`
- `downloads/127110128.pdf`
