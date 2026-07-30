---
id: KN-LIT-3159
type: literature
title: "Converse Results to the Wiener Attack on RSA"
authors:
  - "Ron Steinfeld"
  - "Scott Contini"
  - "Huaxiong Wang"
  - "Josef Pieprzyk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A well-known attack on RSA with low secret-exponent d was given by Wiener about 15 years ago. Wiener showed that using continued fractions, one can efficiently recover the secret-exponent d from the public key (N, e) as long as d < N 1/4 .

## Key claims (as reported)
- Interestingly, Wiener stated that his attack may sometimes also work when d is slightly larger than N 1/4 .
- This raises the question of how much larger d can be: could the attack work with non-negligible probability for d = N 1/4+ρ for some constant ρ > 0?
- We answer this question in the negative by proving a converse to Wiener’s result.
- Our result shows that, for any fixed  > 0 and all sufficiently large modulus lengths, Wiener’s attack succeeds with negligible probability over a random choice of d < N δ (in an interval of size Ω(N δ )) as soon as δ > 1/4 + .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860185 (1).pdf`
- `downloads/33860185 (2).pdf`
- `downloads/33860185 (3).pdf`
- `downloads/33860185.pdf`
