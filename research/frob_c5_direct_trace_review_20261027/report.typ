#set page(paper: "a4", margin: 1.5cm)
#set text(font: "Libertinus Serif", size: 10pt)
#set heading(numbering: "1.")

= FROB C5 successor direct-trace review
2026-10-27 · Technical packet · no scientific-status transition

== Claim and evidence boundary
The reviewed successor replay computes the five-term trace by direct repeated q-power polynomial arithmetic on three fixed degree-five quotient algebras over q = 11, 13, 19. It then compares all 25 matrix entries per cell with h(M) from the separately source-bound q-power matrix replay. The original Sage process and its C5 flag are outside this arithmetic replay.

The precommitted plan is `review-plan.yaml` at `dd4afa8950`. The 14-file input manifest is `inputs.json` (SHA-256 `f0e83bd8572c205dc0417293d4d8c90332a4d705a3b630c5768ab38989c860e5`). The blind statement is `blind-statement.json` (SHA-256 `17ba164feb8a59ba91346448befaf8ca56e8318de2cc53d6f950a377cbff45e2`).

#image("boundary-diagram.svg", width: 100%)

== Reproducibility and controls
All 14 pinned inputs match both their disk bytes and the producer Git tree. Ordinary Python and optimized `python3 -O` regenerate the frozen replay byte for byte; each output SHA-256 is `4188f268e95ae37539153fe59281dd3f4e267d3cf38fd09afec4a3e24aea99cb`. Native-output and prior-matrix tampering fail before producing an output. The q=13 matrix-entry mutation fails. Details and exact source hashes are in `machine/replay-check.json`.

Trace equality does not uniquely identify M: the J1 reviewer found that h(M²) can equal h(M). The separately bound matrix replay and source hashes are essential. Neither successor path authenticates the historical loaded Sage code.

== Verdict and next steps
Both independently sealed reviewers report `holds` for their assigned joints. J1 reproduced the checker and its 13 controls in ordinary and optimized Python. Blind J2 derived all three trace matrices and found rank 1, nullity 4, and the constant-line image in each; its q=13 four-term wrong-length control instead has rank 5 and full image. The stock independence checker passed both attestations.

The successor three-cell arithmetic verdict is *passed / faithful_scoped / validated_scoped*. This verdict is limited to the pinned quotient inputs and executable replay. No fresh Lean theorem build or axiom audit was run for this packet. The historical loaded-source custody and original C5 success flag remain open; C8, full experiment success, ECDLP cost, and performance are outside scope. A future run needs a fail-closed C5 gate and a process receipt binding loaded source and environment.
