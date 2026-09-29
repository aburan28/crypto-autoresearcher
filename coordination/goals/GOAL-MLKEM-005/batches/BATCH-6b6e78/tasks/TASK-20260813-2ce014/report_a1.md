# TASK-20260813-2ce014 — LEAD PRODUCER REPORT: scoring A-1's five falsifiers

    goal / batch     GOAL-MLKEM-005 / BATCH-6b6e78
    role             executor (LEAD, and the only producer of this batch)
    specification    PREREG-2, tasks/TASK-20260813-25cb95/prereg.md
                     FROZEN AND NOTARIZED at 60ac819982793e8ed402bc3b2f4b7ad1b1824f92
                     sha256 6c7c0800f0fdd94f62443262e5283aadc2149bad97d377634581d7aceba405ed
    implementation   HEAD at run time 040a52a8c00bbdcb92790e2c3f12e5617d95db43 (clean of
                     tracked modifications; the only untracked paths were this task's own
                     ten declared artifacts as they were produced)
    claim tier       TOY, UNCONDITIONALLY
    runs             1 declared measurement run, 1 archived-probe re-run (both completed)
    measurement      26.947 s of the 600 s cap (measure_a1.py) + 0.405 s (archived probe)

**THIS IS AN OBSERVATION RECORD.** It declares no hypothesis supported or refuted,
validates or refutes no heuristic, specifies no dispersion criterion, fibre clause, gate,
threshold or `K`, and changes no research status. It rescores no frozen verdict of any
prior batch. **CLAIM TIER TOY: nothing here bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost or on any cost model, and no number transports to
`beta = 606`, `d = 1420` or any FIPS 203 parameter set by extrapolation, analogy or any
other route.**

---

## 0. EVERY PATH THIS TASK WROTE

Inside the repository — **exactly the ten declared artifact paths, and nothing else**, all
under `coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/tasks/TASK-20260813-2ce014/`:

    measure_a1.py
    results_a1.json
    report_a1.md
    rerun_probe_precision_null_output.json
    rerun_probe_precision_null_stdout.log
    rerun_probe_precision_null_stderr.log
    command.txt
    stdout.log
    stderr.log
    run_manifest.yaml

Outside the repository (session scratch, **not** committed, listed for completeness):

    <scratch>/proto_gram.py          prototype of the exact Gram determinant
    <scratch>/smoke.py               reduced-scope smoke driver (3 lattices)
    <scratch>/smoke_out.json         its output
    <scratch>/smoke_stdout.log       its stdout
    <scratch>/smoke_stderr.log       its stderr

No `__pycache__` was created anywhere: every Python invocation ran with
`PYTHONDONTWRITEBYTECODE=1` and `-B`, and `git status --porcelain` after the run showed only
the declared artifacts. **I needed no eleventh file inside the repository and created none.**
`knowledge/INDEX.md` was not written, regenerated or staged. **Nothing was committed.**

---

## 1. CONTRACT AND PROVENANCE, VERIFIED RATHER THAN ASSERTED

* PREREG-2 in the working tree hashes to
  `6c7c0800f0fdd94f62443262e5283aadc2149bad97d377634581d7aceba405ed`, **equal** to the sha256
  of the blob at the notarizing commit `60ac81998` and equal to the committed
  `prereg_sha256.txt` sidecar.
* `60ac81998` is an ancestor of `HEAD` and changed exactly three paths — the snapshot
  receipt, `prereg.md` and `prereg_sha256.txt` — i.e. **zero producer artifacts**, which is
  the split-producer notarization pattern PREREG-2 requires.
* The block structure of every basis was verified entrywise at every family, lattice and
  basis index (`True`), so every exact `|det B_i|` used below is a verified consequence of a
  verified structure rather than an assumption.
* The `PIN-DET` fibre families built here are **bit-identical** to the committed
  `measure_gvar2.build_basis_fam` families `F0|fib_s2/s3/s4`, and `F0` likewise.
* This file's `binary64` routes reproduce the committed lead's own `logdet_routes_fam` at
  **480 of 480 route values bit-identically**, max absolute difference `0.0`.
* The committed `measure_gvar2.py` and `measure_falserefusal.py` were **imported**, not
  transcribed; every clause verdict below (`VAR-S`, `VAR-F`, the `G-VAR2` conjunction,
  `bit_identical`, the `scale_degenerate` handling) is the committed code path.

---

## 2. OBLIGATION (d) — `R3-OUT-4`, AND THE GUARD THAT NOW GUARDS

Each candidate's fibre family was built **from that candidate's own declared nuisance set**
(PREREG-2 2.4) using the frozen `PIN-DET` and `PIN-A00` constructions (2.3), across all three
declared draws (seed prefixes 2, 3, 4). For every candidate, every fibre family and every
lattice the run **asserts and prints** which declared arguments were verified constant across
the basis index — `abs(det B_i)` by **exact integer** equality, `A[0,0]` by **integer**
equality, `every entry of A` by entrywise integer equality, `raw GSO profile` by bitwise
equality of the float64 `|R_jj|`. The 570 printed lines are in `stdout.log`; the full
per-argument record is `results_a1.json -> R3_OUT_4_per_candidate_fibre_guard`.

