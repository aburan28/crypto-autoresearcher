# TASK-20260808-2a9085 — Section A: the AM-4 admissibility gate

BATCH-cbe023 / GOAL-MLKEM-005. **Executor artifact of observations.** No status
change, no hypothesis movement, no evidence record. Nothing here declares a
hypothesis supported, rejected or closed, or a heuristic validated or refuted.

**CLAIM TIER: TOY, unconditionally.** No number in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. No number measured at `d <= 140` is transported to `beta = 606`,
`d = 1420`, or to any other parameter set, by extrapolation or by analogy.

`certificate.kind: none`, stated explicitly: no discrete-log solve and no
factor-base relation is claimed or produced, so `docs/claims-and-verification.md`
requires no solution certificate. Every independent re-verification below is an
INSTRUMENT CHECK and is labelled as one, never as a certificate.

---

## 0. Notarization — verified before any measurement, and quoted here

```
prereg              coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/
                    tasks/TASK-20260808-35efa3/prereg.md
sha256 measured     2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
sha256 task card    2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8   MATCH
sha256 receipt file 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8   MATCH
notarizing commit   4f7c63703d50445c758fc6216ca8d4436e04ae2a
assertion made      git merge-base --is-ancestor <NOTARIZING COMMIT ITSELF> HEAD   -> TRUE
                    (correction V-7 honoured: asserted against the notarizing
                     commit, NEVER its parent)
HEAD at run time    111d04124a4e12f5341dc046da52d0253c5cf65b
```

The run aborts on any mismatch; none occurred. `prereg.md` was not modified.
The worktree was dirty at run time with files belonging to other, unrelated
tasks (`knowledge/INDEX.md`, `GOAL-MCE-001/...`, `KN-LIT-c41d8b.md`,
`RQ-MCE-3f7c02.yaml`, and two sibling BATCH-cbe023 task directories); the exact
list is recorded in `results_am4.json -> notarization.worktree_dirty_paths` and
in the run manifest. No early durability commit was made, for any reason.

## 0.1 Inference record (verbatim, as directed)

```
requested_policy: executor-implementation
degraded_allowed: false ; fallback_allowed: false
resolved: per CLAUDE.md, per-role model selection is process-level under the Claude Code
  runtime and subagents keep model: inherit, so the resolved model is the session model
fallback_used: false
model_verified: false (no adapter probe receipt for this session)
```

Independence in this batch is **procedural** — separate session, no shared
scratch, snapshot before review — and never model-level. Rule 12 remains UNMET
and UNWAIVED in this goal and is recorded, not smoothed.

## 0.2 Budget actually consumed

| item | cap | used |
|---|---|---|
| wall clock | 10800 s | **854.4 s** (`/usr/bin/time`: 855.65 s real) |
| memory | 8 GB | **789 MB** peak RSS |
| runs | 1 | 1 |
| D arm | 3000 s | 232.4 s |
| X9 per lattice | 300 s | L11 **BOUND at 300.4 s**; every other lattice completed |
| X10 total | 3600 s | not bound |
| stage-1 checkpoint | 3600 s | not bound — mirrors L2 and L5 were **NOT** dropped, so REL-2 is measured |

BLAS threads pinned to 1 (`OMP/OPENBLAS/MKL/VECLIB/NUMEXPR = 1`), single
process. `gmpy2` is not installed and nothing here depends on it; `numpy 2.4.0`,
`scipy 1.15.3`, `sympy 1.14.0`, `mpmath 1.3.0`, `fpylll 0.6.4` were present.

---

## 1. THE OUTCOME, from the frozen map of prereg 2.7, applied IN ORDER

The map was applied mechanically in the order `R5 -> R4 -> R1 -> R3 -> R2 -> R2'`.
The outcome was not chosen after seeing data.

> ### **OUTCOME: `R3` — ADMISSIBLE BUT NOT RELEVANT. The obstruction is RELOCATED, not removed.**
>
> Three candidates — `X8 = rdet`, `X9 = lam1n`, `X10 = hkz` — pass `G-NUM`,
> `G-INV` and `G-Q` and **fail `G-REL`**. No candidate passes both clauses of
> `G-REL`, so `R1` is empty. `R3` is reported as its own result, never as `R1`
> and never as `R2`, exactly as prereg 2.7 requires.

Row-by-row, with the evidence for each:

| row | fired? | why |
|---|---|---|
| `R5` | **no** under the arm-level reading; see 1.1 | `G-NUM` passes for all ten candidates (max `rho_T0 = 6.20e-11`, `tau_num = 1e-6`); no dependency is missing |
| `R4` | **no**, per the frozen trigger list | neither clause of 2.7's `R4` fired; see section 4, which also reports the one candidate whose 2.4 per-candidate verdict is "premise REFUTED" |
| `R1` | **no** | no candidate passes `G-REL1` **and** `G-REL2` |
| `R3` | **YES** | `X8`, `X9`, `X10` |
| `R2` | not reached | `R2` is exclusive of `R3` by construction |
| `R2'` | not reached | — |

`R2 / R2'` were not reached because `R3` fired first. The `GEN-1/2/3` conditions
were nevertheless evaluated and are reported in full in section 7, because they
are what a successor needs in order to know whether the `f(P)`-class obstruction
is general — and all three hold.

### 1.1 The one place where `R5` is arguable, and why the headline is robust to it

The `X9/X10` arm at lattice `L11 = (d=40, k=12)` hit its declared 300 s
per-lattice cap at 300.4 s and did not complete its full 8-basis grid; `L7, L8,
L9, L10, L12` completed in full. A budget cap is INFRASTRUCTURE SIGNAL and is
never a refusal of a candidate and never an obstruction (`AGENTS.md` rule 3;
prereg 2.9, 5.7). Two readings of `R5`'s "a declared budget cap binds before that
candidate's arm completes" are available and **both are reported**:

* **arm-level reading** (used for the headline): `X9` and `X10` are adjudicated,
  on 5 of 6 small-`d` lattices complete plus a partial `L11`, with 4449 residual
  samples each. `R3 = {rdet, lam1n, hkz}`.
* **strict reading**: `X9` and `X10` are NOT ADJUDICATED and do not count toward
  `GEN-2`. Then `R3 = {rdet}` alone, and `GEN-2` would FAIL for want of a second
  non-`f(P)` candidate.

