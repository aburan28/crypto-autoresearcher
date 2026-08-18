# red_team_report.md -- TASK-20260817-785c5c

Red Team review of **TASK-20260817-b4b6e4** at snapshot **48d384e0e**
(BATCH-dd0901 / GOAL-HQC-001 / EXP-HQC-982268).

**Independent session. I am not the producer. I committed nothing, changed no
record status, edited no producer artifact, applied no branch of the frozen
reading rule and named no branch.** Claim tier stays **TOY**. H-HQC-18d1b4 stays
**PROPOSED**. Nothing below bears on HQC's IND-CCA security, its
decoding-failure rate, assumption A17 or A5, or any standardized parameter set.

**This batch was built to my own lineage's specification and I was harder on it
for that reason.** TASK-20260817-b4b6e4 executes, verbatim, the
`next_concrete_action` and the first two `required_controls` of
TASK-20260817-94c89e. An agent lineage grading its own prescription is the
failure mode. My finding is that the prescription was executed faithfully and
exactly, that **the executor's conduct is the cleanest in this campaign to
date**, and that **the prescription was again partly wrong** -- the coupled null
I asked for is the right family with a parameter that was never measured when
the measurement was free and already committed, and the low-k recompute I asked
for answers a question about *magnitude* that I framed as a question about
*significance*.

---

## 0. VERDICT

**`objections_material_to_conclusions` -- every number is SOUND and
independently reproduced; the load-bearing INFERENCES are not.**

**SOUND.** I contest no reported number. I re-derived all four fresh cells,
both withheld historical cells, both available historical cells, the three
contrasts, both 4-point ladders at every k, the same-T noise handle at every k
and all four gate residuals from the committed arrays; every one reproduces.
I re-implemented Part B independently from its committed seed specification
through the same three sha256-pinned modules and reproduced **all 15** reported
SDs and band widths to the printed precision. Notarization verifies in both
directions (12/12 declared hashes, 0 undeclared files). The zero-decoder-call
gate is real and enforced. `dominated_by` is recorded verbatim where required.

**MEANING -- seven objections, three of them material to what this batch can
support.**

1. **The collapse is a collapse of UNITS, not of significance, and the batch's
   own band-free yardstick says so.** Normalised by `D_RMS(k)` -- the campaign's
   designated primary real-object yardstick, at the same order `k` --
   `dev_fresh/D_RMS` is **1.499 (k=2), 1.581 (k=5), 0.709 (k=10), 0.776 (k=17)**
   and `dev_hist(all four)/D_RMS` is **1.471 / 2.207 / 0.807 / 0.737**. The
   deviation from 0.5 is *largest relative to the instrument's own noise at low
   k*. Both the deviation and the noise collapse together (19x and 37x from
   k=17 to k=2) because `k` sets the scale of every log-ratio of `se_paired`,
   signal and noise alike (SS-RT2).
2. **The reconstruction gate could not have passed where there was something to
   reconstruct and could not have failed where there was not** (SS-RT3). Its
   information content is near zero on both halves, and its only operative
   effect was to delete the regime-P half of the historical set -- which is
   what makes the batch's own frozen route need a decision the rule does not
   supply.
3. **The coupled null is the SIXTH instance of the control-blindness pattern,
   and I can name the parameter, measure it on committed data, and fix it in one
   line** (SS-RT5). The real pair disagrees on the last block on **0.1094**
   (shard 5000) and **0.1038** (shard 6000) of trials -- I measured this from
   `a79e4f`'s `stage_1.per_trial_S`, the only per-trial `S` arrays this campaign
   ever persisted, in the same file the task already opened. The null's rate is
   `2p(1-p) = 0.434647`, the **maximum** compatible with the marginal:
   a **3.97x-4.19x** over-statement of the paired-difference variance. Repaired,
   the SHAPE statistic moves from 5.14 / 4.30 / 2.83 to **10.25 / 9.04 / 9.25**
   -- inside the real cells' range at **all three** k.

**Not a closure, and I decline to make one.** Nothing here says this lane is
dead. The obstruction is named, measured, localised and repairable at zero
decoder cost. **Symmetrically, this batch UNDER-claims three times** (SS-RT9),
including a usable V1 sizing law that its own committed numbers deliver.

---

## SS-RT0. Notarization chain, re-verified by me in both directions

| check | result |
| --- | --- |
| `git cat-file -t 48d384e0e` | `commit` |
| `git rev-parse 48d384e0e^` | `4bde2277a14a7007fbd322765155d997f59c9207` = the declared `parent_sha`, and = "coord: open GOAL-HQC-001 BATCH-dd0901" |
| `git merge-base --is-ancestor 48d384e0e HEAD` | true (branch `claude/hqc-001-lowk-20260817`) |
| `git diff-tree -r 48d384e0e` | exactly **13** additions: the receipt + 12 producer artifacts. Nothing else. |
| `git diff-tree -r 4bde2277a` | batch.yaml, dispatch_queue.json, 5 task cards, 5 handoffs -- **the frozen reading rule, the 0.25 floor, the factor 2, the reconstruction mapping and the two blindness tests are all in the PARENT commit, before any producer artifact existed.** The freeze claim is verifiable and I verified it. |
| sha256 of all 12 declared paths vs `git show 48d384e0e:<path>` | **12/12 match** `path_sha256` |
| reverse direction: files added but not declared | **0** (excluding the receipt itself) |
| declared paths vs working tree | **0 differ** |
| receipt's own `commit_sha` | `null` in its own blob, filled to `48d384e0e...` by the following bookkeeping commit `bb00afebb`, disclosed in `commit_sha_note` as the two-commit fixed-point form |

**PASS, both directions. No fabrication, no drift, no undeclared file.** One
cosmetic inconsistency: `declared_path_count: 13` counts the receipt while
`path_sha256` carries 12 entries. Not a defect; worth one word at the archive.

**Contract path.** The committed task card, the committed handoff, the committed
`dispatch_queue.json` and `batch.yaml`'s
`review_write_scope_layout_is_declared_once_and_governs` all name
`.../reviews/TASK-20260817-785c5c/` with two artifacts. **This batch's dispatch
orientation named the same path**, so unlike TASK-20260817-94c89e there is no
discrepancy to flag. I wrote exactly the two declared paths and nothing else
anywhere in the repository.

---

## SS-RT1. THE PRODUCER'S CONDUCT, STATED FIRST BECAUSE IT IS UNUSUAL

I looked for the things that have gone wrong in this campaign five times and
did not find them here.

- **The gate was applied as specified against its own author's mapping and was
  allowed to fail.** `historical_cell_reconstruction.json` records
  `mapping_was_adjusted_or_searched: false`, the two failing cells' low-k values
  are `null` in `low_k_recompute_results.json`, and the cells were neither
  dropped nor re-paired. I searched for evidence of an alternative pairing having
  been tried and found none in the code, the results or the logs.
- **The comparator-precision fact was disclosed BEFORE the gate ran**, in
  `design.md` section 2.5 lines 145-159, in terms that concede the gate can only
  pass "if the underlying full-precision value happens to be exactly that
  decimal", and the subordinate diagnostic is explicitly walled off from
  `gate_pass`. I verified the disclosure is in the committed design.md whose
  sha256 both drivers measured at launch.
- **`protocol_deviations: []` is true.** Every constant, window pair, mapping,
  tolerance, contrast definition and blindness test executed is the one
  design.md froze.
- **Zero decoder calls is enforced, not asserted.** Part A imports no pinned
  module at all; Part B installs tripwires that raise rather than delegate,
  asserts both counters are 0 at exit and **re-measures all three module sha256
  values on disk at exit**. I re-verified all three pins myself, before and
  after my own probe.
- **The four SD-ratio discrepancies were reported rather than smoothed**, and
  the executor explicitly offers no explanation, which is the correct role
  boundary. I supply the explanation in SS-RT6 -- and it is that the analytic
  reference is wrong, not the simulation.

**Nothing in this report is an objection to the executor.** Every material
objection below lands on the *specification* it was given, or on what the
numbers are taken to mean.

---

## SS-RT2. DOES THE k-EXPLANATION SURVIVE ON THE HISTORICAL CELLS? -- STATED PLAINLY

**Plainly: it survives as a statement about MAGNITUDE and it does not survive as
a statement about RESOLVABILITY, and the campaign has been reading it as the
second.** And it survives on only two of the four historical cells by the
batch's own gate; I recomputed the other two myself (SS-RT4).

### SS-RT2.1 The absolute numbers -- reproduced, uncontested

All eight cells, recomputed by me from the committed arrays:

| k | F 5000 P | F 5000 N | F 8002 P | F 8002 N | H 5000 P* | H 6000 P* | H 8001 N | H 8002 N |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0.580733 | 0.506553 | 0.628397 | 0.511866 | 0.574626 | 0.491597 | 0.374003 | 0.515715 |
| 5 | 0.697364 | 0.455398 | 0.606080 | 0.492779 | 0.699384 | 0.634578 | 0.224446 | 0.410684 |
| 10 | 1.051457 | 1.136112 | 0.575713 | 0.812011 | 1.224571 | 0.899893 | 0.071112 | 0.120915 |
| 17 | 2.048813 | 2.960737 | 0.323623 | 1.594336 | 2.836098 | 1.401921 | -0.268250 | -0.866236 |

(*) the two gate-failed cells, recomputed by me under the mapping's assumption;
see SS-RT4 for what that is and is not worth. Every value that the producer
reports, I reproduce.

**Yes: on all four historical cells the absolute deviation from 0.5 shrinks
monotonically as k falls, exactly as on the fresh four.** That is a real,
reproduced, non-trivial fact and I do not contest it.

### SS-RT2.2 The same measurement, in the batch's own units -- and it inverts

`batch.yaml` designates `D_RMS(k)` as **"THE PRIMARY YARDSTICK OF ITS READING
RULE"** and as band-free, real-object and distribution-free. Divide by it:

```
  k   D_RMS(k)   dev_fresh  dev_f/D    dev_hist(4)  dev_h/D   |regimeME|/D
  2   0.085654    0.128397    1.499       0.125997    1.471       1.113
  3   0.086045    0.132186    1.536       0.180327    2.096       1.609
  4   0.095088    0.148671    1.564       0.230249    2.421       1.766
  5   0.124859    0.197364    1.581       0.275554    2.207       1.423
  7   0.295823    0.311751    1.054       0.358465    1.212       0.396
 10   0.897713    0.636112    0.709       0.724571    0.807       0.179
 13   1.800719    1.419243    0.788       1.285514    0.714       0.300
 17   3.169955    2.460737    0.776       2.336098    0.737       0.344
 26   6.591013    3.522016    0.534       6.402386    0.971       0.273
```

**In the campaign's own band-free real-object units the phenomenology does not
collapse at low k. It is at its most prominent at low k**, peaking around k=4-5
for both the fresh set (1.58x) and the historical set (2.42x), and falling below
one noise scale only for k >= 8. The regime main effect behaves the same way:
1.77 noise scales at k=4, 0.34 at k=17.

### SS-RT2.3 The mechanism I think is operating, and whether it is the campaign's

**It is not the mechanism the campaign has been assuming.** The campaign's
working story (EV-HQC-e458ef O6; `batch.yaml` objective) is: *at low k the
estimator's own bias is nearly zero (-7e-5 at k=2), so the cells return their
analytically forced 0.5 and the five-batch phenomenology is a high-k artifact.*