| candidate | fibre pinning | declared nuisance set | verified constant across `i` | observed to vary |
|---|---|---|---|---|
| `X_null` | PIN-DET | `abs(det B)` | d, k, beta, q, abs(det B) | — |
| `rdet` | PIN-DET | `abs(det B)` | d, abs(det B) | — |
| `X_parfree` | PIN-DET | `abs(det B)` | d, k, abs(det B) | — |
| `V_evade` | PIN-DET+PIN-A00 | `abs(det B)`, `A[0,0]` | d, k, beta, q, abs(det B), **A[0,0]** | — |
| `X_lambda` (all 10 lambda) | PIN-DET+PIN-A00 | `abs(det B)`, `A[0,0]` | d, k, beta, q, abs(det B), **A[0,0]**, lambda | — |
| `X_gso_k` | PIN-DET | `abs(det B)` | d, k, q, abs(det B) | raw GSO profile *(free by declaration)* |
| `X_hash` (all 4 c) | PIN-DET | `abs(det B)` | d, k, beta, q, abs(det B) | every entry of A *(free by declaration)* |

**`P-G2` HELD; `R3-OUT-V` DID NOT FIRE.** No declared nuisance argument of any scored
candidate varied on that candidate's own fibre family, at any of the 10 lattices, any of the
3 draws, or either pinning.

Concretely, at `F0|fib_s2`, `L1`, the eight `A[0,0]` values are
`2122, 1620, 2918, 1188, 791, 1315, 895, 2284` **under the unpinned BATCH-4ed139
construction** (the eight values PREREG-2 6.1 records, attributed there to Validator `F-2`
and Red Team `O-1`) and `2122` at all eight indices **under this batch's `PIN-A00`**, i.e.
`A'_0[0,0]` everywhere, with `|det B_i|` untouched at `q^(d-k)`.

**CARRIED VERBATIM FROM PREREG-2 6.1, BECAUSE IT BOUNDS EXACTLY THIS RESULT:** under this
batch's `PIN-A00` construction the void row is reachable **only through an implementation
error**, because the pinning is by construction. **Its non-firing is therefore evidence about
the IMPLEMENTATION and about nothing else, and it may NOT be cited as a control, as a
validation of the fibre clause, or as evidence about any object.**

For `X_gso_k`, PREREG-2 2.4 lists `abs(det B)` as its nuisance argument although
`abs(det B)` is not itself a member of its declared argument list; the guard therefore ranges
over the **union** of the declared argument set and the declared nuisance set, never over the
argument list alone. Recorded as an implementation decision, not a change to the frozen table.

---

## 3. `A-1.1` — `R3-OUT-1`, THE EXACT-ROUTE CERTIFICATION

Total exact-route wall clock **20.211 s**. `R7_exact_gram` terminated at **every** lattice
including `d in {100, 140}`, worst case `3.3 s` per lattice against the declared `45 s`
per-lattice cap; **no lattice was `UNCOVERED` for exceeding the cap.**

| candidate | exact route | expected class (2.4) | **CERTIFIED class** | agree |
|---|---|---|---|---|
| `X_null`, `rdet`, `X_parfree`, `V_evade`, `X_lambda` (all 10 lambda) | `R6_exact` | CONSTANT | **CONSTANT** | yes |
| `X_hash` (all 4 c) | `R6_exact` | NON-CONSTANT | **NON-CONSTANT** | yes |
| `X_gso_k` | `R7_exact_gram` | NON-CONSTANT | **UNCERTIFIED** | **no** |

**THE CERTIFICATION BINDS AND THE DISAGREEMENT IS A FINDING OF THIS BATCH.** `X_gso_k` is
`UNCERTIFIED` because `R7_exact_gram` is reported `UNAVAILABLE` under the frozen `P-GRAM`
rule (section 4 below), not because it failed to terminate. Every falsifier below is scored
against the **certified** class and never against the expectation column.

**PREREG-2 6.4's live check, answered with numbers.** At least one candidate is certified
`NON-CONSTANT` by its exact route: `X_hash` at all four declared amplitudes, on all three
draws. The classification is therefore not degenerate. **But the observation that matters for
scope is this: the certified-`NON-CONSTANT` class in this run is populated ONLY by `X_hash`,
the object that reads every entry of `A` and carries no lattice information whatever.
`X_gso_k` — the only in-scope candidate that reads the instance — is `UNCERTIFIED`. Every
`FC-3a` and `FC-3b` firing below therefore comes from the null object.**

---

## 4. `R3-OUT-8` — `P-GRAM`, APPLIED EXACTLY AS FROZEN, AND MY OBJECTION TO IT

`R7_exact_gram` was implemented exactly as PREREG-2 2.9 derives it:
`X_gso_k = (1/(2k)) log det(I_k + A A^T)`, with `det` by exact integer arithmetic
(multi-modular elimination over distinct 30-bit primes with CRT, sized by the Hadamard bound
of the actual matrix) and the logarithm through `decimal` at 60 significant digits. No float
representation of the Gram determinant is read anywhere.

