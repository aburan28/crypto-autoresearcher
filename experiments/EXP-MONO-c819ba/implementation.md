# EXP-MONO-c819ba implementation notes

Pure Python 3 stdlib + numpy (numpy used only for the exact-integer roll-sum
convolution, which is exact int64 arithmetic with no rounding, and for the
FFT-based character-side cross-check, which is float and declared as such).
No sympy, no CAS, no solver.

## Files

- `seed.py` -- SHA-256 seed derivation (`Drawer`), literal to the frozen
  `seed_derivation_rule`. Labels: `prime`, `curve-a`, `curve-b`,
  `null-subset`, `coset-pick`.
- `fields.py` -- `F_p` arithmetic, elliptic-curve point add/negate/scalar-mult,
  trial-division factorization.
- `curve.py` -- prime construction, curve construction, point enumeration,
  `Z/n1 x Z/n2` group-structure determination (elimination-method exact point
  orders, then a generator `G1` of the exponent `n2` and an independent
  generator `G2` of order `n1`), coordinate-map construction, x-coordinate
  factor-base construction and symmetry check.
- `groupstate.py` -- `CurveState`: bundles all of the above per curve.
- `panel.py` -- 8-curve panel construction (4 random-ordinary, `j=0`, `j=1728`,
  2 CM), same algorithm and structure as `EXP-MONO-12ce1c/implementation/panel.py`,
  new domain `EXP-MONO-c819ba/v1` (independent seed stream; no cross-contract
  comparability, per `comparability_policy`).
- `conv.py` -- exact-integer convolution tower (`N_1..N_4` via circular
  roll-sum on the `(n1,n2)` grid, `numpy.int64`, no floating point), exact
  variance via Python-`object` (arbitrary-precision) squaring to avoid int64
  overflow at `m=4`, and the FFT2-based character-spectrum cross-check
  (`numpy.complex128`, declared float, 1e-10 relative tolerance per the
  contract).
- `controls.py` -- matched symmetric null-subset draws, subgroup positive
  control, coset-union positive control.
- `run_experiment.py` -- orchestrates Stage 0 through Stage 4 in the
  contract's own order and writes `raw-result.json`.

## Protocol interpretations and deviations (recorded per AGENTS.md; none
silently resolved)

1. **"Full factor base" vs. the `N/2` ladder rung.** The contract's literal
   `factor_base_construction` text defines "the full factor base" as *every*
   x with `f(x)` a nonzero QR. Since every non-2-torsion curve point
   automatically has `f(x(P)) = y(P)^2`, a QR by construction, this literal
   reading makes "the full factor base" equal essentially the WHOLE group
   minus the `Z` two-torsion/zero points (`F = N-1-Z`, confirmed
   numerically: e.g. RO1 gives `fb_full_size=116` against `N=117`) --
   **not** `F ~ N/2` as the contract's own `factor_base_size_ladder`
   (`["N/16","N/8","N/4","N/2"]`) and `claim_ceiling`/`arms_and_controls`
   text repeatedly call it. Interpretation adopted: the FULL x-coordinate
   factor base referred to throughout the contract's own `F ~ N/2` language
   is the **`N/2`-sized PREFIX** of the QR-x point stream (`fb_full[:N//2]`,
   rounded to the nearest even number so the `(x,y)/(x,-y)` pairing that
   makes it symmetric stays exact), i.e. the SAME truncation rule the
   contract gives for the smaller rungs, applied uniformly to all four rungs
   including the largest. This is the only reading consistent with the
   ladder's own declared top value and with every other place in the
   contract that calls the full base "`F ~ N/2`". The literal QR-x pool
   (`fb_full`, size `N-1-Z`) is retained and reported (`fb_full_size` per
   curve, `panel.group_structures`) as the SOURCE POOL the ladder truncates,
   never as a treatment arm itself. **This is a finding in its own right,
   reported, not silently normalized away.**
2. **Subgroup construction: coordinate-based, not scalar-mult-image.** An
   early implementation built `H_k` as the image of the scalar
   multiplication-by-`k` map, which has EXACT order `N/gcd(k,N)` only for
   CYCLIC groups. On this contract's non-cyclic panel curves (`J0`:
   `n1=18,n2=18`; `J1728`: `n1=2,n2=530`; `RO3`: `n1=3,n2=96`) the kernel of
   mult-by-2 is the FULL 2-torsion subgroup (order `gcd(2,n1)*gcd(2,n2)`,
   which can exceed `gcd(2,N)`), so the image can be SMALLER than `N/2` --
   caught directly: the `k=2` and `k=4` images returned the SAME (wrong,
   `N/4`-sized) set on `J0`/`J1728`/`RO3` in the first test run. Fixed to
   the exact coordinate construction `H_k = {(a,b) in Z/n1 x Z/n2 : b == 0
   mod k}`, order `n1*(n2/k) = N/k` exactly whenever `k | n2`, which is
   correct for both cyclic and non-cyclic groups. **Subgroup availability is
   therefore gated on `4 | n2` (the larger invariant factor), not `4 | N`**
   -- `J0` and `J1728` have `4 | N` but `n2 = 18` and `n2 = 530` respectively
   are NOT divisible by 4, so they are correctly EXCLUDED from the
   subgroup-capable set (`RO3`, `CM1` qualify: `n2 = 96, 140`).
