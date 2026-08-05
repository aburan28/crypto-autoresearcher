# Falsification Review — BATCH-403f13 / TASK-20260804-241b87
**Red Team Task:** TASK-20260804-83d874  
**Producer Task:** TASK-20260804-241b87  
**Snapshot Commit:** b7b3240b4266b85af1e0810831a66aa6e3300535  
**Verdict:** `pass_with_constraints`  
**Reviewed at:** 2026-08-05

---

## Executive Summary

The FC-4 non-firing result (gap = 0.0606, threshold = 0.15) at ell ∈ {47, 101,
151, 211} is supported by real computations: actual Phi_ell polynomial files from
MIT, actual supersingular primes (p ≡ 3 mod 4, verified via Miller-Rabin and
(p+1)P = ∞), and real field-multiplication counts via the committed per_entry_cost.py
instrument. The hypothesis of simulated/synthetic costs (raised in the context
prompt) is contradicted by the artifacts.

The result is constrained by five material qualifications. None of them reverses the
binary FC-4 verdict, but each bears on whether the MECHANISM-INCONSISTENT label
on L5 can be retired cleanly and what further work is required.

---

## OBJ-1: Were Phi_ell Evaluations Real or Simulated?

**Finding: Real, at toy scale.**

The context prompt suspected synthetic costs. The artifacts refute this:

| Check | Status | Evidence |
|---|---|---|
| C-PHI-VERIFY | PASS | All 4 Phi_ell files SHA-256 match committed hashes from RUN-PEC-49c773-a |
| C-BASE-1 (p1) | PASS | p1=1048571 prime, p≡3 mod 4, j=1728, (p+1)P=∞ for 3 random P |
| C-BASE-1 (p2) | PASS | p2=1073741783 prime, p≡3 mod 4, j=1728, (p+1)P=∞ for 3 random P |
| C-BASE-2 | PASS | Phi_ell parses and reduces mod p for all 5 ell at both primes |
| Wall-clock | 39 s | Consistent with actual polynomial GCD computation; not a lookup |

The implementation (nc2d_cpscale.py) calls PE.parse_modpoly → PE.reduce_modpoly →
PE.measure_primary → PE.measure_null — a chain of actual polynomial operations on
the downloaded and verified Phi_ell text files. The mults_rootfind counts (e.g.,
~504k for ell=47 at p1) are consistent with expected O(ell·log p) poly_powmod
iterations.

**Scope caveat:** The primes are p1=2^20, p2=2^30, p3=2^40. These are toy/medium
scale (AGENTS.md rule 7). The specification's own non-claim is explicit: "Measurement
is at p ~ 2^40 with Phi_ell reduced mod that prime; AGENTS.md rule 7 applies." The
FC-4 non-firing is established at this scale only.

---

## OBJ-2: Regressor Conflict and Alpha=1.13 Implication

**Finding: Conflict resolved correctly; alpha=1.13 is consistent with the Wesolowski
claim asymptotically, but introduces a concrete cost overestimate not yet propagated.**

The frozen spec unambiguously requires log2(log2 p) as regressor. The executor
correctly detected and resolved the conflict, recording it in raw-result.json,
manifest.yaml, receipt.json, and the stdout log. Using the correct regressor gives
alpha ≈ 1.13.

### Interpretation of alpha=1.13

With regressor log2(log2 p): **cost ~ C · (log₂ p)^1.13**

The theoretical L5 prediction is alpha = 1.0 (poly_powmod loop runs in O(ell · log p)
field multiplications, linear in log p). The measurement gives alpha = 1.13, within
the pre-registered band [0.85, 1.15].

**Asymptotic consistency:** alpha = 1.13 means cost is still poly(log p), consistent
with the o(1) exponent in Wesolowski's p^{1/3+o(1)} claim. The excess 0.13 contributes
(log p)^0.13 to the o(1) factor.

**Concrete consequence at cryptographic scale:**

