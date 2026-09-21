---
id: KN-LIT-2221
type: literature
title: "A Security Analysis of the NIST SP 800-90 Elliptic Curve Random Number Generator"
authors:
  - "Daniel R. L. Brown"
  - "Kristian Gjøsteen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdlp, elliptic-curve, mov-fr, pairing, provable-security, supersingular, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An elliptic curve random number generator (ECRNG) has been approved in a NIST standard and proposed for ANSI and SECG draft standards. This paper proves that, if three conjectures are true, then the ECRNG is secure.

## Key claims (as reported)
- The three conjectures are hardness of the elliptic curve decisional Diffie-Hellman problem and the hardness of two newer problems, the x-logarithm problem and the truncated point problem.
- The x-logarithm problem is shown to be hard if the decisional DiffieHellman problem is hard, although the reduction is not tight.
- The truncated point problem is shown to be solvable when the minimum amount of bits allowed in NIST standards are truncated, thereby making it insecure for applications such as stream ciphers.
- Nevertheless, it is argued that for nonce and key generation this distinguishability is harmless.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220459 (1).pdf`
- `downloads/46220459 (2).pdf`
- `downloads/46220459 (3).pdf`
- `downloads/46220459.pdf`
