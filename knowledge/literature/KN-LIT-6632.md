---
id: KN-LIT-6632
type: literature
title: "Signature Schemes with Bounded Leakage Resilience"
authors:
  - "Jonathan Katz⋆"
  - "Vinod Vaikuntanathan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, side-channel, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A leakage-resilient cryptosystem remains secure even if arbitrary, but bounded, information about the secret key (and possibly other internal state information) is leaked to an adversary. Denote the length of the secret key by n.

## Key claims (as reported)
- We show: – A full-fledged signature scheme tolerating leakage of n − nǫ bits of information about the secret key (for any constant ǫ > 0), based on general assumptions. – A one-time signature scheme, based on the minimal assumption of one-way functions, tolerating leakage of ( 41 − ǫ) · n bits of information about the signer’s entire state. – A more efficient one-time signature scheme, that can be based on several specific assumptions, tolerating leakage of ( 21 − ǫ) · n bits of information about the signer’s entire state.
- The latter two constructions extend to give leakage-resilient t-time signature schemes.
- All the above constructions are in the standard model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120700 (1).pdf`
- `downloads/59120700 (2).pdf`
- `downloads/59120700 (3).pdf`
- `downloads/59120700.pdf`
