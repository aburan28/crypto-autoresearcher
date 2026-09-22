# J-3 — blind re-derivation of `d_F4`, `closure_D` and their separation

- **Task**: `TASK-20260921-f1e5bd`
- **Review round**: `REVIEW-SEMBIN-20260921-457504`, joint **J-3** (and nothing else)
- **Run under review**: `RUN-SEMBIN-b6eb9f` of `EXP-SEMBIN-c2c312`
- **Runs launched**: 0 (`maximum_runs: 0` respected; every number here is recomputed
  from committed records)
- **Artifacts**: `rederive.py`, `rederived.json` (sha256
  `e545eda29353734b8a50f592d9636957055d23221183387f2eecaf24cabbee15`), this report,
  `attestation.yaml`

---

## 0. Lead: the one place my numbers differ from the producer's

**On one instance the quantity the run records as `d_F4_semaev` is not the value
Semaev's own rule produces, and the two differ by 1.**

| instance | my `d_F4_semaev_literal` | producer `d_F4_semaev` | my `d_F4_naive` | producer `d_F4_naive` | `closure_D` |
|---|---|---|---|---|---|
| `sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3` | **5** | **4** | 5 | 5 | not computed |

The disagreement is definitional, not arithmetic, and it localises cleanly to two
named implementations:

- **Mine** — `rederive.py::derive_d_f4`, field `d_F4_semaev_literal`. Semaev
  excludes the trailing steps *"where 'step degree' was 5, 6, 7 with the message
  'No pairs to reduce'"* (`inputs/SEMAEV-2015-310/paper_fulltext.md`, lines 634–636).
  I transcribed that rule literally: delete the trailing run of rounds that
  **selected no pairs** (`sel == 0`), then take the maximum step degree. Result: 5.
- **The producer's** — whatever computes `d_F4_semaev` / `d_F4_last_productive_round`
  in this run (I did not read it). Its `d_F4_semaev` equals its own
  `d_F4_last_productive_round`, which deletes the trailing run of rounds that added
  **no new basis element** (`new == 0`). Result: 4.

The mechanical facts that separate the two rules, read off the raw log
`workerB/cells/instances/sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3.msolve.log`:

```
  4      34     553    1915 x 2220        0.69%        0 new      34 zero
  5     519     519   84267 x 84198       0.03%        0 new     519 zero
```

The two trailing rounds the producer excludes — and records under the field name
`f4_empty_step_degrees: [4, 5]` — are not empty of pairs. The degree-5 round
selected **519 pairs** and computed a row echelon form of an **84267 × 84198**
matrix. Semaev's "step degree" is defined (line 631) as *"the maximal total degree
of the polynomials for which a row echelon form is computed"*, and his exclusion is
predicated on the message *"No pairs to reduce"*. Both conditions point the same
way here: pairs were present and a row echelon form was computed at total degree 5.

**Whether that makes the producer's convention wrong is not mine to decide** — the
map, its validity, and what it implies are owned by other joints. What I establish
is that the two conventions are distinct, that they diverge on exactly one instance
in this run, and that the run retains enough raw data (`d_F4_naive = 5`,
`f4_empty_step_degrees = [4, 5]`) for a later reader to recover either value.

**This divergence cannot reach the headline.** The instance has no `closure_D` —
the closure instrument was never run on any n = 12 cell — so it contributes to no
separation. See §5.

Three further rows are flagged by my comparison but are **not** numeric conflicts;
they are reporting-scope differences on capped cells, detailed in §6.2.

---

# PART I — MY NUMBERS

Written before any producer artifact was opened. See §7 for the ordering evidence.

## 1. What I computed, and from what

`rederive.py` reads **only** raw records:

