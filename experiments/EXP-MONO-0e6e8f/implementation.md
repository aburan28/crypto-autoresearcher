# EXP-MONO-0e6e8f — implementation notes

Unconditioned five-class Chebotarev census of the m=4 symmetric-base Semaev
cover. Executed under `TASK-20260904-09b094` against the frozen, approved
contract `experiments/EXP-MONO-0e6e8f/specification.yaml`
(sha256 `a028c8bb749097e9adb3421a28c0d632adde51e6772a528cc18a261e4134c107`,
`status: approved`, `frozen: true`, `execution_authorized: true`,
`approved_by: coordinator`).

Single artifact:
`experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`.
Single run: `runs/RUN-MONO-0e6e8f-1/`.

---

## 1. What is new here and what is reused

**Nothing about the Q_e(T) construction is new.** `run_uncond_census.py`
inserts `experiments/EXP-MONO-815525/implementation/` on `sys.path` and does
`import run_census as RC`, then uses that module's already
independently-validated and red-teamed primitives unmodified:

| reused from EXP-MONO-815525 | purpose |
| --- | --- |
| `compile_s4`, `compile_s3`, `compile_sym` | specialise the derived monomial tables to (p, A, B) |
| `qe_from_sym` | symmetric-base Q_e(T) — the Stage-1 fast path |
| `qe_from_ordered` | ordered-base S_4 path (Stage-0 cross-check) |
| `qe_from_resultant` | runtime Sylvester elimination from S_3 (Stage-0 cross-check) |
| `F3`, `pt_add`, `pt_neg`, `points_with_x`, `curve_order`, `j_invariant` | F_{p^3} and curve arithmetic |
| `factor_pattern` (Yun + distinct-degree), `pgcd`, `pdivmod`, `pmul`, `pnorm`, `pdeg`, `pderiv`, `to_fp`, `is_irreducible_cubic` | the F_p[T] toolkit |
| `s4_monomials.json`, `s3_monomials.json`, `s4_symmetric_coeffs.json`, `derivation_checks.json` | the derived polynomial data |

The **only new content is the sampling design**, exactly as the contract
states, plus a resultant routine and a five-class labeller.

### `derive_s4.py` was deliberately NOT executed

Importing or running `derive_s4.py` re-runs the sympy derivation **and
rewrites six files inside `experiments/EXP-MONO-815525/implementation/`**
(`s4_monomials.json`, `s3_monomials.json`, `s4_symmetric_coeffs.json`,
`derivation_checks.json`, `S4_expanded.txt`, `Qe_coeff_c*.txt`). Both the task
card ("read-only — do not copy or modify") and the write-scope constraint
("stay strictly inside `experiments/EXP-MONO-0e6e8f/`") forbid that. It is
read by path, sha256'd, and its symbolic claims are re-verified at run time by
other means — see Stage 0 checks (0a)/(0a2) below, which recompute them from
the stored term table without sympy and without trusting
`derivation_checks.json`.

---

## 2. The design correction relative to EXP-MONO-815525

EXP-MONO-815525 conditioned every Stage-1 draw on "`g` is irreducible over
F_p". Its red-team report proved by explicit null-object control that this
conditioning has **zero discriminating power**. This run applies **no filter
whatsoever on `g`'s factorization type**. `g`'s type is *recorded* for every
instance (as descriptive context, and cross-tabulated against the class label)
but is never used to accept or reject a base point.

The sole exclusion is the one the contract names:

```
g(X) = X^3 - e1 X^2 + e2 X - e3      f(X) = X^3 + A X + B
skip iff Res(g, f) == 0
```

`Res` is computed by a **locally written** Euclidean-algorithm resultant with
full leading-coefficient bookkeeping (`resultant()`), which is independent of
`RC.pgcd`. Stage-0 check (0f) cross-checks the two against each other
(`Res == 0` ⟺ `deg gcd(g,f) > 0`) on 2000 random probes per curve; all passed.
`Res(g,f)=0` means `g` and `f` share a root in the algebraic closure, which is
the exact criterion; when `f` is irreducible it degenerates to `g == f`,
matching the task card's description.

Grep discipline: `run_uncond_census.py` contains exactly one `continue`-style
rejection in `census_curve.handle`, on `r == 0`. Any reviewer can confirm
there is no second selection rule on the base point.

---

## 3. Curves and the isogeny disclosure

Two primes in [101, 2000], two curves each, all ordinary, all with
j ∉ {0, 1728}, all nonsingular:

