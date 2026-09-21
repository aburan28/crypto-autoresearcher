---
id: KN-LIT-5735
type: literature
title: "Password-Authenticated"
authors:
  - "Sabrina Kunzweiler"
  - "Doreen Riepel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, elliptic-curve, endomorphism, isogeny, number-theory, pqc, protocol, provable-security, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present two provably secure password-authenticated key exchange (PAKE) protocols based on a commutative group action. To date the most important instantiation of isogeny-based group actions is given by CSIDH.

## Key claims (as reported)
- To model the properties more accurately, we extend the framework of cryptographic group actions (Alamati et al., ASIACRYPT 2020) by the ability of computing the quadratic twist of an elliptic curve.
- This property is always present in the CSIDH setting and turns out to be crucial in the security analysis of our PAKE protocols.
- Despite the resemblance, the translation of Diffie-Hellman based PAKE protocols to group actions either does not work with known techniques or is insecure (“How not to create an isogeny-based PAKE”, Azarderakhsh et al., ACNS 2020).
- We overcome the difficulties mentioned in previous work by using a “bit-by-bit” approach, where each password bit is considered separately.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070388 (1).pdf`
- `downloads/135070388.pdf`