- the five `worker*/cells/results.jsonl` files, passed through a whitelist
  (`primitive_view()`) that **deletes** the producer's derived scalars —
  `d_F4_naive`, `d_F4_semaev`, `d_F4_last_productive_round`,
  `d_F4_partial_max_deg_seen`, `closure_D`, `D_macaulay_rank_statistic`,
  `f4_empty_step_degrees`, `f4_step_count`, and the per-cap `verdict`,
  `verdict_basis`, `sr_pred_rank`, `sr_HF`, `deficit_vs_semiregular` — before the
  derivation can see them. The derivation cannot read a producer scalar even by
  accident: the key is gone from the dict it is handed. Run with
  `--audit-blindness` to print the drop tally: 2 138 field instances dropped, of
  which 1 980 are the producer's derived scalars and 158 are unlisted keys.
- the raw `worker*/cells/instances/*.msolve.log` engine traces, which I parse with
  my own parser rather than using the record's producer-parsed `rounds` array.
  `rounds` is quarantined and reaches only the post-hoc cross-check in §6.4.
  51 log files are on disk, covering 49 distinct instances (two instances have a
  log in two shards); 48 of those yield a `d_F4`, and the 49th is the orphan of
  §6.5.

**Unit of analysis is the instance, not the (worker, instance) pair.** The two
instruments for one instance frequently live in *different* worker shards — the
heavy cells' F4 pass in `heavy`, their closure pass in `heavy_closure` — so keying
by worker splits instances and understates how many have both statistics. Records
are merged across shards by `instance_id`; all 7 cross-shard instances carry an
identical `system_sha256`, so no merge is conflicted.

### Definitions implemented

| name | rule |
|---|---|
| `d_F4_naive` | max step degree over all **complete** F4 rounds |
| `d_F4_naive_including_partial_rounds` | also counts a round whose header was printed before a kill truncated it |
| `d_F4_semaev_literal` | Semaev's rule transcribed: delete the trailing run of rounds with **no pairs** (`sel == 0`), then take the max |
| `d_F4_excl_trailing_unproductive` | delete the trailing run of rounds with **no new basis element** (`new == 0`), then take the max |
| `d_F4_excl_all_unproductive` | max over rounds with `new > 0`, wherever they occur |
| `closure_D` | smallest cap `D` at which `W_D` is already a Gröbner basis: `1 ∈ W_D`, or standard monomials `= |V(I)|` |

For `closure_D` I decide each cap from primitives only (`contains_one`,
`standard_monomials`, `standard_monomials_exceeds_cap`, `solutions`), never from
the recorded `verdict`. One refinement matters: `|V(I)|` is a property of the
**ideal**, not of the cap, so a value established at one cap decides the others.
That is what lets a cap whose standard-monomial count merely "exceeds the
enumeration cap" still be settled — `> 100000 > |V(I)| = 36` is decisive. Without
this propagation, 10 of my 15 `closure_D` values would have been upper bounds
rather than exact; with it, **all 15 are exact**.

## 2. The central finding about `d_F4`: Semaev's exclusion is vacuous on this engine

**Across all 48 instances with a trace — 749 F4 rounds — not one round has
`sel == 0`.** msolve never emits a "No pairs to reduce" step; it stops when the
pair list empties. So the exclusion that the task card calls "the whole subtlety
of this quantity" **has nothing to act on in this run**, and

> `d_F4_semaev_literal` = `d_F4_naive` on every instance, by construction.

The only thing an msolve trace offers as an analogue is the trailing run of rounds
that produced no new basis element. That is a strictly more aggressive rule: such a
round selected pairs and computed a row echelon form, so its degree counts under
Semaev's own wording. I report it separately rather than folding it into "Semaev's
value", and the gap between the two is §0.

## 3. Per-instance table — the 11 instances where both instruments were reached

`nv` = `d_F4_naive`; `sL` = `d_F4_semaev_literal`; `xT` = excl. trailing unproductive;
`xA` = excl. all unproductive; `cD` = `closure_D`; `sep` = `cD − nv`.

