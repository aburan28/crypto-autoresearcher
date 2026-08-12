# COUNT5 PRE-REGISTRATION (IMMUTABLE)

Written 2026-08-02, **before any cipher call in this session**.
Session start stamp: 2026-08-02T04:58:57Z. Halt boundary: start + 2700 s =
2026-08-02T05:43:57Z.

**Frozen at the moment of writing. Not edited afterwards.** Corrections, if
any, appear as separate `AMENDMENT-*.md` files with their own UTC stamp.

Role: Executor. Exploratory scratchpad gate, not an approved ledger
experiment. `claim_tier: toy`. `certificate.kind: none` (pure measurement; no
solve, no relation, no solution certificate is claimed or required).
**Nothing here asserts anything about AES security.** No hypothesis is
declared supported, rejected or closed; no heuristic validated or refuted.

Governing-contract status, reported not repaired: there is no
`experiments/<EXP-ID>/specification.yaml` with `status: approved` and non-null
`approved_by`. Missing fields relative to a formal contract: `experiment_id`,
`status`, `approved_by`, `budget.wall_clock_seconds`, `budget.memory_gb`,
`budget.maximum_runs`, `stopping_rules`, `required_artifacts`,
`certificate.kind`. `.../gate-rr78/candidate_report.yaml` does not parse as
YAML; it was read as text and NOT repaired.

---

## 1. Conventions (pinned)

Byte order: column-major FIPS-197, `state[row][col] = data[4*col+row]`.

Cipher `E_K^r` (convention C1/C2/C3 of the pinned `aes_reduced.py`):

```
s = P ^ RK[0]
for i in 1..r-1:  s = ARK_i(MC(SR(SB(s))))     # full rounds
s = ARK_r(SR(SB(s)))                            # final round, NO MixColumns
```

Subspaces, all dimension 32 per index:

- `D_j`  (forward / plaintext diagonal) = bytes `{4*((j+t)%4)+t : t=0..3}`.
  `D_0 = {0,5,10,15}`.
- `C_j`  (column) = bytes `{4j, 4j+1, 4j+2, 4j+3}`.
- `ID_j = SR(C_j)` (inverse-ShiftRows / ciphertext diagonal) =
  bytes `{4*((j-t)%4)+t : t=0..3}`. `ID_0 = {0,5,10,15}`, `ID_1 = {4,9,14,3}`.
- `M_j = MC(SR(C_j)) = MC(ID_j)` (mixed space).

For an excluded column index `j0`, write `X_J = ⊕_{j≠j0} X_j` (dim 96).

## 2. THE OBJECT

Input set `V` = the **full 2^32 coset of `D_0`**: 16-byte base `b`, with the
four bytes at `{0,5,10,15}` ranging over all 2^32 values and the other twelve
fixed at `b`.

Output projection, for excluded index `j0`:

```
pi_{j0}(c) = the 4 ciphertext bytes at ID_{j0}, packed little-endian by row:
             pi = sum_{t=0..3} c[4*((j0-t) mod 4)+t] << (8t)
```

Counted quantity:

```
n_r(K, b, j0) = #{ unordered pairs {c,c'} in E_K^r(V), c != c' : c ^ c' in ID_J }
              = sum_v C(m_v, 2),   m_v = #{ x in V : pi_{j0}(E_K^r(x)) = v }
```

`n_r` is always recorded as an exact integer, never only as a residue.
Tested statistic: **`n_r mod 8`** (mod 16 also recorded).

### 2.1 WHY THIS PROJECTION AND NOT THE ONE GATE-RR78-1 USED

GATE-RR78-1 encrypted with the final round **without** MixColumns (C1) but
projected with `pi(c) = column j0 of SR^{-1}(MC^{-1}(c))`, i.e. it tested
`c ^ c' in M_J`. Under a MixColumns-less final round that condition pulls back
through `c = ARK(SR(SB(y)))` to

```
SB(y) ^ SB(y') in SR^{-1} MC SR (C_J)
```

which is **not a byte-aligned (coordinate) subspace**, so it does not pull
back through SubBytes at all. The mixed space `M_J` is the correct output
space only when the last round **includes** MixColumns. With C1 the matching
output space is `ID_J = SR(C_J)`, because