**Under both readings the headline is `R3`**, because `X8 = rdet`'s arm completed
in full and reaches `R3` on its own. The readings differ only in whether `X9` and
`X10` may be cited, and in `GEN-2`.

---

## 2. THE TWO FROZEN CLAUSES THAT COULD HAVE VOIDED THIS RUN — both checked first

These were evaluated before any candidate was judged, exactly as prereg 2.10
requires.

### 2.1 The LAXITY CONTROL: `X7 = tr(P^2)` — **REFUSED by G-Q. The gate discriminates.**

```
X7 = tr(P^2)   G-INV  max rho over {T1,T2,T3} x 6560 samples = 1.30e-15   <= tau_num = 1e-6   PASS
               G-Q    |X(3329) - X(1)| / max(|X(3329)|, beta) = 3.55e-16   <  tau_q = 0.10    REFUSED
```

`tr(P^2)` measured exactly `beta` at every one of the eight `q` values, at every
`beta`, at both sweep cells — the raw ladder is `{15.0}`, `{30.0}`, `{35.0}`,
`{50.0}`, `{65.0}` at `L1` and `{20.0}`, `{40.0}`, `{45.0}`, `{70.0}`, `{95.0}`
at `L4`, each a one-element set across the whole ladder.

**PRED-A3 HOLDS in both halves.** The frozen clause of prereg 2.8 / 2.10 Form 1
— "if `X7` passes `G-Q` the gate is declared INADMISSIBLE and no admissibility
claim may be reported" — **did NOT trigger**. The gate is admissible.

### 2.2 The POSITIVE CONTROLS: `X8 = rdet` and `X9 = lam1n` — **both PASS G-INV.**

```
X8 = rdet    T1 max 2.51e-13   T2 max 0.00e+00   T3 max 9.73e-16    (tau_num = 1e-6)
X9 = lam1n   T1 max 0.00e+00   T2 max 4.51e-15   T3 max 7.15e-15    (tau_num = 1e-6)
```

**PRED-A4 HOLDS**: `X8` passes `G-INV` at `<= tau_num` under `T1` and `T2`, and
at `<= tau_inv` under `T3` — in fact at `<= tau_num` under `T3` as well. `X8`
also passes `G-Q` at `0.9970`, so the pair (`X7`, `X8`) demonstrates that the two
criteria discriminate in **opposite** directions before any candidate was judged.

The frozen clause of prereg 2.10 (b) — "if `X8` fails `G-INV` the gate is
INSTRUMENT-LIMITED and NO REFUSAL OF ANY CANDIDATE MAY BE REPORTED" — **did NOT
trigger**. The refusals below may therefore be reported.

**Independent re-verification of `X8` (INSTRUMENT CHECK, not a certificate).**
`rdet` is a solver-free quantity with an exact closed form on these bases,
`|det B|^{1/d} = q^{(d-k)/d}`. Recomputed by code independent of the measurement
path, against every recorded `q`-ladder entry:

| cell | q=2 | q=4 | q=16 | q=64 | q=256 | q=1009 | q=3329 |
|---|---|---|---|---|---|---|---|
| `L1` measured | 1.6245047927 | 2.6390158215 | 6.9644045064 | 18.3791736800 | 48.5029301283 | 126.6845976271 | 292.1592605136 |
| `L1` exact | 1.6245047927 | 2.6390158215 | 6.9644045064 | 18.3791736800 | 48.5029301283 | 126.6845976271 | 292.1592605136 |
| `L4` measured | 1.6406707120 | 2.6918003853 | 7.2457893141 | 19.5042184673 | 52.5014627845 | 139.8416524874 | 328.0487785943 |
| `L4` exact | 1.6406707120 | 2.6918003853 | 7.2457893141 | 19.5042184673 | 52.5014627845 | 139.8416524874 | 328.0487785943 |

Maximum relative error over the whole ladder: **6.76e-15**.

*Recorded infrastructure note.* `numpy.linalg.slogdet` emits `divide by zero` /
`overflow` / `invalid value` RuntimeWarnings on these bases (at `L4` the
determinant is `q^100 ~ 10^352`, past the float64 range). The warnings arise in
slogdet's internal *sign* accumulation; the returned `logabsdet` is finite and
correct to the 6.76e-15 shown above. Recorded because it appeared in
`stderr.log` and a reader will see it.

### 2.3 The other instrument checks, all passed before any candidate was judged

| check | result |
|---|---|
| `det(U) = +-1` exactly, `sympy`, `d <= 40`, 12 draws | all `+-1` |
| `T3` entry growth (float64 QR of a badly scaled `UB` is how a `T3` residual can be manufactured) | `max abs U = 2`, `max abs UB = 15740` over 1640 draws — growth is mild, so the `T3` residuals below are not a scaling artifact |
| `X9` pipeline: Gram-HKZ `r_0` vs an INDEPENDENT basis-LLL + enumeration `lambda_1^2` | **6 / 6 bit-for-bit match** (`L7..L12`) |
| HKZ achievement, verified by independent per-index enumeration | **1530 / 1530 reductions verified HKZ**, max violation `0.0`, 0 non-canonical presentations |
| Gram integrality deviation before rounding | max `1.49e-07`, five orders below the `0.5` abort threshold |
| `OD + V + beta^2/d = beta` | max residual **4.26e-14** over **6765 frames** (tol `1e-10`) |
| non-finite values in `results_am4.json` | **0** |
| reproduction from seeds in a fresh process | 7 / 7 recorded values **BIT-EXACT** |

**PRED-A1 HOLDS in both halves.** Under `T1`, the mean `E_I` over 8 isometry
draws lies within `max(4 SE, 0.02)` of `k/d` at **25 of 25** cells, and the mean
`V` within `max(4 SE, 0.02 E[V]_haar)` of `E[V]_haar = 2 beta (d-beta)/(d(d+2))`
at **25 of 25** cells. The `T1` implementation is therefore not suspect and the
refusals drawn from it stand.

---

## 3. THE AM-4 TRIPLE, APPLIED TO EVERY CANDIDATE — residual per transform