| Field size | log₂ p | (log₂ p / log₂ 40)^0.13 | Cost multiplier vs alpha=1 |
|---|---|---|---|
| NIST-I (2^256) | 256 | (256/40)^0.13 ≈ 6.4^0.13 | ~1.27× |
| NIST-III (2^384) | 384 | (384/40)^0.13 | ~1.32× |
| NIST-V (2^512) | 512 | (512/40)^0.13 | ~1.39× |

The c-table entries in the current c-bracket are based on theoretical alpha = 1.0.
With measured alpha = 1.13, those entries underestimate the Phi_ell evaluation cost
by 27–39%. **This multiplicative factor has not been propagated into any updated
c-table.** The mandatory attachments MA-1 through MA-8 on the c-bracket remain in
force for exactly this reason.

### Wrong Regressor Counterfactual

If the executor had mistakenly used log2(p) as regressor, they would have computed
alpha ≈ 0.055 (the log2(p) slope for ell=47 is approximately (14.47-13.37)/(40-20) ≈
0.055). The FC-4 verdict would still have been the same (gap ≈ 0.001 << 0.15 with
log2(p) regressor), but the cost model reported would have been wrong (cost ~ p^0.055
rather than cost ~ (log p)^1.13). The correct regressor is essential for the
physical interpretation, even though the binary verdict is robust.

---

## OBJ-3: NC2b gamma_null_refit Anomaly

**Finding: PASS verdict is robust; the 3.7x gamma discrepancy is a real instability
in the power-law model, not a gate defect.**

The gamma_null_refit = −0.003547 vs the expected nominal −0.013241 from
DEC-20260802-48c72c is a factor-of-3.7 discrepancy in magnitude. The executor
correctly identifies the cause: two different input datasets.

| Dataset | ell range | n | gamma_null |
|---|---|---|---|
| EXP-PEC-6be870 nc2b series | ell 11..101 | 21 | −0.013241 |
| EXP-PEC-49c773 C-NULL (W-MID) | ell 11..211 | 43 | −0.003547 |

The NC2b spec correctly uses the 43-ell series (EXP-PEC-49c773 C-NULL). The gate uses
the refit value from the correct input. The gate PASS is robust:

- Worst error: 0.0926 bits
- Tolerance: 0.75 bits
- Margin: 0.6574 bits

Even if the full gamma discrepancy (Δγ = 0.0097 over log2(ell_max)=7.7) were
added: 0.0926 + 0.075 ≈ 0.168 bits << 0.75 bits. PASS is unaffected.

**Genuine concern:** A gamma that varies from −0.013 to −0.004 depending on the ell
range means the null cost per entry does not follow a stable power law in ell.
There are at minimum two regimes (short ell, long ell) or genuine curvature in the
ell-dependence. The NC2b PASS validates the INSTRUMENT at the 43-ell range (this
is the explicit non_claim in nc2b_results.json: "PASS validates the INSTRUMENT only;
cannot be cited as validation of L1"). The red team endorses this non-claim as a
necessary scope restriction.

### Degrees-of-Freedom Assessment

NC2b has 43 ell values, 2 free parameters → 41 residual df. This is adequate for
stable regression. No degrees-of-freedom concern.

---

## OBJ-4: Constant k Not Stated in Abstracts

**Finding: Expected gap; k is verifiable from paper bodies but unverified here;
the relevant k for Wesolowski's margins requires reading the paper body directly.**

### Why the abstracts don't contain k

The three retrieved papers address:
1. Sutherland 2013 — Phi_ell evaluation algorithms (not Elkies fraction counting)
2. Santos-Costello-Shi 2022 — Delfs-Galbraith acceleration via subfield root detection
3. Adj et al. 2018 — vOW/SIDH cost analysis

None of these is the primary locus of the Elkies-prime fraction. The abstract-level
retrieval finding ("not explicitly stated") is the expected outcome for this bibliographic
scope.

### Supersingular observation

For the C-PSCALE measurement context, the "k fraction" question is moot: for
supersingular curves with trace t = 0 over F_p (p ≡ 3 mod 4), the Frobenius
characteristic polynomial is x² + p. ALL ℓ-torsion is defined over F_p for
every prime ℓ ≠ p (the ℓ-torsion is (Z/ℓZ)²), so ALL ℓ-isogenies exist and
Phi_ell(j,Y) factors completely. The measurement confirms this: n_distinct_roots =
ell+1 or ell+2 at every sample point. For supersingular curves, the Elkies-prime
fraction is effectively 1.

### Relevant k for Wesolowski's margin rows

The k in Wesolowski's concrete cost table is a different constant — related to the
probability that a random walk step has a B-smooth degree isogeny, which is the
Canfield-Erdős-Pomerance smoothness probability Ψ(X,B)/X = u^{-u(1+o(1))} with
B = X^{1/u}. This is the P₀ term (Heuristic 1). The specific numeric value of k
in each margin row can only be verified by reading Wesolowski's body text (his
concrete-cost section or Table 2 equivalent).

