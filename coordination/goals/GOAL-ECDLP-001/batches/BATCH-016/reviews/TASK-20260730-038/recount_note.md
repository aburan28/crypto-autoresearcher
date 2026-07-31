# TASK-20260730-038 — recount note

**Cited by path and task id only. NO `VAL-*` IDENTIFIER IS MINTED** — two
duplicated immutable identifiers are already on record in this campaign.

Companion to
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/reviews/TASK-20260730-038/validation_report.yaml`.

Every figure below came from a command this reviewer ran in this session. Nothing
is transcribed from the producer's account. Where a check was not performed it is
in the report's `not_performed` list, never here as a pass.

**Independence note, stated up front.** `DEC-20260730-031` R-9 records that this
reviewer's predecessor independently re-derived both CTRL-4 conditions,
reproduced a tautology, and passed it without detecting that it was one.
Re-deriving the same expression is not a check of it. This review therefore does
not re-derive CTRL-4's English description. It executes the *same bytes* the
producer executed — obtained independently from the Git object store — against
inputs this reviewer constructed from the BATCH-016 queue specification alone,
and then separately probes what the assertion cannot see (§8). Model
independence is unavailable on this harness and is never claimed
(INT-BATCH016-D/E).

---

## 1. The blocking check — verbatim copy, verified from Git object content

Source resolution:

```
git rev-parse e3cf9fdd
  -> e3cf9fdd770cbab3ebf55691a60143ace2b75f4c
git cat-file blob e3cf9fdd:coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py | shasum -a 256
  -> 9885810350ca914ffdb9a7dc1132315dea5ce14d8858de68438046c363b52977
```

That file digest matches
`mutation_manifest.json.verbatim_checker_provenance.source_file_sha256` exactly.

Region slice and digest, computed by this reviewer:

```
python3: L = blob.split(b"\n"); region = b"\n".join(L[415:441])
  sha256(region)        = d8d248da8d28a512b89ad5e2dce6efdd2811fb84e1bb6370724867f034762dc5
  sha256(region + b"\n")= 89ecfa9ac1a6705c83deacb0ee03e75818b93575d3ca97bac28ddf301c1fc3b0
```

The recorded digest is the second form — lines 416–441 inclusive **with** the
trailing newline. 26 lines, 1444 bytes.

Copied-region slice out of the committed driver blob, by its marker comments:

```
python3: i = text.index(BEGIN_MARK) + len(BEGIN_MARK); j = text.index(END_MARK)
  sha256(text[i:j]) = 89ecfa9ac1a6705c83deacb0ee03e75818b93575d3ca97bac28ddf301c1fc3b0
  copied == source   -> True
  len(copied) = 1444 ; len(source) = 1444
```

**RESULT: the checker was COPIED, not rewritten. Zero characters changed inside
the region.** The cited path, the cited line range `[416, 441]` and the cited
commit `e3cf9fdd770cbab3ebf55691a60143ace2b75f4c` are all correct. The Executor
even kept the source identifiers `inst1` and `zeta3_1`, so not a single name
differs.

---

## 2. The subtler check — does the wrapping change the semantics?

Indentation-preserving wrapping *can* change behaviour, so this was checked
separately rather than assumed. The Executor added, all outside the compared
region:

```python
def ctrl4_checker_copied_verbatim(entry, F, inst1, zeta3_1, B):
    for _binding_only in (0,):
        if True:
            # === BEGIN VERBATIM COPY ... ===
            ...26 copied lines...
            # === END VERBATIM COPY ... ===
    return entry
