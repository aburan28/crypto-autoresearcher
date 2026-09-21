# EXP-STR-004 — Derivation note: what `phi_alpha` counts, and the closed form of `T(cell)`

**Status label: `derivation`.** Under `docs/claims-and-verification.md`
("Refutation artifacts: proof before rejection") this note is a *checkable
argument*, class 2 of 3. It is **NOT** a machine-checked proof and the word
*proved* is not used of anything in it. Every step below is either marked
**EXACT** (it follows from the committed source text quoted here, or from
finite-field algebra) or **CONDITIONAL** (it depends on a property of the
committed code, of a library, or of a run that this note has **not** executed
and does **not** assert). The inventory of the conditional steps is
section 9 and it is part of the deliverable, not an afterthought.

**This note was written and frozen BEFORE any cell of EXP-STR-004 was
measured.** It is archived by `TASK-20260729-041`, three commits before the
`TASK-20260729-048` ledger archive, so the ordering rule of
`docs/claims-and-verification.md` and of integrity note `INT-BATCH014-G` is
satisfied by commit order rather than by argument. `DEC-20260727-009`'s single
next action requires exactly this artifact in these terms.

**What this note is not.** It says nothing about H-STR-002's *mechanism*. That
phi is an automorphism, that `phi(R)` is a genuine relation whenever `R` is and
`F` is phi-invariant, and that a closed relation system is `C_3`-equivariant,
are not in doubt and are not derived, used, supported or weakened here. This
note derives properties of **one number produced by one committed measurement
function on one committed row-construction rule**. It licenses no asymptotic
statement, no cost statement, and no claim about any curve outside the fourteen
declared cells.

The authoring session **ran nothing**: no harness, no driver, no Sage, no
allocator, no validator, no git command. Every quantity below is either read off
the source text or derived symbolically. No measured value appears anywhere in
this note, because none exists yet.

---

## 1. Notation

Fix a cell: a curve instance, a factor-base size `B`, and an arity `m`.

* `p`, `n`, `a`, `b` — the prime field, the prime subgroup order, and the curve
  coefficients of the instance, as **computed** by
  `harness.endomorphism_la._generate_j0_instance`. `a = 0` (the j=0 branch).
* `zeta3` — the value returned by `harness.endomorphism_la._find_zeta3(p)`.
* `F = [f_0, ..., f_{B-1}]` — the factor base of the arm, a list of `B`
  x-coordinates.
* `q = B // 3` (integer division), so `B = 3q + (B mod 3)`.
* `tau(B) = {3q, 3q+1, ..., B-1}` — the **truncated-tail index set**. Its size
  is `B mod 3`. Every cell of EXP-STR-004 has `B mod 3` in `{0, 1}`, so
  `tau(B)` is empty or the single index `{3q}`. Nothing in this note is
  asserted for `B mod 3 == 2`; see section 9, item C-8.
* `sigma` — the positional block-of-3 permutation of `[0, B)`:
  `sigma(3j + k) = 3j + ((k + 1) mod 3)` for `3j + k < 3q`, and
  `sigma(i) = i` for `i >= 3q`.
  `sigma` is a bijection of `[0, B)` with `sigma^3 = id`. **EXACT** — it is a
  product of disjoint 3-cycles on `[0, 3q)` and the identity on `tau(B)`.
* For a row vector `v` of length `B`, define the **positional shift**
  `S` by `(S v)[sigma(j)] = v[j]` for every `j`, equivalently
  `(S v)[i] = v[sigma^{-1}(i)]`. `S` is linear and `S^3 = id`. Because
  `sigma(i) = i` on `tau(B)`, `(S v)[i] = v[i]` for `i` in `tau(B)`.
* `delta_e` — the indicator vector of a single index `e`.
* `Pi` — the projection that zeroes every coordinate in `tau(B)` and fixes the
  rest.
* `M` — the row list actually handed to the measurement, as a matrix over
  `Z/nZ`. `MIS(arm, cell)` — the set of **row indices** `i` in `[0, B)` at which
  row `i` of the displacement matrix `D` (section 3) is not the zero row.
* `alpha(arm, cell)` — the integer returned by the committed
  `harness.endomorphism_la._measure_displacement_rank` on that row list.

---

## 2. The committed source facts this note rests on

Quoted from `harness/endomorphism_la.py` at the commit the contract binds.
These are the only source facts used; each is read directly from the text.

