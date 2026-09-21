---
id: KN-LIT-2423
type: literature
title: "All-But-Many Lossy Trapdoor Functions and Selective Opening Chosen-Ciphertext Security from LWE"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Selective opening (SO) security refers to adversaries that receive a number of ciphertexts and, after having corrupted a subset of the senders (thus obtaining the plaintexts and the senders’ random coins), aim at breaking the security of remaining ciphertexts. So far, very few public-key encryption schemes are known to provide simulation-based selective opening (SIM-SO-CCA2) security under chosen-ciphertext attacks and most of them encrypt messages bit-wise.

## Key claims (as reported)
- The only exceptions to date rely on all-but-many lossy trapdoor functions (as introduced by Hofheinz; Eurocrypt’12) and the Composite Residuosity assumption.
- In this paper, we describe the first all-but-many lossy trapdoor function with security relying on the presumed hardness of the Learning-WithErrors problem (LWE) with standard parameters.
- Our construction exploits homomorphic computations on lattice trapdoors for lossy LWE matrices.
- By carefully embedding a lattice trapdoor in lossy public keys, we are able to prove SIM-SO-CCA2 security under the LWE assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401372 (1).pdf`
- `downloads/10401372.pdf`
