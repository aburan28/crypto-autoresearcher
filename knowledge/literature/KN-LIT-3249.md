---
id: KN-LIT-3249
type: literature
title: "Cryptanalysis of OCB2: Attacks on Authenticity and Confidentiality"
authors:
  - "Akiko Inoue"
  - "Tetsu Iwata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, pairing, protocol, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present practical attacks on OCB2. This mode of operation of a blockcipher was designed with the aim to provide particularly efficient and provably-secure authenticated encryption services, and since its proposal about 15 years ago it belongs to the top performers in this realm.

## Key claims (as reported)
- OCB2 was included in an ISO standard in 2009.
- An internal building block of OCB2 is the tweakable blockcipher obtained by operating a regular blockcipher in XEX∗ mode.
- The latter provides security only when evaluated in accordance with certain technical restrictions that, as we note, are not always respected by OCB2.
- This leads to devastating attacks against OCB2’s security promises: We develop a range of very practical attacks that, amongst others, demonstrate universal forgeries and full plaintext recovery.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940339 (1).pdf`
- `downloads/116940339.pdf`
