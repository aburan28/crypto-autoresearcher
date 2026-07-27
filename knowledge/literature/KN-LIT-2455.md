---
id: KN-LIT-2455
type: literature
title: "An Algebraic Framework for Pseudorandom Functions and Applications to Related-Key Security"
authors:
  - "Michel Abdalla"
  - "Fabrice Benhamouda"
  - "Alain Passelègue"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we provide a new algebraic framework for pseudorandom functions which encompasses many of the existing algebraic constructions, including the ones by Naor and Reingold (FOCS’97), by Lewko and Waters (CCS’09), and by Boneh, Montgomery, and Raghunathan (CCS’10), as well as the related-key-secure pseudorandom functions by Bellare and Cash (Crypto’10) and by Abdalla et al. To achieve this goal, we introduce two versions of our framework.

## Key claims (as reported)
- The first, termed linearly independent polynomial security, states that the values (g P1 (~a) , . . . , g Pq (~a) ) are indistinguishable from a random tuple of the same size, when P1 , . . . , Pq are linearly independent multivariate polynomials of the secret key vector ~a.
- The second, which is a natural generalization of the first framework, additionally deals with constructions based on the decision linear and matrix Diffie-Hellman assumptions.
- In addition to unifying and simplifying proofs for existing schemes, our framework also yields new results, such as related-key security with respect to arbitrary permutations of polynomials.
- Our constructions are in the standard model and do not require the existence of multilinear maps.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160309 (1).pdf`
- `downloads/92160309 (2).pdf`
- `downloads/92160309.pdf`