```
c ^ c' in SR(C_J)  <=>  SB(y) ^ SB(y') in C_J  <=>  y ^ y' in C_J
```

(SubBytes is byte-wise, so it preserves byte-aligned supports). GATE-RR78-1
therefore combined a C1 cipher with a `final_mix_columns=True` output space.
**That mismatch is a mis-specification of the object, fixed here.**

## 3. DERIVATION (done before measurement; these are theorems, not data)

### 3.1 Forward trail

`V` is a coset of `D_0`. SubBytes is byte-wise so `SB(V)` is a coset of `D_0`;
`SR` maps it to a coset of `C_0`; `MC` preserves each column space, so after
**round 1** the state set `U` is a **full coset of `C_0`**. Round 2:
`SB(U)` is a coset of `C_0`, `SR` gives a coset of `ID_0`, `MC` gives a coset
of `M_0`. So after **round 2** the state set `W` is a **full coset of `M_0`**.

### 3.2 The per-column parameterisation of a coset of M_0 (key lemma)

Write `w = MC(SR(u)) ^ k2`, `u` in the coset of `C_0`. `SR(u)` puts the four
free bytes `u_t` (t = row) at positions `(row t, col (-t) mod 4)`, one per
column. `MC` acts column-wise, so **column `m` of `w` is**

```
w[:,m] = b_m ^ a_m * v_m ,   a_m := u_{(-m) mod 4} ,  v_m := MC[:, (-m) mod 4]
```

i.e. **column `m` of `w` is an affine function of exactly ONE free byte
`a_m`**, and the four `a_m` range independently over all of GF(2^8). `v_m` has
all four entries nonzero (MixColumns is MDS). This product structure
`W = A_0 x A_1 x A_2 x A_3` is the entire source of everything below.

### 3.3 Pull-back of the output condition

Let `y_i` denote the state after `i` full rounds. For an `r`-round cipher the
condition `c ^ c' in ID_J` is equivalent to `y_{r-1} ^ y'_{r-1} in C_J`
(section 2.1). One more round back: `y_{i} = ARK(MC(SR(SB(y_{i-1}))))`, and
`MC` preserves column spaces, so

```
y_i ^ y'_i in C_J  <=>  SR(SB(y_{i-1}) ^ SB(y'_{i-1})) in C_J
                    <=>  SB(y_{i-1}) ^ SB(y'_{i-1}) in D_J
                    <=>  y_{i-1} ^ y'_{i-1} in D_J        (byte-aligned)
```

### 3.4 Exact values at r = 1, 2, 3, 4

- **r = 1.** Condition `<=> p ^ p' in C_J`. `p ^ p' in D_0`, whose byte in
  column `j0` sits at index `5*j0`. So exactly the pairs agreeing in that one
  free byte: `n_1 = 256 * C(2^24, 2) = 2^31 * (2^24 - 1) = 36028794871480320`,
  independent of key and base.
- **r = 2.** Condition `<=> u ^ u' in C_J`, `u` in the full coset of `C_0`.
  - `j0 = 0`: forces `u = u'`, so **`n_2 = 0` exactly**.
  - `j0 != 0`: always true, so **`n_2 = C(2^32,2) = 9223372034707292160`**.
- **r = 3.** Condition `<=> w ^ w' in C_J`, `w` in the full coset of `M_0`.
  By 3.2 this is `a_{j0} = a'_{j0}` with the other three bytes free:
  **`n_3 = 256 * C(2^24,2) = 2^31 * (2^24 - 1) = 36028794871480320`**, exactly,
  for every key, base and `j0`. (Same value as `n_1`.)
- **r = 4.** Condition `<=> w ^ w' in D_J` (3.3 applied once to `w`), i.e. the
  round-3 output difference vanishes on diagonal `j0`. Round 3 is
  `MC(SR(SB(.)))`. Zero on `D_j0` after `MC(SR(.))`: column `j0` of `SR(Delta)`
  must be zero (`MC` invertible), where `Delta = SB(w) ^ SB(w')`. Column `j0`
  of `SR(Delta)` collects `Delta[t][(j0+t) mod 4]` for `t = 0..3` -- **one byte
  from each of the four columns**. By 3.2, `Delta[t][m] = 0` iff
  `a_m * v_m[t] = a'_m * v_m[t]` iff `a_m = a'_m` (`v_m[t] != 0`). All four
  columns forced equal, so `w = w'`. **`n_4 = 0` exactly**, for every key, base
  and `j0`.

  (GATE-RR78-1 measured `n_4 = 2147497085` under its mis-specified projection.
  The corrected object predicts exactly 0. This is the sharpest discriminator
  in this session.)