| instance | nv | sL | xT | xA | cD | qualifier | **sep** | trailing unproductive degrees |
|---|---|---|---|---|---|---|---|---|
| `ctrl_known_false_N35` | 2 | 2 | — | — | 2 | exact | **0** | [2] |
| `sem_n13_m4_t4_k4_low_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [2, 3, 4] |
| `sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [2, 3, 4] |
| `sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0_repeat` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [2, 3, 4] |
| `sem_n17_m3_t3_k6_low_B_ran_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [] |
| `sem_n15_m5_t3_k3_low_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [] |
| `sem_n15_m5_t3_k3_low_B_ran_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [] |
| `sem_n15_m5_t3_k3_ran_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [] |
| `sem_n15_m5_t3_k3_ran_B_ran_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [] |
| `sem_n19_m3_t3_k7_low_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [2, 3, 4] |
| `sem_n17_m3_t3_k7_low_B_equ_s20260913001_d0` | 4 | 4 | 4 | 4 | 4 | exact | **0** | [2, 3, 4] |

**The separation is 0 on all 11 instances, under every one of the four `d_F4`
conventions I computed.** The headline is convention-independent on its support.

Two observations on this table:

1. **`ctrl_known_false_N35` is where the conventions first bite.** Its single F4
   round is `deg 2, sel 69, new 0` — unproductive. Deleting the trailing
   unproductive run therefore deletes the *only* round and leaves the statistic
   **undefined** (`—` above), not 2. Semaev's literal rule deletes nothing and
   gives 2. This is the control the contract says gives every later disagreement
   its meaning, and one of the two candidate conventions has no value there.
2. The two **reproduction cells** recompute to `d_F4 = 4`
   (`sem_n13_m4_t4_k4…` and `sem_n17_m3_t3_k6…`), matching the value Semaev's
   Table 1 reports for those cells. Whether that discharges the baseline control
   is not my joint; I record the recomputation only.

### `d_F4` on the other 37 instances with a trace

| `d_F4_naive` | count | notes |
|---|---|---|
| 2 | 1 | `ctrl_known_false_N35` |
| 3 | 1 | `sem_n12_m6_t6_k2_ran_B_equ_s20260913005_d4` |
| 4 | 45 | — |
| 5 | 1 | `sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3` (the §0 instance) |

Two further instances reach a **partially executed degree-5 round** before being
killed, so `d_F4_naive_including_partial_rounds` = 5 while `d_F4_naive` = 4:
`null_n17_m3_t3_k6_low_B_equ_s20260913001_d0` (matched null, wall cap) and
`sem_n17_m3_t3_k8_low_B_equ_s20260913001_d0` (off-diagonal, memory cap). In both,
the degree-5 round header was printed — the pairs were selected and the matrix
begun — but no result line was written. I report both readings rather than choosing.

**Instrument-identity spot check.** `sem_n17_m3_t3_k6_…_d0_repeat` reproduces the
original's F4 per-degree pair profile and closure per-degree profile **exactly**.
`sem_n13_m4_t4_k4_…_d0_repeat` reproduces the closure profile exactly; its F4 pass
was never launched, so no F4 comparison exists for it.

## 4. Tail check (i) — statistics agree, do the per-degree profiles?

The contract calls numerical agreement for different reasons "the dangerous case".
The answer depends on which comparison you make, and both readings are in
`rederived.json`.

**Raw comparison (all degrees): 11 of 11 hit.** On every instance where the two
statistics agree, the degree-supports differ. But the difference is the *same* on
every instance and has an entirely structural cause: the closure profile always
carries pivots at degree 1 (and at degree 0 where the ideal is unit), and an F4 run
has **no step at degree 0 or 1 because there are no critical pairs there**. Linear
elements arise inside degree-2-and-up rounds, never as a degree-1 step.