| id | p | A | B | j | #E(F_p) | t | t²−4p | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 101 | 2 | 3 | 74 | 96 | 6 | −368 | exhaustive |
| C2 | 101 | 1 | 35 | 63 | 121 | −19 | −43 | exhaustive |
| C3 | 1009 | 5 | 7 | 459 | 966 | 44 | −2100 | random |
| C4 | 1009 | 2 | 30 | 929 | 1072 | −62 | −192 | random |

Non-isogeny criterion (Tate): two curves over the **same** F_p are isogenous
over F_p iff they have equal group order, equivalently equal trace. Curves
over different primes are over different fields and are not isogenous at all.
The run computes `#E` by an exhaustive Legendre-symbol point count
(`RC.curve_order`) and aborts as `failed_infrastructure` if any declared pair
turns out isogenous.

- C1 vs C2 (same field, p=101): traces 6 vs −19, orders 96 vs 121, CM
  discriminants −368 vs −43. **Not isogenous.**
- C3 vs C4 (same field, p=1009): traces 44 vs −62, orders 966 vs 1072, CM
  discriminants −2100 vs −192. **Not isogenous.**
- All four cross-prime pairs: different fields, not isogenous.

EXP-MONO-815525's disclosed error was that its C1 (p=101, A=2, B=3) and its C5
(p=101, A=37, B=29) both have order 96 / trace 6 and are isogenous. This run
independently re-confirmed that during curve selection and avoided it: C1 here
is EXP-MONO-815525's own C1, but its p=101 partner is a **new** curve
(A=1, B=35, trace −19), not A=37/B=29.

---

## 4. Stage 0 — re-verification of the reused construction

All six checks passed; details and per-instance data are in
`raw-result.json → stage_0`.

| check | what it verifies | result |
| --- | --- | --- |
| (0a) | stored S_4 term table has degree 4 in each of x1..x4 → `[4,4,4,4]` | PASS |
| (0a2) | stored S_4 term table is invariant under all 24 permutations of x1..x4 (540 terms) | PASS |
| (0b) | S_3 vanishes on `x(P ± Q)` computed by ordinary point arithmetic — 30 relations per curve | PASS |
| (0c) | specialised degree law `deg_T Q_e = 4 − #(sign classes summing to O)` on 221 split-g probes | PASS |
| (0d) | Q_e's roots are exactly the finite sign-class sums `x(P1 ± P2 ± P3)`, on the same 221 probes; and the ordered-base path with the three F_p roots embedded as constants reproduces the symmetric-base Q_e | PASS |
| (0e) | on g-irreducible probes (10 per curve): Q_e is invariant under all 6 permutations of the conjugate roots, lands in F_p, and **three mutually independent construction paths agree** (ordered-base S_4 table, symmetric-base Q_e table, runtime Sylvester elimination from S_3) | PASS |
| (0f) | local resultant agrees with `RC.pgcd` degree test, 2000 probes/curve | PASS |

(0a)/(0a2) are the replacement for re-running `derive_s4.py`: they recompute
its two headline symbolic claims directly from the stored table.

The Stage-0 probes in (0e) *do* condition on `g` irreducible — that is
deliberate and harmless: `qe_from_ordered`/`qe_from_resultant` need
F_p[X]/(g) to be a field for the Frobenius-conjugate root triple to be
meaningful. These probes select nothing in Stage 1; Stage 1 draws from a
completely separate part of the stream (and, on C1/C2, from no stream at all).

---

## 5. Stage 1 — the census

- **C1, C2 (p=101):** exhaustive over all 101³ = 1,030,301 triples
  (e1,e2,e3) in lexicographic order. No randomness at all.
- **C3, C4 (p=1009):** 100,000 uniform independent draws from F_p³ each,
  from `random.Random(20260904003)` (the seed the contract's
  `replication.seeds[0]` fixes). Ten times the contract's 10,000 minimum.

For each qualifying base point: build Q_e(T) via `RC.qe_from_sym`, factor it
over F_p via `RC.factor_pattern` (Yun squarefree decomposition + distinct-
degree factorization using `gcd(T^p − T, ·)` and repeated-squaring modular
exponentiation — no CAS), and label it.

### The five-class label, and why the projective reading is primary

The contract's five classes (`1^4`, `2+2`, `2+1+1`, `4`, `3+1`) are the five
partitions of 4. But Q_e's leading coefficient c_4(e1,e2,e3) can vanish — an
anomaly EXP-MONO-815525 itself disclosed — leaving Q_e of degree 3, whose
affine factorization is a partition of 3 and therefore not one of the five.
The fibre of the cover nonetheless always has 4 points in P¹.