The minimum k needed to sustain the margin claims cannot be determined from
abstracts. This is a known open item documented in the c-bracket's mandatory
attachments.

---

## OBJ-5: Campaign Synthesis — What Is Now Established vs. Not

### Established

1. **FC-4 non-firing (EXP-P13-NC2d):** |alpha_primary − alpha_null| = 0.0606 < 0.15
   at ell ∈ {47,101,151,211}, p ≤ 2^40. The MECHANISM-INCONSISTENT label on L5
   can be retired at this ell/p range. (Coordinator ledger archive required.)

2. **alpha ≈ 1.13 within band [0.85, 1.15]:** The p-scaling is approximately
   polynomial in log p, consistent with the L5 mechanism argument for the
   poly_powmod loop at the operating ell range.

3. **NC2b-SLOPE-G1 PASS (worst error 0.0926 bits, margin 0.6574 bits):** The
   slope-only cost law instrument is accurate at the 43-ell W-MID range.

4. **Three bibliography sources retrieved** at abstract level, confirmed at their
   stated venues.

### Not Established

1. **Heuristic 1 tail (NC-3/NC-6):** Infrastructure failure (TASK-20260804-6519fa,
   AGENTS.md rule 5). Zero experimental validation of the load-bearing probabilistic
   term in the Wesolowski theorem.

2. **Cryptographic-scale measurement:** All evidence is at p ≤ 2^40. AGENTS.md rule 7.

3. **Gap-vs-ell stability beyond ell=211:** The gap at ell ∈ {151,211} is already
   59% of the FC-4 threshold. No preregistered or executed check for gap trend with
   larger ell.

4. **alpha = 1.0 exactly:** The systematic excess of 0.13 is unidentified and
   uncompensated in the c-table.

5. **Margin-row k constant from Wesolowski body.**

### What Would Be Needed to Strengthen

| Item | Action | Priority |
|---|---|---|
| Heuristic 1 | Execute NC-3/NC-6 successfully | Critical |
| Gap-vs-ell trend | Fit gap vs log2(ell) over the 4 ell values; extend to ell={500,1000} | High |
| Alpha at crypto scale | Use Deuring correspondence or larger-p measurements | High |
| c-table with alpha=1.13 | Recompute margin rows with cost inflated 27–39% | High |
| k from paper body | Read Wesolowski Sections 4–5 and concrete-cost table | Medium |
| Regression robustness | Add 2–3 more p values to reduce single-df per-ell issue | Medium |

---

## Additional Red-Team Objections

### RT-OBJ-A: Gap-vs-ell Trend (Significant)

The per-ell gaps {47: 0.027, 101: 0.038, 151: 0.089, 211: 0.088} show a 3x jump
between ell ≤ 101 and ell ≥ 151. The pre-registered no-trend check tests
alpha_primary vs log2(ell) but NOT the gap vs log2(ell). The gap already reaches
59% of the threshold at the upper end of the measurement range.

**Falsification route:** Fit alpha_primary − alpha_null vs log2(ell). If b_gap > 0
and the extrapolation to ell ≈ 300–500 crosses 0.15, L5 is contradicted at those
ell values. The Wesolowski algorithm's B-smooth range may include such ell values.

### RT-OBJ-B: alpha=1.13 Not Propagated to c-Table (Significant)

