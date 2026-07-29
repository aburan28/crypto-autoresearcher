# VAL-20260729-003 — recount note

Task: `TASK-20260729-046`, re-pointed by `QUEUE-AMEND-20260729-005`.
Role: validator, independent non-originating session. HEAD reviewed:
`b45edb5965ebec1da056a6df423b604558595562`, branch `claude/ecdlp-b011`.
Tracked working tree clean at the start and at the end of this task; nothing
committed, nothing staged.

**This session executed no experiment.** The only curve computation performed is
the target-period index arithmetic of section 5, which the re-pointed card and
the dispatching instruction permit and label a **feasibility check, not
evidence**.

---

## 0. What replaces the original recount

The original card required a member-by-member recount of the predicted and
measured misalignment sets at fourteen named cells. **Those sets do not exist.**
`TASK-20260729-044` is stood down, `experiments/EXP-STR-004/runs/` does not
exist at this HEAD, and no measured set was ever produced. That recount is
therefore **NOT PERFORMED**, and it is recorded as not performed rather than as
passed. What follows is the recount the amendment substituted: a fourth
independent derivation (D1), and a recount of the amendment's own counts (D6).

---

## 1. D1 — the fourth independent derivation

### 1.1 Provenance and ordering

Written from `harness/endomorphism_la.py` at this HEAD **before** reading
`reviews/TASK-20260729-042/derivation_check.md` section 6.2, before reading
`experiments/EXP-STR-004/derivation_note.md`, and before reading
`QUEUE-AMEND-20260729-005`'s `the_derivation_the_ruling_rests_on` block. The
ordering was maintained by writing the derivation to a scratch file outside the
repository first and only then opening those three artifacts. The claim under
test was supplied to this session in refutable form and is reproduced verbatim
in the validation report.

### 1.2 The shift operator sigma

From lines 173-183, for `shift_type == "phi"` with `cols = B` and
`q = num_orbits = B // 3`, `Z[i][j] == 1` exactly when `j == sigma(i)`, where

```
sigma(3j)   = 3j + 1
sigma(3j+1) = 3j + 2      for j = 0 .. q-1
sigma(3j+2) = 3j
sigma(k)    = k           for 3q <= k < B     (loop at line 182)
```

Every row and every column of `Z` carries exactly one 1, so `Z` is a genuine
permutation matrix; `sigma` is a product of disjoint 3-cycles and fixed points,
hence `sigma^3 = id` and `sigma^{-1} = sigma^2`. Lines 199-203 set
`Z_inv[j][i] = 1` whenever `Z[i][j] == 1`, i.e. `Z_inv = Z^T = Z^{-1}`; the
inverse is correct.

### 1.3 The displacement matrix in the square branch

`(Z M)[i][j] = M[sigma(i)][j]`. `Z_inv[l][j] == 1` iff `l == sigma(j)`, so
`(Z M Z^{-1})[i][j] = M[sigma(i)][sigma(j)]`. Therefore, at lines 233-242,

```
D[i][j] = M[i][j] - M[sigma(i)][sigma(j)]
D[i]    = r_i - sigma^{-1} . r_{sigma(i)}          (*)
```

writing `(sigma . v)[sigma(i)] = v[i]` for the action on rows. **REPRODUCED:
this is the amendment's `D[i][j] = M[i][j] minus M[sigma(i)][sigma(j)]`.**

Precondition **P1**: this branch is entered only when `rows >= cols`
(line 220-223). The other branch computes `diff[i] = sigma . r_i - r_i` with no
row permutation and its rank grows like twice the number of triples. The small
bounds are a statement about the square branch only.

### 1.4 Factor-base index law and the two closures

Lines 85-114 append whole orbits `[x, zeta3 x, zeta3^2 x]` after rejecting any
orbit with a repeated, already-present or non-lifting member, then return
`xs[:B]`. So `factor_base[3j+t] = zeta3^t x_j` on every complete block, and
multiplication of an x-coordinate by `zeta3^s` moves index `3j+t` to
`sigma^s(3j+t)`. At `B = 3q+1` the truncation leaves `x_q` at index `3q` with
`zeta3 x_q` and `zeta3^2 x_q` absent from the factor base.

For a base row `r` write `c := r[3q]` and `r~ := r - c e_{3q}`.

