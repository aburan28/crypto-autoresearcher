---
id: KN-LIT-1015
type: literature
title: "On the Hardness of the Finite Field Isomorphism Problem"
authors:
  - "Dipayan Das"
  - "Antoine Joux"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/998"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/998"
tags: [complexity-theory, cryptanalysis, fhe, finite-field, lattice, pairing, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The finite field isomorphism (FFI) problem was introduced in PKC’18, as an alternative to average-case lattice problems (like LWE, SIS, or NTRU). As an application, the same paper used the FFI problem to construct a fully homomorphic encryption scheme.

## Key claims (as reported)
- In this work, we prove that the decision variant of the FFI problem can be solved in polynomial time for any field characteristics q = Ω(βn2 ), where q, β, n parametrize the FFI problem.
- Then we use our result from the FFI distinguisher to propose polynomial-time attacks on the semantic security of the fully homomorphic encryption scheme.
- Furthermore, for completeness, we also study the search variant of the FFI problem and show how to state it as a q-ary lattice problem, which was previously unknown.
- As a result, we can solve the search problem for some previously intractable parameters using a simple lattice reduction approach.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004053 (1).pdf`
- `downloads/14004053.pdf`
- `downloads/2022-998.pdf`
