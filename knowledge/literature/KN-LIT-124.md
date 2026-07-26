---
id: KN-LIT-124
type: literature
title: On the Cost of Computing Isogenies Between Supersingular Elliptic Curves
authors: [Adj Gora, Cervantes-Vazquez Daniel, Chi-Dominguez Jesus-Javier, Menezes Alfred, Rodriguez-Henriquez Francisco]
year: 2018
venue: 'Selected Areas in Cryptography - SAC 2018, LNCS 11349, Springer'
identifiers:
  eprint: iacr:2018/313
  doi: 10.1007/978-3-030-10970-7_15
  url: https://eprint.iacr.org/2018/313
tags: [supersingular, isogeny, sidh, cssi, meet-in-the-middle, golden-collision, van-oorschot-wiener, collision-search, memory, full-cost, cost-model, classical-baseline, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Re-examines the classical security of the Jao-De Feo SIDH key agreement scheme,
whose hardness rests on the Computational Supersingular Isogeny (CSSI) problem.
The paper's stated conclusion is that the van Oorschot-Wiener (vOW) golden
collision finding algorithm has a **lower cost** for solving CSSI than the
meet-in-the-middle (MITM) attack that had been used to set SIDH parameters, and
that vOW should therefore be the algorithm used to assess SIDH's classical
security.

## Key claims (as reported)
- MITM had been the reference classical attack on CSSI in the SIDH parameter
  literature; this paper argues it is the wrong reference once cost is properly
  accounted.
- vOW golden collision search is reported to have lower cost for CSSI, and is
  recommended as the algorithm against which SIDH classical security should be
  measured.
- The disagreement is a **cost-model disagreement**, not an algorithmic
  discovery: MITM's advantage is in step count, and it is charged for the storage
  its table requires.

## Relevance to this program
Supplies the most likely candidate for a gap that is blocking `GOAL-SSI-001`.
`EV-SSI-001` records that "low-memory distinguished-point collision search on
expander isogeny graphs is underspecified relative to the group setting," and
`DEC-20260725-002` makes "defining or falsifying" that analogue the main
technical content of the BATCH-002 derivation gate.

vOW golden collision search — this paper, with `KN-LIT-125`'s implementation and
`KN-LIT-132`'s memory-free fixed-degree competitor — is the obvious candidate for
that analogue, and BATCH-002 should start from this literature rather than build
from scratch. **But the identification is a lead, not a settled result.** Adj et
al. apply vOW to CSSI, i.e. to F_p^2-rational isogenies of fixed smooth degrees
on SIDH parameters. `EV-SSI-001`'s gap concerns random walks on the expander graph
for the *surviving* assumptions (CGL, endomorphism-ring/SQIsign, CSIDH). Those
differ on exactly the degree axis that `KN-TECH-050` names as one of three
load-bearing regime variables. Whether vOW-for-CSSI instantiates the analogue for
the surviving assumptions **is the BATCH-002 question**, not its answer.

What can be said without further work: a matched-baseline recommendation that
does not engage with this literature is incomplete.

It is also a clean instance of the program's own thesis (`KN-TECH-035`,
`KN-LIT-094`, and §7 of `docs/knowledge-assessment-20260724.md`): two "attack
costs" for the same problem differed because one charged memory and the other
did not, with no algorithmic disagreement between them.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2018/313, Springer DOI 10.1007/978-3-030-10970-7_15, SAC 2018 / LNCS 11349); the
ePrint page, the publisher page, and the PDF could not be fetched, because this
session's egress policy blocks all direct external fetches. Title, author list,
year and venue are corroborated across independent results; **the abstract was
not read in full and no claim below the level stated above was checked.**

Specifically NOT verified here: the exact complexity expressions and constants
for vOW versus MITM on CSSI, the memory model assumed, the concrete SIDH/SIKE
parameter sets analysed, and the resulting security-level figures. Any BATCH-002
derivation that quotes a number from this paper must obtain it from the paper
itself, not from this entry.

Also NOT established here: **that vOW-for-CSSI is the analogue `EV-SSI-001` calls
undefined.** That bridge — from fixed-smooth-degree CSSI on SIDH parameters to
expander-graph walks for the surviving assumptions — is an inference of this
program's, drawn from an abstract that was not read, and it is precisely what the
BATCH-002 gate exists to settle.

**Correction (2026-07-25, pre-merge, same session).** As first written, the
Relevance section asserted that this entry "closes a gap" and that the analogue
"is **not** undefined in the literature: it is vOW golden collision search." That
stated a scope-crossing inference as a settled identification and was not listed
among the entry's unverified items. Both are corrected above; the same softening
was applied to `KN-TECH-050` and to §10 of
`docs/knowledge-review-20260725.md`.
