---
id: KN-LIT-2134
type: literature
title: "A New Attack with Side Channel Leakage during Exponent Recoding Computations"
authors:
  - "Yasuyuki Sakai"
  - "Kouichi Sakurai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, ecdsa, elliptic-curve, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we propose a new side channel attack, where exponent recodings for public key cryptosystems such as RSA and ECDSA are considered. The known side channel attacks and countermeasures for public key cryptosystems were against the main stage (square and multiply stage) of the modular exponentiation (or the point multiplication on an elliptic curve).

## Key claims (as reported)
- We have many algorithms which achieve fast computation of exponentiations.
- When we compute an exponentiation, the exponent recoding has to be carried out before the main stage.
- There are some exponent recoding algorithms including conditional branches, in which instructions depend on the given exponent value.
- Consequently exponent recoding can constitute an information channel, providing the attacker with valuable information on the secret exponent.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560299 (1).pdf`
- `downloads/31560299 (2).pdf`
- `downloads/31560299.pdf`
