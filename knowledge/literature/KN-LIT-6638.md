---
id: KN-LIT-6638
type: literature
title: "Signed Binary Representations Revisited Katsuyuki Okeya1 , Katja Schmidt-Samoa2"
authors:
  - "Christian Spahn"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The most common method for computing exponentiation of random elements in Abelian groups are sliding window schemes, which enhance the efficiency of the binary method at the expense of some precomputation. In groups where inversion is easy (e.g. elliptic curves), signed representations of the exponent are meaningful because they decrease the amount of required precomputation.

## Key claims (as reported)
- The asymptotic best signed method is wNAF, because it minimizes the precomputation effort whilst the non-zero density is nearly optimal.
- Unfortunately, wNAF can be computed only from the least significant bit, i.e. right-to-left.
- However, in connection with memory constraint devices left-to-right recoding schemes are by far more valuable.
- In this paper we define the MOF (Mutual Opposite Form), a new canonical representation of signed binary strings, which can be computed in any order.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/crypto04_camready2 (1).pdf`
- `downloads/crypto04_camready2 (2).pdf`
- `downloads/crypto04_camready2.pdf`
