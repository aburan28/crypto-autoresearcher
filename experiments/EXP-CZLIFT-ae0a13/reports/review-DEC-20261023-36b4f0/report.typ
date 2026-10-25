#set page(paper: "a4", margin: (x: 1.6cm, y: 1.6cm))
#set text(size: 9.5pt)
#set par(justify: false)
#show heading: set text(size: 11pt)

= Decision report: DEC-20261023-36b4f0 (EXP-CZLIFT-ae0a13)

*Decision: support H-CZLIFT-6d4ed1, scoped.* Hypothesis status `approved` → `supported`. Evidence `EV-CZLIFT-ad28f5`: direction supports, strength *replicated*, claim tier *toy* for the measured clauses, proof status *derivation* for the torsion-section and tau-identity clauses. Knowledge promotion `KN-FIND-7e2b94`. No attack, cost-to-break or hardness claim; no experiment approved; RQ-CZLIFT-b9f765 not closed. Not official until the isolated ledger archive carrying this decision is verified and pushed.

== Identity
- Experiment `EXP-CZLIFT-ae0a13` (frozen v1, approved by `DEC-20261009-a3797d`), hypothesis `H-CZLIFT-6d4ed1`, question `RQ-CZLIFT-b9f765`, goal `GOAL-CZLIFT-1516d5`, batch `BATCH-2e44f7`.
- Runs `RUN-CZLIFT-dab752` (seed 20261009) and `RUN-CZLIFT-5b2581` (seed 20261010); executor `TASK-20261009-e0b32d`; observation archive `DEC-20261009-9f9254` (ledger archive `TASK-20261009-ea3bbc`).
- Independent validation `TASK-20261022-93fb1c` (`VAL-20261022-31a388`, passed): #link("../validation-20261022/validation_report.yaml")[`reports/validation-20261022/validation_report.yaml`].
- Red team `TASK-20261023-1d45b5` (`RT-20261023-5636c1`; R1 holds, R2 breaks, PTM-1 holds): #link("../redteam-20261023/redteam_report.yaml")[`reports/redteam-20261023/redteam_report.yaml`].
- Analysis: `experiments/EXP-CZLIFT-ae0a13/analysis.md` (derivation note in section I-A). No `reports/run-*/` folder exists for this experiment; the run records are the manifests under `runs/`.

== Scoped claim
Scope: ordinary `E/F_p` with p ≥ 5, a subgroup `<P>` of prime order n ≠ p, any `Z_p`-lift `E^` with good reduction.

*By derivation, uniform in p* (`analysis.md` I-A, lemmas D1–D6; red-team R1): the n-torsion section `s_tor` is the unique homomorphic (equivalently `[c]`-equivariant) section of reduction over `<P>`; it commutes with every `Z_p`-endomorphism of `E^` preserving `<P>` and, on the canonical lift, is the unique Frobenius-fixed section; it is independent of the Hensel start and computable in at most `2(bits(n)+bits(p^k))+1` complete additions at precision k; the Smart functional `z([n]s(R))` vanishes identically on it; for every section s the Smart ratio equals the leading-digit tau-ratio, `tau_R = s(R) - s_tor(R)`; and `s_tor` carries the discrete-log relation isomorphically into `E^(Q_p)[n]`, no easier. Hence the user's H2 clause "a computable canonical section would be a full break" is *false* under every reading in which "canonical" constrains the section, and circular under the one remaining reading (a section whose Smart residue recovers d is a discrete-log oracle by definition).

*Measured at toy scale* (50 ≤ p ≤ 600, 11 ≤ n ≤ 613, k = 4, 36 curves per seed, two seeds; `RUN-CZLIFT-dab752`, `RUN-CZLIFT-5b2581`): for the `hensel_random`, `naive` and `teichmuller` sections, no identity-readout success rate meeting the predefined 4-sigma threshold was observed on the CM-canonical or the arbitrary-integer lift. Per arm and seed the frozen test excludes only excesses of about 4.2x–5.2x of 1/p and above; a uniform leak at rate `p^(-1/2)` is excluded with power ≥ 0.989.

