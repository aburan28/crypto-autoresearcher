# EXP-GFPN-726eb2 — Coordinator analysis (evidence review)

Written 2026-09-23 by the Coordinator under TASK-20260923-e52c88. Composes the independent review round opened by TASK-20260923-cc166b (plan and prior frozen before any reviewer ran; archived in phase A of TASK-20260923-3b12c2, commit 4c1773f1cee778ee830de7acd03a43c551facbfa) from the two reviewer reports archived in phase B (post-review receipt commit 6e08e10c0b4f41875bf370dd50b96f5eefe79f93, filing commit 9cfa90b4333f698576c952627bd642920ef9a73b):

- TASK-20260923-2d8db0 (validator), joints J1-J4, `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-2d8db0/review-report.yaml`
- TASK-20260923-01af16 (red team), joints J5-J6 and the proves-too-much control, `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-01af16/review-report.yaml`

`tools/check_review_independence.py` accepted the round (PASS, recorded verbatim in the post-review receipt). Neither reviewer attests reading the other's report. Run packages: RUN-GFPN-17ed52 (SCURVE control), RUN-GFPN-b71f2f (EcGFp5), RUN-GFPN-3bbef2 (EcMasFp5). They are bound by snapshot TASK-20260921-b59aad (commit 0776af5027bc5c173d7d5a4abc017864c0904af9). The validator re-hashed all 131 entries against the tree and found them matching.

The sections below are kept strictly apart. **Observation** reports what the artifacts and reports contain. **Comparison** sets that against the frozen contract, the hypothesis and the recorded prior. **Inference** is the Coordinator's reading. **Limitation** says what the reading does not reach. Nothing here is re-run or re-measured by the Coordinator. The Coordinator had no shell. Three load-bearing reviewer claims were re-checked by the dispatching session, and all three reproduced:

- the EcGFp5 conductor and fundamental discriminant, by PARI `coredisc` / `isfundamental`;
- the EcMasFp5 |D| bit length;
- the forged-ECPP-certificate acceptance.

These are cited below as "dispatcher verification". They will be recorded in the TASK-20260923-35aa39 ledger receipt.

---

## 1. Observation

### 1.1 Validity of the run set (before any interpretation)

- **Run count.** The contract asks for one control and one run per curve. Three runs exist, all `completed_valid`.
- **Artifacts.** Every required artifact is present in all three runs. The frozen specification is unchanged, and `trial-plan.json` source hashes match the implementation. `amendments/` contains only `.gitkeep` (validator artifact_checks).
- **Seeds.** Seeds are null and the runs claim determinism. This is consistent with a deterministic audit: SEA and factorization on fixed published models.
- **Raw and summary.** Every audit-table value the validator recomputed agrees with its raw-result, with one exception: EcGFp5 `steps.cm_discriminant`. There D is not conductor_squared times fundamental_discriminant (see 1.2, J2).
- **Control.** RUN-GFPN-17ed52 finished at 04:03:39.9Z. The GFPN runs started at 04:37:54.0Z and 04:37:56.6Z.

The run set is therefore complete and schema-valid, and it is interpretable as measurement. The control's meaning is a separate question (J3).

### 1.2 Per-joint composition against the frozen plan