`rho_T(X; B, r) = |X(TB) - X(B)| / max(|X(B)|, s_X)`, dimensionless.
`T0` is the mathematically-identity round trip `B -> B H H^T` through the
identical float64 QR path with the SAME `H` as `T1`, so its residual is the
measured noise floor and nothing else.

Grid actually run: `L1 (100,30)`, `L2 (100,70)`, `L3 (100,50)`, `L4 (140,40)`,
`L5 (140,100)`, `L6 = Z^100` in the identity basis, at `beta` in
`{15,30,35,50,65}` (`d=100`) and `{20,40,45,70,95}` (`d=140`); 8 bases; 8
replicates of each of `H`, the row permutation and `U`. Small-`d` family
`L7..L12` at `beta` in `{d/4, d/2, 3d/4}` for `X9`, `X10`.

| id | X | s_X | n rho | rho_T0 max | rho_T1 med / max | rho_T2 med / max | rho_T3 med / max | G-NUM | G-INV |
|---|---|---|---|---|---|---|---|---|---|
| X1 | `E_I` | 1.0 | 6560 | 6.66e-16 | 3.02e-01 / 7.40e-01 | 1.74e-08 / 6.67e-01 | 1.54e-08 / 6.90e-01 | PASS | **FAIL** |
| X2 | `V` | E[V]_haar | 6560 | 8.82e-13 | 9.64e-01 / 9.87e-01 | 2.58e-01 / 1.03e+01 | 1.67e-01 / 7.26e+00 | PASS | **FAIL** |
| X3 | `m3` | E[V]_haar^1.5 | 6560 | 6.54e-12 | 9.97e-01 / 1.04e+00 | 1.99e+00 / 8.90e+01 | 1.29e+00 / 5.79e+01 | PASS | **FAIL** |
| X4 | `D` | 0.01 | 288 | 6.20e-11 | 1.01e+00 / 1.10e+00 | 5.19e-02 / 2.63e-01 | 4.41e-02 / 2.25e-01 | PASS | **FAIL** |
| X5 | `W` | sqrt(k 2b(d-b)/(d^2(d+2))) | 6560 | 1.87e-15 | 1.00e+00 / 1.12e+00 | 5.27e-08 / 1.33e+00 | 4.70e-08 / 1.38e+00 | PASS | **FAIL** |
| X6 | `OD` | E[V]_haar | 6560 | 4.98e-13 | 1.05e+00 / 7.01e+01 | 2.77e-01 / 2.23e+00 | 1.73e-01 / 1.84e+01 | PASS | **FAIL** |
| X7 | `TRIV` | beta | 6560 | 9.47e-16 | 1.78e-16 / 1.07e-15 | 1.78e-16 / 1.30e-15 | 1.78e-16 / 1.18e-15 | PASS | PASS |
| X8 | `rdet` | 1.0 | 6560 | 1.22e-13 | 3.19e-14 / 2.51e-13 | 0.00e+00 / 0.00e+00 | 0.00e+00 / 9.73e-16 | PASS | PASS |
| X9 | `lam1n` | 1.0 | 4449 | 0.00e+00 | 0.00e+00 / 0.00e+00 | 0.00e+00 / 4.51e-15 | 0.00e+00 / 7.15e-15 | PASS | PASS |
| X10 | `hkz` | 1.0 | 4449 | 0.00e+00 | 0.00e+00 / 0.00e+00 | 0.00e+00 / 1.20e-14 | 0.00e+00 / 9.99e-15 | PASS | PASS |

`tau_num = 1e-6`, `tau_inv = 0.01`. Full min / median / max distributions per
lattice, per `beta`, per transform are in
`results_am4.json -> invariance_residuals`.

**Detection floors, stated as the prereg requires.** Every non-firing arm is an
upper bound at a declared floor, never an absence. For `X7`: *`tr(P^2)` is
invariant under `T1, T2, T3` to within `1.30e-15` of its scale `s_X = beta`, at
8 bases and 8 replicates on 6 lattices, 6560 residual samples.* For `X8`: *to
within `2.51e-13` of scale, same coverage.* For `X9`: *to within `7.15e-15` of
scale, 4449 samples.* For `X10`: *to within `1.20e-14` of scale, 4449 samples.*
For `X7`'s `q`-sensitivity: *`tr(P^2)` distinguishes `q = 3329` from `q = 1` by
at most `3.55e-16` of scale.*

### 3.1 An observation that differs from the quoted AM4-OBS-1 table, recorded as such

AM4-OBS-1's single-session table reports `E_I` as "passes here" under row
permutation and under `B -> UB`, at `(d, beta, k) = (100, 40, 50)` **[quoted:
red_team_report.md section 4]**. This run measures `E_I` moving by up to
**0.667** under `T2` and **0.690** under `T3`. The two are not in conflict: at
`beta <= k` the frozen construction pins `E_I` at its ceiling `min(1, k/beta) =
1`, where a lattice-preserving re-presentation cannot move it, and `(100,40,50)`
is such a cell. This run's grid includes cells with `beta > k` (`beta` = 50, 65
at `k` = 30; `beta` = 70, 95 at `k` = 40), where `E_I` is not pinned — and there
it moves under all three transforms. The median `rho_T2` and `rho_T3` for `E_I`
are `~1.7e-08`, i.e. **half the grid is the pinned regime and half is not**, and
the maximum comes from the unpinned half. Reported as an observation; no
adjudication of AM4-OBS-1's scope is offered here.

Similarly, `D` under `T2` was quoted at `13.3%`; this run measures up to
**26.3%** under `T2` and **22.5%** under `T3`, over 288 residual samples.

---

## 4. THE DIAGONAL-COLLISION PROBE — AM4-OBS-1 was TESTED, not assumed

### 4.1 The probe object, verified before it was used

Frozen construction (prereg 2.4), at `d = 100`, `k = 50`, `beta = 40`: a
two-level frame on `2 beta = 80` coordinates paired `(a_m, b_m) = (2m, 2m+1)`
with diagonal `(u, 1-u)`, `u in {0.25, 0.75}` on `beta/2` pairs each; `P2` is
the same construction with the `a`-indices cyclically permuted **within each
`u`-level set**, so that the multiset of diagonal entries AND their coordinate
positions are unchanged.

