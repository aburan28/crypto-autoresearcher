# FROB C5 successor direct-trace technical review — 2026-10-27

This packet reviews the mathematical successor replay on the three frozen degree-five quotient algebras. It makes no official experiment or hypothesis-status transition. The original Sage process's loaded-source custody and historical C5 verdict remain open in [the problem record](../../problems/frob-c5-factor-kernel-and-model-bridge.md). C8, full experiment success, ECDLP cost, and performance are outside the scope.

## Bound claim and inputs

The [precommitted review plan](review-plan.yaml) at `dd4afa8950a12ec3aff5697c8a1ccd0bf4c0834a` fixes the exact claim, producer commit `ef1cf2979ef226378e0d0d9529c53fb6caedae52`, two reviewer joints, control, and blind-input boundary. [The 14-file manifest](inputs.json) has SHA-256 `f0e83bd8572c205dc0417293d4d8c90332a4d705a3b630c5768ab38989c860e5`. The blind arithmetic reviewer received only the [isolated mathematical statement](blind-statement.json), SHA-256 `17ba164feb8a59ba91346448befaf8ca56e8318de2cc53d6f950a377cbff45e2`, before sealing.

The producer's [successor report](../../docs/reports/2026-10-25-frob-c5-direct-trace/REPORT.md) asserts that direct repeated-q-power polynomial arithmetic produces a five-term trace matrix equal entrywise to `h(M)` from a separate source-bound matrix replay, with rank one, nullity four, and base-field image for `q=11,13,19`. The native outputs contain moduli and C5 flags but no serialized `M`; the earlier [matrix replay](../../docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json) reconstructs it. The original Sage process and historical `T_equals_hM` flag are separate evidence.

## Coordinator machine checks

The [machine receipt](machine/replay-check.json) records that all 14 manifest files matched both disk bytes and the pinned producer Git blobs. `recheck_direct_trace.py` reproduced frozen `replay.json` byte for byte under ordinary Python and `python3 -O`; all three hashes are `4188f268e95ae37539153fe59281dd3f4e267d3cf38fd09afec4a3e24aea99cb`. A modified native output failed with `native output hash changed`; a modified prior matrix replay failed with `source-bound replay hash changed`; neither wrote an output file. The built-in q=13 matrix mutation was rejected. No scientific trial, Sage process, EKS job, or local Lean build was launched for this packet.

The code for the direct path is pinned at SHA-256 `9673e46c0abf1548e2d27f5ae5b48f9c0cba445166b23d90ba90d3094e7eb720`; the prior matrix replay is pinned at `22bcbdbdc6dd8c020456549cb1aa2edf887422cb10912105d9fa0508a6ee1005`. These byte checks and controls establish reproducible execution of the successor checker on pinned files. They do not authenticate what the old Sage subprocess loaded.

## Independent review and claim table

The [J1 source and fidelity review](reports/TASK-20261027-fc5-j1/report.md) and [J2 blind arithmetic review](reports/TASK-20261027-fc5-j2/report.md) were sealed separately. Their SHA-256 manifest hashes are `439e8b9bcab37b38092f478415212811836cdddba86f7b69f172290581e41294` and `590433baccfaa41b34e27a2d4672d034ec4ef74a55cf81d9796440120e968de2`. Both manifests were verified. The [stock independence checker receipt](machine/independence-check.json) reports `PASS: 2 report(s), every joint owned and attested, blindness respected, controls declared`. That checker tests the declarations and plan structure; it cannot prove that a reviewer told the truth about what they read.

J1 independently checked the source bindings, exact native envelope, direct code path, prior matrix replay, and 13 controls under each of ordinary Python and `-O`; all passed. J2 started from the isolated mathematical statement and independently derived the complete five-term and q-power matrices. In each cell all 25 direct entries agree with the matrix sum; the direct trace has the following only nonzero row, rank one, nullity four and image exactly the constant line:

| q | Nonzero row | Rank / nullity |
| ---: | --- | --- |
| 11 | `[5, 9, 4, 3, 5]` | 1 / 4 |
| 13 | `[5, 5, 12, 8, 1]` | 1 / 4 |
| 19 | `[5, 16, 9, 11, 5]` | 1 / 4 |

The planned known-false q=13 four-term sum has rank five, nullity zero, and image the whole quotient. J2's witness is `T₄(x)=1+x+9x²+11x³+9x⁴`. J2 also independently checked the exact degree-five irreducibility criterion for all three moduli; this is executable arithmetic evidence, not a Lean irreducibility proof.

J1 tested an `M²` substitution at the internal `check_cell` boundary: the trace polynomial accepts it because `h(M²)=h(M)`. Consequently trace equality alone does not certify every entry of `M`; the separate source-bound matrix replay and input hashes are load-bearing. The top-level checker rejects modified replay bytes. This is a limitation of inference, not a discrepancy in the three direct trace matrices.

| Claim | Machine status | Fidelity | Review outcome | Evidence and limit |
| --- | --- | --- | --- | --- |
| Successor direct five-term trace on the three pinned quotient algebras | passed | faithful_scoped | validated_scoped | [machine receipt](machine/replay-check.json), [J1](reports/TASK-20261027-fc5-j1/report.md), [J2](reports/TASK-20261027-fc5-j2/report.md), [independence check](machine/independence-check.json); only these three fixed cells |
| Historical Sage `T_equals_hM` and original C5 success flag | not_verified | partial bridge | inconclusive | Loaded-source custody is absent; [problem record](../../problems/frob-c5-factor-kernel-and-model-bridge.md) remains open |
| Fresh Lean kernel and axiom verification of adjacent quotient theorems | not_verified | not_reviewed | inconclusive | Earlier formal receipts are contextual; this review ran no fresh pinned Lean gate |
| C8, full success, ECDLP cost or performance | not_verified | not_reviewed | inconclusive | Outside this packet |

## Visual and downstream effects

The editable [boundary diagram](boundary-diagram.svg) shows the two successor arithmetic paths, negative control, and the historical process boundary. [The PDF](report.pdf) embeds it and was rendered and visually inspected. This review supplies no measured performance value or official decision, so it changes no canonical performance graph or public dashboard metric. It adds this validation boundary diagram to the technical packet.

The next historical-control step remains an authenticated original execution receipt or a separately adjudicated replacement run with a fail-closed C5 gate. A Lean field bridge would also need the frozen moduli's irreducibility and an explicit connection from quotient algebra to named fields; the current quotient theorems do not establish historical process custody.
