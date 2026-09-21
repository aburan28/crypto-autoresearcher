---
id: KN-LIT-6901
type: literature
title: "Supersingular Curves in Cryptography"
authors:
  - "Steven D. Galbraith"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [abelian-variety, binary-field, class-group, dlp, elliptic-curve, extension-field, finite-field, hyperelliptic, index-calculus, jacobian, number-theory, pairing, provable-security, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Frey and Rück gave a method to transform the discrete logarithm problem in the divisor class group of a curve over Fq into a discrete logarithm problem in some finite field extension Fqk . The discrete logarithm problem can therefore be solved using index calculus algorithms as long as k is small.

## Key claims (as reported)
- In the elliptic curve case it was shown by Menezes, Okamoto and Vanstone that for supersingular curves one has k ≤ 6.
- In this paper curves of higher genus are studied.
- Bounds on the possible values for k in the case of supersingular curves are given which imply that supersingular curves are weaker than the general case for cryptography.
- Ways to ensure that a curve is not supersingular are also discussed.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/22480497 (1).pdf`
- `downloads/22480497 (2).pdf`
- `downloads/22480497.pdf`