**(S-1) The shift matrix `Z`, lines 174–183.** For `shift_type == "phi"`:

```
num_orbits = B // 3
for j in range(num_orbits):
    base = j * 3
    Z[base][base + 1] = 1
    Z[base + 1][base + 2] = 1
    Z[base + 2][base] = 1
for k in range(num_orbits * 3, B):
    Z[k][k] = 1
```

So `Z[i][j] == 1` if and only if `j == sigma(i)`, and `Z` is zero elsewhere.
**EXACT.**

**(S-2) The inverse, lines 199–203.** `Z_inv[j][i] = 1` is set exactly when
`Z[i][j] == 1`. Substituting (S-1): `Z_inv[sigma(i)][i] = 1` for every `i`,
i.e. `Z_inv[u][v] == 1` if and only if `v == sigma^{-1}(u)`. **EXACT.**

**(S-3) The branch test, lines 220–223 and 233–235.**
`sq_rows = min(rows, cols)` with `cols = B`; the **square** branch is taken
when `sq_rows == cols`, that is when `rows >= B`, and it sets
`M_sq = M[:cols]` — the **first `B` rows of the emitted stream, in emission
order**. **EXACT.**

**(S-4) The square-branch difference, lines 236–242.**

```
ZM      = Z @ M_sq
ZMZ_inv = ZM @ Z_inv
diff[i][j] = (int(M_sq[i][j]) - int(ZMZ_inv[i][j])) % n
alpha = matrix_rank_mod(diff, n)
```

**EXACT** as source text; the value of the matrix products is Lemma 1.

**(S-5) The phi-invariant factor base, lines 93–114.** Candidate x-coordinates
are drawn as `x = _seed_int(inst.seed, f"phifb{j}") % p` for `j = 0, 1, 2, ...`.
For each candidate the **orbit** `[x, (zeta3*x) % p, (zeta3^2*x) % p]` is
formed; the orbit is **rejected** unless its three members are pairwise
distinct, none is already in `xs`, and each lifts to a curve point; an accepted
orbit is appended to `xs` **in that order**. The function returns `xs[:B]`.
**EXACT.**

**(S-6) The append block for `m = 2`, lines 292–304 (and its `m = 3` twin at
341–351).** For each found relation row `row` and each `shift` in `(1, 2)`:

```
shifted_row = [0] * B
for idx in range(B):
    if row[idx]:
        x = factor_base[idx]
        shifted_x = pow(zeta3, shift, p) * x % p
        if shifted_x in factor_base:
            shifted_row[factor_base.index(shifted_x)] = 1
if sum(shifted_row) > 0 and shifted_row not in relations:   # lines 303-304
    relations.append(shifted_row)
```

**Arm A-prime of EXP-STR-004 disables exactly the line-303/304 guard** — the
`sum(shifted_row) > 0` filter and the `shifted_row not in relations` dedup —
and appends `shifted_row` unconditionally. It changes nothing else. The
**base-row** zero filter at line 289 (`if sum(row) > 0`) is a different
statement and stays ON; see Remark 2.

**(S-7) `_find_zeta3`, lines 28–37.** Returns `z` only if `z != 1` and
`pow(z, 3, p) == 1`. Therefore `zeta3^3 == 1 (mod p)` and `zeta3 != 1`.
**EXACT.**

**(S-8) `_find_decomposition` (`harness/semaev.py` lines 147–171).** The search
ranges over `v1` in `V` and `v2` in `V[i:]`, and returns summand points whose
x-coordinates are those `v1, v2`. Every summand x-coordinate of a returned
decomposition is therefore an element of the factor base. **EXACT.**

---

## 3. Lemma 1 — the square-branch identity (the `D[i][j]` step)

**Claim.** In the square branch, `diff[i][j] = (M[i][j] - M[sigma(i)][sigma(j)]) mod n`,
where `M` abbreviates `M_sq`.

**Derivation.** By (S-1), `(Z @ M)[i][j] = sum_k Z[i][k] * M[k][j] = M[sigma(i)][j]`,
because the only nonzero entry of row `i` of `Z` sits at column `sigma(i)`.
By (S-2), `Z_inv[u][v] = 1` exactly when `v = sigma^{-1}(u)`, so
`(A @ Z_inv)[i][j] = sum_u A[i][u] * Z_inv[u][j] = A[i][sigma(j)]`, the only `u`
contributing being `u = sigma(j)`. Composing with `A = Z @ M`:

