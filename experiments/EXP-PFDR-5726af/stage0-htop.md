# EXP-PFDR-5726af — Stage 0: the s = 2 hand fixture and the H-TOP symbolic check at m = 3

Task TASK-20260903-b0727c (Executor). Observations only; no hypothesis status is
touched. The frozen prediction file `stage0-predictions.yaml`
(sha256 `e5198d84094fa299933e0f8bbe6c7bcc41e37cce42a9d58854ce5df6cf339e94`) was
written before any official rank; its sha256 is recorded in every manifest under
`inputs.parameters.stage0_predictions_sha256`.

## 1. The s = 2 hand fixture (CTRL-S2-HAND-FIXTURE)

Hand derivation (zero compute). With `ell_1 = a10 + 2 a11`, `ell_2 = a20 + 2 a21`
and `a_i^2 = 0` in the top-form algebra A:

    ell_1^2 = a10^2 + 4 a10 a11 + 4 a11^2 = 4 a10 a11
    ell_2^2 = 4 a20 a21
    degree-4 part of S_3(ell_1, ell_2, x_R) = (x_1^2 x_2^2)|_{x_k = ell_k} = ell_1^2 ell_2^2 = 16 a10 a11 a20 a21,

because the degree-4 part of `S_3(x_1, x_2, x_R)` in `(x_1, x_2)` is the single
monomial `x_1^2 x_2^2` (all terms carrying `a`, `b` or `x_R` have `x`-degree at
most 3). Multiplication by `16 a10 a11 a20 a21` maps `A_1` into `A_5 = 0` (n = 4)
and is nonzero on `A_0`, so `a_0 = 1`, `d_ff = 4 + 1 = 5 = D_null = floor(8/2) + 1`,
and the four rows `a_i S~` all lose their top part, giving `fall_dim = 4` when
they are independent in B.

Meter result (official run `RUN-PFDR-5726af-m2-s2-gate`, metric
`CTRL-S2-HAND-FIXTURE`; curve seed 1101 at p = 4099: a = 527, b = 72, j = 892,
on-curve x in [0, 4) = {1, 2, 3}; target seed 1: x_R = 2374, planted as
P_1 + P_2 with certificate re-verified by two independent point-addition
implementations):

| item | hand | meter |
|---|---|---|
| degree-4 part of S~ | `16 a10 a11 a20 a21` | `16*a10*a11*a20*a21` (exact match of the top form dict) |
| d_ff | 5 | 5 |
| fall_dim(d_ff) | 4 | 4 |
| rank profile (D: rows, full, top, fall) | — | 4: 1, 1, 1, 0; 5: 4, 4, 0, 4; 6: 6, 6, 0, 6 |
| independent rank oracle (sympy DomainMatrix over GF(p)) | — | agrees at every D (full and top) |

Full reduced generator recorded in that run's raw result:
`16*a10*a11*a20*a21 + 1507*a10*a11*a20 + 3022*a10*a11*a21 + 1507*a10*a20*a21 + 3022*a11*a20*a21 + 3103*a10*a11 + 2246*a10*a20 + 3196*a11*a20 + 3196*a10*a21 + 3804*a11*a21 + 3103*a20*a21 + 1756*a10 + 3014*a11 + 1756*a20 + 3014*a21 + 3917`.

**Gate result: PASS** (`gate_pass: true`). The stopping rule "stop before the
deciding cell if the s = 2 hand fixture or the meter's known answer fails" did
not fire. The meter's own known answer (p = 2, KN-FIND-006) and the
planted-syzygy control are the tooling task's tests
(`tests/test_macaulay_fp.py`, 52 passed at meter commit `2d2083e5`). In this
session the suite was re-run (`python3 -m pytest tests/test_macaulay_fp.py -q`,
"52 passed in 2.35s") AFTER the four Stage 0/1 runs and while the Stage 2 runs
were executing, not before the first official run — the ordering is disclosed
in implementation.md (D-TESTS-ORDER). The meter files' per-file sha256 in every
manifest are identical to those listed in `harness/macaulay_fp/VALIDATION.md`,
so the tested code and the executed code are the same bytes.

