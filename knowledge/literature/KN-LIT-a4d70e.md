---
id: KN-LIT-a4d70e
type: literature
title: "The syzygy distinguisher"
authors:
  - "Hugues Randriambololona"
year: 2025
venue: "Eurocrypt"
identifiers:
  eprint: "iacr:2024/1193"
  doi: "10.1007/978-3-031-91095-1_12"
  arxiv: null
  url: "https://eprint.iacr.org/2024/1193"
tags: [code-based, mceliece, structural-attack, distinguisher, syzygy, commutative-algebra, alternant-codes, algebraic-cryptanalysis, claim-class-corrected]
supersedes: [KN-LIT-71d1a0]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Inherited, not re-earned. KN-LIT-71d1a0 records a 2026-08-03 verification of
  this bibliographic line against the IACR ePrint record for report 2024/1193
  and against the Crossref record for the DOI. TASK-20260808-f9374d performed NO
  retrieval of any kind and read no full text; it re-tagged. Not raised to
  `read`: nobody in this program has read this paper.
added: "2026-08-08"
superseded_by: null
---

## Why this entry exists

**It supersedes `KN-LIT-71d1a0` on one point only: the claim-class tags.**

`KN-LIT-71d1a0` carries both `distinguisher` and `key-recovery`. Its own title
and its own recorded description say distinguisher. The pair makes
`RQ-MCE-e65b3c`'s standing constraint *"Distinguisher is not break"*
unauditable except by human reading. This entry drops `key-recovery` and keeps
`distinguisher`, per `knowledge/TAG-CLAIM-CLASS.md` rule R-CC-1.

`KN-LIT-71d1a0` is **not edited**; it is retired by being named in this entry's
`supersedes:` field (rule R-CC-6). Nothing else about the entry changed.

## Claim class

`distinguisher`. The subject distinguishes algebraic (alternant/Goppa-family)
codes from random ones using syzygy computations. No key recovery is claimed by
the subject as this program has recorded it.

**On what basis.** The title and `KN-LIT-71d1a0`'s recorded description.
**This program has not read the paper**, and the superseded entry says so
outright: *"The construction, its complexity, the code families and rates for
which it succeeds, and whether it reaches Classic McEliece parameters are NOT
recorded here."*

**This is the weakest of the four classifications made in this batch, and it is
flagged rather than smoothed over.** The distinguisher line's whole historical
pattern is escalation — a distinguisher published, a key recovery derived from
it later — and the same author is a co-author of `KN-LIT-7c4620`, the 2026
heuristic subexponential attack that is `RQ-MCE-e65b3c`'s primary target. If a
read shows this paper itself carries a recovery result, the correct token is
`distinguish-then-recover` (rule R-CC-2), not `distinguisher`, and this entry
must be superseded under a new id rather than re-tagged.

## Contribution

**The syzygy distinguisher.** Uses syzygies — the relations among generators of
a module, a standard object of commutative algebra — to distinguish algebraic
codes from random ones. Eurocrypt 2025.

## Key claims (as reported)

- A distinguisher for algebraic codes built from syzygy computations.
- Applies to the alternant/Goppa family relevant to McEliece.

## Relevance to this program

The strongest single example in the GATHER-20260803 sweep of the move
`docs/inventor-protocol.md` is built around: **import a mature object from a
neighbouring area of mathematics and ask what it computes about the target.**
Syzygies come from commutative algebra and free-resolution theory, not from
coding theory, and the distinguisher exists because someone asked what they say
about a code.

The idea generator should treat this as a template. The corresponding ECDLP
question — which established algebraic-geometry or commutative-algebra
invariants have not been computed against curve-side objects — is exactly the
kind this program is meant to generate and then test cheaply before committing
compute.

Held together with [[KN-LIT-6b1fc8]] (superseding [[KN-LIT-7ee1a9]]),
[[KN-LIT-4c8135]] and [[KN-LIT-2127]] as the modern distinguisher cluster.

**Does not bear on the ECDLP**, but is the sweep's best methodological exemplar
alongside [[KN-LIT-7965a1]].

## Not verified here

The full text was **not read** for this entry, and was not read for
`KN-LIT-71d1a0` either. Everything under "Key claims" is relayed at one further
remove. No complexity figure, code family, rate condition or security estimate
has been reproduced by this program.

The construction, its complexity, the code families and rates for which it
succeeds, and whether it reaches Classic McEliece parameters are NOT recorded
here. Classic McEliece's actual rates are now transcribed
([[KN-LIT-84b674]]); **this entry supplies nothing to compare them against.**

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.