```
ZMZ_inv[i][j] = M[sigma(i)][sigma(j)]
```

Substituting into (S-4) gives the claim. **EXACT** (given C-1 of section 9:
that `numpy` object-array `@` is the ordinary matrix product over Python
integers).

This is the identity `EV-STR-003.proof_status_basis` and
`DEC-20260727-009.refutation_artifact.why_not_claimed` name as the argument
that existed only inside review reports. It is now archived.

## 4. Lemma 2 — when a row of `D` vanishes

**Claim.** Row `i` of `D` is the zero row **if and only if**
`M[sigma(i)] = S(M[i])` as vectors over `Z/nZ`.

**Derivation.** Row `i` of `D` vanishes iff `M[sigma(i)][sigma(j)] = M[i][j]`
for every `j`. Since `sigma` is a bijection of `[0, B)`, put `j' = sigma(j)`;
the condition becomes `M[sigma(i)][j'] = M[i][sigma^{-1}(j')]` for every `j'`,
which is exactly `M[sigma(i)] = S(M[i])` by the definition of `S`. **EXACT.**

**Corollary 2a (this is `MIS`).**
`MIS(arm, cell) = { i in [0, B) : M[sigma(i)] != S(M[i]) }`. This is the
definition the driver computes independently of any rank computation, and it is
term-for-term the `misaligned_row_count` definition of the frozen EXP-STR-003
contract, section 4, square branch — reported here as a **set** rather than a
count, per PRED-ID-STR.

**Corollary 2b (P-4, the static bound).** `alpha <= |MIS|`. A matrix whose
nonzero rows are indexed by `MIS` has rank at most `|MIS|` over a field, and
`Z/nZ` is a field because `n` is prime (it is `max(sympy.factorint(order))` at
`harness/endomorphism_la.py:60`, and `_generate_j0_instance` rejects `n < 5`).
The inequality may be strict. **EXACT** given C-2.

---

## 5. Lemma 3 — the factor base and where the shift leaves it

Let `q = B // 3`.

**Claim 3a.** For every `i < 3q`: `f_{sigma(i)} = (zeta3 * f_i) mod p`.

**Derivation.** By (S-5) the first `3q` entries of `F` are `q` whole accepted
orbits in order, so writing `i = 3j + k` with `k` in `{0,1,2}` we have
`f_{3j+k} = (zeta3^k * x_j) mod p` for the `j`-th accepted candidate `x_j`.
Then `f_{sigma(3j+k)} = f_{3j+((k+1) mod 3)} = zeta3^{(k+1) mod 3} * x_j`.
For `k` in `{0, 1}` this is `zeta3 * f_{3j+k}` directly; for `k = 2` it is
`x_j = zeta3^3 * x_j = zeta3 * (zeta3^2 * x_j) = zeta3 * f_{3j+2}`, using
`zeta3^3 = 1` from (S-7). **EXACT.**

**Claim 3b.** For `i` in `tau(B)` and `k` in `{1, 2}`:
`(zeta3^k * f_i) mod p` is **not** an element of `F`.

**Derivation.** For our cells `tau(B)` is empty or `{3q}` with `B = 3q + 1`. In
the latter case `f_{3q} = x_q`, the first member of the `(q+1)`-th accepted
orbit, and the other two members `zeta3*x_q` and `zeta3^2*x_q` are precisely
the entries `xs[3q+1]` and `xs[3q+2]` that `xs[:B]` **truncates away**. By
(S-5) an accepted orbit's three members are pairwise distinct and none of them
already occurs in `xs`, so `zeta3*x_q` and `zeta3^2*x_q` differ from every one
of `f_0, ..., f_{3q}`. **EXACT** given C-3 (the builder reached `B`, so a
`(q+1)`-th orbit was in fact accepted).

**Claim 3c.** All `B` entries of `F` are pairwise distinct, so
`F.index(f_i) == i` for every `i`.

**Derivation.** (S-5) rejects an orbit if any member already occurs in `xs` and
if the three members are not pairwise distinct. **EXACT** for arm A-prime.
For arm E-prime, `semaev.build_factor_base` skips any `x` already in `xs`
(`harness/semaev.py:69-70`), giving the same conclusion. **EXACT.**