## 2. H-TOP symbolic check at m = 3 (CTRL-H-TOP-SYMBOLIC)

Official run `RUN-PFDR-5726af-htop`. CAS: **sympy 1.14.0** (Sage is absent on
this host; see deviation D-HTOP-CAS in implementation.md). Construction, exactly
as the contract's `inputs.symbolic_S4` states: a from-scratch
`S_3(x, y, z) = (x - y)^2 z^2 - 2((x + y)(x y + a) + 2 b) z + (x y - a)^2 - 4 b (x + y)`
(not `harness.semaev.s3_expr`, which is only cross-checked), then
`S_4(x_1, x_2, x_3, x_R) = Res_T(S_3(x_1, x_2, T), S_3(x_3, x_R, T))` with `a`,
`b`, `x_R` symbolic, expanded and read as a polynomial in `(x_1, x_2, x_3)` with
coefficients in `Z[a, b, x_R]`.

| quantity | observed |
|---|---|
| total degree in (x_1, x_2, x_3) | 12 |
| per-variable degrees | [4, 4, 4] |
| number of distinct x-exponent monomials | 125 |
| monomials of total degree 12 | exactly one: (4, 4, 4) |
| coefficient c of x_1^4 x_2^4 x_3^4 | **1** (integer constant; not a polynomial in a, b, x_R; cannot vanish on any locus) |
| c mod 4099, c mod 65537 | nonzero, nonzero |
| top form over F_4099 and F_65537 | single monomial x_1^4 x_2^4 x_3^4 |
| numeric consistency of the resultant route | S_4 vanishes at (x(P_1), x(P_2), x(P_3), x(P_1 + P_2 + P_3)) on 5 random on-curve triples at each prime (curve seed 1101) |
| m = 2 check in the same run | degree-4 part of S_3(x_1, x_2, x_R) is x_1^2 x_2^2 with coefficient 1 |
| tail check (contract): can c vanish? | No: c = 1 is constant, so there is no special locus to exclude |

Lowest-order coefficients, for the record (from raw `S4_terms_by_x_exponent`):
constant term `a^4 x_R^4 - 8 a^3 b x_R^3 - 64 b^3 x_R^3`; coefficient of `x_3^4`
is `a^4 - 8 a^2 b x_R + 16 b^2 x_R^2`.

**Gate result: PASS** (`gate_m3_secondary_open: true`); Stage 3 (m = 3, s in
{4, 5}, p = 65537) was therefore run.

### 2.1 Observation about the archived profile cited by the derivation

H-PFDR-4148b8 (D3) and IDEA-20260903-e1e38b infer the m = 3 monomial top form
from "the archived EXP-ALPF-011 profile [4, 4, 4, 12] (total degree 12,
per-variable degree 4)". Reading
`experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep_result.md`
(section 2, "Leading-form degree profile is the homogeneous top-form degrees
actually fed to the meter", rows with |FB| = 4 and rep "(A) x-ring baseline"):
the list `[4, 4, 4, 12]` is the list of **generator degrees** of that meter's
four generators — three factor-base membership polynomials of degree |FB| = 4
and S_4 of total degree 12 — not a per-variable degree profile of S_4. The
archived profile therefore supports only "total degree 12"; the per-variable
degrees [4, 4, 4] and the single-monomial top form are established here
symbolically, not by the archive. This is recorded as an observation about the
derivation's citation (the symbolic check itself passed); no record is edited.

### 2.2 Not done

- m = 4 (S_5) was not attempted (the contract lists it as "if affordable" under
  secondary metrics; the m = 4 cell is not part of any planned run and the
  run budget of 10 was fully allocated).
- The harness `s4_expr` path (KN-OPEN-5b3a08) was evaluated only to report its
  total degree (12 in x_1..x_4); nothing in this experiment relies on it.