```
sigma is the identity                     : False
orthonormality |V^T V - I|  P1 / P2       : 1.11e-16 / 1.11e-16
rank P1 / rank P2                         : 40 / 40
max |diag(P1) - diag(P2)|                 : 0.0            <- EXACT collision
max |P1 - P2|      (off-diagonal)         : 0.4330127019   <- genuinely different projectors
```

### 4.2 Per-candidate result, by the frozen decision rule of prereg 2.4

`coll(X) <= tau_num` -> diagonal-determined; `coll(X) > tau_inv` -> **NOT** a
function of `diag` alone, AM4-OBS-1's premise REFUTED for `X`; otherwise
INDETERMINATE at the probe's resolution.

| id | X | `X(P1)` | `X(P2)` | `coll` | verdict by the frozen rule |
|---|---|---|---|---|---|
| X1 | `E_I` | 0.625 | 0.625 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X2 | `V` | 9.000000000 | 9.000000000 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X3 | `m3` | 0.300000000 | 0.300000000 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X5 | `W` | 5.0 | 5.0 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X6 | `OD` | 15.00000000 | 15.00000000 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X7 | `TRIV` | 40.00000000 | 40.00000000 | **0.000e+00** | DIAGONAL-DETERMINED — premise holds |
| X4 | `D` at `L3` | pools 0.032368 / 0.029439 / 0.034682 | pools 0.025252 / 0.027511 / 0.028445 | **0.15837** | **NOT a function of diag alone — premise REFUTED for X4** |
| X4 | `D` at `L4` | pools 0.031916 / 0.030080 / 0.031683 | pools 0.034672 / 0.030741 / 0.031495 | **0.03447** | **NOT a function of diag alone — premise REFUTED for X4** |

`X8`, `X9`, `X10` are NOT APPLICABLE to this probe: it produces a projector, and
those three are not functions of a projector at all. Their class is settled by
measurement in section 5.

### 4.3 `X4 = D` read against its own floor, as prereg 2.4 directs

Prereg 2.4 directs that `D`'s probe outcome be read against the pooled SE of `D`
and reported as an UPPER BOUND **when it falls below that floor**. It does not
fall below the floor at either cell:

| cell | `coll(D)` | pooled-SE floor in `rho` units | above the floor? |
|---|---|---|---|
| `L3` `(100,50)` `beta=40` | **0.15837** | 0.021137 | **yes, 7.5x** |
| `L4` `(140,40)` `beta=45` | **0.03447** | 0.026745 | **yes, 1.29x** |

The upper-bound wording therefore does not apply. Stated plainly: **on this
probe, two projectors with identical diagonals gave `D` values separated by
15.8% and 3.4% of `D`'s declared scale, both above `D`'s own pooled SE floor,
so `D` is measured NOT to be a function of `diag(QQ^T)`.**

### 4.4 What this does and does not do to the `R4` row

Both prereg 2.4 and prereg 2.7 restrict `R4`'s premise clause to
`X1, X2, X3, X5` — `X4` is deliberately excluded from the trigger, and 2.4 says
why (its outcome is to be read against `D`'s own SE floor rather than used as a
trigger). Applying the map exactly:

* **`R4` did NOT fire.** Premise clause: `coll = 0.000e+00` for `X1, X2, X3,
  X5`, so no trigger. Measured-conclusion clause: no candidate among
  `X1..X5` has `rho_T1 <= tau_inv` at every replicate — the minimum `rho_T1`
  maxima are `0.740, 0.987, 1.04, 1.10, 1.12` respectively, all far above
  `tau_inv = 0.01` — so no trigger.
* **The per-candidate verdict of 2.4 for `X4 = D` is nevertheless "premise
  REFUTED"**, at both cells, above the floor at both. AM4-OBS-1's statement
  explicitly names `D` as one of the observables that "are functions of the
  diagonal of the tail-frame projector in the standard coordinate basis"
  **[quoted: `EV-MLKEM-cd9878` named_finding AM4-OBS-1 statement]**. That
  specific clause is contradicted by this measurement.

**A limitation of the probe that must be recorded with its result.** For
`X1, X2, X3, X5, X6, X7` the probe returned `coll = 0.000e+00` — exactly zero,
not merely small. That is because those six are manifest closed-form functions of
`diag(P)` by their own definitions (`E_I`, `V`, `m3`, `W` are explicit functions
of `diag(P)`; `TRIV = beta` identically; `OD = beta - V - beta^2/d` by the
identity verified in 6.2). The probe **could not have refuted** the premise for
them; their `coll = 0` is arithmetic, not discovery. Among the ten frozen
candidates, the only one on which AM4-OBS-1's premise had content that the probe
could test was `X4 = D` — and there the probe separated. This is stated so that a
reader does not read six exact zeros as six independent corroborations.

**Consequence for `D`'s refusal: none.** `D` fails `G-INV` at `1.10` under `T1`,
`0.263` under `T2` and `0.225` under `T3` regardless. What the probe changes is
the proposed *mechanism* for the failure, not the failure.

---

## 5. PROBE-L — the SUPPLEMENTARY frame-collision (NOT pre-registered)

`GEN-2` requires each candidate's class to be decided **by measurement rather
than by assertion**, and the frozen probe is undefined on `X8, X9, X10`. PROBE-L
supplies the measurement and is labelled SUPPLEMENTARY throughout; it does not
replace the frozen probe, which was run exactly as specified.

Construction: `B' = diag(3,...,3,1,...,1) B` scales rows `1..d-beta` only. That
leaves `span(rows 1..d-beta)` unchanged, hence leaves the tail-`beta` frame
EXACTLY unchanged, while making `L(B')` a proper sublattice of `L(B)`. Measured
at `d = 40, k = 12, beta = 30`; `max |P - P'| = 7.77e-16`, i.e. the frames did
collide.

