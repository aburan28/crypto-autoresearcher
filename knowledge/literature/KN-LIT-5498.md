---
id: KN-LIT-5498
type: literature
title: "On the Impossibility of Instantiating PSS in the Standard Model"
authors:
  - "Rishiraj Bhattacharyya"
  - "Avradip Mandal"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, provable-security, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we consider the problem of securely instantiating Probabilistic Signature Scheme (PSS) in the standard model. PSS, proposed by Bellare and Rogaway [3] is a widely deployed randomized signature scheme, provably secure (unforgeable under adaptively chosen message attacks) in Random Oracle Model.

## Key claims (as reported)
- Our main result is a black-box impossibility result showing that one can not prove unforgeability of PSS against chosen message attacks using blackbox techniques even assuming existence of ideal trapdoor permutations (a strong abstraction of trapdoor permutations which inherits all security properties of a random permutation, introduced by Kiltz and Pietrzak in Eurocrypt 2009) or the recently proposed lossy trapdoor permutations [20].
- Moreover, we show onewayness, the most common security property of a trapdoor permutation does not suffice to prove even the weakest security criteria, namely unforgeability under zero message attack.
- Our negative results can easily be extended to any randomized signature scheme where one can recover the random string from a valid signature.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710359 (1).pdf`
- `downloads/65710359 (2).pdf`
- `downloads/65710359 (3).pdf`
- `downloads/65710359.pdf`
