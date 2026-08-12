---
id: KN-LIT-5549
type: literature
title: "On the Provable Security of an Efficient RSA-Based Pseudorandom Generator"
authors:
  - "Ron Steinfeld"
  - "Josef Pieprzyk"
  - "Huaxiong Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pseudorandom Generators (PRGs) based on the RSA inversion (one-wayness) problem have been extensively studied in the literature over the last 25 years. These generators have the attractive feature of provable pseudorandomness security assuming the hardness of the RSA inversion problem.

## Key claims (as reported)
- However, despite extensive study, the most efficient provably secure RSA-based generators output asymptotically only at most O(log n) bits per multiply modulo an RSA modulus of bitlength n, and hence are too slow to be used in many practical applications.
- To bring theory closer to practice, we present a simple modification to the proof of security by Fischlin and Schnorr of an RSA-based PRG, which shows that one can obtain an RSA-based PRG which outputs Ω(n) bits per multiply and has provable pseudorandomness security assuming the hardness of a well-studied variant of the RSA inversion problem, where a constant fraction of the plaintext bits are given.
- Our result gives a positive answer to an open question posed by Gennaro (J. of Cryptology, 2005) regarding finding a PRG beating the rate O(log n) bits per multiply at the cost of a reasonable assumption on RSA inversion.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840193 (1).pdf`
- `downloads/42840193 (2).pdf`
- `downloads/42840193 (3).pdf`
- `downloads/42840193.pdf`
