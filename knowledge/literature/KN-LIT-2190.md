---
id: KN-LIT-2190
type: literature
title: "A Practical Attack on the Fixed RC4 in the WEP Mode"
authors:
  - "Itsik Mantin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we revisit a known but ignored weakness of the RC4 keystream generator, where secret state info leaks to the generated keystream, and show that this leakage, also known as Jenkins’ correlation or the RC4 glimpse, can be used to attack RC4 in several modes. Our main result is a practical key recovery attack on RC4 when an IV modifier is concatenated to the beginning of a secret root key to generate a session key.

## Key claims (as reported)
- As opposed to the WEP attack from [FMS01] the new attack is applicable even in the case where the first 256 bytes of the keystream are thrown and its complexity grows only linearly with the length of the key.
- In an exemplifying parameter setting the attack recovers a 16-byte key in 248 steps using 217 short keystreams generated from different chosen IVs.
- A second attacked mode is when the IV succeeds the secret root key.
- We mount a key recovery attack that recovers the secret root key by analyzing a single word from 222 keystreams generated from different IVs, improving the attack from [FMS01] on this mode.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/390 (1).pdf`
- `downloads/390 (2).pdf`
- `downloads/390 (3).pdf`
- `downloads/390.pdf`
