# TASK-20260730-033 recount note

Independent recount and re-execution log for the TASK-20260730-031 probe at
snapshot commit `e3cf9fdd770cbab3ebf55691a60143ace2b75f4c`.

This note is cited BY PATH AND TASK ID ONLY. **No `VAL-*` identifier is minted.**
No commit is made by this session. Nothing outside
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-033/`
was written.

Session independence: this Validator session did not produce any probe artifact
and did not read the Executor's own account before re-deriving the quantities
below. Model independence is NOT available on this harness and is NOT claimed
(INT-BATCH015-D).

---

## R1. R_base and Q recomputed at all fourteen cells BEFORE reading the probe table

Rule applied: `R_base(B) = (B + 2) // 3 + 1`, `Q(B) = max(60, B + 10)`.
Cell list read from `git show e3cf9fdd:experiments/EXP-STR-004/specification.yaml`
lines 229-360 (the `cells:` block). The comparison column is against the
specification's own per-cell `R_base:` / `Q:` fields.

| cell | B | m | R_base (mine) | Q (mine) | spec (R,Q) | verdict | 3*R_base |
|---|---|---|---|---|---|---|---|
| L12   | 12  | 2 | 5  | 60  | (5,60)    | MATCH | 15  |
| L13   | 13  | 2 | 6  | 60  | (6,60)    | MATCH | 18  |
| L24   | 24  | 2 | 9  | 60  | (9,60)    | MATCH | 27  |
| L25   | 25  | 2 | 10 | 60  | (10,60)   | MATCH | 30  |
| L48   | 48  | 2 | 17 | 60  | (17,60)   | MATCH | 51  |
| L49   | 49  | 2 | 18 | 60  | (18,60)   | MATCH | 54  |
| L96   | 96  | 2 | 33 | 106 | (33,106)  | MATCH | 99  |
| L97   | 97  | 2 | 34 | 107 | (34,107)  | MATCH | 102 |
| L192  | 192 | 2 | 65 | 202 | (65,202)  | MATCH | 195 |
| L193  | 193 | 2 | 66 | 203 | (66,203)  | MATCH | 198 |
| X96   | 96  | 2 | 33 | 106 | (33,106)  | MATCH | 99  |
| X97   | 97  | 2 | 34 | 107 | (34,107)  | MATCH | 102 |
| A12M3 | 12  | 3 | 5  | 60  | (5,60)    | MATCH | 15  |
| A13M3 | 13  | 3 | 6  | 60  | (6,60)    | MATCH | 18  |

14 of 14 MATCH. The `rows_final_if_no_shortfall` column of the specification
equals `3 * R_base` at every cell (checked above). The probe's per-record
`R_base_recomputed` / `Q_recomputed` and `R_base_in_queue_table` /
`Q_in_queue_table` agree with mine at all 28 records; `table_disagreements` is
`[]` and I independently find none.

**R1 = PASS.**

---

## R2. Archive chain re-derived from Git

```
git rev-parse e3cf9fdd^          -> 085f5d485cc21b4c46e4c6fb4a1db788567f79b7
git diff-tree --name-status -r e3cf9fdd   -> 8 paths, all status A
git rev-parse HEAD               -> 0b0199c72ed4a821b3f36d2aa6356285b4c6e99c
git status --porcelain           -> (empty; clean tree at review start)
```

Parent matches the receipt's `parent_sha` exactly. Commit is reachable from HEAD
(`0b0199c7` -> parent `e3cf9fdd`). The commit changes exactly the eight declared
probe paths and nothing else; `harness/` is untouched by it.

Every path SHA-256 re-derived by
`git cat-file blob e3cf9fdd:<path> | shasum -a 256`:

| path (under `.../BATCH-015/probe/`) | sha256 re-derived by me | vs receipt | vs manifest `artifact_sha256` |
|---|---|---|---|
| command.txt          | `91d739be6dc60572191888c93a93d6b4f6e82a30ba34f38542c8bec9d5d90cdf` | MATCH | MATCH |
| environment.json     | `cf063a15221b424cab04356136dbe02b19bbda4cb648ce6717f9ef7bb4bfb9f9` | MATCH | MATCH |
| probe_driver.py      | `9885810350ca914ffdb9a7dc1132315dea5ce14d8858de68438046c363b52977` | MATCH | MATCH |
| probe_manifest.json  | `b7dea56ff56a547660315bfb2258602edad88c1846e7c4ecbb462404bd192ae5` | MATCH | n/a (null by design) |
| stderr.log           | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | MATCH | MATCH |
| stdout.log           | `34f64cee2f1c5df5b90bcb375f407c26a0ab438cb505a40cc4ece094a76c7f54` | MATCH | MATCH |
| structure_probe.json | `d6bbd9b568f8f30cb8deccb9bb1db3be548b59b0cf3b1c00ad8cd27919a071f2` | MATCH | MATCH |
| supply_probe.json    | `c48b54d8c343f25ee563e57377e92f52be202643c60070e98154fba7c75a31ef` | MATCH | MATCH |

