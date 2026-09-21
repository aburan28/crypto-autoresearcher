---
id: KN-LIT-2397
type: literature
title: "Algebraic Cryptanalysis of the PKC’2009 Algebraic Surface Cryptosystem"
authors:
  - "Jean-Charles Faugère"
  - "Pierre-Jean Spaenlehauer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, elliptic-curve, factoring, finite-field, lattice, pairing, pqc, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we fully break the Algebraic Surface Cryptosystem (ASC for short) proposed at PKC’2009 [3]. This system is based on an unusual problem in multivariate cryptography: the Section Finding Problem.

## Key claims (as reported)
- Given an algebraic surface X(x, y, t) ∈ Fp [x, y, t] such that degxy X(x, y, t) = w, the question is to find a pair of polynomials of degree d, ux (t) and uy (t), such that X(ux (t), uy (t), t) = 0.
- In ASC, the public key is the surface, and the secret key is the section.
- This asymmetric encryption scheme enjoys reasonable sizes of the keys: for recommended parameters, the size of the secret key is only 102 bits and the size of the public key is 500 bits.
- In this paper, we propose a message recovery attack whose complexity is quasi-linear in the size of the secret key.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/60560035 (1).pdf`
- `downloads/60560035 (2).pdf`
- `downloads/60560035 (3).pdf`
- `downloads/60560035.pdf`