**Remark 1 (the ladder is nested, and this is the one-variable lever).** The
candidate sequence in (S-5) depends on `inst.seed` alone, and the accept/reject
test at candidate `j` depends only on the orbits accepted before it. `B` enters
only through the `while len(xs) < B` bound and the final `xs[:B]`. Hence, so
long as the trial bound `j < 50*B + 1000` is not reached (C-4), the factor base
at a smaller `B` is a **prefix** of the factor base at a larger `B` on the same
curve. The same holds for `semaev.build_factor_base`. This is why sweeping `B`
at a **fixed curve** is a one-variable comparison in the sense
`RULE-BATCH014-SCOPE` claims: the earlier factor-base elements do not move when
`B` grows. The contract turns this into a checkable driver assertion
(`CTRL-6`), not an assumption.

**Remark 2 (the base-row zero filter cannot suppress, for `m = 2`).** By (S-8)
both summand x-coordinates of a returned `m = 2` decomposition lie in `F`, so
the base row has at least one nonzero coordinate and the line-289 guard
`sum(row) > 0` never rejects it. The `m = 3` branch appends its base row with
no guard at all (line 338). Hence the pre-registered suppression count of zero
is a consequence of the construction for base rows as well as for appended
rows. **EXACT** given C-5.

---

## 6. Lemma 4 — what each closure emits

Both arms collect exactly `R_base(cell) = ceil(B/3)` base rows and then emit,
for each base row `r` in collection order, a **triple** of rows in this order:
`r`, then the shift-1 row, then the shift-2 row. No row is ever suppressed, so
the stream length is exactly `3 * R_base(cell) >= B` and the square branch of
(S-3) is taken at every cell.

**Claim 4a (arm A-prime).** With the line-303/304 guard disabled, the two
appended rows are `s_1 = S(Pi r)` and `s_2 = S^2(Pi r)`.

**Derivation.** Fix `shift` in `{1, 2}`. By (S-6) the coordinate `idx` of `r`
contributes to `shifted_row` at position `F.index((zeta3^shift * f_idx) mod p)`
**if and only if** that value lies in `F`. By Claim 3a, for `idx < 3q` that
value is `f_{sigma^shift(idx)}`, whose index is `sigma^shift(idx)` by Claim 3c.
By Claim 3b, for `idx` in `tau(B)` the value is **not** in `F` and the
coordinate is silently dropped. So `shifted_row[sigma^shift(idx)] = r[idx]` for
`idx < 3q` and `shifted_row[i] = 0` for `i` in `tau(B)` — which is exactly
`S^shift(Pi r)`, because `sigma` fixes `tau(B)` pointwise and therefore
`S^shift` maps the zeroed tail coordinates to themselves. **EXACT.**

**Claim 4b (arm E-prime).** The two appended rows are `S(r)` and `S^2(r)`, with
**no** projection.

**Derivation.** Arm E-prime's closure is defined by the contract as the
positional permutation itself: `r_shift[sigma^shift(i)] = r[i]` for every `i`
in `[0, B)`, with no membership test of any kind (this is the EXP-STR-003 arm-E
closure with its filter and dedup removed). There is no `zeta3` multiplication
and therefore no coordinate can fall outside `F`. **EXACT** relative to the
contract's definition of the arm.

**This asymmetry is the whole difference between the two arms**, and it is not
an implementation accident: arm A-prime's closure is a **curve** operation
(multiply the x-coordinate by `zeta3`, then look the result up in `F`), which
can miss; arm E-prime's closure is an **index** operation, which cannot.

---

## 7. Theorem 1 — `B mod 3 == 0`: the misalignment set is empty

**Claim.** At every cell with `B mod 3 == 0`, and for **both** arms,
`MIS = {}` and consequently `alpha = 0` exactly.

**Derivation.** Here `tau(B)` is empty, so `Pi = id` and Claims 4a and 4b
coincide: the stream is `r_1, S r_1, S^2 r_1, r_2, S r_2, S^2 r_2, ...`.
`R_base = B/3`, so the first `B` rows are exactly `q = B/3` complete triples,
and `M[3t] = r_{t+1}`, `M[3t+1] = S r_{t+1}`, `M[3t+2] = S^2 r_{t+1}` for
`0 <= t < q`. The row-index permutation `sigma` is, on `[0, B) = [0, 3q)`,
precisely the 3-cycle `3t -> 3t+1 -> 3t+2 -> 3t` inside each triple. Apply
Lemma 2 three times inside triple `t`, writing `r` for `r_{t+1}`:

