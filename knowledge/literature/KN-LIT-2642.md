---
id: KN-LIT-2642
type: literature
title: "Automatic Search for Key-Bridging Technique:"
authors:
  - "Applications to LBlock"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Key schedules in block ciphers are often highly simplified, which causes weakness that can be exploited in many attacks. At ASIACRYPT 2011, Dunkelman et al. proposed a technique using the weakness in the key schedule of AES, called key-bridging technique, to improve the overall complexity.

## Key claims (as reported)
- The advantage of key-bridging technique is that it allows the adversary to deduce some sub-key bits from some other sub-key bits, even though they are separated by many key mixing steps.
- Although the relations of successive rounds may be easy to see, the relations of two rounds separated by some mixing steps are very hard to find.
- In this paper, we describe a versatile and powerful algorithm for searching key-bridging technique on word-oriented and bit-oriented block ciphers.
- To demonstrate the usefulness of our approach, we apply our tool to the impossible differential and multidimensional zero correlation linear attacks on 23-round LBlock, 23-round TWINE-80 and 25round TWINE-128.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830235 (1).pdf`
- `downloads/97830235.pdf`
