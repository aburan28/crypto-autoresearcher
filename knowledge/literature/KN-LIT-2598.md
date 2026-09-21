---
id: KN-LIT-2598
type: literature
title: "Asymptotics of hybrid primal lattice attacks"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The literature gives the impression that (1) existing heuristics accurately predict how effective lattice attacks are, (2) non-ternary lattice systems are not vulnerable to hybrid multi-decoding primal attacks, and (3) the asymptotic exponents of attacks against non-ternary systems have stabilized. This paper shows that 1 contradicts 2 and that 1 contradicts 3: the existing heuristics imply that hybrid primal key-recovery attacks are exponentially faster than standard non-hybrid primal key-recovery attacks against the LPR PKE with any constant error width.

## Key claims (as reported)
- This is the first report since 2015 of an exponential speedup in heuristic non-quantum primal attacks against non-ternary LPR.
- Quantitatively, for dimension n, modulus nQ0 +o(1) , and error width w, a surprisingly simple hybrid attack reduces heuristic costs from 2(ρ+o(1))n to 2(ρ−ρH0 +o(1))n , where z0 = 2Q0 /(Q0 + 1/2)2 , ρ = z0 log4 (3/2), and H0 = 1/(1 + (lg w)/0.057981z0 ).
- This raises the questions of (1) what heuristic exponent is achieved by more sophisticated hybrid attacks and (2) what impact hybrid attacks have upon concrete cryptosystems whose security analyses have ignored hybrid attacks, such as Kyber-512.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/hybrid-20231208.pdf`