- **Arm A-prime** (multiplicative closure, lines 292-304 / 341-351, zero filter
  and dedup disabled): the `if shifted_x in factor_base` guard drops exactly the
  tail coordinate, so the two closure rows are `sigma . r~` and `sigma^2 . r~`.
- **Arm E-prime** (positional closure, specification `arms.E-prime.closure`):
  the closure rows are `sigma . r` and `sigma^2 . r`, tail coordinate retained,
  because `sigma` fixes `3q`.

Precondition **P2**: both results require that the first `B` rows are exactly a
concatenation of ordered triples `(base, shift-1, shift-2)` aligned to row
indices `3j, 3j+1, 3j+2`. This is **not** implied by `sigma^3 = id`; it is a
property of the emission order and of the two filters at lines 303/304. In
arm E-prime it is discharged by construction, since CTRL-2 disables both
filters and the positional closure can never emit a zero row.

### 1.5 The rows — arm A-prime at a `B mod 3 = 1` cell

With `r := r_{3j}`, `c := r[3q]`, using `(*)` and `sigma^{-1} = sigma^2`:

```
D[3j]   = (r~ + c e_3q) - sigma^{-1} . (sigma . r~)   = c e_3q          REPRODUCED
D[3j+1] = sigma . r~    - sigma^{-1} . sigma^2 . r~   = 0               REPRODUCED
D[3j+2] = sigma^2 . r~  - sigma^2 . (r~ + c e_3q)     = -c e_3q         REPRODUCED
D[3q]   = r_q - sigma^{-1} . r_q                                        REPRODUCED
```

`sigma(3q) = 3q`, so the `3q` coordinate of `D[3q]` is
`r_q[3q] - r_q[sigma(3q)] = 0`. **REPRODUCED.**

The `3q` rows arising from complete triples span at most the line through
`e_3q`; `D[3q]` is orthogonal to that coordinate and contributes at most one
more. Hence

```
alpha(A-prime, B mod 3 = 1) = [ exists j < q with r_j[3q] = 1 ]
                            + [ sigma . r_q != r_q ]      in {0, 1, 2}
```

**REPRODUCED, including the exact-rank form**, which matches
`derivation_check.md` section 6.2 line for line.

### 1.6 The rows — arm E-prime at a `B mod 3 = 1` cell

With the tail coordinate retained in the closure rows:

```
D[3j]   = r        - sigma^{-1} . sigma   . r = 0
D[3j+1] = sigma r  - sigma^{-1} . sigma^2 . r = 0
D[3j+2] = sigma^2 r- sigma^{-1} . r           = 0
D[3q]   = r'_q - sigma^{-1} . r'_q            (the orphan base row)
```

so `alpha(E-prime, B mod 3 = 1) = [ sigma . r'_q != r'_q ] in {0, 1}`.
**REPRODUCED.** At `B mod 3 = 0` every one of the `B` rows sits in a complete
triple and `D = 0`, giving `alpha = 0` for both arms. **REPRODUCED.**

### 1.7 A strengthening this session obtained and states as its own

Nothing in section 1.6 refers to the factor base. The general statement is

```
alpha(E-prime) <= (cols mod 3) <= 2   for every cols,
```

because `sigma` fixes exactly the `cols mod 3` tail indices, every complete
triple contributes a zero row, and each tail row contributes at most one. This
is offered as a derivation, never as a proof, and it is the basis of the D2
ruling in section 2.

### 1.8 Numeric confirmation, outside the repository, NOT EVIDENCE

The committed `_measure_displacement_rank` was invoked verbatim on synthetic row
lists built to each arm's declared closure, at
`B in {7, 8, 9, 10, 11, 12, 13, 14, 16, 22}` over `F_101`. This exercises the
real `Z`, `Z_inv`, branch selection and rank routine, not a re-implementation.

| B | B mod 3 | alpha(A-prime) | alpha(E-prime) | closed-form D rows match entrywise |
|---|---|---|---|---|
| 9, 12 | 0 | 0 | 0 | n/a (D = 0) |
| 7 | 1 | 2 | 1 | yes |
| 10 | 1 | 1 | 1 | yes |
| 13 | 1 | 2 | 1 | yes |
| 16 | 1 | 2 | 1 | yes |
| 22 | 1 | 2 | 1 | yes |
| 8 | 2 | 3 | 2 | n/a (out of contract scope) |
| 11 | 2 | 4 | 2 | n/a (out of contract scope) |
| 14 | 2 | 4 | 2 | n/a (out of contract scope) |

