---
id: KN-LIT-5477
type: literature
title: "On the Generic Insecurity of the Full Domain Hash"
authors:
  - "Yevgeniy Dodis"
  - "Roberto Oliveira"
  - "Krzysztof Pietrzak"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Full-Domain Hash (FDH) signature scheme [3] forms one the most basic usages of random oracles. It works with a family F of trapdoor permutations (TDP), where the signature of m is computed as f −1 (h(m)) (here f ∈R F and h is modelled as a random oracle).

## Key claims (as reported)
- It is known to be existentially unforgeable for any TDP family F [3], although a much tighter security reduction is known for a restrictive class of TDP’s [10, 14] — namely, those induced by a family of claw-free permutations (CFP) pairs.
- The latter result was shown [11] to match the best possible “black-box” security reduction in the random oracle model, irrespective of the TDP family F (e.g., RSA) one might use.
- In this work we investigate the question if it is possible to instantiate the random oracle h with a “real” family of hash functions H such that the corresponding schemes can be proven secure in the standard model, under some natural assumption on the family F.
- Our main result rules out the existence of such instantiations for any assumption on F which (1) is satisfied by a family of random permutations; and (2) does not allow the attacker to invert f ∈R F on an a-priori unbounded number of points.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/36210443 (1).pdf`
- `downloads/36210443 (2).pdf`
- `downloads/36210443 (3).pdf`
- `downloads/36210443.pdf`
