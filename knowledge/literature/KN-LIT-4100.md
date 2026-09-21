---
id: KN-LIT-4100
type: literature
title: "Generic Security of the SAFE API and Its Applications"
authors:
  - "Dmitry Khovratovich"
  - "Mario Marhuenda Beltrán"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, prime-field, provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide security foundations for SAFE, a recently introduced API framework for sponge-based hash functions tailored to prime-field-based protocols. SAFE aims to provide a robust and foolproof interface, has been implemented in the Neptune hash framework and some zero-knowledge proof projects, but despite its usability and applicability it currently lacks any security proof.

## Key claims (as reported)
- Such a proof would not be straightforward as SAFE abuses the inner part of the sponge and fills it with protocol-specific data.
- In this work we identify the SAFECore as versatile variant sponge construction underlying SAFE, we prove indifferentiability of SAFECore for all (binary and prime) fields up to around |Fp |c/2 queries, where Fp is the underlying field and c the capacity, and we apply this security result to various use cases.
- We show that the SAFE-based protocols of plain hashing, authenticated encryption, verifiable computation, noninteractive proofs, and commitment schemes are secure against a wide class of adversaries, including those dealing with multiple invocations of a sponge in a single application.
- Our results pave the way of using SAFE with the full taxonomy of hash functions, including SNARK-, lattice-, and x86-friendly hashes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438312 (1).pdf`
- `downloads/14438312.pdf`
