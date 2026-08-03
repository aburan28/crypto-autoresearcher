---
id: KN-LIT-d6d510
type: literature
title: "An attack on the CFS scheme and on TII McEliece challenges"
authors:
  - "Magali Bardet"
  - "Axel Lemoine"
  - "Jean-Pierre Tillich"
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/430"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/430"
tags: [code-based, mceliece, structural-attack, key-recovery, cfs, signatures, challenges, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
An attack on the **CFS signature scheme** and on the **TII McEliece
challenges** — the latter being a public challenge series with concrete
instances, so the paper reports against posted targets rather than only against
a scheme description.

## Key claims (as reported)
- An attack on CFS, the Courtois–Finiasz–Sendrier code-based signature scheme.
- Results against the TII McEliece challenge instances.

## Relevance to this program
Held for the **challenge-instance** methodology. A result stated against a
public challenge is checkable in a way a result stated against a scheme
description is not: the solution is a certificate anyone can verify.

That is precisely the standard `docs/claims-and-verification.md` sets for this
program — a claimed solve carries a certificate the run wrapper re-verifies
independently. Challenge series are the community's version of the same
discipline, and this paper is a current example of it working.

CFS is also a reminder that **signatures are the fragile branch of code-based
cryptography**: the encryption side has held up far better than the signature
side, which is a design observation worth carrying.

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2026/430 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Which challenge instances were solved, at what parameters and cost, is NOT
recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