| instance | F4 work degrees | closure gain degrees | only in closure |
|---|---|---|---|
| `ctrl_known_false_N35` | [2] | [1, 2] | [1] |
| `sem_n13_m4_t4_k4_low_B_equ_…_d0` | [2, 3, 4] | [1, 2, 3, 4] | [1] |
| `sem_n17_m3_t3_k6_low_B_equ_…_d0` | [2, 3, 4] | [1, 2, 3, 4] | [1] |
| `sem_n17_m3_t3_k6_low_B_equ_…_d0_repeat` | [2, 3, 4] | [1, 2, 3, 4] | [1] |
| `sem_n17_m3_t3_k6_low_B_ran_…_d0` | [2, 3, 4] | [0, 1, 2, 3, 4] | [0, 1] |
| `sem_n15_m5_t3_k3_low_B_equ_…_d0` | [2, 3, 4] | [0, 1, 2, 3, 4] | [0, 1] |
| `sem_n15_m5_t3_k3_low_B_ran_…_d0` | [2, 3, 4] | [0, 1, 2, 3, 4] | [0, 1] |
| `sem_n15_m5_t3_k3_ran_B_equ_…_d0` | [2, 3, 4] | [0, 1, 2, 3, 4] | [0, 1] |
| `sem_n15_m5_t3_k3_ran_B_ran_…_d0` | [2, 3, 4] | [0, 1, 2, 3, 4] | [0, 1] |
| `sem_n19_m3_t3_k7_low_B_equ_…_d0` | [2, 3, 4] | [1, 2, 3, 4] | [1] |
| `sem_n17_m3_t3_k7_low_B_equ_…_d0` | [2, 3, 4] | [1, 2, 3, 4] | [1] |

In every row `degrees_only_in_f4` is empty: the F4 support is contained in the
closure support on all 11.

**Like-for-like comparison (degrees ≥ 2): 0 of 11 hit.** Restricting to the range
where both indexings can carry mass, the supports are identical on every instance:
`[2, 3, 4]` against `[2, 3, 4]` (and `[2]` against `[2]` for the control).

**So my answer to tail check (i) is: no instance exhibits the dangerous case under
the only like-for-like comparison the retained artifacts support, and every
instance exhibits it under the raw comparison for a reason that is about indexing
rather than about the instruments.** The two profiles are indexed on different
things — the F4 side on *step degree*, the closure side on the degree of a pivot's
*leading monomial* — and the package retains no common indexing, so I compare
supports and never counts. A reader wanting a stronger answer needs an artifact
this run does not contain: the F4 per-degree profile of *new basis elements by
leading-monomial degree*, which would be directly comparable to the closure's.

## 5. Tail check (ii) — F4's "no pairs" degrees vs the Macaulay block's rank gains

**The contract's predicted mechanism cannot be tested as literally stated on this
run, on any instance.** The predicted coincidence was between "degrees at which F4
reports 'No pairs to reduce'" and "degrees at which the Macaulay block gains rank".
The F4 side of that comparison is **the empty set on all 48 instances**, because
msolve emits no zero-pair round at all (§2). A coincidence between the empty set
and anything is vacuous.

The closest available substitution on each side, with both reported per instance in
`rederived.json`:

- **F4 side (proxy)**: the trailing run of unproductive (`new == 0`) rounds. This
  is non-empty on 7 of 48 instances: degrees `[2, 3, 4]` on six of them, `[4, 5]`
  on `sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3`, `[2]` on the known-false
  control. On the remaining 41 it is empty — F4's last round was productive.
- **Macaulay side**: the block probed **only caps D = 3 and D = 4**, on every one
  of the 126 instances. So at most a single rank increment (4 − 3) is computable,
  and the increment at D = 3 is undefined because D = 2 was never probed. Where
  D = 4 completed the increment is positive; where it did not (all 15 n = 12
  cells), no increment exists at all.

The resulting comparison is therefore between a proxy set that is usually
`[2, 3, 4]` and a one-element set that is at best `{4}`. They do not coincide on
any instance where both are non-empty. **I report that as a structural coverage
limit rather than as a mismatch finding**: a two-point profile whose lower point has
no predecessor cannot answer a question about *which* degrees gain rank, whatever
the answer would have been. What the package would need is a Macaulay profile
probed from D = 2 (or from the generator degree) upward.

## 6. Coverage — what I could and could not recompute, and why

Of **126 instances**:

| quantity | recomputed | not recomputed | reason |
|---|---|---|---|
| `d_F4` | **48** | 78 | no msolve log on disk in any worker: the engine was never launched for that cell |
| `closure_D` | **15** | 108 | the closure instrument was never run on that instance |
| | | 3 | the instrument ran but no cap is decidable |
| both (⇒ separation) | **11** | 115 | — |

