---
id: KN-LIT-7237
type: literature
title: "Towards Topology-Hiding Computation from Oblivious Transfer"
authors:
  - "Marshall Ball"
  - "Alexander Bienstock"
  - "Lisa Kohl"
  - "Pierre Meyer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Topology-Hiding Computation (THC) enables parties to securely compute a function on an incomplete network without revealing the network topology. It is known that secure computation on a complete network can be based on oblivious transfer (OT), even if a majority of the participating parties are corrupt.

## Key claims (as reported)
- In contrast, THC in the dishonest majority setting is only known from assumptions that imply (additively) homomorphic encryption, such as Quadratic Residuosity, Decisional Diffie-Hellman, or Learning With Errors.
- In this work we move towards closing the gap between MPC and THC by presenting a protocol for THC on general graphs secure against all-but-one semi-honest corruptions from constant-round constant-overhead secure two-party computation.
- Our protocol is therefore the first to achieve THC on arbitrary networks without relying on assumptions with rich algebraic structure.
- As a technical tool, we introduce the notion of locally simulatable MPC, which we believe to be of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369053 (1).pdf`
- `downloads/14369053.pdf`
