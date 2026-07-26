---
id: KN-LIT-2141
type: literature
title: "A New Decryption Failure Attack against HQC"
authors:
  - "Qian Guo"
  - "Thomas Johansson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, factoring, lattice, mov-fr, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HQC is an IND-CCA2 KEM running for standardization in NIST’s post-quantum cryptography project and has advanced to the second round. It is a code-based scheme in the class of public key encryptions, with given sets of parameters spanning NIST security strength 1, 3 and 5, corresponding to 128, 192 and 256 bits of classic security.

## Key claims (as reported)
- In this paper we present an attack recovering the secret key of an HQC instance named hqc-256-1.
- The attack requires a single precomputation performed once and then never again.
- The online attack on an HQC instance then submits about 264 special ciphertexts for decryption (obtained from the precomputation) and a phase of analysis studies the subset of ciphertexts that are not correctly decrypted.
- In this phase, the secret key of the HQC instance is determined.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491205 (1).pdf`
- `downloads/12491205.pdf`