```

**(a) Free names.** The region's free names are exactly `entry`, `F`, `inst1`,
`zeta3_1`, `B`, plus the builtins `len`, `pow`, `range`, `int`, `list`. All five
non-builtins are bound by the function signature. An AST walk of the whole
driver confirms no module-level name shadows any of those builtins. The region
calls **no** module-level function of either file: `sha256_obj` appears at source
line 442, which is one line *past* the copied range and is therefore not in the
copy.

**(b) Shadowing / capture by the wrapper.** The wrapper introduces exactly one
new name, `_binding_only`, which does not occur anywhere in the region. `if
True:` introduces none. Neither can rebind `entry`, `F`, `inst1`, `zeta3_1`, `B`,
nor the region's own locals `p`, `complete_blocks`, `failing`, `j`, `base`, `k`,
`want`, `got`, nor the sort lambda's parameter `d`.

**(c) Control flow.** A wrapping loop would matter if the region contained
`break`, `continue`, `return` or `yield` at wrapper level. It contains none. The
only loops are the region's own `for j` and `for k`. `for _binding_only in (0,)`
runs the body once and falls through. Python has no block scope, so the 12-space
nesting is presentation only — it exists solely so the copied text needs no
reindentation.

**(d) Do `inst1` and `zeta3_1` bind to what the original bound?** Traced in both
files:

| name | BATCH-015 source (`main()`) | mutation driver (`run_case`) |
|---|---|---|
| `inst1` | `inst1, zeta3_1 = val` where `val = (ela._generate_j0_instance(seed=spec["requested_seed"], field_bits=spec["field_bits"]), ela._find_zeta3(inst.p))`, `CURVE_SPEC["CURVE-J12S1"] = {"requested_seed": 1, "field_bits": 12}` | `inst` from `ela._generate_j0_instance(seed=1, field_bits=12)` — **same call, same arguments** |
| `zeta3_1` | the true `_find_zeta3(p)` | `z_check`, the zeta3 the case declares for checking |
| `F` | `ela._build_phi_invariant_factor_base(inst1, B, zeta3_1)` | `F_case`, the per-case (possibly mutated) list |
| `B` | loop variable of `for B in (192, 193)` | `B_FIXED = 192` |
| `entry` | dict pre-populated at source line 400 | `rec`, a dict pre-populated with case metadata |

The region reads only `inst1.p`, an `int` in both. The bindings are the same
objects of the same kinds. The one intentional freedom — that `zeta3_1` may be a
bogus `z` in case 1 — is the whole point of the card and is exactly what the
BATCH-015 red team did.

**CONCLUSION: the wrapping is semantically inert. The batch measured CTRL-4.**

---

## 3. Archive-chain recomputation, from Git object content

```
git rev-parse 1454d2be   -> 1454d2bebe84d14b1c84a02ebe46598f064e497f
git rev-parse 1454d2be^  -> 42ddd3b8249c921d85ae54e63f35ced7f468ad3e   (parent as recorded)
git log --oneline -5     -> 5bc95c8c (HEAD, receipt commit) ; 1454d2be ; 42ddd3b8 ; ...
git diff --stat 42ddd3b8 1454d2be
  -> 7 files changed, 2179 insertions(+)
```

Seven blob digests, each recomputed with
`git cat-file blob 1454d2be:<path> | shasum -a 256`:

| path | recomputed sha256 | receipt | manifest |
|---|---|---|---|
| `command.txt` | `03946ee14608dcb748b7eca93ea2bde263307445150581b4860bfd33128fedfb` | match | match |
| `environment.json` | `791c9714435d5bd3335ab64291179f8ec42cd9f1da7ea29d43eb1c2bcb597c13` | match | match |
| `mutation_driver.py` | `1d1a0d8d733c2d4294e772ddd0aff42136f6647df6202c56c689e16323d5e358` | match | match |
| `mutation_manifest.json` | `1b73e7e2e1520371b08ae8174c49df6332e8f4b96e293fa0976e5387e1528c84` | match | n/a (no self-hash) |
| `mutation_probe.json` | `0816c000c8f0f280b454dc119bea2c3fa2586545cdbbada4b366d4eb6a66e756` | match | match |
| `stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | match | match |
| `stdout.log` | `f1a78bc8f70457f3c2cddb70f7f4d2785f299f2396138aa5acbbe38045409134` | match | match |

`e3b0c442...` is the sha256 of the empty byte string — stderr really is empty,
consistent with a clean run.

