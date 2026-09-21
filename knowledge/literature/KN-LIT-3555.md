---
id: KN-LIT-3555
type: literature
title: "Efficient Dissection of Composite Problems, with"
authors:
  - "Applications to Cryptanalysis"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we show that a large class of diverse problems have a bicomposite structure which makes it possible to solve them with a new type of algorithm called dissection, which has much better time/memory tradeoffs than previously known algorithms. A typical example is the problem of finding the key of multiple encryption schemes with r independent n-bit keys.

## Key claims (as reported)
- All the previous error-free attacks required time T and memory M satisfying T M = 2rn , and even if “false negatives” are allowed, no attack could achieve T M < 23rn/4 .
- Our new technique yields the first algorithm which never errs and finds all the possible keys with a smaller product of T M , such as T = 24n time and M = 2n memory for breaking the sequential execution of r = 7 block ciphers.
- The improvement ratio we obtain increases in an unbounded way as r increases, and if we allow algorithms which can sometimes miss solutions, we can get even better tradeoffs by combining our dissection technique with parallel collision search.
- To demonstrate the generality of the new dissection technique, we show how to use it in a generic way in order to attack hash functions with a rebound attack, to solve hard knapsack problems, and to find the shortest solution to a generalized version of Rubik’s cube with better time complexities (for small memory complexities) than the best previously known algorithms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170712 (1).pdf`
- `downloads/74170712 (2).pdf`
- `downloads/74170712 (3).pdf`
- `downloads/74170712.pdf`