| id | X | `X(B)` | `X(B')` | `collL` | class, decided by measurement |
|---|---|---|---|---|---|
| X1 | `E_I` | 0.3999999843 | 0.3999999843 | 0.00e+00 | `f(P)` |
| X2 | `V` | 1.2454261170 | 1.2454261170 | 2.85e-15 | `f(P)` |
| X3 | `m3` | 0.0941842777 | 0.0941842777 | 1.95e-16 | `f(P)` |
| X5 | `W` | 2.9999995301 | 2.9999995301 | 0.00e+00 | `f(P)` |
| X6 | `OD` | 6.2545738830 | 6.2545738830 | 5.68e-16 | `f(P)` |
| X7 | `TRIV` | 30.0 | 30.0 | 0.00e+00 | `f(P)` |
| X8 | `rdet` | — | — | **3.16e-01** | **NOT `f(P)`** — separates two lattices with the identical tail frame |
| X9 | `lam1n` | — | — | **3.22e-02** | **NOT `f(P)`** |
| X10 | `hkz` | — | — | **4.26e-04** | **NOT `f(P)`**, but only 426x above `tau_num` and 23x BELOW `tau_inv` — the weakest of the three separations, recorded as such |

---

## 6. THE TWO CLOSED-FORM ARGUMENTS — TESTED, not assumed

### 6.1 OBS-GEN, stated in full as `GEN-1` requires

> Let `f` be any function of the tail-frame projector `P` alone with
> `f(H^T P H) = f(P)` for every orthogonal `H`. Every rank-`beta` orthogonal
> projector in `R^d` is conjugate to every other by some orthogonal `H`, so `f`
> is constant on that entire set: `f = f(d, beta)`. Hence **no function of the
> tail-`beta` frame alone can be both AM-4-invariant under `T1` and informative
> about anything.** `X7 = tr(P^2) = beta` is not an arbitrary control: it is the
> canonical representative of the whole class that passes `T1`, which is exactly
> why the gate needs the `q`-sensitivity criterion as well as the invariance
> criterion.

This is elementary and a reader can check it by hand. It is **not** a
machine-checked proof and is not claimed as one. Its numerical corollaries were
verified by the run and all hold — `X7` invariant to `1.30e-15` (2.1);
`OD + V + beta^2/d = beta` to `4.26e-14` over 6765 frames (6.2); every
`f(P)`-class candidate fails `G-INV` or `G-Q` (section 3 and 7).

### 6.2 The projector identity that kills the "use the off-diagonal instead" repair

`P^2 = P` gives `sum_{a!=b} P_ab^2 = beta - V - beta^2/d`, so
`X6 = OD` is an **exact affine function of `V`**. Verified at **every one of the
6765 frames** built by this run, max residual `4.26e-14`, tolerance `1e-10`.
The measured behaviour follows: `OD` fails `G-INV` at `70.1` under `T1`,
alongside `V`'s `0.987`. The naive off-diagonal repair is dead by algebra, and
the run confirms the algebra rather than discovering the death.

---

## 7. GEN-1, GEN-2, GEN-3 — each addressed explicitly

These are reported because a successor needs them, even though `R3` fired before
`R2` and therefore no obstruction is being archived by this run.

**GEN-1 STRUCTURAL — HOLDS.**
* OBS-GEN stated in full: yes, section 6.1.
* `X7 = tr(P^2)` invariant under `T1, T2, T3` to `<= tau_num`: **yes**, `1.30e-15`.
* `OD + V + beta^2/d = beta` to `<= 1e-10`: **yes**, `4.26e-14` over 6765 frames.
* **every** `f(P)`-class candidate fails `G-INV` or `G-Q`, residual reported:
  **yes** — `E_I`, `V`, `m3`, `W`, `OD` fail `G-INV` (0.740, 10.3, 89.0, 1.38,
  70.1); `TRIV` passes `G-INV` and fails `G-Q` (3.55e-16). Six of six.

**GEN-2 COVERAGE — HOLDS under the arm-level reading; FAILS under the strict
reading of 1.1.** `>= 3` `f(P)`-class scored: **6** (`E_I, V, m3, W, OD, TRIV`).
`>= 2` non-`f(P)`-class scored: **3** (`rdet, lam1n, hkz`) under the arm-level
reading, **1** (`rdet`) under the strict reading. Class was decided by
measurement — the frozen collision probe for the `f(P)` six, PROBE-L for the
other three — and not by assertion, as `GEN-2` requires.

**GEN-3 SCOPE — HOLDS.** Any claim from this run is stated only over
observables that are functions of the tail-`beta` frame projector alone, at the
tested `(d, k, beta, q)` grid, at `n = 8` bases and 8 replicates. **It is NOT a
theorem that no admissible statistic exists.** The two repairs that remain open
are carried verbatim from the prereg:
1. weaken AM-4 to the basis-change subgroup `{T2, T3}` only, retaining the
   standard coordinate frame, under which the spill question is well posed and
   the goal's existing observables are candidates again; or
2. restate the target question in isometry-invariant terms (for example about the
   GSO profile of a canonical reduction, `X10`), which is a **DIFFERENT
   question** and must be labelled as one.

Forward guidance this run adds, from its own numbers: repair (2) is now known to
be *reachable* — `X10` is admissible, at machine precision, with verified-HKZ
canonicality — and known to be *insufficient as posed*, because `X10` fails
`REL-2`, the block-attribution clause, at every mirrored pair (section 8.3).

---

## 8. THE SWEEPS, per observable

### 8.1 `q`-sweep DOWN TO `q = 1`, frozen construction

`q in {1, 2, 4, 16, 64, 256, 1009, 3329}` at fixed `(d, k, beta)` and fixed
seeds. Under the frozen construction of prereg 2.9,
`A = default_rng([1,d,k,i]).integers(0, q)`, so at `q = 1` we have `A = 0` and
the basis is exactly `I_d`: `Z^d` in its identity basis, an object with no
`q`-ary structure that no spill mechanism can be about.

`L1 (d=100, k=30)`:

