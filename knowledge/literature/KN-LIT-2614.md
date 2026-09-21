---
id: KN-LIT-2614
type: literature
title: "Attacks and Security Proofs of EAX-Prime"
authors:
  - "Kazuhiko Minematsu"
  - "Stefan Lucks"
  - "Hiraku Morita"
  - "Tetsu Iwata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
EAX′ (or EAX-prime) is an authenticated encryption (AE) specified by ANSI C12.22 as a standard security function for Smart Grid. EAX′ is based on EAX proposed by Bellare, Rogaway, and Wagner.

## Key claims (as reported)
- While EAX has a proof of security based on the pseudorandomness of the internal blockcipher, no published security result is known for EAX′ .
- This paper studies the security of EAX′ and shows that there is a sharp distinction in security of EAX′ depending on the input length.
- EAX′ encryption takes two inputs, called cleartext and plaintext, and we present various efficient attacks against EAX′ using single-block cleartext and plaintext.
- At the same time we prove that if cleartexts are always longer than one block, it is provably secure based on the pseudorandomness of the blockcipher.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240303 (1).pdf`
- `downloads/84240303 (2).pdf`
- `downloads/84240303 (3).pdf`
- `downloads/84240303.pdf`