8 of 8 MATCH against the receipt. 7 of 7 MATCH against the manifest's own
`artifact_sha256`. `probe_manifest.json`'s self-entry is `null` with the stated
reason ("a document cannot contain its own hash"); the receipt supplies it and I
re-derived it. `stderr.log` is 0 bytes (`git cat-file -s` = 0), consistent with
the SHA-256 of the empty string.

Nine-path declaration recount: 8 producer paths in `e3cf9fdd` + 1 receipt path
in the immediately following commit `0b0199c7` (parent `e3cf9fdd`, exactly 1
path added: `archives/TASK-20260730-032/snapshot_commit_receipt.json`) = 9.
This is exactly the INT-BATCH007-T pattern the queue declares in advance.
**Members named:** probe_driver.py, command.txt, environment.json, stdout.log,
stderr.log, structure_probe.json, supply_probe.json, probe_manifest.json,
snapshot_commit_receipt.json.

Seven-path declaration recount: the BATCH-015 opening control-plane commit
`d0bdec84` changes exactly 7 paths — dispatch_queue.json, the five
`tasks/TASK-20260730-03{1..5}/task_card.md` mirrors, and
`ledger/goals/GOAL-ECDLP-001.yaml`. **Members named and counted: 7.** Exact.
(The later amend commit `085f5d48` changes 3 paths: dispatch_plan.json,
dispatch_plan.md, dispatch_queue.json — a separate declaration, not part of the
seven.)

Budget sum recount: `2700 (-031) + 300 (-032) + 2400 (-033) + 2400 (-034) +
2400 (-035)`. Partial sums: 2700, 3000, 5400, 7800, **10200**. Card count 5.
Matches `budget_record.declared_batch_task_budget_seconds = 10200`. Exact.

Review-artifact ordering rule: `git log --all -- .../BATCH-015/reviews` returns
only `d4c81aee`, which is **not an ancestor of HEAD** (`git merge-base
--is-ancestor` returns false) and contains `reviews/TASK-20260729-003/*` — a
different, unmerged branch reusing the `BATCH-015` directory name. On HEAD's
history no TASK-20260730-033 or -034 review artifact is committed. The rule
holds so far; my own files are written but NOT committed.

**R2 = PASS.**

---

## R3. PART A (RT35-CTRL-1 / CTRL-4) re-executed independently

Instance re-derived by calling the committed path myself, transcribing nothing:

```
ela._generate_j0_instance(1, 12)
  -> p=2293  n=733  a=0  b=417  derived_seed=100
ela._find_zeta3(2293) -> 1303 ;  1303^3 mod 2293 = 1
```

All five values agree with `structure_probe.json.instance_parameters`.

| B | len(F) | cond (i) `len(F)==B` | complete blocks | cond (ii) block identity | failing (j,k) | tail indices | distinct elements |
|---|---|---|---|---|---|---|---|
| 192 | 192 | **PASS** | 64 | **PASS** | 0 | [] | 192/192 |
| 193 | 193 | **PASS** | 64 | **PASS** | 0 | [192] | 193/193 |

Condition (ii) was evaluated by me as
`F[3j+k] == pow(zeta3, k, p) * F[3j] % p` for every `0 <= j < len(F)//3` and
every `k in {0,1,2}` — i.e. 64*3 = 192 individual identities at each B, all
holding. **The failing set is EMPTY and its members are therefore none — this is
an identity check, not a cardinality check (PRED-ID-STR).**

The factor bases are byte-identical to the probe's. Reproducing the driver's own
hashing convention (`hashlib.sha256(json.dumps(obj, sort_keys=True,
separators=(",",":")).encode())`, driver lines 105-108):

```
B=192 -> 076ddd920539d18403501bbee494776035dfc6cfb03aa368c1df01a2524f0c87  MATCH
B=193 -> bd33390621ec0381252250e1893b20f813c52facd931e96eb021e88e54c3a684  MATCH
```

