# TASK-20260729-042 — independent re-derivation of the EXP-STR-004 derivation note

Report id: `RT-20260729-034`. Task: `TASK-20260729-042`.
Reviewed snapshot: commit `7c9aa579a44305afd9a8c967bc408f88fb8f48da`, parent
`68e4b9b740c70b84c99dddc3b779f8d23b74bfed`, branch `claude/ecdlp-b011`,
worktree HEAD `561495cd59ca27ddd033c504b01aa53f9c024b64`.

**Method.** Every claim below was re-derived from the committed source text of
`harness/endomorphism_la.py`, `harness/semaev.py`, `harness/toycurve.py` and
`harness/runner.py` read at the reviewed HEAD. The derivation note was read
*after* each step was worked out independently, and is cited only to say whether
it agrees. No harness function was executed. One synthetic, index-only
simulation was run **outside the repository** in a scratch directory to test the
new rank result of section 6; it touches no curve, no harness and no repository
file, it is **not archived, not evidence and not citable**, and section 6's
result stands on the algebra alone.

**Snapshot integrity, checked first.** The SHA-256 of all three reviewed files
at commit `7c9aa579` equals the values recorded in
`archives/TASK-20260729-041/snapshot_commit_receipt.json` and equals the
worktree copies; `git diff 7c9aa579 561495cd` is empty for all three; the
tracked tree is clean. `experiments/EXP-STR-004/` contains exactly the two
reviewed files and no driver. No `EV-STR-004`, no `DEC-20260729-004` and no
`RUN-STR-004-*` path exists anywhere in the tree at the reviewed HEAD.

---

## 1. The square-branch identity (note D-1) — REPRODUCED, EXACT

`_measure_displacement_rank(rows_list, B, "phi", ...)` at lines 122-244:

- Lines 173-183 build `Z` with `num_orbits = B // 3 = q`, `Z[3j][3j+1] =
  Z[3j+1][3j+2] = Z[3j+2][3j] = 1` for `j < q`, and `Z[k][k] = 1` for
  `3q <= k < B`. So `Z[i][j] = 1` iff `j = sigma(i)` with
  `sigma(3j+k) = 3j + ((k+1) mod 3)` on `[0, 3q)` and `sigma(i) = i` on the
  tail. `sigma` is a product of `q` disjoint 3-cycles plus `rho` fixed points,
  so `sigma^3 = id`.
- `(Z M)[i][j] = M[sigma(i)][j]`. Lines 199-203 set `Z_inv[j][i] = 1` whenever
  `Z[i][j] = 1`, i.e. `Z_inv[k][l] = 1` iff `k = sigma(l)`, so
  `(A Z_inv)[i][j] = A[i][sigma(j)]`. Composing,
  `(Z M_sq Z_inv)[i][j] = M[sigma(i)][sigma(j)]`.
- Lines 220-223: `sq_rows = min(rows, cols)`; the rectangular branch is entered
  iff `sq_rows < cols`, i.e. iff `rows < B`. Therefore the **square branch is
  entered exactly when `rows_final - B >= 0`**. Lines 235-242 set
  `M_sq = M[:B]` and `diff[i][j] = (M_sq[i][j] - ZMZ_inv[i][j]) mod n`.

Hence `alpha = rank_{Z/nZ}(D)` with `D[i][j] = M[i][j] - M[sigma(i)][sigma(j)]`.
**Agrees with D-1.** The one guard the note does not mention is line 133,
`if not relation_matrix_rows: return 0`, which returns 0 without entering either
branch; it is covered by `SR-10` and does not affect the identity.

## 2. Row vanishing (note D-2) — REPRODUCED, EXACT

Row `i` of `D` is zero iff `M[i][j] = M[sigma(i)][sigma(j)]` for all `j`.
Substituting `j' = sigma(j)` and using bijectivity, this is
`M[sigma(i)][j'] = M[i][sigma^{-1}(j')] = (sigma . M[i])[j']` for all `j'`, i.e.
`M[sigma(i)] = sigma . M[i]`. Entries are `0/1` and `n >= 5` is enforced at
`endomorphism_la.py:61`, so a differing pair of entries is nonzero mod `n` and no
false cancellation is possible. `alpha = rank(D) <= |MIS|`. **Agrees with D-2.**

## 3. Orbit layout of the factor base (note D-3) — REPRODUCED, EXACT under the stated hypothesis

