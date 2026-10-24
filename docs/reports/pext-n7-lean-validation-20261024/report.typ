#set page(paper: "a4", margin: 19mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set heading(numbering: "1.")

= PEXT n=7 Lean build correction
2026-10-24 · EXP-PEXT-212d5c · H-PEXT-d536a1 · Lean 4.34.1

*Scope.* Source and proof-build validation only. No experiment run, scientific review or state transition.

== Observation

The source at autoresearcher main `dcfdd16cdf` failed `lake build CoverCensusN7`. The orbit theorem omitted an out-of-range branch; two finite `decide` proofs reached Lean's default recursion depth. The failed declarations reported `sorryAx`.

The correction explicitly discharges the twenty permitted orbit cases and scopes a higher recursion limit to the two finite proofs. It changes no theorem statement, finite enumeration function, spectrum list or experiment protocol.

The corrected pinned build completed. Eight named theorem constants report only `propext` and `Quot.sound`, or no axioms. The source SHA-256, exact command and per-theorem audit are in `receipt.json`; the build output is `fixed-build.log`. Local controls accepted the intact audit and rejected a missing theorem report and injected `sorryAx`.

#figure(image("diagram.svg", height: 90mm), caption: [Build result and remaining proof boundary. Solid arrows are locally checked steps; the dashed arrow marks claims outside these theorems.])

== Limit

The full n=7 genus-floor hypothesis remains unproved by this Lean file. Arbitrary sigma-set decomposition, placement enumeration, cross-ratio, genus formula and isogeny-class transfer remain outside the kernel-checked scope. The approved trial and independent review remain necessary before a scientific or attack-cost claim.
