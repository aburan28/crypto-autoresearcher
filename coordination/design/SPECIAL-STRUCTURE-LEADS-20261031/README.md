# Special-structure leads: draft experiment designs (2026-10-31)

Ten draft `experiment.protocol/v1` records, one per lead, written by parallel design agents from the ideation
reports in `docs/reports/ecdlp-special-structure-leads-20261031/`. **Status for every design: `review_required`,
unfrozen, not approved, not run.** Each `protocol.json` passes `python3 tools/experiment_protocol.py validate`;
freezing, approval (`tools/experiment_preapproval.py --packet`) and dispatch belong to the Coordinator. Before any run
starts, `scripts/checkpoint.sh` must have pushed a resume checkpoint (AGENTS.md, "Resume checkpoints in S3 before
every run"). Probe scripts in a design directory are short foreground checks of a construction, not results.

Claim boundary: toy and public parameters only; no secret scalar, no attack on a deployed key.

| design | lead it advances | expected result | cost (estimate) | what the probes already changed |
| --- | --- | --- | --- | --- |
| `koblitz-analogue` | LEAD-STR-small-cm-disc-nonunit-endo (idea IDEA-20261031-6610ed) | net loss, 4 to 10 times at h = 19 to 23 | 20 to 30 min on 4 cores | group order is 4l, not prime; only h = 19 and 23 are equality cases |
| `arithmetic-rigidity` | LEAD-STR-isogeny-class-generic-invariance, LEAD-RHO-matched-rho-calibration | null | about 1 h on 4 cores plus about 3 days to write a Rust rho | no prime-field rho exists in the checkout; index calculus capped at 28 bits |
| `minors-guess-and-determine` | LEAD-EXO-minors-guess-and-determine (new) | loss, exponent at or above 1/2 | under 1 h, 3 to 4 days to implement | algorithm is a reconstruction from abstracts; read full texts before freezing |
| `kernel-of-reduction` | LEAD-TRF-kernel-of-reduction-lemma (new) | floor not inherited, lattice-index scaling inherited | about 1 core-hour, 3 to 4 person-days | minimum over fibres is a theorem (height at least 4); the test must read a prescribed fibre |
| `lattes-xline-dynamics` | LEAD-EXO-lattes-xline-dynamics (new) | k-independence of the preimage-tree multiset | about 40 min, 1.5 days | claim holds only for d coprime to the order of P |
| `level-structure-torsor` | LEAD-STR-level-structure-torsor (new) | closure, but PO-1 (gonality over F_p) is unproved | minutes, 4 to 5 days | lead cannot close by derivation alone |
| `curve-aware-ggm` | LEAD-STR-class-group-ecdlp-bridge | all clear for the tested oracle set | about 2 core-hours, 3 to 4 weeks | N dividing p - 1 is impossible at prime order; uses cofactor 2 |
| `volcano-transport-cost` | LEAD-STR-isogeny-class-generic-invariance, LEAD-STR-isogeny-transport-preprocessing | loss at toy size | about 1.5 h, 4 to 6 days | q^0.4 is below sqrt: the exponent alone does not close it; paper read at abstract level only |
| `miller-kummer` | LEAD-EXO-miller-pairing-cocycle, LEAD-TRF-miller-cocycle-nonhom-transfer | flat spectrum, leads collapse | about 1.5 h, 3 to 5 days | circular Kummer-on-Velu test dropped |
| `ulmer-specialisation-control` | LEAD-TRF-function-field-xedni-lift, LEAD-ICP-xedni-function-field-sections | finder falsifier fires, which corrects the report but does not reopen the leads | about 4 h, 3 to 4 days | finder looks table-free at weight 2; the report's permutation null is invalid |

Order the Coordinator might use, cheapest informative first: `koblitz-analogue`, `lattes-xline-dynamics`,
`miller-kummer`, `kernel-of-reduction`, `minors-guess-and-determine` (after reading the papers), then the rest.
