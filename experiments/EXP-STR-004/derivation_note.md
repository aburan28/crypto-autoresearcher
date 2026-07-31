# EXP-STR-004 derivation note

**Artifact class: `derivation`. Never `proved`.**

This is a written, self-contained argument, checkable by an independent reader
step by step against committed source code. Under
`docs/claims-and-verification.md` ("Refutation artifacts: proof before
rejection") it is a **derivation note**, rank 2 of the three refutation-artifact
classes — weaker than a counterexample certificate, stronger than
`empirical_only`. It is **not** a machine-checked proof and it is **not** a
theorem about ECDLP. It is an argument about the behaviour of four specific
committed Python functions on fourteen specific parameter cells.

It is written and archived **before** `EXP-STR-004` executes, and
`TASK-20260729-041` snapshot-commits it three commits before the ledger archive,
so its precedence over every measurement is a property of commit order that any
reader can check against Git.

- Contract: `experiments/EXP-STR-004/specification.yaml`
- Code under derivation: `harness/endomorphism_la.py` (unmodified, and never
  modified by this experiment)
- Obligation discharged in part: `DEFER-BATCH009-001`, via `DEC-20260727-009`
  which requires this note archived **before** execution

Every section states explicitly whether it is **EXACT** (a consequence of the
source text alone, or of the source text together with a hypothesis that the
driver *checks per cell*) or **CONDITIONAL** (depends on a property of the
committed code that this note has not verified).

---

## Notation

Fixed throughout, for one cell:

- `B` — the declared factor-base size of the cell. `q = B // 3`,
  `rho = B mod 3`. Every declared cell has `rho ∈ {0, 1}`; **`rho = 2` is out of
  scope and nothing here is claimed for it.**
- `tau(B) = { 3q, 3q+1, ..., B-1 }` — the **truncated tail index set**. It is
  empty when `rho = 0` and is the singleton `{3q}` when `rho = 1`.
- `F = [f_0, ..., f_{B-1}]` — the cell's factor base, a list of `B` distinct
  x-coordinates.
- `sigma` — the positional block-of-3 permutation of `{0, ..., B-1}` built as the
  matrix `Z` at `harness/endomorphism_la.py:174-183`:

  ```
  sigma(3j + k) = 3j + ((k + 1) mod 3)   for 3j + k < 3q
  sigma(i)      = i                       for i in tau(B)
  ```

  `sigma` is a permutation: it is a product of `q` disjoint 3-cycles on
  `[0, 3q)` together with `rho` fixed points. Hence **`sigma^3 = identity`**.
- For a row vector `v` of length `B`, the **shift action** is
  `(sigma . v)[sigma(i)] = v[i]`, equivalently `(sigma . v)[j] = v[sigma^{-1}(j)]`.
  This is the `shift_row` of `experiments/EXP-STR-003/driver/ablation_driver.py`
  lines 201-206 and is the action the frozen EXP-STR-003 contract uses in its
  `misaligned_row_count` definition.
- `M` — the matrix of the **first `B` rows** of the arm's final row list.
- `MIS = { i ∈ [0, B) : M[sigma(i)] ≠ sigma . M[i] }` — the **misalignment set**.
- `alpha` — the integer returned by
  `_measure_displacement_rank(rows, B, "phi", zeta3, p, n)`.

---

## D-1. The square-branch identity — EXACT

**Claim.** When the arm's final row list has at least `B` rows, the matrix whose
rank the committed code returns as `alpha` is

```
D[i][j] = M[i][j] - M[sigma(i)][sigma(j)]     (all arithmetic mod n)
```

**Derivation, from `harness/endomorphism_la.py:172-244`.**

1. `Z` is built at lines 173-183 as a `B × B` 0/1 matrix with
   `Z[3j][3j+1] = Z[3j+1][3j+2] = Z[3j+2][3j] = 1` for `j < q`, and `Z[k][k] = 1`
   for `k ∈ tau(B)`. So `Z[i][j] = 1` exactly when `j = sigma(i)`.
2. Therefore `(Z M)[i][j] = Σ_k Z[i][k] M[k][j] = M[sigma(i)][j]`, i.e. **left
   multiplication by `Z` permutes rows by `sigma`.**
3. `Z_inv` is built at lines 199-203 by `Z_inv[j][i] = 1` whenever `Z[i][j] = 1`,
   so `Z_inv[k][j] = 1` exactly when `k = sigma(j)`. Therefore
   `(A Z_inv)[i][j] = Σ_k A[i][k] Z_inv[k][j] = A[i][sigma(j)]`, i.e. **right
   multiplication by `Z_inv` permutes columns by `sigma`.**
4. Composing, `(Z M Z_inv)[i][j] = M[sigma(i)][sigma(j)]`.
5. Lines 220-223 select the branch: `sq_rows = min(rows, cols)`; the square
   branch is taken exactly when `rows >= cols = B`. Lines 235-242 then set
   `M_sq = M[:B]` and `diff[i][j] = (M_sq[i][j] - ZMZ_inv[i][j]) mod n`, and
   line 242 returns `matrix_rank_mod(diff, n)`.

Hence `alpha = rank_{Z/nZ}(D)` with `D` as claimed. ∎

*Exactness.* This is a transcription of the source text. It depends on the run
taking the **square** branch, which the contract requires at every cell
(`IV-5`) and which `R_base(B) = ceil(B/3) + 1` guarantees absent a shortfall of
two or more base rows, since the closure emits `3 · R_base ≥ B + 3` rows.

*Note on rows beyond the first `B`.* Line 235 discards them. **Any row of the
emitted stream at index `≥ B` is invisible to `alpha`.** This is why the
contract's budget is stated as a function of `B` and why extra collected rows are
truncated away before the closure rather than carried.

---

## D-2. When a row of the displacement matrix vanishes — EXACT

**Claim.** Row `i` of `D` is identically zero **iff** `M[sigma(i)] = sigma . M[i]`.
Consequently `MIS` is exactly the set of indices of the nonzero rows of `D`, and

```
alpha = rank(D) ≤ |MIS|.
```

**Derivation.** Row `i` of `D` is zero iff `M[i][j] = M[sigma(i)][sigma(j)]` for
all `j ∈ [0, B)`. Substituting `j' = sigma(j)` and using that `sigma` is a
bijection, this is equivalent to
`M[sigma(i)][j'] = M[i][sigma^{-1}(j')]` for all `j'`, i.e. to
`M[sigma(i)] = sigma . M[i]`. The rank of a matrix is at most its number of
nonzero rows. ∎

*Exactness.* Exact. This identity is the reason `MIS` — a **set** — is the
primary metric of this contract and `alpha` is derived from it, rather than the
other way round. It is also the rescoped derivational limb that `EV-STR-003`
observation **O-6** records as confirmed at 4 of 4 (criterion S3), carried here
as falsifier **F-2**.

*What is **not** derived.* Nothing here predicts `rank(D)` exactly. The bound
`alpha ≤ |MIS|` is one-sided. **This note does not adopt `DEC-20260727-009`'s
phrasing "alpha equal to the number of rows touching the truncated tail" as a
numeric prediction** — per `PRED-ID-STR` the contract pre-registers the *set*,
not the count, and only the inequality is derived.

---

## D-3. The factor base is a concatenation of phi-orbits — EXACT given a checked hypothesis

**Claim.** If `_build_phi_invariant_factor_base(inst, B, zeta3)` returns a list
of length exactly `B`, then for every complete block `j < q` and `k ∈ {0,1,2}`

```
F[3j + k] = zeta3^k · F[3j]  (mod p),
```

and the `B` entries are pairwise distinct.

**Derivation, from `harness/endomorphism_la.py:85-114`.** The builder appends
`orbit = [x, (zeta3·x) mod p, (zeta3²·x) mod p]` three elements at a time
(line 113), and only after checking `len(set(orbit)) == 3` (line 101), that no
element of the orbit already occurs in `xs` (lines 105-107), and that every
element lifts to a point of `E` (line 108). `xs` is therefore a concatenation of
whole, pairwise-disjoint orbits in the order `x, zeta3·x, zeta3²·x`. Line 114
returns `xs[:B]`. When `rho = 0` the truncation cuts at an orbit boundary and
`F` is a union of `q` whole orbits; when `rho = 1` it cuts one element into the
`(q+1)`-st orbit, leaving `F[3q] = x_q` with `zeta3·x_q` and `zeta3²·x_q`
**absent from `F`**. ∎

*Exactness.* Exact **given** the hypothesis `len(F) == B`. The builder returns a
**short** list if it cannot find enough whole orbits within its trial bound
`j < 50·B + 1000` (line 95). The contract therefore does not assume the
hypothesis: the driver asserts `len(F) == B` and asserts the displayed orbit
identity per cell (`CTRL-4`), and a failure invalidates the cell (`IV-4`).

*Supporting remark (EXACT, not load-bearing).* On a `j = 0` curve
`y² = x³ + b`, the three orbit members lift or fail to lift **together**, because
`(zeta3^k · x)³ + b = zeta3^{3k} x³ + b = x³ + b`. This is the same one-line fact
that makes `phi(x,y) = (zeta3·x, y)` an endomorphism at all. It bears on
feasibility — orbit candidates survive the `lift_x` filter at roughly the rate a
single x-coordinate does, not its cube — and on nothing else here.

---

## D-4. The two closures, as index maps — EXACT given D-3

Write `S_s` for the **committed multiplicative closure map** of arm A-prime
(`harness/endomorphism_la.py:292-304` for `m = 2`, `341-351` for `m = 3`, with
the line-303/304 zero filter and dedup **disabled**): for each set coordinate
`idx` of a row `v`, take `x = F[idx]`, form `shifted_x = zeta3^s · x mod p`, and
set coordinate `F.index(shifted_x)` **iff `shifted_x ∈ F`**; otherwise the
coordinate is silently dropped.

**Claim (a): on complete blocks the two closures agree.** For `idx = 3j + k < 3q`
and `s ∈ {1,2}`, by D-3 `zeta3^s · F[idx] = zeta3^{k+s} x_j = F[3j + ((k+s) mod 3)]`,
an index `< 3q ≤ B`. So `S_s` moves the mass at `idx` to `sigma^s(idx)`, exactly
as the positional map does.

**Claim (b): on the truncated tail at `rho = 1` the multiplicative map drops.**
For `idx = 3q` and `s ∈ {1,2}`, `zeta3^s · F[3q] = zeta3^s x_q` which by D-3 is
**not** in `F`. The coordinate is dropped. Conversely no index maps *into* `3q`
under `S_s`: an index `< 3q` maps to an index `< 3q`, and `3q` itself is
dropped. Meanwhile `sigma(3q) = 3q`, so the positional map **keeps** it.

**Consequence, `rho = 1`, as an identity of rows.** For any row `v`,

```
S_1 v = (sigma  . v)  with coordinate 3q zeroed
S_2 v = (sigma² . v)  with coordinate 3q zeroed
```

**Consequence, `rho = 0`.** `tau(B)` is empty, so `S_s = sigma^s` exactly, as
permutations of coordinates. ∎

*Exactness.* Exact given D-3.

*Consequence recorded in the contract.* At `rho = 0` the A-prime closure and the
E-prime closure are the **same** index map, so at the seven residue-zero cells
the arms differ in exactly one variable — the factor base. At `rho = 1` they
differ in two — the factor base **and** the tail behaviour of the closure.
The contract binds this to the reading of `F-4`.

---

## D-5. An unconditional closure emits a clean concatenation of triples — EXACT

**Claim.** With the zero filter and the dedup disabled, the emitted row list of
either arm is exactly

```
[ r_0, C_1 r_0, C_2 r_0, r_1, C_1 r_1, C_2 r_1, ..., r_{R-1}, C_1 r_{R-1}, C_2 r_{R-1} ]
```

of length `3R`, where `r_0, ..., r_{R-1}` are the `R = R_base(B)` base rows in
collection order, and `C_s = S_s` for arm A-prime, `C_s = sigma^s .` for arm
E-prime.

**Derivation.** The committed append block appends the base row and then, for
`shift in (1, 2)`, appends the shifted row **subject to**
`sum(shifted_row) > 0 and shifted_row not in relations` (line 303). Deleting
that condition — which is precisely what `DEC-20260727-009` specifies for arm
A-prime and what the contract specifies for arm E-prime — makes each append
unconditional, so exactly three rows are emitted per base row, in that order,
with no skips. Note also that both shifted rows are formed **from the base row**
`row`, not iteratively from the previous shifted row; for A-prime this matters
only through claim (a) of D-4, under which `S_2 = S_1 ∘ S_1` on complete blocks.
∎

*Exactness.* Exact. **This is the whole point of disabling the filter and the
dedup.** With them enabled, a single skipped emission shifts the phase of the
entire downstream stream, which is what `EV-STR-003` observation **O-4**
diagnoses as making `alpha` "a phase-tracking statistic of WHERE skips fall, not
of how many there are". The unconditional closure removes phase noise entirely,
which is what makes the prediction sharp.

*Contract hook.* The suppression count is therefore **zero by construction** in
both arms at every cell; it is pre-registered as zero, reported beside `alpha`
(`UC-2`), and a nonzero value invalidates the cell (`IV-8`) as a driver defect.

---

## D-6. The first `B` rows are aligned exactly when `B mod 3 == 0` — EXACT

Row index `i = 3j + k` of the emitted stream carries `C_k r_j` (with `C_0 = id`).
Because triples start at multiples of 3 and `sigma`'s blocks also start at
multiples of 3, **triple boundaries and `sigma`-block boundaries coincide**.

### Case `rho = 0`

The first `B = 3q` rows are exactly the `q` complete triples `j = 0, ..., q-1`,
and by D-4 `C_s = sigma^s .` for **both** arms. Check all three residues of `k`:

- `k = 0`: `sigma(3j) = 3j+1`, so `M[sigma(i)] = sigma . r_j = sigma . M[i]` ✓
- `k = 1`: `sigma(3j+1) = 3j+2`, so `M[sigma(i)] = sigma² . r_j`, and
  `sigma . M[i] = sigma . (sigma . r_j) = sigma² . r_j` ✓
- `k = 2`: `sigma(3j+2) = 3j`, so `M[sigma(i)] = r_j`, and
  `sigma . M[i] = sigma . (sigma² . r_j) = sigma³ . r_j = r_j` ✓ (using
  `sigma³ = id`)

Every row of `D` vanishes, so

```
MIS = ∅   and   alpha = 0   EXACTLY,   for BOTH arms, at every rho = 0 cell.
```

This is prediction **P-1** for arm A-prime, and the residue-zero half of the
derived consequence recorded beside **P-3** for arm E-prime.

### Case `rho = 1`

The first `B = 3q + 1` rows are the `q` complete triples `j = 0, ..., q-1`
(rows `0 .. 3q-1`) **plus one further row**, row `3q`, which is `r_q`, the first
element of triple `q`. The alignment argument above still applies to the
complete triples for arm E-prime (whose closure is a genuine permutation), but
row `3q` is a lone triple head with `sigma(3q) = 3q`, and for arm A-prime the
dropped tail coordinate of D-4(b) breaks two of the three checks. Section D-7
computes exactly which rows survive.

∎ *Exactness.* Exact given D-3, D-4 and D-5.

---

## D-7. The closed-form rule defining `T(cell)` — EXACT given D-3, D-4, D-5

`T(cell)` is the **predicted misalignment set**. It is a function of

1. the arm's base row list `r_0, ..., r_{R-1}` after truncation to `R = R_base(B)`,
   and
2. the truncated tail index set `tau(B)`,

and of nothing else. The driver computes it from artifacts that exist **before**
any `alpha` is measured — the factor base and the base row list, both
sha256-recorded — and writes it to the run record before the measured set.

### Arm A-prime

**`rho = 0`:**

```
T(A-prime, cell) = ∅          (D-6, case rho = 0)
```

**`rho = 1`**, with `tau(B) = {3q}`:

```
T(A-prime, cell) = T1 ∪ T2 ∪ T3,   where

  T1 = { 3j     : 0 ≤ j < q  and  r_j[3q] = 1 }
  T2 = { 3j + 2 : 0 ≤ j < q  and  r_j[3q] = 1 }
  T3 = { 3q }  if  sigma . r_q ≠ r_q,  and  ∅ otherwise.
```

**Derivation.** Write `c = r_j[3q] ∈ {0,1}`. By D-4(b),
`S_1 r_j = sigma . r_j − c·e_{3q}` and `S_2 r_j = sigma² . r_j − c·e_{3q}`, where
`e_{3q}` is the standard basis row and the subtraction just zeroes coordinate
`3q`. For a complete triple `j < q`:

- **`i = 3j`.** Need `M[3j+1] = sigma . M[3j]`, i.e. `S_1 r_j = sigma . r_j`.
  These differ exactly in coordinate `3q`, so the row is misaligned **iff
  `c = 1`**. Hence `T1`.
- **`i = 3j+1`.** Need `M[3j+2] = sigma . M[3j+1]`, i.e.
  `S_2 r_j = sigma . (S_1 r_j)`. Compute the right side:
  `sigma . (sigma . r_j − c·e_{3q}) = sigma² . r_j − c·sigma . e_{3q}
   = sigma² . r_j − c·e_{3q}` because `sigma(3q) = 3q`. Also
  `(sigma² . r_j)[3q] = r_j[sigma^{-2}(3q)] = r_j[3q] = c`, so the right side is
  `sigma² . r_j` with coordinate `3q` zeroed — which is exactly `S_2 r_j`.
  **This row always vanishes, whatever `c` is.** No contribution.
- **`i = 3j+2`.** `sigma(3j+2) = 3j`, so we need `M[3j] = sigma . M[3j+2]`, i.e.
  `r_j = sigma . (S_2 r_j) = sigma³ . r_j` with coordinate `sigma(3q) = 3q`
  zeroed `= r_j` with coordinate `3q` zeroed. Misaligned **iff `c = 1`**. Hence
  `T2`.
- **`i = 3q`** (the lone triple head). `sigma(3q) = 3q`, so the condition is
  `M[3q] = sigma . M[3q]`, i.e. `r_q = sigma . r_q`. Hence `T3`.

∎

**Reading of the rule.** Each base row that touches the truncated tail
contributes **two** misaligned rows, at positions `3j` and `3j+2` of the stream —
not one, and not one per touching coordinate. The lone tail row contributes at
most one more. So

```
|T(A-prime, cell)| = 2 · #{ j < q : r_j[3q] = 1 }  +  [ sigma . r_q ≠ r_q ]
```

and by D-2, `alpha(A-prime, cell) ≤ |T(A-prime, cell)|`.
**This count is a count and its members are exactly the set displayed above.**

### Arm E-prime

**`rho = 0`:** `T(E-prime, cell) = ∅` (D-6, case `rho = 0`).

**`rho = 1`:** the E-prime closure is the positional `sigma^s .`, a genuine
permutation with no dropped coordinates, so the three checks of D-6 case
`rho = 0` go through unchanged for every complete triple, **regardless of tail
support**. Only the lone triple head survives:

```
T(E-prime, cell) = { 3q }  if  sigma . r'_q ≠ r'_q,  and  ∅ otherwise,
```

where `r'_q` is *this arm's own* `(q+1)`-st base row (arm E-prime has a
different factor base and therefore a different base row list from arm A-prime).
Hence `|T(E-prime, cell)| ≤ 1` and `alpha(E-prime, cell) ≤ 1` at every
residue-one cell.

