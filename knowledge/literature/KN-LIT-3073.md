---
id: KN-LIT-3073
type: literature
title: "Concrete quantum cryptanalysis of binary elliptic curves"
authors:
  - "Gustavo Banegas"
  - "Daniel J. Bernstein"
  - "Iggy van Hoof"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, dlp, elliptic-curve, factoring, hyperelliptic, pairing, prime-field, protocol, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper analyzes and optimizes quantum circuits for computing discrete logarithms on binary elliptic curves, including reversible circuits for fixed-base-point scalar multiplication and the full stack of relevant subroutines. The main optimization target is the size of the quantum computer, i.e., the number of logical qubits required, as this appears to be the main obstacle to implementing Shor’s polynomial-time discrete-logarithm algorithm.

## Key claims (as reported)
- The secondary optimization target is the number of logical Toffoli gates.
- For an elliptic curve over a field of 2n elements, this paper reduces the number of qubits to 7n + blog2 (n)c + 9.
- At the same time this paper reduces the number of Toffoli gates to 48n3 + 8nlog2 (3)+1 + 352n2 log2 (n) + 512n2 + O(nlog2 (3) ) with doubleand-add scalar multiplication, and a logarithmic factor smaller with fixed-window scalar multiplication.
- The number of CNOT gates is also O(n3 ).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/binecc-20201016.pdf`