`_build_phi_invariant_factor_base` (lines 85-114) extends `xs` three at a time
with `[x, zeta3 x, zeta3^2 x]` only after `len(set(orbit)) == 3`, no orbit member
already in `xs`, and every member lifting; it returns `xs[:B]`. So `F[3j+k] =
zeta3^k F[3j]` on complete blocks and the `B` entries are pairwise distinct. At
`rho = 1` the loop condition `len(xs) < B` admits one extra whole orbit and the
slice keeps only its head, so `F[3q] = x_q` while `zeta3 x_q` and `zeta3^2 x_q`
are **absent** from `F` — the rejection test `if ox in xs` guarantees they are
not elsewhere in `F` either. **Agrees with D-3**, including the `j = 0`
lift-together remark, which follows from `(zeta3^k x)^3 + b = x^3 + b`.

## 4. The two closure index maps (note D-4) — REPRODUCED, EXACT given D-3

The committed append block (lines 292-304 for `m = 2`, 341-351 for `m = 3`) maps
each set coordinate `idx` to `factor_base.index(zeta3^s F[idx] mod p)` when that
value is in `F`, and drops it otherwise. On a complete block this is
`sigma^s(idx)`. At `idx = 3q` the image is absent from `F`, so the coordinate is
dropped; and no index maps **into** `3q`, since indices below `3q` stay below
`3q`. Because `sigma(3q) = 3q`, `(sigma^s . v)[3q] = v[3q]`, so

```
S_s v = (sigma^s . v) with coordinate 3q zeroed      (rho = 1)
S_s   = sigma^s exactly                              (rho = 0)
```

**Agrees with D-4.**

## 5. Stream shape (D-5) and residue-zero alignment (D-6) — REPRODUCED, EXACT

With the line-303/304 zero filter and dedup deleted, each base row emits exactly
three rows in the order `r, C_1 r, C_2 r`, so the stream is a clean
concatenation of triples; note that both shifted rows are built from `row`, not
iteratively, which matters only through D-4(a). At `rho = 0` the first
`B = 3q` rows are the `q` complete triples and `C_s = sigma^s` for **both** arms,
so all three residue checks pass and `MIS = {}`, `alpha = 0` exactly.

**A point the note leaves implicit and which is worth stating:** the residue-zero
result uses nothing whatever about the base rows `r_j`. It is a property of the
closure alone. Consequently `alpha = 0` at a residue-zero cell is forced for arm
E-prime by construction, not by any property of its factor base, and `F-4`
firing at a residue-zero cell cannot be evidence that the phi-invariant factor
base "does something": it can only mean the derivation, the driver or `D-3`
failed. See objection **O-4** in `contract_review.yaml`.

*Robustness to shortfall, checked independently.* At `rho = 0` a shortfall of one
base row leaves `rows_final = 3q = B` (square branch retained, first `B` rows
still the `q` triples); at `rho = 1` a shortfall of one leaves `rows_final = B+2`
and row `3q = r_q` still exists because `R = q+1`. A shortfall of two loses the
square branch in both cases. The note's "absent a shortfall of two or more" is
correct.

## 6. The closed-form set `T` (note D-7) — REPRODUCED, and then STRENGTHENED

### 6.1 The rule itself is correct

At `rho = 1`, `M[3j] = r_j`, `M[3j+1] = S_1 r_j`, `M[3j+2] = S_2 r_j` for
`j < q`, and `M[3q] = r_q`. Write `c = r_j[3q]`. All comparisons stay in range,
because `sigma` maps each complete block to itself and fixes `3q`.

- `i = 3j`: need `S_1 r_j = sigma . r_j`. They differ only at coordinate `3q`,
  where the left side is `0` and the right side is `c`. **Misaligned iff
  `c = 1`.**
- `i = 3j+1`: need `S_2 r_j = sigma . (S_1 r_j)`. Now
  `sigma . (sigma . r_j - c e_{3q}) = sigma^2 . r_j - c (sigma . e_{3q})
  = sigma^2 . r_j - c e_{3q}`, because `sigma . e_{3q} = e_{3q}`; and
  `(sigma^2 . r_j)[3q] = r_j[sigma^{-2}(3q)] = r_j[3q] = c`, so that expression
  is exactly `sigma^2 . r_j` with coordinate `3q` zeroed, which is `S_2 r_j`.
  **This row vanishes for every value of `c`.** The note's "provably always
  vanishes" claim is CONFIRMED.
- `i = 3j+2`: need `r_j = sigma . (S_2 r_j) = sigma^3 . r_j - c e_{3q}
  = r_j` with coordinate `3q` zeroed. **Misaligned iff `c = 1`.**
- `i = 3q`: `sigma(3q) = 3q`, so the condition is `r_q = sigma . r_q`.