**`P-GRAM` verdict: FALSIFIED.** 800 comparisons against float64 `X_gso_k`, tolerance `1e-10`
absolute:

| route | max abs deviation | passes `1e-10` | worst cell |
|---|---|---|---|
| `RQ_qr_of_BT` | `1.421e-13` | **yes** | `F0 fib_s2 PIN-DET, L12, i2` |
| `RG_cholesky_of_gram` | `3.002e-09` | **no** | `F0, L5, i1` |

Per lattice against the **committed** `results_falserefusal.json` float64 values of family
`F0` (in-run float64 deviations were identical to these to every digit printed):

| lattice | (d,k) | `RQ` dev | `RG` dev |
|---|---|---|---|
| L1 | (100,30) | 1.776e-15 | 1.776e-15 |
| L2 | (100,70) | 9.015e-14 | **1.331e-09** |
| L4 | (140,40) | 1.776e-15 | 1.776e-15 |
| L5 | (140,100) | 9.015e-14 | **3.002e-09** |
| L7 | (20,6) | 1.776e-15 | 1.776e-15 |
| L8 | (20,14) | 1.337e-13 | **4.356e-10** |
| L9 | (30,9) | 1.776e-15 | 1.776e-15 |
| L10 | (30,21) | 7.061e-14 | **3.420e-10** |
| L11 | (40,12) | 1.776e-15 | 1.776e-15 |
| L12 | (40,28) | 6.617e-14 | **6.189e-10** |

**THE FROZEN CONSEQUENCE WAS APPLIED AND NOT PATCHED:** `R7_exact_gram` is reported
**UNAVAILABLE** for `X_gso_k`, which **fires `FC-1`** for the raw-GSO candidate class. The
derivation of 2.9 was not repaired, no substitute route was introduced, and `X_gso_k` was not
certified through `RQ` alone.

**MY OBJECTION, RECORDED AS THE TASK CARD DIRECTS AND SCORED AS WRITTEN ANYWAY.** I believe
`P-GRAM`'s `1e-10` tolerance is unreachable by *any* exact route, and that the failure above
is a property of route `RG` rather than of the derivation. The reason is already in the
committed record and needs no new measurement: `results_falserefusal.json ->
route_agreement_RQ_vs_RG` records the two committed float64 routes disagreeing **with each
other** by up to `3.0015181451403805e-09` (`F0`, `L5`), and that number matches my `RG`
deviation at `L5` to five significant digits. Two float routes that differ by `3e-09` cannot
both be reproduced to `1e-10` by a single value, so the clause as frozen is unsatisfiable at
`L2`, `L5`, `L8`, `L10`, `L12` regardless of which exact value is supplied. I note further
that the derivation reproduces `RQ` — the route whose diagonal *is* the Gram-Schmidt norm
sequence — to `1.4e-13` at every basis and lattice, and that at the five lattices where the
two float routes agree bit-closely (`1.776e-15`) the exact route agrees with **both**. **None
of that changes the verdict recorded above; the frozen clause fired and `FC-1` is scored as
fired.** Whether the clause should be superseded is a Coordinator act, not mine, and I
propose no replacement tolerance.

---

## 5. OBLIGATION (c) — `R3-OUT-2`, EVERY `VAR-F`-LIKE CONSTANCY CLAUSE AT TWO PRECISIONS

330 blocks (candidate x route x fibre family), **12,426 covered cell evaluations**, each
carrying at both `binary32` and `binary64`: `s_c^fib`, `m_c^fib`, `rho = s/|m|`, the carried
`bit_identical()` flag, the number of distinct IEEE-754 values over the 8 bases, **the
committed `VAR-F` verdict of PREREG-1 3.3 evaluated at that precision**, the fibre family
label and seed prefix, and the ratio `rho(binary32)/rho(binary64)`.

**114 cell evaluations are UNCOVERED**, all of them `X_gso_k | RG_cholesky_of_gram` at
`binary32`: `numpy.linalg.cholesky` raises `LinAlgError: Matrix is not positive definite` on
the float32 Gram at every lattice and basis. **This is NUMERICAL / INFRASTRUCTURE SIGNAL
(AGENTS.md rule 5, PREREG-2 7.6). It forces the `-PARTIAL` suffix. It is NEVER a falsifier of
`A-1` and is never negative mathematical evidence.**

### 5.1 Whether the committed `VAR-F` verdict CHANGES with precision

**It changes at 1,416 of the 12,426 covered cells, in 49 of the 330 blocks.**

| axis | breakdown of the 1,416 changing cells |
|---|---|
| by route | `R4_gram_half_slogdet` 1,396; `R2_QR_of_BT` 20; every other declared route 0 |
| by fibre family | 108 / 104 / 126 on `fib_s2` / `fib_s3` / `fib_s4` under PIN-DET; 352 / 341 / 385 under PIN-DET+PIN-A00 |
| by candidate | `X_null` 96; `rdet` 10; `X_parfree` 10; `V_evade` 98; `X_lambda` 98 at each of the ten lambda; `X_hash` 96 / 95 / 31 / 0 at `c = 1e-9 / 1e-3 / 1e-2 / 1e-1` |

