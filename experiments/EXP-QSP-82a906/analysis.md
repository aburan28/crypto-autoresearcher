# EXP-QSP-82a906 analysis — m=2 eliminant-degree cell of H-QSP-411d8f

Reviewed 2026-10-06 against origin/main e9b096ab05 (snapshot accepted by
DEC-20260918-abba0b, whose NA-2 review this is). Strictly separated into
Observation / Comparison / Inference / Limitation. No number below is
re-derived by hand; every figure is read from the committed run records
RUN-QSP-{c4b336, 55bd71, 28ef77, c6490f, 5ec02a} at the archived commits.

## Observation

All five stages ran; every gate `pass`; no run stopped early
(execution-report.yaml; RUN-QSP-28ef77 stage 2: opened_n [17, 23],
stop_reason null).

- **Instrument agreement (C3): zero disagreements on every reported cell.**
  The two independent implementations (I1_C_Bareiss_F2X and
  I2_Python_Newton_F2n, RUN-QSP-28ef77 `implementations` field) agree on
  deg_elim AND on the eliminant polynomial (identical `elim_hex`) on all 20
  chain rows, all 8 control rows, and the named fixture
  (RUN-QSP-c4b336: deg 14, poly 0x5861, `agree: true`).
- **Degree gates**: every chain cell has S0 per-variable degree 2 and S1
  per-variable degree 2d (RUN-QSP-55bd71, `all chain cells degree 2 and
  2d`, 20 rows).
- **Controls behave as designed** (RUN-QSP-c6490f): C2a (lambda=X) is
  identically zero on both engines with the I3 common factor recorded; C2b
  (lambda=X+1, d=1) gives deg_elim 8; the C1 random-pair nulls give deg_elim
  16 (d=2) and 23-24 (d=3) — the SAME magnitude as the chain cells.
- **The chain cells** (d in {2,3}, the 2+8 = 10 exhaustive non-linearized
  lambda): deg_elim takes values 14, 16 (d=2) and 17, 20, 22, 24 (d=3).
  rho_paper = deg_elim/(4d) ranges 1.4167-2.0.
- **The pre-registered medians** (RUN-QSP-5ec02a): median rho_paper(d=2) =
  1.875 and median rho_paper(d=3) = 1.9167, at BOTH n=17 and n=23 — because:
- **The n axis is exactly degenerate.** For every (d, lambda), the eliminant
  POLYNOMIAL is byte-identical at n=17 and n=23 (verified across all 20
  chain rows; e.g. lambda=X^2+1 gives 0x11544 at both n). Under the xi=1,
  F_2-coefficient specialisation, F^{n'} is the identity, so the chain
  polynomials — and hence the Sylvester matrix and its determinant — are the
  same polynomial at every n. The experiment's effective scope is 10 chain
  cells, not 20.

## Comparison

Against the pre-registered criteria of H-QSP-411d8f (as frozen in the
v1 contract and DEC-20260917-f37ca4, amended v2 DEC-20260917-9f82c1):

- "median rho_paper(d=2) >= 1/2": 1.875 >= 0.5 — **pass**.
- "median rho_paper(d=3) >= 1/2": 1.9167 >= 0.5 — **pass**.
- "median rho_paper(d=3) >= median rho_paper(d=2)/2": 1.9167 >= 0.9375 —
  **pass** (it rises).
- G1 (certified growing deficit): not fired. G2 (both medians < 1/4, or
  all cells identically zero with non-constant gcd): not fired.

Against the two modeled columns (RUN-QSP-5ec02a `M_E_paper_modeled` /
`M_E_note_modeled`): the paper column 4d UNDERSTATES the measured degree by
a factor ~1.9 at both d (14-16 vs 8; 17-24 vs 12); the note column 4d^2
overstates it at d=3 (17-24 vs 36, ratio 0.47-0.67) and matches it at d=2
(14-16 vs 16). The C1 random-pair null sits at the same ~1.9x-of-4d level,
so the factor is a property of the degree pattern (support), not of the
phi-chain structure.

## Inference

CONSISTENT WITH H1 AT THE TESTED CELLS, exactly as pre-registered: the
engine-independent eliminant degree of the m=2 no-Weil-descent chain does
not collapse below a constant fraction of M(E)_paper = 4d as d goes 2 -> 3;
it tracks ~1.9 x 4d with no decay (both medians >= 1/2, and the d=3 median
is not below half the d=2 median). The degree half of the kappa-floor
question (KN-OPEN-ac409f) therefore SURVIVES at m=2: the eliminant is at
least as large as the paper's M(E) pricing assumes, in fact ~1.9x it.

What this does NOT establish, per the contract's own scope: no lower bound
on kappa (a solving exponent, not a degree); nothing at m >= 3; nothing
about the closure reading (E') beyond that its degree assumption was not
falsified at these cells; and no inference from two d points to a growth
law in m.

## Limitation

- **Degenerate n axis (new finding of this review)**: the tested scope is
  10 chain cells, not 20; "at every tested n" is satisfied vacuously at
  both n because the eliminant polynomial is n-independent under this
  specialisation. The consistency verdict carries the weight of ONE field
  (F_2-coefficient chains), not two fields. A K-coefficient-lambda
  successor (where F^{n'} is not the identity) is the cell that would
  break the degeneracy.
- Single experiment, single session, preliminary strength; the in-run C3
  double-instrument agreement is the only replication.
- rho_paper ~ 1.9 rather than ~1: the paper's M(E) = 4d understates the
  degree at these cells; recorded as an observation, not adjudicated (the
  contract pre-registered both columns and decides neither formula).
- Toy tier: m=2, d in {2,3}, algebraic objects only; no curve, group,
  key or attack; ECC2K-130's rho baseline (2^60.9, KN-LIT-096) untouched.
- Wall time and RSS in the run records are diagnostics, never evidence.
