#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set par(justify: false, leading: 0.65em)
= BINSTD elaborated-type supplement
#text(fill: rgb("385b6a"))[28 October 2026 · Technical review · PR 2629]

*Scoped outcome:* the two fixed mathematical declarations are validated under ordinary Lean/Lake trust. The separately printed types are now independently bound to the frozen claims. No scientific state changes.

#table(columns: (1fr, 1.4fr), inset: 6pt, fill: (x,y) => if y == 0 {rgb("e5f1f3")} else {none},
 [Claim], [Evidence],
 [Masks 313 and 471 are irreducible over F₂], [Named build/audit; J1 source review; J2 blind derivation; J3 printed type and binding],
 [Canonical GF(2¹⁷) Frobenius order 17 and stated minimal polynomial], [Same three joints; exact canonical field and factor definitions; no open hypotheses])

#image("diagram.svg", width: 100%)

== What was checked
Original run 40591043322 passed 89 targets and controls. New run 40636717165 supplies both named type printouts; its overall result remains 88 verified and one nested-toolchain infrastructure failure, with its separate smoke tests skipped after setup failed. J3 matched all four receipt hashes, 65 workspace inputs, ten verifier inputs, the generated 49-module root and ZIP digest. Both named axioms lists contain only propext, Classical.choice and Quot.sound.

A later completed control job, 122925704081 in run 40719320437, reported 323 tests passed using real Lean 4.22. Source comparison binds the unchanged cache worker and session tests; this later evidence does not rewrite the earlier failure or replace the pinned Lean 4.35 mathematics checks.

== Independence and limits
The prospective addendum was pushed at dee666eb7d before J3 dispatch. The three-joint checker passes with the previously sealed J2 serialization projection; raw-schema and sparse-checkout failures remain archived. J3's report discloses its lease lapse and runtime metadata limits. No sibling reports were read by J3. No independent kernel rechecker or installed-dependency cleanliness audit was performed.

The runner representation, arithmetic refinement, canonical-field conjugacy, complete invariant-subspace/constructor coverage and archived-output binding remain open. Historical yield and performance graphs are unchanged. Current-head CI and merge gates remain separate delivery obligations.

#text(size:8pt)[Sources: inputs.json; reports/TASK-20261028-68ff01/report.md and seal.sha256; machine/repair-kernel-controls.json; machine/independence-composed-materialized.txt. Original round: REVIEW-BINSTD-20261027-b17d. Archive: TASK-20261028-6fe548; Conductor T-753.]
