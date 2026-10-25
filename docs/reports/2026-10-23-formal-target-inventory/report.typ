#set page(margin: 24mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set heading(numbering: "1.")

= Current-main formal target declaration audit
2026-10-23 · Source commit `d513b75233` · Operational proof validation

== Pinned checks
The current source has 83 target specs and 83 corresponding theorem files. The Lean 4.35.0-rc1 main workspace built 8,975 jobs and audited 652 theorem declarations with standard axioms only. A generated batch checked all 82 named main-workspace targets: 74 use only `propext`, `Classical.choice`, or `Quot.sound`; eight use no axioms. The separate Lean 4.22.0 scoped target built and passed its zero-axiom audit.

#figure(image("target-gates.svg", width: 100%), caption: [Exact declaration and build checks at the named main commit.])

== Source binding and limits
`check_target_audit.py` binds all 148 tracked formal files, all 83 specs, the generated batch source and the raw logs. `evidence/audit.json` records the hashes. Negative controls rejected a changed batch source, injected `sorryAx`, and optimized Python. This is a one-pass inventory and kernel check. A linked open problem names the claim-to-theorem and source-review gap. The separate per-target verifier, independent semantic review, experiment replay, and any performance claims remain outside this result. No scientific graph or dashboard data changed.
