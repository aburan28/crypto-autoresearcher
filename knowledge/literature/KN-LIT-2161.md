---
id: KN-LIT-2161
type: literature
title: "A New Simple Technique to Bootstrap Various"
authors:
  - "Lattice Zero-Knowledge Proofs to QROM"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many of the recent advanced lattice-based Σ-/public-coin honest verifier (HVZK) interactive protocols based on the techniques developed by Lyubashevsky (Asiacrypt’09, Eurocrypt’12) can be transformed into a non-interactive zero-knowledge (NIZK) proof in the random oracle model (ROM) using the Fiat-Shamir transform. Unfortunately, although they are known to be secure in the classical ROM, existing proof techniques are incapable of proving them secure in the quantum ROM (QROM).

## Key claims (as reported)
- Alternatively, while we could instead rely on the Unruh transform (Eurocrypt’15), the resulting QROM secure NIZK will incur a large overhead compared to the underlying interactive protocol.
- In this paper, we present a new simple semi-generic transform that compiles many existing lattice-based Σ-/public-coin HVZK interactive protocols into QROM secure NIZKs.
- Our transform builds on a new primitive called extractable linear homomorphic commitment protocol.
- The resulting NIZK has several appealing features: it is not only a proof of knowledge but also straight-line extractable; the proof overhead is smaller compared to the Unruh transform; it enjoys a relatively small reduction loss; and it requires minimal background on quantum computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826193 (1).pdf`
- `downloads/12826193.pdf`
