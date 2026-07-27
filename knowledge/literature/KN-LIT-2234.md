---
id: KN-LIT-2234
type: literature
title: "A Simple Threshold Authenticated Key Exchange from Short Secrets"
authors:
  - "Michel Abdalla"
  - "Olivier Chevassut"
  - "Pierre-Alain Fouque"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper brings the password-based authenticated key exchange (PAKE) problem closer to practice. It takes into account the presence of firewalls when clients communicate with authentication servers.

## Key claims (as reported)
- An authentication server can indeed be seen as two distinct entities, namely a gateway (which is the direct interlocutor of the client) and a back-end server (which is the only one able to check the identity of the client).
- The goal in this setting is to achieve both transparency and security for the client.
- And to achieve these goals, the most appropriate choices seem to be to keep the client’s password private —even from the back-end server— and to use threshold-based cryptography.
- In this paper, we present the Threshold Password-based Authenticated Key Exchange (GTPAKE) system: GTPAKE uses a pair of public/private keys and, unlike traditional threshold-based constructions, shares only the private key among the servers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/566 (1).pdf`
- `downloads/566 (2).pdf`
- `downloads/566 (3).pdf`
- `downloads/566.pdf`
