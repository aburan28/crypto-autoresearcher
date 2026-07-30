---
id: KN-LIT-6605
type: literature
title: "Shorter Pairing-based Arguments under Standard Assumptions"
authors:
  - "Alonso González"
  - "Carla Ràfols"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper constructs efficient non-interactive arguments for correct evaluation of arithmetic and boolean circuits with proof size O(d) group elements, where d is the multiplicative depth of the circuit, under falsifiable assumptions. This is achieved by combining techniques from SNARKs and QA-NIZK arguments of membership in linear spaces.

## Key claims (as reported)
- The first construction is very efficient (the proof size is ≈ 4d group elements and the verification cost is ≈ 4d pairings and O(n + n0 + d) exponentiations, where n is the size of the input and n0 of the output) but one type of attack can only be ruled out assuming the knowledge soundness of QANIZK arguments of membership in linear spaces.
- We give an alternative construction which replaces this assumption with a decisional assumption in bilinear groups at the cost of approximately doubling the proof size.
- The construction for boolean circuits can be made zero-knowledge with Groth-Sahai proofs, resulting in a NIZK argument for circuit satisfiability based on falsifiable assumptions in bilinear groups of proof size O(n + d).
- Our main technical tool is what we call an “argument of knowledge transfer”.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210313 (1).pdf`
- `downloads/119210313.pdf`