**Stating it as `AM-18(b)` requires, in my own words and cell-counted: the committed `VAR-F`
clause, evaluated on route `R4_gram_half_slogdet` at 1,396 cells and on route `R2_QR_of_BT`
at 20 cells, is reading a REPRESENTATION rather than an observable. At those 1,416 cells the
clause returns a different verdict for the same mathematical object solely because the
working precision changed from `binary32` to `binary64`, with the family, the fibre family,
the declared argument set, the threshold and the code path all held fixed. The verdict there
is a fact about the float format, not about the candidate.** The remaining 281 blocks
returned the same verdict at both precisions; that is reported as a measurement and is not
evidence that those clauses read an observable.

The same phenomenon appears in the `F0` adjudication of section 7: `X_null` through
`R4_gram_half_slogdet` meets its declared `REFUSED` target at 38 of 38 cells at `binary64`
and at only 6 of 38 at `binary32`.

---

## 6. `A-1.2` / `A-1.3` — THE FALSIFIERS, AND `R3-OUT-7`

Scored exactly as PREREG-2 1.2 states them, against the **certified** class, with the
`precision_degenerate` rule of 1.3 applied **as frozen**.

| falsifier | fired | cells | where |
|---|---|---|---|
| `FC-1` (A-1.1) | **YES** | 1 candidate class of 2 | raw-GSO class: `R7_exact_gram` UNAVAILABLE under `P-GRAM` (section 4). Determinant-only class: `R6_exact` exists, is defined and terminates everywhere — `FC-1` does **not** fire there |
| `FC-2a` (A-1.2) | **YES** | **153** | every certified-CONSTANT candidate; **route `R2_QR_of_BT` only**; all six fibre families. Extreme cell `rdet, R2_QR_of_BT, F0 fib_s4 PIN-DET, L5_b95`: `rho(binary32) = 0.0`, `rho(binary64) = 5.109e-14` — the float32 evaluation collapsed the dispersion to exactly zero while float64 did not, at a cell that is **not** `precision_degenerate` |
| `FC-2b` (A-1.2) | no | 0 | `rho` under `R6_exact` is exactly `0` at every certified-CONSTANT candidate, fibre family and cell |
| `FC-3a` (A-1.3) | **YES** | **868** | `X_hash` at all four amplitudes (684 / 113 / 60 / 11 at `c = 1e-9 / 1e-3 / 1e-2 / 1e-1`); all six float routes; all three draws. Ratio range over the firing cells `0.0` to `1.171e+09`; extreme cell `X_hash[c=1e-09], R4_gram_half_slogdet, F0 fib_s3 PIN-DET, L8_b15`, ratio `1.1714e+09` with `rho(32) = 1.813e-01`, `rho(64) = 1.548e-10` |
| `FC-3b` (A-1.3) | **YES** | **354** | `X_hash[c=1e-09]` only; routes `R0` 114, `R1` 114, `R3` 114, `R2` 12; all three draws. Example `X_hash[c=1e-09], R0_closed_form, F0 fib_s2 PIN-DET, L1_b15`: `rho(binary32) = 0.0` with `rho(binary64) = 3.397e-10` — the float evaluation destroyed real fibre content |

**`A-1` does NOT hold in this batch at full declared coverage: four of the five frozen
falsifiers fired, and any one of them is independently sufficient.**

### 6.1 `R3-OUT-7` — the `precision_degenerate` disclosure, with BOTH readings

**4,788 cells** are `precision_degenerate` (`rho(binary64) == 0` exactly): routes
`R0_closed_form` 1,596, `R1_slogdet` 1,596, `R3_slogdet_of_UB` 1,596, spread evenly over the
fourteen certified-CONSTANT candidate instances (342 cells each). All 4,788 are of certified
class CONSTANT.

* **FROZEN reading (BINDING):** all 4,788 are **EXEMPT** from `FC-2a` — not a falsification
  and not a confirmation. `FC-2b` still binds there and did not fire.
* **STRICT reading, printed beside it as 1.3 requires:** `rho(binary32) = rho(binary64) = 0`
  at **all 4,788** of them, so under the strict reading `A-1.2` is **FALSIFIED at every one
  of the 4,788 cells** — nothing decreased. `0` cells satisfy the strict reading.

This is exactly the live instance PREREG-2 6.3 named before the run: at every `R0` cell
`A-1.2` would be falsified **by the definition of `R0`**, which never touches the matrix. The
measurement confirms that reachability at 1,596 `R0` cells and extends it to `R1` and `R3`.
Both readings are recorded so a successor can re-decide against the numbers rather than
against the paragraph. **The frozen reading is what was applied in the scoring above.**

---

## 7. OBLIGATION (b) — `R3-OUT-3`, `F0`'s REFUSAL HALF UNDER `V6`, `V7`, `VX`

