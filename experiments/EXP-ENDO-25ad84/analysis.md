# Analysis: EXP-ENDO-25ad84 / RUN-ENDO-d7cb69

Coordinator review under DEC-20261016-5752c0. Evidence record EV-ENDO-fb5823. Hypothesis H-ENDO-5a33ae; idea IDEA-20261016-15a6fc; question RQ-ENDO-476761; goal GOAL-ENDO-001. Snapshot TASK-20261016-cbf19d at `2a8674d65`. Independent validation TASK-20261016-1b5210 (`experiments/EXP-ENDO-25ad84/validation/TASK-20261016-1b5210.md`, verdict passed). Ledger archive TASK-20261016-5c0f78.

All costs are modelled M_eq = M + S counts in curvesweep's wNAF model (S = 1 M primary). Nothing here is a timing, and nothing here is an ECDLP, rho or exponent statement.

## Validity (checked before interpretation)

| check | result | source |
|:--|:--|:--|
| expected run count | 1 expected, 1 present (RUN-ENDO-d7cb69) | spec `maximum_runs: 1`; manifest |
| manifest | `validity: valid`; 136 rows, 0 error rows; frozen arguments equal the spec | manifest.yaml; validator J1 |
| seeds | one frozen seed 20261016, 200 scalars per cost, 8 verification scalars | manifest; spec `replication` |
| raw / summary agreement | rows.jsonl equals `raw["rows"]` element for element; manifest digests match | validator J1 |
| population completeness | rebuilt independently: same 134 curves in the same order; exclusions 52 duplicates, 7 over 521 bits, 73 non-prime-field | validator J1 |
| controls | control+model, control+ascent, control-/P-256, control-/Curve25519 and the instrument check all pass | validator J2 |
| route certificates | every positive route `verification.ok` on 8 of 8 scalars; validator's own Velu route code 27/27 on all 9 positive rows, with 54/54 deliberately broken routes failing | validator J3 |
| record defects (non-invalidating) | `raw.provenance.dirty` true vs manifest `repository_dirty` false (different scopes; harness sources clean); no peak-memory record | validator J5 items 2-3 |

The run set is valid and complete. No solve or relation is claimed, so no solution certificate is required.

## Observation

- **O1 Controls.** control+model (3-neighbour of NIST P-256): best route back over the degree-3 edge to the a = -3 class, persistent +15.276 %, one-shot +14.465 %, verified 8/8. control+ascent: D_K = -3 reported and `glv_on_reached_crater` priced (path [11], 1779.5 M_eq). NIST P-256: best persistent 0.0, one-shot -1.70 %. Curve25519: baseline `edwards_a=-1`, best persistent 0.0. Instrument check true on 136/136 rows (101 odd-order rows, 0 Edwards/Montgomery reports).
- **O2 Arm M positives.** Seven population curves have a best route with persistent and one-shot gain > 0 against the best model on E (table.md rows 18, 59, 61, 64, 65, 123, 126):

  | curve | E baseline M_eq | neighbour M_eq | path | persistent | one-shot | verified |
  |:--|--:|--:|:--|--:|--:|:--|
  | other/Tom-384 | 4929.5 | 4165.8 | 5 | +15.49 % | +14.52 % | 8/8 |
  | mnt/mnt5/2 | 3124.4 | 2648.2 | 5 | +15.24 % | +13.71 % | 8/8 |
  | mnt/mnt5/3 | 3124.4 | 2648.2 | 5 | +15.24 % | +13.71 % | 8/8 |
  | mnt/mnt3/1 | 2103.7 | 1788.6 | 5 | +14.98 % | +12.70 % | 8/8 |
  | mnt/mnt3/3 | 2103.7 | 1788.6 | 5 | +14.98 % | +12.70 % | 8/8 |
  | other/BADA55-VPR-224 | 2922.8 | 2478.4 | 5·5 | +15.20 % | +11.44 % | 8/8 |
  | GOST 2001 test curve | 3063.9 | 2810.7 | 5 | +8.26 % | +6.70 % | 8/8 |

