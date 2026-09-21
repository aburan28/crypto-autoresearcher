---
id: KN-LIT-2183
type: literature
title: "A Polynomial Time Attack on RSA with Private CRT-Exponents Smaller Than N 0.073"
authors:
  - "Ellen Jochemsz"
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Wiener’s famous attack on RSA with d < N 0.25 shows that using a small d for an efficient decryption process makes RSA completely insecure. As an alternative, Wiener proposed to use the Chinese Remainder Theorem in the decryption phase, where dp = d mod (p − 1) and dq = d mod (q − 1) are chosen significantly smaller than p and q.

## Key claims (as reported)
- The parameters dp , dq are called private CRT-exponents.
- Since Wiener’s proposal in 1990, it has been a challenging open question whether there exists a polynomial time attack on small private CRT-exponents.
- In this paper, we give an affirmative answer to this question, and show that a polynomial time attack exists if dp and dq are smaller than N 0.073 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220388 (1).pdf`
- `downloads/46220388 (2).pdf`
- `downloads/46220388 (3).pdf`
- `downloads/46220388.pdf`