The mechanism I think is operating is: **`k` controls the SCALE of every
log-ratio of `se_paired`, and alpha is nothing but a log-ratio of `se_paired`.**
`log2_A_from_hists` (`measure.py:225-246`) forms `sum_s C(s,k) H_s`. At k=17
against mean S = 17.88 the sum is carried by a thin right tail, so the effective
sample size for the estimand is a small fraction of T, the relative sampling
error of `se_paired` explodes, and *every* log-ratio of two `se_paired` values
inflates -- the ones that encode a real T-dependence and the ones that encode
nothing at all. At k=5 the functional is not tail-carried, the relative error
contracts, and every log-ratio contracts with it. The two collapses are the same
object: from k=17 to k=2 the noise handle falls **37.0x** and the fresh
deviation falls **19.2x**. The noise collapses *faster than the signal*.

**The estimator-bias story is not wrong, it is insufficient.** It explains why
alpha stops being enormous. It does not license "the cells sit at 0.5", because
the yardstick that would decide that shrank at least as fast.

**Applying `docs/inventor-protocol.md` section 3 to the campaign's own newest
claim, as it was applied to the old one:** name the parameter that should
destroy the signal, and say what the measurement should do. Here the parameter
is k and the *correct* prediction of the k-explanation is that the
noise-normalised deviation should decay toward zero as k falls. **Measured, it
stays flat and then rises.** A quantity that fails to decay when it should is
the artifact tell -- and here it fires on the refutation side.

**The narrowest valid conclusion I will defend:** on these eight cells, at every
k in 2..26, the 2-point local exponent is separated from 0.5 by of order one
same-T noise scale, and no cell is readable directionally at any k. The scoped
retirement TASK-20260817-94c89e recommended for k=17 is **not repaired by moving
to k=5**; it applies at k=5 too. What k=5 buys is a *bounded* instrument, not a
*resolving* one.

**Honest limit on my own headline:** `D_RMS(k)` is an **n = 2** scale (one
same-T contrast per shard) measured on the FRESH windows only. Applying it to
the historical cells assumes transfer across procedures. Falsifier named in
SS-RT10.

---

## SS-RT3. THE RECONSTRUCTION GATE -- IT COULD NOT HAVE FIRED, IN EITHER DIRECTION

This is the batch's load-bearing step and it carries almost no information.

### SS-RT3.1 The two PASSes verify a transcription, not a reconstruction

`e61cca`'s own committed JSON contains, for each of 8001 and 8002, a block
`single_shard_only_local_exponent` recording `T_committed: 10000`,
`se_paired_committed_k17: 0.024506333220408173`, `T_new: 20000`,
`se_paired_new_k17: 0.029514095961871902`, the **method string** ("alpha =
-[log(SE_20000) - log(SE_10000)] / [log(20000) - log(10000)]") and the
**answer** `local_exponent_alpha: -0.2682495157085447`. The gate reads the same
two numbers from the same two files and re-executes the same formula. Agreement
at 8.3e-16 and 1.9e-15 is what float64 does when you evaluate one expression
twice. **For these two cells there was never a reconstruction hypothesis: the
source file states the pairing.** The check is worth exactly its transcription
content -- that `a79e4f`'s stage-2 array is byte-for-byte the value `e61cca`
labelled "committed" -- which is real but small.

This is the same class of defect as EV-HQC-e458ef O11's algebraic tautology,
one level up: not an identity that holds for any input, but a recomputation
whose inputs the source already recorded.

### SS-RT3.2 The two FAILs were unpassable before any datum existed

`+2.836` and `+1.402` do not exist in this repository at more than four
significant figures. I traced their origin:
`coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/reviews/TASK-20260814-a49f1c/red_team_report.md`
**line 129** -- a Red Team review table -- from which EV-HQC-469c08 O6 took
them. **A 1e-12 absolute gate against a 4-significant-figure decimal passes only
on a measure-zero coincidence**, for the true mapping as surely as for a false
one. `batch.yaml` specified that gate while printing, in the same paragraph, two
comparators at 4 digits and two at 16 (`the_four_historical_cells_...:
what_they_are`). The mismatch is on the face of the document that froze it.

**So the gate's outcome was determined before the data existed: PASS where the
answer was already written down, FAIL where it was not.** That is this
campaign's **sixth control that could not fire** -- and the first whose
non-firing *removed data* rather than merely failing to detect. Its only
operative effect was to delete the regime-P half of the historical set.

**This is the Coordinator's defect, not the executor's.** The executor disclosed
it in advance and applied the gate exactly as written, which is the correct
behaviour under a bad specification.

### SS-RT3.3 COULD A DIFFERENT PAIRING ALSO PASS? -- I searched exhaustively

I enumerated **all 19** committed per-k `se_paired` arrays in the three named
source files plus the eight fresh windows, formed **all 114** ordered pairs with
`T_lo < T_hi`, and computed `alpha_17` for each.

| target | matches within 1e-12 | matches within 5e-4 (half-ulp of 4 s.f.) |
| --- | ---: | ---: |
| (5000, P) = 2.836 | **0** | **1** (the intended pairing) |
| (6000, P) = 1.402 | **0** | **2** |
| (8001, N) = -0.2682495157085447 | **1** | 1 |
| (8002, N) = -0.8662355237627483 | **1** | 1 |

**Answer to the question the gate cannot answer, in two parts.**

- **At 1e-12 the mapping is unique.** No other pairing among 114 reproduces any
  committed value. So *if* a 16-digit comparator existed for the P cells, the
  gate would be a genuinely discriminating test. It does not exist.
- **At the precision the P comparators actually carry, uniqueness fails for
  (6000, P).** Besides the intended `a79e4f/stage1/shard_6000 -> 8bbdd2/shard_6000`
  (alpha 1.4019206406015738, residual 7.94e-05) there is
  `a79e4f/stage1/shard_5000 -> a79e4f/stage2/POOLED` (alpha 1.4023391930803442,
  residual **3.39e-04**), also inside half an ulp. That competing pairing is
  semantically absurd -- wrong shard, pooled instead of per-shard, `n_batches`
  400 instead of 200, `T_hi` 20000 instead of 10000 -- **and that is exactly the
  point: what identifies the mapping at 4 s.f. is semantics the gate does not
  evaluate, not the residual the gate does evaluate.**

**So "precision artifact" is the ONLY available reading for (5000, P) and is NOT
the only reading for (6000, P) on residual alone.** `batch.yaml`'s claim that
the gate "proves the array selection is the right one" is true at 16 digits and
false at 4. The honest label for the two FAILs is *mapping corroborated to the
full precision the record supports, and to nothing beyond it*.

### SS-RT3.4 Are the paired arrays like-for-like? -- CHECKED, and they are

I verified each pairing's metadata directly rather than accepting the
producer's summary:

| cell | T_lo / T_hi | n_batches lo / hi | jack batch size | pooling | k range | T-points disjoint? |
| --- | --- | --- | --- | --- | --- | --- |
| 5000 P | 5000 / 10000 | 200 / 200 | 25 -> 50 | per-shard / per-shard | 2..26 / 2..26 | **yes** -- 8bbdd2 `n_discard_prefix: 5000`, `retained_slice [5000:15000)` |
| 6000 P | 5000 / 10000 | 200 / 200 | 25 -> 50 | per-shard / per-shard | 2..26 / 2..26 | **yes**, same |
| 8001 N | 10000 / 20000 | 200 / 200 | 50 -> 100 | per-shard / per-shard | 2..26 / 2..26 | **yes** -- e61cca `n_discard_prefix: 10000`, `retained_slice [10000:30000)` |
| 8002 N | 10000 / 20000 | 200 / 200 | 50 -> 100 | per-shard / per-shard | 2..26 / 2..26 | **yes**, same |

`a79e4f`'s `stage_2.stage2_sizing_applied` confirms `T2_shard_8001 = 10000` and
`T2_shard_8002 = 10000`, so the regime-N `T_lo` label is right. All eight fresh
windows also carry `n_batches` 200. **The regime labels are correct: P really is
the 25->50 batch-size step and N really is 50->100, on every cell.**

**Reported as checked-and-clear, with one caveat and one historical hazard.**
Caveat: the two T-points of each historical cell come from different tasks,
processes, machines, OSes, Python and numpy versions (declared, limitation 1).
Hazard, not this batch's: the campaign's older `se_vs_trial_count_fit` ladders
mixed conventions -- `a79e4f/stage_2.se_vs_trial_count_fit` uses a "T = 10000"
point (0.09678123828590589) that is the **2-shard POOLED** statistic at
`n_batches` 400, i.e. 2 x 5000 trials, alongside per-shard points. **This batch
does not repeat that error**: every array it pairs is per-shard at `n_batches`
200. Worth recording so it is not reintroduced.

---

## SS-RT4. IS THE FROZEN ROUTE DECIDABLE? AND IS A TWO-CELL ANSWER BEING SMUGGLED IN?

**The route as frozen needs four historical cells and has two, both regime N,
both from the 8001/8002 family. The regime-P half is gone.** I do not decide the
route; I report what deciding it would require that the batch does not supply.

### SS-RT4.1 The rule does not define its own predicate on a partial set

`dev_set_k` is defined as "**max over the four cells** of the set". The
exhaustiveness argument asserts the predicates "CANNOT BE UNDEFINED" because "a
max of four finite reals always exists; the only way to lose it is a non-finite
or missing value, **which Branch I pre-empts by name**". But Branch I pre-empts
**per cell** and explicitly refuses to void the batch. Pre-empting two of four
cells does not give `dev_set(historical)` a value; it removes its domain. **The
second coordinate of the 2x2 selector therefore has no defined value, and the
rule assigns the choice -- evaluate over the surviving subset, or treat the set
as pre-empted -- to nobody.** That choice is exactly the kind of post-hoc
latitude pre-registration exists to remove.

### SS-RT4.2 The route is decidable here only by an accident nothing in the batch can see

I recomputed the two withheld cells (SS-RT2.1). At k=5 the historical maximum
deviation is attained on an **available** cell (8001, N: |0.224446 - 0.5| =
0.275554), so:

- `dev_hist(5)` over the two surviving cells = **0.275554**
- `dev_hist(5)` over all four = **0.275554** -- *identical*

**So on this outcome the partial set gives the same answer as the whole set, and
the route is decidable.** But that is luck, and **the batch cannot know it**,
because the gate forbade the producer from computing the two withheld values and
no artifact in the batch contains them. Had the maximum fallen on a withheld
cell, the same procedure would have produced a confidently wrong number.

At k=17 the accident does **not** hold: `dev_hist(17)` is **1.366236** over the
surviving two and **2.336098** over all four. `batch.yaml` pre-computed the
factor-2 threshold as `dev_hist(17)/2 = 1.168` **using the gate-failed cell
(5000, P) = 2.836**. On the surviving subset that threshold is **0.683**. Both
still exceed 0.275554, so the outcome again does not turn on it -- again by
luck. **The rule's own stated binding values were invalidated by its own gate,
and the rule contains no instruction to recompute them.**

Note the internal inconsistency this exposes: predicate (ii) compares a k=5
value **recomputed from arrays** against a k=17 value **taken from the published
record**, and for two cells the batch just declared that those two sources are
not verified to agree.

### SS-RT4.3 The CONTRAST CLAUSE quantifies over quantities that do not exist

Its primary form requires "every one of the three fresh contrasts at k=5,
**every historical analogue contrast at k=5**, and **both replication deltas at
k=5**".

- **There are no historical analogue contrasts.** In the historical set regime
  is 100% collinear with shard (5000/6000 are P-only, 8001/8002 are N-only) --
  that collinearity is the confound this entire campaign exists to break. The
  historical set has no factorial structure and therefore no main effects or
  interaction to compare. The clause's referent does not exist even with all
  four cells present.
- **One of the two replication deltas needs a gate-failed cell** ((5000, P)), so
  it is unavailable, while Branch I forbids reading any branch from that cell.

Both the primary form and the BLIND fallback range over the same list, so
**dropping the band does not restore evaluability here** -- the clause is
inevaluable in *both* of its forms, for a reason that has nothing to do with the
control.

### SS-RT4.4 Is a partial answer being smuggled in as the whole?

**Not by the producer.** `low_k_report.md` section 3.1 marks both cells "(gate
FAIL)", states in the same breath that "the four-cell historical set the frozen
route contemplates is **not complete at any k in this run**", and limitation 2
says any historical-set statement "rests on two cells, both regime N, both from
the 8001/8002 shard family". I looked for a place where a two-cell quantity is
labelled as the historical set and found none. The `run_manifest` and
`historical_cell_reconstruction.json` agree.

