---
id: KN-LIT-7557
type: literature
title: "ZMAC: A Fast Tweakable Block Cipher Mode for Highly Secure Message Authentication"
authors:
  - "Tetsu Iwata"
  - "Kazuhiko Minematsu"
  - "Thomas Peyrin"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new mode of operation called ZMAC allowing to construct a (stateless and deterministic) message authentication code (MAC) from a tweakable block cipher (TBC). When using a TBC with n-bit blocks and t-bit tweaks, our construction provides security (as a variable-input-length PRF) beyond the birthday bound with respect to the block-length n and allows to process n + t bits of inputs per TBC call.

## Key claims (as reported)
- In comparison, previous TBC-based modes such as PMAC1, the TBC-based generalization of the seminal PMAC mode (Black and Rogaway, EUROCRYPT 2002) or PMAC_TBC1k (Naito, ProvSec 2015) only process n bits of input per TBC call.
- Since an n-bit block, t-bit tweak TBC can process at most n + t bits of input per call, the efficiency of our construction is essentially optimal, while achieving beyond-birthdaybound security.
- The ZMAC mode is fully parallelizable and can be directly instantiated with several concrete TBC proposals, such as Deoxys and SKINNY.
- We also use ZMAC to construct a stateless and deterministic Authenticated Encryption scheme called ZAE which is very efficient and secure beyond the birthday bound.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401297 (1).pdf`
- `downloads/10401297.pdf`
