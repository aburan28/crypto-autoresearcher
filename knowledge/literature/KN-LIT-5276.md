---
id: KN-LIT-5276
type: literature
title: "Oblivious RAM Revisited"
authors:
  - "Benny Pinkas"
  - "Tzachy Reinman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We reinvestigate the oblivious RAM concept introduced by Goldreich and Ostrovsky, which enables a client, that can store locally only a constant amount of data, to store remotely n data items, and access them while hiding the identities of the items which are being accessed. Oblivious RAM is often cited as a powerful tool, but is also commonly considered to be impractical due to its overhead, which is asymptotically efficient but is quite high.

## Key claims (as reported)
- We redesign the oblivious RAM protocol using modern tools, namely Cuckoo hashing and a new oblivious sorting algorithm.
- The resulting protocol uses only O(n) external memory, and replaces each data request by only O(log2 n) requests.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230495 (1).pdf`
- `downloads/62230495 (2).pdf`
- `downloads/62230495 (3).pdf`
- `downloads/62230495.pdf`