**When is `sigma . v = v`?** Exactly when `supp(v)` is a union of `sigma`-orbits,
i.e. when `supp(v) ∩ [0, 3q)` is a union of complete 3-blocks. For an `m = 2` row
(`|supp| ≤ 2`) that means `supp(v) ⊆ {3q}`. For an `m = 3` row (`|supp| ≤ 3`) it
means `supp(v) ⊆ {3q}` **or** `supp(v)` is exactly one complete block
`{3j, 3j+1, 3j+2}`. Both are possible and the rule is stated in the general form
`sigma . r_q ≠ r_q` so that no case analysis is needed at evaluation time.

### Predicted consequences for `P-3`, stated before execution

Combining: `T(E-prime) = T(A-prime)` **unconditionally at all seven residue-zero
cells**, and at a residue-one cell exactly when no arm-A-prime base row
`r_j` (`j < q`) touches `tau(B)` **and** the two arms agree on whether their own
last consumed base row is `sigma`-invariant. This is a **derived consequence**
recorded in advance in the contract beside `P-3`; it does not replace `P-3`,
which is what `RULE-BATCH014-SCOPE` pre-registered and what `F-1` and `F-4` are
evaluated against.

---

## D-8. What this note does **not** derive

Stated explicitly, because an undeclared basis is the failure and a missing proof
is not.

