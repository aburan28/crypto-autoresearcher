---
id: KN-LIT-2924
type: literature
title: "CLOC: Authenticated Encryption for Short Input"
authors:
  - "Tetsu Iwata"
  - "Kazuhiko Minematsu"
  - "Jian Guo"
  - "Sumio Morioka"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We define and analyze the security of a blockcipher mode of operation, CLOC, for provably secure authenticated encryption with associated data. The design of CLOC aims at optimizing previous schemes, CCM, EAX, and EAX-prime, in terms of the implementation overhead beyond the blockcipher, the precomputation complexity, and the memory requirement.

## Key claims (as reported)
- With these features, CLOC is suitable for handling short input data, say 16 bytes, without needing precomputation nor large memory.
- This property is especially beneficial to small microprocessors, where the word size is typically 8 bits or 16 bits, and there are significant restrictions in the size and the number of registers.
- CLOC uses a variant of CFB mode in its encryption part and a variant of CBC MAC in the authentication part.
- We introduce various design techniques in order to achieve the above mentioned design goals.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400186 (1).pdf`
- `downloads/85400186 (2).pdf`
- `downloads/85400186 (3).pdf`
- `downloads/85400186.pdf`
