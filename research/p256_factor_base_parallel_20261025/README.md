# P-256 factor-base parallel investigation, 25 October 2026

All eight directions in [the original plan](plan/original-week-plan.json) have a completed first implementation or theory-screen pass. [The worklist](today-worklist.json) records the six initial parallel tasks. This folder tracks implementation checks and mathematical screens; it is not an approved performance experiment or an official hypothesis transition.

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

Each producer retains code, exact checks, assumptions, failures and a next discriminating action. The final report distinguishes actual published-field checks from arguments about scaling and from unrun scientific trials. No speed advantage follows from a compact representation or a constructed successful relation.

Inputs in `baseline/` are copied from the earlier local Dickson inspection and plan. They are reference data, not fresh output. The original plan is preserved; today’s instruction changes execution priority, not historical evidence.


Current same-day outputs are summarized in [report.md](report.md) and [the inspected aggregate PDF](report-delivery.pdf), with machine-readable state in [status.json](status.json). The owner explicitly approved public publication on 25 October 2026; [the publication addendum](archive/publication-approval-20261025.json) records the scope and prior checkpoint. Earlier delivery audits and reports retain their historical publication-pending state. Local independent checks carry [a recorded custody exception](reviews/local-custody-exception.json); publication does not discharge canonical scientific promotion gates.

Track PDFs are named `report-delivery.pdf`; all were inspected. [F3 coefficient clarification](corrections/f3-coefficients-mod-r.md) qualifies its original lemma without changing sealed evidence. [P-224/Curve448 comparisons](comparisons/p224-curve448/report.md) and [the Cartier-component derivation](analysis/cartier-proposal/derivation.md) extend the initial pass.
