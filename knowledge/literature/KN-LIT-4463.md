---
id: KN-LIT-4463
type: literature
title: "Improving the Security of Quantum Protocols via Commit-and-Open Ivan Damgård1"
authors:
  - "Louis Salvail"
  - "Christian Schaffner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider two-party quantum protocols starting with a transmission of some random BB84 qubits followed by classical messages. We show a general “compiler” improving the security of such protocols: if the original protocol is secure against an “almost honest” adversary, then the compiled protocol is secure against an arbitrary computationally bounded (quantum) adversary.

## Key claims (as reported)
- The compilation preserves the number of qubits sent and the number of rounds up to a constant factor.
- The compiler also preserves security in the bounded-quantum-storage model (BQSM), so if the original protocol was BQSM-secure, the compiled protocol can only be broken by an adversary who has large quantum memory and large computing power.
- This is in contrast to known BQSM-secure protocols, where security breaks down completely if the adversary has larger quantum memory than expected.
- We show how our technique can be applied to quantum identification and oblivious transfer protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770403 (1).pdf`
- `downloads/56770403 (2).pdf`
- `downloads/56770403 (3).pdf`
- `downloads/56770403 (4).pdf`
- `downloads/56770403.pdf`
