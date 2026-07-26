---
id: KN-LIT-7554
type: literature
title: "Zero-Knowledge Sets with short proofs?"
authors:
  - "Dario Catalano"
  - "Dario Fiore"
  - "Mariagrazia Messina"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Zero Knowledge Sets, introduced by Micali, Rabin and Kilian in [17], allow a prover to commit to a secret set S in a way such that it can later prove, non interactively, statements of the form x ∈ S (or x ∈ / S), without revealing any further information (on top of what explicitly revealed by the inclusion/exclusion statements above) on S, not even its size. [5] abstracted away the Micali, Rabin and Kilian’s construction by introducing an elegant new variant of commitments that they called (trapdoor) mercurial commitments.

## Key claims (as reported)
- Using this primitive, it was shown in [5, 4] how to construct zero knowledge sets from a variety of assumptions (both general and number theoretic).
- In this paper we introduce the notion of trapdoor q-mercurial commitments (qTMCs), a notion of mercurial commitment that allows the sender to commit to an ordered sequence of exactly q messages, rather than to a single one.
- Following [17, 5] we show how to construct ZKS from qTMCs and collision resistant hash functions.
- Then, we present an efficient realization of qTMCs that is secure under the so called Strong Diffie Hellman assumption, a number theoretic conjecture recently introduced by Boneh and Boyen in [3].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650430 (1).pdf`
- `downloads/49650430 (2).pdf`
- `downloads/49650430 (3).pdf`
- `downloads/49650430.pdf`
