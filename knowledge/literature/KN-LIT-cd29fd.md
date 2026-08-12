---
id: KN-LIT-cd29fd
type: literature
title: "Quantum sieving for code-based cryptanalysis and its limitations for ISD"
authors:
  - "Lynn Engelberts"
  - "Simona Etinski"
  - "Johanna Loyer"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2024/1358"
  doi: "10.1007/s10623-024-01545-0"
  arxiv: null
  url: "https://eprint.iacr.org/2024/1358"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, sieving, quantum-sieving, negative-result, cost-model]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Studies quantum sieving for code-based cryptanalysis and — importantly — **its
limitations for ISD**. The title states a boundary, not only a speedup: the
paper is as much about where quantum sieving fails to help as where it helps.

## Key claims (as reported)
- Quantum sieving techniques are analysed in the code setting.
- The paper explicitly reports **limitations** for ISD, i.e. a scoped negative alongside any positive result.

## Relevance to this program
Held partly for its content and partly as a **disclosure model**. A paper whose
title carries its own negative scope is doing what this program requires of its
evidence records under AGENTS.md rule 4 — state the boundary of the claim in
the headline, not in a footnote. The same note is recorded for
[[KN-LIT-7669]].

Substantively it belongs with the sieving-for-codes line
([[KN-LIT-182bfb]], [[KN-LIT-01f731]], [[KN-LIT-47b29b]]): sieving transferred
from lattices to codes, and the open question is how much of the lattice
speedup survives the transfer. A recorded limitation is the useful half of that
answer.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2024/1358 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/s10623-024-01545-0).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which limitation is proven, and whether it is unconditional or conditional on a
heuristic, are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