| `i` | `sigma(i)` | need `M[sigma(i)] = S(M[i])` | holds because |
|---|---|---|---|
| `3t` | `3t+1` | `S r = S(r)` | identical |
| `3t+1` | `3t+2` | `S^2 r = S(S r)` | identical |
| `3t+2` | `3t` | `r = S(S^2 r) = S^3 r` | `S^3 = id` |

Every row of `D` vanishes, so `MIS = {}` and `D` is the zero matrix, so
`alpha = rank(0) = 0`. **EXACT** given C-1, C-2, C-4, C-6.

This is `P-1` of the contract, and it is `DEC-20260727-009`'s "sharp pass/fail
prediction alpha = 0 exactly at every instance with B mod 3 == 0" — here
derived, and stated as the **set** `{}` whose consequence the value `0` is.

Named cells: `L12`, `L24`, `L48`, `L96`, `L192`, `X96`, `A12M3`.

## 8. Theorem 2 — `B mod 3 == 1`: the closed form of `T(cell)`

Let `B = 3q + 1`, let `e = 3q` be the single tail index, and let
`r_1, ..., r_{q+1}` be the base rows in collection order
(`R_base = ceil(B/3) = q+1`). The first `B = 3q+1` emitted rows are `q`
complete triples followed by **one** further row, the base row `r_{q+1}` at
index `3q`:

```
M[3t]   = r_{t+1}                      0 <= t < q
M[3t+1] = first appended row of r_{t+1}
M[3t+2] = second appended row of r_{t+1}
M[3q]   = r_{q+1}
```

`sigma` restricted to `[0, B)` is the 3-cycle inside each of the `q` complete
triples, **and the identity at `e = 3q`**.

### 8.1 Arm A-prime

By Claim 4a, `M[3t+1] = S(Pi r)` and `M[3t+2] = S^2(Pi r)` with `r = r_{t+1}`.
Since `sigma(e) = e`, `(S v)[e] = v[e]` and `S(delta_e) = delta_e`; and
`Pi r = r - r[e] * delta_e`. Apply Lemma 2:

| `i` | `sigma(i)` | need | difference | vanishes iff |
|---|---|---|---|---|
| `3t` | `3t+1` | `S(Pi r) = S(r)` | `-r[e] * delta_e` shifted | `r[e] == 0` |
| `3t+1` | `3t+2` | `S^2(Pi r) = S(S(Pi r))` | `0` | **always** |
| `3t+2` | `3t` | `r = S(S^2(Pi r)) = Pi r` | `r[e] * delta_e` | `r[e] == 0` |
| `3q = e` | `e` | `r_{q+1} = S(r_{q+1})` | — | `r_{q+1}` is `S`-invariant |

Row `3t+1` **never** misaligns: both appended rows lose the *same* coordinate,
so the second is the shift of the first whatever `r[e]` is.

**Closed form.** Define, from artifacts that exist **before** any `alpha` is
measured — the factor base and the base row list, both sha256-recorded:

```
T(cell) = { 3t     : 0 <= t < q and supp(r_{t+1}) meets tau(B) }
        U { 3t + 2 : 0 <= t < q and supp(r_{t+1}) meets tau(B) }
        U { 3q     : if r_{q+1} != S(r_{q+1}) }
```

with `supp(r)` the set of indices where `r` is nonzero, and (for our cells)
"`supp(r)` meets `tau(B)`" meaning `r[3q] != 0`. `T(cell)` for `B mod 3 == 0`
is the empty set, which recovers Theorem 1. **EXACT** given C-1..C-6.

**Claim P-2 is then `MIS(A-prime, cell) = T(cell)`**, at the named cells
`L13`, `L25`, `L49`, `L97`, `L193`, `X97`, `A13M3`, with the tail index
`e = 3q` equal to `12, 24, 48, 96, 192, 96, 12` respectively.

`DEC-20260727-009` states the consequence as "alpha equal to the number of rows
touching the truncated tail otherwise". This note **does not** pre-register a
number: the derivation gives **two** misaligned rows per tail-touching base row
(`3t` and `3t+2`, not `3t+1`), plus possibly the final row `3q`, and
`alpha = rank(D)` may be strictly below `|T(cell)|`. Pre-registering the count
would have been the fifth cardinality-not-identity slip this program has
recorded; PRED-ID-STR forbids it and the set is pre-registered instead.

