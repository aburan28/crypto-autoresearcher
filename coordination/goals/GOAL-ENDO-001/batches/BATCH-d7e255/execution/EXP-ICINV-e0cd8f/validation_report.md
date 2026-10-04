# Validation report — EXP-ICINV-e0cd8f v1, TASK-20260811-d9d01e

```yaml
validation_report:
  id: VAL-20260811-d9d01e
  task_id: TASK-20260811-d9d01e
  role: validator
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  experiment_id: EXP-ICINV-e0cd8f
  contract_version: 1
  recorded_at: '2026-08-11'
  snapshot_commit_validated: 904841f89f3ee74bf3d8ac757e8c026b450134c7
  branch: claude/ecdlp-endomorphism-analysis-4m2w3z
  claim_tier: toy
  run_ids:
    - RUN-ICINV-e0cd8f-m3class
  verdict: passed
```

Read in full before this report: `experiments/EXP-ICINV-e0cd8f/specification.yaml`
(the frozen contract), `ledger/handoffs/TASK-20260811-d9d01e.yaml`,
`coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-ICINV-e0cd8f/execution_report.md`,
`harness/exp_icinv_e0cd8f.py`, `harness/semaev.py`, `harness/isogeny_class.py`,
`AGENTS.md`, `agents/validator.md`. Validated at the Coordinator's own
snapshot commit `904841f8`, HEAD of the named branch — confirmed by
`git rev-parse HEAD` and `git status --short` (clean) before any check below.
Nothing here reads the working tree as evidence; the snapshot commit is the
receipt.

**A `passed` verdict here means the receipt is admissible evidence of what it
computed. It does not decide what `CLASS-VARYING` means for `H-ICINV-d5e351`,
`RQ-ICINV-475b5e`, or `GOAL-ENDO-001` — that is a later Coordinator act, and
this report deliberately renders no opinion on it.**

---

## 1. Snapshot / binding checks

- `git rev-parse 76a48ff3` = `76a48ff3d852473e743741e768319d9721124088`,
  matching both the execution report's stated "task starting commit" and
  `manifest.yaml`'s `code.commit`. No transcription mismatch.
- `git diff 76a48ff3 904841f8 -- harness/semaev.py harness/isogeny_class.py`
  is **empty (0 lines)** — both files are byte-identical between the dispatch
  commit and the snapshot commit. **CONFIRMED: neither file was edited**,
  independent of the executor's own claim.
- `harness/exp_icinv_e0cd8f.py` is a genuinely new module. `grep -n
  "build_factor_base\|measure_s3_decomposition"` finds only its own docstring
  *mentioning* those names to explain why they are absent — no call site, no
  reproduction of their logic. It imports only `s3_expr, s4_expr, x1, x2, x3`
  (bare polynomial definitions) and `isogeny_classes, class_census` from the
  existing modules — never `build_factor_base` or `measure_s3_decomposition`.
  `grep -n "f_V\|fV"` in the module likewise finds only comments explaining
  the prohibition; no ideal in the module's own code ever constructs an `f_V`
  factor-base membership polynomial. **The invalidation rule "any f_V in any
  computed ideal" and the source-constraint rule are both independently
  confirmed, not merely taken from the report.**