| X | beta | q=1 | q=2 | q=4 | q=16 | q=64 | q=256 | q=1009 | q=3329 |
|---|---|---|---|---|---|---|---|---|---|
| `E_I` | 15 | 0 | 0.82615 | 0.95392 | 0.99686 | 0.99981 | 0.99999 | 1 | 1 |
| `E_I` | 35 | 0 | 0.65496 | 0.78162 | 0.85050 | 0.85671 | 0.85712 | 0.85714 | 0.85714 |
| `E_I` | 65 | 0 | 0.41690 | 0.45196 | 0.46095 | 0.46150 | 0.46154 | 0.46154 | 0.46154 |
| `V` | 30 | 21 | 8.4793 | 13.652 | 19.612 | 20.894 | 20.993 | 21.000 | 21.000 |
| `m3` | 30 | 8.4 | 0.86921 | 3.9919 | 7.5722 | 8.3366 | 8.3956 | 8.3997 | 8.400 |
| `W` | 30 | -9 | 11.922 | 16.627 | 20.283 | 20.947 | 20.996 | 21.000 | 21.000 |
| `OD` | 30 | 0 | 12.521 | 7.3483 | 1.3881 | 0.10573 | 0.007305 | 4.69e-4 | 4.31e-5 |
| `TRIV` | any | beta | beta | beta | beta | beta | beta | beta | beta |
| `rdet` | any | 1 | 1.6245 | 2.6390 | 6.9644 | 18.379 | 48.503 | 126.68 | 292.16 |

`L11 (d=40, k=12)`, the small-`d` sweep cell for `X9`, `X10`:

| X | beta | q=1 | q=2 | q=4 | q=16 | q=64 | q=256 | q=1009 | q=3329 |
|---|---|---|---|---|---|---|---|---|---|
| `lam1n` | any | 1 | 1.2311 | 1.5157 | 1.6245 | 1.6919 | 1.6725 | 1.6951 | 1.6105 |
| `hkz` | 10 | 0 | -0.31192 | -0.40094 | -0.42495 | -0.43747 | -0.42947 | -0.45653 | -0.42474 |
| `hkz` | 20 | 0 | -0.19062 | -0.26916 | -0.28776 | -0.28052 | -0.28709 | -0.28382 | -0.27222 |
| `hkz` | 30 | 0 | -0.069315 | -0.12794 | -0.13624 | -0.13955 | -0.13890 | -0.13937 | -0.13095 |

`D` (`X4`), pool-averaged over `E = 3` pools at basis `i = 0`:

| cell | q=1 | q=2 | q=4 | q=16 | q=64 | q=256 | q=1009 | q=3329 |
|---|---|---|---|---|---|---|---|---|
| `L3` beta=40 | 0.08543 | 0.02237 | 0.03938 | 0.05429 | 0.05671 | 0.05616 | 0.05617 | 0.05613 |
| `L4` beta=45 | 0.08062 | 0.03567 | 0.05130 | 0.06775 | 0.06929 | 0.06923 | 0.06927 | 0.06940 |

`G-Q = |X(3329) - X(1)| / max(|X(3329)|, s_X)`, maximum over cells,
`tau_q = 0.10`:

| id | X | G-Q | verdict |
|---|---|---|---|
| X1 | `E_I` | 1.000e+00 | PASS |
| X2 | `V` | 3.004e+00 | PASS |
| X3 | `m3` | 2.609e+01 | PASS |
| X4 | `D` | 5.219e-01 | PASS |
| X5 | `W` | 3.111e+00 | PASS |
| X6 | `OD` | 1.000e+00 | PASS |
| X7 | `TRIV` | 3.553e-16 | **REFUSED** |
| X8 | `rdet` | 9.970e-01 | PASS |
| X9 | `lam1n` | 3.791e-01 | PASS |
| X10 | `hkz` | 4.247e-01 | PASS |

**PRED-A5** predicted the `E_I` `q`-ladder monotone in `q` with `1 - E_I ~ q^-2`.
On the frozen construction, in the `beta <= k` regime, `1 - E_I` at `L1 beta=15`
runs `4.6085e-2, 3.1354e-3, 1.9067e-4, 1.1981e-5, 7.7254e-7, 7.0947e-8` at
`q = 4, 16, 64, 256, 1009, 3329`: successive ratios **14.70x, 16.44x, 15.91x**
and `256 -> 3329` **168.9x** against `(3329/256)^2 = 169.1`. The `q^-2` law is
reproduced. The ladder is monotone in `q` at every `beta` of `L1` and `L4`.
**PRED-A5 holds** on the frozen construction.

**SUPPLEMENTARY `q`-ladder B — POST-HOC, UNCITABLE AS A RESULT** (prereg section
5 rule 6). Holding `A` at its `q = 3329` draw and scaling only the lower block by
`q` makes `q = 1` into `Z^d` in a NON-identity basis. Under that construction
`1 - E_I` is **bit-for-bit constant across the entire ladder including `q = 1`**
(`7.0947e-08` at `L1 beta=15` at every `q`; `5.3846e-01` at `L1 beta=65` at every
`q`), reproducing the BATCH-a44d08 red team's observation exactly — and under
that reading `E_I` would FAIL `G-Q`. The two readings disagree about `E_I`'s
`G-Q` verdict. The frozen reading is the one scored; the alternative is recorded
for forward guidance and may not be cited as a result of this batch.

### 8.2 Rank sweep — and a DEFECT IN THE FROZEN CONSTRUCTION, recorded

The frozen construction (prereg 2.9) is `A = A1 @ A2 mod q` with inner dimension
`r`. The run recorded the **realized** rank, which is what caught the problem:

| requested `r` | 1 | 5 | 10 | 20 | k |
|---|---|---|---|---|---|
| `(100,30)` rank over **R** | 30 | 30 | 30 | 30 | 30 |
| `(100,30)` rank over **F_3329** | 1 | 5 | 10 | 20 | 30 |
| `(140,40)` rank over **R** | 40 | 40 | 40 | 40 | 40 |
| `(140,40)` rank over **F_3329** | 1 | 5 | 10 | 20 | 40 |
| `(40,12)` rank over **R** | 12 | 12 | 12 | 12 | 12 |
| `(40,12)` rank over **F_3329** | 1 | 5 | 10 | 12 | 12 |

**The `mod q` in prereg 2.9 forces the rank exactly over `F_q` and leaves it at
full `k` over `R`.** Prereg 2.1 says the rank is "forced exactly"; prereg 2.9
gives the `mod q` formula. The two are not consistent, because the closed form
that the rank sweep exists to probe — `E_I = min(rank(A_S), beta)/beta + O(q^-2)`
**[quoted: red_team_report.md section 1.3]** — depends on the singular values of
`A_S` over `R`, not on its rank over `F_q`.

