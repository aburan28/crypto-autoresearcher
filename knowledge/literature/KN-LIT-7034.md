---
id: KN-LIT-7034
type: literature
title: "The PHOTON Family of Lightweight Hash Functions"
authors:
  - "Jian Guo"
  - "Thomas Peyrin"
  - "Axel Poschmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
RFID security is currently one of the major challenges cryptography has to face, often solved by protocols assuming that an ontag hash function is available. In this article we present the PHOTON lightweight hash-function family, available in many different flavors and suitable for extremely constrained devices such as passive RFID tags.

## Key claims (as reported)
- Our proposal uses a sponge-like construction as domain extension algorithm and an AES-like primitive as internal unkeyed permutation.
- This allows us to obtain the most compact hash function known so far (about 1120 GE for 64-bit collision resistance security), reaching areas very close to the theoretical optimum (derived from the minimal internal state memory size).
- Moreover, the speed achieved by PHOTON also compares quite favorably to its competitors.
- This is mostly due to the fact that unlike for previously proposed schemes, our proposal is very simple to analyze and one can derive tight AES-like bounds on the number of active Sboxes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/68410219 (1).pdf`
- `downloads/68410219 (2).pdf`
- `downloads/68410219 (3).pdf`
- `downloads/68410219.pdf`
