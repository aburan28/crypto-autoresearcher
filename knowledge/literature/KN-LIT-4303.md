---
id: KN-LIT-4303
type: literature
title: "How To Securely Outsource Cryptographic Computations"
authors:
  - "Susan Hohenberger"
  - "Anna Lysyanskaya"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We address the problem of using untrusted (potentially malicious) cryptographic helpers. We provide a formal security definition for securely outsourcing computations from a computationally limited device to an untrusted helper.

## Key claims (as reported)
- In our model, the adversarial environment writes the software for the helper, but then does not have direct communication with it once the device starts relying on it.
- In addition to security, we also provide a framework for quantifying the efficiency and checkability of an outsourcing implementation.
- We present two practical outsource-secure schemes.
- Specifically, we show how to securely outsource modular exponentiation, which presents the computational bottleneck in most publickey cryptography on computationally limited devices.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_265 (1).pdf`
- `downloads/3378_265 (2).pdf`
- `downloads/3378_265 (3).pdf`
- `downloads/3378_265.pdf`
