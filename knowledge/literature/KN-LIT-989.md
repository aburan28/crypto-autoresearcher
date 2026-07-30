---
id: KN-LIT-989
type: literature
title: "Guaranteed Output in O( n) Rounds for Round-Robin Sampling Protocols?"
authors:
  - "Ran Cohen"
  - "Jack Doerner"
  - "Yashvanth Kondi"
  - "abhi shelat"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/257"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/257"
tags: [cryptanalysis, mpc, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a notion of round-robin secure sampling that captures several protocols in the literature, such as the “powers-oftau” setup protocol for pairing-based polynomial commitments and zkSNARKs, and certain verifiable mixnets. Due to their round-robin structure, protocols of this class inherently require n sequential broadcast rounds, where n is the number of participants.

## Key claims (as reported)
- We describe how to compile them generically into protocols that require √ only O( n) broadcast rounds.
- Our compiled protocols guarantee output delivery against any dishonest majority.
- This stands in contrast to prior techniques, which require Ω(n) sequential broadcasts in most cases (and sometimes many more).
- Our compiled protocols permit a certain amount of adversarial bias in the output, as all sampling protocols with guaranteed output must, due to Cleve’s impossibility result (STOC’86).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760277 (1).pdf`
- `downloads/132760277.pdf`