**Objection recorded, frozen specification run anyway** (prereg section 5 rule
5). The measured consequence:

| rank `r` | `E_I` at beta = 1 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 50 | 65 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9999 | 0.8571 | 0.6000 | 0.4615 |
| 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9999 | 0.8571 | 0.6000 | 0.4615 |
| 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8571 | 0.6000 | 0.4615 |
| 20 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8571 | 0.6000 | 0.4615 |
| 30 (=k) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8571 | 0.6000 | 0.4615 |

`E_I` is identical along the whole ladder, which is exactly what
`min(rank_R(A_S), beta)/beta` predicts when `rank_R(A_S)` does not move. `V`,
`m3`, `W`, `OD`, `rdet`, `D`, `lam1n`, `hkz` ladders are in the JSON; `D` is flat
to within `0.0537-0.0545` at `L3` and `0.0670-0.0693` at `L4`; `rdet` is exactly
constant, as `|det B| = q^{d-k}` requires.

**Therefore `G-RANK` is NOT ADJUDICATED for any candidate.** Its criterion asks
whether `b*(X)` tracks `min(rank(A_S), beta)` rather than `min(k, beta)`; under
the frozen construction `rank_R(A_S) = min(k, beta, d-k)` at every rung, so the
two candidate laws coincide and the criterion cannot discriminate. This is an
instrument limitation of the frozen text, **never a refusal and never a clearance
of any candidate**. In particular the one apparent "REFUSED as a block-content
adjudicator" verdict the script's mechanical rule emitted — `E_I` at `L4`, with
`b* = 28` at `r = 1` against `b* = 41` at every other rung — **must not be read
as a refusal**: with `rank_R(A)` identical across the ladder, that difference is
a different random draw of `A` (the rank-variant seed includes `r`), not a rank
effect. The mechanical verdicts are left in the JSON unaltered and are
superseded by this paragraph.

A successor wanting `G-RANK` should amend the construction to `A = A1 @ A2`
**without** the `mod q` reduction, which forces the rank over `R`, and re-run;
that is an amendment request for the Coordinator, not a change made here.

### 8.3 `G-REL` — the two relevance clauses

`REL-1` beta-dependence at `(15,65)` for `d=100`, `(20,95)` for `d=140`, and at
the endpoints of the declared small-`d` grid for `X9`, `X10` (see 9.1).
`REL-2` block attribution on the mirrored cell pairs `L1/L2`, `L4/L5`,
`L7/L8`, `L9/L10`, `L11/L12`. `tau_rel = 0.10`; both clauses required.

| id | X | REL-1 | REL-2 | G-REL | overall verdict |
|---|---|---|---|---|---|
| X1 | `E_I` | 0.5789 PASS | 0.5789 PASS | PASS | REFUSED (fails `G-INV`) |
| X2 | `V` | 18.9659 PASS | 2.4393 PASS | PASS | REFUSED (fails `G-INV`) |
| X3 | `m3` | 85.1826 PASS | 24.2692 PASS | PASS | REFUSED (fails `G-INV`) |
| X4 | `D` | not measured | not measured | FAIL | REFUSED (fails `G-INV`) |
| X5 | `W` | 3.7500 PASS | 1.1111 PASS | PASS | REFUSED (fails `G-INV`) |
| X6 | `OD` | 1.3584 PASS | 58.8921 PASS | PASS | REFUSED (fails `G-INV`) |
| X7 | `TRIV` | 3.7500 PASS | 0.0000 FAIL | FAIL | REFUSED (laxity control, fails `G-Q`) |
| X8 | `rdet` | **0.0000 FAIL** | 0.9691 PASS | FAIL | **R3 admissible, not relevant** |
| X9 | `lam1n` | **0.0000 FAIL** | 0.0784 FAIL | FAIL | **R3 admissible, not relevant** |
| X10 | `hkz` | 0.3095 PASS | **0.0697 FAIL** | FAIL | **R3 admissible, not relevant** |

`X4 = D`'s `G-REL` is NOT MEASURED, not failed: the frozen D arm runs at one
`beta` per cell (`L3` `beta=40`, `L4` `beta=45`) and at two cells that are not a
mirrored pair, so neither clause has the two points it needs. `D` is refused on
`G-INV` regardless.

`X8` and `X9` fail `REL-1` at exactly `0.0000` because `|det B|^{1/d}` and
`lambda_1/|det B|^{1/d}` do not depend on `beta` at all — the prereg recorded
this expectation in advance and it is confirmed.

**`X10 = hkz` is the interesting one, and it is the reason `R3` rather than
`R1`.** It passes `REL-1` at `0.3095` and fails `REL-2` at every mirrored pair:

| pair | d | beta | `X(d,k,beta)` | `X(d,d-k,beta)` | REL-2 |
|---|---|---|---|---|---|
| L7/L8 | 20 | 5 | -0.172674 | -0.242366 | 0.06969 |
| L7/L8 | 20 | 10 | -0.127351 | -0.144102 | 0.01675 |
| L7/L8 | 20 | 15 | -0.066051 | -0.068709 | 0.00266 |
| L9/L10 | 30 | 7 | -0.333412 | -0.346097 | 0.01269 |
| L9/L10 | 30 | 15 | -0.214071 | -0.227973 | 0.01390 |
| L9/L10 | 30 | 22 | -0.112492 | -0.115878 | 0.00339 |
| L11/L12 | 40 | 10 | -0.424737 | -0.446194 | 0.02146 |
| L11/L12 | 40 | 20 | -0.272217 | -0.278794 | 0.00658 |
| L11/L12 | 40 | 30 | -0.130951 | -0.136665 | 0.00571 |

Maximum `0.0697`, at the smallest `d` on the grid, against `tau_rel = 0.10`.
Detection floor, stated as required: **`X10` distinguishes the mirrored cell pair
`(d,k)` from `(d,d-k)` by at most `0.0697` of scale, at `d in {20,30,40}`,
`beta in {d/4, d/2, 3d/4}`, on 1 basis per cell.** `X9` likewise: at most
`0.0784` of scale, same coverage.

---

## 9. DEVIATIONS, INTERPRETATIONS AND ADDITIONS — all recorded

