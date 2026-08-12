---
id: KN-LIT-7188
type: literature
title: "Total Break of the `-IC Signature Scheme"
authors:
  - "Pierre-Alain Fouque"
  - "Gilles Macario-Rat"
  - "Ludovic Perret"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, mov-fr, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we describe efficient forgery and full-key recovery attacks on the `-IC− signature scheme recently proposed at PKC 2007. This cryptosystem is a multivariate scheme based on a new internal quadratic primitive which avoids some drawbacks of previous multivariate schemes: the scheme is extremely fast since it requires one exponentiation in a finite field of medium size and the public key is shorter than in many multivariate signature schemes.

## Key claims (as reported)
- Our attacks rely on the recent cryptanalytic tool developed by Dubois et al. against the SFLASH signature scheme.
- However, the final stage of the attacks requires the use of Gröbner basis techniques to conclude to actually forge a signature (resp. to recover the secret key).
- For the forgery attack, this is due to the fact that Patarin’s attack is much more difficult to mount against `-IC.
- The key recovery attack is also very efficient since it is faster to recover equivalent secret keys than to forge.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390001 (1).pdf`
- `downloads/49390001 (2).pdf`
- `downloads/49390001 (3).pdf`
- `downloads/49390001.pdf`
