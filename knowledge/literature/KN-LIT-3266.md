---
id: KN-LIT-3266
type: literature
title: "Cryptanalysis of the Full Spritz Stream Cipher"
authors:
  - "Subhadeep Banik"
  - "Takanori Isobe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Spritz is a stream cipher proposed by Rivest and Schuldt at the rump session of CRYPTO 2014. It is intended to be a replacement of the popular RC4 stream cipher.

## Key claims (as reported)
- In this paper we propose distinguishing attacks on the full Spritz, based on a short-term bias in the first two bytes of a keystream and a long-term bias in the first two bytes of every cycle of N keystream bytes, where N is the size of the internal permutation.
- Our attacks are able to distinguish a keystream of the full Spritz from a random sequence with samples of first two bytes produced by 244.8 multiple key-IV pairs or 260.8 keystream bytes produced by a single keyIV pair.
- These biases are also useful in the event of plaintext recovery in a broadcast attack.
- In the second part of the paper, we look at a state recovery attack on Spritz, in a special situation when the cipher enters a class of weak states.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830061 (1).pdf`
- `downloads/97830061.pdf`