### 3.5 r = 5: the multiple-of-8, DERIVED

For `r = 5` the condition pulls back to `R(w) ^ R(w') in D_J` with `w, w'` in
the full coset of `M_0` and `R` one full round. With `Delta = SB(w) ^ SB(w')`
the condition is: for each row `i`, at column `m_i = (j0 - i) mod 4`,

```
sum_t MC[i][t] * Delta[t][(m_i + t) mod 4] = 0 .
```

Each term reads one byte of one column. Group by column: define, for column
`col`,

```
g_col(a_col, a'_col)[i] = MC[i][t] * f_{col,t}(a_col, a'_col),  t = (col - j0 + i) mod 4
f_{col,t}(a, a') = S(b_col[t] ^ a*v_col[t]) ^ S(b_col[t] ^ a'*v_col[t])
```

and the condition is `sum_{col} g_col(a_col, a'_col) = 0` in GF(2^8)^4.

Two facts:

1. **`g_col` depends only on the UNORDERED pair `{a_col, a'_col}`** (`f` is
   symmetric), and `g_col(a,a) = 0`.
2. `MC` has no zero entry, and `v_col[t] != 0`, so `g_col = 0` with `a != a'`
   is impossible: it would force `f_{col,t} = 0` for all four `t`, i.e.
   `a = a'`.

Let `k` = number of columns with `a_col != a'_col` (equivalently the number of
active columns of `w ^ w'`). Count unordered pairs by `k`:

- `k = 0`: `w = w'`, excluded.
- `k = 1`: impossible by fact 2.
- `k = 2, 3`: the `4-k` inactive columns carry a **free shared value**, giving a
  factor `256^{4-k}`. Contribution `= 256^{4-k} * N_ord^{(k)} / 2`, a multiple
  of `2^15` (k=2) resp. `2^7` (k=3). Both are multiples of 8.
- `k = 4`: by fact 1, swapping the coordinates of `(A, A')` on any subset
  `T ⊆ {0,1,2,3}` leaves every unordered pair `{a_col, a'_col}` -- hence the
  whole condition -- invariant. With all four columns differing, the 16 subsets
  give 16 **distinct** ordered pairs, so `N_ord^{(4)} ≡ 0 mod 16` and the
  contribution `N_ord^{(4)}/2` is a multiple of 8.

Summing: **`n_5 ≡ 0 (mod 8)` for every key, every base, every `j0`.** The
modulus is exactly 8 and not 16: the `k = 4` orbit argument gives only 8.

**Why the full 2^32 coset is required.** With only `q < 4` free diagonal bytes
the orbit argument gives only `2^{q-1}`, so a `2^24` sub-coset can force at
most a multiple of 4; and worse, a sub-coset's round-2 image is a
non-product-form subset of the coset of `M_0` (the round-1 image is a
non-byte-aligned 24-dimensional set, so SubBytes at round 2 does not preserve
the product structure), so the swap orbit leaves the data set entirely and
nothing at all is forced. GATE-RR78-1's fact A5 was right about the 2^24 arm,
for this reason.

### 3.6 r = 6: NOT forced

For `r = 6` the condition pulls back to `R^2(w) ^ R^2(w') in D_J`. Round 3
mixes values across columns, so neither the per-column decomposition (3.5 fact
1) nor the free-inactive-column factor survives. Nothing is forced. `r = 5` is
the **deepest round at which the property is forced by this derivation**.

## 4. PRE-REGISTERED PREDICTIONS (frozen)

- **PR-A (positive controls, exact).** `n_2(j0=0) = 0`;
  `n_2(j0!=0) = 9223372034707292160`; `n_3 = 36028794871480320`;
  **`n_4 = 0`**. Exact integers, any key/base/j0. Each trial that matches an
  exact >=55-bit value carries far more than the 3 bits of a mod-8 reading, so
  2-3 trials here are decisive; this is why trial budget is spent on r=5/r=6.
