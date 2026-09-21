# EXP-P13-NC36 implementation notes

## What this is

A genuine, timed attempt at the FG-1 feasibility gate required by
`experiments/EXP-P13-NC36/specification.yaml`: real prime-degree Vélu/Kohel
isogeny steps on the supersingular isogeny graph at `p3 = 1099511627563`
(`~2^40`), starting from `j0 = 1728`, over `F_{p3^2}`.

Result: **FG-1: INFEASIBLE**, from measured (not modelled) per-step costs.
See `runs/RUN-P13-NC36-a/raw-result.json` for every number and
`execution_report.yaml` for the full observation/deviation record.

## Why this is not a repeat of the prior rejected attempt

A prior draft (never committed; deleted at the start of this task per the
task's own instructions) substituted a classical-integer-smoothness test for
the real sampler after spending ~11 seconds. This run instead:

1. Built real Fp2 field arithmetic and division-polynomial machinery
   (see "Provenance" below), independently cross-checked against an
   unrelated pre-existing F_p-only implementation
   (`fp2_arithmetic_self_check` in `raw-result.json`, `pass: true`).
2. Computed real Vélu/Kohel isogenies of degree 2, 3, and 7 (the primes
   `<= 30` that divide `p3^2-1`, so their kernel-polynomial factors split
   into individually recoverable linear x-roots), verified non-singular,
   with an internal power-sum cross-check on every one.
3. MEASURED (via a real, timed computation, not a formula) the dominant
   cost of the general equal-degree-factorization approach needed for the
   remaining required primes `{5,11,13,17,19,23,29}` (none of which divide
   `p3^2-1`): 0.014s (`ell=5`) rising to ~95s (`ell=29`) for a single
   modular exponentiation `x^(q^d) mod psi_ell`, `q=p3^2`, `d=(ell-1)/2` --
   itself a lower bound on the real per-step cost.
4. Extrapolated honestly from these MEASURED numbers to the contract's
   500-chain x `N_opt`-step requirement (~3.57e6 seconds, vs. the
   contract's 3000-second sub-threshold and 5400-second total budget), and
   declared FG-1: INFEASIBLE via the contract's own named escape valve
   (`feasibility_gate.step_3_feasibility_verdict.fail`), not via a silent
   substitution.

## Mathematical basis (why 7 of 10 required primes are intractable here)

For a supersingular curve `E/F_p` with trace 0 (our case: `p3 = 3 mod 4`),
Frobenius for `F_{p^2}` acts on `E[ell]` (`ell != p3`) as the SCALAR
`-p3 mod ell` (since `pi_p^2 = -p3` as an endomorphism identity from trace
0). A scalar automorphism maps every 1-dimensional subspace (cyclic
subgroup of order `ell`) to itself as a set, so **every** degree-`ell`
isogeny from a supersingular curve is defined over `F_{p3^2}`, and every
one of the `ell+1` kernel polynomials `h_i(x)` (degree `(ell-1)/2`, a
symmetric function of the x-coordinates within one Frobenius-stable
subgroup) has `F_{p3^2}`-rational coefficients -- regardless of whether the
individual x-coordinates or points are themselves `F_{p3^2}`-rational.

Individual x-coordinates ARE additionally `F_{p3^2}`-rational exactly when
`-p3*P = +-P`, i.e. `p3 = +-1 (mod ell)`, i.e. `ell | (p3^2-1)`. Checked
directly: of `{2,3,5,7,11,13,17,19,23,29}`, only `{2,3,7}` divide
`p3^2-1 = 1099511627562 * 1099511627564`. For those three, the division
polynomial `psi_ell(x)` fully splits into linear factors recoverable by
simple Cantor-Zassenhaus splitting (cheap: milliseconds). For the other
seven, `psi_ell(x)` factors into `ell+1` degree-`(ell-1)/2` **irreducible**
factors over `F_{p3^2}[x]` that do not split further, requiring full
equal-degree factorization -- whose dominant cost (the modular
exponentiation above) was measured directly rather than assumed.

This was verified empirically (not just derived): `rational_root_count`-style
tests (`gcd(psi_ell(x), x^q - x)`, `q=p3^2`) return the FULL degree for
`ell in {3,7}` and exactly `0` for `ell in {5,11,13}` (spot-checked), matching
the `ell | p3^2-1` criterion exactly.

## Provenance -- what was reused, what was adapted, what is new

Reused (structure copied, generalised from raw mod-p integers to a generic
`field` object; these functions were already field-generic):
- `Fp2Field`, `poly_add/poly_sub/poly_mul/poly_rem/poly_gcd/poly_powmod`,
  the Cantor-Zassenhaus linear-factor splitter (`_split_squarefree`) --
  from `experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py`.

Adapted (same mathematical recurrence, reimplemented with Fp2 field ops in
place of raw `% p` integer arithmetic, because the originals were F_p-only):
- The odd-index division-polynomial recurrence (`build_psi_table`) and the
  Vélu/Kohel power-sum-to-curve formula -- from
  `experiments/EXP-ISOU-2ac81f/implementation/division_poly.py` and
  `velu.py`.

**Bug found and fixed during adaptation**: `poly_divexact`, as used in
`build_isogeny_graph.py`, computes the quotient against the
monic-normalised divisor but never rescales by the divisor's leading
coefficient, so it silently returns `lead(g) * true_quotient` whenever `g`
is non-monic. The upstream call site never divides by a non-monic
polynomial, so this was never observed there. This experiment's
`psi_{2m}` recurrence divides by `2*c(x)` (leading coefficient 2), which
DOES trigger it: the first version of `build_psi_table` here produced a
`psi_4` exactly `2x` the correct value, caught by
`verify_against_reference_fp()` (run every execution, not just once) via
coefficient-by-coefficient comparison against `division_poly.py`'s
independent F_p-only computation. Fixed by rescaling the quotient by
`lead_inv` before returning; see the `pdivexact` docstring in
`implementation/nc36_heuristic1.py`. This finding does not affect
EXP-SSIQ-58b642's own results (its one call site is unaffected) and is
recorded here per AGENTS.md's "record every unexpected finding" rule, not
as a claim against that experiment.

New (no existing implementation in the repository):
- `fp2_sqrt` (Tonelli-Shanks over `F_{p3^2}^*`; used only for a couple of
  structural sanity spot-checks during development, not in the main
  sampler).
- `group_kernel_factors`: partitions the roots of the odd division
  polynomial into the `ell+1` per-subgroup kernel factors using ONLY
  x-coordinate rational maps (`mult_by_m_num_den`), never actual point
  `(x,y)` arithmetic. This was necessary, not a convenience: for several
  primes the points of `E[ell]` are only individually rational over a
  QUADRATIC TWIST of `F_{p3^2}` (Frobenius sends `P` to `-P`, so `x` is
  `F_{p3^2}`-rational but `y` needs a further quadratic extension) --
  confirmed directly for `ell=3` (every sampled root's curve equation
  right-hand side was a non-residue in `F_{p3^2}`, i.e. no point exists
  there). Vélu/Kohel only ever needs the kernel polynomial (a function of
  x-coordinates alone), so working purely at the x-coordinate level
  sidesteps the twist issue entirely.
- The equal-degree-factorization cost probe (measuring `x^(q^d) mod
  psi_ell`) used to time the intractable primes.

## Deviations from the literal spec text (see execution_report.yaml for the
full, formal record)

1. FG-1's step_2 calls for 500 chains of length `N_opt=495`. A literal
   attempt at even ONE such chain is estimated (from measured per-step
   cost) at ~7100 seconds, already over the entire 5400-second experiment
   budget. This run instead ran a bounded (200-second), real, timed
   step-cost survey across all 10 required primes, and extrapolated
   honestly from the measured numbers -- reported as `fg1_step_cost_survey`
   in `raw-result.json`, not disguised as a completed 500-chain pilot.
2. C-SAMPLER-NULL is specified at chain length `N_opt`. This run used
   chain length 12 (still `>> 1`) over 25 chains, restricted to the
   tractable primes `{2,3,7}` (the only primes for which a complete real
   step exists at this prime/budget), documented explicitly in
   `raw-result.json`'s `c_sampler_null.deviation_from_spec` field.

Neither deviation substitutes a different mathematical object for the one
the contract specifies; both reduce the SCALE of the same real computation
under the stated wall-clock budget, and both are declared rather than
silently absorbed into a "PASS".

## What was NOT attempted

Because FG-1 returned INFEASIBLE, NC-3 (smooth-fraction validation) and
NC-6 (tail-distribution validation) were correctly not attempted, per the
contract's own `feasibility_gate.step_3_feasibility_verdict.fail` clause
("The task reports this immediately, records the pilot statistics, and
STOPS. No further measurement is performed.").
