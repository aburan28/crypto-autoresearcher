# TASK-20260913-7ca970 — joints J4 and J5 only

Review round `REVIEW-SEMBIN-20260913-run2`. Object: `RUN-SEMBIN-cbd770` of
`EXP-SEMBIN-92724f`, snapshot-archived by `TASK-20260913-a10003` at
`24f5a574a7f6ae13089edaf3b0fb925e6f84ab23`. Working-tree hashes of the bound
run artifacts match that snapshot `path_sha256` (recomputed; see
`scratch/j4_j5_out.json`). This is a Coordinator-committed snapshot, not a
working-tree-only receipt.

This report owns **J4 and J5 only**. It is not a verdict on H-SEMBIN-c59e50,
on any other joint, on any solving degree, or on any curve's security. No
degree of regularity, first-fall degree or d_F4 is measured or asserted
(IMP-SEMBIN-ENGINE). An infrastructure failure or unreached cell is not
negative mathematical evidence; this run recorded **zero** unreached cells.

Independent recomputation lives in
`scratch/j4_j5_recompute.py` → `scratch/j4_j5_out.json`. Ratios and the typed
objective were recomputed from raw `image-sizes.json` rows and from the three
GG substitutions stated in the specification, without importing
`cost_model.py`, `image_enum.py`, `families.py` or `run_experiment.py`.
`binary_field.py` was imported only for one brute-force group-sum of a recorded
draw (curve law, not the convolution).

---

## J4 — Arm D, the gating negative result

**Verdict: holds.**

Deciding artifacts: `experiments/EXP-SEMBIN-92724f/runs/RUN-SEMBIN-cbd770/image-sizes.json`
(1120 unaggregated rows) together with `scratch/j4_j5_out.json` (independent
domain reconstruction, fibre-mass identities, per-cell distributions, and
one brute-force cross-check).

The joint asks whether the exact coset-typed image ratio genuinely misses the
predicted `m!` at every one of seven cells (median 0.4315, no cell within 10%,
a draw below half `m!` in every cell) and whether the measurement is exhaustive.

### Exhaustiveness, independently of the ratio

The contract forbids sampling. Reconstruction from the recorded factor-base
sizes, with no use of the printed ratio summaries:

- 7 declared cells × 160 draws = **1120** typed enumerations. Statuses:
  `completed` 1092, `empty_typed_base` 28, `unreached` **0**. Every typed
  domain is below the recorded cap `2^24` (largest completed domain 967680).
- For every row, `typed_domain_size` equals the product of `typed_base_sizes`
  (0 mismatches).
- For every completed row, the stored fibre histogram has mass equal to the
  recorded domain and the positive-bin count equals the recorded image size
  (0 mismatches). That is conservation of the enumerated domain, not a
  sampled estimate.
- Untyped domain equals `C(|F|+m-1, m)` and ordered untyped domain equals
  `|F|^m` (0 mismatches).
- `image_size_ratio_typed_over_untyped` and `ratio_over_predicted` recompute
  from `exact_image_size_typed / exact_image_size_untyped / m!` to machine
  precision (0 mismatches).
- Every one of the 1120 draws carries `draw_validated_pairwise_distinct: true`.
- Independent brute force of the first completed draw
  (`n=12, k=2, m=6, B=1, seed=20260913301, draw=0`, additive, domain 128):
  `itertools.product` of the reconstructed point bases with `BinaryCurve.add`
  recovers image 128 and mass 128, matching the recorded convolution. This
  draw is not the exhaustiveness-control draw (that one had domain 12288).

The run's own exhaustiveness control (two tuple orderings plus brute force at
the smallest cell) reports order-independence; that is the producer's check.
The identities above are this reviewer's.

Nothing was sampled. An unreached cell would have been recorded, not scored.
There is no such cell.

### The denominator: what `m!` is a ratio against

The statistic the gate scores is

```
ratio_over_predicted = |typed image| / |untyped image| / m!
```

where both images are **sets of group sums** in `E(F_{2^n})`. That is the
same target population. It is **not** the same domain population:

| family | domain counted | image |
| --- | --- | --- |
| typed | ordered product `∏_i F_i`, `F_i = {P : x(P) ∈ V+v_i}` (or `g_i V`) | `{P_1+⋯+P_m}` |
| untyped | unordered multisets of size `m` from a single `F = {P : x(P) ∈ V}` | `{P_1+⋯+P_m}` |

