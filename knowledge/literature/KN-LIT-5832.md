---
id: KN-LIT-5832
type: literature
title: "Practical Covert Authentication"
authors:
  - "Stanislaw Jarecki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Von Ahn, Hopper, and Langford [vAHL05] introduced the notion of two-party steganographic a.k.a. covert computation, which assures that neither party can distinguish its counterparty from a random noise generator, except for what is revealed by the final output of the securely computed function. The flagship motivation for covert computation is covert authentication, where two parties want to authenticate each other, e.g. as some credential holders, but a party who lacks the credentials is not only unable to pass the authentication protocol, but cannot even distinguish a protocol instance from random noise.

## Key claims (as reported)
- Previous work on covert computation [vAHL05,CGOS07] showed generalpurpose protocols whose efficiency is linear in the size of the circuit representation of the computed function.
- Here we show the first practical (assuming a large-enough random steganographic channel) covert protocol for the specific task of two-party mutual authentication, secure under the strong RSA, DQR, and DDH assumptions.
- The protocol takes 5 rounds (3 in ROM), O(1) modular exponentiations, and supports revocation and identity escrow.
- The main technical contribution which enables it is a compiler from a special honest-verifier zero-knowledge proof to a covert conditional key encapsulation mechanism for the same language.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830237 (1).pdf`
- `downloads/83830237 (2).pdf`
- `downloads/83830237 (3).pdf`
- `downloads/83830237 (4).pdf`
- `downloads/83830237 (5).pdf`
- `downloads/83830237.pdf`