3. **Coset-union control, choice of `g`.** The contract asks for "a union of
   two cosets of a subgroup of index 4" without pinning which two. A
   self-negating pair (`g` and `-g` in the same or paired coset) was tried
   first and shown analytically (and confirmed numerically) to ALWAYS
   degenerate to either the index-2 subgroup itself (extremal, `C/F=1`,
   redundant with positive control 1) or to a single coset (not a union at
   all), for both possible order-4-quotient structures. The implementation
   instead uses `FB = H4 union gH4` for a single `g` NOT required to be
   self-negating (this arm is not required to be symmetric -- the exact
   identities (I1)/(I2) hold for any subset, symmetric or not; symmetry is a
   real-world FB-modeling choice, not a mathematical precondition). Closed
   form, derived here and verified numerically to machine precision on both
   capable curves (`RO3`, `CM1`): `Shat(chi) = h*(1+chi(g))` for `chi`
   trivial on `H4` (four characters), `0` otherwise; measured
   `C/F = 1/sqrt(2) ~ 0.7071` on both curves (genuinely INTERMEDIATE between
   the subgroup extreme's `C/F=1` and a near-zero random value), confirming
   this design choice gives the "effect size that could actually occur"
   sensitivity test the contract asks for, not a second copy of the extreme.
4. **`j=0`/`j=1728` host prime.** `j=0` requires `p = 1 mod 3` and `j=1728`
   requires `p = 1 mod 4` for an ordinary (non-supersingular) member to
   exist. Under THIS contract's own domain (`EXP-MONO-c819ba/v1`, distinct
   from `EXP-MONO-12ce1c`'s by design), `p9 = 307 = 3 mod 4`, so `p9` cannot
   host an ordinary `j=1728` curve at all (every candidate is forced
   supersingular, confirmed: 20000 candidates scanned, 0 accepted). Resolved
   by a deterministic, seed-free search over the already-constructed
   `field_bits` prime list for the smallest prime satisfying each
   congruence (`j=0` -> `p9=307` itself, `1 mod 3`; `j=1728` -> `p10=1013`,
   `1 mod 4`), rather than forcing both onto one prime as
   `EXP-MONO-12ce1c` happened to be able to (that was a property of ITS
   domain's `p9=421`, not a property of the construction rule itself).
5. **`draw_symmetric_null` parity lock.** An early implementation
   opportunistically added a self-negating (2-torsion) point whenever drawn.
   Since ladder sizes `F` are always forced even (interpretation 1), and
   only regular `+/-` pairs (which preserve parity) remain available once a
   single self-negating point has been consumed, this permanently parity-
   locked the draw one short of any even target whenever the lone
   self-negating point was drawn before the target was reached (observed as
   a hang / rejection-budget exhaustion on `RO3`, which has exactly one
   2-torsion point). Fixed: a self-negating point is only accepted when it
   is the EXACT remaining odd slot (`F - len(chosen) == 1`); since every
   target `F` used in this run is even, self-negating points are never
   consumed at all, which is correct and reproducible.
6. **Domain split for replication.** Panel construction (primes, curves) uses
   the fixed `PANEL_DOMAIN = "EXP-MONO-c819ba/v1"` for both runs (confirmed
   identical panel in both runs' `raw-result.json`); null-subset and
   coset-pick draws use `f"{PANEL_DOMAIN}/run-{master_seed}"`, varying
   between the two replication seeds, matching `EXP-MONO-12ce1c`'s
   precedent for resolving the same domain-vs-two-seeds ambiguity.

## Known float-precision limitation (disclosed, not a defect)

The character-side cross-check (`numpy.fft2`, double precision) accumulates
relative error that GROWS with `m` because `Var` at `m` uses `|Shat|^{2m}`
(an 8th power at `m=4`). Measured maximum relative residual between the
EXACT-integer convolution side and the FLOAT character side across every
Stage-3 real-arm cell in RUN-1: `m=1: 4.8e-16`, `m=2: 7.3e-14`,
`m=3: 5.2e-11`, `m=4: 3.9e-9`. The contract's declared float tolerance is
`1e-10` relative; **the `m=4` cross-check exceeds it** on several cells. This
is disclosed as a `dual_path_control` finding, not treated as invalidating
any cell: the contract itself states "the PRIMARY metric is always the
exact-integer convolution side, so the absence of exact roots of unity can
never affect a reported result," and the exact-integer side (verified three
independent ways: Stage 0's fixture, Stage 2's `m=3,4` gate, and every
Stage-3/4 cell) is unaffected by this float-only limitation.

## Performance

Full pipeline (8-curve panel, `N` up to 1063, F-ladder x 4, 30 null draws +
real arm per cell, both positive controls, coset-union control, prime
ladder): **~1.9 seconds wall clock per run**, far under the 7200s budget. No
scope reduction was necessary; the full contract-specified panel size,
F-ladder resolution and null-draw count (30) were used throughout, contrary
to the specification's own anticipation that scope might need reducing --
the `numpy` roll-sum convolution and FFT2 character-spectrum trick are both
`O(N log N)`-to-`O(F*N)` at these toy sizes and complete in milliseconds per
cell (benchmarked: ~10-30ms per 3-step convolution tower at `N~3100,
F~1500`).

## Certificate discipline

`certificate.kind: none` for every run. No discrete-log solve and no
factor-base relation is claimed anywhere in this experiment; it is a pure
group-theory / Fourier-analysis measurement.