**Path-set recount, members named, not counted.** Committed at `1454d2be`:
`command.txt`, `environment.json`, `mutation_driver.py`, `mutation_manifest.json`,
`mutation_probe.json`, `stderr.log`, `stdout.log` — **7**. Declared for
TASK-20260730-037 in the queue: those 7 plus
`archives/TASK-20260730-037/snapshot_commit_receipt.json` — **8**. The receipt
path lands in `5bc95c8c`, the immediately following commit, exactly as the
queue's INT-BATCH007-T disclosure states an archive receipt must (a commit cannot
contain the receipt that records its own sha). **7 + 1 = 8; the union equals the
declaration; nothing missing, nothing extra, no scope expansion.**

`harness/` and `BATCH-015/`:

```
git diff --stat e3cf9fdd 1454d2be -- harness/          -> (empty)
git diff --stat 1454d2be HEAD     -- harness/          -> (empty)
git diff --stat HEAD              -- harness/          -> (empty)
git status --porcelain                                 -> (empty)
git diff --stat 42ddd3b8 HEAD -- .../batches/BATCH-015/ -> (empty)
```

Manifest `harness_code_sha256`, each recomputed from the Git blob at `1454d2be`:

```
5ac9a215eb3767015073b1825456beb394c92003c3bd5a834bb99847e1d44130  harness/endomorphism_la.py
53a23952420f8ee724b70746eb7c872e54cbb33dc4cb24be1e88dcdcbef4817e  harness/semaev.py
0fdf7b35f1dd53d35161423c28627d26184ba8914cdae6c1003c67b7edfef113  harness/toycurve.py
87333f60948641b802bb6b0742a7b80fb94ff4df1c3815134e142b1ac5d52288  harness/runner.py
a50ddbee3f3186ba9c0a37012b26f0014468a4f7e2a2ecb5495f1fa0b9d63f77  harness/rho.py
```

All five match. **`harness/` is unmodified.**

---

## 4. Independent re-execution, fresh process, all five cases

The re-execution script was written by this reviewer from the queue's
`the_mutation_specification` block. It does **not** import
`mutation_driver.py`. It re-extracts the checker region from the Git blob at
`e3cf9fdd` and executes that text, so the checker under test is the same bytes,
obtained independently.

Computed instance parameters (none transcribed, none hardcoded):

```
p = 2293   n = 733   a = 0   b = 417
zeta3 = 1303        zeta3^3 mod p = 1
derived_seed = 100  curve_id = TOY-P12-cf8e3078
len(F_true) = 192   sha256(F_true as int list) = 076ddd920539d18403501bbee494776035dfc6cfb03aa368c1df01a2524f0c87
```

Prior-record figures p = 2293, n = 733, derived seed 100 agree with the computed
values. **No mismatch to report.**

| case | mine cond(i) | mine cond(ii) | mine JOINT | package | agree |
|---|---|---|---|---|---|
| `case_0_baseline` | PASS | PASS | PASS | PASS/PASS/PASS | yes |
| `case_1_z5` | PASS | PASS | PASS | PASS/PASS/PASS | yes |
| `case_1_z1234` | PASS | PASS | PASS | PASS/PASS/PASS | yes |
| `case_2_replaced_element` | PASS | FAIL | FAIL | PASS/FAIL/FAIL | yes |
| `case_3_interleaved_blocks` | PASS | FAIL | FAIL | PASS/FAIL/FAIL | yes |

Every case's `factor_base_sha256` also matched mine — `076ddd92…` (case 0),
`c514867f…` (z=5), `949f93c6…` (z=1234), `1fd55629…` (case 2), `9eccc970…`
(case 3) — which binds the outcomes to the exact input lists rather than to the
verdicts alone. **No divergence anywhere.**

---

## 5. The mutations are what they claim to be

### 5.1 Recomputed cubes (case 1 validity)

```
pow(5,    3, 2293) = 125    is_one = False
pow(1234, 3, 2293) = 1799   is_one = False
```

Both z are genuinely **not** cube roots of unity, so case 1 is a valid mutation
and not a degenerate no-op. The red team's prior-record figures 125 and 1799 are
**confirmed, not adopted**; no disagreement to report.

### 5.2 Case-2 replacement `x`, re-derived from the rule