The c-table entries in the existing c-bracket assume alpha = 1.0. With alpha = 1.13,
those entries underestimate per-entry cost by 27–39% at cryptographic scale. The
mandatory attachments (MA-1 through MA-8) remain binding precisely because this
extrapolation was provisional. This batch has now measured alpha = 1.13, providing
a concrete update. Until the c-table is recomputed with this value, the margin claims
are formally unaudited for this specific deviation.

### RT-OBJ-C: Sparse Regression, Simplified Jackknife (Moderate)

Three p values per ell = 1 residual df. Individual per-ell 95% CIs are very wide.
The jackknife interval [1.1260, 1.1409] is the range of four leave-one-ell-out simple
averages, not refitted pooled OLS estimates. Since all four per-ell alphas are tightly
clustered, this produces an artificially narrow interval. The true uncertainty in the
pooled alpha is larger than the reported range suggests.

This does not reverse the binary FC-4 verdict (gap of 0.0606 has ample headroom
vs threshold 0.15), but it means alpha = 1.13 ± [narrow] should be read as
"all four ell-specific estimates are consistent with each other" rather than
"alpha is known to within ±0.007."

### RT-OBJ-D: p3 Committed-Data Leverage Asymmetry (Moderate)

p3 is the highest-leverage point (extreme x-coordinate in log2(log2 p) space).
Its values are committed from a prior session with 8 j-values vs. 4 j-values for
the fresh p1/p2 measurements. Cross-session bias at the highest-leverage point
would be absorbed entirely into the slope estimate. The prior session's data was
independently validated (BATCH-003 validator), so gross errors are unlikely, but
the asymmetry contributes unquantified session-to-session variance to alpha.

### RT-OBJ-E: No Pooled-Gap Confidence Interval (Minor)

The pooled gap = 0.0606 is a point estimate with no CI. The per-ell null SE for
ell=101 is 0.038 (large), making the null alpha at ell=101 poorly constrained.
The absence of a gap CI means the headroom to the 0.15 threshold is claimed
informally. In practical terms, with gap = 0.06 and threshold = 0.15, the headroom
is large enough that formal testing is not urgent, but it should be noted for
completeness.

### RT-OBJ-F: Heuristic 1 Completely Unvalidated (Significant)

The NC-3/NC-6 infrastructure failure leaves Heuristic 1 — the conditional on which
the Wesolowski theorem rests — completely untested. This is not a mathematical
finding (rule 5), but it is the dominant gap in the campaign's evidence base.
The conditional asymptotic claim cannot be assessed without experimental validation
of Heuristic 1 at the relevant smoothness parameters.

---

## Narrowest Supported Statement

> At ell ∈ {47,101,151,211} (above Karatsuba threshold 16) and prime field sizes
> p ∈ {2^20, 2^30, 2^40}, the p-scaling exponent of Phi_ell evaluation cost
> (per_entry metric, IMPL-A, field-multiplication count) is approximately 1.13
> in the log₂(log₂ p) model, within the pre-registered band [0.85, 1.15].
> The primary–null gap is 0.06, below the pre-registered FC-4 threshold of 0.15.
> The MECHANISM-INCONSISTENT label on assumption L5 can be retired at this ell
> and prime range.
>
> This does not constitute cryptographic-scale evidence (p ≤ 2^40; AGENTS.md rule 7),
> does not validate Heuristic 1, does not certify margin-row constants, does not
> lift the prior FC-4 firing from EXP-PEC-49c773 at ell ∈ {3,5,7,11,13}, and does
> not constitute validation that the gap remains below 0.15 at ell > 211.
> The conditional asymptotic theorem (p^{1/3+o(1)} | Heuristic 1) is unaffected.

---

## Prohibitions Compliance

- No changes to hypothesis status, evidence records, or standing prohibitions.
- No Executor run receipts altered.
- No bounded failure (NC-3/NC-6 infra failure) called an impossibility result.
- No ECDLP conclusion claimed without a complete cost path.
- This report is a working-tree artifact; durability requires Coordinator ledger archive.

---

*Red Team: TASK-20260804-83d874 | Model: amazon-bedrock/us.anthropic.claude-sonnet-4-6*
