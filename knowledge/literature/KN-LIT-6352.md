---
id: KN-LIT-6352
type: literature
title: "Safely Exporting Keys from Secure Channels: On the Security of EAP-TLS and TLS Key Exporters"
authors:
  - "Christina Brzuska"
  - "Håkon Jacobsen"
  - "Douglas Stebila"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We investigate how to safely export additional cryptographic keys from secure channel protocols, modelled with the authenticated and confidential channel establishment (ACCE) security notion. For example, the EAP-TLS protocol uses the Transport Layer Security (TLS) handshake to output an additional shared secret which can be used for purposes outside of TLS, and the RFC 5705 standard specifies a general mechanism for exporting keying material from TLS.

## Key claims (as reported)
- We show that, for a class of ACCE protocols we call “TLS-like” protocols, the EAP-TLS transformation can be used to export an additional key, and that the result is a secure AKE protocol in the Bellare–Rogaway model.
- Interestingly, we are able to carry out the proof without looking at the specifics of the TLS protocol itself (beyond the notion that it is “TLS-like”), but rather are able to use the ACCE property in a semi black-box way.
- To facilitate our modular proof, we develop a novel technique, notably an encryption-based key checking mechanism that is used by the security reduction.
- Our results imply that EAP-TLS using secure TLS 1.2 ciphersuites is a secure authenticated key exchange protocol.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650180 (1).pdf`
- `downloads/96650180.pdf`
