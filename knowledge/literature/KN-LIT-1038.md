---
id: KN-LIT-1038
type: literature
title: "Speeding-Up Parallel Computation of Large Smooth-Degree Isogeny using Precedence-Constrained Scheduling"
authors:
  - "Kittiphon Phalakarn"
  - "Vorapong Suppakitpaisarn"
  - "M. Anwar Hasan"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1103"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1103"
tags: [implementation, isogeny, pqc, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Although the supersingular isogeny Diffie-Hellman (SIDH) protocol is one of the most promising post-quantum cryptosystems, it is significantly slower than its main counterparts due to the underlying large smooth-degree isogeny computation. In this work, we address the problem of evaluating and constructing a strategy for computing the large smooth-degree isogeny in the multi-processor setting by formulating them as scheduling problems with dependencies.

## Key claims (as reported)
- The contribution of this work is two-fold.
- For the strategy evaluation, we transform strategies into task dependency graphs and apply precedence-constrained scheduling algorithms to them in order to find their costs.
- For the strategy construction, we construct strategies from smaller parts that are optimal solutions of integer programming representing the problem.
- We show via experiments that the proposed two techniques together offer more than 13% reduction in the strategy costs compared to the best current results by Hutchinson and Karabina presented at Indocrypt 2018.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1103.pdf`