Forbidden orbit of `F[0]` (a named **set**, not a count):

```
F[0] = 1963 ,  zeta3 = 1303 ,  p = 2293
pow(1303,0,2293)*1963 % 2293 = 1963
pow(1303,1,2293)*1963 % 2293 = 1094
pow(1303,2,2293)*1963 % 2293 = 1529
forbidden = {1963, 1094, 1529}   sorted [1094, 1529, 1963]
```

Upward scan from x = 1:

```
x = 1 : E.lift_x(1) is not None -> True ; 1 in F -> False ; 1 in forbidden -> False  =>  ACCEPT
chosen_x = 1
candidates_scanned = 1   (a COUNT; generating rule = the scan above, which
                          terminated on its first candidate)
```

Package records `chosen_x = 1`, `candidates_scanned_is_a_count = 1`,
`forbidden_orbit_of_F0_sorted = [1094, 1529, 1963]`. **Exact agreement,
including set membership of the forbidden orbit.**

The replaced element went `G[1] : 1094 -> 1`; the package records
`original_value_at_index_1 = 1094`, `replacement_value_at_index_1 = 1`,
`elements_changed_is_a_count = 1`. Agrees.

`x = 1` is the smallest field element, and its lying on this curve is a property
of this instance (a = 0, b = 417). It satisfies the stated rule **as written**,
and the rule was fixed in the queue before the card existed, so this is not a
rule chosen after seeing a result. Recorded so a reader knows the mutation's
magnitude.

### 5.3 Case-3 permutation, re-applied from the fixed specification

```
F[0..5]        = [1963, 1094, 1529,  310,  362, 1621]
H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]]
               = [1963,  310, 1094,  362, 1529, 1621]
multiset preserved      : True
indices changed (SET)   : {1, 2, 3, 4}     (indices 0 and 5 are fixed points)
```

Package: `first_six_before [1963, 1094, 1529, 310, 362, 1621]`,
`first_six_after [1963, 310, 1094, 362, 1529, 1621]`,
`multiset_preserved true`, `indices_changed_sorted [1, 2, 3, 4]`,
`index_map_new_from_old {0:0, 1:3, 2:1, 3:4, 4:2, 5:5}`. **The permutation is the
one the queue fixed, not another.**

---

## 6. Failing (j, k) pairs — recounted as SETS with member identity

`PRED-ID-STR` binds. A cardinality match with different members is disagreement.
Both sets below were compared as sorted tuple sets **and** record-by-record on
all five fields of each offending entry.

### Case 2 — my set `{(0, 1)}`, package set `{(0, 1)}` — **set equality: true**

```
j=0 k=1 index=1  F_index_value=1  expected_zeta3_k_times_F_3j=1094  F_3j=1963
```

Identical in the package on all five fields.
`cardinality_only_agreement: false`.

### Case 3 — my set `{(0,1), (0,2), (1,1), (1,2)}`, package set identical — **set equality: true**

```
j=0 k=1 index=1  got= 310  want=1094  base=1963
j=0 k=2 index=2  got=1094  want=1529  base=1963
j=1 k=1 index=4  got=1529  want=1621  base= 362
j=1 k=2 index=5  got=1621  want= 310  base= 362
```

Identical in the package on all four records and all five fields each.
`cardinality_only_agreement: false`.

**Why these pairs and not others** — derived independently, not merely observed.
Condition (ii) re-anchors on `F[3j]` for each block. Case 2 changed index 1 only,
so only `(0,1)` fails; `(0,0)` compares `F[0]` against `pow(z,0,p)*F[0]` and is
trivially satisfied. Case 3 left indices 0 and 5 fixed and moved 1,2,3,4: block 0
keeps anchor `1963`, so `(0,1)` and `(0,2)` fail; block 1's anchor became
`H[3] = 362 = F[4]`, so `(1,0)` is again trivially satisfied against the *new*
anchor while `(1,1)` and `(1,2)` fail. **`(j, 0)` can never fail for any input
whatsoever** — one third of the 192 comparisons is vacuous by construction. That
observation is developed in §8.

---

## 7. Other recounts

