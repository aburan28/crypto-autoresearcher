---
id: KN-LIT-072f64
type: literature
title: "Reducing the number of qubits in quantum information set decoding"
authors:
  - "Clémence Chevignard"
  - "Pierre-Alain Fouque"
  - "André Schrottenloher"
year: 2024
venue: "Asiacrypt"
identifiers:
  eprint: "iacr:2024/907"
  doi: "10.1007/978-981-96-0944-4_10"
  arxiv: null
  url: "https://eprint.iacr.org/2024/907"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, qubit-count, resource-estimation, grover]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Reduces the **number of qubits** required for quantum information set decoding.
Qubit count, rather than gate count, is the binding constraint on near- and
mid-term quantum hardware, so a memory-side reduction can matter more for
feasibility than a time-side speedup.

## Key claims (as reported)
- A quantum ISD algorithm using fewer qubits than prior constructions.
- The contribution is on the space axis; the paper is framed as reducing qubits rather than reducing time.

## Relevance to this program
Same methodological point as [[KN-LIT-224f2c]] and [[KN-LIT-b8a8be]]: the
quantum-attack literature on codes has moved to costing **space** honestly, and
a claim stated only in query complexity hides the resource that actually binds.

This program's own cost claims are held to the same standard — an evidence
record that reports time and omits memory is incomplete under rule 4.

**Does not bear on the ECDLP.** Note that a corpus entry with a near-identical
title, [[KN-LIT-1845]] ("Reducing the Number of Qubits in Quantum Discrete
Logarithms on Elliptic Curves"), is a *different* paper on the curve side; the
two were separated by hand during this sweep's dedup pass.

## Not verified here
Citation verified against the IACR ePrint record for report 2024/907 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-981-96-0944-4_10).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The qubit count achieved and what it costs in time are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
