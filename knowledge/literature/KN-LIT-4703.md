---
id: KN-LIT-4703
type: literature
title: "Learning a Parallelepiped: Cryptanalysis of GGH and NTRU Signatures"
authors:
  - "Phong Q. Nguyen"
  - "Oded Regev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based signature schemes following the GoldreichGoldwasser-Halevi (GGH) design have the unusual property that each signature leaks information on the signer’s secret key, but this does not necessarily imply that such schemes are insecure. At Eurocrypt ’03, Szydlo proposed a potential attack by showing that the leakage reduces the key-recovery problem to that of distinguishing integral quadratic forms.

## Key claims (as reported)
- He proposed a heuristic method to solve the latter problem, but it was unclear whether his method could attack real-life parameters of GGH and NTRUSign.
- Here, we propose an alternative method to attack signature schemes à la GGH, by studying the following learning problem: given many random points uniformly distributed over an unknown n-dimensional parallelepiped, recover the parallelepiped or an approximation thereof.
- We transform this problem into a multivariate optimization problem that can be solved by a gradient descent.
- Our approach is very effective in practice: we present the first succesful key-recovery experiments on NTRUSign-251 without perturbation, as proposed in half of the parameter choices in NTRU standards under consideration by IEEE P1363.1.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040273 (1).pdf`
- `downloads/40040273 (2).pdf`
- `downloads/40040273 (3).pdf`
- `downloads/40040273.pdf`
