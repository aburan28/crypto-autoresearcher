---
id: KN-LIT-6290
type: literature
title: "RIV for Robust Authenticated Encryption Farzaneh Abed1 , Christian Forler2"
authors:
  - "Eik List"
  - "Stefan Lucks"
  - "Jakob Wenzel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Typical AE schemes are supposed to be secure when used as specified. However, they can – and often do – fail miserably when used improperly.

## Key claims (as reported)
- As a partial remedy, Rogaway and Shrimpton proposed (nonce-)misuse-resistant AE (MRAE) and the first MRAE scheme SIV (“Synthetic Initialization Vector”).
- This paper proposes RIV (“Robust Initialization Vector”), which extends the generic SIV construction by an additional call to the internal PRF.
- RIV inherits the full security assurance from SIV, but unlike SIV and other MRAE schemes, RIV is also provably secure when releasing unverified plaintexts.
- This follows a recent line of research on “Robust Authenticated Encryption”, similar to the CAESAR candidate AEZ.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830021 (1).pdf`
- `downloads/97830021.pdf`
