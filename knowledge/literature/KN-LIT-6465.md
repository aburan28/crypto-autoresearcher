---
id: KN-LIT-6465
type: literature
title: "Secure Signatures and Chosen Ciphertext Security in a Quantum Computing World"
authors:
  - "Dan Boneh"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the study of quantum-secure digital signatures and quantum chosen ciphertext security. In the case of signatures, we enhance the standard chosen message query model by allowing the adversary to issue quantum chosen message queries: given a superposition of messages, the adversary receives a superposition of signatures on those messages.

## Key claims (as reported)
- Similarly, for encryption, we allow the adversary to issue quantum chosen ciphertext queries: given a superposition of ciphertexts, the adversary receives a superposition of their decryptions.
- These adversaries model a natural ubiquitous quantum computing environment where end-users sign messages and decrypt ciphertexts on a personal quantum computer.
- We construct classical systems that remain secure when exposed to such quantum queries.
- For signatures, we construct two compilers that convert classically secure signatures into signatures secure in the quantum setting and apply these compilers to existing post-quantum signatures.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420154 (1).pdf`
- `downloads/80420154 (2).pdf`
- `downloads/80420154 (3).pdf`
- `downloads/80420154.pdf`
