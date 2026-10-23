#set page(margin: 24mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set heading(numbering: "1.")

= Concrete finite Semaev first-fall witness
2026-10-23 · One archived Boolean draw · Machine-checked finite proof

The frozen sample is $n=4$, $n'=4$, seed 32201, $x_R=1$, basis $[9,3,2,12]$. Its equation SHA-256 is `89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb`. No new experiment or performance measurement was run.

== Exact certificate
XOR 23 of 80 degree-three rows using selector `1321682796735964`. The result has monomial masks `1, 2, 4, 8, 9, 10, 12, 16, 18, 20, 32, 40, 48, 64, 65, 128, 144, 192`, all of degree at most two. The linear functional consisting of coefficients at masks 80 and 192 is zero on all 28 degree-two rows but one on this result. It therefore lies in the degree-three row space and outside the degree-two row space. Adding it raises the latter rank from 11 to 12.

#figure(image("row-space.svg", width: 100%), caption: [Exact dimensions from the source-binding receipt; no sampling uncertainty.])

== Checks and scope
`ConcreteFirstFallWitness.concreteNewFall` is compiled with pinned Lean 4.35.0-rc1. A source-binding checker replays the literal archived equations, row order, XOR, separator and rank extension. Full build, axiom audit and formal target verification are recorded in `evidence/concrete-proof.json`; row and source hashes are in `evidence/source-binding.json`.

This proves one finite Boolean-model witness. Independent semantic review, generic rank semantics and symbolic descent, additive correction of historical wording, and any ECDLP cost inference remain open. The existing archived-versus-corrected draw chart and performance dashboards have no changed data.
