---
id: KN-LIT-4055
type: literature
title: "Garbling, Stacked and Staggered Faster k-out-of-n Garbled Function Evaluation"
authors:
  - "David Heath"
  - "Vladimir Kolesnikov"
  - "Stanislav Peceny"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Stacked Garbling (SGC) is a Garbled Circuit (GC) improvement that efficiently and securely evaluates programs with conditional branching. SGC reduces bandwidth consumption such that communication is proportional to the size of the single longest program execution path, rather than to the size of the entire program.

## Key claims (as reported)
- Crucially, the parties expend increased computational effort compared to classic GC.
- Motivated by procuring a subset in a menu of computational services or tasks, we consider GC evaluation of k-out-of-n branches, whose indices are known (or eventually revealed) to the GC evaluator E.
- Our stack-and-stagger technique amortizes GC computation in this setting.
- We retain the communication advantage of SGC, while significantly improving computation and wall-clock time.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900101 (1).pdf`
- `downloads/130900101.pdf`
