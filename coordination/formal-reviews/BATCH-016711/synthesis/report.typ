#set page(paper: "a4", margin: 17mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set heading(numbering: none)
= Concrete Semaev finite witness review
_Batch BATCH-016711 · 31 October 2026_

*Outcome: validated_scoped.* For the single archived Boolean S3 draw (n=4, n′=4, seed 32201, draw 1), the explicit degree-three row combination gives a degree-at-most-two vector outside the degree-two row span. The source, theorem and blind finite calculation were independently reviewed.

#figure(image("structure.svg", width: 100%), caption: [Independent joints and exact finite row-space dimensions.])

== Exact evidence

- *J1, TASK-20261031-f17d2a:* four archived ANFs and 28/80 ordered parity rows matched Lean literals and the 23 selected indices. A changed archive failed the pinned source binder; set-union multiplication gave three spurious monomials.
- *J2, TASK-20261031-4870db:* the named `concreteNewFall` theorem has the finite proposition `witnessVec ∈ lowDegreePartThree ∧ witnessVec ∉ rowSpaceTwo`. The hosted named receipt SHA-256 begins `66325561`; its transitive axioms are `propext`, `Classical.choice`, and `Quot.sound`. A false separator fails on degree-two row 0.
- *J3, TASK-20261031-068004:* from the isolated parameter card, the D2 span rank is 11, the D3 span rank is 53, and the low-degree intersection rank is 12. The explicit 23-row combination is separated by `c80+c192`; parity and mutation controls pass.

The frozen plan and three attestations pass the composed independence checker with zero findings. The named machine receipt comes from GitHub Actions run `41155781140`, job `124402203382`, at CI merge `232f4e78`; J2 checked 68 workspace and 10 verifier input hashes. No local Lean build was run. PR #2814's formal check was scope-skipped and is not counted as a second theorem build.

== Claim boundary and custody

The statement is about the one finite F16 Boolean system and its 256-coordinate vectors. J1 binds that system to the archived draw; the theorem itself contains literal equations. A different draw needs a new binding and check. This packet changes no experiment or hypothesis status. Reviewer raw files and SHA-256 values are in `reviews/` and `review-artifact-hashes.json`; the source-linked narrative is `review.md`.
