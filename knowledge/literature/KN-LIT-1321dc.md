---
id: KN-LIT-1321dc
type: literature
title: "Decoupling support enumeration and value discovery in non-binary ISD"
authors:
  - "Freja Elbro"
  - "Paolo Santini"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/1523"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1523"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, non-binary-isd, q-ary-codes]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Separates two steps that non-binary ISD algorithms usually perform together:
**support enumeration** (which coordinates carry errors) and **value discovery**
(which non-zero field element sits in each of them). Over `F_2` the second step
is free — a non-zero binary value is `1` — so the binary literature never had to
treat it separately; over `F_q` it costs a factor that grows with `q`.
Decoupling the two lets each be optimised on its own terms.

## Key claims (as reported)
- Support enumeration and value discovery can be decoupled in non-binary ISD, and treating them separately improves the algorithm.
- The improvement is specific to `q > 2`; the binary case is where the distinction collapses.

## Relevance to this program
A clean example of a **structural observation that only becomes visible in the
general case**: the binary specialisation hides the degree of freedom, and
recovering it yields the improvement. That is precisely the object-first move
`docs/inventor-protocol.md` asks the idea generator to make — look for the
parameter the standard formulation silently fixed.

Classic McEliece is binary, so this is a generalisation-side result rather than
an attack on the standardised parameter sets.

**Does not bear on the ECDLP**, though the "what did the standard formulation
fix without saying so" question transfers directly.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/1523 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The claimed speedup factor and its dependence on `q` are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
