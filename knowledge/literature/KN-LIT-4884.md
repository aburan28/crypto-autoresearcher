---
id: KN-LIT-4884
type: literature
title: "Meet-in-the-Middle Attacks on Generic Feistel Constructions"
authors:
  - "Jian Guo"
  - "Jérémy Jean"
  - "Ivica Nikolić"
  - "Yu Sasaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show key recovery attacks on generic balanced Feistel ciphers. The analysis is based on the meet-in-the-middle technique and exploits truncated differentials that are present in the ciphers due to the Feistel construction.

## Key claims (as reported)
- Depending on the type of round function, we differentiate and show attacks on two types of Feistels.
- For the first type, which is the most general Feistel, we show a 5-round distinguisher (based on a truncated differential), which allows to launch 6-round and 10-round attacks, for single-key and double-key sizes, respectively.
- For the second type, we assume the round function follows the SPN structure with a linear layer P that has a maximal branch number, and based on a 7-round distinguisher, we show attacks that reach up to 14 rounds.
- Our attacks outperform all the known attacks for any key sizes, have been experimentally verified (implemented on a regular PC), and provide new lower bounds on the number of rounds required to achieve a practical and a secure Feistel.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730238 (1).pdf`
- `downloads/88730238 (2).pdf`
- `downloads/88730238 (3).pdf`
- `downloads/88730238.pdf`