**R3 = PASS. The two structure assertions are verified facts about committed
code at a named commit, re-derived in an independent session, not accepted on
the Executor's word.**

---

## R4. PART B (RT35-CTRL-2) — ALL TWENTY-EIGHT units re-executed independently

The card required at minimum L12, L13, A12M3, A13M3 at both arms. Part B cost
2.05 s in total, so I re-executed **all 28 units**, both arms, all fourteen
cells, in a fresh process, calling the committed functions directly with
`include_phi_orbits=False`.

Second instance re-derived: `ela._generate_j0_instance(3, 16)` ->
p=42013, n=41617, derived_seed=300, `_find_zeta3` -> 15662. Agrees with
`probe_manifest.instances_computed_not_transcribed["CURVE-J16S3"]`.

`R_base` and `Q` below are mine from R1; `shortfall = max(0, R_base - len(relations))`
is mine, computed by the pre-registered rule.

| cell | arm | B | m | \|F\| | R_base | Q | len(rel) | hits | attempts | shortfall | probe rel/hits/att | re-exec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L12   | A' | 12  | 2 | 12  | 5  | 60  | 29  | 29  | 183 | 0 | 29/29/183   | MATCH |
| L12   | E' | 12  | 2 | 12  | 5  | 60  | 17  | 17  | 183 | 0 | 17/17/183   | MATCH |
| L13   | A' | 13  | 2 | 13  | 6  | 60  | 31  | 31  | 183 | 0 | 31/31/183   | MATCH |
| L13   | E' | 13  | 2 | 13  | 6  | 60  | 20  | 20  | 183 | 0 | 20/20/183   | MATCH |
| L24   | A' | 24  | 2 | 24  | 9  | 60  | 60  | 60  | 150 | 0 | 60/60/150   | MATCH |
| L24   | E' | 24  | 2 | 24  | 9  | 60  | 60  | 60  | 132 | 0 | 60/60/132   | MATCH |
| L25   | A' | 25  | 2 | 25  | 10 | 60  | 60  | 60  | 139 | 0 | 60/60/139   | MATCH |
| L25   | E' | 25  | 2 | 25  | 10 | 60  | 60  | 60  | 129 | 0 | 60/60/129   | MATCH |
| L48   | A' | 48  | 2 | 48  | 17 | 60  | 60  | 60  | 67  | 0 | 60/60/67    | MATCH |
| L48   | E' | 48  | 2 | 48  | 17 | 60  | 60  | 60  | 68  | 0 | 60/60/68    | MATCH |
| L49   | A' | 49  | 2 | 49  | 18 | 60  | 60  | 60  | 67  | 0 | 60/60/67    | MATCH |
| L49   | E' | 49  | 2 | 49  | 18 | 60  | 60  | 60  | 68  | 0 | 60/60/68    | MATCH |
| L96   | A' | 96  | 2 | 96  | 33 | 106 | 106 | 106 | 106 | 0 | 106/106/106 | MATCH |
| L96   | E' | 96  | 2 | 96  | 33 | 106 | 106 | 106 | 106 | 0 | 106/106/106 | MATCH |
| L97   | A' | 97  | 2 | 97  | 34 | 107 | 107 | 107 | 107 | 0 | 107/107/107 | MATCH |
| L97   | E' | 97  | 2 | 97  | 34 | 107 | 107 | 107 | 107 | 0 | 107/107/107 | MATCH |
| L192  | A' | 192 | 2 | 192 | 65 | 202 | 183 | 183 | 183 | 0 | 183/183/183 | MATCH |
| L192  | E' | 192 | 2 | 192 | 65 | 202 | 183 | 183 | 183 | 0 | 183/183/183 | MATCH |
| L193  | A' | 193 | 2 | 193 | 66 | 203 | 183 | 183 | 183 | 0 | 183/183/183 | MATCH |
| L193  | E' | 193 | 2 | 193 | 66 | 203 | 183 | 183 | 183 | 0 | 183/183/183 | MATCH |
| X96   | A' | 96  | 2 | 96  | 33 | 106 | 106 | 106 | 289 | 0 | 106/106/289 | MATCH |
| X96   | E' | 96  | 2 | 96  | 33 | 106 | 106 | 106 | 296 | 0 | 106/106/296 | MATCH |
| X97   | A' | 97  | 2 | 97  | 34 | 107 | 107 | 107 | 289 | 0 | 107/107/289 | MATCH |
| X97   | E' | 97  | 2 | 97  | 34 | 107 | 107 | 107 | 296 | 0 | 107/107/296 | MATCH |
| A12M3 | A' | 12  | 3 | 12  | 5  | 60  | 60  | 60  | 82  | 0 | 60/60/82    | MATCH |
| A12M3 | E' | 12  | 3 | 12  | 5  | 60  | 60  | 60  | 104 | 0 | 60/60/104   | MATCH |
| A13M3 | A' | 13  | 3 | 13  | 6  | 60  | 60  | 60  | 75  | 0 | 60/60/75    | MATCH |
| A13M3 | E' | 13  | 3 | 13  | 6  | 60  | 60  | 60  | 95  | 0 | 60/60/95    | MATCH |

