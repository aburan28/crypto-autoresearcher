---
id: KN-LIT-4c8135
type: literature
title: "Polynomial time key-recovery attack on high rate random alternant codes"
authors:
  - "Magali Bardet"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2024
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/tit.2023.3334592"
  arxiv: "2304.14757"
  url: "https://arxiv.org/abs/2304.14757"
tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, polynomial-time, high-rate, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **polynomial-time key-recovery attack on high-rate random alternant codes**.
Alternant codes are the family containing Goppa codes; the result is confined to
the **high-rate** regime, and that scoping is the whole content of its practical
reading.

## Key claims (as reported)
- Polynomial-time key recovery for random alternant codes of high rate.
- The attack is **rate-scoped** — it does not claim to break alternant or Goppa codes at arbitrary rate.
- Published in IEEE Transactions on Information Theory, i.e. it has been through journal review.

## Relevance to this program
The best example in this sweep of a result that is **genuinely strong and
genuinely bounded**, and of how much the boundary carries. Polynomial-time key
recovery against a family adjacent to the one McEliece uses would read as
devastating with the rate condition dropped; with it stated, it is a precise
statement about a region of parameter space that deployed systems avoid.

This is what AGENTS.md rule 4 asks of every conclusion in this program, and it
is worth citing as the standard when a proposal here reports a strong result on
a restricted instance class. The temptation to state the headline without the
scope is exactly the failure mode the rule exists to prevent.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the arXiv record for 2304.14757; citation verified against the Crossref record (DOI 10.1109/tit.2023.3334592).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The precise rate threshold, the polynomial degree, and the distance from
Classic McEliece's operating regime are NOT recorded here — and that threshold
is the single most important number in the paper.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
