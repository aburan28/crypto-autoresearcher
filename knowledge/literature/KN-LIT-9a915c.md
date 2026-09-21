---
id: KN-LIT-9a915c
type: literature
title: "Isogenous hyperelliptic and non-hyperelliptic Jacobians with maximal complex multiplication"
authors:
  - "Bogdan Dina"
  - "Sorina Ionica"
  - "Jeroen Sijsling"
year: 2022
venue: "arXiv preprint (math.NT), v4"
identifiers:
  eprint: null
  doi: null
  arxiv: "arxiv:2104.04919"
  url: "https://arxiv.org/abs/2104.04919"
tags: [complex-multiplication, genus-3, jacobian, hyperelliptic, non-hyperelliptic, picard-curves, shimura-class-group, reflex-field, sextic-cm-field, lmfdb, cm-invariants, abelian-variety, isogeny, elliptic-curve, class-field]
confidence: reported
citation_verified: read
added: "2026-09-06"
superseded_by: null
---

> **Provenance.** Read from a local PDF supplied by the user at
> `/Volumes/SSD990/downloads/2104.04919v4.pdf` (462,300 bytes,
> `sha256:111b63d6c50408f573d6486c787ac2b1ede2b558e02084a5cab22cccd763ae2a`),
> stamped `arXiv:2104.04919v4 [math.NT] 23 Aug 2022`. Abstract and introduction read
> directly; the identifier is self-reported by the document and was not confirmed
> against the arXiv listing by this program. Not vendored into `inputs/`.

## Contribution

Analyzes complex multiplication for Jacobians of **genus-3** curves, together with the
resulting Shimura class groups and the subgroups corresponding to Galois conjugation
over the reflex field. Combines that theory with numerical search to find CM fields
`K` admitting **both** a hyperelliptic and a non-hyperelliptic curve whose Jacobian
has CM by the maximal order `Z_K`.

## Key claims (as reported)

- The search is over the **sextic CM fields in the LMFDB**, and the headline count is
  sharp and checkable: **14 such fields among the 547,156** sextic CM fields the LMFDB
  contains. The authors label the existence conclusion **heuristic**.
- Invariants of the corresponding curves are determined; in the simplest case an
  explicit defining equation is given.
- Framing: genus 1 and genus 2 CM invariants and models are well covered in the
  literature, and the frontier has moved to genus 3, where hyperelliptic *and*
  non-hyperelliptic curves both occur — the latter first studied as Picard curves.
- Uses the standard Shimura–Taniyama fact that invariants of simple CM Jacobians
  generate abelian extensions of CM fields, and the observation that Galois conjugates
  of a hyperelliptic Jacobian are again hyperelliptic Jacobians.

## Relevance to this program

Adjacent rather than central, and worth filing for two specific reasons.

**A genuine population census with a denominator.** "14 of 547,156" is exactly the
shape of statement `RQ-SIMSPK-f6a6c0` and the `GOAL-SCURVE-*` audits keep asking for —
a position in an enumerated distribution rather than an existence claim. If this
program ever needs a *rarity baseline* for a CM-related structural property in genus 3,
this is a published, LMFDB-anchored one. Note the authors call the existence
heuristic, so the denominator is exact and the numerator is not.

**Same-Jacobian, two curve models.** The object here is a CM field admitting two
structurally different curves with isogenous/CM-equivalent Jacobians. That is the
genus-3 analogue of the "same abelian variety, different presentation" question the
program's own work touches in `GOAL-ENDO-001` and the isogeny-class search in
`harness/isogeny_class.py`. Whether it transfers is untested and this entry does not
claim it does.

Sorina Ionica also co-authors the index-calculus SAT line filed as
[[KN-LIT-102cdb]] and [[KN-LIT-92919e]] — the same group works both the algebraic
solver side and the CM/Jacobian side.

## Not verified here

Nothing reproduced. The count of 14, the LMFDB total of 547,156, the invariants, and
the explicit equation are **reported**. The LMFDB was not queried, no curve was
constructed, and the heuristic status of the existence result is the authors' own
label, not this program's assessment of it.