`m!` is the `2^k ≫ m²` limit of the **x-coordinate counting cap**

```
2^{mk} / C(2^k + m − 1, m) = m! / ∏_{j=0}^{m−1} (1 + j/2^k)
```

an identity in integers, re-derived here and verified at all seven cells.
At the declared cells that correction is **not** ~1:

| cell | `m!` | cap / `m!` | cap already `< m!/2`? | `mk−n` |
| --- | ---: | ---: | --- | ---: |
| n12_k2_m6 | 720 | 0.0677 | yes | 0 |
| n12_k3_m4 | 24 | 0.5172 | no | 0 |
| n12_k4_m3 | 6 | 0.8366 | no | 0 |
| n15_k3_m5 | 120 | 0.3448 | yes | 0 |
| n15_k4_m4 | 24 | 0.7045 | no | +1 |
| n17_k3_m6 | 720 | 0.2122 | yes | +1 |
| n17_k4_m4 | 24 | 0.7045 | no | −1 |

Zero of seven cells satisfy HEUR-YT's own second clause `mk ≤ n−3`. The first
clause (`ratio = m!` within 10%) was stated unconditionally and is scored as such.
The point-domain ratio `∏|F_i| / C(|F|+m−1,m)` is also not `m!`: median
domain-ratio/`m!` ranges from 0.020 (n12_k2_m6) to 1.26 (n12_k4_m3).

HEUR-YT as written in H-SEMBIN-c59e50 is a map on **x-tuples** of size
`2^{mk}` via `S_{m+1}`. The specification's observable, and GG 2014/806
section 4.2 as cited there, is **group sums of points**. The run measured the
spec's object. The two families share the group as image; they do not share a
domain whose size ratio is `m!` at these `(k,m)`.

That is a checked convention, not a silent swap of populations. It does **not**
reverse the frozen-prediction miss: even against the exact x-cap, cell-median
image/cap is 0.67, 1.39, 1.13, 2.00, 0.84, 0.38, 0.56 — not 1 within 10% at
every cell. Against the actual point-domain ratio, image/domain medians sit
near 1 (0.69–1.91): the images roughly track their domains. The miss of `m!` is
largely that the domains are not `m!` times apart, plus saturation of the
typed image against `|E|` while the untyped image stays small (`|F|` is 3–25,
not `2^k`).

Additive and multiplicative families miss `m!` similarly (median
ratio/`m!` 0.448 vs 0.422). The representation control does not isolate the
effect to one embedding.

### The summary: full per-cell distribution, not the median

Recomputed over the 1092 completed non-empty draws, matching the manifest to
the printed digits:

- overall median ratio/`m!` = **0.4315329547882895**
- min = **0.000696286472148541**
- max = **68.47083333333333**
- cells with every draw within 10% of `m!`: **0 / 7**
- cells with cell-median within 10% of `m!`: **1 / 7** (n12_k4_m3 at 0.9423)
- cells with a draw below `m!/2`: **7 / 7**

The headline "no cell within 10%" is true under the run's every-draw scoring
and false as a statement about cell medians: n12_k4_m3's median is inside 10%.
That cell still has 48/160 draws below `m!/2`. The gate
`prediction_met_at_every_cell = false` is the every-draw reading.

Per cell, completed draws, ratio/`m!`:

| cell | n | min | p25 | median | p75 | max | within 10% | `< m!/2` | empty |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| n12_k2_m6 | 134 | 0.00070 | 0.0094 | **0.0453** | 0.130 | 0.414 | 0/134 | 134 | 26 |
| n12_k3_m4 | 160 | 0.0211 | 0.403 | **0.721** | 1.269 | 4.002 | 18/160 | 55 | 0 |
| n12_k4_m3 | 160 | 0.108 | 0.444 | **0.942** | 1.515 | 3.775 | 18/160 | 48 | 0 |
| n15_k3_m5 | 159 | 0.0167 | 0.212 | **0.688** | 4.092 | **68.47** | 7/159 | 72 | 1 |
| n15_k4_m4 | 160 | 0.0655 | 0.429 | **0.591** | 1.395 | 2.152 | 14/160 | 55 | 0 |
| n17_k3_m6 | 159 | 0.0032 | 0.047 | **0.0811** | 0.141 | 13.94 | 0/159 | 129 | 1 |
| n17_k4_m4 | 160 | 0.0604 | 0.243 | **0.396** | 0.633 | 9.070 | 5/160 | 108 | 0 |

