---
id: KN-LIT-4191
type: literature
title: "Hiding Secrecy Leakage in Leaky Helper Data"
authors:
  - "Matthias Hiller"
  - "Aysun Gurur Önalan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, implementation, mov-fr, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
PUFs provide cryptographic keys for embedded systems without dedicated secure memory. Practical PUF implementations often show a bias in the PUF responses, which leads to secrecy leakage in many key derivation constructions.

## Key claims (as reported)
- However, previously proposed mitigation techniques remove the bias at the expense of discarding large numbers of PUF response bits.
- Instead of removing the bias from the input sequence, this work reduces the secrecy leakage through the helper data.
- We apply the concept of wiretap coset coding to add randomness to the helper data such that an attacker cannot isolate significant information about the key anymore.
- Examples demonstrate the effectiveness of coset coding for different bias parameters by computing the exact leakage for short code lengths and applying upper bounds for larger code lengths.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529150 (1).pdf`
- `downloads/10529150.pdf`