*Not claimed:* that the non-torsion sections carry no information about d; that every non-canonical section recovers d only at 1/p; that the canonical curve lift contributes nothing structurally; anything about anomalous curves, global lifts, other readouts, or cryptographic sizes.

== Graph
#figure(image("graph.svg", width: 100%), caption: [(a) `v_p(z([n]s(P)))` against working precision k for `s_tor` and the naive section on three curves (red-team `rt_probe` D), and the producer's 1116/1116 pairs at k = 4 (`RUN-CZLIFT-dab752`, `RUN-CZLIFT-5b2581`); dotted: v = k. (b) Identity-readout success rate divided by the recorded per-arm mean 1/p, per section, arm and seed, with Wilson 95 % intervals and counts (successes / pairs) from the two manifests; dashed: the null (ratio 1); black bars: the frozen 4-sigma floor for that arm and seed (red-team `rt_power`). (c) Probability that each frozen rule fires on both seeds against a planted leak at c/p, on the realized rows (red team): the per-arm rule and the arm-difference rule. (d) Red-team exhaustive control over all base points and all d (4,078,200 cells per section and lift, 71 curves): successes over a same-shape random-odd-function null mean, with the null's 95 % band, recorded integral model against a perturbed lift of the same reduction.])

== Observation
- Validity (re-checked by the Coordinator from manifests and receipts): 2 of 2 trials, `output_validated`, commit `03479a00` clean, seeds as planned. Validator: 59/59 hashes, 79/79 metrics per seed recomputed with 0 mismatches, full replay 557/557 and 559/559 rows; sealed blind `s_tor` agrees on 1116/1116 pairs.
- Torsion section: canonicity, homomorphism, degeneracy, reduction and scalar-multiplication equivariance each 1116/1116; mean cost 58.04 and 55.24 complete additions over `Z/p^4`, within the bound on every row (minimum slack 15).
- `identity_rate` 1.0 on 3 × 1116 section-rows.
- Successes: seed 20261009 cm 0, 4, 1 of 371 and random 0, 0, 0 of 186; seed 20261010 cm 2, 0, 1 of 378 and random 1, 1, 1 of 181 (`hensel_random`, `naive`, `teichmuller`); frozen z from −1.38 to +1.88.
- `arm_difference` z: seed 20261009 null (0/371 vs 0/186), +1.421, +0.709; seed 20261010 −0.035, −1.446, −0.534.
- 36 of 1152 attempted samples skipped (S = O at d2 = n − 1), by a rule the specification does not state; outcome-independent.
- Secondary: `teichmuller` cm `homomorphism_rate_prec2` 0.0212 (8/378) on seed 20261010, on j = 0 curves at d2 a cube root of unity.
- Red team (own arithmetic): v = k at k = 2, 3, 4, 6, 8; exhaustive control 0.967x–1.058x of the null; Teichmuller multiplier set `mu_6` minus 1 on 16/16 canonical j = 0 lifts, `{-1}` on their perturbed lifts and everywhere else; Frobenius-lift iteration converges to `s_tor` on 16/16; planted sections with f(x) = n − x and x² pass the frozen test (|z| ≤ 1.39) while recovering d on 0.990–1.000 of pairs.

== Comparison
- Frozen success criterion: met on both seeds on every evaluable entry; the `arm_difference` `hensel_random` entry on seed 20261009 (z null) is *not evaluable*, recorded as such, not as met. Falsification criterion: not triggered. No criterion is changed; no protocol amendment is needed.
- Against the null: every per-arm cell lies below its frozen floor (panel b); the exhaustive control agrees with a same-shape null within 0.97x–1.06x (panel d).
- Against the arm control: the frozen arm-difference rule fires on both seeds with probability 0.035 at a 10x CM-arm leak and 0.909 at 20x (panel c), and the arms differ in family, p, n and class number. It is excluded from the basis. The matched-lift control shows no difference in the identity-readout rate and a structural one the frozen test cannot see (Aut-equivariance on canonical j = 0 lifts).
- Against the baseline (red team): a section "attack" costs about 60 additions per attempt with success about 1/p, about p × 60 in expectation, against `sqrt(pi n/4)` for Pollard rho: at 256 bits about 2^264 against 2^128. Dominated; no deployed system affected.