**The risk is entirely at the ledger archive, and the rule provides no barrier
against it.** A `dev_set(historical)` computed on two regime-N cells is not the
quantity the frozen route names, and the record must say which set every
historical number is over.

---

## SS-RT5. THE COUPLED NULL -- SIXTH INSTANCE, YES; RIGHT FAMILY, UNMEASURED PARAMETER

### SS-RT5.1 The dependence structure, measured on the real object

`a79e4f`'s `stage_1.per_trial_S` carries the **only per-trial S arrays this
campaign ever persisted**: 5000 trials per arm for shards 5000 and 6000, defected
and undefected. The task read that file for its regime-P `T_lo` arrays. One
`np.count_nonzero` on it gives:

| object | P(arms differ) | Var(arm0 - arm1) | difference law |
| --- | ---: | ---: | --- |
| real pair, shard 5000 | **0.1094** | 0.109393 | -1: 267, 0: 4453, +1: 280 |
| real pair, shard 6000 | **0.1038** | 0.103795 | -1: 265, 0: 4481, +1: 254 |
| this batch's coupled null | **0.434647** (realized 0.434770) | 0.434647 | symmetric +-1 |

**The null over-states the paired-difference variance by 3.97x (shard 5000) and
4.19x (shard 6000).** `2p(1-p)` is not "a" disagreement rate; it is the
**maximum** rate achievable by any coupling that preserves both marginals. The
construction did not choose a plausible coupling -- it chose the extreme one,
and it did so while the correct value sat in a file the task had open.

A second, smaller mis-specification: p was frozen by matching **E[S]** only. The
real undefected arm's variance is **11.022759** against `Binomial(56, p)`'s
**12.170123** -- the real object is **9.4% under-dispersed**, so the real block
indicators are not independent Bernoulli. "Marginal law identical, EXACTLY" is a
statement about the null's internal consistency, not about matching the real arm.

### SS-RT5.2 Right shape, or a different wrong one? -- RIGHT FAMILY, WRONG PARAMETER

**Right family.** Shared base plus an independent per-arm perturbation on the one
block the V3 defect can touch is structurally the correct model of the real pair
(the `F[:, 0:n_e-1]` gate proves 55 of 56 blocks are shared), and the direction
of the correction from BATCH-91929e's independent arms was right.

**Wrong parameter, and the error is measurable end-to-end.** I ran, in my own
process with my own tripwires and the same three pinned modules, both the
producer's construction and a **re-coupled** one: `base ~ Binomial(55, p)`,
`b0 ~ Bernoulli(p)`, and `b1 = b0` except on an independent fraction
`c = r/(2p(1-p)) = 0.251698` of trials where `b1` is redrawn `Bernoulli(p)`.
Each arm's marginal stays `Binomial(56, p)` **exactly**, the true paired
difference stays identically 0, and `P(arm0 != arm1) = 0.1094` as measured
(realized 0.109481). R = 200, rungs {5000, 10000, 20000}, zero decoder calls.

**SHAPE statistic, median `se_unpaired / se_paired`:**

| k | eight real cells' range | committed coupled null | **re-coupled (this report)** | |
| ---: | --- | ---: | ---: | --- |
| 5 | [8.545049, 11.126178] | 5.143413 (FAIL) | **10.251924** | **INSIDE** |
| 10 | [4.937997, 11.905557] | 4.301179 (FAIL) | **9.036247** | **INSIDE** |
| 17 | [2.338019, 28.691278] | 2.826520 (PASS) | **9.252385** | **INSIDE** |

**The SHAPE failure at k=5 and k=10 -- the failure that puts the batch on its
BLIND path at the adjudication order -- is caused by one un-calibrated
parameter, and it is repaired by measuring that parameter on data the campaign
already owns.**

### SS-RT5.3 Fatal or scoped? Scoped -- but the correction runs the other way from last time

| k | contrast | committed width | re-coupled width | factor |
| ---: | --- | ---: | ---: | ---: |
| 5 | single cell alpha | 0.4368 | 0.6089 | **1.394x** |
| 5 | regime main effect | 0.4119 | 0.5224 | 1.268x |
| 5 | interaction | 0.8102 | 1.1270 | 1.391x |
| 10 | single cell alpha | 1.2563 | 1.9031 | **1.515x** |
| 10 | regime main effect | 0.9886 | 1.6647 | **1.684x** |
| 17 | single cell alpha | 3.9260 | 5.5921 | 1.424x |
| 17 | interaction | 8.3640 | 13.3347 | **1.594x** |

**Every band in this batch is 1.26x-1.68x too narrow.** Mechanism, stated so it
is checkable: stronger coupling means a smaller paired difference, which means
the paired statistic is carried by the ~11% of trials where the arms actually
differ, which means a smaller effective sample size for `se_paired`, which means
a noisier `se_paired`, which means a **wider** alpha band. More realism makes the
diagnostic look worse -- the third time in this campaign that fixing a control
has widened it, and the largest correction yet (BATCH-91929e's was +22%).

**And the first calibration success this campaign has had.** My re-coupled
null's single-alpha SD at k=5 is **0.156911**, against the real object's
band-free same-T noise scale `D_RMS(5) = 0.124859` -- agreement within the n=2
sampling error of the latter. At k=10 and k=17 the real object is **1.9x and
2.2x noisier** than even the correctly coupled null (0.475868 vs 0.897713;
1.440739 vs 3.169955). So the corrected null is roughly right at k=5 and
conservative above it, and the residual gap at high k is the next thing to
explain.

### SS-RT5.4 Is this the SIXTH instance of the control-blindness pattern? -- YES, and it is also the best-behaved one

**Yes.** By the batch's own pre-registered test the control is SHAPE-blind at
k=5 and k=10 -- the order at which the rule adjudicates -- and POWER-blind for
the interaction at k=17. That is the sixth, after CTRL-BS, CTRL-POSHOM,
CTRL-IDXMAP, BATCH-4b8ad3's planted arm and BATCH-91929e's null object, and the
`blind_fallback` clause requires it be named as such.

**Two things make it different and both should be recorded.** (i) It is the
first instance the campaign **detected in advance with a pre-registered
mechanical test**, rather than a reviewer discovering it afterwards. That is a
real methodological gain and the SHAPE test deserves the credit. (ii) It is the
first whose cause is a **single measurable scalar** with the measurement already
committed -- so it is the first that is repairable rather than merely nameable.
A sixth blindness that arrives with its own diagnosis and its own one-line fix
is not the same event as the five that did not.

### SS-RT5.5 Would a defect survive this null undetected at k=5? -- YES, and the batch's own artifact says which

- **`evaluable_k` gating: entirely undetected, again.** `coupled_null_control_results.json`
  reports `evaluable_k_identical_across_all_draws: true`, 2..26, across all 4,000
  draws. The gate is never exercised near `stage_a.py`'s `T_STAB_THRESHOLD = 30`
  boundary, so any defect in it is invisible by construction. This is unchanged
  from BATCH-91929e, where I flagged it.
- **The jackknife NaN/row-count mismatch: never exercised, again.**
  `matched_pair.py:269-272` divides `nanmean`/`nansum` results by the row count
  rather than the non-NaN count, so a NaN leave-one-out row would silently
  **deflate** `se_paired` -- and a deflated `se_lo` or `se_hi` maps 1:1 into
  alpha. Not triggered anywhere here (every `se_paired` is finite and positive,
  `evaluable_k` is full at every draw), but not tested either.
- **`log2_A_from_hists` at k=5 specifically: the null is blind to exactly the
  defect class that matters.** At k=5 the functional is not tail-carried, so a
  bug in the tail handling is *maximally invisible at k=5 and maximally active
  at k=17*. **A clean coupled null at k=5 therefore certifies nothing about the
  k=17 numbers on which five batches of directional readings rest**, and the
  batch's k=17 leg -- correctly added as a comparison point -- is the only place
  the null touches that regime, and there it is the one k where SHAPE passes for
  the *wrong* reason (the real range [2.338, 28.691] is 12x wide, so almost
  anything falls inside it).

---

## SS-RT6. THE FOUR SD-RATIO DISCREPANCIES ARE NOT FINDINGS -- THE ANALYTIC REFERENCE IS WRONG

The producer reports four discrepancies above 10% "AS FINDINGS AND NOT
SMOOTHED" and offers no explanation, which is the correct role boundary. I
bootstrapped them (4,000 paired resamples of the 200 replicate indices, from the
committed `coupled_null_replicate_summary.csv`):

| k | contrast | measured | analytic | rel. | bootstrap 95% | analytic inside? |
| ---: | --- | ---: | ---: | ---: | --- | --- |
| 10 | regime main effect | 0.8419 | 1.000 | 15.81% | [0.7412, 0.9593] | **no** |
| 10 | shard main effect | 0.8646 | 1.000 | 13.54% | [0.7687, 0.9711] | **no** |
| 10 | replication delta | 1.5717 | 1.414 | 11.16% | [1.3813, 1.7964] | **yes** |
| 17 | regime main effect | 0.8933 | 1.000 | 10.67% | [0.7926, 1.0134] | **yes** |

**Two of the four are Monte-Carlo error at R = 200** on a heavy-tailed statistic
and should not be recorded as findings.

**The other two are explained by an unstated assumption in the analytic
reference, not by any defect in the simulation.** The factors 1.000 / 1.000 /
2.000 / 1.414 require the four cells to be **identically distributed**. They are
not: `coupled_null_control.py:532-535` assigns the P cells to rung pair
5000->10000 and the N cells to 10000->20000, and the artifact itself labels every
mixed contrast `rung_pair: "mixed"`. Measured per-cell SDs from the committed
CSV:

| k | 5000_P | 5000_N | 8002_P | 8002_N | repl. partner |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0.115794 | 0.106132 | 0.113583 | 0.106032 | 0.119758 |
| 10 | 0.307191 | 0.271345 | 0.280048 | 0.246106 | 0.368172 |
| 17 | 1.017414 | 0.977663 | 0.930820 | 0.937435 | 1.212071 |

Substituting these into the same algebra gives main-effect factors 0.9540 /
0.9018 / 0.9499 and interaction factors 1.9081 / 1.8037 / 1.8998 at k = 5 / 10 /
17 -- each inside the corresponding bootstrap interval. **Every discrepancy
disappears against the correct reference.** The self-check is sound as
arithmetic and wrong as a diagnostic: it tested the wrong analytic value.

Objection about *labelling*, not soundness: recording a mis-specified reference
as a finding is its own kind of noise, and the fix is one line -- state the
factors in terms of the realised per-cell variances.

---

## SS-RT7. THE READING RULE -- BAND-FREE, YES; DATA-FREE, NO; AND ONE CONSTANT DECIDES EVERYTHING

I evaluate no predicate, name no branch and adjudicate nothing. What follows
attacks the rule's structure, which the task card directs.

### SS-RT7.1 Does the band-free clause stand on its own? YES -- credit where due

I checked whether anything downstream still needs Part B's band under BLIND, and
**nothing does**. Clause (b) needs only `D_RMS(5)` (committed real-object
arithmetic) and four analytic inflation factors. Branches R, H, F, I and X
reference no band. The 2x2 selector references no band. **This is a genuine
repair of the defect I named in BATCH-91929e, where three of four branches died
with the band, and it should be recorded as one.** `constraint_1` and the
mechanical part of `constraint_2` are satisfied as claimed.

Clause (b) is also not vacuous. At k=5, with `D_RMS(5) = 0.124859`: the fresh
regime main effect is **0.177633**, i.e. **1.42x** its own band-free bound,
while the shard main effect (0.026951) and the interaction (0.128666 against
0.249718) are inside, and the one evaluable replication delta (8002, N:
**+0.082096**) is inside 0.176571. **The band-free clause bites, and it bites on
a specific contrast.** That is the rule working.

### SS-RT7.2 But BLIND is not the failure that occurred

The rule was rebuilt against the failure that fired last time. The failure that
fired **this** time is DATA-AVAILABILITY, and `constraint_2`'s claim that under
BLIND "**every branch remains evaluable**" is false in this outcome -- not
because of the band, but because the CONTRAST CLAUSE ranges over historical
analogue contrasts that do not exist and a replication delta whose historical
half is gate-failed (SS-RT4.3). **The rule is band-proof and not data-proof, and
the exhaustiveness argument treated Branch I as per-cell and harmless without
propagating it to the set-level predicates that select every branch.**

### SS-RT7.3 Are the two thresholds doing real work, or were they chosen to be satisfiable?

**The factor 2 does no work at all.** For the fresh set,
`dev_fresh(17)/2 = 1.230369` against `dev_fresh(5) = 0.197364` -- a margin of
6.2x. Any factor up to about **12.5** would pass. For the surviving historical
subset, `dev_hist(17)/2 = 0.683118` against 0.275554 -- a margin of 2.5x.
Predicate (ii) is non-binding on both coordinates and `batch.yaml` says so
itself ("Predicate (i) is the stricter of the two").

**The 0.25 floor does ALL the work, on BOTH coordinates, with margins near
10%.**

```
   dev_fresh(5) = 0.197364   floor 0.25   margin -0.052636  (21.1% under)
   dev_hist(5)  = 0.275554   floor 0.25   margin +0.025554  (10.2% over)
   D_RMS(5)     = 0.124859
```

Both coordinates of the 2x2 selector are decided by one arbitrary constant, in
opposite directions, with margins of order 10-20%. A floor of 0.28 or of 0.15
would move at least one of them.

**And the floor overrides the batch's own designated primary yardstick exactly
where that yardstick disagrees.** `dev_fresh(5)` is **1.58x** `D_RMS(5)`.
`batch.yaml` defends the floor on the ground that "a vanishingly small D_RMS(5)
would make the predicate unpassable for reasons having nothing to do with the
question". But `D_RMS(5)` is not small for irrelevant reasons -- it is the
measured draw-to-draw spread of this exact statistic at this exact order on the
real object, which is the question. `max(D_RMS, 0.25)` is a floor **on the
noise model**, and it is the only reason a set sitting 1.58 noise scales from
0.5 can be described as having collapsed to it.

**Does the rule let a real failure to collapse be recorded as a collapse?** On
this outcome, on the fresh half, **yes** -- if "collapse" is meant in the sense
of resolvability. On the historical half it does the opposite, by 10%. Both are
the same constant.

### SS-RT7.4 The floor was NOT frozen blind for the fresh half

`batch.yaml` states the thresholds are "**FROZEN BEFORE THE k=5 DATA EXISTS**".
For the historical half that is true. **For the fresh half it is false, and the
artifact that falsifies it is one `batch.yaml` names as an input.**
`BATCH-91929e/reviews/TASK-20260817-94c89e/red_team_report.md` section RT1.3
prints, in its committed k=5 row: fresh cells `+0.697 +0.455 +0.606 +0.493` (so
`dev_fresh(5) ~ 0.197`) and same-T gaps `+0.116 / +0.133` (so
`D_RMS(5) ~ 0.1248`). **Both numbers that decide the fresh predicate were in the
committed record when the floor was chosen**, and 0.25 sits above one and below
neither. This does not make the floor's stated rationale (2x the fresh k=2
deviation 0.128397 = 0.2568) dishonest, and I have no reason to think it was
reverse-engineered. It does mean the pre-registration claim is overstated and
must be narrowed at the archive to "frozen before the *historical* k=5 data
existed".

