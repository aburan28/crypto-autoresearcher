#set page(paper: "a4", margin: (x: 18mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 9.4pt)
#set par(leading: 0.58em)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 17pt, weight: "bold")[BINSTD canonical-field Lean proof review]
  #linebreak()
  27 October 2026 UTC · technical review packet · machine gate pending
]

#v(8pt)
*Producer:* #link("https://github.com/isogeny-labs/crypto-autoresearcher/pull/2484")[PR 2484] at `976b82bf60afda5e3d31c0da2704604ea2f2e5a5`. *Review plan:* `b95ccf3400f34441952930c6ca8b9a129661222d`. The hosted checkout's synthetic merge commit and the producer head have the same complete Git tree `0278ef830e544ff7b04af3765c366bf5acb8a3cb`.

= Assessment at this revision

#table(
  columns: (1.75fr, 1fr, 1.18fr),
  inset: 5pt,
  stroke: 0.4pt + rgb("adb9c2"),
  [*Claim*], [*Current machine status*], [*Fidelity / outcome*],
  [`factor8_irreducible_pair`: factors 313 and 471 are irreducible over F₂],
  [`not_verified` while current-head workspace gate runs],
  [`faithful_scoped`; `inconclusive`],
  [`canonicalFrobenius_order_and_minpoly`: canonical GF(2¹⁷) Frobenius order 17 and stated minimal polynomial],
  [`not_verified` while current-head workspace gate runs],
  [`faithful_scoped`; `inconclusive`],
  [Archived runner, complete invariant-subspace classification and Stage 1 yield],
  [`not_verified` by these declarations],
  [`partial` bridge; `needs_revision` for concrete certification],
)

The current-head machine status above records an incomplete gate, not a Lean refutation. Historical receipts record success for earlier commits but omit complete workspace/verifier input maps. The hosted controls passed 317 tests with zero failures, errors or skips on the dependency-free Lean 4.22.0 smoke project; the subject workspace uses Lean 4.35.0-rc1 and Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`.

= Independent review and controls

J1 inspected the exact types, target specs, polynomial definitions, pinned Mathlib lemmas, worker and CI gate. The two narrow source claims match their declarations. The worker explicitly builds each requested target module and audits the named theorem's transitive axioms. The global wrapper can label a missing theorem file undischarged, so the two named receipts remain required.

J2 derived the factors and canonical Frobenius result from a blinded statement before reading producer source. Its seal was written at 22:07:34 UTC. All five sealed artifact hashes still match, and its deterministic calculation reproduces the archived output. The method rejects reducible `X^8+1` and distinguishes Frobenius on GF(2), whose order is 1. J2 also computed order 17, minimal polynomial `X^17+1`, and kernel dimensions 1, 8, 8 for an independently defined quotient by modulus 131081. These calculations do not certify the archived runner's execution.

#pagebreak()

#figure(
  image("diagram.svg", width: 100%),
  caption: [Evidence chain and missing bridge to the historical runner.],
)

= Protocol finding and open obligations

The stock independence checker returned exit 1 with seven recorded problems. The frozen plan used actual Conductor IDs `T-608` and `T-609`, while the checker requires `TASK-*` IDs. It also requires explicit blind quantity and source fields and a supported phase contract. Truthful reviewer identities and post-seal read lists were retained. This round therefore cannot claim a passed machine-checkable independence gate; a prospectively corrected round is required.

The named Lean receipts, elaborated types and transitive axiom logs from #link("https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40591043322")[run 40591043322] must still be inspected. Formal bridges remain for runner encoding and field construction, executable arithmetic, canonical conjugacy, matrix representation, invariant-subspace classification, constructor correctness (including the empty subset), and exact archived-output binding. Neither theorem proves empirical yield or security cost.

No new experiment, cloud worker or scientific status change was made. The editable report, diagram, blind calculation and reviewer attestations live in `research/binstd_formal_review_20261027/` on #link("https://github.com/isogeny-labs/crypto-autoresearcher/pull/2629")[review PR 2629].
