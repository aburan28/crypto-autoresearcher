# GATE-RR78-1 PRE-REGISTRATION (IMMUTABLE)

Written 2026-08-01, before any AES measurement was taken in this session.
Session start stamp: 2026-08-01T21:54:30Z. Halt boundary: start + 2400 s =
2026-08-01T22:34:30Z.

**This file is frozen at the moment of writing. It is not edited afterwards.**
Any correction appears as a separate `PREREG-AMENDMENT-*.md` file with its own
UTC stamp, never as an edit here.

Role: Executor. Nothing here is a claim about AES security. `claim_tier: toy`.

---

## 0. Status of the governing contract

There is **no `experiments/<EXP-ID>/specification.yaml` with `status: approved`
and non-null `approved_by`** for GATE-RR78-1. The governing document is
`scratchpad/rr78/candidate_report.yaml` (`CAND-RR78-A` / `minimal_test`), which
is an Idea-Generator **proposal**, explicitly self-labelled
`"Every gate is a proposal"`.

Under the Executor contract this is a `specification_error` for a *ledger*
experiment. This session therefore runs as an **exploratory scratchpad gate**,
not as an approved experiment: nothing is written to the repo or the ledger, no
`experiments/.../runs/<RUN-ID>/` package is created, no evidence record is
produced, and the missing contract fields are listed in the final report. The
pre-registration discipline below is applied in full anyway.

Missing-from-a-formal-contract fields (reported, not repaired):
`experiment_id`, `status`, `approved_by`, `budget.wall_clock_seconds`,
`budget.memory_gb`, `budget.maximum_runs`, `stopping_rules`,
`required_artifacts`, `certificate.kind`.

**Certificate discipline**: this is a pure measurement run. `certificate.kind:
none`, set explicitly. No discrete-log solve, no factor-base relation, no
solution certificate is claimed or required.

## 0b. Parse defect in the input specification (reported, NOT repaired)

`scratchpad/rr78/candidate_report.yaml` **does not parse as YAML**. Verbatim
error from `yaml.safe_load` (PyYAML, python 3.11.15):

```
yaml.parser.ParserError: while parsing a block collection
  in "candidate_report.yaml", line 1307, column 7
expected <block end>, but found '?'
  in "candidate_report.yaml", line 1313, column 7
```

Cause: at `report.honest_accounting.deferred_unbounded` (line 1306) a block
**sequence** of two `- >-` items is followed at line 1313 by a **mapping** key
`note:` at the same indentation (6 spaces) as the sequence's `-` markers. A YAML
node cannot be both a sequence and a mapping. The file was hand-audited, not
parsed, by its author, which is exactly how this survives.

Consequence for this session: the specification was read **as text**, as
instructed. It was not repaired and not rewritten. Nothing downstream of this
session should assume `candidate_report.yaml` is machine-readable.

---

## 1. Pre-run structural algebra (derived before measurement, not measured)

Computed by `prereg_algebra.py` from the pinned `aes_reduced.py` primitives,
over GF(2) on 128-bit vectors. These are **theorems about the instrument**, not
observations, and they are fixed here before any cipher call.

Definitions used throughout, all operational on the pinned FIPS-197
column-major byte order (`state[r][c] = data[4c+r]`):

- `D_0` = diagonal space, free bytes `{0,5,10,15}`.
- `C_j` = column space, free bytes `{4j,4j+1,4j+2,4j+3}`.
- `M_j = MC(SR(C_j))` = mixed space. **Note the composition order**: `MC(C_j) =
  C_j` because MixColumns acts within a column, so the mixed space is the
  MixColumns image of the *ShiftRows image* of a column space, not of the column
  space itself.
- `M_J = ⊕_{j≠j0} M_j`, `dim = 96`, indexed by the single excluded column `j0`.

Verified facts (A1–A5):

- **A1**: `dim M_j = 32` for each `j`, and `M_0 ⊕ M_1 ⊕ M_2 ⊕ M_3 = GF(2)^128`
  (rank 128). So the complementary quotient projection `π` onto `M_{j0}` is
  well defined and 32-bit, and `c ⊕ c' ∈ M_J ⟺ π(c) = π(c')`.
- **A2**: `π(c) = ` column `j0` of `SR^{-1}(MC^{-1}(c))`, i.e.
  `π_r = ⊕_k invmix[r][k] · c[4·((j0−r) mod 4) + k]`, `r = 0..3`.
- **A3**: `M_0 ⊆ M_J ⟺ j0 ≠ 0`. Measured intersection dims:
  `dim(M_0 ∩ M_J) = 0, 32, 32, 32` for `j0 = 0,1,2,3`.