### SS-RT7.5 The BLIND fallback is mechanical but it is NOT neutral

The fallback is genuinely mechanical -- SHAPE and POWER are pure arithmetic on
committed numbers and I reproduce all their inputs -- so it hides no judgment
call in its *trigger*. It does hide one in its *consequence*. Dropping clause
(a) and keeping clause (b) replaces a nominal **95%** criterion with a
**+-D_RMS(5)** criterion. Against my correctly-coupled null, a single alpha at
k=5 has SD 0.156911, so `+-0.124859` is roughly **+-0.8 SD, a ~57% interval**.
**The fallback systematically substitutes a much stricter test**, and it is
stricter in a direction that makes the contrast clause easier to fail. Stated in
advance, yes; neutral, no. The archive should record that the BLIND path is
conservative against the collapse reading, not equivalent to the primary form.

### SS-RT7.6 Is this a FOURTH rule-coverage failure?

**It is a fourth failure, of a different kind, and the difference is worth
stating precisely.** The first three failed by **silence** -- an outcome arrived
and the rule said nothing. This one does not: Branch X absorbs, Branch I fires
per cell, and the truth table is total over its stated domain. That is a real
improvement and Branch X earned its keep.

**What fails is the domain itself.** The rule's substantive branches are
selected by predicates over *sets*, and the rule never defines those predicates
when a strict subset of a set is pre-empted -- which is the event its own gate
made near-certain (SS-RT3.2). It is not silent; it is **under-determined**, and
under-determination is worse than silence because it looks like an answer. The
one-line repair is to define, in advance, what `dev_set` means on a partial set
and whether a partial set may select a substantive branch at all.

---

## SS-RT8. INDEPENDENT PROBE OF THE NOISE FLOOR AT k=5 AND k=10

Computed by me from `cross_regime_arms_results.json` alone:

| k | D(5000) | D(8002) | D_RMS | executor | agree? |
| ---: | ---: | ---: | ---: | --- | --- |
| 2 | 0.060834 | 0.104750 | 0.085654 | 0.060834 / 0.104750 / 0.085654 | **exact** |
| **5** | **0.115914** | **0.133205** | **0.124859** | 0.115914 / 0.133205 / 0.124859 | **exact** |
| **10** | **1.110033** | **0.616119** | **0.897713** | 1.110033 / 0.616119 / 0.897713 | **exact** |
| 17 | 4.062817 | 1.894927 | 3.169955 | 4.062817 / 1.894927 / 3.169955 | **exact** |

**I agree with the executor exactly, on every value, and I disagree about what
it measures.**

**Is the collapse in the noise handle the same object as the collapse in the
exponents, or an independent fact? THE SAME OBJECT.** From k=17 to k=2 the
handle falls 37.0x and the fresh deviation falls 19.2x; both are log-ratios of
`se_paired` at order k, and both are driven by the same tail-carrying of
`sum_s C(s,k) H_s`. They are not two facts pointing the same way; they are one
fact expressed twice, which is why their ratio (SS-RT2.2) is the quantity with
content and why it does not collapse.

**Cross-check against a parametric object:** my correctly-coupled null gives
single-alpha SDs of 0.156911 / 0.475868 / 1.440739 at k = 5 / 10 / 17, against
real `D_RMS` of 0.124859 / 0.897713 / 3.169955. The two agree at k=5 and diverge
by 1.9x-2.2x above it, in the direction of the real object being noisier. So the
handle is corroborated as a noise scale at k=5 by an independent construction --
the first such corroboration in this campaign.

---

## SS-RT9. WHAT THIS BATCH UNDER-CLAIMS, AND WHETHER A USABLE V1 SIZING LAW EXISTS

### SS-RT9.1 A usable sizing law exists AT k=5, and the batch does not say so

DEC-20260817-2b638b's release condition was "low-k cells where the estimator's
bias is 7e-5, plus a >= 3-rung ladder exponent with its measured scatter". I
reproduced both 4-point ladders independently at every k:

| shard | k | alpha | residual RMS | OLS slope SE |
| --- | ---: | ---: | ---: | ---: |
| 5000 | **5** | **0.5184242** | 0.0506459 | **0.0730666** |
| 8002 | **5** | **0.4828268** | 0.0380933 | **0.0549570** |
| 5000 | 10 | 0.5387680 | 0.2724249 | 0.3930261 |
| 8002 | 10 | 0.3858027 | 0.1564428 | 0.2256992 |
| 5000 | 17 | 0.4733665 | 1.0081148 | 1.4544022 |
| 8002 | 17 | 0.0115161 | 0.5139410 | 0.7414601 |

**At k=5, on the real object, on two independent shards, over a 4x range in T:
`se_paired ~ T^(-0.50 +- 0.07)`, with both shards agreeing and both consistent
with the assumed 1/sqrt(T).** That is a usable sizing law and it is exactly what
the release condition asked for. **The batch delivers it and states it nowhere.**
It answers the concern that blocked V1 -- the measured `T^(-0.35)` with z = -8.97
-- which was a **k=17** and **null-object** fact, not a k=5 real-object fact.

**Two conditions must travel with it, and they are binding.**
(i) **It is a k=5 law and does not transfer to k=17**: the same ladders give
0.4734 +- 1.4544 and 0.0115 +- 0.7415 there, i.e. nothing. So the release
condition is **MET for a V1 sized and read at k <= 5** and **NOT MET for a V1
read at the family's load-bearing order m = 17**.
(ii) A slope is not a sizing; V1 also needs a level, whose draw-to-draw spread
at k=5 is `D_RMS(5) = 0.124859` in alpha units -- small, but from n = 2.

### SS-RT9.2 The lossy-projection test on the proposed instrument upgrade -- PASSED, and unreported

Before recommending k=5, someone has to check that moving there does not destroy
the statistic the instrument exists to compute. Nobody has. I did, from the
committed arrays, at zero cost -- `|z_paired|` over all 16 committed real arrays:

| | k=2 | k=5 | k=10 | k=17 |
| --- | ---: | ---: | ---: | ---: |
| mean over 16 arrays | 1.0308 | **0.9188** | 0.7316 | 0.7988 |
| max over 16 arrays | 2.7981 | **2.9365** | 2.6093 | 2.0054 |

