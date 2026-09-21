---
id: KN-LIT-5277
type: literature
title: "Oblivious RAM with O((log N )3 ) Worst-Case Cost"
authors:
  - "Elaine Shi"
  - "T-H. Hubert Chan"
  - "Emil Stefanov"
  - "Mingfei Li"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Oblivious RAM is a useful primitive that allows a client to hide its data access patterns from an untrusted server in storage outsourcing applications. Until recently, most prior works on Oblivious RAM aim to optimize its amortized cost, while suffering from linear or even higher worst-case cost.

## Key claims (as reported)
- Such poor worstcase behavior renders these schemes impractical in realistic settings, since a data access request can occasionally be blocked waiting for an unreasonably large number of operations to complete.
- This paper proposes novel Oblivious RAM constructions that achieves poly-logarithmic worst-case cost, while consuming constant client-side storage.
- To achieve the desired worst-case asymptotic performance, we propose a novel technique in which we organize the O-RAM storage into a binary tree over data buckets, while moving data blocks obliviously along tree edges.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730197 (1).pdf`
- `downloads/70730197 (2).pdf`
- `downloads/70730197 (3).pdf`
- `downloads/70730197.pdf`
