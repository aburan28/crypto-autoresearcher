---
id: KN-LIT-2064
type: literature
title: "A Generalized Method of Differential Fault Attack Against AES Cryptosystem"
authors:
  - "Amir Moradi"
  - "Mohammad T. Manzuri Shalmani"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we describe two differential fault attack techniques against Advanced Encryption Standard (AES). We propose two models for fault occurrence; we could find all 128 bits of key using one of them and only 6 faulty ciphertexts.

## Key claims (as reported)
- We need approximately 1500 faulty ciphertexts to discover the key with the other fault model.
- Union of these models covers all faults that can occur in the 9th round of encryption algorithm of AES-128 cryptosystem.
- One of main advantage of proposed fault models is that any fault in the AES encryption from start (AddRoundKey with the main key before the first round) to MixColumns function of 9th round can be modeled with one of our fault models.
- These models cover all states, so generated differences caused by diverse plaintexts or ciphertexts can be supposed as faults and modeled with our models.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/08 (1).pdf`
- `downloads/08 (2).pdf`
- `downloads/08 (3).pdf`
- `downloads/08.pdf`
