---
id: KN-LIT-6b1fc8
type: literature
title: "Understanding the new distinguisher of alternant codes at degree 2"
authors:
  - "Axel Lemoine"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2025/531"
  doi: "10.1007/s10623-025-01626-8"
  arxiv: null
  url: "https://eprint.iacr.org/2025/531"
tags: [code-based, mceliece, structural-attack, distinguisher, alternant-codes, algebraic-cryptanalysis, claim-class-corrected]
supersedes: [KN-LIT-7ee1a9]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Inherited, not re-earned. KN-LIT-7ee1a9 records a 2026-08-03 verification of
  this bibliographic line against the IACR ePrint record for report 2025/531 and
  against the Crossref record for the DOI. TASK-20260808-f9374d performed NO
  retrieval of any kind and read no full text; it re-tagged. Not raised to
  `read`: nobody in this program has read this paper.
added: "2026-08-08"
superseded_by: null
---

## Why this entry exists

**It supersedes `KN-LIT-7ee1a9` on one point only: the claim-class tags.**

`KN-LIT-7ee1a9` carries both `distinguisher` and `key-recovery`, which makes
`RQ-MCE-e65b3c`'s standing constraint *"Distinguisher is not break"*
unauditable except by human reading. This entry drops `key-recovery` and keeps
`distinguisher`, per `knowledge/TAG-CLAIM-CLASS.md` rule R-CC-1.

`KN-LIT-7ee1a9` is **not edited**; it is retired by being named in this entry's
`supersedes:` field (rule R-CC-6). Nothing else about the entry changed.

## Claim class

`distinguisher`. And a further step removed than that: the subject is an
*analysis* of someone else's degree-2 alternant distinguisher. Its recorded
contribution is *"the reason, not the attack"*. It claims no key recovery, and
on this program's record it claims no new distinguisher either.

**On what basis.** The title and `KN-LIT-7ee1a9`'s recorded description.
**This program has not read the paper.**

**Falsification condition.** An explanatory paper is exactly the genre in which
a recovery corollary tends to appear — the predictive theory that explains why a
distinguisher works is what tells you which *other* parameters it reaches. If a
read shows a recovery result, the correct token is `distinguish-then-recover`
(rule R-CC-2) and this entry must be superseded under a new id.

## Contribution

Explains the **new distinguisher of alternant codes at degree 2** — an analysis
paper clarifying why a recently discovered distinguisher works, rather than
introducing a new one. Alternant codes are the family containing Goppa codes, so
a distinguisher there bears directly on McEliece's structural assumption.

## Key claims (as reported)

- An explanation of the mechanism behind the degree-2 alternant distinguisher.
- Understanding-oriented: the contribution is the reason, not the attack.

## Relevance to this program

Held for the genre as much as the content. Papers whose contribution is
**understanding why an existing attack works** are how a field converts a
surprising result into a predictive theory — and predictive theory is what tells
you which *other* parameters are affected.

This program has the same obligation in its own lifecycle: `/review-evidence`
requires the mechanism to be stated, not only the outcome, because an
unexplained empirical win cannot be scoped and therefore cannot be safely
generalised.

**Does not bear on the ECDLP.**

## Not verified here

The full text was **not read** for this entry, and was not read for
`KN-LIT-7ee1a9` either. Everything under "Key claims" is relayed at one further
remove. No complexity figure, degree condition, rate condition or security
estimate has been reproduced by this program.

The mechanism explained and its consequences for Goppa codes at Classic McEliece
parameters are NOT recorded here. Those parameters and their exact rates are now
transcribed ([[KN-LIT-84b674]]); **this entry supplies nothing to compare them
against.**

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.