- **O3 Independence.** mnt5/2 and mnt5/3 carry identical figures, and their neighbour M_eq 2648.2 equals mnt/mnt5/1's own baseline; mnt3/1 and mnt3/3 likewise, with 1788.6 equal to mnt/mnt3/2's baseline. The seven positives come from five curve families (Tom-384, mnt5, mnt3, BADA55-VPR, GOST), not seven independent instances.
- **O4 Where the gain is absent.** All seven positives are among the 9 population curves whose cheapest model on E uses generic-a doubling. None of the 45 a = -3 curves, 13 a = -3-isomorphic curves, 32 twisted Edwards curves or 33 j = 0 unit-GLV curves has a positive persistent gain (run report, "Population observations").
- **O5 Arm A.** D_K is certified within |D_K| ≤ 2^20 on 48 population curves; 33 of them are D_K = -3 curves whose root is a j = 0 crater (`f_E = 1`). Two population rows whose root is not a j = 0 or j = 1728 crater have |D_K| ≤ 20:
  - `bls/Bandersnatch` (rows.jsonl line 26): `ascent.certificate` = "t^2-4q = (-8) * 21482638764116277775478679919733259912^2; CM field Q(sqrt(-8))", `f_E: unresolved`, `glv_on_reached_crater: null`;
  - `mnt/mnt1` (rows.jsonl line 50): `ascent.certificate` = "t^2-4q = (-19) * 6915889423298038776451801^2; CM field Q(sqrt(-19))", `f_E: unresolved`, `glv_on_reached_crater: null`.
- **O6 Against E's own chain GLV** (validator J4; recomputed in the same cost model by RUN-ENDO-795989, EXP-ENDO-7494e7, field `model_change_vs_glv_on_E`). On the six positives with a small D_K, E's verified chain 2-GLV (research/endosweep_curves_20261006, built and point-checked) is cheaper than the best model-change route:

  | curve | D_K | GLV on E M_eq | model change vs GLV on E, persistent | one-shot |
  |:--|--:|--:|--:|--:|
  | GOST 2001 test curve | -915 | 2132.5 | -31.80 % | -34.05 % |
  | mnt/mnt3/1, mnt3/3 | -139 | 1466.5 | -21.96 % | -25.24 % |
  | mnt/mnt5/2, mnt5/3 | -211 | 2131.4 | -24.25 % | -26.50 % |
  | other/Tom-384 | -619 | 3233.8 | -28.82 % | -30.31 % |

  other/BADA55-VPR-224 has no |D_K| ≤ 2^20 here and none ≤ 2·10^6 in RUN-ENDO-795989, so no chain GLV on E was priced for it.

## Comparison (against the frozen contract)

- **Success criterion (arm M)**: "valid, all controls and the instrument check pass, and at least one population curve has a verified best route with oneshot_gain > 0 at S = 1 M". Met: seven curves (O2), five families (O3).
- **Prediction, arm M**: one-shot gain in (0, 15 %] where an a = -3 neighbour exists at ell ≤ 7. All seven one-shot gains (+6.70 % to +14.52 %) lie in the band. The persistent gain of Tom-384, +15.49 %, is above 15 %, but the frozen quantity is the one-shot gain. Prediction "≤ 0 on a = -3 and on a = 0 curves": no such curve has a positive persistent gain (O4). Consistent.
- **Prediction, arm A**: "Ascent hits on non-crater population curves are predicted to be 0"; falsification "any non-crater population curve with |D_K| <= 20". H-ENDO-5a33ae states arm A as "No population curve whose own root is not a j = 0 or j = 1728 crater has |D_K| <= 20", and the instrument flags exactly that condition (`root_crater`, isomodel.py lines 407-413, frozen at `8efe71fc…`). Under that frozen definition there are 2 hits (O5), against a predicted 0. The arm-A prediction is falsified as worded.
  - Reading note. The validator read "non-crater" as "not at the top of its own volcano" (`f_E ≠ 1`), which this run does not certify for these two curves, and applied no label. Under that reading arm A is unresolved, not supported. Neither reading supports arm A. The Coordinator applies the hypothesis's own frozen definition; this is not a change of criterion.
