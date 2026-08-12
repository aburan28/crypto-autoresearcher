---
id: KN-LIT-7255
type: literature
title: "Transient-Steady Effect Attack on Block Ciphers"
authors:
  - "Yanting Ren"
  - "An Wang⋆"
  - "Liji Wu⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A new Transient-Steady Effect attack on block ciphers called TSE attack is presented in this paper. The concept of transient-steady effect denotes the phenomenon that the output of a combinational circuit keeps a temporal value for a while before it finally switches to the correct value.

## Key claims (as reported)
- Unlike most existing fault attacks, our attack does not need a large amount of encryptions to build a statistical model.
- By injecting a clock glitch to capture the temporal value caused by transientsteady effect, attackers can obtain the information of key from faulty outputs directly.
- This work shows that AES implementations, which have transient-steady property, are vulnerable to our attack.
- Experiments are successfully conducted on two kinds of unmasked S-boxes and one kind of masked S-box implemented in serial with FPGA board.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930417 (1).pdf`
- `downloads/92930417.pdf`