### 7.1 Pre-registered consequence flag, recomputed by the stated rule and no other

Rule: TRUE if the JOINT is PASS for case (1) at either z, **or** for case (2),
**or** for case (3); case 0 excluded; a non-completing case excluded in both
directions.

```
case_1_z5    JOINT = PASS  -> contributes
case_1_z1234 JOINT = PASS  -> contributes
case_2       JOINT = FAIL  -> does not contribute
case_3       JOINT = FAIL  -> does not contribute
case_0                     -> excluded by the rule
incomplete cases           -> none, so the exclusion list is empty
FLAG = TRUE ; contributing = {case_1_z5, case_1_z1234}
```

Package: `assertion_passed_a_mutated_case: true`, contributing cases named as
`[case_1_z5, case_1_z1234]`, exclusions `[]`. **Exact agreement, including
contributing-case set membership.**

**What the flag does not add.** Its truth value was fixed before the batch ran —
it is carried entirely by case 1, whose PASS is pre-stated and already
committed, and the queue says so itself
(`AND_IT_IS_ALREADY_TRIGGERED_STATED_PLAINLY_RATHER_THAN_DISCOVERED_LATER`).
The two cases carrying new information both contributed FALSE. The flag is not a
result of this batch and must not be read as one. **The new information is
exactly: cases 2 and 3 FAILED, driven by condition (ii), with condition (i)
PASSING in both.**

### 7.2 Budget sum, terms named

```
600 (TASK-20260730-036)
300 (TASK-20260730-037)
1800 (TASK-20260730-038)
1800 (TASK-20260730-039)
2400 (TASK-20260730-040)

600 + 300  =  900
900 + 1800 = 2700
2700 + 1800 = 4500
4500 + 2400 = 6900      declared: 6900   ✓
card_count = 5 (the five named above)    declared: 5   ✓
```

Each term matches its own `budget.wall_clock_seconds` in `dispatch_queue.json`.

### 7.3 Artifact sizes (`git cat-file -s` at `1454d2be`)

```
 55779  mutation_driver.py
  2089  command.txt
  2286  environment.json
 21457  mutation_manifest.json
 25769  mutation_probe.json
     0  stderr.log
  3738  stdout.log
------
111118  TOTAL

per-file cap 524288  -> largest is 55779, under cap
tree cap    2097152  -> 111118, under cap
```

### 7.4 Observed budget consumption

```
total wall  0.517 s  against a 600 s cap
peak RSS    74776576 B against a 1073741824 B cap
pre-flight  1404830171136 B free (1308.35 GiB) against a 5368709120 B floor
deviations  [] recorded; none found by me
```

Labelled **budget accounting, not a cost measurement**, in the manifest, in every
case record and in `stdout.log`. This note repeats the label rather than
relaxing it.

### 7.5 Prohibitions, checked from the driver source

AST walk of the committed blob. The complete list of harness entry points called
is: `ela._generate_j0_instance`, `ela._find_zeta3`,
`ela._build_phi_invariant_factor_base`, `inst.curve`, `E.lift_x`,
`harness_runner.curve_id`. All six are permitted.

`_measure_displacement_rank`, `_collect_relations`, `_build_random_factor_base`,
`endomorphism_la.main()` and `harness.runner.write_run` are **not called** — every
occurrence of each string is inside prose asserting that it is not called. No
`subprocess` import; module imports are exactly `hashlib`, `json`, `os`,
`platform`, `resource`, `signal`, `sys`, `pathlib.Path`, plus `harness.
endomorphism_la`, `harness.runner`, `numpy`, `sympy` inside `main()`. No `exec`,
`eval`, `compile` or `__import__` call (apparent hits are the substrings of
`execution`/`evaluation`, and `.resolve()` for `solve`). The string `RUN-` does
not occur at all. Exactly three `write_text()` targets, all under the mutation
directory. Nothing under `experiments/`, `ledger/`, `knowledge/`, `harness/` or
`tools/`. No certificate emitted — a `kind: none` statement with a reason instead.

### 7.6 Case-1 prohibition