| joint | owner | attested | artifact it rests on | attacked, not broken | not attacked / residual |
|---|---|---|---|---|---|
| J1 order and twist certificates | 2d8db0 (validator) | holds | `scratch/inv1/result.json`, `sage_third_opinion.json`, `scratch/vlib.py` (own ECPP chain checker, own F_{p^5} group law, no producer code, no PARI in verification) | Every ECPP certificate re-verifies: n (10 and 13 rows) and every large factor of n-1, \|D\|, N' and l'-1. [n]P = O holds in three implementations. The 2-torsion argument (EcGFp5) holds. Hasse uniqueness holds. The twist products and primality hold. Twist security reproduces: 120.6583 and 101.9321. Verifier negative controls are rejected. No published integer was used as the order candidate. | GMP-ECM hint logs carry no timestamp or command line. Their provenance is unrecorded, but hints can only split a regenerated integer, so this cannot manufacture agreement. |
| J2 embedding degree and CM discriminant | 2d8db0 | **breaks** | `scratch/inv1/result.json` (B_EcGFp5.cm, B_EcMasFp5.cm); `gfpn_audit.py` lines 440 and 630 | e = (n-1)/5 (317 bits) and n-1 (320 bits), reproduced by the order test. \|D\| is 322 bits for both curves. Both D_K are 322 bits. EcMasFp5 conductor is 1. The EcMasFp5 D integer reproduces exactly. | — |
| J3 SCURVE control and D-1 | 2d8db0 | **breaks** | `scratch/inv1/result.json` (D_J3a_callgraph, C_J3b_scurve, E_J3c_chronology); `gfpn_audit.py` line 635 | Prior-package hashes match the SCURVE lane's own receipt. l*B = O and the Hasse endpoints regenerate under the validator's own group laws. Chronology holds for the two scoring runs. | The claim "control ran before any GFPN computation" is not verifiable for the ECM hint jobs or the development SEA probes, which have no timestamps. |
| J4 rigidity re-enumeration | 2d8db0 | holds | `scratch/inv2/witnesses.jsonl` (2097 records), `scratch/inv3/witnesses.jsonl` (620 records), `scratch/inv3/cm_j0_orders.json` | The frozen text pins both procedures. All 2096 + 619 predecessors carry self-certifying rejection witnesses: a 4-subgroup, a point of small prime order, or a Hasse-interval N with composite N/h. The 196 j = 0 curves were re-counted by the CM formula. The first hit is the published curve in both searches. | The 124 j != 0 full counts were not re-counted by a PARI-independent routine; none exists on the host. The WN witnesses certify the rejections without needing N = #E. For 8 of 320 full counts, compositeness rests on a Fermat witness only, with no factor. |
| J5 figure-provenance tags | 01af16 (red team) | holds | `scratch/small_checks.out.json` (C1-C3) | All 11 tags are defensible under the table's vocabulary. Every quoted fragment is verbatim. The 142 arithmetic (102.4 + 40) reproduces. "inherited" is correct provenance for EcMasFp5. | See 1.3 for defects found that do not break the joint. |
| J6 scope and interpretation | 01af16 | **breaks** (description only) | enumeration in the report, `joint_J6.attacks_performed(b)` | No committed GFPN record reads the audit as evidence about attack cost, 128-bit security, index calculus, OA-SDH, covers or the validity of 142. | — |
| proves-too-much A-D | 01af16 | A, B, C prove too much; D fails as it must | `scratch/objects/*/out/audit-table.yaml`, `scratch/variants/*/variant.diff` (literal-only input mutations of the hash-checked committed pipeline) | Object D, the shifted rigidity claim, gives FAIL on both curves. | Object A was not run without ECM hints. Object D was not run as "curve shifted too". |

**J2 findings, one line each.**

- (i) The EcGFp5 CM conductor is 1, not 2. The committed `runs/RUN-GFPN-b71f2f/raw-result.json` records `conductor_squared: "4"`, and `implementation.md` lines 128 and 197 say "conductor 2". The cause is `gfpn_audit.py` line 440, `conductor_squared = abs(D) // sf`. That expression equals f^2 only when -sf = 1 mod 4. Dispatcher verification: PARI `coredisc(D) == D` and `isfundamental(D) = 1`. Coordinator derivation: see 1.4.
- (ii) Under the frozen falsification criterion the EcMasFp5 `cm_discriminant_bits` row must read FAIL. The self-reported figure is the bit count, which the note states three times as "323 bits". The recomputation gives 322, and no tolerance is declared. The committed row reads `result: PASS` with `matches_self_report: false`. Dispatcher verification: 81 hex digits, leading digit 3, so 322 bits.