- Manifest source-hash pinning verified against git blobs directly (not
  against the manifest's own self-report): `git show 76a48ff3:<path> |
  sha256sum` for `harness/__init__.py`, `harness/isogeny_class.py`,
  `harness/runner.py`, `harness/semaev.py`, `harness/toycurve.py`, and `git
  show 904841f8:harness/exp_icinv_e0cd8f.py | sha256sum` for the new module —
  **all six hashes match `manifest.yaml`'s `code.source.files` exactly.**
- `python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-e0cd8f
  --strict` (run myself, not read from the report): `1 pinned, 0 unpinned, 0
  unreadable, of 1 run manifest(s) in scope`, exit 0. Matches the report
  verbatim.
- Only one run directory exists under `experiments/EXP-ICINV-e0cd8f/runs/`
  (`RUN-ICINV-e0cd8f-m3class`); no orphaned dry-run artifacts leaked into the
  committed tree. `git show 904841f8 --name-only` touches exactly the 15
  required artifacts + `command.txt` + the harness module + the execution
  report — no scope creep.
- `tools/validate_ledger.py` on the current tree: `OK: validated 5629
  records, no new violations` (whole-repo sanity check; not experiment-scoped
  but confirms this snapshot introduces no ledger-schema regressions).

---

## 2. SR1 — support gate, independently recomputed

Not taken from `support-derivation.json` alone. I re-derived the generic S_3
monomial support **from the raw formula in the spec, with my own sympy
session**, independent of any harness code:

```
S3 = (x1-x2)**2*x3**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3 + ((x1*x2-a)**2 - 4*b*(x1+x2))
sympy.Poly(sympy.expand(S3), x1,x2,x3,a,b).terms()  ->  13 terms, exactly:
  x1^2x2^2, x1^2x2x3, x1^2x3^2, x1x2^2x3, x1x2x3^2, x1ax2, x1ax3, x1(4b term),
  x2^2x3^2, x2ax3, x2(4b), x3(4b), a^2
```
13 terms confirmed independently — matches the spec's derived 3+4+1+3+2=13.

Then read directly from the run's own `support-derivation.json` and
`per-curve-invariants.json` (two separate files, cross-checked against each
other): `symbolic_generic_support=13`, `a0_support=9`, `b0_support=10`,
`derivation_matches_13_9_10=True`. Independently tallied
`per-curve-invariants.json`'s `curves[i].m3.s3_support` for all 138 class
members directly (not via the file's own summary field): `{13: 138}`, zero
exceptions. **SR1 independently confirmed both symbolically and per-curve.**

---

## 3. SR2 — census gate, independently recomputed

`class-census.json`: `p=4001, t=30, observed_member_count=138,
census_agrees=True`, `predicted_weighted=138.0`.

I did **not** trust `harness/isogeny_class.py`'s own
`hurwitz_class_number` implementation for this. I wrote an **independent
Python implementation from scratch** of the weighted Hurwitz–Kronecker class
number by reduced-form enumeration, and ran it on `N = 15104 = 4*4001 - 30^2`:

```
f=1,  D=-15104, h=72, hw=72.0
f=2,  D=-3776,  h=36, hw=36.0
f=4,  D=-944,   h=18, hw=18.0
f=8,  D=-236,   h=9,  hw=9.0
f=16, D=-59,    h=3,  hw=3.0
TOTAL H(15104) = 138.0
```
This matches both the reported `predicted_weighted=138.0` **and** the spec's
independently-stated `true_volcano_levels_reference` `{0:3,1:9,2:18,3:36,4:72}`
level-by-level (my `f=16,hw=3` ↔ level 0; `f=8,hw=9` ↔ level 1; `f=4,hw=18` ↔
level 2; `f=2,hw=36` ↔ level 3; `f=1,hw=72` ↔ level 4). **Independently
confirmed via a from-scratch implementation, not by re-running the harness's
own function.**

I additionally brute-force verified `trace_of_frobenius(4001, a, b) = 30` by
direct character-sum point counting (my own implementation, not
`harness/isogeny_class.py`'s) on 8 random members drawn from
`class-census.json` — all 8 matched exactly.

**SR2 independently confirmed at three levels: class-number formula
recomputed from scratch, per-curve trace recomputed from scratch, and
`class-census.json`'s own reported figures cross-checked against both.**

Confirmed also: `j=0` and `j=1728` are absent from all 138 members and no
member has `a=0` or `b=0` (T4), matching the spec's stated prediction.

---

## 4. Core verdict — recomputed directly from the raw per-curve arrays

Tallied `curves[i].m3.<field>` myself, directly from
`per-curve-invariants.json` and `control-set-invariants.json` (not from
`verdict.json`'s own summary), for all seven `PRIMARY_FAMILIES`:

| family | class (my tally) | control (my tally) |
|---|---|---|
| `s3_support` | `{13: 138}` | `{13: 138}` |
| `singular_locus_dim` | `{0: 138}` | `{0: 138}` |
| `singular_locus_degree` | `{6: 138}` | `{6: 138}` |
| `regularity` | `{5: 138}` | `{5: 138}` |
| `elimination_poly_degree` | `{3: 138}` | `{3: 138}` |
| `elimination_factor_partition` | `{(1,1,1): 66, (1,2): 72}` | `{(1,1,1): 26, (1,2): 63, (3,): 49}` |
| `betti_table` | one shared table, `138` | same shared table, `138` |

Every sum is exactly 138. This is **bit-for-bit identical** to
`verdict.json`'s `primary_family_comparison` block and to the execution
report's §4 table. Six of seven families constant on both sets; the
`elimination_factor_partition` family is the sole survivor of the F5
withdrawal check, with the 66/72 split in the class and the 26/63/49 split in
the control, confirmed by direct tally, not by reading the run's own claim.

### Deviating-curve set identity

`verdict.json:deviating_curves_by_family.elimination_factor_partition` lists
66 curves. I independently recomputed the set of class curves whose
`m3.elimination_factor_partition == [1,1,1]` directly from
`per-curve-invariants.json`: **66 curves, and the two sets of `(a,b)` pairs
are set-equal** (`dev_keys == partition_111 == True`).

---

## 5. Backend cross-check — recomputed, not sampled

`backend-crosscheck.json` has exactly 66 rows. I confirmed:
- `{(a,b) for row}` == the same 66 deviating `(a,b)` pairs from §4, exactly
  (not a superset, not a subset).
- `carries_claimed_difference == True` on all 66 rows.
- `m2_agrees` is `True` on **literally all 66 rows** (`set(m2_agrees for all
  rows) == {True}`) — checked over the full array, not a sample.
- `order_agrees` is `True` on **literally all 66 rows**, same method.

`meets_minimum_20: true` and `includes_all_deviating_curves: true` both
verify against the raw data, not just as asserted fields.

---

## 6. Independent hand-built re-derivation (no harness code at all)

To go beyond re-tallying the harness's own output, I wrote my own Singular
driver **from scratch** (new script, not importing
`harness/exp_icinv_e0cd8f.py`, using only the polynomial formula written out
in the frozen contract) and ran it against both installed backends (Singular
4.3.2 and Macaulay2 1.22, both present in this environment) on three curves:
one class `(1,1,1)` deviant `(a,b)=(460,2974)`, one class `(1,2)` modal
`(2133,265)`, and one control-only `(3,)` `(2423,845)`.

Result: **every single reported number reproduces exactly** — `s3_support=13`,
`singular_locus_dim=0`, `singular_locus_degree=6`, `elimination_poly_degree=3`,
`elimination_factor_partition` matching `(1,1,1)`/`(1,2)`/`(3,)` respectively,
and the **same Betti table** `(i=0,j=0,β=1),(i=1,j=3,β=3),(i=1,j=4,β=1),
(i=2,j=5,β=2),(i=2,j=6,β=2),(i=2,j=7,β=1),(i=3,j=8,β=2)` on all three curves,
identical to what the run reports for all 276. This is the strongest check
available short of re-running the whole 138+138-curve batch: **the numbers
are not fabricated and are reproducible by an implementation that shares no
code with the one under review.**

I also confirmed the Betti-table shape is exactly what the ideal's generator
degrees predict: `S_3` is degree 4 in `(x1,x2,x3)` (my own sympy count of the
generic expansion), its three partials are degree 3, and after `x0`-homogenization
to each generator's own top degree the resolution's first syzygy module
carries 3 generators at internal degree 3 (`β_{1,3}=3`) and 1 at degree 4
(`β_{1,4}=1`) — exactly the counted generator degrees. This is a sanity check
against the specific corruption mode disclosed in D1 (see §9), not a generic
plausibility check.

---

## 7. Gauge recheck — recomputed for both m3 AND m4, class AND control

`gauge-recheck.json`'s own `summary.all_agree` field is computed in the
harness from `m3_agrees` alone (confirmed by reading
`harness/exp_icinv_e0cd8f.py:run_experiment`'s
`class_gauge_fail`/`control_gauge_fail` construction — it only inspects
`g["m3_agrees"]`). I independently tallied **both** `m3_agrees` and
`m4_agrees` across **all 276 rows** (138 class + 138 control) directly from
the raw JSON:

- `m3_agrees == False` count: class 0, control 0 (matches the summary).
- `m4_agrees == False` count: class 0, control 0 (**this is not certified by
  the summary field itself**, which only covers m3 — I confirmed it directly
  from the per-row data since the field is present on every row).

**0/276 failures on both m3 and m4, both sets, confirmed by direct count, not
by trusting the aggregate `summary` object alone.**

Additionally confirmed why this is expected rather than a weak check: the
gauge transform `(a,b) -> (u^4 a, u^6 b) mod p` is exactly a Weierstrass
change of variables `(x,y) -> (u^2 x, u^3 y)` — i.e. an **F_p-isomorphism of
the same curve**, not a different curve. Any correctly-implemented geometric
invariant of the curve must be gauge-invariant by construction; 0 failures is
the expected outcome of a correct implementation and would not, by itself,
catch e.g. a coordinate-dependent bug that happened to commute with this
specific substitution (a weaker but real limitation of gauge-recheck as a
control, inherent to the contract's own design, not an executor defect).

---

## 8. Koszul indicator — confirmed, and its actual scope assessed

`koszul-indicator.json` and `per-curve-invariants.json` both independently
tallied: `codim_hom=3` and `num_generators=4` on **every** one of 276 rows
(class + control), so `koszul_degeneration=False` everywhere
(`class_all_koszul=False`, `class_any_koszul=False`,
`control_all_koszul=False`) — **confirmed directly, not from the summary
alone.**

**On relevance to the varying family (the question this task specifically
asked about):** the Koszul indicator, per the contract's own C-KOSZUL/F3
design, only bears on whether a **constant** Betti table is a trivial
consequence of the Jacobian generators forming a regular sequence — it says
nothing about whether the `elimination_factor_partition` variation is real or
an artifact. Those two computations are structurally independent in the
harness: the Betti table/Koszul test runs on the **homogenized** ideal in
`F_p[x0,x1,x2,x3]`, while the elimination polynomial is computed on the
**un-homogenized affine** ideal by `eliminate(Jaff, x1*x2)` in
`F_p[x1,x2,x3]` — a different ring, a different computation, with no shared
intermediate object. So a Koszul-adjacent defect in the homogenized-ideal
resolution code could not silently manufacture the elimination-partition
variation, and the indicator, correctly, is not offered by the run as
evidence either way for that family. The controls that actually bear on
whether the variation is real are C-GAUGE, C-BACKEND, and C-ORDER — all three
independently confirmed passing in §§6–7 and below. This is not a defect; it
is worth stating explicitly because the falsification criterion's F3 language
could be misread as covering the varying family too, and it does not.

---

## 9. D1 disclosure (`**` vs `^`) — assessed for residual symptoms, not just re-read

I confirmed independently (not from the report's prose) that Macaulay2 does
in fact parse `**` as its tensor-product operator rather than raising an
error: `x1**2` on a live M2 session in this environment returns a `Matrix`,
not a polynomial — i.e. the disclosed defect class is real and would have
been silent, not a crash.

I then checked the **current, committed** code and its output for any
residual symptom of that defect class:

- `build_m3_m2_script`'s `m2()` helper and `_to_singular` both apply
  `.replace("**", "^")` before any exponent reaches the generated script
  text. I generated the actual M2 script for a real curve
  (`build_m3_m2_script(460, 2974, 4001)`) and confirmed `"**" not in script`
  — the fix is present in the code actually executed, not merely described.
- Scanned all 66 `backend-crosscheck.json` rows' `m2_raw` fields: **zero**
  rows have `elimination_ideal_size in (0, None)` or a missing
  `elimination_poly_degree` — i.e. the second half of D1 (omitted elimination
  computation) also shows no residual symptom in the real run.
- All 66 `m2_raw.betti_entries` shapes are the single, uniform, mathematically
  sane table from §4/§6 — not degenerate, not exploded in degree, and
  identical to Singular's independently-computed shape on every row
  (`m2_agrees: True` on all 66, §5). A tensor-product corruption would not
  plausibly reproduce a Singular-matching Betti table by accident.
- `regularity_m2_builtin - regularity(from betti)` is **exactly `+1` on all
  66 rows**, consistently — the disclosed D2 convention offset, not a
  sporadic disagreement, which is the signature of a real, systematic
  convention difference rather than a residual bug.
- Zero nonzero `returncode`s anywhere in the entire run (class m3/m4, gauge
  m3/m4, control m3/m4, backend-crosscheck m2, alt-order Singular) — checked
  programmatically across every JSON artifact.

**No symptom of the pre-fix defect class survives into the committed run's
artifacts.** The D1 disclosure is credible and, on inspection, complete: it
correctly identifies a real M2 parsing gotcha, and the current code and every
downstream artifact are consistent with the disclosed fix having actually
been applied before `RUN-ICINV-e0cd8f-m3class` started.

---

## 10. Manifest hash pinning and budget accounting — reconciled against raw data

- Wall time reconciliation: manifest `wall_seconds=855.475139`. Raw-result's
  own `class_wall_seconds=392.44` + `control_wall_seconds=369.35` = `761.80s`.
  Sum of `backend-crosscheck.json`'s 66 `m2_raw.wall_seconds` values =
  `87.06s`. `761.80 + 87.06 = 848.85s`, leaving `≈6.6s` for SR1/SR2 gates, 66
  alt-order Singular calls, and JSON writes — all consistent with plausible
  per-call costs (sub-100ms Singular calls, fast sympy support checks). **No
  discrepancy.**
- `855.475s / 3600 = 0.2376` CPU-hours (single-threaded) — matches the
  claimed "~0.24 of 6 CPU-hours" exactly.
- `855.5s` of `7200s` budget (11.9%), `1` of `8` maximum runs, both well
  inside budget; SR6 not triggered.
- **Gap, not a defect but worth flagging:** neither `manifest.yaml` nor any
  other artifact records an actual measured peak-memory figure (no RSS
  sample, no `resource.getrusage`, no `/usr/bin/time -v` capture anywhere in
  the run tree). The execution report's "peak memory: well under 8 GB (no
  OOM, no `RLIMIT_AS` trip)" is an **inference from absence of failure**, not
  a measurement — a materially weaker claim than it reads. AGENTS.md's
  Artifact Policy lists "resource measurements" among required per-run
  records; this run has none for memory. It does not affect the verdict
  (the computations here are small — degree-≤4 ideals in 4 variables over a
  4001-element field — and there is no evidence of memory pressure), but a
  Coordinator citing this run should not treat "well under 8GB" as a measured
  fact.
- `environment.json` (`sympy 1.14.0`, `pyyaml 6.0.1`, `Linux-6.18.5-fc-v20`,
  Python `3.11.15`) matches this validation session's own environment
  exactly (`python3 -c "import sympy; print(sympy.__version__)"` → `1.14.0`
  here too), consistent with re-execution being possible in the same
  container.

---

## 11. m=3 vs m=4 consistency and tail checks — recomputed

- `S_4` support tally (my own count from raw `curves[i].m4.s4_support`):
  class `{227: 136, 225: 1, 210: 1}`, control `{227: 137, 225: 1}` — matches
  the execution report exactly. Both class outliers `(1509,1006)` and
  `(441,294)` confirmed gauge-stable (`base==gauge` on `s4_support`) directly
  from `per-curve-invariants.json`.
- `singular_locus_dim`/`singular_locus_degree` at m=4: constant `{2:138}` and
  `{60:138}` on both sets — confirmed by direct tally.
- No overlap between the class and control `(a,b)` sets (`class_set &
  control_set == set()`); no duplicates within either set; `30 not in
  drawn_traces`; `len(drawn_traces)==92`. Control construction rule
  ("traces OTHER than t=30, excluding supersingular") independently
  confirmed on the raw JSON, not asserted.
- Zero curves with `singular_locus_is_unit_ideal=True` or
  `elimination_empty=True` anywhere in either set — checked programmatically
  across all 276 rows, matching §8b of the execution report.

---

## 12. The `(3,)`-absence question — independently explained, and the run record does not explain it

This is squarely an "is the number right and what does it actually measure"
question, not an interpretation of what it means for `H-ICINV-d5e351` — I
answer it at that level only.

**The elimination polynomial computed here IS (up to a unit scalar) the
classical 2-division polynomial `x^3 + a x + b`.** I verified this
independently, without using any harness code, by factoring `x^3+ax+b` over
`F_4001` directly with sympy for the same three sample curves in §6 and
matching the reported partition exactly (`(1,1,1)`/`(1,2)`/`(3,)`), then
extended the check to 15 additional randomly-sampled class curves — **0
mismatches out of 15** — confirming this is a general algebraic identity, not
a coincidence on the samples in §6. This is elementary but worth being
precise about: it means `elimination_factor_partition` is literally recording
how many of the three F_p-rational x-coordinates of the 2-torsion subgroup
`E(F_p)[2]` exist — `(1,1,1)` = all three rational (full 2-torsion, i.e.
`E(F_p)` is non-cyclic), `(1,2)` = exactly one rational (E(F_p) cyclic with
even order), `(3,)` = none rational (`#E(F_p)` odd).

Given that, the class's shared group order is `N = p+1-t = 4001+1-30 = 3972 =
2^2*3*331`, which is **even**. An even group order forces at least one
rational 2-torsion point, which algebraically **excludes** partition `(3,)`
for every curve of trace 30 — independent of any measurement, this is forced
by elementary group theory once the order's parity is known. I confirmed this
is not merely a class-level regularity by checking 15 random control-set
curves against their own independently-recomputed trace (brute-force point
count, my own code): **every control curve with `partition=(3,)` has odd
group order, and every even-order sampled control curve has partition
`(1,1,1)` or `(1,2)`, with zero exceptions in the 15-curve sample.**

**So: yes, the `(3,)`-absence in the class is expected, not merely observed —
it follows immediately from `N=3972` being even, which is itself an isogeny
invariant (isogenous curves share `#E(F_p)`). Neither `execution_report.md`
nor `verdict.json` states this.** This is not a contract violation — the
executor was explicitly instructed *not* to interpret results — but it is
something the Coordinator should have on hand before writing an evidence
record: the `elimination_factor_partition` "variation" reduces, at the level
of what is actually being measured, to the classical and well-documented fact
that isogenous curves share group *order* but not group *structure*
(cyclic vs. non-cyclic 2-part). I state this as a verified mathematical fact
about what the measured quantity *is*; I take no position on what it implies
for closing or not closing any axis of `RQ-ICINV-475b5e`.

---

## 13. Falsification/invalidation rules checked against the frozen contract

- F1 (support/census failure): did not occur — both gates passed and are
  independently confirmed above.
- F2 (control equally constant on every family the class is constant on):
  the run's own logic only evaluates F2 language on the `CLASS-INVARIANT`
  branch; since the verdict is `CLASS-VARYING`, F2's caution text is
  correctly not emitted. Independently confirmed: on the one varying family
  the control set is *not* equally constant either (it has 3 distinct values
  vs. the class's 2), so an F2-style objection would not have applied to that
  family in any case.
- F3 (Koszul degeneration explains constancy): `koszul_degeneration=False`
  everywhere (§8) — F3 does not fire; correctly not claimed.
- F4 (order-dependence): `order_agrees=True` on all 66 cross-checked curves
  (§5) — F4 does not fire.
- F5 (claimed difference must survive gauge + backend): confirmed via §5 and
  §7 that the sole varying family survives both, independently, not by
  reading `withdrawn_families: []` alone.
- F6 (planned negative — not applicable, verdict is `CLASS-VARYING` not
  `CLASS-INVARIANT`).
- No `f_V` in any computed ideal (checked in §1), no edit to the two
  protected modules (checked in §1), full hash pinning (checked in §1 and
  §10), no monomial-order dependence in a reported order-independent quantity
  (checked in §5), no claimed difference without both gauge and backend
  survival (checked in §5, §7), no reported quantity from an incomplete
  enumeration (census 138/138, §3). `grep -ni
  "p.value|p_value|pvalue|permutation|null.object|stddev|std_dev|variance("`
  over `harness/exp_icinv_e0cd8f.py` returns nothing — **no forbidden
  statistic anywhere in the module that produced these artifacts.**

None of the frozen contract's `invalidation_rules` are triggered.

---

## limitations

```yaml
  limitations:
    - >-
      No peak-memory measurement exists anywhere in the run's artifacts
      (manifest.yaml, raw-result.json, or elsewhere); the execution report's
      "well under 8GB" claim is an absence-of-failure inference, not a
      measured figure. Does not affect the verdict at this toy scale but
      should not be cited as a measurement.
    - >-
      CPU-hours (~0.24 of 6) is derived from wall-clock time under a
      single-threaded assumption, not from a direct CPU-time measurement
      (no os.times()/getrusage capture). Plausible for these subprocess
      calls but unverified directly.
    - >-
      gauge-recheck.json's own summary.all_agree field is computed from
      m3_agrees only in the harness code; m4_agrees is present per-row but
      not aggregated into any summary boolean. I independently tallied it
      (0/276 failures) but a reader trusting only the summary object would
      not see m4 covered by it.
    - >-
      The run record does not identify that the elimination polynomial
      equals the classical 2-division polynomial x^3+ax+b, nor that the
      class's (3,)-absence follows immediately from its shared group order
      3972 being even. Both are independently confirmed true in this report
      (section 12) and are relevant context for anyone about to interpret
      CLASS-VARYING, though establishing that context was outside the
      executor's assigned scope (no-interpretation instruction) and outside
      this report's own mandate to render RQ-level judgment.
    - >-
      Not independently re-executed end-to-end (would re-spend ~855s of
      compute and is not required by the validator role); instead
      recomputed every reported quantity from the raw per-curve JSON arrays
      directly, cross-checked SR1/SR2 from first principles with
      independent from-scratch implementations, and reproduced the full
      per-curve invariant set for 3 sample curves (one from each
      partition class) with a hand-written driver sharing no code with
      harness/exp_icinv_e0cd8f.py, run against the same two installed
      backends.
```

## artifact_paths

```yaml
  artifact_paths:
    - experiments/EXP-ICINV-e0cd8f/specification.yaml
    - ledger/handoffs/TASK-20260811-d9d01e.yaml
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-ICINV-e0cd8f/execution_report.md
    - harness/exp_icinv_e0cd8f.py
    - harness/semaev.py
    - harness/isogeny_class.py
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/manifest.yaml
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/support-derivation.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/class-census.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/per-curve-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/control-set-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/gauge-recheck.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/koszul-indicator.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/backend-crosscheck.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/backend-provenance.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/verdict.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/raw-result.json
```

## Terminal verdict

```yaml
  verdict: passed
```

**Rationale.** Every required artifact is present, correctly bound by
sha256 to its declared source at the snapshot commit, and internally
consistent. SR1–SR7 all independently reconfirmed from raw data, not from the
report's own narration. The core `CLASS-VARYING` verdict, the exact 66/72 and
26/63/49 splits, the shared six-family constancy, and the shared Betti table
all recompute bit-for-bit from `per-curve-invariants.json` and
`control-set-invariants.json` directly. The backend cross-check set is
exactly the deviating set, and agreement is total across all 66 rows, checked
in full, not sampled. Gauge recheck is 0/276 failures on both m3 and m4, both
sets, checked in full. The disclosed D1 defect is real (confirmed by testing
M2's `**` behavior myself) and shows no residual symptom anywhere in the
committed run's artifacts. Hash pinning, dirty-tree state, budget, and
`harness/semaev.py`/`harness/isogeny_class.py` non-modification all verify
independently against git and the raw JSON. No invalidation rule is
triggered. The gaps noted above (unmeasured memory/CPU, the unexplained
`(3,)`-absence, the Koszul indicator's scope) are limitations to carry
forward, not defects that make the receipt inadmissible.

This report supports exactly one claim: **this run's own numbers hold up
under independent, from-scratch recomputation, and its artifacts are what
they say they are.** It does not evaluate, and takes no position on, whether
`CLASS-VARYING` on these seven families at this one toy-scale class
constitutes evidence for or against any reading of `RQ-ICINV-475b5e`, whether
it should promote `min_{E'~E} C(E')` as a campaign target, or how heavily the
2-division-polynomial identification in §12 should weigh on that judgment —
those are Coordinator acts.