At every `B mod 3 = 1` size the predicted `D` matrix was compared to the actual
`M[i][j] - M[sigma(i)][sigma(j)]` **entry by entry, not by rank**, and agreed at
every entry. This is a synthetic index-only check on invented rows; it is not a
measurement of any cell and it is not evidence about `H-STR-002`.

### 1.9 Sensitivity of the two preconditions, same harness

| perturbation | B | alpha(A-prime) | alpha(E-prime) |
|---|---|---|---|
| aligned triples, square branch | 13 / 16 / 22 | 2 / 2 / 2 | 1 / 1 / 1 |
| one row deleted from an early triple (P2 broken) | 13 / 16 / 22 | 9 / 10 / 14 | 8 / 10 / 14 |
| `B - 1` rows only (P1 broken, rectangular branch) | 13 / 16 / 22 | 8 / 10 / 14 | 8 / 10 / 14 |

Both preconditions are load-bearing and neither is cosmetic. Both are named in
the contract — P1 by `IV-5` and the `R_base` derivation, P2 by `CTRL-2` — and
neither depends on `D-3`.

---

## 2. D2 — is the arm E-prime limb independent of `D-3`?

`D-3` (derivation note lines 135-161) is the claim that
`_build_phi_invariant_factor_base` returns a list of length exactly `B` whose
complete blocks satisfy `F[3j+k] = zeta3^k F[3j]`. It is used by `D-4` to turn
the **multiplicative** closure map into an index map, and `D-4` is used only by
arm A-prime.

**RULING: the arm E-prime limb IS independent of `D-3`.** Three independent
routes, all checked:

1. **Textual.** Arm E-prime's factor base is
   `_build_random_factor_base(inst, B)`. `_build_phi_invariant_factor_base` is
   not called on that arm, so `D-3`'s hypothesis has no subject there.
2. **Structural.** The section 1.6 derivation uses only: `sigma` as built at
   lines 174-183, which is a function of `cols` alone and never touches the
   factor base, `zeta3`, `p` or the curve; the closure being unconditional and
   positional, so the row stream is exactly `(r, sigma r, sigma^2 r)`; and the
   square-branch identity `(*)`. No step names a factor-base entry.
3. **Numeric.** The section 1.8 arm E-prime rows were generated by applying
   `sigma` positionally to arbitrary random 0/1 vectors. **No factor base
   existed in that computation at all**, and `alpha(E-prime) <= 1` held at every
   residue-one size and `= 0` at every residue-zero size.

The independence is in fact **stronger than the ruling claims**: by section 1.7,
`alpha(E-prime) <= cols mod 3 <= 2` whatever the factor base is and whatever its
length, so even a short random factor base — the E-prime-side analogue of the
hypothesis `D-3` guards — leaves `alpha(E-prime) = O(1)` and leaves the
non-discrimination reading intact.

**The two things the E-prime limb does depend on are P1 and P2, and neither is
`D-3`.** P2 is discharged by `CTRL-2` by construction. P1 is a relation-yield
question governed by `IV-5` and `IV-6`, with a margin of one base-row shortfall
at residue-zero cells (`rows_final - B = 3`) and two at residue-one cells
(`= 5`), per the `derivation_check.md` section 7 table, which this session
recomputed and confirms: `R_base(B) = (B+2)//3 + 1` gives
`5, 6, 9, 10, 17, 18, 33, 34, 65, 66, 33, 34, 5, 6` across the fourteen cells
and `rows_final - B in {3, 5}` at all fourteen, so all fourteen take the square
branch absent a shortfall of two or more base rows.

**Consequence for the ruling: the stand-down ruling STANDS on this limb.** It
does not rest on a conditional it declared unconditional.

---

## 3. D3 — the archive chain against Git

Chain, all four commits reachable from HEAD, parents forming one linear
sequence with no gap:

```
15fd845b  BATCH-014 opening (dispatch_queue.json added)
    ...
68e4b9b7  merge of origin/main
7c9aa579  TASK-20260729-040 artifacts        parent 68e4b9b7
561495cd  TASK-20260729-041 receipt          parent 7c9aa579
0cea73f9  TASK-20260729-042 review           parent 561495cd
71dd1880  TASK-20260729-043 receipt          parent 0cea73f9
b45edb59  QUEUE-AMEND-20260729-005 = HEAD    parent 71dd1880
```

