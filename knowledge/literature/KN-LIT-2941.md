---
id: KN-LIT-2941
type: literature
title: "Collision Attacks on AES-based MAC: Alpha-MAC"
authors:
  - "Alex Biryukov"
  - "Andrey Bogdanov"
  - "Dmitry Khovratovich"
  - "Timo Kasper"
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
Message Authentication Code construction Alred and its AES-based instance Alpha-MAC were introduced by Daemen and Rijmen in 2005. We show that under certain assumptions about its implementation (namely that keyed parts are perfectly protected against side-channel attacks but bulk hashing rounds are not) one can efficiently attack this function.

## Key claims (as reported)
- We propose a side-channel collision attack on this MAC recovering its internal state just after 29 measurements in the known-message scenario which is to be compared to 40 measurements required by collision attacks on AES in the chosen-plaintext scenario.
- Having recovered the internal state, we mount a selective forgery attack using new 4 to 1 round collisions working with negligible memory and time complexity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270166 (1).pdf`
- `downloads/47270166 (2).pdf`
- `downloads/47270166 (3).pdf`
- `downloads/47270166.pdf`
