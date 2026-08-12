# Implementation notes -- EXP-JINV-bd141d

## Code

New driver, per `source_constraints` (`harness/exp_icinv.py` not touched):

- `harness/exp_jinv_matched.py` -- family re-derivation, Hurwitz-Kronecker
  completeness certification, per-curve order/support certification, |Aut|
  arm structural enumeration, T1 transport attempt, r-structural argument.
- `harness/run_jinv_matched.py` -- run wrapper calling the above and
  `harness.runner.write_run`.

Both files are new (`status: untracked` in the run manifest's
`code.source.files`, pinned by sha256; `all_pinned: true`).

## What was executed, in stopping-rule order

1. **SR1 family gate.** `derive_family(19507)` re-derives the whole
   N = 19507 family from the identity `D = t^2 - 4p = (t-2)^2 - 4N` with
   `p = N + t - 1` prime and the class ordinary. Result: 59 classes, 51 at
   f = 1, 46 distinct |D_0|, 5 hit twice (30067, 42307, 72403, 75427,
   76003), |D_0| range [1299, 78027], conductor arm [1, 3, 107] -- an EXACT
   match to `inputs.family_construction.expected_inventory_from_design_document`.
   The t = 211, p = 19717, D = -34347 = -3*107^2 aut-arm class is present
   with the exact declared (p, D). **Gate: PASS.**
2. **Hurwitz-Kronecker completeness certificate, per class (SR1 control
   C-FAMILY).** For every one of the 59 classes, `isogeny_class.class_census`
   was run against the FULL enumeration at that class's p (not just the
   curves of the target trace), and the weighted observed count agreed with
   H(4p - t^2) for all 59. **All agree.**
3. **SR2 support gate + per-curve order verification, over the WHOLE
   family (all 2,212 curves across all 59 classes, not only the 51 f = 1
   classes measured by Arm 1).** For every curve: (a) an INDEPENDENT point
   enumeration (`exp_icinv_fullgroup.enumerate_points_table`, a square-root
   table method that shares no code with `toycurve.lift_x`) gave the exact
   point count, compared against the character-sum trace already carried by
   `CurveRecord.order` -- both agree with N = 19507 on every curve; (b) since
   N = 19507 is PRIME, Lagrange's theorem forces every non-identity point to
   generate the whole group, so the cyclic table built from any one point IS
   `targets_B`'s support (n1 = 1 degenerates `[u]P + [v]G2` to `[v]G2` over
   the whole group) -- this was certified per curve by EXPLICIT
   CONSTRUCTION (build the table, compare as a set against the independently
   enumerated point set), not asserted from the parity argument alone.
   **All 2,212 curves pass both checks.** Runtime: 289.2s wall / 288.2s CPU
   for this stage (well inside the 21,600s per-run and 48 CPU-hour budgets).
4. **r-stratification structural finding.** N = 19507 is odd (in fact
   prime), so `E(F_p)[2]` is trivial for every curve of order N: no curve in
   the family can have a rational 2-torsion point, so `r = 0` identically.
   Verified per curve (not just argued): the independently enumerated point
   set was checked for `(x, 0)` points on all 2,212 curves. **r = {0}
   observed, no other value.** This means the contract's r in {0, 1, 3}
   stratification collapses to a single populated stratum for this entire
   family -- pooled and "stratified" figures are identical by construction,
   which is a genuine deviation from the contract's assumed three-stratum
   design, reported here rather than silently absorbed.
5. **|Aut| arm structural enumeration.** Within the t = 211 class, curves
   were split by `j == 0` (crater, `aut_order == 6`) vs. everything else
   (floor, `aut_order == 2`) -- fields already computed by
   `isogeny_class.enumerate_curves`, NOT `two_torsion_x_count` or
   `ell_subgroup_count(., 2)` (both explicitly prohibited by the contract's
   `invalidation_rules` as crater/level proxies). Result: 1 crater + 36
   floor = 37 vertices, matching `1 + h(-3*107^2) = 1 + 36 = 37` exactly.
   This is DATA (a structural fact from the enumeration), not a verdict --
   no rank or permutation probability was computed (SR3, item 8 below).
6. **C-TRANSPORT-CERT attempt.** `attempt_transport_certificate` tried to
   build the crater<->floor 107-isogeny using the only ell-isogeny machinery
   committed in this codebase
   (`isogeny_class.find_kernel_generator` + `velu_odd`). Result: **UNREACHED**.
   `gcd(107, 19507) = 1` and every curve of trace t = 211 has
   `#E(F_p) = 19507` (Tate), so NO curve in this class carries an
   F_p-rational point of order 107 -- `find_kernel_generator`'s own
   precondition (`order % ell == 0`) fails on every curve here by
   construction, and `velu_odd` was never called. The genuine crater/floor
   107-isogeny needs a Galois-stable-subgroup (kernel-polynomial) construction
   over an extension field, which is not implemented anywhere in this
   codebase. No transport certificate was fabricated; the obstruction is
   recorded as an `implementation_gap`, classified `UNREACHED`.
