---
id: KN-LIT-6809
type: literature
title: "Stealing Keys from PCs using a Radio: Cheap Electromagnetic Attacks on Windowed Exponentiation"
authors:
  - "Daniel Genkin"
  - "Lev Pachmanov"
  - "Itamar Pipman"
  - "Eran Tromer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, lattice, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present new side-channel attacks on RSA and ElGamal implementations that use sliding-window or fixed-window (m-ary) modular exponentiation. The attacks extract decryption keys using a very low measurement bandwidth (a frequency band of less than 100 kHz around a carrier under 2 MHz) even when attacking multi-GHz CPUs.

## Key claims (as reported)
- We demonstrate the attacks’ feasibility by extracting keys from GnuPG (unmodified ElGamal and non-blinded RSA), within seconds, using a nonintrusive measurement of electromagnetic emanations from laptop computers.
- The measurement equipment is cheap and compact, uses readily-available components (a Software Defined Radio USB dongle or a consumer-grade radio receiver), and can operate untethered while concealed, e.g., inside pita bread.
- The attacks use a few non-adaptive chosen ciphertexts, crafted so that whenever the decryption routine encounters particular bit patterns in the secret key, intermediate values occur with a special structure that causes observable fluctuations in the electromagnetic field.
- Through suitable signal processing and cryptanalysis, the bit patterns and eventually the whole secret key are recovered.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930202 (1).pdf`
- `downloads/92930202.pdf`
