---
id: KN-LIT-7561
type: literature
title: "“Ooh Aah... Just a Little Bit” : A small amount of side channel can go a long way"
authors:
  - "Naomi Benger"
  - "Joop van de Pol"
  - "Nigel P. Smart"
  - "Yuval Yarom"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, cryptanalysis, curve-arithmetic, ecdsa, elliptic-curve, implementation, lattice, prime-field, provable-security, rsa, side-channel, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We apply the F LUSH +R ELOAD side-channel attack based on cache hits/misses to extract a small amount of data from OpenSSL ECDSA signature requests. We then apply a “standard” lattice technique to extract the private key, but unlike previous attacks we are able to make use of the side-channel information from almost all of the observed executions.

## Key claims (as reported)
- This means we obtain private key recovery by observing a relatively small number of executions, and by expending a relatively small amount of post-processing via lattice reduction.
- We demonstrate our analysis via experiments using the curve secp256k1 used in the Bitcoin protocol.
- In particular we show that with as little as 200 signatures we are able to achieve a reasonable level of success in recovering the secret key for a 256-bit curve.
- This is significantly better than prior methods of applying lattice reduction techniques to similar side channel information.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310103 (1).pdf`
- `downloads/87310103 (2).pdf`
- `downloads/87310103 (3).pdf`
- `downloads/87310103.pdf`
