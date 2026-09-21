---
id: KN-LIT-4934
type: literature
title: "Minimizing the Two-Round Tweakable"
authors:
  - "Even-Mansour Cipher"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In CRYPTO 2015, Cogliati et al. have proposed one-round tweakable Even-Mansour (1-TEM) cipher constructed out of a single nbit public permutation π and a uniform and almost XOR-universal hash function H as (k, t, x) 7→ Hk (t) ⊕ π(Hk (t) ⊕ x), where t is the tweak, and x is the n-bit message. Authors have shown that its two-round extension, which we refer to as 2-TEM, obtained by cascading 2-independent instances of the construction gives 2n/3-bit security and r-round cascading gives rn/r +2-bit security.

## Key claims (as reported)
- In ASIACRYPT 2015, Cogliati and Seurin have shown that four-round tweakable Even-Mansour cipher, which we refer to as 4-TEM, constructed out of four independent n-bit permutations π1 , π2 , π3 , π4 and two independent n-bit keys k1 , k2 , defined as k1 ⊕ t ⊕ π4 (k2 ⊕ t ⊕ π3 (k1 ⊕ t ⊕ π2 (k2 ⊕ t ⊕ π1 (k1 ⊕ t ⊕ x)))), is secure upto 22n/3 adversarial queries.
- In this paper, we have shown that if we replace two independent permutations of 2-TEM (Cogliati et al., CRYPTO 2015) with a single n-bit public permutation, then the resultant construction still guarrantees security upto 22n/3 adversarial queries.
- Using the results derived therein, we also show that replacing the permutation (π4 , π3 ) with (π1 , π2 ) in the above equation preserves security upto 22n/3 adversarial queries.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491136 (1).pdf`
- `downloads/12491136.pdf`