== Inference
The theorem-grade clauses follow from Hensel uniqueness and `Hom(Z/n, E^_1) = 0` for n prime to p (D1–D6); the runs confirm the instruments against them with no exception, and the instrument detects a planted leak at rate 1 (PTM-1), so it does not prove too much. The measured clauses held as preregistered, within a 4.2x–5.2x floor. The frozen `on_positive` branch therefore applies in the scope above: support, with the answer to the H2 clause recorded by derivation rather than "at toy scope". Strength is replicated, not strong, because the arm control is confounded and powerless, the readout is single-functional and the floor is coarse. Two mechanism sentences of H-CZLIFT-6d4ed1 are not supported as written ("the canonical curve lift … contributes nothing"; "a section recovering d would need tau(dP)/tau(P) = d"). The 1/p reference rests on a random-model assumption, numbered here as H-1 (uniform outside the `Aut(E^)`-orbit of d), validated at toy scale by panel (d) and the multiplier sets.

== Limitation
- Toy only for the measured clauses (fields of at most 10 bits); one readout; 4.2x–5.2x floor; confounded, powerless arm comparison; 36 unstated, outcome-independent exclusions; rows do not record d, d2, base point or residue.
- The derivation is a checkable argument, not machine-verified. The cm-arm canonical label is checked directly only for D = −3; the hypothesis's Katz citation is recalled with no verifier (the red team verified Deuring / Lubin–Serre–Tate in Chambert-Loir 2006 instead).
- The archived checker shares the producer's code; independence comes from the validator's blind re-derivation and replay and the red team's own arithmetic. Reviewer model identities are not probe-verified.

== Next actions
+ N-1. Session: write `analysis.md` and `KN-FIND-7e2b94` from the coordinator subagent's handback, check the KN id, render `plot.py` and this PDF, validate the ledger, run one isolated ledger archive of the exact paths, push and open or refresh a ready PR naming `EV-CZLIFT-ad28f5`, `DEC-20261023-36b4f0`, `KN-FIND-7e2b94`.
+ N-2. Synthesis task: correction record on `RQ-CZLIFT-b9f765` `decision_target` (a) ("every non-canonical section recovers d at the random rate 1/p" is false; red-team O1). The RQ is not closed or cited through (a) before it is committed.
+ N-3. Same task: corrections on `DEC-20261009-9f9254` ("so no choice of lift removes it", O2; "carries no information about d", O3; "Contradicted at toy scope" → contradicted by derivation, O4).
+ N-4. Same task: correction on `H-CZLIFT-6d4ed1` mechanism (O5, O6) and the canonical-lift citation; correction on `EXP-CZLIFT-ae0a13` for the unstated exclusion and the not-evaluable arm entry (O8).
+ N-5. Checkpoint `GOAL-CZLIFT-1516d5` with one next action (the N-2 to N-4 synthesis task); the reviews of `EXP-CZLIFT-17b7eb` and `EXP-CZLIFT-a255fc` follow and precede any closure of the RQ, which takes rule-12 review.
+ N-6. No follow-up experiment on this hypothesis: no task ranks ahead of doing nothing. Any later structured-section lane uses a matched-lift control, a readout-agnostic statistic, per-row d and residue, stated exclusions and H-1 as a numbered heuristic.

== Canonical graphs
Checked and left unchanged: `knowledge/frontiers/ecdlp/index-calculus/KR-IC-cd159a.yaml` (lifting to characteristic zero; consistent for the p-adic formal-logarithm route, nothing about global lifts) and `knowledge/frontiers/ecdlp/generic-rho/KR-RHO-53c89f.yaml` (anomalous boundary outside this decision). No frontier moves.

== Files
`plot.py` draws `graph.svg` from `plot_data.json` only. `plot_data.json` holds values copied from `runs/RUN-CZLIFT-dab752/manifest.yaml`, `runs/RUN-CZLIFT-5b2581/manifest.yaml` and `reports/redteam-20261023/{rt_probe,rt_probe_summary,rt_power,rt_power_armdiff_ext}_stdout.txt`, each with its run IDs; `plot.py` derives only counts (asserted integral) and Wilson intervals.