1. **It does not derive `rank(D)`.** Only `alpha ≤ |MIS|`. Every statement about
   the exact value of `alpha` at a residue-one cell is a **measurement**, not a
   derivation.
2. **CONDITIONAL: it does not verify that the committed collection returns the
   rows this note calls `r_0, ..., r_{R-1}`.** It assumes only that
   `_collect_relations(..., include_phi_orbits=False)` returns *some*
   deterministic list of 0/1 incidence rows over `F`, in a fixed order. Which
   rows those are depends on `semaev._find_decomposition`'s search order and on
   the target sequence at `endomorphism_la.py:272`, neither of which is analysed
   here. The rule for `T` is evaluated on whatever rows are actually returned,
   so this is a limitation on *predicting the members of `T` in advance of the
   run*, not on the rule's correctness.
3. **CONDITIONAL: it does not verify `len(F) == B` or the orbit layout.** Both
   are hypotheses of D-3 and both are turned into per-cell run-time assertions
   (`CTRL-4`) whose failure invalidates the cell (`IV-4`).
4. **CONDITIONAL: it does not verify that the driver implements the closures as
   specified.** That is checked instead by the pre-registered suppression count
   of zero (`IV-8`) and by the certificate/row-reconstruction assertion
   (`IV-10`).
5. **It says nothing about `B mod 3 = 2`.** No declared cell has that residue and
   the tail behaviour differs there: for `rho = 2` the multiplicative map is
   *partially* closed on the tail (`3q ↦ 3q+1` under `s = 1` and
   `3q+1 ↦ 3q` under `s = 2` are both inside `F`, while the other two images are
   not), so a different case analysis would be needed.
