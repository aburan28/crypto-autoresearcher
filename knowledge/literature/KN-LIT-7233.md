---
id: KN-LIT-7233
type: literature
title: "Towards Tight Random Probing Security Gaëtan"
authors:
  - "Maximilian Orlt"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proving the security of masked implementations in theoretical models that are relevant to practice and match the best known attacks of the side-channel literature is a notoriously hard problem. The random probing model is a promising candidate to contribute to this challenge, due to its ability to capture the continuous nature of physical leakage (contrary to the threshold probing model), while also being convenient to manipulate in proofs and to automate with verification tools.

## Key claims (as reported)
- Yet, despite recent progress in the design of masked circuits with good asymptotic security guarantees in this model, existing results still fall short when it comes to analyze the security of concretely useful circuits under realistic noise levels and with low number of shares.
- In this paper, we contribute to this issue by introducing a new composability notion, the Probe Distribution Table (PDT), and a new tool (called STRAPS, for the Sampled Testing of the RAndom Probing Security).
- Their combination allows us to significantly improve the tightness of existing analyses in the most practical (low noise, low number of shares) region of the design space.
- We illustrate these improvements by quantifying the random probing security of an AES S-box circuit, masked with the popular multiplication gadget of Ishai, Sahai and Wagner from Crypto 2003, with up to six shares.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826191 (1).pdf`
- `downloads/12826191.pdf`
