---
id: KN-LIT-7642
type: literature
title: "Efficient quaternion algorithms for the Deuring correspondence, and application to the evaluation of modular polynomials"
authors:
  - "Antonin Leroux"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/185"
identifiers:
  eprint: "iacr:2026/185"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/185"
tags: [deuring, quaternion, quaternion-algebra, endomorphism-ring, isogeny, supersingular, modular-polynomial, implementation, cost-model, sqisign, elliptic-curve, number-theory]
confidence: reported
citation_verified: web
added: "2026-08-01"
supersedes: KN-LIT-2414
superseded_by: null
---

> **Correction entry.** This supersedes [[KN-LIT-2414]], which holds the same paper
> under a corrupted citation — its `title` field concatenates an ANTS XVII conference
> banner with a truncated paper title, its `authors` field contains the fragment
> `"APPLICATION TO THE"` rather than a person, and all three identifier fields are
> `null`. That record cannot support a novelty check or a citation. Per
> `knowledge/README.md`, the correction is a new entry; KN-LIT-2414 is marked
> `superseded_by: KN-LIT-7642` and its body is left intact.

## Contribution
Algorithms for operations on the **quaternion ideals and orders arising from the
Deuring correspondence**. The stated point is that although these operations are
solvable by generic linear algebra, they can be done much faster while keeping strict
control over the **size of the integers involved** — enabling an implementation of the
effective Deuring correspondence with **fixed-size integers**.

Applied to the modular-polynomial evaluation algorithm of Corte-Real Santos, Eriksen,
Leroux, Meyer and Panny, the new implementation is reported to run **20× faster** than
the previous one at level `ℓ = 11681`.

## Key claims (as reported)
- Quaternion-ideal/order operations for the Deuring correspondence admit substantially
  faster algorithms than the generic linear-algebra route, with bounded integer sizes.
- Fixed-size-integer implementation of the effective Deuring correspondence is achieved.
- **20× speedup** over the prior implementation for modular-polynomial evaluation at
  `ℓ = 11681`. This is the only quantitative figure in the abstract: one level, one
  comparison, one machine.
- The author states that fixed-size efficient quaternion operations appear to be a main
  missing feature of recent **SQIsign** implementations, and suggests the algorithms
  could help there. This is framed as a belief, not a demonstrated result.
- The ePrint record carries a note that the current version corrects typos and
  editorial problems.

## Relevance to this program
Two direct connections, both to **cost accounting** rather than to hardness:

- **Modular-polynomial evaluation** is the same machinery [[KN-LIT-7613]] prices from
  the coefficient-height side. This entry supplies the complementary
  arithmetic-engineering side: a reported constant-factor improvement in the evaluation
  routine itself. Constant factors, not exponents — nothing here moves an asymptotic.
- **Quaternion arithmetic as substrate.** The program's isogeny-path-finding cost
  models (`KN-TECH-050`, `KN-TECH-057`) assume some concrete cost for effective Deuring
  operations. A 20× swing in that layer is large enough to matter to any full-cost claim
  that instantiates it, and small enough that it changes no security conclusion.

Read alongside [[KN-LIT-7641]] and [[KN-LIT-7656]]: those two are about what quaternion
orders *prove*; this one is about what they *cost*.

**Does not bear on the prime-field ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/185,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author Antonin Leroux, report number, year 2026. The
all-capitals title as recorded on ePrint has been normalized to sentence case here; the
`identifiers.url` points at the authoritative record.

NOT verified here: the speedup factor, the hardware or baseline it was measured
against, whether the `ℓ = 11681` result is representative of other levels, the
integer-size bounds, and the suggested applicability to SQIsign. **No revision to
`KN-TECH-050` or `KN-TECH-057` is asserted**, and no cost model in this program is
re-derived from the 20× figure — a single-level speedup reported in an abstract is not
a cost model.