7. **SR4 baseline-identity gate + the density-swept raw measurement
   collection (decomposition_rate_m2/m3, liftable_density,
   decomposition_efficiency for both arms): BLOCKED, `specification_error`.**
   `inputs.density_grid` in the approved, frozen contract states only the
   RULE (`exp_icinv.factor_base_fixed_size`) and `sweep_required: true` --
   it never instantiates the swept factor-base sizes, and no target count
   `T` is frozen anywhere in the text (contrast the sibling contract
   EXP-ICINV-4d33aa, whose `inputs.density_grid` explicitly lists
   `factor_base_sizes: [4,5,6,...,22]` and `target_counts: [100,400,1600]`).
   `experiments/EXP-JINV-bd141d/amendments/` does not exist. SR5 ("NO
   additional N, class, density row or seed without a versioned
   protocol_amendment filed BEFORE the extra data is generated") presupposes
   a frozen grid to compare against; inventing factor-base sizes or T here
   would BE the SR5 violation, not a way to satisfy the contract. This
   blocks SR4, the per-curve rate measurements for both arms, the
   RATE-based half of C-TRACEPAIR (the structural t/p/D0 listing of the five
   doubly-hit pairs is unaffected and was produced separately), C-RESIDUAL-P,
   and the density/degenerate-rate/coverage tail checks.
8. **SR3 instrument gate (BLOCKING), stated but also moot given item 7.**
   Verbatim per the contract: no |D_0|-arm or |Aut|-arm verdict may be read
   or reported until EXP-INSTR-36c8cf delivers a two-directional detection
   floor / false-positive rate at this design's actual geometry.
   EXP-INSTR-36c8cf Phase A (`RUN-INSTR-36c8cf-phaseA-2a5cd1`,
   `RUN-INSTR-36c8cf-phaseA-v2-57ca9a`) stopped at its own falsification
   criterion with no interval accepted; Phase B has not run. No verdict was
   computed for either arm -- `verdict.json` records
   `BLOCKED_SR3_AND_SPEC_GAP` for both, not a chosen or withheld
   TREND-DETECTED / NO-TREND / NOT-RESOLVABLE (SR7: nothing was computed and
   then selected/withheld).

## Protocol deviations (all recorded, none silently absorbed)

- **D1.** The contract's `inputs.density_grid` and target-count fields are
  incomplete in the approved text (see item 7 above). This experiment
  therefore terminates SHORT of raw rate measurement, not because SR3 fired
  first, but because a `specification_error` was hit independently and
  earlier in the pipeline. Both blocks are recorded; SR3 was never in a
  position to be the sole reason no verdict exists.
- **D2.** The contract's stratification variable r is, for this specific
  family (N = 19507 odd), IDENTICALLY zero on every curve -- there is only
  one populated stratum, not three. This is a structural consequence of the
  matched-order construction itself (fixing N odd forces r = 0), reported
  as a finding rather than modelled around.
- **D3.** C-TRANSPORT-CERT could not be discharged: the only ell-isogeny
  construction committed in this codebase (`isogeny_class.velu_odd` /
  `find_kernel_generator`) requires an F_p-rational kernel point, which
  cannot exist for ell = 107 on this class because gcd(107, 19507) = 1. No
  certificate was fabricated; the run reports `UNREACHED` with the exact
  mathematical obstruction and what a genuine construction would require.
- **D4.** `harness/runner.py` defines `_inference_block()` TWICE at module
  scope (once trying `orchestration.adapter.manifest.block_from_env`, once
  unconditionally returning a hardcoded `executor-terra` block); the second
  definition shadows the first, so every run this wrapper writes -- this one
  included -- records `inference.requested_policy: executor-terra` in its
  manifest rather than resolving through the adapter. This is a pre-existing
  defect in `harness/runner.py` (confirmed `status: clean` against HEAD at
  the commit this run pinned, i.e. it predates this task) and is out of this
  task's `write_scope`; it is recorded here rather than silently worked
  around or fixed out of scope. It does not affect correctness of this run's
  measured content: the run is deterministic Python with no model in the
  execution loop, so "no inference happened" is the honest content either
  way -- only the specific hardcoded label is wrong.

## Certificate discipline

`certificate.kind: none` throughout -- this run makes no discrete-log or
relation-decomposition claim; every number reported is a structural
enumeration or a count. `claim_tier: toy`, `sota_delta: 0`, no ECDLP claim in
either direction (contract `success_criterion` and `scale_relevance`).

## Reproducibility

`experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/manifest.yaml`
pins all 8 executed source files by sha256 (`all_pinned: true`); the 6
committed files are `status: clean` against `HEAD` at commit
`a9028dcd1dd755419223854e060e2f8d3043bc30`, and the 2 new modules are
`status: untracked` and pinned by their own hash.
