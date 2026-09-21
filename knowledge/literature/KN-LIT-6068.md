---
id: KN-LIT-6068
type: literature
title: "Quantifying the Security Cost of Migrating Protocols to Practice"
authors:
  - "Christopher Patton"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a framework for relating the concrete security of a “reference” protocol (say, one appearing in an academic paper) to that of some derived, “real” protocol (say, appearing in a cryptographic standard). It is based on the indifferentiability framework of Maurer, Renner, and Holenstein (MRH), whose application has been exclusively focused upon non-interactive cryptographic primitives, e.g., hash functions and Feistel networks.

## Key claims (as reported)
- Our extension of MRH is supported by a clearly defined execution model and two composition lemmata, all formalized in a modern pseudocode language.
- Together, these allow for precise statements about game-based security properties of cryptographic objects (interactive or not) at various levels of abstraction.
- As a real-world application, we design and prove tight security bounds for a potential TLS 1.3 extension that integrates the SPAKE2 password-authenticated key-exchange into the handshake.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171182 (1).pdf`
- `downloads/12171182.pdf`