**When is `r_{q+1}` `S`-invariant?** `S`-invariance means `supp(r_{q+1})` is a
union of complete `sigma`-orbits, i.e. of whole triples `{3j, 3j+1, 3j+2}`
and/or the singleton `{e}`. A base row has at most `m + 1` nonzero
coordinates (2 for `m = 2`, 3 for `m = 3`), so the reachable `S`-invariant
cases are exactly: `supp = {e}` (both summand x-coordinates equal `f_e`), and
— at `m = 3` only — `supp` equal to one whole triple. Neither is forced and
neither is excluded by the construction, so both branches of the last row are
reachable. Nothing here asserts which occurs.

### 8.2 Arm E-prime, and the divergence from `P-3`

By Claim 4b there is no projection, so with `r = r_{t+1}`:

| `i` | `sigma(i)` | need | vanishes |
|---|---|---|---|
| `3t` | `3t+1` | `S r = S(r)` | **always** |
| `3t+1` | `3t+2` | `S^2 r = S(S r)` | **always** |
| `3t+2` | `3t` | `r = S(S^2 r) = S^3 r` | **always** |
| `3q = e` | `e` | `r_{q+1} = S(r_{q+1})` | iff `S`-invariant |

**Derived reference set (NOT a criterion, NOT a prediction of the contract):**

```
T_E(cell) = { 3q : if r_{q+1}^{E-prime} != S(r_{q+1}^{E-prime}) }   for B mod 3 == 1
T_E(cell) = { }                                                     for B mod 3 == 0
```

**The divergence, declared here before execution.** The contract's
pre-registered `P-3` predicts `MIS(E-prime, cell) = MIS(A-prime, cell)` at
**all fourteen** cells. This derivation agrees with `P-3` at the seven
`B mod 3 == 0` cells, where Theorem 1 forces both sets empty. At the seven
`B mod 3 == 1` cells the derivation says the two sets **can differ**, and names
the exact condition: they differ as soon as some base row among the first
`ceil(B/3)` of arm A-prime has a nonzero coordinate at the tail index `e`,
because arm A-prime's closure can drop that coordinate and arm E-prime's
cannot. The tail index is one of `B` coordinates and a base row has at most
`m + 1` of them nonzero, so **neither branch is forced by the construction** at
any named cell.

Consequences, all pre-registered:

1. `P-3` is carried **unchanged**. This note does not amend, weaken or
   reinterpret a pre-registered prediction of the dispatch queue; it records
   what the derivation says beside it. Both statements predate every
   measurement, and the disagreement between them is reported to the
   Coordinator as a finding rather than resolved by preference.
2. If `F-4` fires **only at `B mod 3 == 1` cells**, with direction
   `alpha(A-prime) >= alpha(E-prime)`, then the derivation's account of it is a
   **factor-base truncation artifact** — a dropped coordinate at
   `xs[:B]` — and **not** endomorphism content. It is the same mechanism
   `EV-STR-003` observation `O-4` identifies as arm A's skip cause. Reading
   such a firing as "the phi-invariant factor base is doing something" would be
   an error, and it is forbidden in advance here and in the contract's
   `interpretation_limits`.
3. The `mixed` verdict branch is therefore not decorative: it is the branch the
   derivation makes most likely, and the contract's verdict rule is defined
   over set equalities precisely so that it is reachable (repairing the
   EXP-STR-003 defect `EV-STR-003` observation `O-5` names).
4. `instrument_artifact_falsified` requires a named cell with
   `alpha(E-prime) > alpha(A-prime)`. The derivation makes that reachable only
   through the last-row branch — `r_{q+1}^{A-prime}` `S`-invariant while
   `r_{q+1}^{E-prime}` is not, with no tail-touching arm-A-prime base row. That
   is a narrow but genuinely available outcome, and it is recorded as available
   rather than dismissed.

---

## 9. Which steps are exact and which are conditional

**EXACT** (source text, or algebra over `F_p` / `Z/nZ`): (S-1) to (S-8);
Lemma 1 modulo C-1; Lemma 2; Corollary 2a; Corollary 2b modulo C-2; Lemma 3a,
3b (modulo C-3), 3c; Remark 2 modulo C-5; Lemma 4a, 4b; Theorem 1 and
Theorem 2's tables and closed form, modulo the conditions below.

**CONDITIONAL** — each is a property this note has **not** executed and does
**not** assert. Each is either checked by the driver and recorded, or covered by
an invalidation rule of the contract:

