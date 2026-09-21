---
id: KN-LIT-724
type: literature
title: "Weak-Key Distinguishers for AES"
authors:
  - "Lorenzo Grassi"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/852"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/852"
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we analyze the security of AES in the case in which the whitening key is a weak key. After a systematization of the classes of weak-keys of AES, we perform an extensive analysis of weak-key distinguishers (in the single-key setting) for AES instantiated with the original key-schedule and with the new key-schedule proposed at ToSC/FSE'18.

## Key claims (as reported)
- As one of the main results, we show that (almost) all the secret-key distinguishers for round-reduced AES currently present in the literature can be set up for a higher number of rounds of AES if the whitening key is a weak-key.
- Using these results as starting point, we describe a property for 9-round AES-128 and 12-round AES-256 in the chosen-key setting with complex64 ity 2 without requiring related keys.
- These new chosen-key distinguishers  set up by exploiting a variant of the multiple-of-8 property introduced at Eurocrypt'17  improve all the AES chosen-key distinguishers in the single-key setting.
- The entire analysis has been performed using a new framework that we introduce here  called weak-key subspace trails, which is obtained by combining invariant subspaces (Crypto'11) and subspace trails (FSE'17) into a new, more powerful, attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-852.pdf`
