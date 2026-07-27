---
id: KN-LIT-6110
type: literature
title: "Quark: a lightweight hash"
authors:
  - "Jean-Philippe Aumasson"
  - "Luca Henzen"
  - "Willi Meier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The need for lightweight cryptographic hash functions has been repeatedly expressed by application designers, notably for implementing RFID protocols. However not many designs are available, and the ongoing SHA-3 Competition probably won’t help, as it concerns general-purpose designs and focuses on software performance.

## Key claims (as reported)
- In this paper, we thus propose a novel design philosophy for lightweight hash functions, based on a single security level and on the sponge construction, to minimize memory requirements.
- Inspired by the lightweight ciphers Grain and KATAN, we present the hash function family Quark, composed of the three instances u-Quark, d-Quark, and t-Quark.
- Hardware benchmarks show that Quark compares well to previous lightweight hashes.
- For example, our lightest instance u-Quark conjecturally provides at least 64-bit security against all attacks (collisions, multicollisions, distinguishers, etc.), fits in 1379 gate-equivalents, and consumes in average 2.44 μW at 100 kHz in 0.18 μm ASIC.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250001 (1).pdf`
- `downloads/62250001 (2).pdf`
- `downloads/62250001 (3).pdf`
- `downloads/62250001.pdf`
