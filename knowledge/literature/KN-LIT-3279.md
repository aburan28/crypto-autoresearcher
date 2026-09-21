---
id: KN-LIT-3279
type: literature
title: "Cryptanalysis of the Revised NTRU Signature Scheme"
authors:
  - "Craig Gentry"
  - "Mike Szydlo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, lattice, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we describe a three-stage attack against Revised NSS, an NTRU-based signature scheme proposed at the Eurocrypt 2001 conference as an enhancement of the (broken) proceedings version of the scheme. The first stage, which typically uses a transcript of only 4 signatures, effectively cuts the key length in half while completely avoiding the intended hard lattice problem.

## Key claims (as reported)
- After an empirically fast second stage, the third stage of the attack combines lattice-based and congruence-based methods in a novel way to recover the private key in polynomial time.
- This cryptanalysis shows that a passive adversary observing only a few valid signatures can recover the signer’s entire private key.
- We also briefly address the security of NTRUSign, another NTRUbased signature scheme that was recently proposed at the rump session of Asiacrypt 2001.
- As we explain, some of our attacks on Revised NSS may be extended to NTRUSign, but a much longer transcript is necessary.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/nsssign_short3 (1).pdf`
- `downloads/nsssign_short3 (2).pdf`
- `downloads/nsssign_short3.pdf`
