---
id: KN-LIT-4855
type: literature
title: "Masking against Side-Channel Attacks: a Formal Security Proof"
authors:
  - "Emmanuel Prouff"
  - "Matthieu Rivain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, mpc, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking is a well-known countermeasure to protect block cipher implementations against side-channel attacks. The principle is to randomly split every sensitive intermediate variable occurring in the computation into d + 1 shares, where d is called the masking order and plays the role of a security parameter.

## Key claims (as reported)
- Although widely used in practice, masking is often considered as an empirical solution and its effectiveness is rarely proved.
- In this paper, we provide a formal security proof for masked implementations of block ciphers.
- Specifically, we prove that the information gained by observing the leakage from one execution can be made negligible (in the masking order).
- To obtain this bound, we assume that every elementary calculation in the implementation leaks a noisy function of its input, where the amount of noise can be chosen by the designer (yet linearly bounded).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810139 (1).pdf`
- `downloads/78810139 (2).pdf`
- `downloads/78810139 (3).pdf`
- `downloads/78810139.pdf`
