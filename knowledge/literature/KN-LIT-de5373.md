---
id: KN-LIT-de5373
type: literature
title: "Security analysis for BIKE, Classic McEliece and HQC against the quantum ISD algorithms"
authors:
  - "Asuka Wakasugi"
  - "Mitsuru Tada"
year: 2022
venue: null
identifiers:
  eprint: "iacr:2022/1771"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1771"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, classic-mceliece, bike, hqc, nist-pqc]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Security analysis of BIKE, Classic McEliece and HQC **against quantum ISD
algorithms** — applying the quantum ISD line ([[KN-LIT-80202e]],
[[KN-LIT-f7d7dd]]) to the NIST candidates' actual parameter sets.

## Key claims (as reported)
- Quantum ISD costs are estimated for the three code-based NIST candidates.
- Stated against the candidates' parameter sets rather than asymptotically.

## Relevance to this program
The applied counterpart to the quantum-ISD entries in this sweep. Its
significance for this program is the standing conclusion of that literature,
first made precise in Bernstein's "Grover vs. McEliece" ([[KN-LIT-4144]]):
**the quantum speedup against code-based schemes is modest and does not
approach the naive square root**, because Grover applies only to part of the
computation and its iterations are expensive.

This is the strongest available caution against a quantum-cost claim asserted
by analogy rather than computed — a caution that applies to any quantum
comparison this program might make about the ECDLP.

**Does not bear on the ECDLP directly**, where the relevant quantum algorithm
is Shor's and the situation is categorically different.

## Not verified here
Citation verified against the IACR ePrint record for report 2022/1771 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The estimated quantum security levels and the cost model used are NOT recorded
here. Note: this paper is distinct from Li–Wang [[KN-LIT-5677ae]], which covers
the same three schemes in the *low-memory classical* setting; the two were
separated during dedup after an automated title match confused them.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
