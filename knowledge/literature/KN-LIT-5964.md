---
id: KN-LIT-5964
type: literature
title: "Prouff & Rivain’s Formal Security Proof of Masking, Revisited Tight Bounds in the Noisy Leakage Model"
authors:
  - "Loïc Masure"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, mpc, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking is a counter-measure that can be incorporated to software and hardware implementations of block ciphers to provably secure them against side-channel attacks. The security of masking can be proven in different types of threat models.

## Key claims (as reported)
- In this paper, we are interested in directly proving the security in the most realistic threat model, the so-called noisy leakage adversary, that captures well how real-world sidechannel adversaries operate.
- Direct proofs in this leakage model have been established by Prouff & Rivain at Eurocrypt 2013, Dziembowski et al. at Eurocrypt 2015, and Prest et al. at Crypto 2019.
- These proofs are complementary to each other, in the sense that the weaknesses of one proof are fixed in at least one of the others, and conversely.
- These weaknesses concerned in particular the strong requirements on the noise level and the security parameter to get meaningful security bounds, and some requirements on the type of adversary covered by the proof — i.e., chosen or random plaintexts.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850004 (1).pdf`
- `downloads/140850004.pdf`
