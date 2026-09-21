# EXP-MONO-e102a3 implementation notes

## What this is

Second-object replication of EXP-MONO-bb6fa1's own m=4 residual-cubic
Galois-group measurement, at the same prime p=101, on a genuinely
different curve and point, with Stage 1's tolerance model corrected per
`ledger/corrections/CORR-20260904-8cc20f.yaml`.

## Adaptation from EXP-MONO-bb6fa1's own script

`implementation/run_galois_cubic_census_v2.py` is a direct adaptation of
`experiments/EXP-MONO-bb6fa1/implementation/run_galois_cubic_census.py`.
The following functions are copied UNMODIFIED IN LOGIC (byte-identical
except for a shared docstring trim): `j_invariant`, `curve_order`,
`pt_add`, `pt_neg`, `pt_mul`, `point_order`, `find_points`,
`classify_cubic`, `load_symmetric_terms`, `specialize_at_T0`,
`find_VR_points`, `stage0_VR_census`, `stage_r8`. These reuse
EXP-MONO-815525's own already-proven exact symmetric descent
(`s4_symmetric_coeffs.json`) and R8 monomial table (`s3_monomials.json`)
read-only, unmodified (identical sha256 to EXP-MONO-bb6fa1's own run --
see manifest.yaml `reused_frozen_artifacts`).

Two things differ, exactly per the task card and frozen specification:

1. **Curve/point selection continues the SAME scan past the first hit.**
   `find_admissible_curve(p, log, skip_first_hit=True)` runs the
   identical ascending (A,B) scan (A outer 0..100, B inner 0..100; first
   nonsingular discriminant, j not in {0,1728}, ordinary trace mod p != 0
   curve taken at each step). To guarantee this is genuinely the SAME
   declared scan continued (not a new rule that happens to look similar),
   the script first re-derives the scan's own first hit and asserts it
   equals EXP-MONO-bb6fa1's own recorded (A=1,B=1) exactly -- if it did
   not, the run would stop with `specification_error` before touching
   anything else. Having confirmed that, the scan continues from where
   the first hit was found and takes the very next admissible pair. Both
   the re-derived first hit and the new second hit are recorded in
   `raw-result.json`'s `curve_selection` block, along with the exact
   count of additional pairs examined (1 -- the very next candidate,
   (A,B)=(1,2), was already admissible).

2. **Stage 1's tolerance model is corrected.** `stage1_controls_corrected`
   replaces `stage1_controls`'s asymptotic-plus-3-standard-error gate
   with exact `fractions.Fraction` equality against the exact closed-form
   finite-p triples named in `CORR-20260904-8cc20f` and the frozen
   specification: `((p-2)/(3p), 0, 2(p+1)/(3p))` for the synthetic A_3
   object and `((p-2)/(6p), 1/2, (p+1)/(3p))` for the unconstrained
   object. Both control objects are exhaustive deterministic censuses of
   the entire finite population of monic cubics over F_101 (not
   statistical samples), so their observed densities are compared to the
   exact closed forms as exact fractions with zero tolerance, not
   floating point "close enough."

A third, additive-only change: a new "KEY CHECK" block computes the new
object's own R3 as an exact `Fraction` and compares it, by exact
`Fraction` equality, to `Fraction(17, 101)`.

## Curve/point found

- Re-derived first hit (confirms identical scan order): A=1, B=1
  (E: y^2=x^3+x+1), j=34, #E=105, trace=-3, 103 (A,B) pairs examined to
  reach it -- matches EXP-MONO-bb6fa1's own recorded values exactly.
- Continuing the scan: 1 additional pair examined; the very next
  admissible pair, (A,B)=(1,2), is the new curve: E': y^2=x^3+x+2 over
  F_101, j=4, #E'(F_101)=100, trace=2.
- Generator G' = (6,27), true order verified = 100 (== #E'(F_101)).
- R' = k*G' with k=2 (the same rule): R'=(53,82), TRUE order (computed by
  factoring, not assumed) = 50 (> 2, so R' is not in E'[2]).
- T0 = x(R') = 53.

## Results summary

- Stage R8 (m=3 baseline): PASS on 30 sample (x1,T0) pairs.
- Stage 1 (corrected exact tolerance): BOTH controls match their exact
  closed-form triples EXACTLY (synthetic A_3: (33/101, 0, 68/101);
  unconstrained: (33/202, 1/2, 34/101)) -- unlike EXP-MONO-bb6fa1's own
  run, which stopped here under the flawed asymptotic gate. Here Stage 0
  is interpreted.
- Stage 0 (V_R' census): |V_R'(F_101)| = 10200 (Lang-Weil expectation
  p^2=10201, within envelope). Non-degenerate: 10005, degenerate: 195,
  anomaly: 0.
  - R1 (disc-square rate) = 57/115 ~= 0.49565
  - R2 (1+2 density) = 58/115 ~= 0.50435
  - R3 (split density) = 1523/10005 ~= 0.15222
  - irreducible density = 3436/10005 ~= 0.34343
  - Interpretation: all three of R1, R2, R3 are within 3 standard errors
    of the asymptotic S_3 triple (0.5, 0.5, 1/6) and R1 != 1.0, so
    `outcome_I_s3_confirmed` (excludes trivial/C2/A3, consistent with
    S_3) per the identical criterion EXP-MONO-bb6fa1's own script uses.
- **Key check: R3 = 1523/10005, which does NOT equal 17/101 exactly**
  (verified by exact `Fraction` inequality). The striking exact match
  observed on the first object does not reproduce on this second object.

## Independent construction cross-checks (not part of this run)

None re-performed in this session: this run reuses EXP-MONO-bb6fa1's own
enumeration/classifier construction verbatim, which was already
cross-checked (500 random triples against `qe_from_sym`, and a
brute-force zero-set match) before EXP-MONO-bb6fa1's own recorded run.
No new construction was introduced here that would require a fresh
cross-check, beyond the curve-scan self-consistency check (re-deriving
the first hit and asserting it matches) described above, which IS
performed inside this run and gates execution.

## Protocol deviations

See `runs/RUN-MONO-e102a3-1/manifest.yaml`'s `protocol_deviations` field
for the complete, authoritative list. Summary: none in enumeration
method or curve/point-selection rule; the two intended, disclosed changes
(scan continuation, corrected Stage-1 tolerance) were applied exactly as
specified; no git commands were run per the dispatching instruction.
