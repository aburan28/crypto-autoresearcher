# R4 — nearby objects, confounds and conventions

Task TASK-20260904-ed0e8f (red team), joint R4. Numbers from `r4_results.json`
(`r4_nearby_and_ptm.py`), `r4d_sigma.json`, `r4d_sigma_crypto.txt`. Scope:
d = 2, the tested (m, s, p). Result of the joint: **breaks (partially)** — (a)
and (c) hold with one re-scoping each, (b) produces the missing nearby object
and a partial proves-too-much hit, (d) finds the closure's stated reason wrong
while its conclusion survives at the parameters that matter.

---

## (a) The mixed-block object: is the executed reading the right one?

The contract's `NEARBY-MIXED-BLOCK` says "x_k = sum_i c_{k,i} a_i with the a_i
shared across k". `D-MIXED-READING` executed it with all **ms = 6** variables
shared and recorded the literal **s = 3**-shared reading as degenerate and not
run.

* Executed reading, independently recomputed (3 random coefficient draws,
  p = 4099): `d_ff = 6`, `fall_dim = 14`, profile
  `(4;1,1,1,0) (5;6,6,6,0) (6;15,15,1,14) (7;20,20,0,20)` — identical to the
  package's 36/36 at 6 with fall_dim 14.
* Literal reading (n = 3 shared variables), which the package did not run:
  the generator has degree **3**, not 4 (`ell_1^2 ell_2^2` needs 4 distinct
  squarefree variables), `d_ff = 4`, `fall_dim = 3`. Reporting it costs
  nothing and closes the deviation: it is degenerate as recorded, and it does
  not return 5 either.

The executed object IS the nearest object the method-ceiling names (same
generator degree 4, same number of variables 6, same ring; only the block
factorisation of the top form is destroyed), and it separates from the Semaev
value by one degree. **But it does not establish what F5 claims it does.** See
(b): I exhibit a top form that is not a block tensor and still gives
`d_ff = 5`. The correct reading of the mixed-block result is "a GENERIC
destruction of the block structure raises d_ff to D_null", not "d_ff = 5
identifies block structure".

## (b) A non-tensor top form that does not collapse (the missing test)

`D-NONMONO-COLLAPSE`: the contract's `NEARBY-NON-MONOMIAL-TOP`
(`x_1^2x_2^2 + x_1^4`) collapses at s = 3 because `ell_1^4 = 0` in three
squarefree variables, so the object never realised a non-monomial top form. I
constructed two that do (degree-4 top form, plus dense random sub-top terms,
p = 4099, 3 reps each; rank of the block-1 × block-2 coefficient matrix
computed to certify non-tensor):

| top form | tensor rank 1? | d_ff | fall_dim | note |
|---|---|---|---|---|
| `ell_1^3 ell_2 + ell_1 ell_2^3` | no | **6** | 14 | the plan's object; the closed form's 5 is NOT forced |
| `ell_1^2 ell_2^2 + ell_1^3 ell_2` | no | **5** | **2** | `d_ff` agrees with the closed form; `fall_dim` does not (2 vs 4) |
| `ell_1^2 ell_2^2` (tensor control) | yes | 5 | 4 | reproduces the Semaev pair |

The first object satisfies the declared failure signature (a value in [5,6],
not forced to 5 — it is 6). The second is the interesting one and is reported
as a **partial proves-too-much hit**: its top form is
`ell_1^2 ell_2 (ell_1 + ell_2)`, not a block tensor, so (D4)'s tensor-kernel
step does not apply, yet `d_ff = 5` comes out. The survival happens at the step
"`AI_p(S~) = min_k a_0(A_k, ell_k^e)`": what actually produces 5 is the mere
EXISTENCE of a degree-1 annihilator of the top form, and being a block tensor
is a sufficient, not a necessary, way to have one. `fall_dim` does discriminate
(2 vs 4). **Consequence: `d_ff` alone under-determines the mechanism; the
mechanism claim should be carried by the pair (d_ff, fall_dim) or by the
kernel dimension, not by d_ff.**

## (c) Confounds

**(i) Ideal-level / CRT reading (`IDEA-20260830-cb8e46`, A-NSOL-6).** No metric
reads an ideal invariant directly: `N_sol` and `d_solve` are computed in
`sol_covariate` and never enter `d_ff` or `fall_dim` (verified by reading
`run_pfdr_5726af.py`; `N_sol` appears only at lines 388–405 and in the metric
dump). **But the confound is not absent by construction, as
`CTRL-CONFOUNDERS-NAMED` asserts.** By the R1 derivation,
`full_rank(D) ≤ 2^{ms} − N_sol` and the row-collapse term is exactly "a degree
`D−δ` form vanishing on `supp(S~)`", so the solution set reaches `fall_dim`
through a side channel. It is numerically absent at every tested cell
(`N_sol ∈ {1,2,6}` against thresholds `2^{ms-a_0} ∈ {8, 32, 64, 256, 512, 2^11,
2^14}`) and exhaustively present at two small-prime instances (R1 §5). The
honest statement is "excluded numerically at the tested cells", not "excluded
by construction".

