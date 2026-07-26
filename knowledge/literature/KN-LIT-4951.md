---
id: KN-LIT-4951
type: literature
title: "MonZ2k a: Fast Maliciously Secure Two Party Computation on Z2k"
authors:
  - "Dario Catalano"
  - "Mario Di Raimondo"
  - "Dario Fiore"
  - "Irene Giacomelli"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present a new 2-party protocol for secure computation over rings of the form Z2k . As many recent efficient MPC protocols supporting dishonest majority, our protocol consists of a heavier (input-independent) pre-processing phase and a very efficient online stage.

## Key claims (as reported)
- Our offline phase is similar to BeDOZa (Bendlin et al.
- Eurocrypt 2011) but employs Joye-Libert (JL, Eurocrypt 2013) as underlying homomorphic cryptosystem and, notably, it can be proven secure without resorting to the expensive sacrifice step.
- JL turns out to be particularly well suited for the ring setting as it naturally supports Z2k as underlying message space.
- Moreover, it enjoys several additional properties (such as valid ciphertext-verifiability and efficiency) that make it a very good fit for MPC in general.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110138 (1).pdf`
- `downloads/12110138.pdf`
