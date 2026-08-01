---
id: KN-LIT-2336
type: literature
title: "Adaptive Succinct Garbled RAM or: How To Delegate Your Database?"
authors:
  - "Ran Canetti"
  - "Yilei Chen"
  - "Justin Holmgren"
  - "Mariana Raykova"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how to garble a large persistent database and then garble, one by one, a sequence of adaptively and adversarially chosen RAM programs that query and modify the database in arbitrary ways. The garbled database and programs reveal only the outputs of the programs when run in sequence on the database.

## Key claims (as reported)
- Still, the runtime, space requirements and description size of the garbled programs are proportional only to those of the plaintext programs and the security parameter.
- We assume indistinguishability obfuscation for circuits and somewhatregular collision-resistant hash functions.
- In contrast, all previous garbling schemes with persistent data were shown secure only in the static setting where all the programs are known in advance.
- As an immediate application, we give the first scheme for efficiently outsourcing a large database and computations on the database to an untrusted server, then delegating computations on this database, where these computations may update the database.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/99850180 (1).pdf`
- `downloads/99850180.pdf`
