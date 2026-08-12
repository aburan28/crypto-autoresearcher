---
id: KN-LIT-5693
type: literature
title: "Ouroboros Praos: An adaptively-secure, semi-synchronous proof-of-stake blockchain"
authors:
  - "Bernardo David"
  - "Peter Gaži"
  - "Aggelos Kiayias"
  - "Alexander Russell"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present “Ouroboros Praos”, a proof-of-stake blockchain protocol that, for the first time, provides security against fully-adaptive corruption in the semi-synchronous setting: Specifically, the adversary can corrupt any participant of a dynamically evolving population of stakeholders at any moment as long the stakeholder distribution maintains an honest majority of stake; furthermore, the protocol tolerates an adversarially-controlled message delivery delay unknown to protocol participants. To achieve these guarantees we formalize and realize in the universal composition setting a suitable form of forward secure digital signatures and a new type of verifiable random function that maintains unpredictability under malicious key generation.

## Key claims (as reported)
- Our security proof develops a general combinatorial framework for the analysis of semi-synchronous blockchains that may be of independent interest.
- We prove our protocol secure under standard cryptographic assumptions in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822378 (1).pdf`
- `downloads/10822378.pdf`
