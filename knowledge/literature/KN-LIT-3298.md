---
id: KN-LIT-3298
type: literature
title: "Cryptographic Analysis of the Bluetooth Secure Connection Protocol Suite"
authors:
  - "Marc Fischlin"
  - "Olga Sanina"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, pairing, protocol, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a cryptographic analysis of the Bluetooth Secure Connections Protocol Suite. Bluetooth supports several subprotocols, such as Numeric Comparison, Passkey Entry, and Just Works, in order to match the devices’ different input/output capabilities.

## Key claims (as reported)
- Previous analyses (e.g., Lindell, CT-RSA’09, or Troncoso and Hale, NDSS’21) often considered (and confirmed) the security of single subprotocols only.
- Recent practically verified attacks, however, such as the Method Confusion Attack (von Tschirschnitz et al., S&P 21), against Bluetooth’s authentication and key secrecy property often exploit the bad interplay of different subprotocols.
- Even worse, some of these attacks demonstrate that one cannot prove the Bluetooth protocol suite to be a secure authenticated key exchange protocol.
- We therefore aim at the best we can hope for and show that the protocol still matches the common key secrecy requirements of a key-exchange protocol if one assumes a trust-on-firstuse (TOFU) relationship.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900295 (1).pdf`
- `downloads/130900295.pdf`
