---
id: KN-LIT-4472
type: literature
title: "IND-CCA secure Cryptography based on a variant of the LPN Problem"
authors:
  - "Nico Döttling"
  - "Jörn Müller-Quade"
  - "Anderson Nascimento"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2003 Michael Alekhnovich (FOCS 2003) introduced a novel variant of the learning parity with noise problem and showed that it implies IND-CPA secure public-key cryptography. In this paper we introduce the first public-key encryption-scheme based on this assumption which is IND-CCA secure in the standard model.

## Key claims (as reported)
- Our main technical tool to achieve this is a novel all-but-one simulation technique based on the correlated products approach of Rosen and Segev (TCC 2009).
- Our IND-CCA1 secure scheme is asymptotically optimal with respect to ciphertext-expansion.
- To achieve IND-CCA2 security we use a technique of Dolev, Dwork and Naor (STOC 1991) based on one-time-signatures.
- For practical purposes, the efficiency of the IND-CCA2 scheme can be substantially improved by the use of additional assumptions to allow for more efficient signature schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580482 (1).pdf`
- `downloads/76580482 (2).pdf`
- `downloads/76580482 (3).pdf`
- `downloads/76580482.pdf`