- **PR-B (the object).** `n_5 ≡ 0 mod 8` in **every** trial, 20 trials with
  independent keys, bases and `j0`. Under the uniform null (PR-C) 20 agreeing
  trials cost `8^-20 = 2^-60`.
- **PR-C (null model).** Under a random permutation at matched data
  complexity, `n_r mod 8` is uniform on `{0..7}`.
- **PR-D (round-key null / structural check).** With 11 independent uniform
  round keys replacing the AES-128 schedule, `n_5 ≡ 0 mod 8` must **still**
  hold: the derivation uses no key-schedule property. A failure here is an
  implementation fault, not evidence.
- **PR-E (sibling null, isolates the exploited output geometry).** Identical
  everything, but `pi` reads the **forward** diagonal `D_{j0}` instead of
  `ID_{j0}` (wrong ShiftRows handedness, same shape, same 32 bits). Must NOT
  be forced to 0 mod 8 at r=5.
- **PR-F (random-permutation control).** Same coset, same `pi`, cipher
  replaced by full 10-round AES-128 (surrogate for a random permutation, at
  identical data complexity 2^32). Residues must NOT be identically 0.
- **PR-G (structure-destroying null).** Plaintexts replaced by 2^32 values
  whose four D_0 bytes are a keyed pseudorandom scramble of the counter (still
  16 bytes, same base elsewhere) so the input set is a random subset rather
  than a coset. Must NOT be forced.
- **PR-H (decay).** `n_6 mod 8` must NOT be identically 0 over trials if the
  effect is depth-limited as derived. A residue flat to 0 at every round
  including r=10 is the canonical artifact tell.

### Decision rule, frozen

For each `(arm, r)`: report the exact `n` per trial, the 8-bin residue
histogram, and the count of trials reading 0. "Survives at `r`" means **every**
trial of the AES arm reads residue 0 at `r` **and** at least one null arm at
the same `r` does not. `p` under PR-C for `t` agreeing trials is `8^-t`. With
`t < 8` a mod-8 arm is reported as underpowered and labelled so. No other
statistic is substituted.

## 5. VOID conditions

If any fires, the affected readings are **VOID** / `invalid_measurement`, never
a negative observation:

- **V1**: any PR-A control fails. Instrument broken; checked FIRST, execution
  stops.
- **V2**: the C AES-NI path disagrees with `aes_reduced.py` or with
  pycryptodome on any pinned vector, at any round count used.
- **V3**: `sum_v m_v != N`, or `n` from `sum_v C(m_v,2)` disagrees with the
  independent identity `n = (sum_v m_v^2 - N)/2` from the same occupancy
  histogram.
- **V4**: counter overflow (any occupancy reaching 255).
- **V5**: residue 0 at every round including the 10-round surrogate (PR-F/PR-H
  artifact tell).
- **V6**: wall-clock halt at 2026-08-02T05:43:57Z. Runs not started are
  reported as not run. **A budget halt is never a null result and never
  evidence about AES.**

## 6. Randomness

Single master seed **`20260802`**; all keys, bases, `j0`, round keys and
scramble keys derived from it by SHA-256 expansion in Python and passed to the
C program on the command line. The C program contains **no RNG**. Every
per-trial parameter is recorded in the raw JSONL.

## 7. Planned grid (priority order, executed top-down until halt)

1. PIN: C AES-NI vs `aes_reduced.py` vs pycryptodome, r = 1..10, FIPS-197 KAT.
2. PC (PR-A): r=2 j0=0, r=2 j0=1, r=3, r=4 -- blocks everything.
3. r=5 AES arm, 20 trials, independent key/base/j0.
4. r=6 AES arm, 20 trials.
5. r=3 and r=4 additional trials (exact predictions).
6. Nulls PR-D, PR-E, PR-F, PR-G at r=5.
7. r=7 only if r=6 reads 0 in every trial.

Expected cost is ~20-30 s per 2^32 configuration; the grid is budget-limited
and any shortfall is reported as achieved resolution, not smoothed over.