**J3 findings, one line each.**

- `scurve_control.py` shares no project function with the GFPN scoring path and calls no PARI.
- The GFPN tables' `scurve_control_certificate_match` row is a string literal at `gfpn_audit.py` line 635. The pipeline never reads the control result.
- D-1 changed "re-run of the instrument" to "separate script". The contract required a versioned amendment for that change, and none exists.
- The invalidation rule "Scoring results after a failed SCURVE control match" is NOT triggered, because nothing failed. The control was misdirected, not failed.
- `rigidity_reproduced`, as produced, rested on PARI early-abort behaviour that the control never exercised. It now stands on the J4 witnesses.

**J6 findings, one line each.**

- Six of the eleven SafeCurves criteria, as the program's SCURVE lane operationalises them, are neither examined nor marked `not_verifiable`: field, equation, base, ladder, complete, ind.
- Three are partial: rho, transfer (MOV only) and twist.
- The extension-field transfer criterion (Weil descent / GHS / Diem covers at n = 5) is absent.
- H-GFPN-ee4d45 prediction 1 ("All SafeCurves-style criteria decided ...") is not met as worded.
- The row label PASS means "computed with a certificate", or, for rigidity, "the search's first hit equals the declared tuple". It never means "meets the criterion".
- IDEA-20260920-63a902's sentence that 101.9 bits "fails the SafeCurves twist criterion" is not established by this audit.

**Proves-too-much, per object.** Each object is a literal-only mutation of the committed pipeline, hash-checked. The expected signature is FAIL on the named row.

- **A, supersingular curve y^2 = x^3 - 35x + 98 over F_p viewed over F_{p^5}.** PROVED TOO MUCH.
  - `embedding_degree` reads PASS with e = n - 1 = p^5 (320 bits). The true embedding degree is 2.
  - The cause is `gfpn_audit.py` line 397, which uses the uncertified `n_cand` after the order proof has failed. In addition, `mult_order_from_factorization` (lines 227-234) never checks q^(n-1) = 1 mod n.
  - The same object also collects PASS on the CM row (66-bit CM field discriminant), on the twist (89.5 bits) and on rigidity.
- **B, subfield curve y^2 = x^3 + 3x + 8.** PROVED TOO MUCH on rigidity ("reproduced" for a curve outside the search) and FAILED TO FAIL on order and cofactor.
  - A proof of composite order is filed as NOT_VERIFIABLE. It carries the same reason string a primecert timeout produces, so the table cannot tell a disproof from an infrastructure outcome.
- **C, EcMasFp5 with three tampered self-reports.** PROVED TOO MUCH, 3 of 3.
  - All three affected rows read PASS.
  - The tampered CM integer never reaches the audit table: the CM row compares bit length only.
  - Only `rigidity_reproduced` has a FAIL branch among the nine labels. The frozen falsification criterion, "That criterion row is FAIL", is therefore unreachable by construction.
- **D, shifted rigidity claims.** FAILED AS IT MUST on both curves.

The frozen success criterion is met on all five known-false outputs (`scratch/c7_corrected.json`). The red team disclosed and corrected its own C7 predicate bug.

### 1.3 Findings recorded but not breaking a joint

- **J1 side finding, producer verifier unsound.** The producer's `gfpn_arith.py` `verify_ecpp` (sha256 d4586286...) is the check behind every `independent_verify_ecpp: true` and behind check_run.py's "13 ECPP certificates re-verified".
  - Line 266 accepts `[q]([s]P)` as the point at infinity whenever `gcd(Z, N) != 1`, including a proper factor of N.
  - Line 254's size test is weaker than the theorem's.
  - The validator's one-row certificate for the composite N = 5058901727581901 * 3055061130351253 is accepted by it (`scratch/inv4/result.json`).
  - The Coordinator read lines 235-275 of the committed file and confirms the logic at line 266. Dispatcher verification reproduces the acceptance.
  - No certified number changes: every committed certificate passes the validator's sound checker and PARI's `primecertisvalid`.