The 3 instances where the closure ran but `closure_D` is not derivable, each because
`|V(I)|` was never established anywhere in the instance's profile and no larger cap
was reached:

- `null_n17_m3_t3_k6_low_B_equ_s20260913001_d0` — **the matched null**. D = 3 and
  D = 4 both undetermined, D = 5 unreached. Its F4 pass was also wall-capped. So
  **no separation is computable on the matched-null control**, by either
  instrument. The one other matched-null instance in the run is the orphan of
  §6.5, which has no closure record either. I record that as a gap; what it means
  for the control is another joint's call.
- `sem_n21_m3_t3_k7_ran_B_equ_s20260913001_d0` — D = 4 gives 5323 standard
  monomials against an unknown `|V(I)|`.
- `sem_n17_m3_t3_k8_low_B_equ_s20260913001_d0` — D = 3, 4 undetermined, D = 5
  unreached.

I did not interpolate or estimate any of these, and no value in `rederived.json`
is a guess.

---

# PART II — COMPARISON AGAINST THE PRODUCER

Opened only after `rederived.json` was written and hashed (§7). Reproduce with:

```
python3 rederive.py --run-dir experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f \
                    --out rederived.json --compare
```

`--compare` is a post-hoc path that reads the very fields the derivation drops; it
runs after `--out` is written and cannot influence it. Verified: adding it left
`rederived.json` byte-identical at sha256 `e545eda2…`.

## 6.1 What reproduces

- **`closure_D` reproduces exactly on all 126 instances** — all 15 values and all
  111 nulls agree with the producer's, with no exceptions. My derivation reached
  those 15 values from the primitives alone, never reading the recorded `verdict`.
- **The producer's headline reproduces.** `closure_D − d_F4 = 0` on the 11
  instances where both instruments were reached. Independently: my 11-instance set
  is exactly the producer's; the producer's `summary.json` reports
  `agreements: 11`, `largest_separation: [0, 'ctrl_known_false_N35']`, and
  `n_instances: 126` — all three match my roll-ups.
- **`d_F4_naive` agrees on every instance where the producer reports one** (45 of
  45 non-null values).
- **The producer's trace parser is correct.** My independent parse of every
  `.msolve.log` agrees field-for-field (`deg`, `sel`, `pairs`, `new`, `zero`,
  `rows`, `cols`) with the `rounds` array of every record I derived from — zero
  field mismatches anywhere in the run.

## 6.2 The three flagged rows that are not numeric conflicts

On three capped cells the producer reports `d_F4_naive: null` where I derive a
value from the retained partial trace:

| instance | my `d_F4_naive` | producer `d_F4_naive` | producer `d_F4_partial_max_deg_seen` | cap |
|---|---|---|---|---|
| `null_n17_m3_t3_k6_low_B_equ_s20260913001_d0` | 4 | null | **4** | wall |
| `sem_n12_m6_t6_k2_ran_B_equ_s20260913002_d1` | 4 | null | **4** | memory |
| `sem_n17_m3_t3_k8_low_B_equ_s20260913001_d0` | 4 | null | **4** | memory |

These are **not** disagreements. The producer withholds the headline statistic on a
cell whose trace is incomplete — defensible, and arguably the more conservative
choice — while retaining the same number I derive under a different field name. The
two implementations agree on the value and differ only on whether to publish it.
I flag the rows so the mapping between the field names is on the record.

## 6.3 The one genuine disagreement

Stated in full in §0. In summary: the producer's `d_F4_semaev` implements
"exclude the trailing run of **unproductive** rounds", not Semaev's "exclude the
trailing run of **no-pair** steps". Consequences across the run:

- On 46 of 48 instances the two rules coincide, so the label is harmless there.
- On `ctrl_known_false_N35` they coincide only via a **fallback**: the producer's
  own `d_F4_last_productive_round` is `null` there (matching my `—`), and its
  `d_F4_semaev` falls back to 2, which is what Semaev's literal rule gives. Same
  number, reached by a different route.
