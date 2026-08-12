---
id: KN-LIT-5621
type: literature
title: "One-Message Zero Knowledge and Non-Malleable Commitments"
authors:
  - "Nir Bitansky"
  - "Huijia Lin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new notion of one-message zero-knowledge (1ZK) arguments that satisfy a weak soundness guarantee — the number of false statements that a polynomial-time non-uniform adversary can convince the verifier to accept is not much larger than the size of its non-uniform advice. The zero-knowledge guarantee is given by a simulator that runs in (mildly) super-polynomial time.

## Key claims (as reported)
- We construct such 1ZK arguments based on the notion of multi-collision-resistant keyless hash functions, recently introduced by Bitansky, Kalai, and Paneth (STOC 2018).
- Relying on the constructed 1ZK arguments, subexponentially-secure timelock puzzles, and other standard assumptions, we construct one-message fullyconcurrent non-malleable commitments.
- This is the first construction that is based on assumptions that do not already incorporate non-malleability, as well as the first based on (subexponentially) falsifiable assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239144 (1).pdf`
- `downloads/11239144.pdf`