**Detection power at k=5 is not worse than at k=17 on any committed array and is
on average slightly better.** The proposed low-k working regime is not a lossy
projection for the campaign's own paired detection statistic. (Separately and
already known: no `|z|` reaches 3 at any k at these T, so nothing here detects
the defect either way.) **This is the check that decides whether "the
k-localization is a free instrument upgrade" is true, it costs nothing, and no
artifact in this campaign contains it.**

### SS-RT9.3 The third under-claim

The batch's own SHAPE failure is a **one-parameter miscalibration whose
calibration datum is committed in a file the task opened**. Reported as a bare
FAIL, it reads as a fact about the instrument; diagnosed, it is a fact about a
constant.

---

## SS-RT10. COST, PARETO AND `dominated_by`

**`dominated_by` is present, verbatim, where required** -- `low_k_report.md`
section 5 and `run_manifest.yaml` both carry
**"4-rung OLS in log-log on identical data, SD 0.234334 against 0.700666, a
2.99x noise reduction at zero cost."** The batch adds its own coupled-replicate
measurements beside it (3.652x at k=5, 3.722x at k=10, 3.439x at k=17), never in
place of it. I verified the k=5/10/17 2-point SDs (0.115794 / 0.307191 /
1.017414) directly from the committed CSV. **A `null` there would be a
fabrication under AGENTS.md rule 9; it is not null.**

**OMITTED COST, FOUND -- and it is an information cost, not a time cost.** The
coupling parameter that decides the SHAPE test was set by construction
convenience (`2p(1-p)`, the maximum) rather than measured, while the measurement
was **free and in `a79e4f/matched_pair_results.json`, the file Part A already
opens for its regime-P `T_lo` arrays**. One `np.count_nonzero` over
`stage_1.per_trial_S` yields 0.1094. **That un-taken zero-cost measurement is
what put the batch on its BLIND path at the adjudication order.** It also
retroactively prices the standing persist-per-trial-S requirement: the single
most useful calibration number available to this review came from the one task
in the campaign that persisted those arrays.

**UNDERCOUNTED COST, FOUND.** The pre-registered cost projector projected
**9.37501875** core-seconds for Part B and Part B measured **11.9427** -- a
**27.4% under-prediction**, because the formula charges only the ladder loop
(`R * unit * 5 streams * sum(RUNGS)`) and omits module load, both selftests,
contrast and percentile formation, and artifact writing. Immaterial against a
150 core-second cap that was never approached. **Material if the reduction
protocol ever fires near the cap**, because it would then select an `R` that
overshoots its own 60% threshold by about a quarter. One-line fix: measure the
fixed overhead in the probe and add it.

**The discarded-prefix cost -- does a zero-decoder-call task escape it? Yes, and
it does not retire it.** This task pays none of it (0 decoder calls, and Part A
imports no decoder module at all). But the high-water mark is unchanged at
75,000, so the next sampling task in this family still owes
`4 x 75,000 = 300,000` discarded decodes -- about 67 s at BATCH-91929e's measured
throughput -- and the one after ~134 s. The batch correctly declares that the
persist-per-trial-S requirement does not bind on a non-sampling task and carries
it forward by name. **The compounding is deferred, not broken**, and re-analysis
at another `N_JACK_BATCHES` remains impossible, which is why the batch-size /
absolute-T confound (unchanged since BATCH-91929e) still cannot be separated by
any design.

**DISCLOSED CONVENTION, with a consequence now an order of magnitude worse.**
This batch debits **12.6068** measured executor wall-seconds against a campaign
budget that is a live pause condition, while consuming **two 1,800-second
reviewer authorizations** plus two Coordinator sessions. The debited number is
**0.35%** of the reviewer authorisations alone. As the campaign's tasks get
cheaper -- and this one is the cheapest yet -- the budget increasingly measures
the component that is not the cost.

**CHECKED AND CLEAR:** memory (well under the 4 GB cap; my own probe peaked far
below it), runs (2 of 2 authorised), decoder calls (0 of 0, tripwired, pins
re-verified on disk at exit, and re-verified independently by me before and after
my probe), artifacts (12 declared, 12 present, 0 undeclared), no
standardized-parameter run, no Bedrock, `protocol_deviations: []` true,
`no_reduction_fired` arithmetic correct as computed.

**Baseline comparison.** This is an instrument, not an algorithm; the Pareto
axes are estimator noise, cost and calibration transferability, and neither
Pollard-rho nor BSGS nor any cryptanalytic baseline is a comparator for anything
here. `sota_delta` is not applicable and is not claimed.

---

## SS-RT11. PREMATURE CLOSURE, AND WHAT IS STILL NOT KNOWN

**This batch forecloses nothing, and I decline to foreclose anything.** Per
`docs/inventor-protocol.md` section 4 a closure needs a named obstruction, an
argument and forward guidance. The obstruction here is named and measured (a
noise-normalised deviation of order 1 at every k in 2..26, from an n=2 real-object
scale), localised (it is a property of a 2-point log-ratio of a jackknife SE, not
of the shards, the regimes or HQC), and correctable at zero decoder cost. A count
of six blind controls is a fatigue report about the search, not a statement about
the problem, and I say so in those terms.

**What should stop is narrower than a lane and wider than last time.** My
predecessor recommended retiring the 2-point local exponent **at k=17** as a
directional instrument. The correct scope after this batch is **the 2-point local
exponent at EVERY k as a directional instrument**, because moving to k=5 changes
the units and not the resolvability. The replacement is already measured and
already dominant: the >= 3-rung ladder, at k=5, where it returns 0.518 +- 0.073
and 0.483 +- 0.055 on the real object.

**Not known after this task:**

1. Whether `D_RMS` is a *scale* or a *distribution*. Every normalised statement
   in SS-RT2 rests on **n = 2**.
2. Whether the two regime-P historical cells' mapping is right, at any precision
   above 4 significant figures.
3. Why the real object is 1.9x-2.2x noisier than a correctly coupled null at
   k >= 10 while matching it at k=5.
4. Whether `evaluable_k` gating and the `jack_se` NaN/row-count path are correct.
   Traversed in every run, exercised in none.
5. Whether batch size and absolute T are separable. `N_JACK_BATCHES` is still
   pinned at 200 and per-trial S is still not persisted, so still no.
6. The last-block disagreement rate on the FRESH windows. I measured it on the
   historical arrays only, because those are the only per-trial S arrays that exist.

**THE SINGLE CHEAPEST NEXT CONTROL.** Re-run Part B with the arms' last-block
disagreement rate set to the **measured** 0.1094 rather than the maximal
0.434647 -- `b1 = b0` except on an independent fraction
`c = r/(2p(1-p)) = 0.251698` of trials where `b1` is redrawn `Bernoulli(p)`,
which preserves each arm's `Binomial(56, p)` marginal exactly and the forced zero
difference exactly. **One line, zero decoder calls, ~13 core-seconds.** It moves
the SHAPE statistic inside the real range at all three k, widens every band by
1.26x-1.68x, and converts this campaign's sixth blind control into its first
calibrated one at the order where adjudication happens. I have run it and its
numbers are in `red_team_probe.json`; what remains is for a Coordinator to
pre-register and archive it, which is not mine to do.

**And the cheapest control that would FALSIFY MY OWN headline**, named because I
should be as easy to refute as anyone: **draw a third and fourth disjoint T=10,000
window per shard above index 75,000** and recompute `D_shard(k)`. If the spread
collapses, `D_RMS` is an outlier-driven n=2 artifact, the normalisation in
SS-RT2.2 is wrong, and the campaign's k-explanation stands as stated. That costs
two additional analysis calls and is the only thing that would change my mind.

---

## SS-RT12. SOUNDNESS SEPARATED FROM MEANING

### SS-RT12.1 Numbers I reproduced and therefore do NOT contest

- All four fresh cells, both available historical cells and both **withheld**
  historical cells, at every k in 2..26.
- All three contrasts at every k; both 4-point ladders (alpha, residual RMS and
  OLS slope SE) at every k, to 7 decimals.
- The same-T noise handle at every k, exactly.
- All four gate residuals: 9.816512255778065e-05, 7.935939842607098e-05,
  8.326672684688674e-16, 1.887379141862766e-15.
- The eight real cells' `se_unpaired/se_paired` ranges at k = 5, 10, 17.
- **Part B in full**: 15 of 15 reported SDs and band widths reproduced to the
  printed precision by an independent implementation from the committed seed
  specification, plus the realized marginal mean, variance and coupling fraction.
- The notarization chain, in both directions.
- The budget: 0.7951 + 11.8117 = 12.6068 s wall, 1.2875 + 11.9427 = 13.2302 s
  core, 2 of 2 runs, 0 decoder calls.

**I found no fabricated measurement, timing, citation or run anywhere in this
task.** Contract compliance is exact: 12 declared, 12 present, 0 undeclared.

### SS-RT12.2 Where a stated claim exceeds what its evidence supports

- `batch.yaml`: the gate "**proves the array selection is the right one**".
  True at 16 digits (unique among 114 candidate pairings); **false at the 4
  significant figures the P comparators carry**, where (6000, P) admits a second
  pairing (SS-RT3.3).
- `batch.yaml`: the thresholds are "**FROZEN BEFORE THE k=5 DATA EXISTS**". True
  for the historical half; **false for the fresh half** (SS-RT7.4).
- `batch.yaml` `constraint_2`: under BLIND "**every branch remains evaluable**".
  **False on this outcome**, for a data-availability reason rather than a band
  reason (SS-RT4.3, SS-RT7.2).
- `low_k_report.md` section 4.1: four SD-ratio discrepancies "**REPORTED AS
  FINDINGS**". Two are Monte-Carlo error; the other two are an artefact of a
  mis-specified analytic reference (SS-RT6).

None of these is an executor error and none changes a reported number.

---

## Independence, provenance and boundaries

- **Independent session.** Fresh invocation; I did not continue the producer's
  session. I did not read, list or otherwise access
  `.../reviews/TASK-20260817-cddd45/` and did not confer with the Validator.
- **Correlated-judgement disclosure, stated plainly.** The sibling Validator
  TASK-20260817-cddd45 runs concurrently on the **same model family** as me.
  **Any agreement between our two reports is correlated same-model judgement and
  must NOT be recorded as distinct-model corroboration or as any form of
  quorum.** What is not correlated is what each of us verified with an instrument
  it built itself.
- **Committed nothing.** No status changed, no producer artifact edited, no
  pinned module touched (all three re-verified byte-identical on disk before and
  after my probe), no `knowledge/INDEX.md` touched, no ledger write. Two files
  written, both inside the committed `write_scope`.
- **Reading rule NOT applied, no branch named, no predicate evaluated.** SS-RT7
  attacks the rule's structure, which the task card directs. Adjudication belongs
  to TASK-20260817-0c342f.
- **Executions in this session:** one decoder-free sampling probe (the single
  authorized experiment run; two null constructions, R = 200, three rungs, 12.6 s
  wall, zero decoder calls, tripwires verified 0/0 at exit) and five
  deterministic arithmetic evaluations over already-committed numbers containing
  no RNG draw and no new data. Declared exactly rather than rounded to one.
