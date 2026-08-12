---
id: KN-LIT-fab214
type: literature
title: "Punctured syndrome decoding problem: Efficient side-channel attacks against Classic McEliece"
authors:
  - "Vincent Grosso"
  - "Pierre-Louis Cayrel"
  - "Brice Colombier"
  - "Vlad-Florin Dragoi"
year: 2023
venue: "COSADE"
identifiers:
  eprint: "iacr:2023/308"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/308"
tags: [side-channel, code-based, classic-mceliece, implementation-attack, punctured-syndrome-decoding, problem-definition, efficient-attacks]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Defines the **punctured syndrome decoding problem** — syndrome decoding when
some coordinates are known or removed via side-channel information — and shows
it supports efficient attacks on Classic McEliece.

## Key claims (as reported)
- Side-channel-assisted decoding is formalised as a punctured syndrome decoding problem.
- The punctured problem is substantially easier than the full one.

## Relevance to this program
The best methodological entry in the side-channel section: rather than reporting
an attack, it **names the problem the attack solves.** Once punctured syndrome
decoding exists as an object, its hardness can be studied independently of any
particular measurement setup, and results about it transfer to every attack that
produces the same kind of partial information.

This is the abstraction discipline `docs/inventor-protocol.md` asks for —
object-first generation, where the useful move is identifying and naming the
object rather than solving one instance. A direct model for how this program
should convert a recurring experimental situation into a stated problem.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2023/308 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The complexity of punctured syndrome decoding as a function of puncturing, and
the resulting attack costs, are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