**THIS IS A NEW MEASUREMENT IN THIS BATCH.** The `BATCH-4ed139` frozen verdict is immutable
and is **not** rescored here: `F0` FAILED, the branch was `T-F0FAIL` reported as
`T-F0FAIL-PARTIAL`, and `DEC-20260812-781961` closed it. What follows is this batch's own
answer, computed from this batch's own bases through the committed `G-VAR2` code path, with
`VAR-S` on the scored family `F0` (seed prefix 1) and `VAR-F` on `F0|fib_s2|PIN-DET`.

**Scope: `F0`'s REFUSAL HALF ONLY** — `X_null` and `rdet`, both determinant-only, requiring
no reduction. The `lam1n` / `hkz` / `rawtail` ADMITTED half is **not in scope** (PREREG-2
2.5); its exclusion is a declared scope limit and is never an `FC-1` firing.

At the frozen `binary64` reading, per candidate per route, target `REFUSED`, coverage 38/38
everywhere:

| candidate | R0 | R1 | R2 | R3 | R4 | R5 | `R6_exact` |
|---|---|---|---|---|---|---|---|
| `X_null` | REFUSE 38 | REFUSE 38 | REFUSE 38 | REFUSE 38 | REFUSE 38 | REFUSE 38 | **REFUSE 38** |
| `rdet` | REFUSE 38 | REFUSE 38 | **ADMIT 38** | REFUSE 38 | **ADMIT 38** | **ADMIT 38** | **REFUSE 38** |

* **The verdict over the SIX FLOAT ROUTES `{R0, R1, R2, R3, R4, R5}` — the frozen PREREG-1
  4.1 reading, recomputed here — is `V6 = FAIL`.**
* **The verdict over the SEVEN ROUTES `{R0, R1, R2, R3, R4, R5, R6_exact}`, where every route
  must hold, is `V7 = FAIL`.**
* **The verdict over the EXACT ROUTE ALONE `{R6_exact}` is `VX = PASS`, at 38 of 38 cells for
  `X_null` and 38 of 38 for `rdet`.**

A `binary32` column was computed as a **diagnostic** and is not one of the three frozen
readings: there `V6 = FAIL` over `{R0..R5}`, `V7 = FAIL` over `{R0..R5, R6_exact}`,
`VX = PASS` over `{R6_exact}`, with `X_null` through `R4` additionally missing its target at
32 of 38 cells.

**What `VX = PASS` over the route set `{R6_exact}` licenses, quoted from the frozen section
4:** it licenses exactly the statement Red Team `RC-1` frames — that the `F0` refusal failure
is localised to the **float representation** consumed by PREREG-1 3.3's fallback, and **not**
to `AM-16(a)`. It licenses **nothing** about any lattice, about any observable's
admissibility, about `F1`, about any prior batch's verdict, or about the gate, and it
validates no criterion. **The proposition itself is already promoted in `KN-FIND-9d44b4` and
is NOT a new finding of this batch; what is new here is only that BATCH-6b6e78's own record
now answers it rather than inheriting `DEC-20260812-781961`'s answer, which is what the
goal's `next_action` commissioned.**

### 7.1 The archived probe, re-run unmodified from its committed path

Command, from the repository root, with `--out` pointing into this task's directory (the
exact string is in `command.txt`): `python3 -B <BATCH-4ed139 committed
probes/probe_precision_null.py> --out <this task dir>/rerun_probe_precision_null_output.json`
under `PYTHONDONTWRITEBYTECODE=1`.

The probe was **not copied, not edited and not vendored**. Its sha256 at the committed path
is `c7f18ec2f4f6c282a5e60f38c23e8d5d493c24018c1fd55479bb9198c1c8e87c`, unchanged before and
after the re-run. Wall clock `0.405 s`.

**Field-by-field comparison with the archived `probe_precision_null_output.json`: 660 leaf
fields in each, identical key sets, and 658 of 660 values equal exactly. The two disagreeing
fields are named here:**

| field | archived | this re-run |
|---|---|---|
| `git_revision` | `e205c22b83f352a1c517d798ba34da2fc962682e` | `040a52a8c00bbdcb92790e2c3f12e5617d95db43` |
| `wall_clock_seconds` | `0.33` | `0.405` |

Both are expected to differ between runs and neither is a measured quantity of the probe.
**Every measured number agrees exactly**, including `eps32/eps64 = 5.369e8`, the `rdet`
`binary32/binary64` relative-dispersion ratios, the `X_gso_k` ratios, and the probe's
`R6_exact` counters. The probe's own stdout is in `rerun_probe_precision_null_stdout.log`;
`rerun_probe_precision_null_stderr.log` is empty.

---

## 8. `R3-OUT-5` — `P-SEP`, THE `K`-INTERVALS (SOLVED, NOT GRIDDED)

`K_min(r,p) = max` over certified-CONSTANT candidates and covered cells of `rho/u_p`;
`K_max(r,p) = min` over certified-NON-CONSTANT candidates and covered cells of `rho/u_p`;
EMPTY iff `K_min >= K_max`. Unit roundoff `u_p = eps_p/2`: `u_32 = 5.960e-08`,
`u_64 = 1.110e-16`.

