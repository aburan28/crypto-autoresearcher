---
id: KN-LIT-5180
type: literature
title: "Non-Interactive Composition of Sigma-Protocols via Share-then-Hash"
authors:
  - "Masayuki Abe"
  - "Miguel Ambrona"
  - "Andrej Bogdanov"
  - "Miyako Ohkubo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proofs of partial knowledge demonstrate the possession of certain subsets of witnesses for a given collection of statements x1 , . . . , xn . Cramer, Damgård, and Schoenmakers (CDS), built proofs of partial knowledge, given “atomic” protocols for individual statements xi , by having the prover randomly secret share the verifier’s challenge and using the shares as challenges for the atomic protocols.

## Key claims (as reported)
- This simple and highly-influential transformation has been used in numerous applications, ranging from anonymous credentials to ring signatures.
- We consider what happens if, instead of using the shares directly as challenges, the prover first hashes them.
- We show that this elementary enhancement can result in significant benefits: • the proof contains a single atomic transcript per statement x , i • it suffices that the atomic protocols are κ-special sound for κ ≥ 2, • when compiled to a signature scheme using the Fiat-Shamir heuristic, its unforgeability can be proved in the non-programmable random oracle model.
- None of the above features is satisfied by the CDS transformation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491376 (1).pdf`
- `downloads/12491376.pdf`