`7c9aa579` changed exactly `experiments/EXP-STR-004/specification.yaml`,
`experiments/EXP-STR-004/derivation_note.md` and
`.../TASK-20260729-040/feasibility_table.md` — three additions, no deletion, no
modification. `0cea73f9` changed exactly the two `TASK-20260729-042` review
files. `71dd1880` changed exactly the `TASK-20260729-043` receipt.
`b45edb59` changed exactly `.../BATCH-014/dispatch_queue.json`.

Every recorded SHA-256 re-derived from the Git blob at the recorded commit, via
`git show <commit>:<path> | shasum -a 256`, never from the working tree:

| commit | path | recorded | re-derived | match |
|---|---|---|---|---|
| 7c9aa579 | experiments/EXP-STR-004/specification.yaml | `1744ffce...6cf6d5` | `1744ffce...6cf6d5` | YES |
| 7c9aa579 | experiments/EXP-STR-004/derivation_note.md | `d7819e77...81ef43` | `d7819e77...81ef43` | YES |
| 7c9aa579 | .../TASK-20260729-040/feasibility_table.md | `f2c9f95f...25139` | `f2c9f95f...25139` | YES |
| 0cea73f9 | .../TASK-20260729-042/contract_review.yaml | `cbe508df...2358d0` | `cbe508df...2358d0` | YES |
| 0cea73f9 | .../TASK-20260729-042/derivation_check.md | `32ed2c28...94cb77` | `32ed2c28...94cb77` | YES |

Both receipts' `parent_sha` fields match Git exactly
(`68e4b9b740c70b84c99dddc3b779f8d23b74bfed` and
`561495cd59ca27ddd033c504b01aa53f9c024b64`). Both declare one deferred path —
their own receipt file — under `INT-BATCH007-T`, and in both cases the deferred
receipt does land in the immediately following commit (`561495cd` for the -041
receipt; the -043 receipt is itself the content of `71dd1880`). Declared sets
are strict supersets of committed sets by exactly the deferred path in each
case, with no extra path, no deletion and no AppleDouble sidecar.

No git command timed out. Every git check in this section **finished**.

`tools/check_merge_hygiene.py` was run on this branch and printed
`PASS: no conflict markers, no unparseable records`, exit 0.

---

## 4. D4 — the ruling is verifiably pre-data

At HEAD `b45edb59`, `git ls-tree -r HEAD --name-only` returns exactly two paths
under `experiments/EXP-STR-004/` — `specification.yaml` and
`derivation_note.md`. Confirmed absent, in the committed tree and in the
working tree:

- `experiments/EXP-STR-004/runs/` — **does not exist**, in any form; no
  `driver/`, no `results/` either.
- `ledger/evidence/EV-STR-004.yaml` — **does not exist**
  (`ledger/evidence/` carries `EV-STR-002.yaml` and `EV-STR-003.yaml` only).
- `ledger/decisions/DEC-20260729-004.yaml` — **does not exist**
  (`ledger/decisions/` carries `DEC-20260729-001/-002/-003` only).

The tracked working tree is clean, so the working tree and the committed tree
agree. **The ruling is pre-data as a checkable fact, not as an assertion.**

---

## 5. Re-derivation of the `O-2` pre-flight — FEASIBILITY CHECK, NOT EVIDENCE

Re-derived independently from `_generate_j0_instance` and the committed target
line `endomorphism_la.py:272`,
`k = (t_idx+1) * max(2, inst.seed % max(2, n-3)) % (n-1) + 1`. Instance
generation plus index arithmetic only; no relation collection, no factor base,
no rank measurement, no run record.

| quantity | `-043` receipt | this session | agree |
|---|---|---|---|
| CURVE-J12S1 `p` | 2293 | 2293 | YES |
| CURVE-J12S1 `n` | 733 | 733 | YES |
| CURVE-J12S1 derived seed | 100 | 100 | YES |
| CURVE-J12S1 `c` | 100 | 100 | YES |
| `gcd(c, n-1)` | 4 | `gcd(100, 732) = 4` | YES |
| distinct-target bound | 183 | `732/4 = 183`, and 183 realised | YES |
| max `R_base` required | 66 | `(193+2)//3+1 = 66` | YES |
| CURVE-J16S3 `p` | 42013 | 42013 | YES |
| CURVE-J16S3 `n` | 41617 | 41617 | YES |
| CURVE-J16S3 derived seed | 300 | 300 | YES |
| CURVE-J16S3 `c` | 300 | 300 | YES |
| `gcd(c, n-1)` | 12 | `gcd(300, 41616) = 12` | YES |
| distinct-target bound | 3468 | `41616/12 = 3468` | YES |

