---
id: KN-LIT-1974
type: literature
title: "(One) failure is not an option Bootstrapping the search for failures in lattice-based encryption schemes"
authors:
  - "Jan-Pieter D’Anvers∗"
  - "Mélissa Rossi"
  - "Fernando Virdia"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, pairing, pqc, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based encryption schemes are often subject to the possibility of decryption failures, in which valid encryptions are decrypted incorrectly. Such failures, in large number, leak information about the secret key, enabling an attack strategy alternative to pure lattice reduction.

## Key claims (as reported)
- Extending the “failure boosting” technique of D’Anvers et al. in PKC 2019, we propose an approach that we call “directional failure boosting” that uses previously found “failing ciphertexts” to accelerate the search for new ones.
- We analyse in detail the case where the lattice is defined over polynomial ring modules quotiented by hX N + 1i and demonstrate it on a simple Mod-LWE-based scheme parametrized à la Kyber768/Saber.
- We show that for a given secret key (single-target setting), the cost of searching for additional failing ciphertexts after one or more have already been found, can be sped up dramatically.
- We thus demonstrate that, in this single-target model, these schemes should be designed so that it is hard to even obtain one decryption failure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105294 (1).pdf`
- `downloads/12105294.pdf`