- **J5 defects.**
  - Six EcGFp5 citation line numbers use `str.splitlines()` numbering, which counts 18 form feeds. Under ordinary numbering they are 2 or 11 lines late.
  - The tag vocabulary has no token for "model-derived, arithmetic recomputable, not recomputed" or for "no figure stated".
  - No unit is recorded for 2^142. DEC-20260921-683a85's audit-keyed revisit trigger for IDEA-20260920-68b279 therefore cannot be evaluated from this table.
  - The rho formula 0.5*log2(pi*l/4) is identified by fit. The note states no formula.
  - H-GFPN-ee4d45 prediction 2's qualifier "raw-system floor" appears in no table and, as worded, is not met.
- **Out-of-scope pointers** (not coverage). The validator reports that PARI 2.15.4 is installed while the ellsea documentation read was for 2.17 (moot, since every rejection carries a witness). The red team independently computed j^p != j for both named curves, consistent with goal.yaml's "neither named curve is subfield". The audit itself does not test that property.

### 1.4 Coordinator derivation: the EcGFp5 conductor is odd

This is checkable by hand. It uses only facts certified in J1. For EcGFp5, #E = N = 2n with n an odd prime, and q = p^5 with p = 2^64 - 2^32 + 1 = 1 (mod 4), so q = 1 (mod 4).

1. Take the trace t = q + 1 - N. Since q + 1 = 2 (mod 4) and N = 2n = 2 (mod 4), t = 0 (mod 4). Write t = 2u with u even.
2. D = t^2 - 4q = 4(u^2 - q), and d := u^2 - q = 0 - 1 = 3 (mod 4).
3. If the conductor f of Z[pi] were even, D/4 = (f/2)^2 D_K would itself be a discriminant, so D/4 would be 0 or 1 (mod 4). But D/4 = d = 3 (mod 4). So f is odd, and "conductor 2" is impossible for this curve whatever the odd part of |D| is.
4. With |D|/4 = 3 * 41 * p313 squarefree, as committed and as re-proved by the validator's certificate for p313, f = 1 and D_K = D.

This derivation, the validator's recomputation and the dispatcher's `coredisc`/`isfundamental` check agree.

---

## 2. Comparison

### 2.1 Against the frozen contract

- **Success criterion.** "scurve_control_certificate_match is true; ... every primary metric is present with a regenerated certificate or an explicit not_verifiable reason; figure_provenance_table includes tags ...". It is met only literally.
  - The control row is a hard-coded string (J3).
  - The contract's control is an instrument re-run. It was replaced without the versioned amendment the specification's status_note requires.
  - Every metric is present with a certificate.
  - Both tags are present.
  - The red team shows the criterion is also met by every known-false object (proves-too-much), so meeting it carries no information about the curves.
- **Falsification criterion.** The EcMasFp5 cm_discriminant_bits self-report (323 bits) fails recomputation (322). Under the frozen text "That criterion row is FAIL and is the finding; the run remains valid measurement". The committed table says PASS. The run's validity is unaffected, and the row label is wrong (CORR-20260923-80d978).
- **Invalidation rules.** None fires.
  - No integer was copied: J1(d) shows the order candidate was regenerated by SEA.
  - No required artifact is missing.
  - No failed control match was scored, because nothing failed.
  - No attack claim is made.
- **Scientific boundary.** Respected. No S_m, PDP, OA-SDH, cover genus, DLP or rho claim appears in any producer artifact (J6(a)).

### 2.2 Against H-GFPN-ee4d45

