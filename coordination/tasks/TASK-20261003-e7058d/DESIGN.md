# TASK-20261003-e7058d: zero-run re-draft of EXP-SEMBIN-3d9a71 (draft version 2) against HEUR-HARVEST-FV-1 version 2, clause (a)

- **Role and session.** idea-generator, policy research-deep, independent session, 2026-10-03. This session is not TASK-20261001-9b3e70, not either reviewer of REVIEW-SEMBIN-20261002-c7e1d4, and not the TASK-20261002-a84e65 designer. That rests on the session boundary only (§13).
- **Runs.** None. No Z4, Z3, N_2, R_2 or decomposition count of any F_V, or of any null list, was computed at any scale. Every number below is hand arithmetic and is labelled **scratch**. None of it is a measurement.
- **Curve selection.** Not performed. §5 specifies it for the executor's pre-run step.
- **Status.** Nothing committed, no record edited, no status changed. The version-1 draft (`coordination/tasks/TASK-20261002-a84e65/`) was read and not edited. The contract is `proposed-records/EXP-SEMBIN-3d9a71/specification.yaml`: version 2, `status: review_required`, no `approved_by` key.
- **Dispatch note (disclosed).** The user requested this run now. DP-1 (receipt of TASK-20261003-6d2f84), DP-2 (receipt of TASK-20261002-5f0b2c) and DP-3 (lane claim) did not hold, and the TASK-20261002-c13d8e snapshot had not run. The inputs were read from the working tree of branch `claude/continue-task-v5f6a5` (PR #1771, not merged), which this session could not verify because it had no shell or git (§13).
- **Security.** Nothing here is a statement about the security of any curve, in either direction. Degrees are parameter labels.

---

## 0. One-page summary

**Object under test.** F_V = {Q ∈ ⟨P⟩ : x(Q) ∈ V} on toy and medium binary curves. It is compared with a closure-matched random list F* whose size is matched per V to the realised |F_V|. Throughout this contract Γ = ⟨−1⟩ (§3). The σ-stable case is dropped by X5.

**Decision statistics (X2).** For a negation-closed list L:
- **Z4(L)** is the number of ±-classes of 4-element zero-sum subsets with no inverse pair.
- **Z3(L)** is the number of ±-classes of zero-sum multisets {s, s, u, v} with s, u, v distinct and no inverse pair. This is the raw Z3 that the clause tests on every arm here.
- **N_2** = Σ_{g≠O} C(r(g), 2) is computed, gated by the identity **N_2 = 6·Z4 + 2·Z3** on every list, and reported. It is never tested against a Poisson law.
- **R_2** = Z4 + Z3 is derived and reported. It is not a decision statistic (ambiguity B1).
- On Koblitz lists, every Z3 configuration is also classified as structural or not (§4). Z3_struct and Z3_excl = Z3 − Z3_struct are reported.

**Null.** For each sampled V_i there are M = 6 reference null lists plus 1 held-out placebo list (arm W uses M = 20 plus 1). Each null list is a union of |F_{V_i}|/2 distinct ±-orbits of uniform r ∈ [1, ℓ−1]. It is counted exactly in Z/ℓ, and a subset is pushed through the point path, where the two paths must agree exactly (G4). Every constant comes from the null sample. The references |F|^4/(48ℓ) for Z4 and |F|^3/(4ℓ) for Z3 enter only a [½, 2] counter sanity band (N-SCALE).

**Decision tests (X3).** All are two-sample, stratified-permutation tests against the null's empirical law. A stratum is {F_{V_i}, its M null lists}.
- **T4:** the cell total of Z4, by exact convolution, two-sided.
- **T3:** the cell total of Z3, by exact convolution, two-sided.
- **KS4:** two-sample KS on Z4, by Monte Carlo permutation.
- **MX4:** the max over V of Z4, upper tail. This is the tail check, and it is null-calibrated.
- Arm-pooled T4 and T3 are added for each of the five arms.
- Poisson fits of Z4 and the VMR of N_2 are **secondary** and are reported only.

**Null calibration (X3).** The v1 N-POI check is replaced by a **split-half null-versus-null calibration**: in every stratum, null halves A and B (3 + 3, or 10 + 10 on W) are compared by T4, T3 and KS4, with a frozen per-test threshold θ_SH = 10^-3/195 = 5.13·10^-6. A global uniformity check (GU) on randomised split-half and placebo p-values is frozen at p ≥ 5·10^-4 each.

**Decision rule.**
- α = 10^-3 family-wise, Bonferroni, over **m_max = 270** (X6). That is 4 tests × 65 cells + 2 pooled tests × 5 arms, frozen now. The raw threshold is **p ≤ 3.70·10^-6**.
- **FALSIFIED** requires all of:
  - the run is valid;
  - AP and GAP are flagged on T4 and T3 at corrected p < 10^-6;
  - SID4 and SID3 are flagged on the lower tail;
  - no placebo test rejects;
  - GU passes;
  - the cell's split-half check passes;
  - some decision test reaches raw p ≤ 3.70·10^-6.

  A pre-registered fresh-label replication then labels the result REPLICATED or UNREPLICATED.
- **PASS** requires the same validity conditions, no rejection, and the SENS power floors.
- **INCONCLUSIVE** and **INVALID** follow the v1 rules, with N-POI replaced as above (§10).

**Smallest detectable effect.** This is the rate ratio ρ_90 at power 0.9 against α′ = 3.70·10^-6 two-sided (z = 4.63), computed as δ_90 = 6.89/√E with M = 6 (scratch, normal approximation).

| λ_2 nominal | per-cell N_V | E[Z4 total] | Z4 ρ_90 excess / deficit | E[Z3 total] | Z3 per cell |
|---|---|---|---|---|---|
| 2^-2 | 1200 | 50 | 1.98 / near-total absence only | 0.6–1.2 | gross only |
| 2^-1 | 600 | 50 | 1.98 / — | 0.15–2.3 | gross only |
| 2^0 | 300 | 50 | 1.98 / — | 0.15–2.3 | gross only |
| 2^1 | 150 | 50 | 1.98 / — | 0.3–0.6 | gross only |
| 2^2 | 75 | 50 | 1.98 / — | 0.3–0.6 | gross only |
| 2^3 | 38 | 51 | 1.97 / — | 0.07–1.2 | gross only |
| 2^4 | 30 | 80 | 1.77 / ≤ 0.23 | 0.12–1.9 | gross only |
| 2^5 | 30 | 160 | 1.55 / ≤ 0.45 | 0.5–0.9 | gross only |
| 2^6 | 30 | 320 | 1.39 / ≤ 0.61 | 0.9–1.9 | gross only |
| **D3 band** (λ_2 2^11–2^14) | 30 or 60 | 10^4–8·10^4 | 1.02–1.07 / 0.93–0.98 | 60–120 | **1.63–1.89** / ≤ 0.37 |

- **Z3 needs a dense band.** In the λ-grid cells E[Z3] ≈ 12·E[Z4]/|F| ≤ 2.3, so Z3 is gross-only everywhere on that grid. The **D3 band** (§3.3) puts |F|^3 ≈ 4ℓ to 16ℓ, which is the factor-base density of 3-term decompositions. It is the only place this contract can resolve Z3 at about one bit.
- **Arm-pooled Z4 ρ_90:** O4 1.14, O2 1.26, W 1.17, KR 1.34, D3 1.012.
- **Arm-pooled Z3 ρ_90:** D3 1.31; elsewhere gross only.
- **The λ_2 = 2^-2 limit.**
  - Each list has P(Z4 = 0) ≈ 0.959 under the null.
  - N_V = 1200 buys ρ_90 = 1.98.
  - Deficits are unresolvable except near-total absence.
  - V-classes rarer than about 1/1200 are invisible. That includes V ⊂ ker Tr, at density about 2^-11 to 2^-12.
  - Z3 is unresolvable there.

**Arms after X5.**
- **O4** (h = 4, two curves per n) and **O2** (h = 2, one curve per n), with uniform random V.
- **W**: polynomial-basis windows, which version 2's SCOPE treats as a separate structured claim.
- **KR**: Koblitz curves with non-σ-stable random V. Toy scratch predicts only n = 41, a = 0 is admissible, giving 3 cells. Admissibility is decided at S0-3.
- **D3**: the Z3-resolving dense band, on O4a and O2 at n ∈ {31, 37, 41}.
- **V3**: an optional, disclosed-weak arm at n = 131, outside the family.
- **KS is dropped**, and the **σ-stable sub-clause is UNTESTED**.

**Koblitz structural families (X4).**
- §4 re-derives from the definition that the only intra-orbit configurations with f(π) = 0 in ℤ[π] are the two Z3 families:
  - {w, w, [λ²]w, −μ[λ]w}, from X² − μX + 2;
  - {w, w, μ[λ³]w, μ[λ]w}, from X³ + X + 2μ.
- There is no Z4 family.
- Each full ⟨±λ⟩-orbit therefore carries Z3_struct = 2n ±-classes, which is **N_2 = 4n**. That matches VAL JR3-B2.
- G3 now expects this value for a full orbit, where version 1 expected 0. G16 checks the derivation by exhaustive enumeration and brute force on three Koblitz calibration curves.
- Version 2's exclusion applies only to σ-stable V, and no such cell exists here. It is therefore implemented, gated and reported (raw and excluded) on KR and on gate lists, but it governs no decision cell (§4.4).

**Ambiguities found in version 2** (§2.2, each with a proposed restatement):
- **B1.** R_2 is undefined.
- **B2.** The exclusion is silent on π-related triples in non-π-closed lists.
- **B3.** Curve-specific "accidental" intra-orbit relations are not addressed.
- **B4.** The N_2 identity on π-closed lists is stated for Γ = ⟨−1⟩ classes only.
- **B5.** No direction is stated.
- **B6.** The joint law is stated but no joint test is specified.
- **B7.** |F_V| = 0 is not covered.
- **B8.** "V inside ker Tr" sits inside the a-rand sample.
- **B9.** "Same distribution" is ambiguous between unconditional and size-conditional readings.

None blocks the test. B2 and B3 matter only for the untested σ-stable sub-clause, or for a measure-zero event on KR.

**Cost (scratch, advisory).**
- About 2.5·10^10 point additions and up to about 6.4·10^11 integer pair-sums: roughly 3 to 4 CPU-hours with a compiled kernel.
- The largest cell (D3, O2, n = 41, D = 15) takes about 25 minutes.
- Peak memory is about 1 to 1.5 GiB: 2^27 64-bit keys, sorted.

**dominated_by:** "n/a (no result claimed)". **sota_delta:** 0 on time, memory and data/queries, under every outcome.

---

## 1. R6 X1 to X9: where each item is met

| R6 item | requirement (abridged) | met in | how / reason |
|---|---|---|---|
| **X1** | Quote HEUR-HARVEST-FV-1 v2 clause (a), SCOPE and falsification_condition verbatim, bound by the file's sha256 at the ledger commit; mark A1–A11 resolved or carried | §2.1, §2.3; spec `heuristic_as_stated` | Quoted verbatim, lines 371–403 and 438–444 of `ledger/hypotheses/H-SEMBIN-c7e1d4.yaml`. **sha256 NOT computed**: no shell in this session, and the binding commit (TASK-20261003-6d2f84) does not yet exist. The field is `null` with that reason and is an approval precondition. A1–A11 are dispositioned in §2.3. New ambiguities B1–B9 are in §2.2 |
| **X2** | Decision statistics Z4 and Z3 (R_2 = Z4 + Z3); N_2 computed, gated by N_2 = 6Z4 + 2Z3, reported; no decision test is a Poisson fit of N_2 | §3.1, §8 (T4, T3, KS4, MX4), G9, G15 | Z4 and Z3 are the only decision statistics. N_2 is gated (G9) and reported. R_2 is reported, not tested (B1; X3's "or of Z4 and Z3" branch). The **D3 band** is added so that the Z3 test has power somewhere (§3.3). It is severable: if declined, re-draft with m_max = 244 |
| **X3** | Two-sample tests against the null's empirical distribution; split-half null-vs-null calibration with frozen threshold replaces N-POI; Poisson fits secondary | §8.2, §8.3, C-NULL | Stratified-permutation T4, T3, KS4 and MX4. SH calibration at θ_SH = 5.13·10^-6 per test, frozen, plus GU at 5·10^-4. Poisson fit of Z4 and VMR of N_2 are secondary. The FALSIFIED condition cites SH, not Poisson (§10) |
| **X4** | Re-derive the X²−tX+2 and X³+X+2t families from the definition; gate by brute force on calibration curves; apply v2's exclusion; report raw and excluded; correct v1 G3-EXCL | §4, G3, G16, C-PLANT | Derivation in §4.2: exactly two families, both Z3-type, 2n ±-classes and 4n coincidences per orbit, and no Z4 family. G16 enumerates exhaustively plus brute force on KCAL-13, KCAL-17 and KCAL-23. G3's full-orbit case is corrected to N_2 = 4n + 6Z4_acc + 2Z3_acc. The exclusion is implemented and reported raw and excluded. Its scope (σ-stable V) is empty here, so it governs no decision cell (§4.4) |
| **X5** | Ordinary + arm KR (non-σ-stable V on admissible Koblitz); drop KS; σ-stable sub-clause UNTESTED; recompute arm sizes and power | §3.2, §6, §10 | KS is removed. KR is frozen at the scratch-predicted admissible curve (n = 41, a = 0), with 3 cells. Admission is still decided at S0-3; any other admitted Koblitz curve runs reported-only. The σ-stable sub-clause is recorded UNTESTED. Sizes and power are in §6 |
| **X6** | m_max recomputed from the re-drafted cell table and frozen | §8.1; spec `statistical_plan` | C = 24 + 10 + 22 + 3 + 6 = 65 cells, × 4 tests + 5 arms × 2 pooled = **270**, frozen. Not reduced if cells fail admission |
| **X7** | Tested V distribution conditioned on \|F_V\| > 0; log skip rate; record \|F_V\| against trace-geometry classes (O9) as secondary | §3.4, metrics | Tested law: V uniform among D-dimensional subspaces, conditioned on \|F_V\| > 0. The skip rate is logged per cell (G6-SKIP). Each V's trace class T0/T1, Tr(A), h and \|F_V\|/(2^D/h) are secondary. The null stays matched to the realised size |
| **X8** | Rewrite decision_it_changes and hypothesis_link per R6 X8 | §11; spec `decision_it_changes`, `hypothesis_link` | FALSIFIED voids the generic layer's application to F_V for every harvester outside the conservation-law laws, at the cell's scope (CH-2; JR1-B2). hypothesis_link → P3 of the filed H-SEMBIN-c7e1d4 |
| **X9** | allocate_id.py --check EXP-SEMBIN-3d9a71; git grep 3d9a71; TASK-20261002-5f0b2c receipt | §13; spec `approval.approval_preconditions` | **Not met here, for a stated reason**: no shell. A Grep of `ledger/`, `knowledge/` and `experiments/` found 3d9a71 only in records that name this experiment (§13). All three checks are carried as approval preconditions |

---

## 2. The heuristic as filed (X1), and its ambiguities

### 2.1 Verbatim text

**Source:** `ledger/hypotheses/H-SEMBIN-c7e1d4.yaml`, `heuristic_assumptions[0]` (id HEUR-HARVEST-FV-1, restatement_version 2), field `formal_statement`, lines 371–403, and field `falsification_condition`, lines 438–444. The text was read from the working tree on 2026-10-03.

**sha256: not computed.** There was no shell. Binding is owed at the TASK-20261003-6d2f84 ledger commit, which does not yet exist. The lines are copied without the file's YAML indentation. In the record both fields are folded scalars (`>-`), so the field value is these lines joined by single spaces.

Preamble, lines 371–378, quoted because it defines Γ and F*:

```text
Fix (n, E, <P>, V): E/F_{2^n} a binary curve with n prime, <P> of prime
order l with cofactor h in {2, 4}, V an F_2-subspace of F_{2^n} of
dimension D, and F = F_V = {Q in <P> : x(Q) in V}, which is
negation-closed. Let Gamma = <-1>, or Gamma = <-1, pi> on a Koblitz
curve with sigma-stable V (then F is also pi-closed and pi acts on <P>
as [lambda]). Let F* be a uniform union of the same number of distinct
Gamma-orbits of <P> \ {O} as F (size matched to the REALISED |F_V| per
V, never to 2^D/h). Targets R are uniform in <P>.
```

Clause (a), lines 379–392:

```text
(a) TWO-SUM CONFIGURATIONS. Let Z4(L) be the number of Gamma-classes of
4-element subsets {u1, u2, u3, u4} of L with u1 + u2 + u3 + u4 = O and
no inverse pair, and Z3(L) the number of Gamma-classes of zero-sum
multisets {t, t, u, v} (t, u, v distinct, no inverse pair). On Koblitz
lists with sigma-stable V, exclude from Z3 the two structural families
inside each orbit, from X^2 - tX + 2 and from
(X + t)(X^2 - tX + 2) = X^3 + X + 2t, and report their count
separately. CLAUSE: (Z4(F), Z3(F)) and (Z4(F*), Z3(F*)) have the same
distribution. The raw count N_2 = sum_{g != O} C(r(g), 2) over
2-element subsets satisfies N_2 = 6 Z4 + 2 Z3 on negation-closed lists
(Gamma = <-1>), with clumps of 6n on pi-closed lists, so N_2 is
compound Poisson and is reported, not tested against a Poisson law.
Poisson(mu) with mu ~ |F|^4/(48 l) (Z4, ordinary) is a REFERENCE only;
every constant comes from the null sample.
```

SCOPE, lines 397–403:

```text
SCOPE. "Fix V" is read as V uniform among D-dimensional subspaces
(a-rand). Structured V (polynomial-basis windows; sigma-stable V; V
inside ker Tr) are separate cells, each its own claim. The
sigma-stable Koblitz sub-clause applies only where a testable cell
exists. On the n-grid {31, 37, 41, 43, 47} none is expected
(VAL-20261003-17b1e4 JR3-B7, toy scratch), so that sub-clause is
UNTESTED until a design supplies one.
```

falsification_condition, lines 439–444:

```text
At a tested cell, with every gate passing, the positive controls
flagged, and the null passing a split-half null-versus-null
calibration (not a Poisson fit): a two-sample departure of Z4 or Z3 of
F_V from the closure-matched null at Bonferroni-corrected p < 10^-3
over a multiplicity count frozen before any run. Any tail check uses
the null-calibrated compound law.
```

**Notation.** In the clause, "t" in the polynomials is the Frobenius trace. This document writes it **μ = (−1)^{1−a} = ±1**, as in the v1 definitions, and writes the doubled element of a Z3 multiset as **w** or **s**, to avoid the clash.

### 2.2 Ambiguities in version 2 (reported, not designed around), with proposed restatements

- **B1 (minor). R_2 is not defined in version 2.** R6 X2 says "R_2 = Z4 + Z3 as defined by version 2", but the filed text defines only Z4, Z3 and N_2.
  - This contract defines R_2 := Z4 + Z3, with Γ = ⟨−1⟩ in every cell here.
  - R_2 is derived and reported only. X3's "or of Z4 and Z3" branch is taken.
  - Proposed restatement: add "R_2(L) := Z4(L) + Z3(L), reported, not tested", or delete R_2 from R6's wording.
- **B2 (minor here; material for a σ-stable design). The exclusion's domain.** "On Koblitz lists with sigma-stable V, exclude ..." is silent about lists that are not π-closed but contain π-related triples. A random V can be partially σ-compatible, so F_V on KR can contain {w, w, [λ²]w, −μ[λ]w} (§4.4).
  - As filed, such a configuration counts in Z3 on KR. That is a real departure, carried by Frobenius structure beyond Γ = ⟨−1⟩.
  - The scratch expectation per random V is about 2^{3D−2n}, effectively 0.
  - This contract tests the clause as filed: the decision Z3 on KR is raw. Z3_struct and Z3_excl are reported. A KR falsification carried only by structural configurations is labelled FALSIFIED-STRUCTURAL.
  - Proposed restatement: "On every Koblitz list, classify Z3 configurations as structural (the two families) or not. Exclude structural configurations only when Γ ∋ π; otherwise count them and report them separately."
- **B3 (σ-stable only). Curve-specific intra-orbit relations.** For a fixed Koblitz curve, any f with f(λ) ≡ 0 (mod ℓ) gives the same relation in every full orbit, deterministically and identically in F_V and F*. That includes members of the ideal (ℓ, π−λ) such as multiples of π^n − 1.
  - Version 2 excludes only the two families with f(π) = 0 in ℤ[π].
  - At n ≥ 31 the scratch expectation of such accidentals is about n³/ℓ ≈ 10^-4 per curve. At the calibration curves they occur, for example about 3 Z4 classes per orbit at n = 13.
  - Proposed: "exclude every intra-orbit configuration (all f with f(λ) ≡ 0 mod ℓ), report it separately, and record which are structural". This has no effect on any cell here (§4.3).
- **B4 (σ-stable only). The N_2 identity on π-closed lists.** "N_2 = 6 Z4 + 2 Z3 on negation-closed lists (Gamma = <-1>)" holds with ±-class counts. With Γ = ⟨−1, π⟩ classes, and orbits of size n by DESIGN v1 A1, it reads N_2 = 6n·Z4 + 2n·Z3_raw, where Z3_raw includes the 2 structural classes per orbit. Equivalently N_2 = 6n·Z4 + 2n·Z3_excl + 2|F|, in agreement with VAL JR3-B2.
  - Proposed: state the Γ = ⟨−1, π⟩ form explicitly. It has no effect here.
- **B5. Direction.** "A two-sample departure" states no direction. Carried forward as two-sided, so excess and deficit both falsify (v1 A9).
- **B6. Joint versus marginal law.** The CLAUSE equates the joint law of (Z4, Z3). The falsification_condition speaks of "a departure of Z4 or Z3", which is marginal. This contract tests the marginals. A departure in dependence only, with equal marginals, is not resolved. Under the null Z3 is sparse and nearly independent of Z4, so this is disclosed as a limitation.
  - Proposed: replace "(Z4(F), Z3(F)) and (Z4(F*), Z3(F*)) have the same distribution" with "Z4 and Z3 each have the same distribution under F and F*".
- **B7. Empty factor bases.** V with |F_V| = 0 are not addressed. R6 X7 makes the tested law conditional on |F_V| > 0.
  - Proposed: "V uniform among D-dimensional subspaces with |F_V| > 0".
- **B8. "V inside ker Tr" inside the a-rand sample.** SCOPE makes ker-Tr subspaces a separate claim, but a uniform V lands inside ker Tr with probability about 2^-D.
  - This contract keeps such draws in the a-rand sample, because they are draws from the uniform law, and flags them in the trace record.
  - The ker-Tr structured class is not tested as its own cell, so it is **UNTESTED**.
  - Polynomial-basis windows may lie mostly inside ker Tr (§3.4). W therefore mixes two structured classes, and W is reported per trace class as a secondary result.
- **B9. "Same distribution" when |F_V| varies with V.** The contract reads the clause as size-conditional: given the realised size s, the law of Z4 (or Z3) under V uniform with |F_V| = s equals its law under F* of size s. The stratified permutation tests exactly this exchangeability. An unconditional reading would compare against a null whose sizes are drawn from the |F_V| law, which differs only through the size distribution itself. That size distribution is recorded (X7) and is not the claim.

None of B1–B9 makes clause (a) untestable on the cells of this contract.

### 2.3 Disposition of v1 statement issues A1–A11

| v1 issue | disposition under version 2 |
|---|---|
| A1 (N_2 not Poisson under its own null) | **Resolved by v2.** The clause is on Z4 and Z3. N_2 is reported only, and Poisson is a reference only |
| A2 ({a, a} pairs) | **Resolved by v2.** 2-element subsets for N_2. The former {a, a} identity 2a = μπa − π²a is now the family-1 Z3 multiset {a, a, π²a, −μπa}, excluded where Γ ∋ π |
| A3 (three readings of "π-images excluded") | **Resolved by v2.** Γ-classes plus the explicit two-family exclusion. Moot here, since Γ = ⟨−1⟩ in every cell |
| A4 (every V or random V) | **Resolved by v2** SCOPE: a-rand; structured V are separate claims (W here; σ-stable and ker-Tr UNTESTED) |
| A5 (realised size) | **Resolved by v2:** "size matched to the REALISED \|F_V\| per V" |
| A6 (omitted \|F\|^3 term) | **Resolved by v2.** Z3 is explicit, and constants come from the null |
| A7 (no tolerance) | **Carried forward.** The operative tolerance is this contract's reported resolution ρ_90 (§6) |
| A8 (which λ in the tail clause) | **Resolved by v2:** "Any tail check uses the null-calibrated compound law". MX4 is permutation-calibrated |
| A9 (direction) | **Carried forward** as B5: two-sided |
| A10 (transfer to n ≥ 97) | **Carried forward** as TA-1, by assumption |
| A11 (σ-stable sub-clause untestable on the grid) | **Resolved by v2** SCOPE: UNTESTED. KS is dropped (X5) |

---

## 3. Statistics, null, arms and cells (frozen definitions)

### 3.1 Statistics (X2)

- **r_L(g)** = #{{a, b} ⊂ L : a ≠ b, a + b = g}.
- **N_2** = Σ_{g≠O} C(r(g), 2). It is computed by sorting all 2-subset sums as 64-bit keys and counting runs.
- **Z3** has two independent routes:
  - closed form, Z3 = ½·Σ_{s∈L} [r(−2s) − 1{−3s ∈ L}];
  - enumeration: for each s and each u ∈ L, check −2s − u ∈ L in a hash set of L. This lists every configuration, which the structural classifier needs.

  The two routes must agree (G9).
- **Z4** = (N_2 − 2·Z3)/6, which must be a non-negative integer (G9). On lists with |L| ≤ 48, G1 brute force checks Z4 directly from the definition.
- **R_2** = Z4 + Z3, reported only.
- **Z3_struct** (Koblitz curves only) is the number of Z3 configurations matching a §4 family pattern. Z3_excl = Z3 − Z3_struct. On ordinary curves Z3_struct := 0.
- **Identity derivation (scratch, after DESIGN v1 A1).** A coincidence {{a,b},{c,d}} with a + b = c + d ≠ O has {a,b} ∩ {c,d} = ∅.
  - At most one of a, b equals the negation of one of c, d. Both cannot, because that forces c + d = O.
  - If none does, T = {a, b, −c, −d} is a Z4 set. T and −T together yield exactly six coincidences.
  - If one does (say b = −c), the multiset {−c, −c, a, −d} is Z3. It and its negation yield exactly two.
  - Hence N_2 = 6·Z4 + 2·Z3, gated by G9 and checked by G1.
- **Structural identities checked on every list:** Σ_g r(g) = C(|L|, 2); r(O) = |L|/2; r(g) = r(−g).
- **Point-path key.** The key is (x(g) ≪ 1) | b(g), where b(g) is bit j of y(g) and j is the index of the lowest set bit of x(g). This separates g from −g = (x, x + y) without an inversion. Mutant M4 (x-only key) must be caught.

### 3.2 Arms (X5)

| arm | curves | V | Γ | M (+ placebo) | role |
|---|---|---|---|---|---|
| **O4** | O4a, O4b: ordinary, A = 0, h = 4, two per n | uniform rank-D | ⟨−1⟩ | 6 (+1) | a-rand |
| **O2** | O2: ordinary, A = 1, h = 2, one per n | uniform | ⟨−1⟩ | 6 (+1) | a-rand |
| **W** | O4a and O2 | all windows W_s = span{z^s, …, z^{s+D−1}}, s = 0..n−D, with \|F_V\| > 0 | ⟨−1⟩ | 20 (+1) | structured-V claim (separate) |
| **KR** | admissible Koblitz E_a. Frozen family: (n = 41, a = 0, h = 4), per toy scratch (VAL JR3-B7) | uniform, non-σ-stable (rejected and logged if σ-stable) | ⟨−1⟩ | 6 (+1) | a-rand on Koblitz |
| **D3** | O4a and O2 at n ∈ {31, 37, 41} | uniform | ⟨−1⟩ | 6 (+1) | a-rand, Z3-resolving density |
| **V3** (optional) | ECC2K-130 (a = 0, n = 131), from `inputs/BAILEY-2009-541-ECC2K130/paper_fulltext.md` lines 1093–1098 | 3 uniform V, D = 16 (not σ-stable, since ord_131(2) = 130) | ⟨−1⟩ | none | disclosed-weak, outside the family |

- **KS (σ-stable V) is dropped.** The σ-stable sub-clause is **UNTESTED** (SCOPE; VAL JR3-B7: at n = 41 the σ-stable dimensions are {0, 1, 20, 21, 40, 41}, which give λ_2 of about 2^30 or more).
- **KR admission.** If S0-3 admits any further Koblitz curve (any (n, a) other than (41, 0)), contradicting the scratch, its cells run **reported-only**. They are outside the Bonferroni family, labelled, and can neither falsify nor pass. A raw p ≤ 3.70·10^-6 there routes to the Coordinator as a signal outside the frozen family. If (41, 0) is not admitted, KR is empty and m_max is unchanged.

### 3.3 Cell table (frozen; C = 65)

Scratch sizes: h = 4 gives |F| ≈ 2^{D−2}, ℓ ≈ 2^{n−2}, λ_2 = 2^{4D−n−9} and μ3 = |F|^3/(4ℓ) = 2^{3D−n−6}. h = 2 gives |F| ≈ 2^{D−1}, ℓ ≈ 2^{n−1}, λ_2 = 2^{4D−n−6} and μ3 = 2^{3D−n−4}. Throughout, μ4 = λ_2/6 is the per-list Z4 mean.

**O4 (O4a and O4b; 12 cells each, 24 in total), also KR rows at n = 41 (3 cells), also W on O4a (12 cells).**

| n | D | e = log2 λ_2 | \|F\| | N_V (random V) | E4 = N_V λ/6 | E3 = N_V μ3 |
|---|---|---|---|---|---|---|
| 31 | 10 | 0 | 2^8 | 300 | 50 | 2.3 |
| 31 | 11 | 4 | 2^9 | 30 | 80 | 1.9 |
| 37 | 11 | −2 | 2^9 | 1200 | 50 | 1.2 |
| 37 | 12 | 2 | 2^10 | 75 | 50 | 0.6 |
| 37 | 13 | 6 | 2^11 | 30 | 320 | 1.9 |
| 41 | 12 | −2 | 2^10 | 1200 | 50 | 0.6 |
| 41 | 13 | 2 | 2^11 | 75 | 50 | 0.3 |
| 41 | 14 | 6 | 2^12 | 30 | 320 | 0.9 |
| 43 | 13 | 0 | 2^11 | 300 | 50 | 0.3 |
| 43 | 14 | 4 | 2^12 | 30 | 80 | 0.2 |
| 47 | 14 | 0 | 2^12 | 300 | 50 | 0.15 |
| 47 | 15 | 4 | 2^13 | 30 | 80 | 0.12 |

**O2 (10 cells), also W on O2 (10 cells).**

| n | D | e | \|F\| | N_V | E4 | E3 |
|---|---|---|---|---|---|---|
| 31 | 9 | −1 | 2^8 | 600 | 50 | 2.3 |
| 31 | 10 | 3 | 2^9 | 38 | 51 | 1.2 |
| 37 | 11 | 1 | 2^10 | 150 | 50 | 0.6 |
| 37 | 12 | 5 | 2^11 | 30 | 160 | 0.9 |
| 41 | 12 | 1 | 2^11 | 150 | 50 | 0.3 |
| 41 | 13 | 5 | 2^12 | 30 | 160 | 0.5 |
| 43 | 12 | −1 | 2^11 | 600 | 50 | 0.3 |
| 43 | 13 | 3 | 2^12 | 38 | 51 | 0.15 |
| 47 | 13 | −1 | 2^12 | 600 | 50 | 0.15 |
| 47 | 14 | 3 | 2^13 | 38 | 51 | 0.07 |

**D3 (6 cells).** This is the Z3-resolving band: μ3 ∈ [1, 4], i.e. |F|^3 ≈ 4ℓ to 16ℓ, the density at which 3-term decompositions of a target exist (m = 3).

| curve | n | D | \|F\| | λ_2 | μ4 | μ3 | N_V | E4 | E3 |
|---|---|---|---|---|---|---|---|---|---|
| O4a | 31 | 13 | 2^11 | 2^12 | 683 | 4 | 30 | 20480 | 120 |
| O4a | 37 | 15 | 2^13 | 2^14 | 2731 | 4 | 30 | 81920 | 120 |
| O4a | 41 | 16 | 2^14 | 2^14 | 2731 | 2 | 30 | 81920 | 60 |
| O2 | 31 | 12 | 2^11 | 2^11 | 341 | 2 | 30 | 10240 | 60 |
| O2 | 37 | 14 | 2^13 | 2^13 | 1365 | 2 | 30 | 40960 | 60 |
| O2 | 41 | 15 | 2^14 | 2^13 | 1365 | 1 | 60 | 81920 | 60 |

Notes on the table:
- **Sizing rule.** Random-V λ-grid cells use N_V = max(30, ⌈300/λ_nom⌉). D3 uses N_V = max(30, ⌈60/μ3⌉). W uses N_V = the number of windows with |F_V| > 0.
- **Why D3 stops at n = 41.** n ≥ 43 would need |F| ≈ 2^15 and 2^29 keys, beyond the 4 GB envelope.
- **Total cells:** 24 (O4) + 10 (O2) + 22 (W) + 3 (KR) + 6 (D3) = **65**.
- **Grid coverage.** Every λ-grid value occurs at two or three n in the ordinary arms. KR is single-n: its reading is scoped to n = 41, and C-SCALE is met by the ordinary arms.

### 3.4 V distribution, empty factor bases and trace geometry (X7)

- **Tested law.** V is uniform among D-dimensional F_2-subspaces of F_{2^n}, **conditioned on |F_V| > 0**. On W the tested set is the windows with |F_V| > 0.
- **Empty factor bases are skipped and logged.** A V with |F_V| = 0 is skipped and replaced by the next index, and the skip is logged with its label. The per-cell **skip rate** = skipped / consumed is a reported metric. G6-SKIP checks that consumed indices equal tested indices plus logged skips, recomputed independently.
- **Trace-geometry classes (RT-20261003-24c995 O9).** On ⟨P⟩, Tr(x(Q)) = Tr(A) is constant (VAL scratch S3). Each V is classed **T1** if V ⊂ ker Tr, else **T0**. The record also holds Tr(A), h, |F_V|, |F_V|/(2^D/h), the count of x ∈ V that are x-coordinates of points of E, and the count of those in 2E.
- **Scratch expectations** (reported, never decided):
  - T0: ratio about 1.
  - T1 with h = 2 (A = 1, Tr(A) = 1): F_V = ∅, so the V is skipped.
  - T1 with h = 4 (A = 0): ratio about 2.
  - For uniform V, P(T1) ≈ 2^-D, so the expected skip rate on O2 is about 2^-D, and about 0 on O4 and D3.
- **Windows (recalled, unverified).** For a trinomial basis, Tr(z^i) = 1 only for i ∈ {0, n − k} or i = 0 alone. If that holds, most windows lie in ker Tr. Then on O2, most windows give F_V = ∅ and the W cells shrink to the windows that contain index 0 or n − k. On O4a, most windows have |F_V| doubled, which raises λ_2 by about 16.
  - This is why W's realised N_V and trace class are fixed at S0-3, before any statistic, and why W cells with null-estimated Ê4 = N_V·mean_null(Z4) < 1 are recorded UNTESTED.
  - m_max is unchanged either way.
- **The null stays matched to the realised |F_{V_i}|.**

### 3.5 Null lists

- **Construction.** Each stratum i has lists j = 0..M:
  - j = 0 is the **placebo**;
  - j = 1..M are the **references**;
  - halves A = {1..M/2} and B = {M/2+1..M} are used for split-half calibration.
- **Sampling.** Each list is a union of |F_{V_i}|/2 distinct ±-orbits {r, −r}, with r drawn uniformly from [1, ℓ−1] by a SHA-256 counter DRBG under the label `EXP-SEMBIN-3d9a71|<cell>|null|<i>|<j>`. Repeated orbits are rejected. Lists are counted in Z/ℓ.
- **Point path.** At least 5 reference lists per cell are also counted on the point path (G4).

---

## 4. Koblitz structural families (X4)

### 4.1 Setting

- E_a is y² + xy = x³ + ax² + 1 over F_{2^n}, n prime, with μ = (−1)^{1−a}.
- π(x, y) = (x², y²) satisfies π² − μπ + 2 = 0 in End(E). It acts on ⟨P⟩ as [λ], where λ² − μλ + 2 ≡ 0 and λ^n ≡ 1 (mod ℓ).
- A full ⟨±λ⟩-orbit is {ε[λ^i]u : ε = ±1, i ∈ ℤ/n}, of size 2n. It is size 2n because λ has odd order n, so −1 is not a power of λ (v1 A1).
- An intra-orbit Z4 configuration is a polynomial f(X) = Σ_{j=1..4} ε_j X^{i_j} with distinct exponents mod n.
- An intra-orbit Z3 configuration is f(X) = 2ε_0X^{i_0} + ε_1X^{i_1} + ε_2X^{i_2} with distinct exponents.
  - Distinct elements with no inverse pair forces distinct exponents.
  - The configuration is a zero sum iff f(λ) ≡ 0 (mod ℓ). That condition does not depend on u, so it holds in every orbit of the curve or in none.
- **Definition.** A configuration is **structural** iff f(π) = 0 in ℤ[π] for some integer lift of its exponents. Since X² − μX + 2 is irreducible and monic, this means (X² − μX + 2) divides f in ℤ[X]. Otherwise a zero configuration is **accidental**: f(π) ∈ (ℓ, π − λ) \ {0}, which is curve-specific.

### 4.2 Derivation (scratch, single session; checked by G16)

Multiplying by X^{−k} preserves divisibility, because X and X² − μX + 2 are coprime over ℚ. So normalise the lift to minimum exponent 0. Mod 2, X² − μX + 2 ≡ X(X + 1), so a structural f has f ≡ X(X + 1)·g (mod 2).

1. **Z4: none.** All coefficients are ±1, so f(0) = ±1 is odd. But X | f mod 2 forces f(0) even. Contradiction. This is v1 A2's argument, now applied to Z4.
2. **Z3.**
   1. The terms with odd coefficients are ε_1X^b + ε_2X^c. X | f mod 2 forces b, c ≥ 1, so the doubled term sits at exponent 0: f = 2ε_0 + ε_1X^b + ε_2X^c with 1 ≤ b < c.
   2. Take absolute values at the root π, where |π| = √2: |ε_1 + ε_2π^{c−b}| = 2/2^{b/2}. With Re π = μ/2 and Re π² = −3/2, one has |1 ± π| ∈ {√2, 2}, |1 ± π²| ∈ {√2, 2√2}, and |1 ± π^k| ≥ 2^{k/2} − 1 ≥ 1.83 for k ≥ 3.
   3. Hence b = 1 and c ∈ {2, 3}. The value b = 2 would need modulus 1, which never occurs, and b ≥ 3 would need modulus at most 0.71.
   4. **c = 2.** f = ε(X² − μX + 2), the family **F1**.
   5. **c = 3.** Reduce mod X² − μX + 2: X³ ≡ −X − 2μ. Then f ≡ (ε_1 − ε_2)X + 2(ε_0 − με_2), which vanishes iff ε_1 = ε_2 and ε_0 = με_2. So f = ε(X³ + X + 2μ) = ε(X + μ)(X² − μX + 2), the family **F2**.

**Result.**
- **F1:** {w, w, [λ²]w, −μ[λ]w}, with w = ε[λ^i]u.
- **F2:** {w, w, μ[λ³]w, μ[λ]w}, with w = εμ[λ^i]u.

Both are Z3-type, with the doubled element w. For n ≥ 5 they are distinct and well defined. They agree with VAL JR3-B2's families once the relabelling of the doubled element is made.

**Count per full orbit.**
- Each family has one multiset per (i, ε): 2n multisets, which is n ±-classes.
- So **Z3_struct = 2n** ±-classes per orbit.
- Each ±-class gives 2 coincidences, so the structural N_2 is **4n** per orbit. This agrees with the 4n of VAL scratch S2 at n = 11–23.
- **Z4_struct = 0.**
- A list of k full orbits (|F| = 2nk) carries Z3_struct = |F| and structural N_2 = 2|F|, again in agreement with JR3-B2.

### 4.3 Accidental intra-orbit relations

The number of intra-orbit candidate patterns up to rotation is about n³ for Z4 and Z3 together. Each vanishes "with probability" about 1/ℓ, so the scratch expectation is about n³/ℓ per curve:
- about 6·10^-5 at n = 41;
- several per curve at n = 13, ℓ = 2003.

G16 enumerates them exhaustively, so there is no expectation to trust.

### 4.4 How the exclusion is applied here

- Version 2 excludes the families "on Koblitz lists with sigma-stable V". No σ-stable cell exists here (X5).
- On KR lists, which are F_V with non-σ-stable V and Γ = ⟨−1⟩, the **decision Z3 is raw**, as filed (B2). Every Z3 configuration on a KR list is classified, and Z3_raw, Z3_struct and Z3_excl are reported.
- A structural configuration in a KR F_V needs three π-related points with x, x², x⁴ (or x, x², x⁸) all in V. The scratch expectation is about 2^{3D−2n}, or 2^{−46} at (41, 14).
- The null F* on KR has no π-structure.
- **FALSIFIED-STRUCTURAL.** If a KR falsification is carried by structural configurations, meaning the T3 test computed on Z3_excl does not reject, the cell's outcome is labelled FALSIFIED-STRUCTURAL. It is still FALSIFIED as filed, and it routes with B2.
- The exclusion is otherwise exercised on gate lists only: full orbits and planted structural triples (G3, G16, C-PLANT).

### 4.5 Corrected v1 G3-EXCL expectation

v1 expected "one full ⟨±π⟩-orbit at n ≥ 31 gives N_2 = 0". **That was wrong.** The correct expectation for one full orbit is:
- N_2 = 4n + 6·Z4_acc + 2·Z3_acc;
- Z3_raw = 2n + Z3_acc;
- Z3_struct = 2n;
- Z3_excl = Z3_acc;
- Z4 = Z4_acc.

Here (Z4_acc, Z3_acc) is G16's exhaustive accidental count for that curve, which is 0 for n ≥ 31 unless G16 finds otherwise.

---

## 5. Curve selection (specified; executed at S0-3, not here)

The v1 procedure is unchanged except for the Koblitz rows and the calibration set.

- **Fields.** f_n is the least irreducible trinomial z^n + z^k + 1, else the lexicographically least irreducible pentanomial.
- **Ordinary roles.** O4a and O4b are the first two acceptances with A = 0; O2 is the first with A = 1. B is drawn by DRBG under the label `EXP-SEMBIN-3d9a71|curve|n|role|attempt`, and #E by BSGS. A curve is accepted iff #E = hℓ with ℓ proved prime by complete trial division.
- **Koblitz.** #E is computed by the Lucas sequence and cross-checked by BSGS. A curve is admissible iff #E/h is proved prime.
  - Every (n, a) with n ∈ {31, 37, 41, 43, 47} and a ∈ {0, 1} is tested.
  - Toy scratch (VAL JR3-B7) predicts that only (41, 0) is admissible, with ℓ = 549756390943 (scratch, unverified here).
  - KR uses (41, 0) if admitted. Any other admitted pair is reported-only (§3.2).
- **Calibration curves (never evidence).**
  - Ordinary: CAL-13 (n = 13, A = 0) and CAL-19 (n = 19, A = 1), as in v1.
  - Koblitz, new for X4: **KCAL-13** (a = 0, h = 4, scratch ℓ = 2003), **KCAL-17** (a = 1, h = 2, scratch ℓ = 65587) and **KCAL-23** (a = 0, h = 4, scratch ℓ = 2095853). These ℓ values come from `scratch_koblitz_identities_output.txt`; G8 recomputes them.

---

## 6. Sample-size derivation (scratch)

**Unit.** Primitive configurations. Per list, Z4 is approximately Poisson(μ4) and Z3 approximately Poisson(μ3) under the null. This is a sizing approximation only, since decisions are permutation-exact. Per cell, E4 = N_V·μ4 and E3 = N_V·μ3.

**Power.** The stratified permutation test of a cell total with M references per stratum detects a uniform rate ratio ρ = 1 + δ at power 0.9 when

    δ·(M/(M+1))·E ≥ (z_{α′/2} + z_{0.9})·√E,

with α′ = 10^-3/270 = 3.70·10^-6 two-sided, so z_{α′/2} = 4.63 and z_{0.9} = 1.28. That gives:
- **δ_90 = 6.89/√E** at M = 6;
- **δ_90 = 6.20/√E** at M = 20 (W);
- for comparison, v1 had 7.15/√E at M = 5 with m_max = 345.

**Per-cell results.** These are the §0 table:
- **Z4**, at E4 = 50: ρ_90 = 1.98. Higher-λ cells reach 1.77, 1.55 and 1.39. D3 reaches 1.024 to 1.068.
- **Deficit side:** ρ ≤ 1 − δ_90. That is none at E ≈ 50 except near-total absence, which the exact permutation law still detects; then ≤ 0.23, ≤ 0.45 and ≤ 0.61.
- **Z3 in D3:** ρ_90 = 1.63 at E3 = 120 and 1.89 at E3 = 60.
- **Z3 elsewhere:** E3 ≤ 2.3, so the normal approximation is void. By the exact Poisson upper tail at 3.7·10^-6, E3 ≈ 2 needs a count of at least 12, so ρ_90 ≈ 8. E3 ≈ 0.3 gives ρ_90 ≈ 30. **Gross only.**

**Arm-pooled ρ_90 (excess).**

| arm | Z4: E4 → ρ_90 | Z3: E3 → ρ_90 |
|---|---|---|
| O4 | 2460 → 1.14 | 21 → about 2.5 |
| O2 | 722 → 1.26 | 6.5 → about 3.7 |
| W | 1279 nominal → 1.17 | gross only |
| KR | 420 → 1.34 | 1.8 → gross only |
| D3 | 317440 → 1.012 | 480 → 1.31 |

The W figures are nominal, not trace-adjusted (§3.4). The realised W power is recomputed from Ê4 at S0-3 and recorded before any F_V statistic is read.

**At λ_2 = 2^-2** (cells (37, 11) and (41, 12) on O4a, O4b and KR, at h = 4):
- Each null list has P(Z4 = 0) ≈ e^{−1/24} ≈ 0.959, so N_V = 1200 is needed for E4 = 50 and ρ_90 = 1.98.
- **Can detect:**
  - a uniform excess of at least 2× per cell;
  - a near-total absence of Z4;
  - a V-subpopulation at density of at least about 1% with a large excess (MX4, KS4);
  - about 1.14 pooled over O4.
- **Cannot detect:**
  - any deficit short of near-total;
  - V-classes rarer than about 1/1200, including ker-Tr subspaces at 2^-11 to 2^-12;
  - any Z3 effect short of about 10×, since E3 = 0.6 to 1.2;
  - anything about the constant in the dense regime. Part of that is what D3 measures, at n ≤ 41 only.

**Why M = 6.** M must be even for the split-half check. The variance factor (M+1)/M = 1.17 is close to v1's 1.2. The null is cheap in Z/ℓ.

---

## 7. Controls (endorsed set, restated on Z4 and Z3)

| id | what | required reading |
|---|---|---|
| **C-NULL** | Matched null as in §3.5. N-SCALE: mean null Z4 over mean \|F\|^4/(48ℓ) in [½, 2] at every cell, and mean null Z3 over mean \|F\|^3/(4ℓ) in [½, 2] at D3 cells. This is a counter sanity band only. **SH** (split-half, §8.3), **GU** (§8.3) and PLACEBO (j = 0 run as "V" through every decision test and the pooled tests) | N-SCALE in band. SH passes per cell. GU passes. No placebo test at raw p ≤ 3.70·10^-6 |
| **C-AP** | F_AP = ±{jP : 1 ≤ j ≤ k}, k = median \|F_V\|/2, plus random dilates ±{jsP}. 30 strata per λ-grid cell, 10 per D3 cell, each with 6 matched nulls. One AP list per cell goes through the point path | T4 **and** T3 at corrected p < 10^-6 (raw ≤ 3.70·10^-9) at every admitted random-V cell. All dilates give identical (Z4, Z3), equal to an independent integer count (G5) |
| **C-GAP** | Rank-2 GAP ±{(ig1 + jg2)P}, L1·L2 = k. On KR, g2 = λg1 (a Frobenius GAP). 30 or 10 strata as for AP | T4 and T3 at corrected p < 10^-6 at every admitted random-V cell |
| **C-SID** | SID4: alteration-built lists with Z4 = 0 at λ-grid cells with λ_nom ≥ 2^2, and Z4 ≤ ⌊μ̂4/2⌋ at D3 cells (rejection refill, at most 10^4 iterations, else NOT BUILT). SID3: lists with Z3 = 0 at D3 cells | SID4: T4 lower tail at corrected p < 10^-6. SID3: T3 lower tail at corrected p < 10^-6 at each D3 cell. NOT BUILT makes PASS unavailable at that cell; it is not INVALID |
| **C-PLANT** | Null lists with k_inj ∈ {1, 2, 5, 20} injected parallelograms (Z4 += 1, N_2 += 6) and Z3 triples {s, u, −2s−u} (Z3 += 1, N_2 += 2). On KR curves also: (i) one planted F1 triple {w, [λ²]w, −μ[λ]w} with negations (Z3_raw += 1, Z3_struct += 1, Z3_excl += 0); (ii) one full ⟨±λ⟩-orbit (§4.5 expectation) | Counters equal the exact independent recount (and brute force where \|L\| ≤ 48). Increments equal the injection except for accidental extras that the recount identifies |
| **C-SENS** | 200 resampled pseudo-cells per random-V cell: one of the stratum's M+1 null values is the pseudo-V, plus Poisson((ρ−1)μ̂4) injected Z4 (N_2 += 6 each), or separately Poisson((ρ−1)μ̂3) injected Z3, at ρ ∈ {1.5, 2, 3}. Additivity is gated by C-PLANT | T4: power(ρ = 2) ≥ 0.9 per arm-pooled T4 and ≥ 0.5 at ≥ 80% of random-V cells. T3: power(ρ = 2) ≥ 0.9 pooled over D3 and ≥ 0.5 at every D3 cell. Otherwise PASS is unavailable at the stated scope |
| **C-SCALE** | Each λ-grid value at ≥ 2 n in the ordinary arms. S-TREND is the slope of log ρ̂4 on log2 ℓ per arm, with its CI | A band with fewer than 2 admitted n is INCONCLUSIVE for that band. S-TREND is reported and does not decide |
| **C-SEEDS** | Unique labels `EXP-SEMBIN-3d9a71\|<cell>\|<role>\|<i>\|<j>` with roles {curve, V, null, placebo, plant, ap, gap, sid, sens, rep1, v3}. Halves A and B are disjoint by j | G11 |

**Why no coordinate-defined nearby object.** Theorem C of KN-FIND-ffe1df, transferred to ⟨P⟩ per VAL-20261003-17b1e4, excludes any exact sum-compatible map on a prime-order group. So objects with known structure must be built by scalar multiplication, as in v1. The Frobenius GAP on KR is the curve-natural one.

---

## 8. Statistical plan (X3, X6)

### 8.1 Multiplicity (X6)

**m_max = 4 × 65 + 2 × 5 = 270, frozen now.**
- The 4 per-cell tests are T4, T3, KS4 and MX4.
- The 2 pooled tests per arm are T4 and T3, over O4, O2, W, KR and D3.

Rules:
- m_max is not reduced when cells fail admission, and not increased by reported-only cells.
- The raw per-test threshold is p ≤ 10^-3/270 = **3.70·10^-6**.
- The positive-control threshold is 10^-6/270 = 3.70·10^-9 raw.
- If D3 is declined at approval, m_max = 244 and the contract is re-drafted.

### 8.2 Decision tests (two-sample, permutation-calibrated)

Stratum i is {F_{V_i}, references j = 1..M}. Under H0, F_{V_i}'s value is exchangeable with its M references at the realised size (B9).

- **T4.** S = Σ_i Z4(F_{V_i}). The reference law is the exact convolution of one uniform pick per stratum from its M+1 values. The p-value is two-sided: p = min(1, 2·min(P(S′ ≥ S), P(S′ ≤ S))).
- **T3.** As T4, on Z3. On KR the statistic is raw Z3 (§4.4), and T3 on Z3_excl is computed and reported.
- **KS4.** The KS distance between {Z4(F_{V_i})} and the pooled references. It uses stratified Monte Carlo permutation with Besag–Clifford stopping at h = 20 exceedances and B_max = 4·10^6, so the minimum p is 2.5·10^-7. The p-value is h/b if stopped at b, else (1 + G)/(B_max + 1).
- **MX4.** max_i Z4(F_{V_i}), upper tail, permutation-calibrated as for KS4. This is the null-calibrated tail check that version 2's last sentence requires.
- **Pooled tests.** T4 and T3 over all strata of all admitted in-family cells of an arm.
- **Secondary only (never decide):**
  - a Pearson X² of each cell's Z4 against Poisson(mean null Z4);
  - the null VMR of N_2 and of Z4, pooled within strata;
  - ρ̂4 and ρ̂3 with exact 99% CIs;
  - R_2;
  - Z3_struct and Z3_excl;
  - |F_V| by trace class and the skip rate;
  - S-TREND.

### 8.3 Null calibration (replaces N-POI)

- **SH (split-half), per cell.** For each test X ∈ {T4, T3, KS4}, compare half A with half B within strata.
  - T-type tests use the exact law of the sum of a uniformly random M/2-subset of the stratum's M values, convolved over strata: C(6,3) = 20 subsets per stratum, or a DP for M = 20.
  - KS4 uses Monte Carlo with B_max = 10^6.
  - **Pass iff every SH p ≥ θ_SH = 10^-3/(3·65) = 5.13·10^-6** (frozen). A correct null therefore fails somewhere in the run with probability at most 10^-3.
  - One failing cell makes that cell INCONCLUSIVE. Two or more make the run INCONCLUSIVE.
- **GU (global uniformity).**
  - Each cell contributes a randomised one-sided upper SH-T4 p-value, with ties broken by a labelled DRBG; this p-value is exactly U(0,1) under exchangeability.
  - The same is done for the placebo T4.
  - Each set of 65 p-values gets a one-sample KS test against U(0,1). **Pass iff both p ≥ 5·10^-4** (frozen). A failure makes the run INCONCLUSIVE, because the machinery is miscalibrated.

### 8.4 Pre-registered prediction (frozen before any run)

- **H0, per cell, as filed:** Z4(F_{V_i}) and Z3(F_{V_i}) are each exchangeable with their M size-matched references (B6, B9).
- **Predicted reading:** no decision or pooled test at raw p ≤ 3.70·10^-6, and ρ̂4 ≈ ρ̂3 ≈ 1. This is what the placebo must give.
- **Source.** HEUR-HARVEST-FV-1(a) v2 (filed, internal). Its random-model justification, "sparse sums of weakly dependent indicators of probability about 1/ℓ", is `recalled` and backs nothing. Every constant comes from the null.
- **Secondary predictions** (checks, not decisions):
  1. null VMR(N_2), pooled within strata over ordinary λ-grid cells with λ_nom ≥ 2^2, in [4.5, 7.5], with the exact form (36μ4 + 4μ3)/(6μ4 + 2μ3) ≈ 6;
  2. null VMR(Z4) at the same cells in [0.8, 1.25];
  3. G16's exhaustive enumeration finds exactly the two families at every Koblitz curve (§4);
  4. on KR, Z3_struct(F_V) = 0 in every list (scratch expectation about 2^{3D−2n});
  5. AP dilation invariance;
  6. S-TREND slope 0, reported with its CI.

### 8.5 Replication of a falsification

This is pre-registered as in v1. Each falsifying cell is rerun once with fresh labels (role rep1) at the same N_V and M, on the single test that fired, at α = 10^-3 with no multiplicity. The result is **REPLICATED** if it rejects in the same direction and **UNREPLICATED** otherwise.

---

## 9. Gates (written from the statement, no shared code) and mutation self-test

**R3 compliance (DEC-20261002-7a3f19, by analogy).** Nothing reuses `experiments/EXP-SEMBIN-04ec3c/code/v2/`. Module A holds the counters and tests; module B holds the gates. They share no code, and the integer and point paths share no counting code.

The JV-2 defect classes map to gates as follows:

| JV-2 defect class | gates |
|---|---|
| off-grid / mislabel | G6, G7 |
| domain predicate | G1, G3, G16 |
| enumerator | G2 |
| shared input | G8 |
| baseline column | G7, C-NULL, G14 |

| gate | check |
|---|---|
| G0-ARITH | Modules A and B agree on 10^4 random additions per curve; [ℓ]P = O; [#E]R = O |
| G1-BRUTE | A literal O(\|L\|^4) enumeration from §3.1, using module B, on: 50 lists at each \|L\| ∈ {16, 24, 32, 48} in Z/101, Z/1009 and Z/10007; F_V at CAL-13 and CAL-19 with \|F\| ≤ 48; KCAL full-orbit lists of k ∈ {1, 2, 3} orbits; and every planted list with \|L\| ≤ 48. The counters must match N_2, Z4, Z3, Z3_struct and Z3_excl exactly |
| G2-ENUM | Σ r = C(\|L\|, 2), r(O) = \|L\|/2, r(g) = r(−g), and a caller-side partner tally. The emitted cell set equals the frozen 65-cell table read from an independent copy |
| G3-EXCL | Hand-built cases with expected values written before code: {±a, ±b} → N_2 = 0. One parallelogram → N_2 = 6, Z4 = 1. {±s, ±u, ±(2s+u)} → N_2 = 2, Z3 = 1. {±s, ±3s} → N_2 = 0, Z3 = 0. **Corrected:** one full ⟨±λ⟩-orbit → the §4.5 expectation, at KCAL-13, KCAL-17 and KCAL-23 and at the KR curve. Planted F1 triple on a ⟨−1⟩ KR list → Z3_raw = Z3_struct = 1, Z3_excl = 0, decision-Z3 increment 1 |
| G4-PATH | Integer path = point path (N_2, Z4, Z3, Z3_struct) on ≥ 5 null lists per cell, every planted list, and one AP and one GAP list per cell |
| G5-DILATION | AP dilates give identical (Z4, Z3), equal to the integer count |
| G6-MEMBERSHIP | Every element has x ∈ V, lies on E and satisfies [ℓ]Q = O (all elements at calibration curves and n = 31; a 1% sample elsewhere). F_V is negation-closed. \|F_V\| is recounted for 3 V per cell. **SKIP:** consumed V indices = tested ∪ skip log, recounted independently. KR: every V is checked non-σ-stable |
| G7-NULL | \|F*\| = \|F_{V_i}\|; orbits distinct; λ² − μλ + 2 ≡ 0 (mod ℓ) and π(P) = [λ]P on KR and KCAL; top-8-bit histogram χ² p > 10^-6 (weak sanity) |
| G8-INPUT | ℓ and #E recomputed by module B (Lucas and BSGS from two points); ℓ proved prime; f_n re-tested for irreducibility; the ECC2K-130 ℓ compared with the vendored string; KCAL ℓ recomputed |
| G9-IDENTITIES | N_2 = 6Z4 + 2Z3 with Z4 a non-negative integer, on every list. The Z3 closed form equals the Z3 enumeration count. 0 ≤ Z3_struct ≤ Z3; Z3_struct = 0 on ordinary curves |
| G10-STATS | Exact convolution equals brute force on toy strata (N_V = 3, M = 2, and an M = 6 split-half case). 1000 synthetic placebo p-values are not rejected as U(0,1) at 10^-3. Synthetic shifts reject. **Constants:** m_max = 270, θ_SH = 5.13·10^-6, GU threshold 5·10^-4, each read from an independent copy |
| G11-SEEDS | No label collision; no repeated V within or across cells; no repeated null orbit set; halves A and B disjoint; replication labels disjoint |
| G12-MUTATION | Every mutant M1–M30 makes at least one gate fail; the unmutated code passes. An uncaught mutant makes the run INVALID |
| **G13-NULLEQ** (X3) | 200 synthetic cells in which "V" and references are i.i.d. from an over-dispersed law (negative binomial, mean 20, VMR 3; N_V = 100, M = 6). The full decision machinery must reject nothing at raw 3.70·10^-6. The expected false rejections are about 0.003 |
| **G14-NULLCAL** (X3) | 200 synthetic correct-null cells with Z4 ~ Poisson and N_2 = 6Z4 + 2Z3 built from them. SH and GU must pass in ≥ 199 cells |
| **G15-STATMAP** (X2, X4) | The per-cell decision vector is recomputed by module B from the per-list records, using the frozen map: decision statistics Z4 and raw Z3 on every arm, including KR. It must equal module A's |
| **G16-INTRAORBIT** (X4) | (i) Curve-free: enumerate every Z4 pattern (four ±1 terms) and Z3 pattern (one ±2 term and two ±1 terms) with exponents in [0, 7], μ = ±1, and test divisibility by X² − μX + 2 in ℤ[X] by module B. The structural set must equal {±F1, ±F2} up to shift, and the Z4 structural set must be empty. (ii) Per Koblitz curve (KCAL-13, -17, -23 and the KR curve): enumerate all intra-orbit patterns with exponents mod n, evaluate f(λ) mod ℓ, and classify zeros as structural or accidental. The structural count must be 2n Z3 ±-classes per orbit. Accidentals are recorded. (iii) Brute force N_2 on one full orbit must equal 4n + 6Z4_acc + 2Z3_acc |

**Mutants** (at least one per defect class, including at least one each for X2, X3 and X4):

| id | class | mutant |
|---|---|---|
| M1 | exclusion logic | include the g = O class |
| M2 | exclusion logic | count {a, a} 2-sums |
| M3 | pair enumerator | skip pairs (i, i+1), or drop the last element |
| M4 | hash key | key on x(g) only |
| M5 | field arithmetic | wrong reduction polynomial in module A |
| M6 | curve special case | a + (−a) returns a non-O point |
| M7 | null size | null lists of size \|F_V\| − 2 |
| M8 | null closure | null of independent, non-negation-closed elements |
| M9 | null distribution | r drawn from [1, 2^20] |
| M10 | Z3 closed form | omit the −1{−3s ∈ L} correction |
| M11 | shared input (order) | membership tested by [#E]Q = O |
| M12 | shared input (eigenvalue) | use the other root of λ² − μλ + 2 |
| M13 | stratification | V_i paired with stratum i+1's references |
| M14 | p-value | no +1, or one-sided where two-sided is required |
| M15 | statistic (X2) | Z4 = round(N_2/6), ignoring Z3 |
| M16 | cell enumerator | drop the largest D of each curve |
| M17 | multiplicity (X6) | m_max from admitted cells, or the stale 345 |
| M18 | seed reuse | the same null lists reused across strata |
| M19 | V sampling | rank-deficient V accepted |
| M20 | window basis | windows built in a non-polynomial basis |
| M21 | decision test (X3) | decide by a Pearson goodness-of-fit of Z4 to Poisson(λ̂) |
| M22 | null calibration (X3) | validity uses the v1 N-POI Poisson heterogeneity on N_2 |
| M23 | statistic (X2) | T4 computed on N_2 instead of Z4 |
| M24 | exclusion omitted (X4) | structural classifier disabled (Z3_struct ≡ 0) |
| M25 | families counted twice (X4) | each structural configuration counted once per family orientation (4n per orbit) |
| M26 | exclusion in wrong scope (X4) | KR decision uses Z3_excl |
| M27 | unfrozen threshold (X3) | θ_SH taken from the run's own SH p-value quantile |
| M28 | skip handling (X7) | \|F_V\| = 0 dropped without a log entry, or an earlier V index reused |
| M29 | split-half overlap (X3) | halves A and B share list j = M/2 |
| M30 | class count (X2) | Z4 counts T and −T separately |

Expected catching gates:

| mutant | caught by |
|---|---|
| M21 | G13 |
| M22 | G14 |
| M23, M26 | G15 |
| M24, M25 | G3, G16 (M25 also by G9 non-negativity) |
| M27 | G10 |
| M28 | G6-SKIP |
| M29 | G11 |
| M30 | G1, G9 |
| M10 | G3 {±s, ±3s}, G1 |
| M1–M9, M11–M20 | as in v1 |

---

## 10. Outcomes (decidable from the metrics)

| outcome | condition |
|---|---|
| **INVALID** (defect, not evidence) | Any gate fails; a mutant is uncaught; N-SCALE out of band; a path mismatch; the identity fails; a size mismatch; the scratch formula used in a decision; or a frozen quantity (N_V, M, m_max, θ_SH, the GU threshold, the cell table, the arm→statistic map) changed without a versioned amendment |
| **INCONCLUSIVE** | Valid, but any of: a placebo test at raw p ≤ 3.70·10^-6; AP or GAP not flagged on T4 or T3 at some admitted random-V cell; SID4 or SID3 not flagged where required; SH failing at ≥ 2 cells (a single failure makes only that cell INCONCLUSIVE); GU failing |
| **FALSIFIED** (clause (a) v2, at the cell's scope) | Valid; controls OK; the cell's SH passed; GU passed; and any in-family decision test (T4, T3, KS4, MX4 at an admitted cell, or a pooled T4 or T3) at raw p ≤ 3.70·10^-6. The direction (excess, deficit, shape, tail), the statistic, the arm and the cell are recorded. **FALSIFIED-STRUCTURAL** applies on KR when T3 on Z3_excl does not reject (§4.4). The result is labelled REPLICATED or UNREPLICATED |
| **PASS** (at stated resolution) | Valid; controls OK; no rejection; the SENS floors of C-SENS met. Reported with ρ̂4 and ρ̂3, their 99% CIs per cell and per arm, and the scope: Z4 at the §6 resolution per cell; Z3 at resolution only at D3 cells, and gross-only elsewhere |
| **PASS-UNDERPOWERED** | Valid, no rejection, a SENS floor unmet. Reported as INCONCLUSIVE at that scope |
| **UNTESTED** | The σ-stable sub-clause (always, here); the ker-Tr structured class; a W cell with Ê4 < 1 |
| **V3** | Any Z4 ≥ 1 or Z3 ≥ 1: STOP, certify (the points re-verified independently), route; it is FALSIFIED at that cell, since the scratch λ_2 is about 2^-76 and no multiplicity is needed. Zero is recorded as consistent and confirms no rate |
| **infrastructure** | A timeout, crash or memory stop is never evidence; it checkpoints the run |

**What each outcome discriminates.**
- **E1:** the clause holds at resolution, giving PASS.
- **E2:** x ∈ V leaks additive structure, giving an excess. Evidence for this would be a ρ̂ that grows along the n-ladder at fixed λ (S-TREND).
- **E3:** repulsion, giving a deficit, resolvable only at λ_nom ≥ 2^4 and in D3.
- **E4:** an instrument artifact, caught by the placebo, SH, GU, path, gates and controls.
- **E5:** a size-only effect, where |F_V| departs from 2^D/h (trace geometry) while the matched-size rate is null. This is a secondary measurement, not a falsification.
- **E6:** a Frobenius leak on KR, giving FALSIFIED-STRUCTURAL (B2).

---

## 11. decision_it_changes and hypothesis_link (X8)

- **hypothesis_link.** Prediction **P3** of the filed `ledger/hypotheses/H-SEMBIN-c7e1d4.yaml`: "Two-sample stratified-permutation p-values of Z4 and Z3 of F_V against the closure-matched null, per cell and per arm", with P3's minimum_effect. Nothing here moves any status. That is the Coordinator's.
- **FALSIFIED.** The generic layer's **application to F_V is void for every harvester outside the conservation-law laws**, at the falsifying cell's (curve class, D, V-distribution) scope.
  - The conservation-law laws are ENUM by lookup, MITM, MITM_CAPPED and per-target golden-collision search over uniform targets.
  - Examples of affected harvesters are PCS batched harvesting and pair-sum hashing.
  - Sources: H-SEMBIN-c7e1d4 CH-2 and its TRANSFER TO F_V falsification condition; VAL-20261003-17b1e4 JR1-B2.
  - **Not touched:** the random-list statement, the unconditional first-moment transfer for the conservation-law laws, and the model layer.
  - F_V becomes an object worth attacking at that scope. An excess at fixed λ that grows along the n-ladder is the exponent-relevant signature.
  - Link: F_V is the 0-fibre of the F_2-linear filter x ↦ x mod V, so an excess is weak first evidence on **KN-OPEN-91d4f6**. It does not settle it.
  - The cell routes to the Coordinator before any interpretation.
- **PASS.** Clause (a) v2 is consistent at the stated resolution in the tested cells. The generic layer's transfer to F_V, for harvesters outside the conservation-law laws, is thereby validated at toy and medium scale for those cells, with transfer to n ≥ 97 **by assumption** (TA-1). The conditional is never discharged.
  - **Says nothing about:** the σ-stable sub-clause or the ker-Tr class (both UNTESTED), clause (b), HEUR-HARVEST-FV-2, or any higher-arity oracle.
- **INCONCLUSIVE or INVALID.** Nothing is read.

---

## 12. Scale and transfer; cost

**Scale.**
- n = 31 is `toy` and n = 37–47 is `medium`, by the mechanical rule in docs/claims-and-verification.md.
- ℓ ranges from about 2^29 to 2^46.
- V3 at n = 131 is a disclosed-weak arm with a cryptographic label.

**Transfer.**
- **TA-1 (BY ASSUMPTION).** The rate ratios ρ4(λ) and ρ3(μ3) at matched density are the same at n ≥ 97 as at n ≤ 47.
- **TA-2.** Random-V results say nothing about structured V.
- **TA-3.** D3 transfers to the m = 3 factor-base density at n ≥ 97 by assumption only.
- **Correspondence:** null. Sampling is direct; no shortcut comparable to Deuring is known.

**Cost** (scratch, unmeasured, advisory; throughput is measured at S0-4).

| arm | point additions (F_V and the G4 subset) | integer pair-sums (7 or 21 lists per stratum) |
|---|---|---|
| O4 | 5.7·10^9 | 8.0·10^10 |
| O2 | 4.3·10^9 | 6.0·10^10 |
| KR | 0.5·10^9 | 7.3·10^9 |
| W | 2.1·10^9 nominal, ≤ 5.2·10^9 if O4a windows are doubled by trace | 0.9·10^11, ≤ 2.2·10^11 |
| D3 | 7.1·10^9 | 1.0·10^11 |
| controls (AP, GAP, SID) | about 2·10^9 | about 1.7·10^11 |
| **total** | **about 2.5·10^10** | **≤ 6.4·10^11** |

- **Time.** At about 5·10^6 additions/s and 10^8 sums/s that is about 3 to 4 CPU-hours.
- **Largest cell.** D3, O2, n = 41, D = 15, at about 25 minutes.
- **Memory.** At most 2^27 64-bit keys (1 GiB) plus the sort, so peak ≤ 1.5 GiB.
- **Envelope.**
  - 7 scientific runs plus up to 7 infrastructure reruns.
  - 14,400 s watchdog per run.
  - 8 CPU-hours advisory.
  - 4 GB memory.
- Pure Python is not viable. A missing compiled kernel is an infrastructure stop, or an amendment with ρ_90 recomputed, never a silent cut.

**Runs plan.**

| run | content |
|---|---|
| RUN-A | S0: gates, G16, mutation self-test, curve selection, throughput |
| RUN-B | n = 31 and 37, all arms, including D3 |
| RUN-C | n = 41, all arms, including KR and D3 |
| RUN-D | n = 43 |
| RUN-E | n = 47 |
| RUN-F | analysis: pooled tests, SH, GU, outcomes, replication |
| RUN-G | optional V3 |

**dominated_by: "n/a (no result claimed)".** A heuristic-validation experiment claims no algorithm. The frontier rows were not re-read in this session; the v1 check list is inherited (§13). **sota_delta:** 0 on time, memory and data/queries under every outcome. A falsification removes a transfer premise and opens a routed attack question. It moves no frontier row without a separate algorithm and record.

---

## 13. Honest accounting (inventor-protocol §5) and disclosures

```yaml
honest_accounting:
  objects_considered:
    - "Z4(F_V), Z3(F_V): +-class counts of zero-sum 4-sets and of degenerate zero-sum multisets {s,s,u,v} in the 0-fibre F_V of x -> x mod V"
    - "the closure-matched, realised-size random list F* (integer path) as the null object"
    - "the intra-orbit configuration polynomials f in Z[X] on Koblitz curves, classified by divisibility by X^2 - mu X + 2 (section 4)"
  lossy_projection_test: >-
    Not applicable as an object proposal: this is a measurement of a
    distributional premise. For the record, (Z4, Z3) is invariant under Gamma
    and under the dilation action of (Z/l)^*. It is a lossy projection of the
    list that propagates under no group operation. KN-FIND-ffe1df Theorem C
    (transferred per VAL-20261003-17b1e4) excludes an exact sum-compatible
    projection, so the statistic measures only an approximate residue in one
    fibre.
  depth_of_verified_structure: >-
    Derivation grade, single session, unreviewed: the two-family
    classification with no Z4 family (section 4.2), the 2n / 4n count, and all
    sizing arithmetic. Inherited: N_2 = 6 Z4 + 2 Z3 (DESIGN v1 A1; VAL scratch
    C1, not independent). The JR3-B2 toy count 4n at n <= 23 agrees with
    section 4.2 but was not re-run here. Every item is checked by a gate
    before any reading.
  dominated_by: "n/a (no result claimed)"
  dominated_by_check: >-
    No algorithm or bound is claimed. This session read H-SEMBIN-c7e1d4's
    dominated_by and RT-20261003-24c995's baseline_comparison, and did one web
    search for prior art on additive structure of x-restricted point sets
    (section 13, prior art). The v1 design's check (KN-FIND-ffe1df, the 24
    KR-RHO claim lines, KR-IC-73db3f, -889857, -b0fcda, KN-FIND-007 lines
    1-80) is inherited and was NOT repeated here.
  sota_delta: "0 on time, memory and data/queries; measurement-design contribution only"
  enumerated_closures:
    - closure: none
      note: >-
        Nothing is closed. A PASS is a scoped validation at resolution rho_90.
        The sigma-stable sub-clause and the ker-Tr class remain UNTESTED and
        open.
  open_directions:
    - "A sigma-stable Koblitz design: choose n with an admissible Koblitz curve and a sigma-stable dimension near (n+9)/4 (v1 A11); needs B3 resolved first"
    - "A ker-Tr structured-V cell on h = 4 curves (B8), where |F_V| is doubled and the trace geometry is exact"
    - "D3 extended to n >= 43 with a sharded or external-memory counter (|F| ~ 2^15, 2^29 keys)"
    - "Clause (b) (V2) and HEUR-HARVEST-FV-2 (V4) designs, after this contract returns"
    - "Rigorous half: an energy bound for {Q : x(Q) in V} over F_{2^n} at |F| ~ l^{1/4} to l^{1/3}; Ahmadi-Shparlinski-type bounds are nontrivial only at much higher density (prior art below)"
```

**Prior art (design novelty: `unverified`).**
- Ahmadi–Shparlinski, "On the Sum-Product Problem on Elliptic Curves" (arXiv 0806.0640; retrieved at ar5iv this session, abstract and theorem statements only). It bounds sets of the form {x(aP) + x(bP)} and {x(abP)} over F_q. The bounds are nontrivial only for #A ≥ T^{1/2}q^{7/16}, far above |F| ≈ ℓ^{1/4} to ℓ^{1/3}. **Adjacent**, and not applicable at this density.
- "Additive Rigidity for x-Coordinates of Rational Points on Elliptic Curves" (arXiv 2510.03828) and "Additive Rigidity for Images of Rational Points on Abelian Varieties" (arXiv 2603.24340). Titles and search snippets only; not opened. They concern rational points over number fields and the field-additive energy of x-coordinates. **New relative, unrelated sense.**
- No source stating a group-law energy bound for {Q : x(Q) ∈ V} over F_{2^n} was found. Absence of a hit is not evidence of absence.

**Disclosures.**
- **PD-1 (material). Dispatched before its preconditions.**
  - DP-1: the TASK-20261003-6d2f84 receipt does not exist, so H-SEMBIN-c7e1d4 and this card are not committed on main.
  - DP-2: the TASK-20261002-5f0b2c receipt does not exist, so the version-1 bytes read here are not fixed.
  - DP-3: no lane was claimed by this session, which had no shell.
  - The TASK-20261002-c13d8e snapshot has not run.
  - The user requested this run now. These are disclosed, not waived.
- **PD-2 (material). No shell.**
  - sha256 of the hypothesis file was not computed, so X1's binding is owed.
  - `allocate_id.py --check EXP-SEMBIN-3d9a71`, `git grep 3d9a71`, `validate_ledger.py` and the branch/commit identity were not run or verified. The environment reported no git repository.
  - Grep found `3d9a71` only in ledger/handoffs/TASK-20261003-e7058d.yaml, ledger/handoffs/TASK-20261003-7a4c19.yaml, ledger/hypotheses/H-SEMBIN-c7e1d4.yaml, ledger/decisions/DEC-20261003-4e91b7.yaml and knowledge/open-problems/KN-OPEN-91d4f6.md, all of which name this experiment, and not in experiments/. A repository-wide grep timed out, so coordination/ and inputs/ were not fully content-searched.
- **PD-3. Scope additions an approver may decline.** These are the D3 band (6 cells, +26 tests), KR's frozen single-curve family with reported-only extras, M = 6 in place of 5, and FALSIFIED-STRUCTURAL as a label. Each is justified above. Declining D3 means a re-draft with m_max = 244.
- **PD-4. Scratch inputs.** The Koblitz admissibility pattern, the KCAL ℓ values and the n = 41 ℓ come from VAL-20261003-17b1e4 scratch output, not from this session. G8 and S0-3 recompute them. The trinomial trace pattern in §3.4 is recalled and unverified.
- **PD-5. kb MCP.** It was not in the tool surface; Grep and Glob were used.
- **PD-6. Write scope.** Only `coordination/tasks/TASK-20261003-e7058d/` was written. No knowledge/literature note was written; the card's scope governs.

**Read in full or in the relevant part:**
- the card;
- agents/idea-generator.md;
- H-SEMBIN-c7e1d4.yaml (full);
- DEC-20261003-4e91b7 (full);
- CORR-20261003-b35a0c (full);
- the v1 DESIGN.md and specification.yaml (full);
- VAL-20261003-17b1e4 (full);
- scratch_koblitz_identities_output.txt (full);
- RT-20261003-24c995 (lines 420–569, including O8 and O9);
- DEC-20261002-7a3f19 (R3 and R11);
- .claude/skills/design-experiment/SKILL.md;
- templates/research-records.md (Experiment section);
- docs/inventor-protocol.md (§§3–7);
- docs/claims-and-verification.md (scale tiers, by grep);
- KN-FIND-ffe1df (frontmatter and Theorem C lines, by grep);
- TASK-20261003-7a4c19.
