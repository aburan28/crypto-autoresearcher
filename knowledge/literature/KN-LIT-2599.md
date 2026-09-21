---
id: KN-LIT-2599
type: literature
title: "Asynchronous Byzantine Agreement with Subquadratic Communication"
authors:
  - "Erica Blum"
  - "Jonathan Katz⋆"
  - "Chen-Da Liu-Zhang"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Understanding the communication complexity of Byzantine agreement (BA) is a fundamental problem in distributed computing. In particular, for protocols involving a large number of parties (as in, e.g., the context of blockchain protocols), it is important to understand the dependence of the communication on the number of parties n.

## Key claims (as reported)
- Although adaptively secure BA protocols with o(n2 ) communication are known in the synchronous and partially synchronous settings, no such protocols are known in the fully asynchronous case.
- We show asynchronous BA protocols with (expected) subquadratic communication complexity tolerating an adaptive adversary who can corrupt f < (1 − ε)n/3 of the parties (for any ε > 0).
- One protocol assumes initial setup done by a trusted dealer, after which an unbounded number of BA executions can be run; alternately, we can achieve subquadratic amortized communication with no prior setup.
- We also show that some form of setup is needed for (non-amortized) subquadratic BA tolerating Θ(n) corrupted parties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550219 (1).pdf`
- `downloads/12550219.pdf`
