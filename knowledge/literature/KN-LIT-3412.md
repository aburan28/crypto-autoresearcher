---
id: KN-LIT-3412
type: literature
title: "Differential Analysis of the LED Block Cipher"
authors:
  - "Florian Mendel"
  - "Vincent Rijmen"
  - "Deniz Toz"
  - "Kerem Varıcı"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present a security analysis of the lightweight block cipher LED proposed by Guo et al. at CHES 2011. Since the design of LED is very similar to the Even-Mansour scheme, we first review existing attacks on this scheme and extend them to related-key and relatedkey-cipher settings before we apply them to LED.

## Key claims (as reported)
- We obtain results for 12 and 16 rounds (out of 32) for LED-64 and 16 and 24 rounds (out of 48) for LED-128.
- Furthermore, we present an observation on full LED in the related-key-cipher setting1 .
- For all these attacks we need to find good differentials for one step (4 rounds) of LED.
- Therefore, we extend the study of plateau characteristics for AES-like structures from two rounds to four rounds when the key addition is replaced with a constant addition.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580185 (1).pdf`
- `downloads/76580185 (2).pdf`
- `downloads/76580185 (3).pdf`
- `downloads/76580185.pdf`