* **C-1** `numpy` object-array `@` computes the ordinary matrix product over
  Python integers, and `Z`, `Z_inv`, `M_sq` have the shapes lines 173–241
  assume. *Not verified here.* Covered by: `P-4`/`F-2` (a violation of
  `alpha <= |MIS|` is the observable symptom) and `CTRL-5`.
* **C-2** `matrix_rank_mod` (lines 145–170) computes the rank over `F_n`
  correctly, and `n` is prime so its `pow(pivot, -1, n)` is always defined.
  *Primality is read from source (`max(sympy.factorint(order))`) but not
  recomputed here.* Covered by `F-2` and by invalidation rule `IV-8`.
* **C-3** `_build_phi_invariant_factor_base` actually reached `B` entries, so a
  `(q+1)`-th orbit was accepted at the `B mod 3 == 1` cells. Covered by
  `IV-3` (factor-base length must equal `B`).
* **C-4** The candidate trial bound `j < 50*B + 1000` was not exhausted, so the
  prefix-nesting of Remark 1 holds. Covered by `IV-3` and `CTRL-6`.
* **C-5** `E.lift_x`, `E.add`, `E.negate` and `_seed_int` in
  `harness/toycurve.py` behave as their names say. *Not read line by line for
  this note.* Covered by the independent Sage re-verification of every base-row
  certificate (`CTRL-2`), which is the one place this matters: a base row is a
  claimed decomposition and Sage re-checks it with its own arithmetic.
* **C-6** The driver emits the triples in the declared order and collects
  exactly `R_base(cell)` base rows. Covered by `IV-4`, `IV-5` and the
  shortfall disposition.
* **C-7** Nothing here depends on any instance parameter value. The note is
  uniform in `p`, `n`, `a`, `b`, `zeta3`, and **no value of any of them is
  asserted anywhere in it**. `EV-STR-003` records
  `p in {2293, 2953, 42013, 631843}` and `n in {733, 3061, 41617, 158071}`
  across its four instances; this note assigns none of those to a cell, and the
  driver computes them.
* **C-8** The closed form is stated for `B mod 3` in `{0, 1}`, which covers all
  fourteen cells. It is **not** asserted for `B mod 3 == 2`, where `tau(B)` has
  two members and the last partial triple is longer; that case is outside every
  declared cell and outside this note.

## 10. What this note does not derive

* Nothing about H-STR-002's **mechanism**, in either direction (see the header).
* Nothing asymptotic. Theorems 1 and 2 are exact statements about the row list
  a declared construction emits at a declared `B`; they are not a scaling law,
  they do not say `alpha = O(1)`, and they do not say it is not. `alpha` here is
  small at these cells *because the construction closes the row list under
  `sigma`*, which is a property of the bookkeeping, and that observation is
  neither support for nor evidence against the hypothesis.
* No cost statement. No operation count, no memory term, no comparison to
  Wiedemann, rho or BSGS. `RC-7` is declared inapplicable in the contract with
  its reason and its cost.
* No resolution of `UC-7`: H-STR-002's falsification condition `FC-1` is
  ambiguous as drafted — "relation collection" may or may not be read as
  including the orbit closure that lives inside `_collect_relations` — and this
  note does not resolve it in either party's favour. The derivation is
  compatible with both readings and says so.
* No statement about whether the phase breaks it counts "correlate with
  anything mathematical". `EV-STR-003` `UC-1` records that as the open
  question, and Corollary 2b bounds a number without answering it.

## 11. Provenance

* Written by: coordinator session, `TASK-20260729-040`, no shell, no git, no
  execution of any kind.
* Requested inference policy `coordinator-orchestration-code`;
  resolved model `claude-opus-5` (Cursor/Claude Code subagent, runtime-reported,
  **not** probe-verified); `model_verified: false`; `fallback_used: true`
  because this harness cannot resolve `orchestration/model-policies.yaml`
  identifiers. See the specification's `inference_receipt` for the full block.
* Cited records: `DEC-20260727-009` (next action; `refutation_artifact`),
  `EV-STR-003` (`proof_status_basis`, `O-4`, `O-5`, `O-6`, `UC-1`, `UC-2`,
  `UC-6`, `UC-7`), `H-STR-002`, `EXP-STR-003`
  `specification.v1-frozen-1c6f10b7.yaml`, `docs/claims-and-verification.md`,
  and the `BATCH-014` dispatch queue's `preregistration` block.
* No commit identifier, hash or timestamp beyond date precision is asserted
  anywhere in this note.
