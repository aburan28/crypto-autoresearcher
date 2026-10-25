# P-256 factor-base parallel investigation, 25 October 2026

The eight directions in [the original plan](plan/original-week-plan.json) are being implemented and inspected in parallel under the user’s instruction to begin today. [The worklist](today-worklist.json) assigns six disjoint tasks. This folder tracks implementation checks and mathematical screens; it is not an approved performance experiment or an official hypothesis transition.

| Track | Work | Output |
| --- | --- | --- |
| F1 | Implicit symmetric bases and shifted torus cosets | [Artifacts](tracks/f1/) |
| F2 | Auxiliary elliptic curves and isogeny-defined bases | [Artifacts](tracks/f2/) |
| F3 | Coefficient-labelled bases and a single useful relation | [Artifacts](tracks/f3/) |
| F4 | Nonuniform divisor relations and partial-relation stitching | [Artifacts](tracks/f4/) |
| F5 | Isogenous representatives of the target curve | [Artifacts](tracks/f5/) |
| F6 | Interval or digit-box bases with lattice-assisted solving | [Artifacts](tracks/f6/) |
| F7 | Auxiliary covers and compatible branch geometry | [Artifacts](tracks/f7/) |
| F8 | Endomorphism-orbit factor bases | [Artifacts](tracks/f8/) |

Each producer retains code, exact checks, assumptions, failures and a next discriminating action. The final report will distinguish actual published-field checks from arguments about scaling and from unrun scientific trials. No speed advantage follows from a compact representation or a constructed successful relation.

Inputs in `baseline/` are copied from the earlier local Dickson inspection and plan. They are reference data, not fresh output. The original plan is preserved; today’s instruction changes execution priority, not historical evidence.