| route | precision | `K_min` | `K_max` | EMPTY |
|---|---|---|---|---|
| `R0_closed_form` | binary32 | 0 | 0 | **yes** |
| `R0_closed_form` | binary64 | 0 | 4.550e+05 | no |
| `R1_slogdet` | binary32 | 0 | 0 | **yes** |
| `R1_slogdet` | binary64 | 0 | 4.550e+05 | no |
| `R2_QR_of_BT` | binary32 | 11.47 | 0 | **yes** |
| `R2_QR_of_BT` | binary64 | 1.616e+03 | 4.551e+05 | no |
| `R3_slogdet_of_UB` | binary32 | 0 | 0 | **yes** |
| `R3_slogdet_of_UB` | binary64 | 0 | 4.550e+05 | no |
| `R4_gram_half_slogdet` | binary32 | 5.272e+06 | 1.750e+04 | **yes** |
| `R4_gram_half_slogdet` | binary64 | 2.608e+07 | 2.851e+05 | **yes** |
| `R5_slogdet_of_BH_ambient_isometry` | binary32 | 355.7 | 17.08 | **yes** |
| `R5_slogdet_of_BH_ambient_isometry` | binary64 | 920.4 | 4.550e+05 | no |
| `RQ_qr_of_BT` | both | undefined | undefined | undefined |

`RQ` has no endpoint on either side because `X_gso_k` is `UNCERTIFIED`, so no certified
candidate of either class supplies a `rho` on that route; `RG` at `binary32` is uncovered
(section 5) and contributes nothing. Intersections over precisions at fixed route are EMPTY
for `R0`, `R1`, `R2`, `R3`, `R4`, `R5` and undefined for `RQ`.

**Joint intersection over routes and precisions: `K_min = 2.6079e+07`, `K_max = 0.0`,
EMPTY = `True`.** `P-SEP`'s frozen prediction — that the joint intersection is EMPTY — is
therefore **not falsified by this measurement**. This is a measurement that an interval is
empty. **I propose no `K` and specify no criterion; that is not mine to make.**

An honest reading limit, stated because the numbers invite it: the certified-NON-CONSTANT
side of every `K_max` above is supplied **only** by `X_hash`, and every `K_max` witness is an
`X_hash` cell.

---

## 9. `R3-OUT-6` — `AM-18(e)`, `X_hash` AT EVERY DECLARED AMPLITUDE, ALL THREE DRAWS

**REPORTED AS A RE-EXECUTION AND EXTENSION OF AN ARCHIVED CONSTRUCTION AND NEVER AS A NEW
FINDING.** That `X_hash` is admitted at 38 of 38 cells at the top amplitude by the
`BATCH-4ed139` code path is **archived, `n = 1`, and attributed** to that batch's Red Team
`probe_argset.py` section Q3 and to `KN-FIND-9d44b4` section 6 item 5. What is new here is
only its behaviour **across precisions** and on the **per-candidate fibre**, which nobody has
measured.

Scored through the identical code path at `c in {1e-9, 1e-3, 1e-2, 1e-1}` on all three draws
(`AM-10` replication), dispersion reported per draw in
`results_a1.json -> R3_OUT_6_X_hash_null_object_calibration`. The pattern is stable across
the three draws. On route `R0_closed_form`, where the only fibre variation is `c*H(B)`:

| amplitude | `rho(binary64)` range (fib_s2) | `rho(binary32)` range | cells with `rho(32)=0` | `FC-3a` | `FC-3b` |
|---|---|---|---|---|---|
| `c = 1e-9` | 5.05e-11 .. 9.93e-10 | 0 .. 0 | 38 of 38 | 38 | 38 |
| `c = 1e-3` | 5.05e-05 .. 9.91e-04 | 5.05e-05 .. 9.91e-04 | 0 | 0 | 0 |
| `c = 1e-2` | 5.05e-04 .. 9.78e-03 | 5.05e-04 .. 9.78e-03 | 0 | 0 | 0 |
| `c = 1e-1` | 5.01e-03 .. 8.63e-02 | 5.01e-03 .. 8.63e-02 | 0 | 0 | 0 |

On route `R4_gram_half_slogdet` the float32 route noise (`rho(32)` up to `1.8e-01`) dominates
the injected amplitude at every `c`, and `FC-3a` fires at 38, 37-38, 17-22 and 3-5 cells per
draw at `c = 1e-9, 1e-3, 1e-2, 1e-1` respectively.

**`P-HASH` is FALSIFIED** — `FC-3a` and `FC-3b` fired on `X_hash`. PREREG-2 section 5 froze
the consequence of `P-HASH` **holding**; it did not hold, so that consequence does not arise,
and I record no statement about it beyond this sentence. `X_hash` is certified NON-CONSTANT,
so those firings are `A-1.3` firings and are counted as such in section 6.

---

## 10. THE PREDICTION REGISTER (PREREG-2 section 5), AS FROZEN

All ten items were **OPEN at the moment of notarization**; none had been evaluated by anyone
when PREREG-2 was frozen. Five are predictions, four are consistency checks that are reported
and **not** counted toward empirical content, and one is the must-pass guard.

