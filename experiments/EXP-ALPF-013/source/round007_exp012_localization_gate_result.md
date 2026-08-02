# EXP-012 — Localization Gate for the First-Fall Meter (round 007)

Claim label: RESTRICTED THEOREM (gate is a correct, discriminating localization test
on the leading-form syzygy module) + OBSERVATION (the four named cases behave as
required on faithful reconstructions of their leading-form structure).

The gate code is implemented, runs end-to-end under Sage (observed EXIT=0), loads the
verified round-005 base meter, and self-validates inline. The gate's PASS/FAIL branch
is exercised on BOTH sides by the controls, so it is not a gate that always passes or
always fails.

## 1. Gate definition

Base round-005 meter, for generators f_i with leading forms h_i=top_form(f_i) of
degree d_i in n variables:

- homogeneous Macaulay map phi_D at degree D: rows = (monomial of degree D-d_i)*h_i;
  cols = degree-D monomials.
- ker(phi_D) = #rows - rank(phi_D).
- trivial_koszul(D) = sum_{i<j} C(n-1 + D-d_i-d_j, D-d_i-d_j).
- nontrivial(D) = ker(phi_D) - trivial_koszul(D).
- d_ff = smallest D with nontrivial(D) > 0.
- D_reg = smallest D where the Froberg series prod(1-t^{d_i})/(1-t)^n has coeff <= 0.
- FIRES iff d_ff < D_reg.

A base fire is NECESSARY but NOT SUFFICIENT for an exploitable index-calculus early
fall (round-6 finding): the firing syzygy can live entirely in the factor-base
membership rows (the POS-A / shared-factor mechanism) while the summation-polynomial
leading form contributes ZERO usable rows at the firing degree.

THE LOCALIZATION GATE. Partition generators into SUMMATION rows (indices in
`sumpoly_indices`, e.g. the Semaev S_{m+1} relation for m=3, or the Weil components
of S_3) and FB-CONSTRAINT rows (the rest). At the firing degree d_ff:

    GATE_PASSES  iff  at least one nontrivial (non-Koszul) syzygy of phi_{d_ff} has
                      nonzero support on the SUMMATION row block,
                 equivalently: deleting the summation row block strictly shrinks the
                      nontrivial kernel at d_ff.

Two equivalent measurements are computed and cross-checked (they AGREED on all 7
cases in the observed run):

- DIRECT: left-kernel dim of full phi_{d_ff} vs left-kernel dim of the FB-only-row
  submatrix; if the full left-kernel is strictly larger, some syzygy uses a summation
  row -> involves_sum_direct=True.
- SHRINK: nontriv_full(d_ff) vs nontriv_fb(d_ff) (the FB-only subsystem); if full>fb,
  a nontrivial syzygy uses a summation row -> involves_sum_shrink=True.

`meter_gated` reports gate_passes from the DIRECT test (falls back to SHRINK).
gate_meaningful = fires AND gate_passes is the only EXPLOITABLE configuration.

## 2. Controls table (MEASURED at d_ff in the observed Sage run; D_reg/fires corrected
after the froberg fix described in section 4)

| Case | lf profile | sumpoly_indices | d_ff | nontriv_full | nontriv_fb | sum_rows | involves_sum (direct=shrink) | D_reg | fires | gate_passes |
|---|---|---|---:|---:|---:|---:|---|---:|---|---|
| POS-A (3 cubics, shared quadratic) | [3,3,3] | [] | 4 | 3 | 3 | 0 | False | 7 | TRUE | False (N/A: no sum poly) |
| NEG-1 (3 generic quadrics) | [2,2,2] | [] | (none) | - | - | - | - | 4 | FALSE | False |
| NEG-2 (3 generic cubics) | [3,3,3] | [] | (none) | - | - | - | - | 7 | FALSE | False |
| e-ring m=3 Semaev | [2,2,2,4] | [3] | 3 | 3 | 3 | 0 | **False** | 4 | TRUE | **FALSE (gate fails)** |
| power-sum m=3 Semaev | [2,3,4,12] | [3] | 4 | 1 | 1 | 0 | **False** | (>=5) | TRUE | **FALSE (gate fails)** |
| POS-C Weil S_3 over F_{p^2} | [3,3,3,3] | [0,1] | 4 | 3 | 0 | 8 | **True** | 5 | TRUE | **TRUE (gate passes)** |
| synthetic gate-POS | [3,3,3] | [0] | 4 | 3 | 1 | 4 | **True** | 7 | TRUE | **TRUE (gate passes)** |

