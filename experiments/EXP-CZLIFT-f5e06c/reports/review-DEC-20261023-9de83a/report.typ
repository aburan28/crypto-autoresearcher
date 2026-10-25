#set page(paper: "a4", margin: 15mm)
#set text(font: "DejaVu Sans", size: 8.6pt)
#set par(justify: false)
#show heading: set block(above: 1.0em, below: 0.5em)

#text(size: 15pt, weight: "bold")[EXP-CZLIFT-f5e06c: evidence review]
#linebreak()
#text(size: 10pt)[Decision report for DEC-20261023-9de83a, hypothesis H-CZLIFT-bd2017, goal GOAL-CZLIFT-1516d5]

#table(
  columns: (auto, 1fr),
  stroke: 0.4pt + gray,
  inset: 4pt,
  [*Decision*], [`refine`. H-CZLIFT-bd2017 moves approved → analyzed (DEC-20261023-9de83a). H-CZLIFT-889c9d and H-CZLIFT-6d4ed1 are not moved here; separate review tasks decide them.],
  [*Evidence*], [EV-CZLIFT-e9a7cf, direction `supports` for the exact clauses only],
  [*Strength*], [`replicated` for the exact clauses (torsion clauses same-code); `inconclusive` for the 1/p clauses; tier clause not met as posed],
  [*Claim tier*], [`toy`. The largest field is $FF_p$ with $p = 97813 < 2^(17)$. The specification's "medium" label is a mislabel.],
  [*Runs*], [RUN-CZLIFT-032a92 (seed 20261009), RUN-CZLIFT-6447f0 (seed 20261010)],
  [*Tasks*], [producer TASK-20261009-951dfd; snapshot TASK-20261009-046d5b; run archive TASK-20261009-4ac56e; validation TASK-20261022-65e6c1; red team TASK-20261023-e5df50; ledger archive TASK-20261023-4d7449],
  [*Knowledge*], [nothing promoted (the decision is refine; see the decision record's `knowledge_promotion`)],
)

== Exact scoped claim

At toy tier, the largest field being $FF_p$ with $p = 97813 < 2^(17)$. The data are two clean runs (RUN-CZLIFT-032a92 and RUN-CZLIFT-6447f0) of the unmodified lane-1 drivers over a new sampler with $10^4 <= p <= 10^5$.

- *Anomalous arm.* 41 distinct class-number-one CM anomalous curves ($D in {-3, -11, -19, -43, -67, -163}$) at precision $p^8$. The j-distance degeneracy rule agreed on all 4608 rows (164 curve × lift-class cells). Smart's ratio equalled $d$ on all 1152 `pert_p` rows, and every canonical, isomorphic and `pert_p2` row degenerated.
- *Torsion arm.* 48 distinct odd-order curves ($n in [109, 93001]$) at precision $p^4$. The five torsion-section rates and the tau-ratio identity held on all 576 pairs (same-code evidence).
- *Non-canonical recoveries.* 0 successes in 3456 anomalous-degenerate rows and 0 in 576 rows per torsion section. The 95% one-sided bounds are $8.7 times 10^(-4)$ and $5.2 times 10^(-3)$ per row; these do not test the 1/p rate.

No claim is made about 33 to 96-bit fields, a deployed curve, or any attack cost.

#figure(
  image("graph.svg", width: 100%),
  caption: [Panel A shows one-sided 95% Clopper-Pearson upper bounds on the per-row exact-hit success rate (0 successes in every cell), against the recorded mean 1/p (the prediction) and the $p^(-1\/2)$ range of the tested primes. The bars are drawn by `plot.py` from recorded p lists. The torsion bounds are per section, because the three sections share $(P, d)$ draws. Panel B shows the red team's operating characteristic of the frozen $|z| <= 4$ clause. Rate 0 passes it with probability 1.000 and the predicted 1/p with probability 0.900. Runs RUN-CZLIFT-032a92 and RUN-CZLIFT-6447f0.],
)

== Observation

- *Validity.* Both planned runs are present: `completed_valid`, `output_validated`, seeds as frozen, `code.dirty: false`, 0 dropped rows. Manifest metrics equal the raw results (141/141 per seed), a full replay is byte-identical, and the blind re-derivation agrees (VAL-20261022-1d018a). Wall time was 10.85 s and 11.21 s.
- *Anomalous arm*, both seeds:
  - `rule_agreement` is 1.0 with 0 disagreements in 2304 rows per seed;
  - Smart ratio $= d$ on 576/576 nondegenerate rows per seed, all `pert_p`;
  - 1728 degenerate rows per seed with 0 next-digit successes, against 0.0591 and 0.0557 expected under 1/p;
  - recorded z is $-0.2432$ and $-0.2361$;
  - lift distances: $v_p(j - j_"CM") = 1, 2, 8$ at $e = 1$ and $3, 6, 8$ at $e = 3$.
- *Torsion arm*, both seeds:
  - the five torsion rates are 1.0 on 288/288 pairs;
  - `identity_rate` is 1.0 in all 9 section × arm cells, with the non-vacuity control holding (`homomorphism_rate_prec2` 0.0);
  - 0/288 successes per section;
  - arm-difference z is null;
  - mean torsion lift cost is 107.17 and 107.75 complete additions, within the bound.
- *Driver sources*, read in this review:
  - the anomalous driver draws a fresh $(P, d)$ per row (`EXP-CZLIFT-17b7eb/implementation/run.py`, lines 79-86);
  - the torsion driver reuses each $(P, d)$ across the three sections (`EXP-CZLIFT-ae0a13/implementation/run.py`, lines 80-118);
  - both count points in $O(p)$ (`harness/toycurve.py`, lines 80-81).

== Comparison

- *Frozen criteria.* The success criterion is met on both seeds; the falsification criterion is not.
- *Against the toy runs* (EXP-CZLIFT-17b7eb, $p <= 1500$; EXP-CZLIFT-ae0a13, $p <= 600$): the same exact outcomes recur on new curves with $p$ up to 97813.
- *Rule disagreement.* With 0 disagreements, the 95% bound is 1.81% per curve × class cell.
- *Torsion failures.* With 0 failures, the 95% bound is 0.52% per pair.
- *1/p clauses.* The bounds are $1.73 times 10^(-3)$ per seed and $8.66 times 10^(-4)$ pooled on the anomalous arm (51× to 54× and 26× the mean 1/p). On the torsion arm they are $1.03 times 10^(-2)$ per seed and $5.19 times 10^(-3)$ pooled per section (352× to 395× and 187×).
  - P(all zero | 1/p) = 0.850, so the likelihood ratio of 1/p to rate 0 is 0.85.
  - The recorded z equals the design-only value $-sqrt(sum 1\/p_i)$ to $1.2 times 10^(-15)$.
  - One success on seed 20261010 would give $z = 4.0001$.
- *Against $p^(-1\/2)$*, whose range over the tested primes is $[3.35, 9.24] times 10^(-3)$ (anomalous) and $[3.20, 10.0] times 10^(-3)$ (torsion):
  - the anomalous bounds lie below the whole range;
  - the pooled torsion per-section bound lies inside it.
- *Correction to the red team.* Its all-sections common-rate torsion bound ($1.73 times 10^(-3)$, $n = 1728$) assumes independent rows, which the driver does not provide, so it is not used.
- *Tier.* Fields of at most 17 bits are toy by the mechanical rule, so the tier clause cannot be met by this design.

== Inference

- *Exact clauses.* At toy tier, with $p$ up to $10^5$, the exact clauses of H-CZLIFT-889c9d and H-CZLIFT-6d4ed1 hold with no exception on new curves, on two seeds. The anomalous valuations have independent-code corroboration; the torsion identities have same-code evidence only. The identities follow from stated derivations (Serre-Tate splitting, $"Hom"(ZZ\/n, ZZ_p) = 0$, Smart's theorem) whose mechanism does not depend on $p$. The run therefore adds instance coverage, not a new regime.
- *1/p clauses.* These are inconclusive: the data do not distinguish 1/p from 0. The anomalous bound excludes a $p^(-1\/2)$ rate at every tested $p$; the torsion per-section bound alone does not.
- *Tier clause.* This fails on policy grounds, not because of a measurement, so no adverse transition is taken and no refutation artifact is needed.
- *Decision.* The decision is `refine`, not support or inconclusive.
  - Support would endorse a tier move the data cannot carry and an untested rate clause.
  - Inconclusive would discard a clean exact replication.
- *Earlier reading.* The reading in DEC-20261009-44c288 that success rates "stay at 1/p", and its "medium tier" boundary, are not adopted.

== Limitation

- Toy tier only; no transfer argument to 33 to 96-bit fields or to a deployed curve.
- Same-code torsion replication.
- 41 of 84 anomalous curves sampled, not a census.
- The $e = 3$ threshold 6 is not distinguished from 4 or 5.
- Exact-hit counting cannot see partial leakage of $d$, because rows record no $d$ or ratio.
- The structured small-$d$ stratum is hit in about $1.5 times 10^(-4)$ of rows.
- The "1/p rate" is an unnumbered random-model assumption in all three hypotheses.
- The arm contrast confounds lift type with curve type.
- No memory figure is recorded and no package versions are pinned.

== Next actions

+ *Ranked first; this is the goal's next action.* A numbered-heuristic validation contract, designed through `/design-experiment` from a refined hypothesis. The heuristic: the Smart (tau-) ratio of the `hensel_random`, `naive` and `teichmuller` sections is uniform on $FF_p$ and independent of $d$. The contract should:
  - use a new driver that records $r$ and $d$ per row;
  - pre-register residue-uniformity, independence and near-miss tests with tail checks;
  - add a structured-$d$ stratum, a CM non-canonical-lift torsion arm, and the census of all 84 anomalous primes in $[10^4, 10^5]$;
  - state the unit of analysis.

  Toy tier suffices for power. It is not approved here.
+ The separate reviews of H-CZLIFT-889c9d and H-CZLIFT-6d4ed1 should cite the EV-CZLIFT-e9a7cf clause readings: no medium tier, 1/p inconclusive, same-code torsion evidence, arm difference not evaluated.
+ Optional: an independent implementation of the torsion section, folded into the first action.
+ Deferred: the red team's 33 to 96-bit exact-clause successor. Its information value is low because the clauses are $p$-independent consequences of theorems. It also needs a new driver, because the lane-1 drivers count points in $O(p)$.

== Reviews and links

- Validation (passed; J1, J2, J3 and PTM-1 hold): #link("../validation-20261022/validation_report.yaml")[`reports/validation-20261022/validation_report.yaml`]
- Red team (R1 breaks, R2 breaks, PTM-1 holds): #link("../redteam-20261023/redteam_report.yaml")[`reports/redteam-20261023/redteam_report.yaml`] and #link("../redteam-20261023/rt_power_and_design.json")[`rt_power_and_design.json`]
- Records: `ledger/evidence/EV-CZLIFT-e9a7cf.yaml`, `ledger/decisions/DEC-20261023-9de83a.yaml`, `experiments/EXP-CZLIFT-f5e06c/analysis.md`
- Earlier run reports: none exist for this experiment (no `reports/run-*/` directory). Run records are under `experiments/EXP-CZLIFT-f5e06c/runs/`.
- Canonical graphs: none for this lane; `knowledge/frontiers/` has no CZLIFT graph, so nothing was refreshed.
- Graph source: `plot.py` reads `plot_data.json` (recorded values and red-team computations, with run IDs) and writes `graph.svg`.
