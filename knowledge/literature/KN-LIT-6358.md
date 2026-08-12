---
id: KN-LIT-6358
type: literature
title: "Sanitization of FHE Ciphertexts"
authors:
  - "Léo Ducas"
  - "Damien Stehlé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
By definition, fully homomorphic encryption (FHE) schemes support homomorphic decryption, and all known FHE constructions are bootstrapped from a Somewhat Homomorphic Encryption (SHE) scheme via this technique. Additionally, when a public key is provided, ciphertexts are also re-randomizable, e.g., by adding to them fresh encryptions of 0.

## Key claims (as reported)
- From those two operations we devise an algorithm to sanitize a ciphertext, by making its distribution canonical.
- In particular, the distribution of the ciphertext does not depend on the circuit that led to it via homomorphic evaluation, thus providing circuit privacy in the honestbut-curious model.
- Unlike the previous approach based on noise flooding, our approach does not degrade much the security/efficiency trade-off of the underlying FHE.
- The technique can be applied to all lattice-based FHE proposed so far, without substantially affecting their concrete parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650134 (1).pdf`
- `downloads/96650134.pdf`