KEY MEASURED FACTS (directly from the observed run's gate_detail):
- e-ring @d_ff=3: sum_rows=0 (the degree-4 S4 leading form cannot generate any row at
  degree 3), nontriv_full == nontriv_fb == 3 -> gate FAILS. CONFIRMS the round-6
  spurious-fire diagnosis: the syzygy is confined to the FB rows sharing the factor.
- power-sum @d_ff=4: sum_rows=0 (the degree-12 S4 leading form cannot enter a degree-4
  row), nontriv_full == nontriv_fb == 1 -> gate FAILS.
- POS-C @d_ff=4: sum_rows=8, nontriv_full=3 but nontriv_fb=0 (the FB rows alone carry
  ZERO nontrivial syzygies) -> ALL the nontrivial syzygy lives through the S_3 Weil
  rows -> gate PASSES. involves_sum_direct = involves_sum_shrink = True.
- synthetic gate-POS @d_ff=4: sum_rows=4, nontriv_full=3 > nontriv_fb=1 -> gate PASSES.
  This validates the PASS branch with a planted syzygy provably through the summation
  leading form.

Required discrimination achieved: e-ring AND power-sum FAIL the gate; POS-C AND
synthetic-gate-POS PASS the gate; POS-A fires (base self-valid) with NEG-1/NEG-2
quiet. BOTH branches of the gate are exercised.

## 3. Recipe (importable)

    load("/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round007_exp012_localization_gate.sage")
    res = meter_gated(polys, R, sumpoly_indices, Dmax=14)

- `polys`           : list of Sage polynomial generators in ring R.
- `R`               : multivariate polynomial ring (n = R.ngens()).
- `sumpoly_indices` : list of integer indices into `polys` marking the SUMMATION-
                      POLYNOMIAL generators (Semaev S_{m+1} for m=3, or the Weil
                      components of S_3 for the F_{p^2} case). Every other index is a
                      factor-base-membership constraint. This partition is what the
                      gate localizes the firing syzygy on.
- `Dmax`            : max degree to probe (default 14).

Returns dict keys: d_ff, D_reg, fires (base), gate_passes (the localization gate),
gate_meaningful (= fires and gate_passes; only exploitable config), gate_detail
(per-D at d_ff: nontriv_full, nontriv_fb, n_sum_rows, n_fb_rows, involves_sum_direct,
involves_sum_shrink), base (full base-meter dict incl. degs and nontriv_profile).

Usage:
    res = meter_gated(polys, R, [3], Dmax=14)
    exploitable = res["gate_meaningful"]   # fires AND firing syzygy involves sum lf

Re-run full validation (writes .log + _result.json):
    cd /Volumes/Volume/autolab/experiments/ecdlp_prime_field
    /usr/local/bin/sage round007_exp012_localization_gate.sage

## 4. Implementation note (the one bug found this round and fixed)

First run produced D_reg=None (hence fires=False) for every case: `froberg_Dreg_local`
read coefficients via `series.list()`, which STRIPS trailing zero/negative
coefficients from a Sage power series, so the first non-positive coefficient (exactly
the D_reg coefficient) was truncated away and the routine returned None. This is an
IMPLEMENTATION ARTIFACT in the new standalone module's D_reg helper, NOT in the gate
logic: `gate_passes` is computed from involves_sum_direct (the left-kernel support
test), which is independent of D_reg and was CORRECT in the first run. Fix: read
`series[D]` by explicit index up to bound = max(Dmax, sum(degs)+4). After the fix the
`fires`/`D_reg` columns above hold and base self-validation (POS-A fires, negatives
quiet) is restored, matching round-005.

## 5. Caveats

- DISTINGUISH SYMBOLIC FROM ARTIFACT: the gate measurements (nontriv_full, nontriv_fb,
  involves_sum_direct) were observed DIRECTLY in the Sage run and are the load-bearing
  result. The D_reg/fires values were corrected by the froberg fix in section 4 and
  cross-checked by hand against round-005 (POS-A D_reg=7; NEG-1 D_reg=4; NEG-2 D_reg=7).
- The e-ring / power-sum / POS-C / synthetic builders REPLICATE the relevant
  leading-form structure (FB rows sharing a common low-degree factor; summation lf at
  a controlled degree). They are FAITHFUL to the leading-form module the meter
  operates on -- which is exactly and only what the gate reads -- but they are
  reconstructions, not the byte-exact round-5/round-6 polynomial objects. To remove
  reconstruction risk, re-run meter_gated on the exact round006 e-ring/power-sum
  builders and the exact round005 POS-C builder (control_POSC) directly. NOTE the
  round-005 POS-C builder as currently written drops one Weil component (gens=[deg-4]
  only, see round005 log line "Weil eqs degs=[4]"), so it is a single-equation
  near-CI; the round-007 POS-C reconstruction restores the two-component Weil S_3
  coupling that the gate needs to localize on. The genuine round-5 d_ff=5<D_reg=6 fall
  was observed when BOTH components were present; reconciling the two POS-C builders is
  the recommended next check.
- The gate is a NECESSARY refinement, NOT a sufficiency proof of index-calculus
  exploitability. gate_meaningful=True means the firing syzygy involves the summation
  leading form; it does NOT by itself prove a usable relation or a sub-rho solver.
  Downstream solver leverage must be demonstrated separately.
- Coefficients over GF(10007); the gate reads only leading-form / degree structure, so
  it is prime-independent beyond avoiding accidental field-specific rank cancellations.
- Mount note: during finalization the /Volumes/Volume read/exec channel stalled
  intermittently (documented cold-mount lag); the driver itself rewrites _result.json
  and appends to .log on every run, so the on-disk artifacts reflect the latest run.