**(ii) Gröbner output degree (`IDEA-20260807-899c5e`).** Verified absent: no
Gröbner basis, no CAS termination event, no reduced-basis degree anywhere in
`run_pfdr_5726af.py` or in `harness/macaulay_fp/`. `sol(D)` is a recorded
covariate only, and `d_solve` is `None` at every draw (never reached within
`D_max`).

**(iii) The D_null convention.** For one generator of degree δ on n squarefree
variables the semi-regular layer count is `c_D = C(n,D) − C(n,D−δ)`, and
`c_D < 0 ⟺ 2D > n + δ ⟺ D ≥ floor((n+δ)/2) + 1`, while `c_D = 0 ⟺ 2D = n+δ`.
So the contract's `floor((n+δ)/2)+1` is the first **strictly forced** fall, and
84cdb7's `ceil((n+δ)/2)` is the **balanced** degree, where the layer matrix is
square and a generic object is invertible — no fall. The measurement settles
it: NULL-1 falls at the contract's value in 60/60 seeds at each of five m = 2
cells and 10/10 at each m = 3 cell, and never one lower. **84cdb7's null
formula under-predicts by one whenever `n+δ` is even.** Does the convention
change a scored comparison? **No** — every scored comparison in this package is
against the *measured* NULL-1, not against a formula. But two narrative
statements do depend on it: under 84cdb7's convention "d_ff strictly below the
null" would be false at s = 2, 3, 4 (5 vs 4, 5 vs 5, 6 vs 6). A second, larger
defect: 84cdb7's `ceil((ms(d−1)+2m)/2)` uses `2m` for the summation
generator's total degree, correct only at m = 2; at m = 3 the digit generator
has degree `m·2^{m-1} = 12` (confirmed: `generator_degree = 12` in both m = 3
runs), so the `D_null_84cdb7` column printed at (3,2,4) and (3,2,5) (9 and 11)
is the null of a system that does not exist and is not a comparator. It is
harmless because it is never scored, and it should be dropped or annotated.

## (d) (D7): σ ≥ 1 and the closure of 84cdb7's Outcome 3 at d = 2

`IDEA-20260808-812554` defines `T_solve = B^{(m-1)σ}` and requires
`σ < 1 − 2/(m−1)` to beat rho. (D7) argues: even under `d_solve = d_ff`, the
column count `Σ_{j ≤ d_ff} C(ms, j) ≈ B^{m H(1/(2m))}` gives `σ ≥ 1`.

Recomputed (`r4d_sigma.py`), charging `T_solve ≥ columns^ω`, so
`σ ≥ ω·m·H(1/(2m))/(m−1)` in the limit `s → ∞`:

| m | 2 | 3 | 4 | 5 | 6 | 7 | 10 |
|---|---|---|---|---|---|---|---|
| asymptotic σ bound (ω = 1) | 1.623 | 0.975 | 0.725 | 0.586 | 0.497 | 0.433 | 0.318 |
| admission threshold 1 − 2/(m−1) | — | 0 | 0.333 | 0.5 | 0.6 | 0.667 | 0.778 |
| bound ≥ threshold (ω = 1)? | — | yes | yes | yes | **no** | **no** | **no** |

So **"σ ≥ 1" is literally true only at m = 2**, and the asymptotic form of the
argument stops excluding Outcome 3 from m = 6 upward with a linear cost charge
(from m = 10 with ω = 2). That is a defect in the stated reason for the
closure.

The conclusion nevertheless survives at the parameters that exist, and the
reason is a constraint the record does not invoke: `2^s ≤ p` caps s (≤ 256 for
a 256-bit p) while the regime condition `s ≥ 2^{m-1}` caps m at 9 for s = 256
(and at 7 for s = 64, the β = 1/4 balance point). At those finite points the
exact column count gives (ω = 1)

| (m, s) | (3,256) | (4,128) | (4,256) | (5,256) | (6,256) | (7,256) | (9,256) |
|---|---|---|---|---|---|---|---|
| σ lower bound | 1.015 | 0.901 | 0.818 | 0.779 | 0.859 | 1.031 | 1.125 |
| threshold | 0 | 0.333 | 0.333 | 0.5 | 0.6 | 0.667 | 0.75 |

— the bound clears the threshold everywhere the closed form applies. **So the
Outcome-3 stake is closed at d = 2 for `2^s ≤ p ≤ 2^256` and every m for which
the closed form applies, but NOT because σ ≥ 1** (σ ≥ 1 fails at (4,128),
(4,256), (5,256), (6,256)). And what remains open is named precisely: for
`m ≥ 10` at 256-bit p, `s < 2^{m-1}` and the hypothesis is in its own excluded
regime, so it closes nothing there — and `IDEA-20260808-812554`'s table says
large m is exactly where the admission threshold is loosest. The closure is
weakest where the stake is most attractive; that should be in the record.

Two further notes. (1) `d_solve = d_ff` is generous in the safe direction (a
larger solving degree only increases the column count), and the package's own
covariate says `d_solve` was never reached within `D_max` at any draw, so the
hypothetical is not supported by measurement but its use is conservative.
(2) `EXP-PFDR-cbdefb` observes `d_lf = d_ff` at every cell (the closure
completes at the first fall), which makes `d_solve = d_ff` more plausible, not
less; it does not change the arithmetic above.