**28 of 28 units reproduce EXACTLY on `factor_base_length`, `len_relations`,
`hits` and `attempts`. Zero mismatches.**

Cells re-executed by me: **all fourteen** — L12, L13, L24, L25, L48, L49, L96,
L97, L192, L193, X96, X97, A12M3, A13M3 — at **both** arms.
Cells NOT re-executed: **none.**

Derived recounts, each with its members named:
- `|F| == B` at **28 of 28** units. Members: every row of the table above.
- `hits == len(relations)` at **28 of 28** units.
- `attempts == distinct_targets_measured` at **28 of 28** units.
- `shortfall == 0` at **28 of 28** units. **Maximum shortfall over all
  (cell, arm) pairs = 0.** Units with shortfall >= 1: **none** (empty set).
- `include_phi_orbits_actually_passed == false` at **28 of 28** units.
- `terminal_status == "completed"` and `valid == true` at **28 of 28** units.
  `units_not_completed_named` is `[]` and I independently find the set empty.
- `len_relations <= Q` at 28 of 28 units (no over-quota row).
- Distinct cells = 14, distinct arms = 2, 14 * 2 = 28 records. Exact.
- Records with `distinct_targets_measured == 183`: **8**, at 4 cells —
  L12/A', L12/E', L13/A', L13/E', L192/A', L192/E', L193/A', L193/E'.
  (The task card's framing "at six cells" is not what the data says; the true
  figure is 8 records at 4 cells. Recorded as a card-vs-data discrepancy, not a
  probe defect.)

**R4 = PASS.**

---

## R5. The pre-registered falsification condition, evaluated by me

Rule, taken verbatim from the queue and from
`probe_manifest.falsification_condition.text`:

> fires if `len(F) != B` at B = 192 or at B = 193, OR if
> `max(0, R_base(B) - len(relations)) >= 2` at any (cell, arm).

**Clause 1.** From my own PART A re-execution (R3): `len(F) = 192` at B = 192
and `len(F) = 193` at B = 193. `192 != 192` is false; `193 != 193` is false.
Clause 1 does **not** fire.

**Clause 2.** From my own 28-unit re-execution (R4): shortfall = 0 at every one
of the 28 (cell, arm) pairs. `max over all units = 0`. `0 >= 2` is false.
Clause 2 does **not** fire.

**Independent verdict: the falsification condition did NOT fire. Contributing
entries: the empty set. Maximum shortfall: 0.** This AGREES with the probe's
`falsification_condition_fired: false` and `contributing_entries_named: []`.
No disagreement; nothing BLOCKING arises here.

