---
id: KN-LIT-2510
type: literature
title: "Analysing the HPKE Standard"
authors:
  - "Joël Alwen"
  - "Bruno Blanchet"
  - "Eduard Hauck"
  - "Eike Kiltz"
  - "Benjamin Lipp"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Hybrid Public Key Encryption (HPKE) scheme is an emerging standard currently under consideration by the Crypto Forum Research Group (CFRG) of the IETF as a candidate for formal approval. Of the four modes of HPKE, we analyse the authenticated mode HPKEAuth in its single-shot encryption form as it contains what is, arguably, the most novel part of HPKE.

## Key claims (as reported)
- HPKEAuth ’s intended application domain is captured by a new primitive which we call Authenticated Public Key Encryption (APKE).
- We provide syntax and security definitions for APKE schemes, as well as for the related Authenticated Key Encapsulation Mechanisms (AKEMs).
- We prove security of the AKEM scheme DH-AKEM underlying HPKEAuth based on the Gap Diffie-Hellman assumption and provide general AKEM/DEM composition theorems with which to argue about HPKEAuth ’s security.
- To this end, we also formally analyse HPKEAuth ’s key schedule and key derivation functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960008 (1).pdf`
- `downloads/126960008.pdf`
