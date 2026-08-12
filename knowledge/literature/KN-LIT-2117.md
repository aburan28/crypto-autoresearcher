---
id: KN-LIT-2117
type: literature
title: "A Modular Framework for Building Variable-Input-Length Tweakable Ciphers"
authors:
  - "Thomas Shrimpton"
  - "R. Seth Terashima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the Protected-IV construction (PIV) a simple, modular method for building variable-input-length tweakable ciphers. At our level of abstraction, many interesting design opportunities surface.

## Key claims (as reported)
- For example, an obvious pathway to building beyond birthday-bound secure tweakable ciphers with performance competitive with existing birthday-bound-limited constructions.
- As part of our design space exploration, we give two fully instantiated PIV constructions, TCT1 and TCT2 ; the latter is fast and has beyond birthday-bound security, the former is faster and has birthday-bound security.
- Finally, we consider a generic method for turning a VIL tweakable cipher (like PIV) into an authenticated encryption scheme that admits associated data, can withstand nonce-misuse, and allows for multiple decryption error messages.
- Thus, the method offers robustness even in the face of certain sidechannels, and common implementation mistakes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82710279 (1).pdf`
- `downloads/82710279 (2).pdf`
- `downloads/82710279 (3).pdf`
- `downloads/82710279.pdf`
