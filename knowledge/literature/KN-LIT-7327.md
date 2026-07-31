---
id: KN-LIT-7327
type: literature
title: "TWORAM: Efficient Oblivious RAM in Two Rounds with Applications to Searchable Encryption"
authors:
  - "Sanjam Garg"
  - "Payman Mohassel"
  - "Charalampos Papamanthou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present TWORAM, an asymptotically efficient oblivious RAM (ORAM) protocol providing oblivious access (read and write) of a memory index y in exactly two rounds: The client prepares an encrypted query encapsulating y and sends it to the server. The server accesses memory M obliviously and returns encrypted information containing the desired value M[y].

## Key claims (as reported)
- The cost of TWORAM is only a multiplicative factor of security parameter higher than the tree-based ORAM schemes such as the path ORAM scheme of Stefanov et al.
- TWORAM gives rise to interesting applications, and in particular to a 4-round symmetric searchable encryption scheme where search is sublinear in the worst case and the search pattern is not leaked—the access pattern can also be concealed assuming the documents are stored in the obliviously accessed memory M.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160545 (1).pdf`
- `downloads/98160545.pdf`
