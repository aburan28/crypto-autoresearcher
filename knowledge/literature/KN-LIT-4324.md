---
id: KN-LIT-4324
type: literature
title: "ICEBERG : an Involutional Cipher Efficient for Block Encryption in Reconfigurable Hardware. Francois-Xavier Standaert, Gilles Piret, Gael Rouvroy"
authors:
  - "Jean-Jacques Quisquater"
  - "Jean-Didier Legat"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a fast involutional block cipher optimized for reconfigurable hardware implementations. ICEBERG uses 64-bit text blocks and 128-bit keys.

## Key claims (as reported)
- All components are involutional and allow very efficient combinations of encryption/decryption.
- Hardware implementations of ICEBERG allow to change the key at every clock cycle without any performance loss and its round keys are derived “on-the-fly” in encryption and decryption modes (no storage of round keys is needed).
- The resulting design offers better hardware efficiency than other recent 128-key-bit block ciphers.
- Resistance against side-channel cryptanalysis was also considered as a design criteria for ICEBERG.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170280 (1).pdf`
- `downloads/30170280 (2).pdf`
- `downloads/30170280.pdf`
