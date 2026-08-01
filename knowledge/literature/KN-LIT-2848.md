---
id: KN-LIT-2848
type: literature
title: "CCA Updatable Encryption Against Malicious Re-Encryption Attacks"
authors:
  - "Long Chen"
  - "Yanan Li"
  - "Qiang Tang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Updatable encryption (UE) is an attractive primitive, which allows the secret key of the outsourced encrypted data to be updated to a fresh one periodically. Several elegant works exist studying various security properties.

## Key claims (as reported)
- We notice several major issues in existing security models of (ciphertext dependent) updatable encryption, in particular, integrity and CCA security.
- The adversary in the models is only allowed to request the server to re-encrypt honestly generated ciphertext, while in practice, an attacker could try to inject arbitrary ciphertexts into the server as she wishes.
- Those malformed ciphertext could be updated and leveraged by the adversary and cause serious security issues.
- In this paper, we fill the gap and strengthen the security definitions in multiple aspects: most importantly our integrity and CCA security models remove the restriction in previous models and achieve standard notions of integrity and CCA security in the setting of updatable encryption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491420 (1).pdf`
- `downloads/12491420.pdf`
