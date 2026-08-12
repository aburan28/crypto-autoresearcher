---
id: KN-LIT-6882
type: literature
title: "Succinct Functional Commitment for a Large Class of Arithmetic Circuits"
authors:
  - "Helger Lipmaa"
  - "Kateryna Pavlyk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A succinct functional commitment (SFC) scheme for a circuit class CC enables, for any circuit C ∈ CC, the committer to first succinctly commit to a vector α, and later succinctly open the commitment to C(α, β), where the verifier chooses β at the time of opening. Unfortunately, SFC commitment schemes are known only for severely limited function classes like the class of inner products.

## Key claims (as reported)
- By making non-blackbox use of SNARK-construction techniques, we propose a SFC scheme for the large class of semi-sparse polynomials.
- The new SFC scheme can be used to, say, efficiently (1) implement sparse polynomials, and (2) aggregate various interesting SFC (e.g., vector commitment and polynomial commitment) schemes.
- The new scheme is evaluation-binding under a new instantiation of the computational uber-assumption.
- We provide a thorough analysis of the new assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491274 (1).pdf`
- `downloads/12491274.pdf`