- **Statement.** The statement is that regenerating the certificates produces a certificate-bearing audit table, and that a non-reproducing self-report is a first-class finding. It is borne out for the values: J1, J2 except the conductor, J4, and the dispatcher re-checks. The one non-reproducing self-report (EcMasFp5 "323 bits") was found.
- **Prediction 1** ("All SafeCurves-style criteria decided with regenerated certificates ... or explicitly marked not verifiable"). NOT MET as worded. 5 of 11 criteria are decided or partial, 6 are unexamined and unmarked, and extension-field transfer is absent (J6(b)).
- **Prediction 2.**
  - "101.93 tagged computed vs self-report after regeneration": met (101.9321, |delta| 0.0021).
  - "142-bit figure tagged inherited": met in tag.
  - "... raw-system floor": not met as worded. By joint K7 of the sibling round (TASK-20260923-fe27e4; dispatcher-verified frozen-text reading), the design note's 142 describes the S_5-symmetrized system, not the raw one. The qualifier is therefore wrong as well as unrecorded (CORR-20260923-27ce4f).
- **Falsification conditions.** The first (a self-report does not reproduce) fired for cm bits. As the hypothesis says, that is a finding and not a falsification. The second (SCURVE control fails byte-for-byte) did not fire, but it could not have fired against the instrument, which the control never ran.

### 2.3 Against the recorded coordinator_prior (TASK-20260923-cc166b)

The prior was written before any reviewer ran. It was anchored to the producer's numbers and was not blind. Agreement with it is weak evidence, as DEC-20260923-885c52 recorded. Where a verdict below agrees with the prior, it rests on an artifact the reviewer built independently, and it is that artifact, not the agreement, that carries weight.

| prior item | recorded | outcome |
|---|---|---|
| J2 label must read FAIL | 0.65 | agreed. Weak as agreement; the ruling quotes the frozen text. |
| J2 recomputed D differs | 0.03 | not realised: D reproduces. But the plan's own joint statement carried the producer's "conductor 2" as fact, and that is wrong. The prior did not anticipate an error in a derived quantity. **Overturned in substance.** |
| J3 control shares no instrument code | 0.60 | agreed. The call graph is the artifact. |
| J3 D-1 an unamended reinterpretation | 0.50 | agreed. |
| J3 no GFPN row depends on the control | 0.80 | **partly overturned**: `rigidity_reproduced` depended on uncontrolled PARI behaviour until J4 witnessed it. |
| J4 false rejection | 0.05 | not realised. 2715 witnesses. |
| J4 procedure not pinned by the frozen text | 0.40 | **overturned**: both procedures are pinned verbatim. |
| J1 certificate fails | 0.03 | not realised. |
| J1 procedural gap in regenerated_not_copied | 0.25 | a gap was found (ECM-hint provenance), but it cannot manufacture agreement. Not a break. |
| J5 142 tag misapplied | 0.35 | not realised. A vocabulary gap was found instead. |
| J6 transfer criterion must be scoped | 0.70 | agreed. |
| J6 committed overreading in goal or question framing | 0.50 | **not realised** for attack cost or security. The overreaching wording found is in H-GFPN-ee4d45 prediction 1 and in IDEA-20260920-63a902, not in the goal or question. |
| proves-too-much: at least one object passes | 0.35 | **exceeded**: three of four objects prove too much. The sharpest branch (C) is realised exactly as predicted. |
| modal outcome ("every numeric row certified ... one frozen-rule mismatch ... scoped support") | 0.65 | **not realised as a whole**. The numeric content matches the modal expectation except the conductor. The instrument's failure on known-false objects and the misdirected control go beyond it, and they move the decision from the modal "scoped support" to `refine`. |

---

## 3. Inference