6. **It says nothing about H-STR-002's mechanism.** The mechanism — that `phi` is
   an automorphism, that `phi(R)` is a genuine relation whenever `R` is and `F`
   is `phi`-invariant, and that the closed system is `C_3`-equivariant — is a
   one-line consequence of `phi` being an automorphism and is **not in doubt**.
   **No arm of `EXP-STR-004` measures it, and nothing in this note bears on it in
   either direction.**

   *Derivational aside, not measured and not claimed as evidence:* at a
   residue-zero cell the appended rows of arm A-prime **would** be genuine
   relations, by exactly that automorphism property. This contract nevertheless
   emits certificate kind `none` for every appended row and **no record may
   describe either arm's matrix as a matrix of relations**. The aside is recorded
   because it explains *why* `alpha = 0` at residue-zero cells is not evidence
   for the mechanism: the mechanism is true, the closure makes the matrix
   `sigma`-equivariant **by construction**, and a construction with zero
   endomorphism content (arm E-prime) achieves the identical result.
7. **It derives no asymptotic statement.** Nothing here says `alpha = O(1)` and
   nothing here says it is not. The derivation is per-cell arithmetic on
   `B ≤ 193` at two toy curves.
8. **It derives no cost statement.** No time, no memory, no operation count, no
   baseline, no comparison to Wiedemann or to Pollard rho.

