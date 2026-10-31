#set page(paper: "a4", margin: (x: 18mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 9.4pt)
#set par(leading: 0.58em)
#set heading(numbering: "1.")

#align(center)[
  #text(size: 17pt, weight: "bold")[BINSTD canonical-field Lean proof review]
  #linebreak()
  27 October 2026 UTC · technical review packet · scoped machine gate passed; packet evidence gap
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
  [`passed`: named build and axiom audit],
  [`faithful_scoped`; `inconclusive`],
  [`canonicalFrobenius_order_and_minpoly`: canonical GF(2¹⁷) Frobenius order 17 and stated minimal polynomial],
  [`passed`: named build and axiom audit],
  [`faithful_scoped`; `inconclusive`],
  [Archived runner, complete invariant-subspace classification and Stage 1 yield],
  [`not_verified` by these declarations],
  [`partial` bridge; `needs_revision` for concrete certification],
)

The full packet remains `inconclusive` against its frozen contract because no separate elaborated-type printout was emitted. Run 40591043322 completed successfully: 89 machine-verified receipts, including the two named targets. Artifact 12774634972 has SHA-256 `4a558a174bbcb8f8f13f27cd9c96d45a8868c67a3fd20fbf6928aa766acbb99f`. J1 independently downloaded both named receipts and matched all 65 workspace and 10 verifier inputs to the producer tree. The audit reported 713 theorems using only standard allowed axioms. Hosted controls passed 317 tests. The subject workspace uses Lean 4.35.0-rc1 and Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`. No independent lean4checker binary check was available.

= Independent review and controls

Prospective J1 checked exact source signatures, coefficients, target specs, pinned Mathlib dependencies, verifier logic, and the fresh named receipts. Both narrow source claims match their declarations without circular premises; machine status is `passed` and fidelity is `faithful_scoped`. Source signatures are not a separate elaborated-type dump.

Prospective J2 received only an isolated statement and read no producer or sibling report through delivery. It exhaustively tested all 30 possible low-degree monic divisors for each degree-eight factor and proved canonical GF(2¹⁷) Frobenius order 17 and minimal polynomial `X^17+1` by the field root bound. False controls `X^8+1` and GF(2) were rejected. Its exact script reproduced sealed raw output SHA-256 `606465241f032b7e1d924f92235df0a49d277a7eeef367355767f5c72ded73fd`. Its quotient calculation does not certify archived runner code.

#pagebreak()

#figure(
  image("diagram.svg", width: 100%),
  caption: [Evidence chain and missing bridge to the historical runner.],
)

= Protocol finding and open obligations

The first frozen review round failed the stock independence checker with seven recorded plan/schema problems; that failure remains preserved. A corrected prospective round assigned valid task refs and a truly blind J2. The stock checker initially rejected J2's truthful YAML serialization twice: it expected a `review_attestation` wrapper and path-string `sources_read` list, while the sealed report recorded detailed read objects. A deterministic, sealed-hash-pinned adapter projected only the read paths and preserved the full objects. The stock checker returned exit 0 on J1's original attestation and that disclosed projection. The raw pair does not directly pass its interface.

The hosted job did not emit a separate elaborated `#print` or `#check` type output. That frozen documentation item remains open, as do ordinary Lean/Lake binary trust and absent independent kernel recheck. Runner encoding, executable arithmetic, canonical conjugacy, complete invariant-subspace classification, constructor correctness including the empty subset, and archived-output binding need separate proof. Neither named theorem proves empirical yield or security cost.

No new experiment, cloud worker or scientific status change was made. The editable report and evidence live in `research/binstd_formal_review_20261027/` on #link("https://github.com/isogeny-labs/crypto-autoresearcher/pull/2629")[review PR 2629].