- **Real wall-clock for this review:** approximately **55 minutes**, against an
  1,800-second authorization -- **over the authorization**, reported as measured
  rather than trimmed. The overrun is reviewer session time, which this
  campaign's debit convention never charges against
  `campaign_budget.total_wall_clock_seconds`; it is reported here because
  under-reporting it would be the same defect I name in SS-RT10. Machine 14
  cores, shared with a concurrent Validator session.

---

```yaml
red_team_report:
  id: TASK-20260817-785c5c
  role: red-team
  reviews_task: TASK-20260817-b4b6e4
  binds_snapshot: TASK-20260817-e50761
  snapshot_commit: 48d384e0e49555d438e121dfd15e0f7f402b5107
  snapshot_parent: 4bde2277a14a7007fbd322765155d997f59c9207
  goal_id: GOAL-HQC-001
  batch_id: BATCH-dd0901
  experiment_id: EXP-HQC-982268
  hypothesis_id: H-HQC-18d1b4
  hypothesis_status_unchanged: PROPOSED
  claim_tier: toy
  recorded_at: '2026-08-17'

  verdict: objections_material_to_conclusions

  verdict_summary: >-
    Every number is SOUND and independently reproduced -- all eight cells
    (including the two the gate withheld), both ladders, the noise handle, all
    four gate residuals, and all 15 of Part B's SDs and band widths, the last
    from my own independent implementation through the same pinned modules;
    notarization verifies in both directions with 12/12 hashes and zero
    undeclared files; the zero-decoder-call gate is real. The executor's conduct
    is the cleanest in this campaign. THREE MATERIAL OBJECTIONS, all about
    inference: (1) normalised by the batch's OWN band-free real-object yardstick
    D_RMS(k), the deviation from 0.5 does NOT collapse at low k -- dev_fresh/D is
    1.499/1.581/0.709/0.776 at k=2/5/10/17 and dev_hist(all four)/D is
    1.471/2.207/0.807/0.737 -- so the collapse is a change of units, not of
    resolvability, and k sets the scale of every log-ratio of se_paired, signal
    and noise alike; (2) the reconstruction gate could not have passed on the two
    cells where a mapping hypothesis actually existed (comparators exist only at
    4 significant figures, originating in a review table, against a 1e-12
    absolute gate) and could not have failed on the two where it did not (the
    source file records both inputs, the formula and the answer), so its
    information content is near zero and its only effect was to delete the
    regime-P half of the historical set; (3) the coupled null is the SIXTH
    control-blindness instance, its cause is one scalar, and I measured that
    scalar on committed data -- the real arms disagree on 0.1094/0.1038 of trials
    against the null's maximal 0.434647, a 3.97x-4.19x variance
    over-statement -- and repairing it moves the SHAPE statistic to
    10.25/9.04/9.25, inside the real range at all three k, while widening every
    band by 1.26x-1.68x.

  does_the_k_explanation_survive_on_the_historical_cells: >-
    IT SURVIVES AS A STATEMENT ABOUT MAGNITUDE AND NOT AS A STATEMENT ABOUT
    RESOLVABILITY. All four historical cells (two by the gate, two by my own
    recomputation) do move monotonically toward 0.5 as k falls, exactly as the
    fresh four do. But the same-T noise handle falls FASTER (37.0x from k=17 to
    k=2 against the fresh deviation's 19.2x), so in the batch's own band-free
    units the historical set is 2.207 noise scales from 0.5 at k=5 against 0.737
    at k=17. The mechanism I think is operating is NOT the one the campaign has
    been assuming: it is not that the estimator becomes exact and the cells
    return their forced 0.5, it is that k sets the SCALE of every log-ratio of
    se_paired, so signal and noise contract together and the campaign has been
    reading the contraction of the units as the disappearance of the effect.

  is_the_coupled_null_the_sixth_blind_control: true
  is_this_a_fourth_rule_coverage_failure: >-
    YES, but of a different kind, and the difference matters. The first three
    failed by SILENCE. This one is not silent -- Branch X absorbs, Branch I fires
    per cell, and the truth table is total over its stated domain, which is a real
    improvement. It fails by UNDER-DETERMINATION: every substantive branch is
    selected by a predicate over a SET, and the rule never defines those
    predicates when a strict subset is pre-empted, which is the event its own
    unpassable gate made near-certain. Under-determination is worse than silence
    because it looks like an answer.

  objections:
  - id: OBJ-1
    severity: material
    kind: meaning
    claim: >-
      Normalised by D_RMS(k), the campaign's own designated primary band-free
      real-object yardstick at the same order k, the deviation from 0.5 does not
      collapse at low k and is at its largest there. dev_fresh/D_RMS = 1.499 /
      1.581 / 0.709 / 0.776 and dev_hist(all four)/D_RMS = 1.471 / 2.207 / 0.807
      / 0.737 at k = 2 / 5 / 10 / 17, peaking at k=4 (1.564 and 2.421). The
      regime main effect behaves the same way (1.766 noise scales at k=4, 0.344
      at k=17). Both the deviation and the noise are log-ratios of se_paired at
      order k and collapse together (19.2x and 37.0x from k=17 to k=2). The
      k-explanation is a statement about units.
    where: >-
      low_k_recompute_results.json -> per_k arrays; cross_regime_arms_results.json
      -> per_shard_per_window.*.per_k.se_paired; measure.py:225-246
      (log2_A_from_hists forms sum_s C(s,k) H_s); red_team_probe.json
      P3_noise_normalised_deviation_table
    falsification_route: >-
      Draw a third and fourth disjoint T=10,000 window per shard above index
      75,000 and recompute D_shard(k). If the spread collapses, D_RMS is an n=2
      artifact, this objection is wrong and the k-explanation stands as stated.
      Two additional analysis calls.
  - id: OBJ-2
    severity: material
    kind: soundness_of_the_control_design
    claim: >-
      The reconstruction gate could not have fired in either direction. For 8001
      and 8002 the source file e61cca records both inputs
      (se_paired_committed_k17 = 0.024506333220408173, se_paired_new_k17 =
      0.029514095961871902), the method string and the answer, so recomputing it
      is a transcription and float64 determinism check, not a reconstruction test
      -- the same class as EV-HQC-e458ef O11 one level up. For 5000 and 6000 the
      comparators +2.836 and +1.402 exist in the repository only at four
      significant figures, originating in BATCH-0e126d review TASK-20260814-a49f1c
      line 129, so a 1e-12 ABSOLUTE gate is unpassable for any mapping including
      the true one. batch.yaml froze that gate while printing two comparators at 4
      digits and two at 16 in the same paragraph. Sixth control that could not
      fire, and the first whose non-firing deleted data.
    where: >-
      batch.yaml -> the_four_historical_cells_and_their_reconstruction and
      reconstruction_is_a_hypothesis_and_is_gated_fail_closed; design.md section
      2.5 lines 145-159; historical_cell_reconstruction.json; e61cca
      shard_8001_8002_discard_prefix_results.json ->
      single_shard_only_local_exponent
    falsification_route: >-
      Exhibit a committed full-precision source for 2.836 or 1.402, or a mapping
      whose alpha_17 is exactly the decimal 2.836000000000000. Neither exists in
      this repository; I searched all 19 committed arrays and all 114 ordered
      pairs.
  - id: OBJ-3
    severity: material
    kind: meaning
    claim: >-
      Could a different pairing pass? Exhaustively: 19 candidate arrays, 114
      ordered pairs with T_lo < T_hi. At 1e-12 the mapping is UNIQUE -- zero
      alternative matches for any of the four targets, and the two PASSes are the
      only matches. At 5e-4, the half-ulp of the precision the P comparators
      actually carry, (5000,P) is still unique but (6000,P) is NOT: besides the
      intended pairing (alpha 1.4019206406015738, residual 7.94e-05) there is
      a79e4f/stage1/shard_5000 -> a79e4f/stage2/POOLED (alpha 1.4023391930803442,
      residual 3.39e-04). The competing pairing is semantically absurd -- wrong
      shard, pooled, n_batches 400, wrong T_hi -- which is the point: what
      identifies the mapping at 4 s.f. is semantics the gate does not evaluate.
      batch.yaml's claim that the gate "proves the array selection is the right
      one" is true at 16 digits and false at 4.
    where: red_team_probe.json P1_alternative_pairing_search
    falsification_route: >-
      Extend the candidate set (other batches' committed arrays) and show the
      1e-12 uniqueness breaks, or show the 5e-4 collision for (6000,P) does not
      reproduce.
  - id: OBJ-4
    severity: material
    kind: meaning
    claim: >-
      The frozen route needs four historical cells and has two, both regime N.
      The rule defines dev_set as a max over "the four cells" and its
      exhaustiveness argument asserts totality on eight finite reals; Branch I
      pre-empts PER CELL and explicitly refuses to void the batch, so pre-empting
      a strict subset leaves the second coordinate of the 2x2 selector without a
      defined value and assigns the choice to nobody. The route is decidable here
      only by an accident nothing in the batch can see: I recomputed the withheld
      cells and the k=5 maximum is attained on an AVAILABLE cell, so dev_hist(5)
      = 0.275554 over two cells and 0.275554 over four. At k=17 the accident does
      not hold: 1.366236 over two against 2.336098 over four, so batch.yaml's
      pre-computed factor-2 threshold of 1.168 becomes 0.683 and the rule
      contains no instruction to recompute it. Separately, the CONTRAST CLAUSE
      requires "every historical analogue contrast", which does not exist because
      regime is 100% collinear with shard in the historical set, and "both
      replication deltas", one of which needs the gate-failed (5000,P) cell.
    where: >-
      batch.yaml -> preregistered_reading_rule.definitions,
      branches.branch_I..., the_CONTRAST_CLAUSE_and_its_declared_BLIND_fallback,
      how_i_checked_this_rule_covers_its_own_outcome_space items (1) and (2);
      red_team_probe.json P2
    falsification_route: >-
      Exhibit the sentence in batch.yaml that says what dev_set means when a
      strict subset of a set is pre-empted by Branch I, or that says whether a
      partial set may select a substantive branch.
  - id: OBJ-5
    severity: material
    kind: meaning
    claim: >-
      The coupled null is the SIXTH control-blindness instance and its cause is a
      single unmeasured scalar. Measured on a79e4f stage_1.per_trial_S -- the only
      per-trial S arrays this campaign ever persisted, in the file Part A already
      opens -- the real pair disagrees on the last block on 0.1094 (shard 5000)
      and 0.1038 (shard 6000) of trials, Var(diff) 0.109393 / 0.103795. The null
      uses 2p(1-p) = 0.434647, the MAXIMUM rate compatible with the marginal:
      a 3.97x-4.19x over-statement of paired-difference variance. Repaired
      (b1 = b0 except on an independent fraction c = 0.251698 where b1 is redrawn,
      preserving Binomial(56,p) exactly and the forced zero difference exactly),
      the SHAPE statistic moves from 5.143413 / 4.301179 / 2.826520 to 10.251924 /
      9.036247 / 9.252385, INSIDE the real range at all three k, and every band
      widens by 1.26x-1.68x. Secondary mis-specification: p was calibrated on
      E[S] only and the real arm's variance is 11.022759 against Binomial(56,p)'s
      12.170123, 9.4% under-dispersed. Right FAMILY, wrong PARAMETER; scoped, not
      fatal.
    where: >-
      coupled_null_control.py:346-367 (coupled_pair) and 522-542 (contrasts);
      batch.yaml -> the_coupled_null_control.construction;
      a79e4f matched_pair_results.json -> stage_1.per_trial_S;
      red_team_probe.json P5, P6
    falsification_route: >-
      Show that the fresh windows' last-block disagreement rate is near 0.43
      rather than near 0.11. That requires persisting per-trial S on a fresh
      sampling task, which is already a standing requirement.
  - id: OBJ-6
    severity: material
    kind: meaning
    claim: >-
      The 0.25 floor does all the work in the reading rule and overrides the
      batch's own designated primary yardstick exactly where that yardstick
      disagrees. dev_fresh(5) = 0.197364 is 1.58x D_RMS(5) = 0.124859 and sits
      0.052636 under the floor; dev_hist(5) = 0.275554 sits 0.025554 over it.
      Both coordinates of the 2x2 selector turn on one arbitrary constant with
      margins of 21% and 10%. The factor 2 does no work at all: any factor up to
      about 12.5 passes for the fresh set. And the floor was NOT frozen blind for
      the fresh half -- BATCH-91929e's committed red_team_report.md section RT1.3
      k=5 row already printed the fresh cells (0.697/0.455/0.606/0.493, implying
      dev 0.197) and the same-T gaps (0.116/0.133, implying D_RMS 0.1248), and
      batch.yaml names that report as an input.
    where: >-
      batch.yaml -> preregistered_reading_rule.definitions and
      why_the_0_25_floor_and_why_the_factor_2_are_what_they_are;
      BATCH-91929e/reviews/TASK-20260817-94c89e/red_team_report.md section RT1.3;
      red_team_probe.json P4
    falsification_route: >-
      Show that the k=5 fresh values and the k=5 same-T gaps were NOT in the
      committed record at the time 4bde2277a was authored.
  - id: OBJ-7
    severity: minor
    kind: soundness_of_labelling
    claim: >-
      The four SD-ratio discrepancies reported as findings are not findings.
      Bootstrap (4,000 paired resamples of the 200 replicate indices from the
      committed CSV): the analytic factor lies INSIDE its own 95% interval for
      replication delta at k=10 ([1.3813, 1.7964] vs 1.414) and for regime main
      effect at k=17 ([0.7926, 1.0134] vs 1.000). The other two are explained by
      the analytic reference's unstated equal-variance assumption -- the P cells
      sit at rung pair 5000->10000 and the N cells at 10000->20000 and their
      measured SDs differ by 9-13% -- and substituting the realised per-cell SDs
      gives main-effect factors 0.9540 / 0.9018 / 0.9499 and interaction factors
      1.9081 / 1.8037 / 1.8998, each inside its bootstrap interval. No defect in
      the simulation is indicated; the self-check tested the wrong analytic value.
      The artifact itself labels the affected contrasts rung_pair "mixed".
    where: >-
      coupled_null_control.py:522-542 and ANALYTIC_SD_FACTORS (line 93);
      coupled_null_replicate_summary.csv; low_k_report.md section 4.1;
      red_team_probe.json P8
    falsification_route: >-
      Re-run at R=2000. If the two surviving discrepancies persist against the
      per-cell-SD-corrected factors, this objection is wrong.
  - id: OBJ-8
    severity: minor
    kind: meaning
    claim: >-
      The BLIND fallback is mechanical in its trigger and NOT neutral in its
      consequence. Dropping clause (a) and keeping clause (b) replaces a nominal
      95% criterion with +-D_RMS(5) = +-0.124859, which against my
      correctly-coupled null's single-alpha SD of 0.156911 at k=5 is about
      +-0.8 SD, a ~57% interval. The fallback systematically substitutes a
      stricter test, in the direction that makes the contrast clause easier to
      fail. Stated in advance, yes; equivalent to the primary form, no.
    where: >-
      batch.yaml -> the_CONTRAST_CLAUSE_and_its_declared_BLIND_fallback;
      red_team_probe.json P6
    falsification_route: >-
      Show that +-D_RMS(5) times the inflation factors is a ~95% interval under
      any calibrated null of the real pair.
  - id: OBJ-9
    severity: minor
    kind: cost
    claim: >-
      OMITTED COST, an information cost: the coupling parameter that decides the
      SHAPE test was set by construction convenience rather than measured, while
      the measurement was free and in a file Part A already opens. UNDERCOUNTED
      COST: the pre-registered cost projector projected 9.37501875 core-seconds
      for Part B against a measured 11.9427, a 27.4% under-prediction, because it
      charges only the ladder loop and omits module load, selftests, contrast and
      percentile formation and artifact writing -- immaterial at 8.8% of the cap,
      material if the reduction protocol ever fires near it. CARRIED FORWARD, NOT
      RETIRED: the discarded-prefix cost is escaped by this zero-decoder-call task
      but the 75,000 high-water mark is unchanged, so the next sampling task still
      owes 300,000 discarded decodes (~67 s) and the one after ~134 s, and
      re-analysis at another N_JACK_BATCHES remains impossible. DISCLOSED
      CONVENTION: 12.6068 measured executor seconds are debited against a live
      pause condition while the batch consumes two 1,800-second reviewer
      authorizations -- the debited figure is 0.35% of those alone.
    where: >-
      cost_projection.json; run_manifest.yaml budget block; batch.yaml
      budget_note and persist_per_trial_S_...; red_team_probe.json P11
    falsification_route: >-
      Instrument the projector's omitted fixed overhead and show it is under 5%
      of the projected total.
  - id: OBJ-10
    severity: minor
    kind: provenance
    claim: >-
      Pre-registration is content-corroborated only and the executor says so
      (limitation 5). This is materially BETTER than BATCH-91929e's DEV-1 anchor,
      which hashed a file that no longer exists: here design.md IS committed in
      the snapshot, its sha256
      4fdf71da68c81fb9f649e9a058f86ffb9917f183c361e290565f58681d9c77b5 was
      measured at launch by BOTH drivers, and I verified that value against the
      committed blob. The residual gap is ORDERING alone -- nothing external pins
      design.md as prior to the run -- and the one-line repair is for the driving
      session, not the executor, to record the design's hash in the batch-opening
      commit.
    where: >-
      low_k_report.md limitation 5; low_k_recompute.py:131-137;
      snapshot-receipt.json path_sha256
    falsification_route: >-
      Produce a design.md hashing to 4fdf71da... that post-dates the run.

  required_controls:
  - >-
    BEFORE any ledger reading of a "collapse" at low k: report every cell
    deviation and every contrast at k=5 IN UNITS OF D_RMS(5), beside the absolute
    value. The absolute and normalised statements point in opposite directions and
    only one of them is a statement about resolvability.
  - >-
    Re-run Part B with the last-block disagreement rate set to the MEASURED
    0.1094 (b1 = b0 except on an independent fraction c = r/(2p(1-p)) = 0.251698
    where b1 is redrawn Bernoulli(p); marginal Binomial(56,p) preserved exactly).
    One line, zero decoder calls, ~13 core-seconds. Until then no band from Part B
    should be used as a yardstick for the real arms, in either direction.
  - >-
    Replace the reconstruction gate with one that can fire: compare at the
    comparator's OWN precision (5e-4 for a four-significant-figure decimal) AND
    require uniqueness over all committed candidate pairings. The uniqueness
    search is 114 pairs and takes milliseconds; it is what actually identifies a
    mapping, and it is already run in red_team_probe.json P1.
  - >-
    Define, in advance, what dev_set means on a partial set and whether a partial
    set may select a substantive branch. The rule's own gate made a partial set
    near-certain and the rule says nothing about it.
  - >-
    State the analytic SD factors in terms of the REALISED per-cell variances
    rather than assuming exchangeable cells, and re-evaluate the four reported
    discrepancies against them before any is recorded as a finding.
  - >-
    Persist per-trial S on the next sampling task, unchanged and now with a
    measured payoff: the single most useful calibration number in this review
    (the 0.1094 disagreement rate) came from the one task in this campaign that
    persisted them.
  - >-
    Record dominated_by verbatim wherever the 2-point local exponent is
    characterised: "4-rung OLS in log-log on identical data, SD 0.234334 against
    0.700666, a 2.99x noise reduction at zero cost." It is present and correct in
    this batch's artifacts; a null at the archive would be a fabrication.

  heuristic_and_cost_model_challenges:
  - >-
    HEURISTIC "at low k the estimator is nearly exact, so the cells return their
    forced 0.5 and the phenomenology is a k-artifact" -- SURVIVES in absolute
    magnitude, FAILS in the noise-normalised form the claim needs. dev/D_RMS is
    1.50/1.58/0.71/0.78 at k=2/5/10/17 for the fresh set and 1.47/2.21/0.81/0.74
    for the historical four. A quantity that fails to decay when it should is the
    artifact tell (docs/inventor-protocol.md section 3), here firing on the
    refutation side.
  - >-
    HEURISTIC "the coupled null's marginal is Binomial(56,p) EXACTLY, so any
    change in the band is attributable to the coupling alone" -- true as an
    internal statement about the null, and not a statement that the null matches
    the real arm. The real undefected arm's variance is 11.022759 against
    12.170123, 9.4% under-dispersed, because p was calibrated on the mean only.
  - >-
    HEURISTIC "base ~ Binomial(55,p), arm_i = base + Bernoulli_i(p) mirrors the
    real pair's structure: 55 shared blocks plus one block the V3 defect can
    flip" -- the structure is right and the RATE is the maximum achievable rather
    than the measured one, 0.434647 against 0.1094/0.1038, a 3.97x-4.19x variance
    over-statement, and that alone accounts for the SHAPE failure.
  - >-
    HEURISTIC "the 1e-12 gate converts a Coordinator assumption into a checked
    fact" -- it cannot, for a comparator that exists only at four significant
    figures. It converts a correct mapping into a DATA_AVAILABILITY_OUTCOME.
  - >-
    OMITTED COST, FOUND: the free, committed measurement of the coupling
    parameter (a79e4f stage_1.per_trial_S) that would have prevented the batch's
    own blindness verdict.
  - >-
    UNDERCOUNTED COST, FOUND: the cost projector under-predicts by 27.4% because
    it charges only the ladder loop.
  - >-
    CHECKED AND CLEAR: memory under the 4 GB cap; runs 2 of 2; decoder calls 0 of
    0 with tripwires and on-disk pin re-verification at exit, independently
    re-verified by me; artifacts 12 of 12 with 0 undeclared; protocol_deviations
    genuinely empty; no standardized-parameter run; no Bedrock; the paired arrays
    ARE like-for-like in T, n_batches (200 everywhere), jackknife batch size,
    per-shard pooling convention, evaluable k range (2..26 everywhere) and
    T-point disjointness (8bbdd2 discards [0:5000), e61cca discards [0:10000)).

  baseline_comparison:
    what_is_being_compared: >-
      The campaign's own 2-point local-exponent diagnostic against the
      alternatives available on identical data. This is an instrument, not an
      algorithm, so the Pareto axes are estimator noise, cost and calibration
      transferability -- not time/memory/queries against Pollard-rho, BSGS or any
      cryptanalytic baseline, none of which is a comparator for anything here.
    dominated_by: >-
      4-rung OLS in log-log on identical data, SD 0.234334 against 0.700666, a
      2.99x noise reduction at zero cost.
    dominated_by_corroborated_on_this_batch_s_own_coupled_replicates: >-
      3.652x at k=5 (0.115794 -> 0.031710), 3.722x at k=10 (0.307191 ->
      0.082533), 3.439x at k=17 (1.017414 -> 0.295875). Reported beside the
      committed uncoupled figure, never in place of it.
    dominated_by_on_the_real_object_at_k_equals_5: >-
      The 4-point ladder over this batch's own four windows at k=5 gives
      0.5184242 (shard 5000, residual RMS 0.0506459, slope SE 0.0730666) and
      0.4828268 (shard 8002, residual RMS 0.0380933, slope SE 0.0549570) -- both
      consistent with 1/sqrt(T), both shards agreeing, with 2 residual degrees of
      freedom against the 2-point's zero.
    sota_delta: >-
      Not applicable and not claimed. Nothing in this batch advances or bears on
      any cryptanalytic state of the art. Claim tier TOY, hard ceiling.
    lower_cost_alternative_not_taken: >-
      Measuring the real pair's last-block disagreement rate from
      a79e4f/stage_1.per_trial_S, the file Part A already opens. One
      np.count_nonzero. It decides the SHAPE test.

  usable_v1_sizing_law_exists: partial_and_scoped
  usable_v1_sizing_law_statement: >-
    YES AT k <= 5 AND NO AT k = 17. At k=5, on the real object, on two
    independent shards, over a 4x range in T, the >= 3-rung ladder gives
    se_paired ~ T^(-0.518 +- 0.073) (shard 5000) and T^(-0.483 +- 0.055) (shard
    8002) with residual RMS 0.051 and 0.038 -- exactly the "low-k cells plus a
    >= 3-rung ladder exponent with its measured scatter" DEC-20260817-2b638b
    made binding, and the batch delivers it and states it nowhere. The
    T^(-0.35) concern that blocked V1 was a k=17 and null-object fact and does
    not apply here. TWO BINDING CONDITIONS: (i) it does NOT transfer to the
    family's load-bearing order m=17, where the same ladders give 0.4734 +-
    1.4544 and 0.0115 +- 0.7415; (ii) a slope is not a sizing -- the level's own
    draw-to-draw spread at k=5 is D_RMS(5) = 0.124859 in alpha units, from n=2.
    A FIFTH DEFERRAL OF A k <= 5 V1 WOULD NEED A REASON THIS TASK DOES NOT
    SUPPLY. A k=17 V1 is still unsized.
  lossy_projection_check_on_the_low_k_upgrade: >-
    PASSED AND UNREPORTED BY THE BATCH. Mean |z_paired| over all 16 committed
    real arrays is 1.0308 / 0.9188 / 0.7316 / 0.7988 at k = 2 / 5 / 10 / 17 and
    the maximum is 2.9365 at k=5 against 2.0054 at k=17. Moving the instrument to
    k=5 does not cost detection power on any committed array. Separately and
    already known: no |z| reaches 3 at any k at these T.

  scope_limits:
  - Everything here is scoped to PS-R3 reduced parameters (n=7187, n_e=56,
    n_2=128, dup=1, N=7168, k 2..26, m=17, N_JACK_BATCHES=200), one defect class
    (V3, last-block-window-read-early), one injection point, shards 5000, 6000,
    8001, 8002, the named trial ranges and windows, and this batch's budget.
    Nothing bears on HQC's IND-CCA security, its decoding-failure rate,
    assumption A17 or A5, or any standardized parameter set.
  - D_RMS(k) is a SCALE FROM n = 2 CONTRASTS, one per shard, measured on the
    FRESH windows only. Every normalised statement in OBJ-1 inherits that limit,
    and applying it to the historical cells assumes transfer across procedures.
    No confidence interval is computable from it and none is claimed.
  - My recomputation of the two gate-failed historical cells is conditional on
    batch.yaml's mapping being correct. It is offered as a diagnostic about the
    ROUTE'S DECIDABILITY, never as a substitute for the gate, and I apply no
    branch to it.
  - My re-coupled null is a minimal correction of one parameter of the batch's own
    construction, calibrated to a rate measured at T=5,000 on shards 5000 and
    6000. It shows the band DEPENDS on that rate and that the SHAPE failure is
    caused by it; it does not claim to be the right null for the real object,
    whose variance at k >= 10 exceeds it by 1.9x-2.2x.
  - The 114-pair uniqueness search covers the 19 arrays in the three named source
    files plus the eight fresh windows. It does not cover arrays committed
    elsewhere in the repository.
  - I hold no authority to change any record status, promote evidence, apply the
    reading rule, name a branch, or move a claim tier.

  premature_closure_assessment: >-
    This batch FORECLOSES NOTHING and I decline to foreclose anything. The
    obstruction is named and measured (a noise-normalised deviation of order 1 at
    every k in 2..26, from an n=2 real-object scale), localised to a property of a
    2-point log-ratio of a jackknife SE rather than to the shards, the regimes or
    HQC, and correctable at zero decoder cost. A count of six blind controls is a
    fatigue report about the search, not a statement about the problem. What
    should be retired is WIDER than my predecessor said: the 2-point local
    exponent as a directional instrument at EVERY k, not only at k=17, because
    moving to k=5 changes the units and not the resolvability -- and the
    replacement is already measured and already dominant (the >= 3-rung ladder at
    k=5). SYMMETRICALLY, THIS BATCH UNDER-CLAIMS THREE TIMES: it contains, in
    committed artifacts, (1) a usable k=5 real-object sizing law, (2) the free
    check showing the low-k upgrade is not lossy for the campaign's own detection
    statistic, and (3) the diagnosis that its own SHAPE failure is a
    one-parameter miscalibration whose calibration datum it already read. None is
    stated.

  next_concrete_action: >-
    Re-run Part B with the arms' last-block disagreement rate set to the MEASURED
    0.1094 rather than the maximal 0.434647 -- base ~ Binomial(55,p), b0 ~
    Bernoulli(p), b1 = b0 except on an independent fraction c = r/(2p(1-p)) =
    0.251698 of trials where b1 is redrawn Bernoulli(p), which preserves each
    arm's Binomial(56,p) marginal EXACTLY and the forced zero paired difference
    EXACTLY -- and report the SHAPE statistic, every band and unpaired_over_paired
    beside the committed values. ONE LINE, ZERO DECODER CALLS, ~13 CORE-SECONDS.
    It moves the SHAPE statistic to 10.25 / 9.04 / 9.25 (inside the real range at
    all three k), widens every band by 1.26x-1.68x, and converts this campaign's
    sixth blind control into its first calibrated one at the order where
    adjudication happens. Run it in the same task as the two free repairs it
    enables: a reconstruction gate at the comparator's own precision plus the
    114-pair uniqueness search, and every cell deviation and contrast reported in
    units of D_RMS(5) beside its absolute value. PRE-STATED FALSIFICATION OF MY
    OWN HEADLINE: draw a third and fourth disjoint T=10,000 window per shard above
    index 75,000; if D_shard(k)'s spread collapses, D_RMS is an n=2 artifact and
    my normalised reading is wrong.

  independence:
    independent_session: true
    is_producer: false
    read_sibling_validator_directory: false
    conferred_with_sibling_validator: false
    correlated_judgement_disclosure: >-
      The sibling Validator TASK-20260817-cddd45 runs concurrently on the SAME
      MODEL FAMILY as this Red Team session. Any agreement between the two
      reports is CORRELATED SAME-MODEL JUDGEMENT and must not be recorded as
      distinct-model corroboration or as any form of quorum. What is not
      correlated is what each reviewer verified with an instrument it built
      itself.

  inference:
    runtime: claude_code
    native_authenticated_session: true
    requested_policy: review-adversarial
    requested_reasoning_effort: xhigh
    this_sessions_actual_resolved_model_id: claude-opus-5[1m]
    this_sessions_actual_resolved_model_id_source: >-
      GENUINE SELF-REPORT from this session's own runtime system context. Not
      read from any configuration file and not copied from any committed binding
      target.
    committed_binding_target_read_for_reference_only: >-
      orchestration/model-bindings.yaml was NOT written by this session and is
      NOT the source of the field above. The two are recorded separately by
      design; the working copy of that file may carry another session's
      uncommitted edits and is therefore not evidence of anything here.
    reasoning_effort_source: >-
      .claude/agents/red-team.md frontmatter, derived from roles.yaml
      default_policy review-adversarial -> model-policies.yaml reasoning_effort
      xhigh. Confirmable with tools/check_runtime_bindings.py --list.
    fallback_allowed: false
    fallback_used: false
    degraded_allowed: false
    degraded_requirements: []
    independent_session_required: true
    amazon_bedrock_selected_configured_probed_contacted_or_used: false
    amazon_bedrock_note: >-
      AWS_BEARER_TOKEN_BEDROCK is present in the environment and
      CLAUDE_CODE_USE_BEDROCK is unset. Bedrock was not selected, configured,
      probed, contacted or used. Refused under AGENTS.md rule 16.

  execution_record:
    experiment_runs_authorized: 1
    sampling_probe_executions: 1
    sampling_probe_wall_seconds: 12.6
    sampling_probe_constructions: 2
    sampling_probe_replicates_per_construction: 200
    decoder_calls_made: 0
    decoder_tripwires_installed_by_me: 2
    pinned_module_sha256_verified_by_me_before_and_after: 3
    deterministic_arithmetic_evaluations: 5
    review_wall_clock_seconds_approx: 3300
    review_wall_clock_authorized: 1800
    review_wall_clock_note: >-
      OVER THE AUTHORIZATION AND REPORTED AS MEASURED RATHER THAN TRIMMED. This
      is reviewer session time, which this campaign's debit convention never
      charges against campaign_budget.total_wall_clock_seconds; it is disclosed
      because under-reporting it would be the same defect named in OBJ-9.
    machine: 14 cores, shared with a concurrent Validator session
    memory_gb_authorized: 4
    pinned_modules_edited: 0
    producer_artifacts_edited: 0
    files_written: 2
    commits_made: 0
    ledger_records_written: 0
    status_changes_made: 0
    reading_rule_applied: false
    branch_named: false
    predicate_evaluated: false

  write_scope_note: >-
    The committed task card, the committed handoff, the committed
    dispatch_queue.json and batch.yaml's
    review_write_scope_layout_is_declared_once_and_governs all name
    coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/reviews/TASK-20260817-785c5c/
    with two artifacts. This batch's dispatch orientation named the SAME path, so
    unlike TASK-20260817-94c89e there is no discrepancy to flag. Both declared
    paths are written, red_team_probe.json unconditionally. Nothing else was
    written anywhere in the repository.

  artifact_paths:
  - coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/reviews/TASK-20260817-785c5c/red_team_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/reviews/TASK-20260817-785c5c/red_team_probe.json

  inputs_read:
  - coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/batch.yaml
  - coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/tasks/TASK-20260817-b4b6e4/ (all twelve artifacts, at 48d384e0e)
  - coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/archives/TASK-20260817-e50761/snapshot-receipt.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/reviews/TASK-20260817-94c89e/red_team_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/cross_regime_arms_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/reviews/TASK-20260814-a49f1c/red_team_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
  - ledger/handoffs/TASK-20260817-785c5c.yaml
```

*Red-team record. I wrote only inside this directory, committed nothing, and
hold no authority to change any record's status, promote evidence, apply
batch.yaml's reading rule, name a branch, or move a claim tier. Adjudication
belongs to TASK-20260817-0c342f.*