- **A4**: **`dim(SR(C_0) ∩ M_J) = 0` for every `j0 ∈ {0,1,2,3}`.**
- **A5**: `MC(SR(D_3'))` for the 3-byte sub-diagonal `D_3' = {0,5,10}` has
  dimension 24 but its basis **touches all four bytes `{0,1,2,3}` of column 0**.
  It is therefore **not a coordinate (byte-aligned) subspace**.

### 1.1 What A4 and A5 force, and the design change they compel

Under the pinned convention (C1: final round drops MixColumns), for a **full
`2^32` diagonal coset**:

- `r = 1`: output is a coset of `C_0` (SubBytes preserves a byte-aligned coset,
  ShiftRows relabels).
- `r = 2`: round 1 full, round 2 final. Output is a coset of `SR(C_0)`.
  By **A4** the intersection with `M_J` is `{0}`, so **`n_2 = 0` exactly**.
- `r = 2` with `final_mix_columns=True`: output is a coset of `M_0`. By **A3**,
  for `j0 ≠ 0` every difference lies in `M_J`, so **`n = C(N,2)` exactly and π
  is constant**; for `j0 = 0`, **`n = 0` exactly**.

**A5 is the design-changing fact.** The gate as specified in
`candidate_report.yaml` uses a **3-byte diagonal sub-coset of `2^24` texts**.
For that sub-coset the round-1 output space `MC(SR(D_3'))` is 24-dimensional
but **not byte-aligned**, so **SubBytes at round 2 does not preserve it** and
the subspace trail is destroyed at round 2 — for a reason that has **nothing to
do with depth**. The candidate report anticipates this only as a possibility
("Sub-coset degeneracy", confounder 1, and heuristic H2); A5 settles it
**affirmatively, by derivation, before any run**.

Consequence, pre-registered: **the `2^24` sub-coset arm cannot carry the
positive control at all**, because at `2^24` there is no round at which the
ciphertext set is a coset of a space with a known relation to `M_J`. The
positive control is only available on the **full `2^32` diagonal coset**.

**Therefore the primary arm of this session is the full `2^32` diagonal coset**,
not the `2^24` sub-coset. The `2^24` sub-coset arm is still run, because it is
cheap and it is what the proposal specified, but it is pre-registered as
**structurally degenerate** and no depth conclusion may be drawn from it in
either direction. This is a **protocol deviation from the proposal**, recorded
here before execution, with its derivation (A5) exposed so it can be attacked.

---

## 2. The object, frozen

For a key `K`, a coset `V` of a diagonal space, a round count `r`, and an
excluded column `j0`:

```
n_r = #{ unordered pairs {c,c'} ⊆ E_K^r(V), c ≠ c' : c ⊕ c' ∈ M_J }
    = Σ_b C(m_b, 2),   m_b = #{ x ∈ V : π(E_K^r(x)) = b }
```

`E_K^r` is `aes_reduced.AES(key, rounds=r, final_mix_columns=False)`, i.e.
`ARK0`, then `r−1` full rounds, then a final round without MixColumns, round
keys `RK[0..r]` from the untruncated FIPS-197 AES-128 schedule (conventions
C1/C2/C3).

**Tested statistic: `n_r mod 8`** (and `n_r mod 16`, recorded). `n_r` is always
recorded as an exact integer, never only as a residue.

---

## 3. Pre-registered predictions

Frozen. Not adjusted after runs begin. Not re-scored.

- **PR-1 (positive control, deterministic).** Full `2^32` diagonal coset,
  pinned convention, `r = 2`, any `j0`: **`n_2 = 0` exactly**, equivalently all
  `2^32` values of `π` are distinct and max bucket occupancy is exactly 1. This
  follows from A4 and is a joint test of the coset construction, the AES-NI
  encryption path, the projection `π`, and the pair counter.
- **PR-1b (positive control, saturating).** Same but
  `final_mix_columns=True`, `r = 2`, `j0 ≠ 0`: **π is constant**, so
  `n = C(2^32,2) = 9223372034707292160`, and `j0 = 0` gives **`n = 0`**.
- **PR-2 (null model, H1).** Under a random permutation at matched data
  complexity, `n_r mod 8` is uniform on `{0,…,7}`. `t` agreeing trials cost
  `8^{−t}` under this null.
- **PR-3 (the object).** If the object is real to depth `r*`, then for every
  `r ≤ r*` and every trial, `n_r ≡ 0 (mod 8)`. The falsifiable content is
  **the exact largest `r` at which every trial reads 0**.
