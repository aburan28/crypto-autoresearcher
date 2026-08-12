---
id: KN-LIT-224f2c
type: literature
title: "Quantum circuit design for the Lee-Brickell based information set decoding"
authors:
  - "Simone Perriello"
  - "Alessandro Barenghi"
  - "Gerardo Pelosi"
year: 2024
venue: "ACNS"
identifiers:
  eprint: null
  doi: "10.1007/978-3-031-61489-7_2"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-3-031-61489-7_2"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, quantum-circuit, lee-brickell, grover, resource-estimation]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A concrete **quantum circuit design** for Lee–Brickell ISD ([[KN-LIT-10be29]]),
the simplest ISD refinement above Prange. Circuit-level design, as opposed to
oracle-counting, is what turns a Grover-style speedup claim into a resource
estimate that can be compared against a gate budget.

## Key claims (as reported)
- A quantum circuit realising Lee–Brickell-based ISD.
- Positioned as a design/resource-estimation contribution rather than a new asymptotic speedup.

## Relevance to this program
This is the third entry in a group ([[KN-LIT-aa3372]], [[KN-LIT-37562e]],
[[KN-LIT-224f2c]]) by the same authors that moves quantum ISD claims from
asymptotics to **circuits with counted resources**. That progression — oracle
count, then circuit, then optimised circuit — is exactly the honesty ladder
this program's claim tiers demand (`docs/claims-and-verification.md`): a
speedup asserted at oracle level is a weaker claim than the same speedup with
a gate count attached.

Bernstein's "Grover vs. McEliece" ([[KN-LIT-4144]], already held) is the
cautionary baseline: the quantum speedup on ISD is real but far smaller than
the naive square-root intuition.

**Does not bear on the ECDLP**, where the quantum picture is Shor's algorithm,
not Grover search.

## Not verified here
citation verified against the Crossref record (DOI 10.1007/978-3-031-61489-7_2).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Gate counts, qubit counts, and the depth/width trade-off are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
