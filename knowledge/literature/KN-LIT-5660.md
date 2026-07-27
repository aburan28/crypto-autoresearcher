---
id: KN-LIT-5660
type: literature
title: "Optimal Security Proofs for Full Domain Hash, Revisited"
authors:
  - "Saqib A. Kakvi"
  - "Eike Kiltz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
RSA Full Domain Hash (RSA-FDH) is a digital signature scheme, secure again chosen message attacks in the random oracle model. The best known security reduction from the RSA assumption is nontight, i.e., it loses a factor of qs , where qs is the number of signature queries made by the adversary.

## Key claims (as reported)
- It was furthermore proved by Coron (EUROCRYPT 2002) that a security loss of qs is optimal and cannot possibly be improved.
- In this work we uncover a subtle flaw in Coron’s impossibility result.
- Concretely, we show that it only holds if the underlying trapdoor permutation is certified.
- Since it is well known that the RSA trapdoor permutation is (for all practical parameters) not certified, this renders Coron’s impossibility result moot for RSA-FDH.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370533 (1).pdf`
- `downloads/72370533 (2).pdf`
- `downloads/72370533 (3).pdf`
- `downloads/72370533.pdf`