"A draw below half `m!` in every cell" is true, and at three cells
(n12_k2_m6, n15_k3_m5, n17_k3_m6) it is **automatic** from the counting-layer
cap already being below `m!/2`. At the other four it is not automatic; the
best cell still has 48 such draws.

The overall median 0.4315 is a mixture of two `m=6` cells sitting at 0.045
and 0.081 with 293 draws and five other cells between 0.40 and 0.94. It is
the right one-number summary of a skewed pooled list; it is a fragile
description of any single cell. The table is the result.

### The 68.47 draw is real, not degenerate

Maximum ratio/`m!` = 68.47083333333333 is

- cell n15 k=3 m=5, additive cosets, low-degree V, `B=1`,
  seed `20260913305`, draw 0
- status `completed` (not `empty_typed_base`)
- typed base sizes `[12, 10, 12, 12, 10]` — all nonempty
- typed domain 172800, typed image **32866** against `|E|=33044` (typed image
  saturates the group)
- untyped `|F|=3`, untyped domain `C(3+5−1,5)=21`, untyped image **4**
- 32866 / 4 = 8216.5, / 120 = 68.4708…

This is the opposite of an empty typed family: the **untyped** V happened to
carry three curve points, so the denominator is four group sums, while the
typed product saturates `E`. The contract's degenerate rule is empty typed
bases and collapsed types, neither of which fires. Excluding it would lower
the cell mean (9.91 vs median 0.688) and would not create a within-10% cell.
The spread of five orders of magnitude is this starved-untyped / saturated-typed
corner plus the `m=6` cells whose domain ratio is already ~0.02 of `m!`. Both
are real completed enumerations.

### Degenerate-draw exclusion is directional-neutral

28 draws have `status: empty_typed_base` and ratio exactly 0 (a typed coset
with no curve point). All 28 are **additive**; multiplicative translates always
contain `x=0`, and in characteristic 2 `y^2=B` has one root, so `gV` is
never an empty point-base. 26 of 28 sit in n12_k2_m6.

Including them lowers the pooled median from 0.4315 to 0.4178 and cannot
create a within-10% cell. The run's claim that the gate is unchanged in
direction if they are folded back in is correct. The exclusion does not remove
the draws "where typing works." `implementation.md` says 29 empty draws; the
rows contain 28. The 29th stdout anomaly is the recorded halt-and-continue
event, not an empty coset.

### Proves-too-much (this task's two known-false objects)

Not taken at face value.

- **GG symmetrised presentation.** Independently: at operating point
  `m = n/log2 n`, `value(n)/log2 n` stays bounded as `n` runs to `10^7` for
  `G ∈ {1, m^2}` and is unbounded for `G ∈ {2^m, 2^{m log2 m}, m!}`. All five
  families match their declared class. The argument collapses only for
  uniformly polynomial-in-`m` per-solve cost. `G=1` (Semaev's chain) **does**
  collapse — that is the reductio, not a control failure. Superpolynomial `G`
  does not. The producer replaced a single-`n` 10-bit slack that could not
  separate `2^m` from a polynomial at `n=283`; the growth discriminator is the
  stated reason and it is the reason that fires. Provenance of "GG's extra
  variables" is the hypothesis's structural_ingredients, not a fresh reading
  of ePrint 2014/806 in this task.
- **Trimoska search-side removal.** Independently: on the 4×4 grid
  `n ∈ {163,283,409,571}`, `l ∈ {1,2,5,10}`, the total `n+l` is strictly
  above `n/2` at every cell (16/16). Their exponent contains no `m`-growing
  term to delete. The argument fails for that reason, not for an incidental
  one.

### J4 verdict

The frozen prediction `image_size_ratio = m!` within 10% at every enumerated
cell is missed. The measurement is exhaustive. The degenerate-exclusion rule
is not selecting on the success of typing. The 68.47 draw is a completed
non-empty draw with a starved untyped base, not a draw that should have been
dropped under the contract's own empty-typed rule.

The denominator `m!` is the large-`V` limit of the x-multiset cap, not the
measured point-domain ratio, and none of the seven cells is inside
`mk ≤ n−3`. That is disclosed by the run's own layer-D1 identity and is
checked here. It qualifies what the negative result **means** (toy `|F|`,
saturation, finite-`k` cap); it does not make the scored miss of `m!` an
arithmetic error or a sampled cell.

Holding artifact: the per-cell table above, with exhaustiveness independently
confirmed and the denominator convention stated.

Package defects that do not reverse J4: `implementation.md` off-by-one on
empty draws (29 vs 28); `DRAWS_PER_CELL = 20` in the driver vs 160 draws per
`(n,k,m)` after crossing subspace × `B` × family (more draws, not fewer);
halt-and-continue recorded as a protocol deviation.

---

## J5 — the interior minimum

**Verdict: holds.**

Deciding artifacts: the independent derivation below, evaluated on the typed
stage-1 / total formulae from the specification's three GG substitutions,
cross-checked against the producer's numerical surface at `n=100` (argmin
`m=69`, depth 0.08605637067770999 bits) and `n=571` (argmin `m=396`, depth
0.08607112336403588 bits).