Additional check the receipt did not make, and it strengthens rather than
weakens its finding. `_collect_relations` dedups on the **x-coordinate** of the
target, not on `k`, and `x(kP) = x((n-k)P)`, so the distinct-`k` bound could in
principle have over-counted the usable targets by up to a factor of two. It
does not here: enumerating the realised sequence gives **183 distinct target
x-coordinates** for CURVE-J12S1, equal to the k-bound, because the realised
k-set contains no pair `{k, n-k}`. Against a maximum requirement of `R_base = 66`
the margin is 2.77x.

**The period is NOT smaller than the dispatching session found.** The top cells
were runnable on the target-supply criterion, and that part of the record does
not change.

**One narrowing this check does require.** The gcd bound governs the supply of
distinct **targets**; a base row exists only where a target also **decomposes**.
The pre-flight therefore shows that `O-2` does not fire; it does not show that
`R_base(B)` base rows are obtainable at every cell, which is the separate
shortfall risk `IV-6` and the `Q(B)` floor address. The `-043` receipt's phrase
"Every cell including the top rungs is runnable" is stronger than what a gcd
check can establish and should be read as "no cell is target-starved".

---

## 6. D6 — recount of every count in `QUEUE-AMEND-20260729-005`

Recomputed against the file itself, and where the claim is about the file's
history, against `git show 15fd845b:<queue>` versus `git show b45edb59:<queue>`.

### 6.1 Budget: 23700 -> 16200 s

The nine `tasks[].handoff.budget.wall_clock_seconds` values in the queue are
`3600, 300, 3000, 300, 7200, 300, 3600, 3000, 2400`, summing to **23700**,
matching `budget_record.declared_batch_task_budget_seconds` and its named terms.
The addendum's terms `3600 + 300 + 3000 + 300 + 0 + 0 + 3600 + 3000 + 2400` sum
to **16200**, and `23700 - 16200 = 7500 = 7200 + 300`, the two stood-down cards.
`card_count` 9, seven performed and two stood down: **9 = 7 + 2**. **ALL
CORRECT.** The addendum's refusal to claim 16200 fits inside `28800` is
consistent with `campaign_budget.total_wall_clock_seconds` being untracked.

### 6.2 The seven-path `-048` set

`declared_commit_sets.TASK-20260729-048_ledger_commits_8_paths_by_default` holds
**8** members. Removing the single declared removal
`ledger/evidence/EV-STR-004.yaml` and adding nothing yields **exactly** the
seven members listed in
`declared_commit_set_superseded.TASK-20260729-048_ledger_commits_7_paths_as_amended`,
in the same relative order. **CORRECT, member by member, not by cardinality.**

### 6.3 The 28 released run identifiers

The queue names **28 distinct** `RUN-STR-004-*` tokens: `AP-` and `EP-` across
the 14 cells `L12, L13, L24, L25, L48, L49, L96, L97, L192, L193, X96, X97,
A12M3, A13M3`. `14 x 2 = 28`, matching
`tasks[TASK-20260729-044].handoff.budget.maximum_runs = 28`. **CORRECT.**
The cell partition also recounts: `residue_zero_seven` and `residue_one_seven`
each have 7 members, are disjoint, and their union is the 14 declared cells.
No declared cell has `B mod 3 = 2`, as `residue_two_is_out_of_scope` states.

### 6.4 The 174-path `-045` product declaration (untouched, recounted anyway)

`28 run ids x 6 per-run files + 6 additional paths = 168 + 6 = 174`. **CORRECT**,
and unchanged by the amendment.

### 6.5 "No card deleted, no card rewritten, no committed archive's declared set enlarged"

Structural diff of the queue JSON across `15fd845b -> b45edb59`, flattened to
leaves:

- leaves **removed: 0**
- leaves **changed: 0**
- leaves **added: 176**
- top-level keys added: exactly one, `queue_amendments`
- `declared_commit_sets`: exactly **one** added key,
  `SUPERSEDED_IN_PART_BY_QUEUE-AMEND-20260729-005` — matching "one added pointer
  key"
