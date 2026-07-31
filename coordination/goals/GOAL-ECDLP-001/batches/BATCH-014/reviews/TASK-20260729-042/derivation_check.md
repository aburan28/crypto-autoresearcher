# TASK-20260729-042 — Independent re-derivation of the square-branch identity and `T(cell)`

**Report:** `RT-20260729-034` (path + task id; cite as such).
**Reviewed HEAD:** `f3e15614ed04b128436ca938b16aab30f02912e3` (equals the TASK-20260729-041 snapshot; four declared paths only).
**Source of truth:** committed `harness/endomorphism_la.py` at that HEAD — **not** the derivation note.
**Status label:** this document is a `derivation` check (class 2), never `proved`.

I did **not** treat `experiments/EXP-STR-004/derivation_note.md` as true. Every step below was re-derived from the harness source text, then compared to the note. Steps I executed as finite checks are marked **CHECKED**; steps that are pure reading of source are **READ**; algebra over `Z/nZ` / `F_p` is **EXACT** under the named conditions.

---

## 0. What I read from the source (no trust of the note)

From `harness/endomorphism_la.py` at HEAD:

| Tag | Lines | Fact |
|---|---|---|
| S-1 | 174–183 | For `shift_type == "phi"`: `num_orbits = B // 3`; each block of 3 is a cycle `base → base+1 → base+2 → base`; indices `k ∈ [3·num_orbits, B)` are fixed points of `Z`. |
| S-2 | 199–203 | `Z_inv[j][i] = 1` exactly when `Z[i][j] = 1`. |
| S-3 | 220–235 | Square branch iff `rows >= B`; then `M_sq = M[:cols]` = first `B` emitted rows. |
| S-4 | 236–242 | `diff = M_sq - (Z @ M_sq @ Z_inv)` entrywise mod `n`; `alpha = matrix_rank_mod(diff, n)`. |
| S-5 | 93–114 | Phi factor base appends full orbits `[x, ζ₃x, ζ₃²x]` then returns `xs[:B]`. |
| S-6 | 292–304 / 341–351 | Appended shift uses `shifted_x = ζ₃^shift · f_idx`, sets the index only if `shifted_x ∈ F`; committed code then filters/dedups (lines 303–304). |
| S-7 | 28–37 | Returned `zeta3` satisfies `zeta3 ≠ 1` and `zeta3³ ≡ 1 (mod p)`. |

Define `σ` by `σ(i) = j` iff `Z[i][j] = 1`. Then `σ` is the positional block-of-3 permutation of `[0,B)`, identity on the truncated tail `τ(B) = {3q,…,B−1}` with `q = B // 3`.

---

## 1. Square-branch identity (re-derived)

**Claim.** In the square branch, `diff[i][j] ≡ M[i][j] − M[σ(i)][σ(j)] (mod n)`.

**Derivation (EXACT, given ordinary matrix product — condition C-1).**

1. Row `i` of `Z` has a single 1 at column `σ(i)`, so `(Z @ M)[i][j] = M[σ(i)][j]`. **READ + algebra.**
2. `Z_inv[u][v] = 1` iff `v = σ⁻¹(u)`, equivalently the unique `u` with `Z_inv[u][j] = 1` is `u = σ(j)`. Hence `(A @ Z_inv)[i][j] = A[i][σ(j)]`. **READ + algebra.**
3. With `A = Z @ M`: `(Z @ M @ Z_inv)[i][j] = M[σ(i)][σ(j)]`. **algebra.**
4. Subtract from `M` mod `n` as in S-4. **READ.**

**CHECKED:** for every declared cell `B ∈ {12,13,24,25,48,49,96,97,192,193}` I built `Z` exactly as lines 174–183, formed random `M ∈ (Z/97Z)^{B×B}`, computed `M − ZMZ⁻¹` with numpy, and compared entrywise to `M[i][j] − M[σ(i)][σ(j)]`. All ten sizes matched.

**Agreement with the note:** Lemma 1 of `derivation_note.md` matches this re-derivation.

---

## 2. When a displacement row vanishes

Define the positional shift `S` by `(S v)[σ(j)] = v[j]` for all `j` (equivalently `(S v)[i] = v[σ⁻¹(i)]`). Then `S` is linear and `S³ = id`, and `S` fixes coordinates in `τ(B)` pointwise.

**Claim.** Row `i` of `D` is zero iff `M[σ(i)] = S(M[i])` as vectors over `Z/nZ`.