- On `sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3` they differ: 4 against 5.
- The field the producer names `f4_empty_step_degrees` holds `[4, 5]` on that
  instance, for rounds that selected 34 and 519 pairs respectively. The name
  suggests Semaev's empty steps; the contents are unproductive steps.

**No instance where the conventions diverge has a `closure_D`**, so the divergence
reaches no separation value and does not disturb the headline. That containment is
a fact about this run's coverage, not a property of the definitions: had the
closure instrument reached the n = 12 cells, this instance would have produced a
separation that differs by 1 depending on which convention is used.

## 6.4 One artifact-binding observation

Four F4 *records* carry a `rounds` array that is a strict **prefix** of the log
file on disk under the same name — never a contradiction, always a prefix, with
zero field mismatches:

| instance | worker | recorded status | record rounds | log rounds |
|---|---|---|---|---|
| `sem_n19_m3_t3_k7_low_B_equ_…_d0` | workerB | unreached_declared | 0 | 16 |
| `sem_n19_m3_t3_k7_low_B_equ_…_d0` | workerB | unreached_declared | 0 | 16 |
| `sem_n19_m3_t3_k7_low_B_equ_…_d0` | heavy | unreached_memory_cap | 16 | 20 |
| `sem_n17_m3_t3_k7_low_B_equ_…_d0` | workerC | unreached_declared | 0 | 12 |

The consistent reading is that a retried cell keeps only the **last** attempt's log
under `<instance>.msolve.log`, so an earlier attempt's raw trace survives only
inside its record's `rounds` array. None of this touches a value I derived — in
each case a later, complete record for the same instance exists and is the one I
used — but it means the retained-log set is not one-to-one with the record set, and
a reader recomputing an earlier attempt's `d_F4` from the logs alone cannot. I
record it; whether it meets the contract's artifact-retention requirement is
another joint's call.

## 6.5 Three instances have retained artifacts and no record at all

*Found during write-up, after the comparison. Derived with the same blind parser
and the same definitions; `rederived.json` is unchanged and still hashes to
`e545eda2…`. Reproduce with `python3 rederive.py … --orphan-scan`.*

Reconciling the `cells/instances/` directories against the records gives **129
instance stems on disk against 126 instance ids in `results.jsonl`**. Three
instances left artifacts but produced no row in any `results.jsonl`:

| instance | artifacts retained | ran? |
|---|---|---|
| `null_n17_m3_t3_k6_low_B_ran_s20260913001_d0` | `.ms`, `.json`, `.gb`, `.msolve.log`, `.msolve.err` | **yes** |
| `null_n13_m4_t4_k4_low_B_equ_s20260913001_d0` | `.ms`, `.json` | no |
| `sem_n12_m6_t6_k2_ran_B_ran_s20260913001_d0` | `.ms`, `.json`, `.gb` | no |

Both my enumeration and the run's own `summary.json` count instances from
`results.jsonl`, so **both of us count 126 and both of us miss these three.** They
are invisible to any reader who does not reconcile against the directory.

The first of them genuinely ran. Its log carries three complete F4 rounds plus a
truncated degree-5 round, and `d_F4` is fully derivable from it:

| | value |
|---|---|
| `d_F4_naive` | **4** |
| `d_F4_naive_including_partial_rounds` | 5 |
| `d_F4_semaev_literal` | 4 |
| `d_F4_excl_trailing_unproductive` | 4 |
| per-degree pair counts | `{2: 4, 3: 93, 4: 1096}` |
| no-pair step degrees | `[]` |

It is a **second matched-null instance** — the `B_random` companion to the null
that appears in the records — and it has no closure or Macaulay record, so it
yields no `closure_D` and no separation. It therefore changes none of my §3
numbers and does not disturb the headline. What it changes is the coverage
statement: the matched-null control has two instances in this run, not one, and
`d_F4 = 4` is recoverable on the second even though no record reports it.

I record the reconciliation as a fact. Whether an instance that ran without
producing a record is an artifact-retention defect, a generator-side rejection, or
an interrupted worker is not something the retained files let me settle, and the
question belongs to whichever joint owns run integrity.

---

## 7. Ordering evidence — `rederived.json` was written first

In this order, and I attest to it:

