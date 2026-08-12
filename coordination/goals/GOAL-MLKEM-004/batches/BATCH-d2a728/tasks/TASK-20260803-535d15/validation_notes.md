# Validation Notes — TASK-20260803-535d15

**Producer task:** TASK-20260803-e53ce2  
**Snapshot commit:** `8cc51677f7202e9f9b85efdf834860254798abf4`  
**Verdict:** `accept_with_qualifications`  
**Validated at:** 2026-08-03

---

## 1. What was validated

This is an independent review of the batch-1 measurement for GOAL-MLKEM-004 /
BATCH-d2a728. The executor measured the per-vector dual-attack score
distribution of BGJ1-sieve-produced dual-lattice vectors on a dimension-60 LWE
instance (m=35, n=25, q=127, σ=2 rounded-Gaussian error, η=2 CB secret).

The key question is whether the data is **admissible as raw data** — i.e.,
whether the hashes are correct, the measurement ran as described, the null
object is valid, and the reported numbers are internally consistent.

**Scope boundary enforced:** this review does NOT compare against `MATZOV.Nf`
or any cost model (batch-2 work). It does NOT claim anything about FIPS 203
dimensions or ML-KEM security.

---

## 2. Hash verification

Every declared artifact was independently hashed (current working tree,
`git show` from the pinned commit). All six files match exactly:

| File | Expected sha256 | Match |
|------|----------------|-------|
| `raw_scores.json` | `892991c4...` | ✓ |
| `results.json` | `82cf8006...` | ✓ |
| `measure_scores.py` | `c93d41f8...` | ✓ |
| `rebuild_transcript.txt` | `99763183...` | ✓ |
| `receipt.json` | `d92002139...` | ✓ |
| `report.md` | `56848a46...` | ✓ |

The snapshot commit `8cc51677` adds exactly the seven declared paths (six task
artifacts plus `snapshot_receipt.json`) and no others. The commit message
is non-self-serving and correctly characterized as pre-review.

---

## 3. Certificate adequacy

The certificate checks `y ≡ Aᵀx (mod q)` on all 17,919 sieve vectors using
integer arithmetic independent of g6k's internal representation. Parameters
are well-formed (q=127 prime, m=35, n=25, d=60). The verification aborts
the script before reporting any score if it fails.

**Independent confirmation via phase equality:** The `x_dot_e_main` field
(= center_mod(xᵢ · e, q)) matches `phases_t[i]` for candidate 0 (correct
secret) for all 17,919 vectors exactly. This is only possible if
`yᵢ · s ≡ xᵢ · As (mod q)`, i.e., `yᵢ ≡ Aᵀxᵢ (mod q)`, confirming lattice
membership through the scoring identity independently of the explicit certificate
code.

Vector norms range [218, 329] with median 315. The Gaussian heuristic gives
||v||² ≈ 199 — actual norms are ~58% above GH minimum, consistent with the
BGJ1 sieve stopping before saturation at default parameters. Not a defect.

---

## 4. Secret leakage assessment

The correct secret `s` is placed as candidate index 0. The scoring function
`phases_for_target(b, Cmat[sub])` computes `center_mod(X·b − Y·Cmat[sub]ᵀ, q)`
where `Cmat` is the (K × n) matrix of all candidates. The secret is only a row
of `Cmat`; it receives no privileged treatment in the scoring pipeline.

**b_main reconstruction:** `As + e` recomputed independently from raw A, s,
e_main. Matches raw `b` field exactly: [8, 118, 9, 41, 87, ...].

**No leakage found.** The secret is not embedded in any scoring intermediate
other than as a candidate value in Cmat[0].

---

## 5. Null shape assessment

The null target uses `b_null` drawn uniformly from Z_q^m with seed 20260803003.

**Reconstruction:** `np.random.default_rng(20260803003).integers(0, 127, size=35)`
gives [2, 24, 79, 52, 36, ...] — matches raw `b` field exactly.

**b_null ≠ b_main** (confirmed); b_null is not b_main + noise or any LWE-related
vector.

**Theoretical soundness:** For any fixed (x,y) and any fixed s, the phase
`center_mod(x·b_null − y·s, q)` is approximately uniform on (−q/2, q/2] since
`x·b_null mod q` is uniform for nonzero x and b_null independent of s. Therefore
`E[cos(2πt/q)] ≈ 0` for any candidate s under the null. Confirmed by outcome:
correct secret ranks 18/33 with mean +0.00330, statistically indistinguishable
from the wrong-candidate mean (+0.00347).

**Alternative null design note:** Using a different secret as the "null candidate"
would be complementary rather than strictly better — with uniform b, the same
theoretical argument holds for any candidate. The current design is sound.

---

## 6. Raw-vs-summary agreement (independent recomputation)

