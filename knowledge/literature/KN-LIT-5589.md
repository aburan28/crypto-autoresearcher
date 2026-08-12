---
id: KN-LIT-5589
type: literature
title: "On the Security of the “Free-XOR” Technique?"
authors:
  - "Seung Geol Choi"
  - "Jonathan Katz"
  - "Ranjit Kumaresan"
  - "Hong-Sheng Zhou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Yao’s garbled-circuit approach enables constant-round secure two-party computation of any function. In Yao’s original construction, each gate in the circuit requires the parties to perform a constant number of encryptions/decryptions and to send/receive a constant number of ciphertexts.

## Key claims (as reported)
- Kolesnikov and Schneider (ICALP 2008) proposed an improvement that allows XOR gates to be evaluated “for free,” incurring no cryptographic operations and zero communication.
- Their “free-XOR” technique has proven very popular, and has been shown to improve performance of garbled-circuit protocols by up to a factor of 4.
- Kolesnikov and Schneider proved security of their approach in the random oracle model, and claimed that (an unspecified variant of) correlation robustness suffices; this claim has been repeated in subsequent work, and similar ideas have since been used in other contexts.
- We show that the free-XOR technique cannot be proven secure based on correlation robustness alone; somewhat surprisingly, some form of circular security is also required.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940123 (1).pdf`
- `downloads/71940123 (2).pdf`
- `downloads/71940123 (3).pdf`
- `downloads/71940123.pdf`
