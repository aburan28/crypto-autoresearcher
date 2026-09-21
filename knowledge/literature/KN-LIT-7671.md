---
id: KN-LIT-7671
type: literature
title: "Exploiting the complexity of Lattice Isomorphism Problem via Irreducible Decomposition"
authors:
  - "Kaijie Jiang"
  - "Yinchen Liu"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1139"
identifiers:
  eprint: "iacr:2026/1139"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1139"
tags: [lattice-isomorphism-problem, slip, complexity, am-coam, polynomial-hierarchy, np-hardness, graph-isomorphism, kz-basis, orthogonal-decomposition, svp, foundational]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A **complexity-theoretic upper bound on the search Lattice Isomorphism Problem (SLIP)**.

Background as stated: Haviv and Regev (SODA 2014) showed the **decisional** LIP lies in
statistical zero-knowledge and so is unlikely to be NP-hard; that argument does not apply
to the search version, which is believed **harder than SVP**.

The main result answers the natural question negatively: **every language reducible to
SLIP lies in AM ∩ coAM**, obtained by analysing the **direct-sum structure of
irreducible lattices**. Consequences drawn:

- **NP cannot reduce to SLIP unless the polynomial hierarchy collapses.**
- **There is no reduction from SVP to SLIP unless the polynomial hierarchy collapses.**

The paper also establishes reductions among the **search, counting, and decisional**
variants of LIP — connections the authors note mirror the known relationships for
**graph isomorphism** — and proposes a new algorithm using a **KZ basis** to compute an
orthogonal decomposition of a lattice.

## Key claims (as reported)
- Languages reducible to SLIP lie in AM ∩ coAM.
- No NP→SLIP and no SVP→SLIP reduction absent a polynomial-hierarchy collapse.
- Search/counting/decision reductions for LIP, paralleling graph isomorphism.
- A KZ-basis algorithm for orthogonal lattice decomposition.

**What this is not.** It is an **upper bound on hardness**, not an attack: it says SLIP
cannot be *as hard as* NP-complete problems or SVP, not that SLIP is easy. LIP-based
cryptography is not weakened by it. This is the same logical shape as the classic
`GapSVP ∈ NP ∩ coNP` results, which likewise broke no scheme.

## Relevance to this program
Completes the sweep's LIP picture from the **structural** side, alongside the
algorithmic entries:

- [[KN-LIT-7648]] — LIP for quadratic forms collapses via genus/spinor genus; DEFI
  falls, HAWK reported unaffected.
- [[KN-LIT-7670]] — a heuristic polynomial-time HAWK key-recovery route via nrd-PIP,
  with one heuristic publicly conceded insufficient.
- **This entry** — SLIP sits in AM ∩ coAM, so it is *provably not* as hard as SVP unless
  the polynomial hierarchy collapses.

Read together they say something coherent and worth having in one place: **LIP is a
problem whose hardness is bounded above by complexity theory, attacked successfully in
at least one concrete instantiation, and under active heuristic attack in another.**
That is a materially different risk profile from "believed hard," and a proposal in this
program that reached for a LIP-style assumption should read all three before treating it
as a hardness baseline.

The **graph-isomorphism parallel** is the reusable frame. GI is the canonical
"structurally intermediate" problem — not known NP-hard, not known easy, with search/
decision/counting equivalences and an AM ∩ coAM ceiling. Recognizing an assumption as
GI-shaped tells you which arguments are available and which are foreclosed, and this
paper makes the analogy explicit rather than suggestive. Compare [[KN-LIT-7652]], where
invariant theory on code equivalence produced correct-but-infeasible invariants — the
same intermediate texture.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1139,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the ePrint
record: title, two authors, report number, year 2026.

NOT verified here: the AM ∩ coAM containment or the irreducible-direct-sum analysis
producing it; the two polynomial-hierarchy corollaries; the search/counting/decision
reductions; the KZ-basis decomposition algorithm; and the attribution to Haviv–Regev
(SODA 2014), which is relayed and is not an entry in this corpus. **No LIP-based scheme
is assessed, and this entry asserts nothing about whether LIP is hard enough for
cryptography.**
