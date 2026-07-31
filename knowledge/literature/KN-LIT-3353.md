---
id: KN-LIT-3353
type: literature
title: "DAG-Σ: A DAG-based Sigma Protocol for Relations in CNF"
authors:
  - "Gongxian Zeng"
  - "Junzuo Lai("
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 1994, Cramer, Damgård and Schoenmakers proposed a general method to construct proofs of knowledge (PoKs), especially for k-out-of-n partial knowledge, of which relations can be expressed in disjunctive normal form (DNF). Since then, proofs of k-outof-n partial knowledge have attracted much attention and some efficient constructions have been proposed.

## Key claims (as reported)
- However, many practical scenarios require efficient PoK protocols for partial knowledge in other forms.
- In this paper, we mainly focus on PoK protocols for k-conjunctive normal form (k-CNF) relations, which have n statements and can be expressed as follows: (i) k statements constitute a clause via “OR” operations, and (ii) the relation consists of multiple clauses via “AND” operations.
- We propose an alternative Sigma protocol (called DAG-Σ protocol) for k-CNF relations (in the discrete logarithm setting), by converting these relations to directed acyclic graphs (DAGs).
- Our DAG-Σ protocol achieves less communication cost and smaller computational overhead compared with Cramer et al.’s general method.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910276 (1).pdf`
- `downloads/137910276.pdf`