So the classifier restores the (4 − deg Q_e) roots at T = ∞ as F_p-rational
fibre points, exactly as EXP-MONO-815525's own `projective_degrees` statistic
did, and labels the resulting partition of 4. **The literal affine pattern and
`deg_T Q_e` are also recorded for every instance** and reported per curve, so
the choice is fully reversible by a reviewer. 20,509 of 2,249,894 pooled
instances (0.91%) had deg Q_e = 3; none had Q_e ≡ 0.

Ramification (`Q_e` not squarefree) is recorded per instance and counted per
class. It is **not** excluded from the pre-registered M3 statistic; a
squarefree-subset chi-square is reported additionally as M3b and explicitly
labelled descriptive.

Storage: per-class, per-affine-pattern, per-degree, per-ramification and joint
(g-type × class) counts are **exact and complete** for all 2,249,894
instances. Full per-instance records are retained for up to 60 instances per
class per curve and up to 400 exclusions per curve — storing all 2.2M would
exceed the 20 MB disk budget by two orders of magnitude. Nothing is dropped
from any count; the accounting identity
`drawn == classified + excluded + identically_zero` holds exactly
(2,260,602 = 2,249,894 + 10,708 + 0), and C1/C2 are exhaustive so their
per-instance data is fully regenerable with no randomness.

---

## 6. Stage 2 — the two results, kept separate

The contract's `invalidation_rules` forbid conflating M1 with M3, so they are
computed and reported as distinct blocks:

- **M3** (frequency match): Pearson chi-square, df = 4, against the frozen
  density (1/24, 1/8, 1/4, 1/4, 1/3), pooled and per curve.
- **M1** (per-subgroup existence): for each transitive subgroup of S_4
  (C_4, V_4, D_4, A_4, S_4), the set of cycle types it *cannot* realise, and
  whether any observed instance falls there. The cycle types were tabulated
  from the standard element structure — A_4 has no transpositions and no
  4-cycles, so `2+1+1` and `4` are impossible; D_4 (order 8) has no 3-cycles,
  so `3+1` is impossible; C_4 realises only `1^4`, `4`, `2+2`; V_4 only `1^4`
  and `2+2`.
- **M3c** (descriptive, declared in the source before the full run executed):
  per-class absolute frequency deviations, pooled and per curve. Its rationale
  is that two curves are censused exhaustively, so their chi-square is not a
  sampling test at all — for any fixed nonzero bias it grows without bound
  with n. This is an additional disclosure; it does not adjust M3.

---

## 7. Protocol deviations

All deviations are listed in
`runs/RUN-MONO-0e6e8f-1/manifest.yaml → protocol_deviations`. Summarised:

1. `derive_s4.py` not executed (would write outside this experiment); its
   symbolic claims re-verified at run time instead. §1 above.
2. Four curves rather than the minimum two, so the non-isogeny check is
   non-vacuous *within* each prime.
3. Sample size above the minimum (exhaustive at p=101, 100k at p=1009). Fixed
   before any Stage-1 result was observed; not adjusted afterwards.
4. Projective (fibre) reading of the five-class label, with the affine reading
   also recorded. §5 above.
5. Ramified instances included in M3, disclosed separately, with a descriptive
   squarefree-subset statistic reported alongside.
6. **Three executions, all disclosed.** The first was wrapped in
   `/usr/bin/time -l`, which exited 1 and wrote a sandbox error
   (`sysctl kern.clockrate: Operation not permitted`) into `stderr.log`
   although the Python program itself completed normally. It was re-executed
   without that wrapper for a clean stderr and a true exit code (0); the
   archived artifacts are from that second execution. A third execution to a
   scratch path was diffed field-by-field against the archived
   `raw-result.json`: **every mathematical field was identical**, the only
   differences being measured `wall_seconds`, `cpu_seconds` and
   `peak_rss_bytes`. No execution was discarded for being unfavourable and no
   result differed between them.
7. No git command was run and no commit sha is recorded, per the dispatching
   Coordinator's explicit instruction for this shared working directory.

## 8. Budget

Wall 283.4 s / 1200 s. CPU 283.3 s / 1200 s. Peak RSS 26,427,392 B /
268,435,456 B. Run directory 831,884 B / 20,971,520 B. One worker. No network
call on any code path.
