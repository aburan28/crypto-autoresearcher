---
id: KN-LIT-5507
type: literature
title: "On the Insecurity of a Server-Aided RSA Protocol"
authors:
  - "Phong Q. Nguyen"
  - "Igor E. Shparlinski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, hash, lattice, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto ’88, Matsumoto, Kato and Imai proposed a protocol, known as RSA-S1, in which a smart card computes an RSA signature, with the help of an untrusted powerful server. There exist two kinds of attacks against such protocols: passive attacks (where the server does not deviate from the protocol) and active attacks (where the server may return false values).

## Key claims (as reported)
- Pfitzmann and Waidner presented at Eurocrypt ’92 a passive meet-in-the-middle attack and a few active attacks on RSAS1.
- They discussed two simple countermeasures to thwart such attacks: renewing the decomposition of the RSA private exponent, and checking the signature (in which case a small public exponent must be used).
- We present a new lattice-based provable passive attack on RSA-S1 which recovers the factorization of the RSA modulus when a very small public exponent is used, for many choices of the parameters.
- The first countermeasure does not prevent this attack because the attack is a one-round attack, that is, only a single execution of the protocol is required.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/22480021 (1).pdf`
- `downloads/22480021 (2).pdf`
- `downloads/22480021.pdf`