| id | class | outcome |
|---|---|---|
| `P-A11` | PREDICTION | **FALSIFIED** (`FC-1` fires for the raw-GSO class; it does **not** fire for the determinant-only class) |
| `P-A12a` | CONSISTENCY CHECK | **FALSIFIED** at 22 cells — see the correction below |
| `P-A12b` | PREDICTION | **FALSIFIED** (`FC-2a` at `R2_QR_of_BT` for `X_parfree`, `V_evade` and every `X_lambda`) |
| `P-A13a` | CONSISTENCY CHECK | **NOT SCORABLE**: `X_gso_k` is `UNCERTIFIED` because `R7_exact_gram` is UNAVAILABLE |
| `P-HASH` | PREDICTION | **FALSIFIED** |
| `P-SEP` | PREDICTION | joint intersection **EMPTY** — not falsified |
| `P-F0Xa` | CONSISTENCY CHECK | **HELD**: `V6 = FAIL` over `{R0..R5}` |
| `P-F0Xb` | PREDICTION | **HELD**: `V7 = FAIL` over `{R0..R5, R6_exact}` **and** `VX = PASS` over `{R6_exact}` at 38/38 |
| `P-GRAM` | CONSISTENCY CHECK | **FALSIFIED** (section 4) |
| `P-G2` | MUST-PASS GUARD | **HELD** |

**Correction to the machine-generated `P-A12a` line, recorded rather than left for a reader
to trip over:** the automated scorer in `measure_a1.py` matched `FC-2a` instances against a
truncated summary list and wrote `"OUTCOME": "HELD"` for `P-A12a` into `results_a1.json`. The
complete per-block record shows `FC-2a` firing at 12 cells for `X_null` and 10 for `rdet`,
both on route `R2_QR_of_BT`. Read against the frozen statement of `P-A12a` —
`rho(f32) > rho(f64)` at every non-degenerate covered cell — **`P-A12a` is FALSIFIED at those
22 cells**, on the same route and by the same mechanism as `P-A12b`. The table above carries
the corrected value; the uncorrected value is left visible in `results_a1.json` rather than
edited. The falsifier counts in section 6 are the authoritative numbers and are unaffected.
`P-A12a` is a consistency check and does not count toward this batch's empirical content in
either direction.

---

## 11. THE TERMINATION BRANCH

Read off `R3-OUT-1` and `R3-OUT-2` under `R3-OUT-V`'s precedence, **and nowhere else**:

* `R3-OUT-V` did **not** fire (`P-G2` held) -> `T-VOID` does not fire.
* `FC-1` fired for the raw-GSO class but **not** for the determinant-only class, whose
  `R6_exact` is defined and terminates everywhere -> the 7.2 condition ("for **EVERY**
  in-scope candidate class") is **not** met, so `T-UNSTATABLE` does not fire.
* `FC-1` (some but not all classes), `FC-2a`, `FC-3a` and `FC-3b` fired at covered cells ->
  **`T-A1-FALSIFIED` fires, with the scope named.**
* Coverage is not full: 114 uncovered cell evaluations (`X_gso_k` through `RG` at `binary32`,
  a float32 Cholesky failure) -> the `-PARTIAL` suffix of 7.6 applies.

> **THE BRANCH THAT FIRED IS `T-A1-FALSIFIED-PARTIAL`.**

**Quoting the clause it fires under (PREREG-2 7.3):** *"FIRES WHEN: any of `FC-1` (for some
but not all classes), `FC-2a`, `FC-2b`, `FC-3a`, `FC-3b` fires at any covered cell, route or
candidate. MEANS: `A-1` as stated is false at the declared precisions, routes, families and
candidates. It does not mean that no finite-precision meaning exists; it means this one does
not survive."*

**What this branch LICENSES (7.3):** a decision recording exactly which sub-clause failed, at
which cells and routes, and for which certified class — recorded in section 6 above — and the
specification of a **SUCCESSOR ASSUMPTION**, not a criterion, subject in full to 7.5's
six-part repair bar and its absolute bar on an eighth consecutive gate repair without a
committed Coordinator decision that first records why the `C3` lane cannot be entered instead.

**What this branch FORBIDS (7.3):** specifying **any** dispersion criterion, fibre clause or
gate resting on `A-1`; proceeding to `C3` behind any gate; presenting the falsification as
evidence about any lattice, any observable's admissibility, or any proposition in this goal —
**it is an instrument outcome**; reading a failure caused by a missing dependency, a timeout,
a crash or the declared `R7` cap at `d > 40` as a falsifier at all; and **closing, pausing or
completing `GOAL-MLKEM-005`**.

I do not argue for a different branch, I do not re-read the clause, and I report no branch
the numbers do not fire.

---

## 12. DEVIATIONS, ANOMALIES AND UNEXPECTED OBSERVATIONS — ALL RECORDED, NONE DISCARDED

1. **`X_gso_k` through `RG_cholesky_of_gram` at `binary32` failed at every lattice and basis**
   (`LinAlgError: Matrix is not positive definite`). 114 cell evaluations uncovered.
   Infrastructure / numerical signal; forces `-PARTIAL`; never a falsifier.
