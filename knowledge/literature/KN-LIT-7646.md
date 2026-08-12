---
id: KN-LIT-7646
type: literature
title: "Decomposition of the Ate Pairing and its Relation to Generalized Pairing Inversion"
authors:
  - "Takakazu Satoh"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1049"
identifiers:
  eprint: "iacr:2026/1049"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1049"
tags: [pairing, pairing-inversion, ate-pairing, elliptic-curve, supersingular, mov-fr, dlp, finite-field, number-theory, cryptanalysis, miller-function]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A note studying the **decomposition of the Ate pairing** on certain elliptic curves
over finite fields. As an application, **generalized pairing inversion** is reduced to
**root-finding for an element of the affine coordinate ring** appearing in that
decomposition.

For a supersingular `E/F_q` with `#E(F_q) = q + 1`, the author reports a **heuristic
observation** that the number of calls to a root-finding algorithm appears to be `O(N)`,
where `N` is the largest power of `2` dividing `q + 1`.

The stated key structural observation is that the **Miller function forms a factor
system**. The author remarks that the resulting algorithm does **not** use fixed-argument
pairing inversion.

## Key claims (as reported)
- Decomposition of the Ate pairing on certain curves; generalized pairing inversion
  reduces to root-finding in an affine coordinate ring.
- `O(N)` root-finding calls in the supersingular `#E = q+1` case, with `N = 2^{v_2(q+1)}`
  — explicitly labelled a **heuristic observation**, not a theorem, by the abstract
  itself.
- No fixed-argument pairing inversion is required.
- The Miller function is a factor system (in the group-cohomology sense).

## Relevance to this program
**Pairing inversion is the standing open reduction between the pairing-based world and
the ECDLP**: if pairings were efficiently invertible, the ECDLP on pairing-friendly
curves would fall via the MOV/Frey–Rück correspondence the program tracks under
`mov-fr`. So a paper that restructures the inversion problem is on-topic by
construction, and this one is worth holding for the **shape** of the reduction rather
than for a cost.

Two honest qualifications, both decisive:

- **`O(N)` is not a speedup.** `N` is the 2-adic valuation part of `q+1`; for
  supersingular curves chosen with `q + 1` having a large power of `2` — which is the
  common construction — `N` can be enormous, and the abstract offers no bound relating
  it to `√q` or to any generic baseline. **Nothing here claims pairing inversion is
  feasible, and this entry does not.**
- **Heuristic, unquantified, single-family.** The estimate is the author's stated
  observation for one curve family. The paper is presented as a note.

The genuinely interesting content is structural: identifying the Miller function as a
**factor system** places pairing computation inside a cohomological frame, which is the
kind of object-level reframing `docs/inventor-protocol.md` asks generators to look for.
Whether that frame buys anything is unresolved and is not asserted here.

**Does not establish any bearing on the prime-field ECDLP.** Pairing inversion remains
open; this entry records a reformulation, not progress against it.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1049,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author Takakazu Satoh, report number, year 2026.

NOT verified here: the decomposition; the reduction to root-finding; the factor-system
observation; the `O(N)` heuristic or the size of `N` for any deployed parameter set;
and whether the root-finding subproblem is itself tractable, which the abstract does
not address. **No pairing-based security estimate is revised on the basis of this
entry**, and no claim tier above "reported reformulation" is asserted.