So `T(A-prime) = T1 ∪ T2 ∪ T3` with `T1 = {3j : r_j[3q] = 1}`,
`T2 = {3j+2 : r_j[3q] = 1}`, `T3 = {3q}` iff `sigma . r_q != r_q`; the three
parts are pairwise disjoint, so
`|T| = 2 · #{j < q : r_j[3q] = 1} + [sigma . r_q != r_q]`.
**The closed form of D-7 is correct, complete and exhaustive over the `q + 1`
rows of the square block.** The `sigma`-invariance case analysis
(`supp(v) ⊆ {3q}` or one whole block, for `m <= 3`) is also correct: the
`sigma`-orbits are the `q` blocks plus the fixed point `{3q}`, and a
`sigma`-invariant support of size `<= 3` is `{}`, `{3q}` or one whole block.
Arm E-prime's `T(E-prime) = {3q}` iff `sigma . r'_q != r'_q` likewise reproduces.

### 6.2 The rank itself is exactly derivable, and the note stops one step early

Computing the **rows of `D`** rather than only their vanishing:

- `D[3j][l] = r_j[l] - (S_1 r_j)[sigma(l)]`. For `sigma(l) != 3q` this is
  `r_j[l] - r_j[l] = 0`; for `l = 3q` it is `c - 0 = c`. So
  **`D[3j] = c · e_{3q}`.**
- `D[3j+2][l] = (S_2 r_j)[l] - r_j[sigma(l)]`. For `l != 3q` this is
  `r_j[sigma(l)] - r_j[sigma(l)] = 0`; for `l = 3q` it is `0 - c = -c`. So
  **`D[3j+2] = -c · e_{3q}`.**
- `D[3j+1] = 0` (section 6.1).
- `D[3q][l] = r_q[l] - r_q[sigma(l)]`, i.e. `D[3q] = r_q - sigma^{-1} . r_q`,
  whose `3q` coordinate is `r_q[3q] - r_q[sigma(3q)] = 0`.

**Every tail-induced row of `D` is a scalar multiple of the single vector
`e_{3q}`, and `D[3q]` is orthogonal to that coordinate.** Therefore, exactly:

```
alpha(A-prime, rho = 1 cell) = [ exists j < q with r_j[3q] = 1 ]
                             + [ sigma . r_q != r_q ]            ∈ {0, 1, 2}
alpha(A-prime, rho = 0 cell) = 0
alpha(E-prime, rho = 1 cell) = [ sigma . r'_q != r'_q ]          ∈ {0, 1}
alpha(E-prime, rho = 0 cell) = 0
```

An index-only synthetic check (outside the repository, **not evidence**) over
`B ∈ {12,13,24,25,48,49,96,97,192,193}`, `m ∈ {2,3}` and 60 random base-row
draws each — 1200 configurations — returned a maximum of `alpha(AP) = 2` and
`alpha(EP) = 1`, and exhibited `B = 193` cases with `|MIS(AP)| = 5` and
`alpha(AP) = 2`.

Two consequences, both load-bearing:

1. `DEC-20260727-009`'s phrasing "alpha equal to the number of rows touching the
   truncated tail otherwise" is **provably wrong as a numeric prediction**. The
   contract's `P-2.form` clause was right to refuse it, and this is the reason:
   all the tail rows of `D` are parallel.
2. The feasibility table's statement that "**Two** base rows touching the tail
   already give `|T| >= 4`, so `alpha > 3` is arithmetically available and
   **F-5 CAN FIRE for arm A-prime**" is **false**. `|T| >= 4` does not make
   `alpha >= 4`; `alpha <= 2` always. This is a **count read as a magnitude**,
   in the load-bearing place where the design's own headline falsifier is
   certified non-vacuous. It is reported as objection **O-1** and as the sixth
   cardinality-not-identity instance.

`D-8` item 1 ("It does not derive `rank(D)`. Only `alpha <= |MIS|`") is therefore
an **under-derivation, not a limitation**: `rank(D)` is derivable exactly, in
four lines, from the same computation that produces `T`.

## 7. The fourteen cells and the square branch — CHECKED CELL BY CELL

`R_base(B) = (B+2)//3 + 1`, `rows_final = 3 R_base`, square branch iff
`rows_final - B >= 0` (section 1).

| cell | B | q | R_base | rows_final | rows_final − B | branch |
|---|---|---|---|---|---|---|
| L12 | 12 | 4 | 5 | 15 | 3 | square |
| L13 | 13 | 4 | 6 | 18 | 5 | square |
| L24 | 24 | 8 | 9 | 27 | 3 | square |
| L25 | 25 | 8 | 10 | 30 | 5 | square |
| L48 | 48 | 16 | 17 | 51 | 3 | square |
| L49 | 49 | 16 | 18 | 54 | 5 | square |
| L96 | 96 | 32 | 33 | 99 | 3 | square |
| L97 | 97 | 32 | 34 | 102 | 5 | square |
| L192 | 192 | 64 | 65 | 195 | 3 | square |
| L193 | 193 | 64 | 66 | 198 | 5 | square |
| X96 | 96 | 32 | 33 | 99 | 3 | square |
| X97 | 97 | 32 | 34 | 102 | 5 | square |
| A12M3 | 12 | 4 | 5 | 15 | 3 | square |
| A13M3 | 13 | 4 | 6 | 18 | 5 | square |

