---
id: KN-LIT-6123
type: literature
title: "Random Oracles in a Quantum World Dan Boneh1 , Özgür Dagdelen2 , Marc Fischlin2"
authors:
  - "Anja Lehmann"
  - "Christian Schaffner"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, lattice, pairing, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The interest in post-quantum cryptography — classical systems that remain secure in the presence of a quantum adversary — has generated elegant proposals for new cryptosystems. Some of these systems are set in the random oracle model and are proven secure relative to adversaries that have classical access to the random oracle.

## Key claims (as reported)
- We argue that to prove post-quantum security one needs to prove security in the quantum-accessible random oracle model where the adversary can query the random oracle with quantum state.
- We begin by separating the classical and quantum-accessible random oracle models by presenting a scheme that is secure when the adversary is given classical access to the random oracle, but is insecure when the adversary can make quantum oracle queries.
- We then set out to develop generic conditions under which a classical random oracle proof implies security in the quantum-accessible random oracle model.
- We introduce the concept of a history-free reduction which is a category of classical random oracle reductions that basically determine oracle answers independently of the history of previous queries, and we prove that such reductions imply security in the quantum model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730041 (1).pdf`
- `downloads/70730041 (2).pdf`
- `downloads/70730041 (3).pdf`
- `downloads/70730041.pdf`