1. Read `experiments/EXP-SEMBIN-c2c312/specification.yaml` (definitions) and
   `inputs/SEMAEV-2015-310/paper_fulltext.md` (Semaev's `d_F4`, "step degree", and
   the exclusion).
2. Surveyed the raw `results.jsonl` **schemas and primitive structures** and the
   raw `.msolve.log` format. Field *names* of the producer's derived scalars were
   visible in that survey; their *values* were not printed, and the derivation
   drops the keys outright.
3. Wrote `rederive.py` and ran it. Wrote `rederived.json`.
4. **Hashed and timestamped it**: sha256
   `e545eda29353734b8a50f592d9636957055d23221183387f2eecaf24cabbee15`,
   mtime `2026-09-21 19:55:23 UTC`, recorded in the shell transcript at
   `2026-09-21T19:55:44Z`.
5. **Only then** opened `summary.json` and the producer's per-instance derived
   scalars, and wrote Part II.
6. Re-ran the derivation after adding `--compare` and confirmed `rederived.json`
   byte-identical.
7. During write-up, reconciled the `instances/` directories against the records
   and found §6.5's three orphans. Derived with the same blind parser; re-ran and
   confirmed `rederived.json` byte-identical again. This step came after the
   comparison, and nothing in `summary.json` prompted it — it is a disk-against-
   records check that reads no producer-derived value — but the ordering is stated
   so a reader can discount it if they disagree.

**Disclosures.** Two, stated precisely rather than glossed:

- The per-cell `results.jsonl` files — which the card names as my inputs and my
  read scope — **embed the producer's derived per-instance scalars** alongside the
  primitive profiles. Perfect blindness to the producer's *numbers* is therefore
  not achievable from this package. What I could protect, and did, is blindness to
  the producer's *implementation*, which is the failure mode the exercise targets:
  I never read `code/summarize.py`, and my derivation drops those keys
  programmatically before any computation. The §0 disagreement is evidence the
  protection held — a contaminated derivation would have reproduced the producer's
  convention rather than diverging from it.
- My independence has a floor at the linear algebra. `closure_D` is derived from
  the recorded per-cap `standard_monomials`, `solutions` and `contains_one`, which
  the producer's closure instrument computed. With `maximum_runs: 0` I cannot
  recompute them. My re-derivation is independent at the level of the **statistic
  definitions applied to the per-degree profiles**, which is what the card asked
  for ("taken from the per-degree closure profiles"), and not at the level of the
  rank computations underneath.

I did **not** read, at any point: `summary.json` before step 5; and not at all
`task-report.md`, `results-table.json`, `code/summarize.py`,
`NOTES-deviations-and-limitations.md`, the `result` or `controls` blocks of
`manifest.yaml`, the `coordinator_prior` block of the review plan, or either
sibling reviewer's directory (`TASK-20260921-f2d82f`, `TASK-20260921-411a9d`).
No `git` command was run. Nothing was written outside
`coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-f1e5bd/`.

## 8. Limitations

1. **Zero runs.** Everything is recomputed from committed records; no engine was
   launched. Instances the run never reached stay unreached here.
2. **`closure_D` rests on the producer's linear algebra** (see §7).
3. **The separation rests on 11 instances**, 9 of them distinct systems (two are
   identity repeats), spanning n ∈ {13, 15, 17, 19} plus one planted-dependency
   control. n = 21, the n = 12 separation cells, the matched null and every
   `k = 8` off-diagonal cell contribute **no** separation value.
4. **`d_F4` at the two degree-5 partial rounds is convention-dependent** and I
   report both readings rather than choosing one.
5. **Tail check (ii) is answered as untestable-as-stated**, not as a negative
   result. Under AGENTS.md rule 5 the absent zero-pair steps are an engine
   property and the two-point Macaulay profile is a coverage limit; neither is
   evidence about the predicted mechanism.
6. **Scope.** I establish whether these numbers are the systems' or one
   implementation's. I make no finding on whether the map is right, on Assumption
   1, on the controls, or on the run's overall validity — each is owned elsewhere
   in this round and I am blind to all of them.
