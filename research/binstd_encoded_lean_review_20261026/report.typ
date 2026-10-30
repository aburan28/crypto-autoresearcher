#set page(paper: "a4", margin: (x: 18mm, y: 15mm))
#set text(font: "DejaVu Sans", size: 9pt)
#set par(leading: 0.6em)

= BINSTD encoded certificate: independent review
_26 October 2026 · producer `6409590d` · plan `cab536aa`_

Two sealed reviewers examined separate joints. J1 checked the exact frozen
Lean declaration, direct pinned compilation, seven types, seven axiom outputs
and a rejected false control. J2 independently enumerated 1,110 monic
candidate rows from the statement alone. The repository independence checker
passed after separate compatibility addenda were filed; original attestations
and the initial format failure are retained.

#image("diagram.svg", width: 100%)

== Claim results

#table(
  columns: (2.1fr, 1.1fr, 1.1fr), inset: 4pt,
  [Scope], [Machine], [Outcome],
  [Five exact encoded masks; 510/30/30 candidate counts], [passed], [validated scoped],
  [Frozen Lean declaration; direct compile/type/axioms], [passed direct], [inconclusive as full certificate],
  [Archived direct-check receipt], [passed replay], [validated direct scope],
  [Full Mathlib/Lake target gate], [not verified], [inconclusive],
  [Polynomial irreducibility and Frobenius bridge], [not verified], [inconclusive],
)

The direct Lean checks used pinned 4.35.0-rc1. Six axiom queries reported only
`propext`; the count theorem had none. The false-control attempt failed as
expected. Both reviewers agree on all five finite predicate values and first
zero divisors. Reducible masks 131073 and 257 both divide by mask 3 with zero
remainder, requiring 17 and 8 XOR steps.

== Boundary and next proof

The theorem proves finite equalities of a source-defined bitmask function. It
does not prove that function equals `(ZMod 2)[X]` remainder, factor
irreducibility, or a normal-basis/Frobenius correspondence. The pinned full
workspace gate was not run; hosted Actions executed no steps due an account
payment or spending-limit gate. Run the exact target gate with exclusive host
ownership, then prove the mask-to-polynomial and remainder bridges. No
official scientific status changes here.

Evidence: `REPORT.md`, `archive/claim-verdicts.json`, `reconciliation.json`,
`independence-check.json` and the two `reports/TASK-*/` directories in this
packet. Review tasks: `TASK-20261026-538444`, `TASK-20261026-7ab9cb`.
