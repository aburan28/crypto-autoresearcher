---
id: KN-LIT-2126
type: literature
title: "A New and Improved Paradigm for Hybrid Encryption Secure Against Chosen-Ciphertext Attack"
authors:
  - "Yvo Desmedt∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new encryption scheme which is secure against adaptive chosenciphertext attack (or CCA2-secure) in the standard model (i.e. without the use of random oracle). Our scheme is a hybrid one: it first uses a public-key step (the Key Encapsulation Module or KEM) to encrypt a random key, which is then used to encrypt the actual message using a symmetric encryption algorithm (the Data Encapsulation Module or DEM).

## Key claims (as reported)
- Our scheme is a modification of the hybrid scheme presented by Shoup in [18] (based on the Cramer-Shoup scheme in [4]).
- Its major practical advantage is that it saves the computation of one exponentiation and produces shorter ciphertexts.
- This effciency improvement is the result of a surprising observation: previous hybrid schemes were proven secure by proving that both the KEM and the DEM were CCA2secure.
- On the other hand, our KEM is not CCA2-secure, yet the whole scheme is, assuming the Decisional Diffie-Hellman (DDH) Assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/kdgs-journal.pdf`
