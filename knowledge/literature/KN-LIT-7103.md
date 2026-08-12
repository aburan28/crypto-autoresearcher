---
id: KN-LIT-7103
type: literature
title: "Threshold and Proactive Pseudo-Random Permutations"
authors:
  - "Yevgeniy Dodis⋆"
  - "Aleksandr Yampolskiy⋆⋆"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a reasonably efficient threshold and proactive pseudo-random permutation (PRP). Our protocol needs only O(1) communication rounds.

## Key claims (as reported)
- It tolerates up to (n − 1)/2 of n dishonest servers in the semi-honest environment.
- Many protocols that use PRPs (e.g., a CBC block cipher mode) can now be translated into the distributed setting.
- Our main technique for constructing invertible threshold PRPs is a distributed Luby-Rackoff construction where both the secret keys and the input are shared among the servers.
- We also present protocols for obliviously computing pseudo-random functions by Naor-Reingold [41] and Dodis-Yampolskiy [25] with shared input and keys.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/38760546 (1).pdf`
- `downloads/38760546 (2).pdf`
- `downloads/38760546 (3).pdf`
- `downloads/38760546.pdf`