**Derivation (EXACT).** Row `i` vanishes iff `M[σ(i)][σ(j)] = M[i][j]` for every `j`. Put `j' = σ(j)` (bijection): `M[σ(i)][j'] = M[i][σ⁻¹(j')]` for every `j'`, i.e. `M[σ(i)] = S(M[i])`.

Therefore
`MIS(arm, cell) = { i ∈ [0,B) : M[σ(i)] ≠ S(M[i]) }`.

**Corollary (static bound).** Over a field, `α = rank(D) ≤ |MIS|`. Here `n` is taken as `max(sympy.factorint(order))` at line 60 and instances with `n < 5` are rejected, so `Z/nZ` is a field under that construction (condition C-2: primality not re-proved in this review session beyond reading the source).

**Agreement with the note:** Lemma 2 / Corollaries 2a–2b match.

---

## 3. Factor-base facts used by the closure

Let `q = B // 3` and `F = [f_0,…,f_{B−1}]`.

**Claim 3a (EXACT from S-5 + S-7).** For `i < 3q`, `f_{σ(i)} ≡ ζ₃ · f_i (mod p)`.
Reason: the first `3q` entries are `q` whole accepted orbits in order; `σ` advances the orbit position; at position `k=2`, `ζ₃³ ≡ 1` closes the cycle.

**Claim 3b (EXACT given the builder reached `B` — C-3).** For `i ∈ τ(B)` and `k ∈ {1,2}`, `(ζ₃^k · f_i) ∉ F` when `B = 3q+1`.
Reason: `f_{3q}` is the first member of the next accepted orbit; `xs[:B]` truncates away the other two distinct orbit members, which by S-5 are not already in `xs`.

**Claim 3c (EXACT from S-5 / `semaev.build_factor_base` skip-if-present).** Entries of `F` are pairwise distinct, so `F.index(f_i) = i`.

I did **not** execute the factor-base builders against live curves in this review (budget / no measurement). Claims 3a–3c are source+algebra only; C-3/C-4 remain conditional exactly as the note inventories.

---

## 4. What each arm emits (contract closures, harness append rule)

Both arms of EXP-STR-004 are specified to collect exactly `R_base(cell) = ceil(B/3)` **base** rows and emit the triple `(r, shift-1, shift-2)` per base row with **no** line-303/304 suppression. Stream length `3·R_base ≥ B` at every declared cell, so the square branch is taken (feasibility table arithmetic **CHECKED**: all fourteen cells have `emitted ≥ B`; one missing base row drops below `B` at every cell).

**Arm A-prime (curve closure, guard off).** For `shift ∈ {1,2}`, the append block of S-6 with the filter/dedup disabled yields
`shifted = S^{shift}(Π r)`,
where `Π` zeroes coordinates in `τ(B)`.
Reason: for `idx < 3q`, Claim 3a+3c place the image at `σ^{shift}(idx)`; for `idx ∈ τ(B)`, Claim 3b drops the coordinate. **EXACT** relative to S-6 with guard off + Claims 3a–3c.

**Arm E-prime (index closure).** By contract (not by harness `main()`), appends are pure `S(r)` and `S²(r)` with no `ζ₃` test. **EXACT** relative to the contract’s arm definition; there is no corresponding function in the committed harness — the driver must implement it (DEV-BASE-1).

---

## 5. Theorem — `B mod 3 == 0`: `MIS = ∅`

Here `τ(B) = ∅`, so `Π = id` and the two arms’ closures coincide: the first `B` rows are exactly `q = B/3` complete triples
`M[3t] = r_{t+1}`, `M[3t+1] = S r_{t+1}`, `M[3t+2] = S² r_{t+1}`.

Inside each triple, `σ` is the 3-cycle `3t → 3t+1 → 3t+2 → 3t`. Lemma 2 holds on all three rows because `S³ = id`. Hence `MIS = ∅`, `D = 0`, `α = 0` for **both** arms.

Named cells: `L12, L24, L48, L96, L192, X96, A12M3`.

**Agreement with the note:** Theorem 1 matches. **CHECKED** on a synthetic stream for `B=12` (empty MIS).

---

## 6. Closed form of `T(cell)` at `B mod 3 == 1` (the load-bearing object)

Let `B = 3q+1`, `e = 3q`, `R_base = q+1`. The first `B` emitted rows are `q` complete triples plus the bare base row `r_{q+1}` at index `e`. `σ` is the usual 3-cycles on `[0,3q)` and `σ(e) = e`.

### 6.1 Arm A-prime — re-derived table

