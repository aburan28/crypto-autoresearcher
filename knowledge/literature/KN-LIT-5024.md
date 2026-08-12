---
id: KN-LIT-5024
type: literature
title: "Multi-User Security of the Sum of Truncated"
authors:
  - "Random Permutations"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
For several decades, constructing pseudorandom functions from pseudorandom permutations, so-called Luby-Rackoff backward construction, has been a popular cryptographic problem. Two methods are well-known and comprehensively studied for this problem: summing two random permutations and truncating partial bits of the output from a random permutation.

## Key claims (as reported)
- In this paper, by combining both summation and truncation, we propose new Luby-Rackoff backward constructions, dubbed SaT1 and SaT2, respectively.
- SaT2 is obtained by partially truncating output bits from the sum of two independent random permutations, and SaT1 is its single permutationbased variant using domain separation.
- The distinguishing advantage √ against SaT1 and SaT2 is upper bounded by O( μqmax /2n−0.5m ) and √ 1.5 2n−0.5m ), respectively, in the multi-user setting, where n O( μqmax /2 is the size of the underlying permutation, m is the output size of the construction, μ is the number of users, and qmax is the maximum number of queries per user.
- We also prove the distinguishing advantage against a variant of XORP[3] (studied by Bhattacharya and Nandi at Asiacrypt 2021) using independent permutations, dubbed SoP3-2, is upper bounded √ 2 by O( μqmax /22.5n ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910317 (1).pdf`
- `downloads/137910317.pdf`