- **Against the best known method on E** (outside the frozen baseline, which includes only E's unit GLV): the model change is dominated on 6 of 7 positives by 25.2 % to 34.1 % one-shot (O6).
- **Against the index-calculus baseline and the matched rho**: not applicable. This is known-scalar k·P cost; no ECDLP pipeline, rho figure or index-calculus baseline is involved, and none moves.

## Inference

- **I1 Arm M holds as worded, at the modelled tier.** On the tested population, a model change on a rational 5- or 25-isogenous neighbour lowers modelled one-shot k·P cost against E's best model plus E's unit GLV, on seven curves from five families, with every route verified on points.
- **I2 Its practical reach is one curve.** Against the best verified method on E, the model change alone loses on all six small-D_K positives (O6). other/BADA55-VPR-224 is the only positive with no known cheaper decomposition on E within the scanned discriminant bound. The baseline the hypothesis fixed was narrower than the best known method; that limits the significance of I1, it does not falsify it.
- **I3 Arm A is false as worded (counterexample certificate).** See the derivation below. Two deployed or published prime-field curves outside j ∈ {0, 1728} carry |D_K| ≤ 20. Whether ascent, or E's own non-unit endomorphism, yields a k·P gain on them is untested: the instrument prices a GLV only on j = 0 / 1728 craters.
- **I4 The hypothesis as a whole is weakened.** One of its two conjuncts (arm A) is refuted by a checkable counterexample; the other (arm M) holds in a scope that a known method dominates on 6 of 7 curves. Arm M's substantive question has already been carried forward as H-ENDO-f58749 (compose with the GLV) and H-ENDO-c9f324 (timed, on BADA55-VPR-224).

### Arm A counterexample (proof_ref for EV-ENDO-fb5823)

Claim refuted: "No population curve whose own root is not a j = 0 or j = 1728 crater has |D_K| ≤ 20" (H-ENDO-5a33ae, arm A).

1. **The identity is checkable.** For row r, with p = int(r["p"], 16) and t = r["trace"], the recorded certificate states t^2 - 4p = D_K · f_pi^2 with D_K = -8 (Bandersnatch) and D_K = -19 (mnt1), and the f_pi quoted in O5. Both D_K are fundamental discriminants (-8 = 4·(-2), -2 ≡ 2 mod 4; -19 is squarefree and ≡ 1 mod 4). This is integer arithmetic on recorded values.
2. **Both curves are ordinary.** t^2 - 4p = D_K f_pi^2 with D_K ∈ {-8, -19} excludes t = 0 (which would give -4p, whose fundamental part is -p or -4p for these p of 255 and 170 bits). With |t| ≤ 2√p and t ≠ 0, p does not divide t.
3. **Neither root is j = 0 or 1728.** For an ordinary E over F_p with p > 3, End(E) is an order in K = Q(√D_K). j(E) = 0 implies an automorphism of order 3 in End(E), so K = Q(√-3) and D_K = -3; j(E) = 1728 implies one of order 4, so D_K = -4. Since D_K ∉ {-3, -4}, j(E) ∉ {0, 1728}.
4. **Hence** both rows satisfy the hypothesis's antecedent and violate its consequent. Two counterexamples among 132 population curves.

Status of the check: the identity in step 1 has not yet been recomputed by code independent of `harness/endosweep/quadorder.py`. That recomputation is a completion gate of the ledger archive TASK-20261016-5c0f78; if it fails, the arm-A part of DEC-20261016-5752c0 is void and the archive stops.

Context, recalled and not relied on: Bandersnatch was published as a curve with an efficient degree-2 endomorphism for GLV, and MNT curves are built by the CM method. Both points are pointers for a reviewer; neither supports the inference above, which rests on steps 1 to 4.

## Limitation

- **L1** Modelled counts only, in one cost model (curvesweep wNAF, widths 3-7, affine or Jacobian tables, 200 sampled scalars). No timing; no transfer to other formula families, constant-time or complete formulas, or fixed-base k·P. Edwards counts are recalled from the EFD; Doche-Icart-Kohel models are not priced; the S = 0.8 M column is persistent only.
- **L2** One deterministic pass, one seed. Validator J4 puts the 200-scalar baseline sampling error at 3.2 to 3.8 M_eq (about 0.1 to 0.2 % of cost), far below every gain or loss above.
- **L3** Scope: prime fields, ≤ 521 bits, ell ∈ {2, 3, 5, 7, 11, 13}, depth 2, ≤ 64 nodes per curve, |D_K| ≤ 2^20. A null or a domination outside that bound is not established.
- **L4** Seven positives are five families (O3).
- **L5** f_E is certified only at j = 0 / 1728 roots. The arm-A falsification rests on the hypothesis's own definition; under an f_E-based reading the two rows are unresolved (Comparison, reading note).
- **L6** The baseline omits E's non-unit chain GLV by contract; O6 brings it in from RUN-ENDO-795989 and research/endosweep_curves_20261006, which share the cost model. Bandersnatch's and mnt1's own non-unit endomorphisms are absent from their baselines too.
- **L7** The idea's heuristics H1-H3 are not validated by this run.
- **L8** No peak-memory record; the manifest dirty flag covers harness/ only.
