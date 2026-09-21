---
id: KN-LIT-5177
type: literature
title: "Non-Interactive CCA2-Secure Threshold Cryptosystems: Achieving Adaptive Security in the Standard Model Without Pairings"
authors:
  - "Julien Devevey"
  - "Benoı̂t Libert"
  - "Khoa Nguyen"
  - "Thomas Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider threshold public-key encryption, where the decryption servers distributively hold the private key shares, and we need a threshold of these servers to decrypt the message (while the system remains secure when less than the threshold is corrupt). We investigate the notion of chosen-ciphertext secure threshold systems which has been historically hard to achieve.

## Key claims (as reported)
- We further require the systems to be, both, adaptively secure (i.e., secure against a strong adversary making corruption decisions dynamically during the protocol), and non-interactive (i.e., where decryption servers do not interact amongst themselves but rather efficiently contribute, each, a single message).
- To date, only pairing-based implementations were known to achieve security in the standard security model without relaxation (i.e., without assuming the random oracle idealization) under the above stringent requirements.
- Here, we investigate how to achieve the above using other assumptions (in order to understand what other algebraic building blocks and mathematical assumptions are needed to extend the domain of encryption methods achieving the above).
- Specifically, we show realizations under the Decision Composite Residuosity (DCR) and Learning-With-Errors (LWE) assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110194 (1).pdf`
- `downloads/127110194.pdf`
