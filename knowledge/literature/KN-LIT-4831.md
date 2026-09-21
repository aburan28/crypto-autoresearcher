---
id: KN-LIT-4831
type: literature
title: "MacORAMa: Optimal Oblivious RAM with Integrity"
authors:
  - "Surya Mathialagan"
  - "Neekon Vafa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAM (ORAM), introduced by Goldreich and Ostrovsky (J. ACM ‘96), is a primitive that allows a client to perform RAM computations on an external database without revealing any information through the access pattern.

## Key claims (as reported)
- For a database of size N , well-known lower bounds show that a multiplicative overhead of Ω(log N ) in the number of RAM queries is necessary assuming O(1) client storage.
- A long sequence of works culminated in the asymptotically optimal construction of Asharov, Komargodski, Lin, and Shi (CRYPTO ‘21) with O(log N ) worst-case overhead and O(1) client storage.
- However, this optimal ORAM is known to be secure only in the honest-but-curious setting, where an adversary is allowed to observe the access patterns but not modify the contents of the database.
- In the malicious setting, where an adversary is additionally allowed to tamper with the database, this construction and many others in fact become insecure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850072 (1).pdf`
- `downloads/140850072.pdf`