- `tasks[]`: the nine ids and their order are unchanged; **five** cards
  (`-044, -045, -046, -047, -048`) each gain **exactly one** field,
  `AMENDED_BY_QUEUE-AMEND-20260729-005`; no existing field of any card is
  altered, removed or reordered — matching "a single ADDED note field on each of
  five cards"
- `TASK-20260729-041_snapshot_commits_4_paths`,
  `TASK-20260729-043_snapshot_commits_3_paths`,
  `TASK-20260729-045_snapshot_commits_174_paths` and the 11-path opening set are
  all byte-identical across the amendment

**The append-only claim is verified mechanically, not accepted on assertion.**
`5 = 2 stood down + 3 re-pointed` also reconciles with `cards_stood_down`
(2 task keys) and `cards_repointed` (3 task keys). `cards_appended` is `[]`,
matching "no card is appended".

### 6.6 "Three named independent derivations"

Three members, each named and each checkable: (1) the contract author's
`derivation_note.md` `D-1` to `D-7`, which its own `D-8` item 1 confirms "does
not derive `rank(D)`"; (2) the `TASK-20260729-042` reviewer, whose
`derivation_check.md` section 6.2 computes the rows and the exact rank; (3) the
recording Coordinator session. **The count and its members are CORRECT.** This
report is the fourth and it **agrees**.

### 6.7 "Four enumerated candidate statistics"

`the_discriminating_statistic_question_answered_candidate_by_candidate` carries
`C-1`, `C-2`, `C-3`, `C-4` as candidates, plus a `why_this_block_exists`
preamble and a `conclusion`. **Four candidates. CORRECT.**

### 6.8 One count in the queue this session cannot corroborate

`integrity_notes.INT-BATCH014-C` and the identifier block state that
`RT-20260729-034` and `RT-20260729-035` "were searched free in this worktree".
As section 7 shows, no search that `tools/allocate_id.py` can perform is capable
of finding an `RT-*` collision. The claim is not contradicted; it is
**unsupported by the named tool**, and section 7 states the narrowing.

---

## 7. D5 — the allocator on `RT-20260729-034`, `-035` and `-036`

`python3 tools/allocate_id.py --check <id>` was run on all three. **Verbatim
result, identical in form for all three** (only the id line differs):

```
identifier: RT-20260729-034
  well-formed: YES -- no pattern is enforced for RT-* in validate_ledger.ID_PATTERNS; well-formedness NOT checked
  occurrences across the union (8257 files scanned): 0

OK: well-formed and free across the union.
```

```
identifier: RT-20260729-035
  well-formed: YES -- no pattern is enforced for RT-* in validate_ledger.ID_PATTERNS; well-formedness NOT checked
  occurrences across the union (8257 files scanned): 0

OK: well-formed and free across the union.
```

```
identifier: RT-20260729-036
  well-formed: YES -- no pattern is enforced for RT-* in validate_ledger.ID_PATTERNS; well-formedness NOT checked
  occurrences across the union (8257 files scanned): 0

OK: well-formed and free across the union.
```

Exit status 0 in all three cases. **No collision. Nothing was renamed.**

### 7.1 The result is a NULL RESULT for `RT-*`, and that is the real finding

`RT-20260729-034` is demonstrably occupied — it is the `id` field of
`contract_review.yaml` line 2 and of `derivation_check.md` line 3 — yet the
allocator reports **0 occurrences**. Reading `tools/allocate_id.py`:

- `occurrences()` (lines 72-80) matches an id against a file's **basename** or
  its **parent directory name**. It never reads file content. An `RT-*` report
  id lives only in content, under a file named `contract_review.yaml`, so it is
  structurally undetectable.
- `SEARCH_GLOBS` (lines 43-48) covers `ledger/*.yaml`, `ledger/*/*.yaml`,
  `experiments/*/specification.yaml` and `knowledge/*/*.md`. It does **not**
  cover `coordination/**`, which is where every review report in this program
  lives.
- `RT` is absent from `PREFIX_TYPE` (lines 51-59) and from `ID_TOKEN`
  (line 61), so `--audit` and `--next` do not reach it either, and
  well-formedness is explicitly not checked.

**`tools/allocate_id.py` cannot detect an `RT-*` collision under the current
repository layout.** Its `OK ... free` verdict on these three ids carries no
information about their freedom, and `SUP-BATCH014-C` cannot be adjudicated by
it. This is reported as a defect of the tool's coverage, not of the ids.

### 7.2 Content-level occupancy — the check that does have an object

