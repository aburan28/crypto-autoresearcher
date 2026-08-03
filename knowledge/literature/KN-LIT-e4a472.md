---
id: KN-LIT-e4a472
type: literature
title: "The tangent space attack"
authors:
  - "Axel Lemoine"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/763"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/763"
tags: [code-based, mceliece, structural-attack, key-recovery, algebraic-cryptanalysis, alternant-codes, tangent-space]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**The tangent space attack** — a structural attack framed through the tangent
space of an algebraic variety attached to the code. Naming an attack after the
geometric object it exploits is the object-first framing this program's own
protocol prescribes.

## Key claims (as reported)
- A structural attack built on a tangent-space construction.

## Relevance to this program
Held for the **methodological shape**, which is unusually legible. The attack is
named for its object; the object is a linearisation (a tangent space is the
first-order approximation of a variety at a point); and the attack works, when
it works, because that first-order information is enough.

`docs/inventor-protocol.md`'s lossy-projection test asks precisely this
question in reverse — which projections of the hard object lose the hardness?
A tangent space is a canonical lossy projection, and an attack built on one is
a worked example of the test finding something.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/763 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

What the attack targets, its complexity, and its applicability to Classic
McEliece are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