2. **`P-GRAM` failed on route `RG` at five lattices** and passed on `RQ` everywhere. Scored as
   frozen (`FC-1` fires); my objection is in section 4 and the derivation was not patched.
3. **The certified class of `X_gso_k` contradicts PREREG-2 2.4's expectation** (UNCERTIFIED vs
   NON-CONSTANT). The certification binds; the disagreement is recorded as a finding.
4. **Every `FC-3a`/`FC-3b` firing comes from the null object `X_hash`**, because the only
   in-scope candidate that reads the instance is uncertified. Recorded as a scope fact.
5. **Two implementation defects were found by a reduced-scope smoke test BEFORE the declared
   run and fixed before it**, both disclosed here rather than left invisible.
   (a) The guard originally ranged over `declared_arguments` alone, so `X_gso_k`'s nuisance
   argument `abs(det B)` — which 2.4 lists as its nuisance but not among its arguments — was
   reported as unchecked and spuriously fired `R3-OUT-V`; the guard now ranges over the union.
   (b) The exact-route statistic was computed in a 60-digit `decimal` context, whose rounding
   produced `rho_exact` of order `1e-59 > 0` on constant fibres and spuriously fired `FC-2b`
   (an existence test with no threshold); the **statistic** is now taken at 240 digits, where
   the mean and deviations of eight equal exact values are exact and the sd of a constant
   fibre is exactly `0`. The declared route precision of 60 significant digits is unchanged.
6. **Peak memory was not instrumented.** No `ru_maxrss` was captured for the measurement
   invocation. No `MemoryError`, OOM or swap event occurred and the host has 15 GB, but this
   is recorded as **MISSING DATA** rather than estimated against the 4 GB budget.
7. **The `FC-3a` / `FC-3b` `instances` lists in `results_a1.json` are truncated to the first
   200 entries** with the truncation count recorded beside them. The complete firing record is
   in `R3_OUT_2_two_precision_table.per_block`, per cell, and every count in this report was
   recomputed from that complete record rather than from the truncated lists.
8. **`P-A12a` was mis-scored by the automated register line**; corrected in section 10 against
   the raw data, with the mis-scoring left visible in `results_a1.json` rather than edited.
9. **The requested policy is `executor-implementation`; the model that answered is not the
   model the adapter binds to that policy.** See `run_manifest.yaml`; recorded, not reconciled.

**No protocol deviation from PREREG-2 was made.** Every clause was implemented as written,
including the two I object to (`P-GRAM`'s tolerance, section 4; and the `precision_degenerate`
rule's strict/frozen split, whose strict reading falsifies `A-1.2` at 4,788 cells by the
definition of `R0`, section 6.1). Both objections are recorded as findings and both clauses
were scored as frozen.

---

## 13. BINDING CARRIES AND SCOPE

`AM-10` through `AM-18` and their carries are in force; `AM-3` is **not** retired;
`BATCH-a44d08` is **not** rescored in any respect and its Section C verdict and detection
floors stay **VOID IN BOTH DIRECTIONS**; `BATCH-9e3584`, `BATCH-cbe023` and `BATCH-4ed139`
are **not** revalidated; `AM4-OBS-1` is cited only through `KN-FIND-f38a89`; `AM-9` binds; the
`G-VAR` refusal is cited only as conditional on the frozen family `F0`. This report cites
**none** of the items on PREREG-2 10.1's not-citable list: no span of the form "a factor of 6
to 31", neither sub-6x count, no sub-threshold count of any kind, no "genuinely
cross-platform" reading, and no "29 of 48" figure. `knowledge/INDEX.md` was not written,
regenerated or staged. **Nothing was committed.**

**Nothing in PREREG-2 section 9's promoted `KN-FIND-9d44b4` list is restated here as a new
result of `BATCH-6b6e78`.** In particular the float-representation character of the `F0`
failure, the `R6_exact` refusal of `rdet` at 38/38, the threshold-independence across sixteen
decades, the decorative declared argument set of the `BATCH-4ed139` implementation, and the
two-sided obstruction are **promoted, attributed and binding**; this batch tests what follows
from them.

**SCOPE.** `q = 3329`; `d in {20, 30, 40, 100, 140}`; the frozen `k` and `beta` grids; 8 bases
per lattice per fibre family; one scored family `F0` and three fibre draws under two frozen
pinnings; six float routes plus one exact route for the determinant-only candidates, two float
routes plus one exact route for `X_gso_k`; two working precisions `binary32` and `binary64`;
**no reduction of any kind** and nothing reduction-dependent above `d = 40`. `float32` is a
knob used to move machine epsilon and **is not a claim about any deployment**. `lam1n`, `hkz`
and `rawtail` are **OUT OF SCOPE** (PREREG-2 2.5) — a declared scope limit, **never** an
`FC-1` firing — so `A-1`, held or falsified, says nothing about any reduction-dependent
observable in this goal, which is the half of the candidate list that matters for `C3`. `F1`
is not used in this batch; its absence is a declared scope limit and not a result. **Every
observation above is scoped to exactly that and transports nowhere.**

**CLAIM TIER TOY.**
