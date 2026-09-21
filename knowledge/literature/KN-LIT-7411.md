---
id: KN-LIT-7411
type: literature
title: "Universally Composable Σ-protocols in the Global Random-Oracle Model"
authors:
  - "Anna Lysyanskaya and"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Numerous cryptographic applications require efficient noninteractive zero-knowledge proofs of knowledge (NIZKPoK) as a building block. Typically they rely on the Fiat-Shamir heuristic to do so, as security in the random-oracle model is considered good enough in practice.

## Key claims (as reported)
- However, there is a troubling disconnect between the standalone security of such a protocol and its security as part of a larger, more complex system where several protocols may be running at the same time.
- Provable security in the general universal composition model (GUC model) of Canetti et al. is the best guarantee that nothing will go wrong when a system is part of a larger whole, even when all parties share a common random oracle.
- In this paper, we prove the minimal necessary properties of generally universally composable (GUC) NIZKPoK in any global random-oracle model, and show how to achieve efficient and GUC NIZKPoK in both the restricted programmable and restricted observable (non-programmable) global random-oracle models.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470133 (1).pdf`
- `downloads/137470133.pdf`