7. `model_verified: false` throughout (§9).

---

## 9. Required records

```yaml
review_attestation:
  task_id: TASK-20260921-f1e5bd
  joints_owned: [J-3]
  sources_read:
    - experiments/EXP-SEMBIN-c2c312/specification.yaml
    - inputs/SEMAEV-2015-310/paper_fulltext.md
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/workerA/cells/results.jsonl
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/workerB/cells/results.jsonl
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/workerC/cells/results.jsonl
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/heavy/cells/results.jsonl
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/heavy_closure/cells/results.jsonl
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/*/cells/instances/*.msolve.log
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/*/cells/instances/*.msolve.err  # 1 file
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/dispatch_queue.json
    - AGENTS.md
    - agents/validator.md
    - templates/research-records.md
    - experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f/summary.json  # AFTER step 4 only
  read_sibling_reports: false
  blind_from_respected: true
  verdict: holds
```

```yaml
validation_report:
  id: VAL-20260921-f1e5bd
  task_id: TASK-20260921-f1e5bd
  scope: J-3 only — recomputation of d_F4, closure_D and their separation.
         Not a verdict on RUN-SEMBIN-b6eb9f, on the stated map, or on any claim.
  run_ids: [RUN-SEMBIN-b6eb9f]
  artifact_checks:
    - all 5 worker results.jsonl present and parseable; 314 records, 126 instances
    - 51 msolve logs on disk over 49 distinct instances; 78 recorded instances have
      no log because the cell never launched
    - every log parsed with zero unparsed lines
    - cross-shard merges: 7 instances, all with a single system_sha256; 0 conflicts
    - 4 records carry a rounds array that is a strict prefix of the log on disk
      (retried cells retain only the last attempt's log) — see section 6.4
    - 129 instance stems on disk vs 126 instance ids in results.jsonl; 3 instances
      have retained artifacts and no record, one of which ran and yields
      d_F4 = 4 — see section 6.5. Both this derivation and the run's own
      summary.json enumerate from results.jsonl and so both omit these three.
  metric_recomputations:
    - d_F4 recomputed on 48 of 126 instances from an independent parse of the raw
      msolve traces; agrees with the producer on all 45 instances where the
      producer publishes a value
    - closure_D recomputed on 15 of 126 instances from per-cap primitives only;
      agrees with the producer on all 126 (15 values, 111 nulls)
    - separation closure_D - d_F4 recomputed on the 11 instances where both were
      reached; equals 0 on all 11 under all four d_F4 conventions
    - producer's F4 trace parser independently confirmed: zero field mismatches
    - ONE definitional divergence, one instance:
      sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3, producer d_F4_semaev = 4 vs
      rederived d_F4_semaev_literal = 5; no closure_D on that instance, so the
      divergence reaches no separation
  control_checks:
    - not in scope for J-3; the controls joint is owned elsewhere. Recorded as
      recomputation only: ctrl_known_false_N35 recomputes to d_F4 = 2 and
      closure_D = 2; both reproduction cells recompute to d_F4 = 4; the
      instrument-identity repeat of sem_n17_m3_t3_k6 reproduces both per-degree
      profiles exactly; the matched null yields neither statistic
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: passed
  limitations:
    - see section 8; in particular closure_D rests on the producer's linear
      algebra, and the separation rests on 11 instances / 9 distinct systems
    - rederived.json covers the 126 recorded instances only; the 3 unrecorded
      instances of section 6.5 are reported in this document and not in that file,
      which is left byte-frozen at the hash written before summary.json was opened
  artifact_paths:
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-f1e5bd/rederive.py
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-f1e5bd/rederived.json
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-f1e5bd/report.md
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-457504/TASK-20260921-f1e5bd/attestation.yaml
```

`verdict: passed` means the J-3 quantities are reproducible from the raw records by
an implementation that never saw the producer's, and that the headline separation
is a property of the two systems rather than of one summarizer. It does **not**
assert that the producer's `d_F4_semaev` is Semaev's `d_F4`, that the stated map is
correct, that the run is valid overall, or anything at all about Assumption 1.