1. **The certified values stand, independently of the producer's instrument and labels.** For EcGFp5 and EcMasFp5 over F_p[z]/(z^5 - 3), p = 2^64 - 2^32 + 1, the following are established:
   - the group order and cofactor (2n with n a 319-bit prime; n prime of 320 bits);
   - the MOV embedding degree ((n-1)/5 of 317 bits; n-1 of 320 bits);
   - the CM discriminant (|D| 322 bits for both, fundamental, conductor 1 for both);
   - the quadratic-twist factorisations and their rho costs (120.6583 and 101.9321 bits);
   - the rigidity of both published searches, with a self-certifying witness for every predecessor.

   They were established by code that shares nothing with the producer (J1, J2, J4) and were spot-checked by the dispatcher's PARI. The run set is valid measurement, and these values are independently replicated.
2. **The audit table as committed is not a SafeCurves-style verdict instrument.** Its PASS labels record that a value was computed. They cannot express a failed criterion or a failed self-report. It reports a wrong e on a supersingular curve, and its rigidity row is not tied to the audited curve (objects A-C). Its control did not control it (J3). The information is in the values, in `matches_self_report` and in the certificates, never in the labels. Two committed record defects follow:
   - the EcGFp5 conductor (CORR-20260923-887c3d);
   - the EcMasFp5 cm row label, together with the PASS-label semantics (CORR-20260923-80d978).
3. **The one self-report finding is EcMasFp5's CM bit length:** "323 bits" against a recomputed 322. The integer D itself reproduces exactly. No explanation of "323" is adopted. The producer's "sign character counted" is a conjecture.
4. **The hypothesis over-promised coverage.** Its prediction 1 asks for all SafeCurves-style criteria. The contract declared nine metrics, and the audit decided or partly decided 5 of 11 criteria. This is a design mismatch between hypothesis and contract. It is not evidence against the curves or against the certified values.
5. **Hence `refine`, not `support`.** What survives is narrower than H-GFPN-ee4d45 as stated. A support would lean on the reviewers' recomputation rather than on the experiment's own instrument, and it would certify an audit table whose labels are shown to pass known-false curves. The hypothesis must be restated to the certified-values claim, with the unexamined criteria named. Before the audit pipeline scores any further curve, it must pass objects A-D as acceptance fixtures and use a real instrument control.
6. **Nothing here is adverse to either curve**, and nothing bears on attack cost, on the 142-bit figure's validity, on covers at n = 5, or on any 128-bit claim. Scope sentence (red team J6, adopted verbatim in EV-GFPN-ba8e4d):
   - Affected: none. This audit threatens no deployed system.
   - Safe: none certified. No system using EcGFp5 or EcMasFp5 may cite this audit as evidence of SafeCurves conformance or of 128-bit security.

---

## 4. Limitation

- **No shell.** The Coordinator ran nothing. Numeric claims rest on:
  - the validator's independent instrument;
  - the dispatcher's spot re-checks: the conductor and fundamental discriminant, the EcMasFp5 bit length, and the forged-certificate acceptance;
  - the Coordinator's hand derivation in 1.4 and its reading of `gfpn_arith.py` lines 235-275.
- **Rigidity residuals.** The 124 j != 0 full-count rejections were not re-counted by a PARI-independent routine. They are certified by WN witnesses, which do not need N = #E. For 8 candidates compositeness rests on a Fermat witness only.
- **Unexamined criteria.** The six unexamined SafeCurves criteria and extension-field transfer at n = 5 are not decided here. No SafeCurves threshold was applied. The SCURVE lane holds its thresholds as recalled (audit-plan capsule C6b).
- **Proves-too-much coverage.** The objects were run through the committed pipeline with literal-only input mutations. Object A was not run without ECM hints. By lines 406-416 and 629 of the code, it would read BOUND, not FAIL.
- **Scope of the objects.** They show what the instrument does on known-false inputs. They say nothing about the two named curves, whose values are certified independently.
- **Control timing.** Whether the control preceded every GFPN computation, including the ECM hint jobs and the development SEA probes, is not verifiable. Those artifacts carry no timestamps.
- **Tier.** Crypto tier, direct computation at the deployed parameters, no transfer assumption. The claim is scoped to these two exact curves and the nine declared metrics.
