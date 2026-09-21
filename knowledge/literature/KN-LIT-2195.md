---
id: KN-LIT-2195
type: literature
title: "A Practical-Time Related-Key Attack on the"
authors:
  - "KASUMI Cryptosystem Used in GSM"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The privacy of most GSM phone conversations is currently protected by the 20+ years old A5/1 and A5/2 stream ciphers, which were repeatedly shown to be cryptographically weak. They will soon be replaced by the new A5/3 (and the soon to be announced A5/4) algorithm based on the block cipher KASUMI, which is a modified version of MISTY.

## Key claims (as reported)
- In this paper we describe a new type of attack called a sandwich attack, and use it to construct a simple distinguisher for 7 of the 8 rounds of KASUMI with an amazingly high probability of 2−14 .
- By using this distinguisher and analyzing the single remaining round, we can derive the complete 128 bit key of the full KASUMI by using only 4 related keys, 226 data, 230 bytes of memory, and 232 time.
- These complexities are so small that we have actually simulated the attack in less than two hours on a single PC, and experimentally verified its correctness and complexity.
- Interestingly, neither our technique nor any other published attack can break MISTY in less than the 2128 complexity of exhaustive search, which indicates that the changes made by ETSI’s SAGE group in moving from MISTY to KASUMI resulted in a much weaker cipher.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230387 (1).pdf`
- `downloads/62230387 (2).pdf`
- `downloads/62230387 (3).pdf`
- `downloads/62230387.pdf`
