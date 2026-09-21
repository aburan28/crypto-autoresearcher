# Validation Notes — TASK-20260804-cf1ae3
## Validator: TASK-20260804-cf1ae3 | Producer: TASK-20260804-241b87
## Snapshot: b7b3240b4266b85af1e0810831a66aa6e3300535

---

### Scope of this review

This report validates the executor task TASK-20260804-241b87 in BATCH-403f13
(GOAL-P13-001), which produced:

- **EXP-P13-NC2d** (NC2d-PROPER): C-PSCALE re-run at ell ∈ {47,101,151,211}
- **EXP-P13-NC2b** (NC2b-SLOPE): Null-series slope test at s ∈ {0.4, 0.8}
- **Bibliographic subtask**: Sutherland 2013, Santos-Costello-Shi 2022, Adj et al. 2018

NC-3/NC-6 (TASK-20260804-6519fa) is a separate task and is not within my review scope.

---

### CHK-1: Hash integrity

SHA-256 independently recomputed for all four task artifacts and four experiment
artifacts listed in receipt.json. Every hash matches exactly.

```
nc2d_results.json  1d659a46c09a2c15e8a8e44aeb5478ac3bc2c66b9e7a91db6cd523ff4a10ba9c  MATCH
nc2b_results.json  450eac4cd0cbc4306572bdd4a34068290f8e939efaf4873d57b24bc6ada3b5cf  MATCH
bib_results.json   51a3139cb6f63a37c5a7ee13948f419ae9f47be90c4023c6d10396738bcf783d  MATCH
run_log.txt        76724448cf8437aa3f5d104806a34c941245c423418ca4b83d9bce6c555defb8  MATCH
raw-result (NC2d)  dc6af07179f2eb1d571be2cffd20251b3de12c7ec4441108cc8d9ba31daaf8d3  MATCH
nc2d_cpscale.py    7d28584725cb52969fe422b4c8f34718caf7245b3a87949e92068e23d0bb1ade  MATCH
raw-result (NC2b)  faef5143220091987c4a031d76a41657eb7d479b0532a9f75fedea9b8a4d24fc  MATCH
nc2b_slope.py      b2cd4141399a7a3976f8c84491bc5cc2092991fbc55221e8562c0a1e4b8a85a6  MATCH
stdout (NC2d)      880d5d3e834450d12e346d572d4f4a8e7c99fc46535067c8d40077d89de4c437  MATCH
stdout (NC2b)      dc41ef32b7e609c38cbe0ab96604399200821e4239d5f6f17220ab113f0ab13d  MATCH
```

