---
id: KN-LIT-3305
type: literature
title: "CRYPTOGRAPHIC IMPLICATIONS OF HESS’ GENERALIZED GHS ATTACK"
authors:
  - "ALFRED MENEZES"
  - "EDLYN TESKE"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, extension-field, finite-field, hyperelliptic, index-calculus, isogeny, jacobian, pollard-rho, prime-field, provable-security, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A finite field K is said to be weak for elliptic curve cryptography if all instances of the discrete logarithm problem for all elliptic curves over K can be solved in significantly less time than it takes Pollard’s rho method to solve the hardest instances. By considering the GHS Weil descent attack, it was previously shown that characteristic two finite fields Fq5 are weak.

## Key claims (as reported)
- In this paper, we examine characteristic two finite fields Fqn for weakness under Hess’ generalization of the GHS attack.
- We show that the fields Fq7 are potentially partially weak in the sense that any instance of the discrete logarithm problem for half of all elliptic curves over Fq7 , namely those curves E for which #E(Fq7 ) is divisible by 4, can likely be solved in significantly less time than it takes Pollard’s rho method to solve the hardest instances.
- We also show that the fields Fq3 are partially weak, that the fields Fq6 are potentially weak, and that the fields Fq8 are potentially partially weak.
- Finally, we argue that the other fields F2N where N is not divisible by 3, 5, 6, 7 or 8, are not weak under Hess’ generalized GHS attack.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/corr2004-25.pdf`