**All fourteen take the square branch, absent a base-row shortfall of two or
more.** The contract's and the feasibility table's `q`, `tau`, `R_base`, `Q` and
`rows_final` columns are all arithmetically correct; so are the derived
groupings (seven residue-zero, seven residue-one), the run count 28 as the
product of two arm codes and fourteen cell names, the 174-path declaration
(`28 x 6 + 6`, and the queue's `declared_commit_sets` does contain exactly
`28` run ids, `6` per-run files and `6` additional paths), and the stage budget
sums (optimistic `60+10+300+100+30+5 = 505`; pessimistic
`900+120+3000+1500+900+60 = 6480`; headroom `7200 - 6480 = 720`).

## 8. The one arithmetic gap the feasibility table did not close

The table's shortfall analysis anchors on `EV-STR-003` O-10(a) (`hits = 15`,
`attempts = 27` at `B = 27`, verified present in the committed record) and scales
the per-target rate by `(B/27)^2`. The scaled numbers reproduce
(`0.5556 · (12/27)^2 = 0.110`, `· (13/27)^2 = 0.129`, `· (24/27)^2 = 0.439`,
`· (25/27)^2 = 0.476`; `× 300` gives `33, 39, 131, 143`; headrooms `6.6x` and
`6.5x`). The prose sentence "the per-target decomposition probability **falls**
roughly like `B^2`" is inverted — the table's own arithmetic has it **grow** —
but that is wording, not error.

What the table does **not** do is bound the quantity that actually binds at the
top of the ladder. The committed target sequence is

```
k = ((t_idx + 1) * c) mod (n - 1) + 1,   c = max(2, seed mod max(2, n - 3))
```

with `seen_targets` deduplicating by x-coordinate. The number of **distinct**
targets is at most `(n - 1) / gcd(c, n - 1)`, which is a function of the derived
seed and `n` and is **independent of `Q`**. Raising `Q` cannot raise it. For
`CURVE-J12S1` the derived seed is `100 + offset` with `offset ∈ [0, 50)` and
(per `EV-STR-003` I1) `n = 733`, `n - 1 = 732 = 2^2 · 3 · 61`. Enumerating all
fifty candidate derived seeds:

- 45 of 50 give a period of `122` or more — comfortably above `R_base(193) = 66`;
- `s ∈ {108, 120, 132, 144}` give `gcd = 12`, period **61**;
- `s = 122` gives `gcd = 122`, period **6**.

At period 61 the ladder's top two cells can collect at most 61 base rows against
`R_base = 65` and `66`, so `rows_final <= 183 < 192`: **`IV-5` fires, `L192` and
`L193` are invalid in both arms, and branch 1 forces the whole verdict to
`incomplete`.** At period 6 the failure reaches down to `L24`. The same
enumeration for `CURVE-J16S3` (`n = 41617`, derived seed `300 + offset`) gives a
minimum period of `136`, comfortably above `R_base(97) = 34`, so the cross-curve
cells are not at risk.

This is a one-line pre-flight computation from `n` and the derived seed, before
any collection. It is the cheapest control this contract is missing; see
objection **O-2** and `required_controls` item 1.

## 9. Steps I could not reproduce, and things I did not reach

- **Nothing in the derivation note failed to reproduce.** Sections D-1 through
  D-7 are correct as written; D-8 item 1 is too weak (section 6.2); D-9's "F-5
  does not fire there" is category-confused, since `F-5` is evaluated per arm
  over the whole ten-cell ladder and not per cell.
- I did **not** execute any harness function, so `len(F) == B` at `B = 192/193`,
  the actual derived seeds, the actual `p`, `n`, `zeta3`, and the actual hit
  rates are **unverified by me**. My section 8 period analysis is conditional on
  `EV-STR-003`'s committed `n` values and on the derived-seed form
  `seed*100 + offset` read from `endomorphism_la.py:43`.
- I did **not** run `tools/allocate_id.py`, `tools/validate_ledger.py` or
  `tools/check_merge_hygiene.py`; the task card records those as already
  resolved by the dispatching session and I did not re-spend budget on them.
- I did **not** review the BATCH-011/012/013 review reports beyond the pointers
  the contract itself cites, and I did not audit `RT-20260729-031` directly, so
  the "fifth instance" count is taken from the contract's own citation, not
  re-verified.
- I did **not** time any run; the budget assessment in `contract_review.yaml` is
  a complexity argument over the committed loops, not a measurement.