All key numbers recomputed from `raw_scores.json` `phases_t` arrays using
`cos(2π·t/127)`:

| Quantity | Declared | Recomputed | Match |
|----------|----------|------------|-------|
| MAIN correct mean | 0.427375 | 0.427375 | ✓ |
| MAIN uniform_00 mean | 0.000679 | 0.000679 | ✓ |
| MAIN rank | 1/33 | 1/33 | ✓ |
| NULL correct mean | 0.003298 | 0.003298 | ✓ |
| NULL rank | 18/33 | 18/33 | ✓ |
| DECAY σ=0.5 mean | 0.94924 | 0.949240 | ✓ |
| DECAY σ=1.0 mean | 0.84115 | 0.841150 | ✓ |
| DECAY σ=4.0 mean | 0.018271 | 0.018271 | ✓ |
| DECAY σ=8.0 mean | 0.004641 | 0.004641 | ✓ |

**Phase-cosine identity:** emitted `scores_cos` vs recomputed `cos(2πt/q)`:
max absolute difference 4.87 × 10⁻⁷ (rounding to 6 decimal places only).

**All six decay b vectors** reconstructed from their seeds and match stored
values exactly, confirming no silent substitution.

**The results.json summary is fully re-derivable from raw_scores.json.**

---

## 7. Reproducibility

The rebuild transcript shows the reproduction run (identical script + seeds,
scratch directory) producing 17,919 vectors with all scientific values
bit-identical to the official run. The two files differ by 1 byte in size due
to 5 wall-clock timing leaves (check_seconds, scoring_seconds) changing
value. The sha256 of the repro file is different from the official
`892991c4...`; this is expected and correctly documented by the executor
(content equality, not hash equality, is the reproduction identity here).

This is physically plausible: numpy.default_rng, FPLLL.set_random_seed, and
g6k Siever(seed=469431436621) are all explicitly seeded. The sieve seed
`0x6D4C4B454D` = ASCII "mLKEM" — intentional and documented.

The instrument verification (step 0 of rebuild_transcript.txt) reproduced
KN-TECH-14efa5's exact benchmarks: fpylll BKZ-30 ||b₀|| 160.4 → 130.3 in
0.31s, g6k dim-50 gauss_sieve db 4075 in 0.93s. Both documented gotchas
reproduced. The instrument was verified functional before measurement.

---

## 8. Scope check

No comparison against `MATZOV.Nf`, `lwe_dual`, or any cost model was found
in `measure_scores.py`, `results.json`, or `raw_scores.json`. The one
reference to `MATZOV.Nf` in the script header is an explicit EXCLUSION
statement ("NOT against ..."). The receipt fields `states_a_finding: false`
and `compared_against_assumed_law: false` are correct. The scope constraint
was fully respected.

---

## 9. Outstanding items from Section 6 of report.md

| Item | Render data inadmissible? | Notes |
|------|--------------------------|-------|
| No MATZOV.Nf comparison | No — correctly deferred | Batch-2 work |
| Dim-60 / q=127 only | No — correct scope boundary | |
| One LWE instance | No — limitation noted | Affects generalizability, not admissibility |
| Distinguishing form only | No — scope limitation | |
| Dual vectors not in file (DEF-1) | No — phases_t sufficient for 33 candidates | Batch-2 fix recommended |
| Sieve quality defaults uncharacterized (DEF-4) | No — limitation on inference | |
| model_verified: false | No — correctly recorded | |

None of the Section 6 items render the data inadmissible.

---

## 10. Qualifications summary

Four qualifications are recorded:

- **DEF-1** (deferred): dual vectors absent from raw_scores.json; reviewer
  cannot score new candidates without re-running. Batch-2 fix.
- **DEF-2** (deferred): single instance; instance-to-instance variation unmeasured.
- **DEF-3** (minor): model fallback to claude-opus-5, correctly documented,
  fallback_allowed was set.
- **DEF-4** (minor): sieve quality parameters at defaults, effect uncharacterized.

None of these are blocking.

---

## 11. Verdict

**ACCEPT_WITH_QUALIFICATIONS.** The measurement is admissible as raw data.
All hashes match, the null object is correctly constructed and clean, the
reported numbers are independently confirmed, the scope constraint (no
cost-model comparison) was respected, and the instrument was verified functional
before measurement. The four qualifications are deferred limitations appropriate
for batch-2 investigation, not defects in the data itself.

This verdict is limited to raw-data admissibility. Whether the observed signal
(correct secret mean +0.42738, rank 1/33 at σ=2) is consistent with or
inconsistent with the MATZOV cost model's independence law is the subject of
batch 2 and is not assessed here.

---

*Validated by: TASK-20260803-535d15*  
*Inference: amazon-bedrock/us.anthropic.claude-sonnet-4-6 (review-adversarial,
fallback_allowed, independent_session: true)*
