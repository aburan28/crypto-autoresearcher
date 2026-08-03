---
id: KN-LIT-0138f3
type: literature
title: "Message-recovery horizontal correlation attack on Classic McEliece"
authors:
  - "Brice Colombier"
  - "Vincent Grosso"
  - "Pierre-Louis Cayrel"
  - "Vlad-Florin Drăgoi"
year: 2025
venue: "COSADE"
identifiers:
  eprint: "iacr:2023/546"
  doi: "10.1007/978-3-032-01405-4_4"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/978-3-032-01405-4_4"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, horizontal-attack, correlation, message-recovery, single-trace]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **horizontal correlation** attack recovering the *message* (not the key) from
Classic McEliece. Horizontal attacks extract many samples from a **single**
trace by exploiting repeated operations within one execution, rather than
correlating across many executions.

## Key claims (as reported)
- Message recovery from horizontal correlation analysis.
- Single-trace in character — the repetition exploited is within one execution.

## Relevance to this program
The single-trace property is what matters. Countermeasures premised on limiting
the number of observed operations — key rotation, session limits, ephemeral use
— **do not apply** when one trace suffices.

Held as an example of an attack that invalidates a whole class of defences by
changing the resource it consumes rather than by being faster. When this program
proposes a mitigation or a cost bound, the question "which resource does the
attack actually need?" is the one this paper answers unexpectedly.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/546 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1007/978-3-032-01405-4_4).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Trace requirements, target implementation, and success rate are NOT recorded
here. **Title drift:** published at COSADE 2025 as "Message-recovery horizontal
correlation attack on Classic McEliece"; the 2023 ePrint (2023/546) is titled
"Horizontal Correlation Attack on Classic McEliece". Both are recorded from the
bibliography and were reconciled against the ePrint record during verification.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