Snapshot commit `b7b3240b4` is at HEAD. `git show b7b3240b4 --name-only` confirms all
21 declared artifacts (task files + EXP-P13-NC2d/* + EXP-P13-NC2b/*) are in the
commit. No additional unintended files were staged.

---

### CHK-2: NC2d arithmetic

#### Pooled alphas and gap

From per-ell values in nc2d_results.json (4 d.p. rounded; raw-result.json confirms
higher-precision values):

| ell | α_primary | α_null | gap |
|-----|-----------|--------|-----|
| 47  | 1.1055    | 1.0784 | 0.0270 |
| 101 | 1.1318    | 1.0938 | 0.0381 |
| 151 | 1.1407    | 1.0512 | 0.0894 |
| 211 | 1.1504    | 1.0626 | 0.0877 |
| **pooled** | **1.1321** | **1.0715** | **0.0606** |

All four means verified arithmetically. Raw-result pooled values: α_primary =
1.1320907, α_null = 1.0715207, gap = 0.0605699.

#### FC-4 evaluation

Threshold = 0.15. gap = 0.0606 < 0.15. **FC-4 DID NOT FIRE** ✓.

#### Jackknife CI

Frozen spec defines jackknife interval as "[min, max] of the four leave-one-out
estimates". Independent computation:

```
Remove ell=47:  mean(1.1318,1.1407,1.1504) = 1.1410  → max
Remove ell=101: mean(1.1055,1.1407,1.1504) = 1.1322
Remove ell=151: mean(1.1055,1.1318,1.1504) = 1.1292
Remove ell=211: mean(1.1055,1.1318,1.1407) = 1.1260  → min
```

Raw-result.json values: [1.1259982, 1.1409560], consistent with above (difference
due to higher-precision per-ell values in raw-result.json vs rounded values used here).

**Containment check**: 1.1259982 ≥ 0.85 ✓ and 1.1409560 ≤ 1.15 ✓ →
`contained_in_band = true` is arithmetically correct.

**Note on notation**: The handoff summary labels this a "95% CI". The frozen spec
does not use that label; it defines the interval as [min, max] of leave-one-out
estimates. The arithmetic is correct; the label is non-standard. See Q-1.

#### FC-2 evaluation

FC-2 fires iff CI is disjoint from [0.85, 1.15]. CI = [1.1260, 1.1410] overlaps
[0.85, 1.15] (they share [1.1260, 1.15]). **FC-2 DID NOT FIRE** ✓.

#### Regressor

Frozen spec § estimator: "OLS of log2(median per_entry) on log2(log2 p)".
Run log line 2: "Permanent constraint: frozen spec governs. Regressor is log2(log2 p)."
Handoff conflict explicitly recorded in receipt.json (`handoff_conflict_recorded`) and
raw-result.json (`handoff_conflict`). **log2(log2 p) used** ✓.

#### No-trend check

b = 0.0206 via OLS of α̂(ell) vs log2(ell). Independently verified:
```
x = [log2(47), log2(101), log2(151), log2(211)] = [5.555, 6.658, 7.237, 7.722]
b = Σ(xi−x̄)(yi−ȳ) / Σ(xi−x̄)² = 0.05381 / 2.613 = 0.0206
|b| = 0.0206 ≤ 0.10 → PASS ✓
```

---

### CHK-3: NC2b arithmetic

#### Gate NC2b-SLOPE-G1 (W-MID, 10 checks)

All 10 W-MID checks verified from nc2b_results.json:

| s   | curve        | error (bits) | pass |
|-----|-------------|-------------|------|
| 0.4 | NIST_I_256  | 0.0504 | ✓ |
| 0.4 | NIST_III_384| 0.0631 | ✓ |
| 0.4 | NIST_V_512  | 0.0741 | ✓ |
| 0.4 | log2p_576   | 0.0791 | ✓ |
| 0.4 | log2p_768   | 0.0926 | ✓ |
| 0.8 | NIST_I_256  | 0.0504 | ✓ |
| 0.8 | NIST_III_384| 0.0631 | ✓ |
| 0.8 | NIST_V_512  | 0.0741 | ✓ |
| 0.8 | log2p_576   | 0.0791 | ✓ |
| 0.8 | log2p_768   | 0.0926 | ✓ |

Worst error = 0.0926 bits ≤ 0.75 bits tolerance. **Gate: PASS** ✓.

#### gamma_null_refit anomaly

Observed: γ_null_refit = −0.003547 (from 47-ell C-NULL series, n=43 in W-MID).
Nominal in DEC-20260802-48c72c: −0.013241 (fitted on 21-ell nc2b series, n=21).

This discrepancy is properly annotated as an anomaly (run_log.txt line 54, nc2b_results.json
§ anomaly, nc2d_results.json § anomaly). The gate uses the refitted value from the
correct 47-ell input object; the gate result is valid. The discrepancy does not
constitute an anomalous finding about the hypothesis; it reflects the two series
having different ell ranges.

The non-claim preservation is intact: "PASS validates the INSTRUMENT only; cannot
be cited as validation of L1."

---

### CHK-4: Bibliographic scope

All three sources confirmed found. The elkies_prime_counting_constant_k_stated = false
for all three is the expected result:

- Sutherland 2013 addresses evaluation algorithms for Φ_ell(j(E),Y).
- Santos-Costello-Shi 2022 addresses Delfs-Galbraith subfield-root acceleration.
- Adj et al. 2018 addresses cost of isogenies for SIDH/CSSI.

None of these is the primary vehicle for the ~1/2 Elkies-prime counting fraction,
which is a standard result from the SEA (Schoof-Elkies-Atkin) literature. The
bib_results.json correctly identifies where to find it.

---

### CHK-5: Scope integrity

- `states_a_finding: false` in receipt.json, nc2d_results.json, nc2b_results.json ✓
- No hypothesis status change claimed in any artifact ✓
- Non-claims from frozen spec preserved: prior FC-4 firing not retroactively lifted;
  no crypto-scale claim made; all standing prohibitions from DEC-20260802-48c72c
  referenced ✓
- NC-3/NC-6 correctly characterised as failed_infrastructure (TASK-20260804-6519fa
  infra_failure_receipt.yaml); not used as evidence per AGENTS.md rule 5 ✓

---

### Qualifications

**Q-1 (informational)**: Jackknife interval labelled "95% CI" in handoff summary.
Frozen spec defines it as [min, max] of leave-one-out estimates, not a
standard 95% CI. Arithmetic is correct; label is non-standard. Future handoffs
should use "leave-one-out range" to avoid ambiguity.

**Q-2 (informational)**: TASK-20260804-6519fa (NC-3/NC-6 infra failure) is
untracked and not in snapshot b7b3240b4. It is outside the scope of this
validation, but the Coordinator should archive it before any review depending
on it.

---

### Admissibility

The run is **admissible**. Artifacts are complete, hashes verified, arithmetic
correct, regressor conforms to frozen spec, falsification gates properly
evaluated, scope statements intact. The two qualifications are informational
only and do not affect the evidential status of the run.

**Verdict: ACCEPT_WITH_QUALIFICATIONS**