Scanned all seven committed artifacts. Case 1's pre-stated status is carried at
four independent places (driver docstring, `CASE_META` for both z, the per-case
`status_of_outcome` in every probe record including the determinism repeats, and
the manifest's `case_1_pre_stated_status`), each saying its reproduction is not a
new result, not a discovery, not a replication and not evidence about
phi-invariance, and each citing TASK-20260730-034 OBJ-1, EV-STR-005 L-1 and
DEC-20260730-031. `stdout.log` logs it as a bare per-case line with no adjective.
Case 0 is labelled an instrument sanity check everywhere it appears and is
excluded from the consequence in code. **No breach.**

### 7.7 Mirror-vs-queue

The scratchpad `TASK-20260730-038.queue_entry.json` is JSON-canonically equal to
the `dispatch_queue.json` `tasks[]` entry (True); likewise for
TASK-20260730-036. The `task_card.md` mirror agrees with the queue on role,
dependency, budget, write scope and the blocking checker-provenance instruction.
No disagreement found. (The queue's own recount constraint reads "the eight-path
and eight-path declarations" — a duplicated word, not a semantic conflict; both
eight-path sets, TASK-20260730-037's and TASK-20260730-040's, are recounted
above and in the report.)

### 7.8 One inconsistency found

`command.txt` comments its git-state block as *"(clean tree, dirty count 0)"*.
The actually recorded value is **1**, in `environment.json`
(`MUT_GIT_DIRTY_COUNT: "1"`) and in `stdout.log` (`dirty_count=1`). The
measurement is honest and was recorded, not suppressed; the prose comment beside
it is wrong. The dirty path is fully explained — `mutation_driver.py` was an
untracked file at launch, unavoidable for a card that writes its own driver — and
no artifact draws any conclusion from tree cleanliness. **Minor, non-blocking.
Do not repair in place: the file is committed and immutable; a correction
supersedes.**

---

## 8. The question that matters most — is the two-way characterisation complete?

**No.** "Detects layout breaks, blind to `zeta3` validity" is not the complete
characterisation, and one of the gaps is a *layout* break.

**Status of this section: validator exploratory probe.** Not part of
CTRL-RT034-A, not pre-registered, **not a result of BATCH-016**, and not to be
recorded as one. Every outcome below was measured by this reviewer with the same
verbatim checker region, on the same instance (p = 2293, zeta3 = 1303) at
B = 192.

### The root cause, stated exactly

Condition (ii) re-anchors on `F[3j]` separately for every block j and compares
only ratios *within* that block. Two consequences follow mechanically:

1. **`(j, 0)` can never fail for any input**, because it compares `F[3j]` against
   `pow(z,0,p)*F[3j] = F[3j]`. One third of the 192 comparisons is vacuous by
   construction.
2. **The predicate is purely relative.** It constrains `F` only up to an
   arbitrary choice of 64 independent anchors and their order. It never asks
   whether any element is an x-coordinate on E, whether the elements are
   distinct, or whether they came from the constructor.

> **The complete semantic content of CTRL-4 is: `len(F) == B`, and `F` is a
> concatenation of `len(F)//3` geometric triples whose common ratio equals the
> `z` you handed the checker.** Nothing outside that statement is detected —
> including *which* `z`, *which* curve, and *which* anchors.

### Measured further classes

| # | mutation | cond(i) | cond(ii) | JOINT | control on the probe |
|---|---|---|---|---|---|
| 4a | 64 blocks permuted **as units** (order reversed, block interiors untouched) | PASS | PASS | **PASS** | multiset preserved True; all elements still on curve True; list ≠ F True |
| 4b | 192 elements, ratio structure intact, every anchor chosen so `E.lift_x(x) is None` | PASS | PASS | **PASS** | 192 of 192 elements **not on the curve**; **zero** elements in common with F |
| 4c | block j=0 repeated 64 times | PASS | PASS | **PASS** | 3 distinct elements vs the true F's 192 |
| 4d | all-zero list of length 192 | PASS | PASS | **PASS** | — |
| 4e | bogus z=7 (`pow(7,3,p)=343`) **and** arbitrary integer anchors, checked with the same z | PASS | PASS | **PASS** | compounds 1 with 4b |
| — | *positive control:* perturb one element, `F[4] -> F[4]+1 mod p` | PASS | **FAIL** | **FAIL** | 1 failing pair — the probe does report FAIL when a within-block ratio breaks |

The positive control is load-bearing: without it the five PASS rows would not be
evidence, only scaffolding noise.

### Why 4a is the most consequential

**4a is a layout break and CTRL-4 does not see it.** It is the exact complement
of case 3: case 3 permuted *across* block boundaries and was caught; a
permutation that *respects* block boundaries is invisible. So "CTRL-4 detects
layout breaks" is false as stated — what it detects is layout breaks that alter
**within-block ratios**. Anything downstream that depends on factor-base *order*
— row ordering, index-to-element maps, positional comparison of two runs' factor
bases — is unprotected.

**4b** shows the checker never tests curve membership: it calls no `lift_x` and
no curve method at all, reading only `inst1.p`. A "factor base" sharing zero
elements with the real one, none of them on the curve, passes in full. Note the
asymmetry with case 2: case 2's replacement *was* on the curve and was caught,
because what broke was the ratio — CTRL-4 never checked the property case 2's
mutation happened to preserve.

**4c/4d** show a maximally degenerate factor base passes. Anything relying on
CTRL-4 to establish that F supplies 64 distinct orbits or 192 distinct targets is
relying on a check that never looked.

### What this section is not

Not a disposition on CTRL-4 — retire-or-rewrite is the Coordinator's call at
TASK-20260730-040 and is not taken here. Not a claim that any past "CTRL-4
passes" record was false; those records reported a true fact about a weak
predicate. Not evidence about phi-invariance, alpha, rank, supply or cost. Not
pre-registered, therefore not scored against any expectation. Scoped to
CURVE-J12S1 at B = 192 and to nothing else. If any decision is to rest on it, it
should be re-run under a proper card.

---

## 9. What the determinism check establishes, and what it does not

The producer re-executed all five case records **in the same process** and
compared `returned_length`, `condition_i`, `condition_ii`, `joint_pass_fail`,
`factor_base_sha256` and the failing (j, k) list — the last compared as full
records, not as a count. Result PASS on all five,
`failing_pairs_identical_as_sets_not_counts` true on all five.

**It establishes:** repeatability within one interpreter session at one commit —
no hidden per-call randomness, no mutable global state accumulating between
cases, no iteration-order nondeterminism. It also shows cases 1–3 did not corrupt
`F_true` for the repeat, since case 0's repeat reproduces the same
`factor_base_sha256`.

**It does not establish:** cross-process, cross-host, cross-OS, cross-Python or
cross-dependency-version reproducibility; independence from `PYTHONHASHSEED`
(unpinned — irrelevant here only because the sets are sets of ints and the
failing list is explicitly sorted, but that is an argument, not a measurement);
seed independence (seed = 1 only); B independence (B = 192 only); instance
independence (CURVE-J12S1 only). **A same-process repeat is the weakest
determinism check available.**

This review supplied **the missing cross-process leg**: a separate interpreter,
a separately written script, reproducing every value including all four
factor-base digests and both failing-pair sets — extending the evidence to
cross-process **at this host, this Python and this commit, and no further**.

---

## 10. Bottom line

The blocking check passes. The checker is the committed CTRL-4 checker byte for
byte, and its wrapping is semantically inert. The archive chain, the harness
integrity, the mutations, the outcomes, the failing-pair **set membership**, the
consequence flag, the prohibitions, the case-1 prohibition and the claim ceiling
all verify. All five cases reproduce in a fresh process with no divergence. One
minor non-blocking inconsistency (§7.8). One material observation: the control's
characterisation is incomplete, with three further blind classes measured (§8).

**Verdict: `passed`. `blocks_ledger_record: false`.** A passed validation means
the receipt is admissible evidence. It does not support an ECDLP claim, does not
demonstrate a speedup, does not move H-STR-002, and does not authorize
promotion or decide CTRL-4's disposition.