- **PR-4 (decay requirement / artifact tell).** At `r = 10` the residue must
  **not** be identically 0 across trials. A residue that is flat across all
  rounds including `r = 10` is the canonical artifact tell.
- **PR-5 (sibling null).** The sibling-subspace arm — identical construction
  with `MC^{-1}` replaced by the inverse of a random invertible `4×4` GF(2^8)
  matrix `B ≠ MC`, giving a 96-dim subspace of the same shape that is **not** a
  MixColumns image of a column space — must **not** reproduce the target's
  residue at the rounds where the target shows one.
- **PR-6 (structure-destroying null).** Replacing the coset `V` by uniformly
  random plaintexts of the same cardinality must **not** reproduce the residue.
- **PR-7 (independent-round-key null).** Replacing the AES-128 key schedule by
  fresh independent uniform round keys, same wiring and same code path, must
  **not** reproduce the residue at rounds where the target shows one. This is
  the control MEAS-RT-C lacked.

### Decision rule, frozen

For each `(arm, r)`: report the exact count of trials whose `n_r mod 8` is 0,
and the full 8-bin residue histogram. "Survives at `r`" means **every** trial in
the AES arm reads residue 0 at that round **and** at least one null arm at the
same `r` does not. `p` under PR-2 for `t` agreeing trials is `8^{−t}`; with
`t < 8` the result is reported as underpowered and labelled as such. No other
statistic is substituted; no chi-square or bias measurement replaces the
residue.

---

## 4. VOID conditions

If any of these fires, the affected readings are **VOID**, classified
`invalid_measurement`, and are **not** reported as a negative observation:

- **V1**: PR-1 fails (`n_2 ≠ 0` on the full `2^32` coset, pinned convention).
  Instrument broken. **Checked first; execution stops if it fires.**
- **V2**: PR-1b fails.
- **V3**: The C AES-NI path disagrees with `aes_reduced.py` on any pinned
  vector, at any round count, in either final-MixColumns mode.
- **V4**: Residue 0 at every round including `r = 10` in the AES arm
  (artifact tell: failure to decay when the parameter meant to destroy the
  structure increases).
- **V5**: Counter overflow (any bucket exceeding 255 in the `uint8` array)
  without the saturating fast path. Occupancy histogram is reported for every
  run to demonstrate this did not happen.
- **V6**: `n_r` disagrees between the sum-over-buckets accumulation and the
  independent identity `n = (Σ_b m_b² − N)/2` computed from the same histogram.
- **V7**: The sibling null (PR-5) reads identically to the target at every
  round. The attribution to "mixed space" is withdrawn; the label is not doing
  the work.
- **V8**: Wall-clock halt at 2026-08-01T22:34:30Z is reached. Runs not started
  are reported as not run. **A budget halt is never reported as a null result
  and never as evidence about AES.**

---

## 5. Planned run grid (as intended before execution)

Priority order, executed top-down until the halt boundary:

1. **PIN**: C AES-NI vs `aes_reduced.py`, `r ∈ {1..10}`, both final-MC modes,
   plus FIPS-197 `r=10` known-answer vector. Blocks everything (V3).
2. **PC**: PR-1 at `2^32`, then PR-1b. Blocks everything (V1, V2).
3. **AES arm**, `2^32` full diagonal coset, `r ∈ {3,4,5,6,10}`, ≥2 trials each
   with independent keys, coset bases and `j0`.
4. **NULL-RK** (PR-7), **NULL-SIB** (PR-5), **NULL-RANDPT** (PR-6) at the rounds
   where the AES arm shows a residue, and at `r ∈ {4,5,6}` regardless.
5. **`r = 7`** at `2^32`, run **only if** the AES arm reads residue 0 at `r = 6`.
6. **Sub-coset arm** at `2^24`, `r ∈ {2,3,4,5,6,10}`, 20 trials — recorded, and
   pre-registered as structurally degenerate per A5.

Expected trial count at `2^32` is budget-limited and likely **below** the 20
trials the proposal asks for. That shortfall is pre-registered here as expected
and will be reported as achieved resolution, not smoothed over.

## 6. Sources of randomness, frozen

All randomness is derived from a single recorded master seed via
`hashlib.sha256`-based expansion in Python; the C program receives already-fixed
byte strings (round keys, coset base, matrices, plaintext-stream key) on its
command line and contains **no** internal RNG. Every per-trial seed, key, coset
base, `j0`, and matrix is recorded in the raw results JSON. `xorshift64` is not
used anywhere (MEAS-RT-C confounder).

Master seed: **`20260801`**.