### Independent `dT/dm`

Under the un-ceiled reading `k = n/m` the yield exponent `n − mk` vanishes.
The typed formulae (GG's three substitutions, nothing else) are, in log2,

```
T1(m) = n/m + log2 m + 4 ω log2 n
T2(m) = ω' (n/m + log2 m)
```

Let `u(m) = n/m + log2 m` and `C = 4 ω log2 n` (independent of `m`). Then
`T1 = u + C` and `T2 = ω' u`. The true total is `log2(2^{T1} + 2^{T2})`, not
`T1+T2`. Because `T1` dominates `T2` by tens of bits at every tested `n`
(`ω=3` makes `C = 12 log2 n`), the total has the same `m`-shape as `u`.

```
du/dm = −n/m² + 1/(m ln 2)
```

Stationary iff `m = n ln 2`. The second derivative at that point is
`1/(n² (ln 2)³) > 0`, a minimum, interior for every `n > 2/ln 2`. Depth of `u`
below the `m=n` boundary:

```
u(n) − u(n ln 2) = 1 − 1/ln 2 − log2(ln 2) = 0.08607133205593431 bits
```

independent of `n`. The missed rising term is `log2 m`, entering from GG's
replacement of the relation store `2^k` by `m 2^k`.

This reproduces the producer's closed-form argmin and the **unit** depth they
put in the manifest. Their written `T(m) = (1+ω') u + C` is the **sum of the
two log-costs**, whose depth is `(1+ω') × 0.086 = 0.258` bits at `ω'=2`. That
is not the total the numerical surface minimises. The numerical total depth is
the unit depth, because stage 1 dominates. The 0.086 in the joint and in the
manifest is the operational number.

Independent numeric, `ω=3`, `ω'=2`, paper-raw, unceiled, total =
`log2(stage1+stage2)`:

| n | argmin | `n ln 2` rounded | depth vs `m=n` | 2^{depth} |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 69 | 69 | 0.086056 | 1.0615 |
| 571 | 396 | 396 | 0.086071 | 1.0615 |

Argmin and depth agree with the producer to the printed digits. Untyped at
`n=100` still has a deep interior min at `m=6` with depth ~500 bits: that is
the `log2(m!)` balance, and it is not this 0.086-bit wiggle.

### Optimum or flatness

**Flatness.** 0.086 bits is a 6.1% linear-cost difference between the
critical point and the `m=n` boundary. At `n=100` the objective falls from
130.7 bits at `m=2` to 87.28 at `m=69`, then rises 0.086 bits to 87.37 at
`m=100`. 76 of 99 feasible `m` lie within 1 bit of the boundary. The right
tail is operationally flat. There is a real interior critical point of `u(m)`
and it is not a useful optimum.

### Does this refute H-SEMBIN-c59e50's prediction or only its phrasing?

The frozen prediction is: typed objective monotone decreasing on `2 ≤ m ≤ n`
at every tested `n`, argmin at the boundary, **no interior optimum**.
Falsification: an interior minimum at any tested `n`, and the missed rising
term must be named.

- As **phrasing**, the prediction fails on the unceiled reading: `u(m)` is
  not monotone decreasing, the argmin is interior at `m = n ln 2`, and the
  missed term is `log2 m`. Recorded as failed against the sentence as
  written.
- As **research content** — that `log2(m!)` is the unique term that *sets the
  exponent*, and that deleting it dissolves the `sqrt(n ln n)` tradeoff —
  this 0.086-bit tail does not refute it. `log2 m` is `O(log n)`, not
  `Θ(sqrt(n ln n))`. The untyped interior min is hundreds of bits deep; the
  typed remainder is 6%. The optimisation that produced `c = 1.6986` has
  ceased to exist as an exponent-setting balance. What remains is a
  lower-order wiggle the hypothesis's "every cost term falls with `m`"
  sentence missed.

### The depth under another defensible normalisation

The breaking artifact names a depth that vanishes under a different but
equally defensible normalisation. Two candidates:

1. **Sum of logs vs log of sum.** Depth 0.258 vs 0.086. Neither vanishes.
2. **Ceiled `k = ceil(n/m)` with yield capped at 1** (eq. (15)'s `k`, and
   `1/P` not allowed above 1). Independently: at `n=571` the global argmin
   is at the **boundary** `m=n` and the depth below the boundary is 0. At
   `n=100` the global min is a two-point tie `{m=50, m=n}` (depth 0.0000);
   no `m` beats `m=n`. Ceil sawteeth exist and do not beat `m=n`. Under this
   pair the 0.086-bit interior min of `u` **does not appear as a
   global-vs-boundary gap**. Numbers in `scratch/j4_j5_out.json`
   `j5.ceiled_capped`.

   Ceiled **paper-raw** (negative yield exponent, `P>1`) produces a deep
   spurious interior min (70 bits at `n=100`, 99 bits at `n=571`). That is an
   artifact of an illegal probability, not a confirmation of `m = n ln 2`.

So: the closed form is correct for the unceiled model the Table 3 arithmetic
uses; 0.086 bits is real there and is flatness; under ceiled+capped the
hypothesis's "argmin at the boundary" actually holds at `n=571`. The
localisation is not refuted. The phrasing "monotone decreasing, no interior
optimum" is false on the unceiled reading by 0.086 bits.

J5 holds for the named closed form. It is not a useful optimum. It refutes
the prediction's wording, not the claim that `log2(m!)` is the
exponent-setting rising term.

---

## Run-package defects (in scope of these joints)

1. `implementation.md` reports 29 empty typed draws; `image-sizes.json` has
   28. The 29th stdout anomaly is the halt-and-continue record.
2. Driver constant `DRAWS_PER_CELL = 20` vs 160 enumerations per declared
   `(n,k,m)` after crossing subspace × `B` × family. More, not fewer; the
   spec's "all 20" is not the table that was scored.
3. Closed-form typed objective written as `(1+ω')u`, depth 0.258 bits; the
   numerical total they minimise has depth 0.086. The manifest stores the
   unit depth. Inconsistent labelling, same argmin.
4. Run recorded `git_dirty: true` (the experiment directory was untracked at
   launch). Snapshot `24f5a574a` then bound the bytes. Hashes match that
   snapshot.
5. Protocol deviation: stopping rule 1 fired and phases 1b–5 still ran.
   Recorded. Arm D's observation is complete without them. This review used
   those later phases only for J5 and for the proves-too-much objects J4 was
   assigned.
6. Mean at n15_k3_m5 is 9.91 against median 0.688, driven by the 68.47 draw.
   Any reader of a mean here is reading the starved-untyped corner.

No degree was measured. Stderr is empty (sha256 of the empty file). Command
matches `command.txt`. Seeds match the contract. This report asserts nothing
about any curve's security.

## What this report does not do

It does not move H-SEMBIN-c59e50. It does not write an evidence record. It
does not settle transfer to Nagao ePrint 2015/984 §7 (the plan forbids
pre-empting that; a pointer only: Arm D measured H-SEMBIN-c59e50's
coset-typed family, not EQS3/EQS4). It does not compose J1–J3 or J6-BLIND.

```yaml
review_attestation:
  task_id: TASK-20260913-7ca970
  joints_owned:
    - "J4 -- ARM D, THE GATING NEGATIVE RESULT"
    - "J5 -- THE INTERIOR MINIMUM"
  sources_read: see coordination/review/sembin-20260913-run2/TASK-20260913-7ca970/attestation.yaml
  read_sibling_reports: false
  blind_from_respected: null
  verdicts:
    J4: holds
    J5: holds
  verdict: holds
```