---

## D-9. What the derivation predicts the experiment will find, stated in advance

Recorded here so that it cannot be fitted afterwards, and so that a
favourable-looking ladder cannot be re-read as a mechanism result.

- At the **seven residue-zero cells** (`L12, L24, L48, L96, L192, X96, A12M3`):
  `MIS = ∅` and `alpha = 0` for **both** arms. Hence `F-1` does not fire, `F-2`
  does not fire, `F-4` does not fire at those cells, and `F-5` does not fire
  there.
- At the **seven residue-one cells** (`L13, L25, L49, L97, L193, X97, A13M3`):
  `MIS(A-prime) = T(A-prime)` per D-7, `MIS(E-prime) ⊆ {3q}`, and
  `alpha ≤ |MIS|` in both arms.
- Therefore the **expected verdict** is `instrument_artifact_confirmed` or
  `mixed`, and — this is the load-bearing sentence —

  > **Neither is support for `H-STR-002`.** A bound of 3 that a construction with
  > **zero endomorphism content** satisfies identically is a property of the
  > closure convention, not of the endomorphism.

- The **informative** outcome, and the one the derivation says will *not* occur,
  is `F-4` firing at a **residue-zero** cell: there the two closures are the same
  index map and the factor base is the only difference, so a disagreement would
  contradict this note and would be a finding about the derivation or about the
  committed code. `F-4` firing only at residue-one cells is explained by the
  truncated tail (D-4b) and is **not** evidence of endomorphism content.

---

## D-10. Provenance

The session that wrote this note had **no shell**: it ran no git command, no
parser, no validator, no allocator, no harness and no Sage, and it made no
commit. Every line above is derived from reading committed source text. No line
number, identity or claim in this note has been executed or machine-checked by
its author, and every step is written to be checked by a reader who has the same
source in front of them. Errors in it are defects to report against
`TASK-20260729-040`, not values to adjust after a measurement.
