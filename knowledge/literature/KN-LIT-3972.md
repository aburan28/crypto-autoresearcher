---
id: KN-LIT-3972
type: literature
title: "FSBday: Implementing Wagner’s generalized birthday attack against the SHA-3 round-1 candidate FSB"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Ruben Niederhagen"
  - "Christiane Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, hyperelliptic, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper applies generalized birthday attacks to the FSB compression function, and shows how to adapt the attacks so that they run in far less memory. In particular, this paper presents details of a parallel implementation attacking FSB48 , a scaled-down version of FSB proposed by the FSB submitters.

## Key claims (as reported)
- The implementation runs on a cluster of 8 PCs, each with only 8GB of RAM and 700GB of disk.
- This situation is very interesting for estimating the security of systems against distributed attacks using contributed off-the-shelf PCs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/fsbday-20091003.pdf`
