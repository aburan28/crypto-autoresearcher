---
id: KN-LIT-3211
type: literature
title: "Cryptanalyses on a Merkle-Damgård Based MAC — Almost Universal Forgery and Distinguishing-H Attacks"
authors:
  - "Yu Sasaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, pollard-rho, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents two types of cryptanalysis on a MerkleDamgård hash based MAC, which computes a MAC value of a message M by Hash(Kk`kM ) with a shared key K and the message length `. This construction is often called LPMAC.

## Key claims (as reported)
- Firstly, we present a distinguishingH attack against LPMAC instantiating any narrow-pipe Merkle-Damgård hash function with O(2n/2 ) queries, which indicates the incorrectness of the widely believed assumption that LPMAC instantiating a secure hash function should resist the distinguishing-H attack up to 2n queries.
- In fact, all of the previous distinguishing-H attacks considered dedicated attacks depending on the underlying hash algorithm, and most of the cases, reduced rounds were attacked with a complexity between 2n/2 and 2n .
- Because it works in generic, our attack updates these results, namely full rounds are attacked with O(2n/2 ) complexity.
- Secondly, we show that an even stronger attack, which is a powerful form of an almost universal forgery attack, can be performed on LPMAC.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370405 (1).pdf`
- `downloads/72370405 (2).pdf`
- `downloads/72370405 (3).pdf`
- `downloads/72370405.pdf`
