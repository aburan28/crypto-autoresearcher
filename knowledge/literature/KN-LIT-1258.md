---
id: KN-LIT-1258
type: literature
title: "Lattice-based Fault Attacks against ECMQV"
authors:
  - "Weiqiong Cao"
  - "Hua Chen("
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/882"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/882"
tags: [curve-arithmetic, ecdlp, ecdsa, elliptic-curve, lattice, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ECMQV is a standardized key agreement protocol based on ECC with an additional implicit signature authentication. In this paper we investigate the vulnerability of ECMQV against fault attacks and propose two efficient lattice-based fault attacks.

## Key claims (as reported)
- In our attacks, by inducing a storage fault to the ECC parameter a before the execution of ECMQV, we can construct two kinds of weak curves and successfully pass the public-key validation step in the protocol.
- Then, by solving ECDLP and using a guess-and-determine method, some information of the victim’s temporary private key and the implicit-signature result can be deduced.
- Based on the retrieved information, we build two new lattice-attack models and recover the upper half of the static private key.
- Compared with the previous lattice-attack models, our models relax the attack conditions and do not require the exact partial knowledge of the nonces.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-882 (1).pdf`
- `downloads/2024-882.pdf`
