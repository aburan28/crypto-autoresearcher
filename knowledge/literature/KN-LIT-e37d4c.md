---
id: KN-LIT-e37d4c
type: literature
title: "A note on the Goppa code distinguishing problem"
authors:
  - "Andreas Wiemers"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/1661"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1661"
tags: [code-based, mceliece, structural-attack, key-recovery, goppa, distinguisher, indistinguishability]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A note on the **Goppa code distinguishing problem** — the assumption, separate
from syndrome decoding, that a Goppa code's public generator matrix cannot be
told apart from a random one. McEliece's security needs both, and the
distinguishing assumption is the weaker-understood of the two.

## Key claims (as reported)
- A contribution to understanding when Goppa codes can be distinguished from random.
- Note-length: a focused observation rather than a full attack.

## Relevance to this program
The distinguishing problem is where **all the structural attacks in this
section live**, and it is the part of McEliece's security that rests on the
least theory. Held as part of that thread ([[KN-LIT-13a01d]],
[[KN-LIT-71d1a0]], [[KN-LIT-7ee1a9]]).

The transferable observation for this program is architectural: a cryptosystem
built on a hidden-structure trapdoor has **two** assumptions, and the one about
the structure being hidden is usually the softer one. Any ECDLP-side proposal
introducing a structured object should expect its structural assumption, not
its hardness assumption, to be the first thing attacked.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/1661 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The note's actual observation is NOT recorded here. **Title drift:** the
bibliography lists this as "A note on the Goppa code distinguishing problem",
but the current IACR ePrint record for report 2025/1661 is titled
*"Distinguishing Goppa codes using higher-order vanishing"*. This entry keeps
the bibliography's title as listed and records the ePrint title here; the two
were reconciled during verification, not assumed equal.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
