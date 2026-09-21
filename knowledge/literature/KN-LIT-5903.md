---
id: KN-LIT-5903
type: literature
title: "Privacy-Preserving Authenticated Key Exchange in the Standard Model"
authors:
  - "You Lyu"
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
Privacy-Preserving Authenticated Key Exchange (PPAKE) provides protection both for the session keys and the identity information of the involved parties. In this paper, we introduce the concept of robustness into PPAKE.

## Key claims (as reported)
- Robustness enables each user to confirm whether itself is the target recipient of the first round message in the protocol.
- With the help of robustness, a PPAKE protocol can successfully avoid the heavy redundant communications and computations caused by the ambiguity of communicants in the existing PPAKE, especially in broadcast channels.
- We propose a generic construction of robust PPAKE from key encapsulation mechanism (KEM), digital signature (SIG), message authentication code (MAC), pseudo-random generator (PRG) and symmetric encryption (SE).
- By instantiating KEM, MAC, PRG from the DDH assumption and SIG from the CDH assumption, we obtain a specific robust PPAKE scheme in the standard model, which enjoys forward security for session keys, explicit authentication and forward privacy for user identities.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910269 (1).pdf`
- `downloads/137910269.pdf`