Repository-wide content search at this HEAD (this worktree only; it cannot see
non-ancestor branches, and this report does not claim otherwise):

| id | files carrying it | status |
|---|---|---|
| `RT-20260729-034` | `reviews/TASK-20260729-042/contract_review.yaml` (its own `id`), `reviews/TASK-20260729-042/derivation_check.md` (its own `id`), the `-042` task card, `dispatch_queue.json`, `ledger/goals/GOAL-ECDLP-001.yaml` | **TAKEN, consistently, by the `TASK-20260729-042` review** |
| `RT-20260729-035` | `-047` task card, `dispatch_queue.json`, `ledger/goals/GOAL-ECDLP-001.yaml` | **RESERVED for `TASK-20260729-047`; borne by no authored report yet** |
| `RT-20260729-036` | `archives/TASK-20260729-043/snapshot_commit_receipt.json` (as `verdict_source`), `dispatch_queue.json` (only inside `SUP-BATCH014-C`, which describes the defect) | **borne by NO authored report** |

### 7.3 Which id the review may keep

**`RT-20260729-034`.** It is the id the review declares for itself in **both**
of its files; it is the id `INT-BATCH014-C` reserves for `TASK-20260729-042`;
and it is the id `ledger/goals/GOAL-ECDLP-001.yaml` carries. Four of the five
records agree; the sole dissenting record is the `-043` receipt's
`verdict_source`, which is a **citation** of the review, not the review's own
declaration, and which is immutable. **The defect is in the citation, not in the
review, and the review keeps `-034`.**

**`RT-20260729-036` is borne by nothing and must never be issued to anything.**
It is not a free slot to be filled: `allocate_id.py`'s own instruction is
"Allocate above the union maximum; never reuse, and never fill a gap", and
`-036` now appears in a committed immutable receipt as a name for the `-042`
review. The next `RT-*` in this lineage should be `RT-20260729-037` or above.
`RT-20260729-035` stays reserved for `TASK-20260729-047` and is not reassigned.

**One correction to the framing this session was given.** The instruction stated
that "the queue reserves `-036` elsewhere". It does not. The queue mentions
`-036` exactly twice, both inside `SUP-BATCH014-C` and both describing the
mis-citation. What `INT-BATCH014-C` reserves elsewhere is `-034` (for `-042`)
and `-035` (for `-047`); `-036` is reserved for nothing.

---

## 8. Checks NOT PERFORMED, and why

Recorded as not performed, never as passed, per the amendment's
`what_is_dropped_because_its_object_will_not_exist`. In every case the object
does not exist because `TASK-20260729-044` is stood down.

1. Expected run count of exactly 28 — **NOT PERFORMED**, no runs exist.
2. Manifest schema completeness against the AGENTS.md artifact policy — **NOT
   PERFORMED**, no manifests exist.
3. Instance-parameter recomputation and seed integrity per run — **NOT
   PERFORMED**, no run records exist. (Section 5 re-derives the two curves'
   parameters as a feasibility check, which is not this check.)
4. Raw-to-summary leaf-by-leaf agreement and maximum absolute difference —
   **NOT PERFORMED**, no raw or summary files exist.
5. Matched base-row budget per cell, `CTRL-1`/`UC-2` — **NOT PERFORMED**, no arm
   consumed any budget. No cell is named unevaluable, because no cell was
   evaluated.
6. Member-by-member comparison of predicted and measured misalignment sets, and
   the `cardinality_only_agreement` test — **NOT PERFORMED**, no measured set
   exists.
7. Independent re-verification of named decomposition certificates — **NOT
   PERFORMED**, no certificates exist; zero were checked and none can be named.
8. Artifact-policy items: per-run timing windows, `numpy.__version__` in every
   `raw-result.json`, agreeing harness code hashes across 28 runs, non-empty
   stdout and stderr — **NOT PERFORMED**, no run artifacts exist.
9. `D-3` itself (that `_build_phi_invariant_factor_base` returns exactly `B`
   entries in whole-orbit layout at `B = 192, 193`) — **NOT PERFORMED**, and
   deliberately: it remains unverified, `CTRL-4`/`IV-4` are the declared route
   to it, and the D2 ruling of section 2 does not need it.
10. Model-independent corroboration — **NOT AVAILABLE**, per `INT-BATCH014-D`.
    Session independence is asserted; model independence is neither claimed nor
    achieved.

Nothing was left unreached for want of budget. No git command timed out.