All were declared in the script **before any result was computed** and are in
`results_am4.json -> deviations` (10 entries).

1. **INTERPRETATION — REL-1 endpoints at small `d`.** Prereg 2.5 pins REL-1
   endpoints only for `d = 100` and `d = 140`. `X9`/`X10` are "small `d` only"
   (2.3) on `L7..L12`, whose `beta` grid is `{d/4, d/2, 3d/4}` (2.9). REL-1 for
   those candidates is taken at the endpoints of that declared grid,
   `(d/4, 3d/4)`. The full ladder is in the JSON so a reviewer may rescore.
2. **INTERPRETATION — `L6`'s `k`.** `L6 = Z^100` in the identity basis carries no
   `k` in 2.9, but `E_I` and `W` need `K_I`. `k = 50` (`= d/2`, `L3`'s value) was
   used. Disclosed rather than silently chosen.
3. **INTERPRETATION — the `q = 1` basis.** The frozen 2.9 formula gives `A = 0`
   at `q = 1`, so the `q = 1` basis is exactly `I_d`. Ladder B is reported
   separately, labelled POST-HOC and uncitable (8.1).
4. **ADDITION — PROBE-L** (section 5), labelled SUPPLEMENTARY.
5. **DISCLOSURE — the Gram pipeline for `X9`/`X10`.** They are computed through
   the integer Gram matrix `G = M M^T` (`fpylll GSO.Mat(gram=True)`), the only
   route this environment offers for a non-integer presentation. `G` is exactly
   preserved by an ambient isometry in exact arithmetic, so **the `T0` and `T1`
   residuals for `X9`/`X10` are structurally near-zero and measure only
   Gram-formation float noise — they are a WEAK test and must not be read as an
   independent geometric one.** The `T2` and `T3` residuals ARE genuine: the Gram
   matrix genuinely changes (`Pi G Pi^T`, `U G U^T`) and the reduction must
   recover the same invariant from a different starting basis. Pre-rounding
   integrality deviation is reported per presentation; max `1.49e-07`.
6. **DISCLOSURE — the HKZ reduction had to be repaired to be HKZ.** fpylll's
   `BKZReduction.svp_call` discards any improvement not better than
   `lll_delta = 0.99 * r_i`, so `BKZ(block_size = d)` alone does **not** reach
   HKZ: violations up to `7.6e-3` were measured at `d = 30` before the repair.
   The run therefore adds explicit HKZ sweeps and then **verifies** every
   reduction by an independent per-index enumeration. Result: **1530/1530
   reductions verified HKZ, max violation `0.0`, 0 non-canonical presentations**,
   so the prereg 2.9 step-4 fallback (label the arm NON-CANONICAL and treat the
   `T3` residual as uninformative) did not have to be invoked for any pair. This
   matters: with the unrepaired reducer, `X10` showed a spurious `T3` residual of
   `1.7e-2` — it would have been REFUSED by `G-INV` as a pure reducer artifact.
7. **DISCLOSURE — `beta` in the `X9`/`X10` transform seed.** The HKZ-reduced
   basis does not depend on `beta` (only the readout window does), so one
   reduction per presentation serves every `beta` and the transform seed uses
   `beta = d/2` for those arms.
8. **DISCLOSURE — rank-variant seed.** `default_rng([1,d,k,i,r])`; 2.9 pins TAG 1
   for "the basis matrix `A` (and its rank-`r` factors)" and gives only the
   un-ranked form explicitly, so `r` is appended.
9. **ADDITION — finer rank-sweep `beta` grid**, `beta = 1..min(k+5, d-k)`, beside
   the frozen grid, because `b*(X)` is resolved only to the grid it is read on.
10. **OBJECTION recorded, frozen specification run anyway** — the `mod q` in the
    rank construction (8.2), and `numpy.linalg.slogdet`'s internal warnings
    (2.2).

### 9.1 Wording-ban compliance

The frozen ban on "absent", "no departure", "vanishes", "consistent with zero"
and synonyms applied to a measured arm without its floor was applied to this
report, to `results_am4.json` and to `measure_am4.py`. Every non-firing arm above
is stated as an upper bound with its floor printed.

---

## 10. WHAT THIS RUN DOES NOT REACH

It measured the behaviour of ten observables under three lattice-preserving
transforms, two sweeps and two collision probes, on explicitly constructed q-ary
bases and `Z^d`, at `d in {20,30,40,100,140}`, `q <= 3329`, `n = 8` bases and 8
replicates. It adjudicates **nothing** about which spill mechanism is correct,
nothing about reduction, nothing about the `2^-10` tail law, and nothing about
ML-KEM.

* The M-K / M-D question remains where `DEC-20260806-607779` left it: **NOT
  DECIDED, and not decidable by `E_I`.**
* AM-3 is not retired and is not touched here.
* Section C's proposition — whether `D` depends on the frame only through `V` at
  the `2^-10` quantile — stays OPEN IN BOTH DIRECTIONS and is not addressed here.
* `R3` is not an obstruction archived. `R2` was not reached, so **no claim that
  "no admissible predicate exists" is made by this run**, and none may be cited
  from it. What is reported is narrower and firmer: three observables are
  admissible under the frozen gate, and none of them is relevant under the frozen
  relevance criterion.
* `G-RANK` is NOT ADJUDICATED (8.2). No block-content refusal or clearance may be
  cited from this run for any candidate.
* Every `f(P)`-class refusal is scoped to the tested grid and is an upper bound at
  the floors printed in section 3.

## 11. AM-4's ledger after this run, stated as observation only

AM-4 had refused five statistics before this run (P3, `V`, `E_I`, `m3`, `D`).
This run, under a pre-registered gate rather than a post-hoc criterion, and at
6560 residual samples per `f(P)` candidate rather than one session, records:
`E_I`, `V`, `m3`, `D`, `W`, `OD` REFUSED on `G-INV`; `TRIV` REFUSED on `G-Q` as
designed; `rdet`, `lam1n`, `hkz` ADMISSIBLE and NOT RELEVANT. Whether that
constitutes support for, or refutation of, AM4-OBS-1 or of any heuristic is a
judgement for the Reviewer and the Coordinator. This report records observations
and applies the frozen map; it draws no such conclusion.