With `r = r_{t+1}` and appended rows `S(Π r)`, `S²(Π r)`:

| `i` | `σ(i)` | need `M[σ(i)] = S(M[i])` | holds iff |
|---|---|---|---|
| `3t` | `3t+1` | `S(Π r) = S(r)` | `r[e] = 0` |
| `3t+1` | `3t+2` | `S²(Π r) = S(S(Π r))` | **always** |
| `3t+2` | `3t` | `r = S(S²(Π r)) = Π r` | `r[e] = 0` |
| `e` | `e` | `r_{q+1} = S(r_{q+1})` | `r_{q+1}` is `S`-invariant |

Reason for row `3t`: `S(r) − S(Π r) = S(r[e]·δ_e) = r[e]·δ_e` because `σ(e)=e`. Reason for row `3t+1`: both appended rows lose the same coordinate. Reason for row `3t+2`: `S³(Π r) = Π r`.

**Closed form (re-derived, not copied):**

```text
T(cell) = { 3t     : 0 ≤ t < q and r_{t+1}[e] ≠ 0 }
        ∪ { 3t + 2 : 0 ≤ t < q and r_{t+1}[e] ≠ 0 }
        ∪ { e      : if r_{q+1} ≠ S(r_{q+1}) }
```

For `B mod 3 == 0`, `T(cell) = ∅` (recovers §5). For the declared cells, `τ(B)` is empty or `{e}`, so “`supp(r)` meets `τ(B)`” is exactly `r[e] ≠ 0`.

**Claim P-2** is then `MIS(A-prime, cell) = T(cell)` at
`L13, L25, L49, L97, L193, X97, A13M3`
with `e ∈ {12,24,48,96,192,96,12}` respectively.

**CHECKED:** synthetic A-prime streams at `B ∈ {7,13,25}` with mixed tail-touching base rows: computed `MIS` from Lemma 2 equaled this `T(cell)` in every trial run in this session.

**Agreement with the note:** §8.1 closed form matches my re-derivation **term for term**. I independently obtained the same three pieces (the `3t` / `3t+2` pair per tail-touching base row among the first `q`, plus the optional final index `e`). I did **not** skip this step by reading the note first and “confirming”; the table was written from Lemma 2 + Claim 4a, then compared.

### 6.2 Arm E-prime — reference set (not a contract criterion)

With no projection, every complete triple is aligned; only the final row can misalign:

```text
T_E(cell) = { e : if r_{q+1}^{E-prime} ≠ S(r_{q+1}^{E-prime}) }   (B ≡ 1 mod 3)
T_E(cell) = ∅                                                      (B ≡ 0 mod 3)
```

**Divergence from P-3 (also re-derived, not trusted from the note).** At `B ≡ 0 mod 3`, both arms have `MIS = ∅`. At `B ≡ 1 mod 3`, the sets **can differ** as soon as some A-prime base row among the first `R_base` has `r[e] ≠ 0`, because A-prime’s closure can drop that coordinate and E-prime’s cannot. Neither branch is forced at any named cell. **CHECKED** on a synthetic all-tail-touch A-prime stream at `B=13`: `MIS_A` had nine indices while `MIS_E` was `{12}`.

---

## 7. Steps I could not reproduce / did not execute

| Item | Status |
|---|---|
| Square-branch identity | **Re-derived and CHECKED** on all fourteen `B` values |
| `T(cell)` closed form for A-prime | **Re-derived and CHECKED** on synthetic streams |
| Live factor-base nesting / C-3 / C-4 on CURVE-J12S1 / CURVE-J16S3 | **Not executed** (no measurement; pre-execution review) |
| `matrix_rank_mod` correctness on live `n` | **Not re-proved**; read source only (C-2) |
| numpy object-dtype `@` on the exact harness path | **Not executed** through the harness function; identity CHECKED with numpy integer/`object` matrices built like the source |
| Arm E-prime as committed harness code | **N/A** — it is a driver obligation, not a function in `endomorphism_la.py` |
| Any cell measurement / `α` / real `T(cell)` members | **None exist at reviewed HEAD**; none were invented |

---

## 8. Verdict on question (1) of the card

The derivation note’s rule for `T(cell)` is **correct** and **follows from the committed source** (plus the contract’s A-prime guard-off closure), not from an assumption about the source. P-2 may be pre-registered as that set identity.

This does **not** by itself make the whole contract PASS: see `contract_review.yaml` for BLOCKING defects elsewhere (verdict-rule coverage; false F-1/F-4 coincidence claim for arm E-prime).
