---
id: KN-LIT-5386
type: literature
title: "On Quantum Secure Compressing Pseudorandom Functions Ritam Bhaumik1[0000−0002−2883−4870] , Benoı̂t Cogliati2[0000−0001−6445−2514]"
authors:
  - "Jordan Ethan"
  - "Ashwin Jha"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pqc, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we characterize all 2n-bit-to-n-bit Pseudorandom Functions (PRFs) constructed with the minimum number of calls to n-bit-to-n-bit PRFs and arbitrary number of linear functions. First, we show that all two-round constructions are either classically insecure, or vulnerable to quantum period-finding attacks.

## Key claims (as reported)
- Second, we categorize three-round constructions depending on their vulnerability to these types of attacks.
- This allows us to identify classes of constructions that could be proven secure.
- We then proceed to show the security of the following three candidates against any quantum distinguisher that makes at most 2n/4 (possibly superposition) queries: TNT(x1 , x2 ) := f3 (x2 ⊕ f2 (x2 ⊕ f1 (x1 ))); LRQ(x1 , x2 ) := f2 (x2 ) ⊕ f3 (x2 ⊕ f1 (x1 )); LRWQ(x1 , x2 ) := f3 (f1 (x1 ) ⊕ f2 (x2 )).
- Note that the first construction is a classically secure tweakable blockcipher due to Bao et al., and the third construction was shown to be a quantum-secure tweakable block-cipher by Hosoyamada and Iwata with similar query limits.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438006 (1).pdf`
- `downloads/14438006.pdf`
