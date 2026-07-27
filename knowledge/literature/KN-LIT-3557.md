---
id: KN-LIT-3557
type: literature
title: "Efficient Extension of Standard Schnorr/RSA Signatures into Universal Designated-Verifier Signatures"
authors:
  - "Ron Steinfeld"
  - "Huaxiong Wang"
  - "Josef Pieprzyk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Universal Designated-Verifier Signature (UDVS) schemes are digital signature schemes with additional functionality which allows any holder of a signature to designate the signature to any desired designatedverifier such that the designated-verifier can verify that the message was signed by the signer, but is unable to convince anyone else of this fact. Since UDVS schemes reduce to standard signatures when no verifier designation is performed, it is natural to ask how to extend the classical Schnorr or RSA signature schemes into UDVS schemes, so that the existing key generation and signing implementation infrastructure for these schemes can be used without modification.

## Key claims (as reported)
- We show how this can be efficiently achieved, and provide proofs of security for our schemes in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470087 (1).pdf`
- `downloads/29470087 (2).pdf`
- `downloads/29470087.pdf`