I also checked the driver implements this rule and no other. Driver lines
674-687 test exactly `a["returned_length"] != a["B"]` over valid PART A
assertions and `r["shortfall"] >= 2` over valid PART B records, with
`fired = len(contributing) > 0`; line 572 computes
`rec["shortfall"] = max(0, rb - len(rels))`. No third clause, no threshold
substitution, no re-weighting. Invalid / infrastructure-failed units are
excluded from the evaluation **in either direction** (line 664-666,
"INFRASTRUCTURE SIGNAL; not fed to the falsification condition in either
direction") — correct per AGENTS rule 3, and vacuous here because zero units
were invalid.

**R5 = PASS.**

---

## R6. The "183" question, resolved from the code

`_collect_relations` (endomorphism_la.py 269-278) enumerates targets by

```python
for t_idx in range(num_targets * 5):
    if len(relations) >= num_targets: break
    k = (t_idx + 1) * max(2, inst.seed % max(2, n - 3)) % (n - 1) + 1
    ...
    if target_x in seen_targets: continue
    seen_targets.add(target_x); attempts += 1
```

For CURVE-J12S1: `n = 733`, `inst.seed = 100`, `n - 3 = 730`, so the multiplier
is `c = max(2, 100 % 730) = 100`. The k-sequence is the arithmetic progression
`100*t mod 732`, whose image is the subgroup of multiples of
`gcd(100, 732) = 4` in Z/732, of size `732 / 4 = 183`, and whose period in t is
also 183.

Measured by me, by simulating the loop's own generator:

| t_idx range simulated | distinct k | distinct target_x |
|---|---|---|
| 300  | 183 | 183 |
| 1010 | 183 | 183 |
| 5000 | 183 | 183 |

The count is **invariant** as the iteration range grows from 300 (= 5*Q at
L12) through 1010 (= 5*Q at L192) to 5000. The `range(num_targets * 5)` break
is therefore **not** the binding constraint.

**Answer: 183 is a GENUINE SATURATION of the target set the committed loop can
reach, not an artifact of the loop's break condition.** At L192/L193 the loop
runs out of reachable targets (183) before it reaches its quota (202/203), so
`len(relations) = 183 < Q`. That is a supply ceiling, and it is still far above
`R_base = 65/66`, which is why the shortfall is 0.

**But the ceiling is a property of the GENERATOR, not of the curve.** I measured
the full target space: over all `k in 1..n-1` there are **366** distinct
x-coordinates on CURVE-J12S1 (`= (n-1)/2`, as expected since k and n-k share an
x-coordinate). The loop reaches **183 = 50.0%** of them, because every k it
generates satisfies `k ≡ 1 (mod 4)` (verified: the set of residues mod 4 hit
over 2000 iterations is exactly `{1}`). So "183" is **not** an exhaustion of the
target range on a p = 2293 curve; it is exhaustion of a structured index-4
arithmetic progression that the committed target generator happens to be
confined to for this seed.

This is a **latent limitation of the committed instrument**, correctly
*measured* by the probe (the probe reports `attempts` as the loop's own counter
and defines it exactly that way) but **not characterised** by it. It is recorded
here as a finding for downstream consumers, not as a probe defect: at any cell
requiring more than 183 base rows on CURVE-J12S1 the harness cannot supply them
regardless of B, and a future EXP-STR-004 execution at larger Q on this curve
would silently hit the same wall.

---

## R7. The `hits == len(relations)` question

From the committed code (m = 2 branch, lines 281-290):

```python
found, summands, cert = semaev._find_decomposition(...)
if found:
    hits += 1
    row = [0] * B
    for s in summands:
        sx = s[0]
        if sx in factor_base: row[factor_base.index(sx)] = 1
    if sum(row) > 0:
        relations.append(row)
```

`hits` is incremented on every `found`. A row is appended on every `found`
whose row is non-zero. The row can only be all-zero if *no* summand's
x-coordinate lies in the factor base — but `_find_decomposition` searches for
summands drawn from the factor base, so that branch is unreachable in practice.

**Answer: `hits == len(relations)` is essentially a TAUTOLOGY of how the
committed loop counts, not a substantive observation.** It is worth exactly one
thing — it certifies that the `sum(row) > 0` guard never discarded a hit at any
of the 28 units, i.e. no decomposition was found whose summands all fell outside
the factor base. It carries no information about relation quality, independence,
or usefulness. Any downstream record that presents `hits == len(relations)` as
an empirical finding would be overreading it. The probe itself does not do so.

---

## R8. The E-prime identity question

The queue and `experiments/EXP-STR-004/specification.yaml` declare arm E-prime
as a **phi-free factor base**. Traced through the committed code:

```
driver ARMS[1] = ("arm_E_prime", "_build_random_factor_base")   (driver line 151)
driver line 537: fb = ela._build_random_factor_base(inst, B)
endomorphism_la.py:117-119  _build_random_factor_base(inst, B)
    -> semaev.build_factor_base(inst, B, inst.seed)
semaev.py:60-73  deterministic: x = _seed_int(seed, f"fb{j}") % p,
    keep if distinct and E.lift_x(x) is not None, until len(xs) == size
```

So E-prime is `B` deterministic pseudorandom **on-curve** x-coordinates on the
**same curve**, from the **same derived seed**, differing from A-prime only in
the domain-separation tag (`"fb{j}"` vs `"phifb{j}"`) and in the absence of the
orbit-completion filter. **This is the declared null object, and it is a
correctly matched one: same shape, same size, same curve, same seed, structure
removed.**

I checked that the structure really is removed, and that the residue behaves as
a null object should:

| B | \|A'\| | \|E'\| | overlap | E' elements x with zeta3*x also in E' | A' complete phi-blocks |
|---|---|---|---|---|---|
| 12  | 12  | 12  | 1  | **0 / 12**   | 4 / 4   |
| 192 | 192 | 192 | 32 | **26 / 192** | 64 / 64 |
| 193 | 193 | 193 | 32 | **26 / 193** | 64 / 64 |

A-prime is fully phi-closed (64/64 complete blocks). E-prime is not phi-closed
at all at B = 12 (0/12), and at B = 192 shows only 26/192 = 13.5% incidental
closure — consistent with chance, since a B = 192 base covers roughly
192/1146 ≈ 17% of the ~(p-1)/2 on-curve x-coordinates and the chance expectation
is ≈ 32. **The residual structure DECAYS toward zero as B shrinks, which is
exactly what the null-object quantity should do (docs/inventor-protocol.md §3).
It does not fail to decay, so the canonical artifact tell is absent.**

**Answer: E-prime IS what the queue declares. No defect.**

One qualification, recorded as a limitation and not as a defect: E-prime is a
**deterministic single realisation** per cell, not an ensemble. It is a null
*object* but not a null *distribution*. The A'/E' `len(relations)` differences
visible above (29 vs 17 at L12; 31 vs 20 at L13; identical at 10 of the 14
cells) therefore carry **no error bar** and cannot be separated from realisation
noise. The probe makes no comparison and states none, so this is a constraint on
downstream use, not a flaw in the probe.

---

## R9. Prohibitions checked from the driver SOURCE

AST walk over the committed `probe_driver.py` (833 lines). Complete set of
harness calls made anywhere in the file:

```
ela._generate_j0_instance
ela._find_zeta3
ela._build_phi_invariant_factor_base
ela._build_random_factor_base
ela._collect_relations
harness_runner.curve_id
```

All six are on the specification's `committed_functions_the_driver_must_call`
allow-list. Nothing else from `harness` is called.

| prohibition | finding |
|---|---|
| `_measure_displacement_rank` called | **NOT CALLED** (absent from the AST call set) |
| `endomorphism_la.main()` called | **NOT CALLED**. The only `main` in the file is the driver's own, defined at line 211 and invoked at line 833 `sys.exit(main())`. `ela.main` never appears. |
| `harness.runner.write_run` called | **NOT CALLED** |
| `RunResult` constructed | **NOT CALLED** |
| `semaev._find_decomposition` called directly | **NOT CALLED** (only reached inside the committed `_collect_relations`) |
| subprocess / os.system / exec / eval | **NONE**. No `subprocess` import; the only matches for the string are in prose. |
| Sage | **NONE**. No import, no invocation. |
| closure / shifted / permuted / appended row | **NONE**. No row is transformed anywhere; the driver only takes `len()` of the returned list. |
| alpha, phi_alpha, rank, rank_M, displacement rank, misalignment set | **NONE computed**. Every textual occurrence is inside the negating `forbidden_computations_assertion.statement`. |
| any cost quantity | **NONE**. Wall-clock and RSS are present but labelled BUDGET ACCOUNTING in three separate places and never compared to a baseline. |
| certificate emitted | **NONE**; `certificate.kind = "none"` |
| `RUN-*` identifier | **ZERO occurrences** across all eight artifacts (grepped `RUN-[A-Z0-9]` in each git blob: 0,0,0,0,0,0,0,0). |
| writes outside the probe directory | **NONE**. All four `write_text` calls (lines 294, 693, 694, 822) are `PROBE_DIR / ...`. Nothing under `experiments/`, `harness/` or `ledger/`. |
| `harness/` modified | **NOT MODIFIED**. `git diff e3cf9fdd -- harness/` is empty. |

Harness code hashes verified against Git, and against the current worktree:

| file | git blob @ e3cf9fdd | worktree | manifest `harness_code_sha256` |
|---|---|---|---|
| harness/endomorphism_la.py | `5ac9a215eb3767015073b1825456beb394c92003c3bd5a834bb99847e1d44130` | SAME | MATCH |
| harness/semaev.py | `53a23952420f8ee724b70746eb7c872e54cbb33dc4cb24be1e88dcdcbef4817e` | SAME | MATCH |
| harness/toycurve.py | `0fdf7b35f1dd53d35161423c28627d26184ba8914cdae6c1003c67b7edfef113` | SAME | MATCH |
| harness/runner.py | `87333f60948641b802bb6b0742a7b80fb94ff4df1c3815134e142b1ac5d52288` | SAME | MATCH |

(`harness/rho.py` is also hashed in the manifest but is not among the four the
specification names as code under measurement; its presence is harmless.)

`harness_code_sha256` in `environment.json` equals the manifest's block exactly.
I re-ran every one of the harness re-executions in R3 and R4 against these exact
bytes, so my re-execution and the probe's are demonstrably measuring the same
instrument. **I modified nothing under `harness/`.**

**R9 = PASS.**

---

## R10. `include_phi_orbits` at every one of the 28 calls

From the source: there is **exactly one** `_collect_relations` call site in the
driver, at lines 538-539, and it passes the literal
`include_phi_orbits=False`. It is inside `one_unit()`, through which every one
of the 28 units (plus the 4 determinism repeats) is routed. There is no other
path and no conditional.

From the record: `include_phi_orbits_actually_passed` is `false` at **28 of 28**
supply records, and `include_phi_orbits_policy` reads "False at EVERY call,
without exception". `forbidden_computations_assertion.include_phi_orbits_true_anywhere`
is `false`.

Both the source and the per-call record agree. **R10 = PASS.**

---

## R11. Claim ceiling

I grepped all eight artifacts for `phi_alpha`, `displacement rank`,
`displacement_rank`, `misalignment`, `rank_M`, `discharg*`, `approv*`,
`diagnostic*`, `DEFER-BATCH009-001`, `weaken*`, `promot*`, `speedup`,
`crossover`, `cost ratio`.

`structure_probe.json`, `supply_probe.json`, `stdout.log` and `command.txt`:
**zero matches of any kind.**

`probe_manifest.json`: 7 matches, **all inside negations** —
`forbidden_computations_assertion.statement` ("no alpha; no phi_alpha; no
displacement rank; ... no misalignment set; ... no rank_M"),
`_measure_displacement_rank_called: false`, the budget disclaimer ("NOT A COST
RATIO"), and `run_ids_reason` ("No experiment is approved"). Not one is an
assertion of the forbidden quantity.

No artifact asserts an alpha, a rank, a cost, a diagnosticity verdict, a
hypothesis movement, a discharge of DEFER-BATCH009-001, an approval of
EXP-STR-004, or a re-adjudication of BATCH-014.
`falsification_condition.no_interpretation_note` explicitly declines to write an
interpretation, a recommendation or a disposition. **No BLOCKING over-claim
found. R11 = PASS.**

---

## R12. Determinism claim — what it does and does not establish

The probe's check: same process, second in-process execution, same commit, at
L12 and A12M3, both arms (4 comparisons), comparing `factor_base_length`,
`len_relations`, `hits`, `attempts`. All 4 report PASS, and the numbers in the
manifest's `determinism_check` match the corresponding primary records exactly
(verified by me against my own table in R4).

**What it establishes:** the committed functions are referentially stable
*within one process* — no hidden mutable module-level state, no RNG that
advances between calls, no dependence on invocation order. That is a real and
non-trivial property and the check is correctly scoped.

**What it does NOT establish:**
1. **Cross-process reproducibility.** A second call in the same interpreter
   shares `PYTHONHASHSEED` and all interned state. A same-process repeat cannot
   detect set/dict-iteration-order dependence, because the order is fixed for
   the process lifetime.
2. **Cross-machine, cross-OS, cross-Python-version reproducibility.** One host,
   one stack (macOS-26.6-arm64, CPython 3.13.1, numpy 2.4.0, sympy 1.14.0).
3. **Coverage of the other twelve cells.** Only L12 and A12M3 were repeated.
4. **Correctness.** A deterministic function reproduces a wrong answer exactly
   as faithfully as a right one.

**I partially close gap (1) and gap (3).** My R3/R4 re-execution ran in a
**separate process** on the same host and reproduced **all 28 units** and both
PART A assertions exactly. That is strictly stronger than the probe's own check
and rules out process-local hash-order effects on this platform. Gaps (2) and
(4) remain open and are recorded as limitations. In particular I did **not**
re-execute on a second machine, a second OS, or a second Python version, and I
did **not** independently verify that any returned relation row is a
mathematically valid relation (see R13).

---

## R13. Artifact policy completeness (AGENTS.md lines 287-303)

| required item | present? | where |
|---|---|---|
| exact command | YES | `command.txt`, all commands in execution order incl. the post-run hash pass |
| git commit and dirty-tree state | YES | `environment.git.head_commit = 085f5d48...` (the parent — correct, the probe ran before its own artifacts were committed), cross-checked against `PROBE_GIT_HEAD` (`git_head_crosscheck.match: true`), `PROBE_GIT_DIRTY_COUNT = "1"` |
| environment and dependency versions | YES | `environment.json` + manifest `environment`; no contradiction between them (checked field-by-field: 0 contradictions; `environment.json` is a strict superset) |
| input parameters and random seeds | YES | requested_seed 1 / 3, derived_seed 100 / 300, p, n, a, b, zeta3, curve_id, B, m, Q, R_base per record |
| requested policy / backend / resolved model id | PARTIAL | `requested_policy: executor-implementation`, `resolved_model_id: claude-opus-5`. **No explicit `backend` field**; the backend is only describable from `fallback_reason`. |
| model provenance / probe-verified | YES | `model_verified: false` with an honest reason (adapter module absent, INT-BATCH015-D) |
| reasoning effort / fallback / degraded | PARTIAL | `fallback_used: true` with reason. **`reasoning_effort` and a degraded-requirements field are ABSENT from the manifest `inference` block.** The task card carries `reasoning_effort: null`, so nothing is contradicted, but the field is not carried into the receipt. |
| stdout and stderr | YES | `stdout.log` (informative), `stderr.log` (0 bytes) |
| raw machine-readable results | YES | `structure_probe.json`, `supply_probe.json` |
| validity status and reason | YES | per-record `valid` / `terminal_status` / `invalid_reason`; `overall_terminal_status: completed`, `overall_terminal_reason: null`; `deviations: []` |
| timestamps and resource measurements | YES | `started_/finished_wall_clock_utc`, per-unit wall seconds, peak RSS with its unit ambiguity disclosed and the platform recorded so the unit is checkable |

`run_ids: []` — **the stated reason is ACCURATE.** I confirmed INT-BATCH015-F
reads, verbatim in the batch queue: "THE PROBE IS NOT AN EXPERIMENT RUN, CREATES
NO RUN IDENTIFIER, AND MUST NOT BE ARCHIVED AS ONE (INT-BATCH015-F)." This is
pre-registered in the opening commit, not a post-hoc rationalisation, and the
driver's behaviour matches it (no `write_run`, nothing under `experiments/`,
zero `RUN-*` strings in any artifact). The absence is **declared, not silently
omitted.**

`certificate.kind: "none"` — **the stated reason is ACCURATE.** The probe claims
no solve and no relation; it reports the *length* of a list and two structural
properties of a list of field elements. Under
`docs/claims-and-verification.md` a certificate is owed by a claimed
solve/relation, and none is claimed. An empty certificate block is correctly
**not** emitted in place of the statement.

**Nothing required by the artifact policy is actually missing except
`reasoning_effort`, a degraded-requirements field, and an explicit `backend`
field, all of which are minor and none of which affects any measured
quantity.**

---

## R14. NOT PERFORMED / NOT CHECKED

Recorded as NOT PERFORMED, never as passed:

1. **Cross-platform / cross-Python-version reproduction.** One host only. Not
   attempted; no second machine available to this session.
2. **Mathematical validation of relation rows.** I re-derived `len(relations)`
   but did NOT independently verify that any row is a correct decomposition of
   its target over the factor base. The probe claims no such thing, and
   `certificate.kind: none` says so, but the check was not run.
3. **`_measure_displacement_rank`, alpha, phi_alpha, closure, ladder, rank_M.**
   Deliberately not computed by me either — they are outside this batch's
   ceiling.
4. **`tools/validate_ledger.py` execution.** Not run; no ledger record is in
   scope for this card and I am forbidden to touch one.
5. **The BATCH-014 RT35-CTRL-1 / RT35-CTRL-2 required_controls text.** I read
   the queue's and the specification's statement of the two controls and checked
   execution against those. I did NOT separately open
   `BATCH-014/reviews/TASK-20260729-047/red_team_report.yaml` to re-confirm the
   controls' original wording, so "what was executed IS what was required" is
   verified against the queue and the frozen specification but **not** against
   the red-team report as a third source.
6. **Model independence.** NOT AVAILABLE on this harness and NOT CLAIMED
   (INT-BATCH015-D). Session independence IS asserted separately.
7. **Provenance of the single dirty worktree path at run time.**
   `PROBE_GIT_DIRTY_COUNT = "1"` is recorded but the dirty path is not named, so
   I cannot confirm from the receipt which file it was (almost certainly
   `probe_driver.py` itself, written but not yet committed — consistent with
   `head_commit` being the parent). Recorded as a LOW-severity gap.

All ten completion gates G1-G10 were reached inside the 2400 s cap. No check was
abandoned for budget.
