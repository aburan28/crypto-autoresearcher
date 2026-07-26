---
id: KN-LIT-2325
type: literature
title: "Adaptive Garbled RAM from Laconic Oblivious Transfer"
authors:
  - "Sanjam Garg"
  - "Rafail Ostrovsky"
  - "Akshayaram Srinivasan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a construction of an adaptive garbled RAM scheme. In the adaptive setting, a client first garbles a “large” persistent database which is stored on a server.

## Key claims (as reported)
- Next, the client can provide garbling of multiple adaptively and adversarially chosen RAM programs that execute and modify the stored database arbitrarily.
- The garbled database and the garbled program should reveal nothing more than the running time and the output of the computation.
- Furthermore, the sizes of the garbled database and the garbled program grow only linearly in the size of the database and the running time of the executed program respectively (up to poly logarithmic factors).
- The security of our construction is based on the assumption that laconic oblivious transfer (Cho et al., CRYPTO 2017) exists.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993267 (1).pdf`
- `downloads/10993267.pdf`
