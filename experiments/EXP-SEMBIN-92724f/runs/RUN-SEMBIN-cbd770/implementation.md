# Implementation notes — RUN-SEMBIN-cbd770 of EXP-SEMBIN-92724f

Task `TASK-20260913-80bae1`. Executor role: **observations only**. No ledger
record was written, no hypothesis status was changed, and no research conclusion
is drawn here.

> **Placement note.** `docs/evidence-and-reproducibility.md` puts
> `implementation.md` at the experiment root. That path is **outside this task's
> declared write scope** (`experiments/EXP-SEMBIN-92724f/code/` and
> `experiments/EXP-SEMBIN-92724f/runs/RUN-SEMBIN-cbd770/`), so these notes live
> inside the run directory instead. Recorded rather than resolved silently.

## What was built

Nine modules under `experiments/EXP-SEMBIN-92724f/code/`:

| file | role |
| --- | --- |
| `binary_field.py` | **vendored byte-identically** from `EXP-SEMBIN-354a75`; not edited |
| `image_enum.py` | group coordinatisation, exact convolution and multiset DP, brute-force cross-check, fibre summaries |
| `families.py` | typed-family construction and the input guards that reject invalid draws |
| `cost_model.py` | Semaev eqs. (15)–(16), GG substitutions, Table 3, symbolic `c'`, surfaces, floor, corner, nearby objects |
| `f2poly.py` | Weil descent and the coefficient-wise builder comparison (arm B) |
| `symbolic_s3.py` | symbolic F_2-degree expansion under the affine substitution (arm C) |
| `selftest.py` | instrument self-checks, run as phase 0 before any measurement |
| `run_experiment.py` | the driver; fixes the phase order the contract requires |
| `make_manifest.py` | emits `manifest.yaml` from `raw-result.json` so no number is hand-typed |

`binary_field.py` sha256 matches its source exactly; both values and the
match statement are in `manifest.yaml` and `environment.json`. No fix to the
vendored arithmetic was needed, so there is no divergence to report.

## Phase order actually executed

Arm D ran **first**, before every other phase, and its gate was evaluated and
written to `raw-result.json` (`arm_d_gate`) before any later phase started.

```
phase 0   instrument self-checks                      (all passed)
phase 1   ARM D exact enumeration                     (gates everything)
phase 1a  ARM D GATE evaluation                       (stopping rule 1)
phase 1b  arm D controls: degenerate, shuffled, exhaustiveness, representation
phase 1c  supplementary sub-saturation cells          (labelled supplementary)
phase 2   baseline: Table 3, m*, symbolic c'
phase 3   arm A: surfaces, savings, floor, corner, nearby objects
phase 4   arm B: coefficient-wise builder comparison
phase 5   arm C: symbolic F_2-degree expansion
```

## Protocol deviation: the run continued past a fired gate

**Stopping rule 1 fired.** Arm D's ratio is not about `m!` at any declared cell,
and the frozen falsification threshold (`< m!/2`) was crossed at all seven. The
specification's `stopping_rules[0]` and the handoff's `completion_gate[0]` both
say the run stops there. **It did not stop.** Phases 1b–5 ran.

The reason, recorded in full at `raw-result.json` →
`protocol_deviation_continuation`:

- The **same handoff's** `completion_gate[1..10]` independently require the
  degenerate-typing null, the Table 3 reproduction under both k readings with
  `c'` recovered symbolically, the shuffled-type null, the subset-sum corner,
  both nearby objects, all four invalid-input rejections, the exhaustiveness
  control and the vendored-sha256 statement.
- `success_criterion` enumerates deliverables from the baseline and from arms A,
  B and C, and says a ratio far from `m!` *"satisfies the criterion"* rather
  than terminating it. `required_artifacts` lists 18 items spanning all arms.
- `invalidation_rules[1]` and `[2]` make the **run** invalid if the
  exhaustiveness control shows order dependence or the degenerate-typing null
  does not return exactly 1. Arm D's own refutation is therefore **not
  admissible as a measurement** until those two controls have run, so halting
  before them would have left the gate's finding unverified.
- The halt rule states its own purpose as order and cost. The **order was obeyed
  literally**, and the whole run costs 66 s of a 3600 s budget, so continuing
  spent nothing the rule was protecting.

What was **not** done: the frozen prediction was not adjusted, re-scoped or
re-scored; no later phase was used to soften or reinterpret arm D's observation;
no status was changed; no degree was measured.

**This branch is the Coordinator's to adjudicate.** If the halt was meant
literally, phases 1b–5 are surplus and can be disregarded without touching arm
D's observation, which is complete and self-contained in `image-sizes.json`. An
amendment fixing precedence between `stopping_rules[0]` and
`completion_gate[1..10]` would remove the ambiguity for the successor contract.

## Failed attempts, retained

Four attempts. The first two produced no measurement and are
`implementation_error` — **not** evidence about the hypothesis in either
direction (core rule 5).

1. **`ZeroDivisionError`** in `arm_d_draw`. A typed coset `V + v_i` can contain
   no curve point at all: for a given x, `y^2 + xy = x^3 + Ax^2 + B` is solvable
   for about half of all x, so a coset of size `2^k` is entirely off the curve
   with probability roughly `2^{-2^k}`, which is not negligible at k = 2, 3. The
   typed domain is then 0 and the random-map reference divided by it.
   **Fix:** the empty-coset case is now recorded as its own outcome
   (`status: empty_typed_base`, ratio exactly 0, offending coset indices and all
   base sizes retained) instead of crashing. 29 such draws occurred; they are in
   the rows table and are counted in `arm_d_gate.draw_accounting`. They are kept
   out of the ratio *statistics* because a family with no relations has no
   typed-over-untyped ratio to compare against `m!` — and including them can
   only deepen the recorded shortfall, which is stated in the gate.
2. **`AttributeError: families.random_basis`.** The helper lives in
   `image_enum`. **Fix:** call `image_enum.random_basis`.
3. **Completed**, then a defect was found *by inspection* in the
   Galbraith–Gebregiyorgis nearby-object control: its `collapses_to_polynomial`
   flag compared two numbers at a single n against a fixed 10-bit slack. At
   n = 283 with m = n/log2 n = 34, the 34 bits added by `G(m) = 2^m` is small
   beside the 130-bit polynomial reference, so a super-polynomial `G` was
   flagged as collapsing. A proves-too-much control with a discriminator that
   cannot discriminate is worse than none.
   **Fix:** `gg_growth_discriminator` decides polynomiality by **growth** —
   whether `value(n)/log2(n)` stays bounded as n runs to 10^7, at the argument's
   own operating point `m = n/log2 n`, with the yield exponent capped at
   `max(0, n - mk)` because a negative exponent is a probability above 1. It now
   separates all five declared families correctly. The single-n numbers are
   retained with an explicit note that they are not the verdict.
4. **Final run.** Exit 0, empty stderr, 66.1 s, peak RSS 0.221 GB.

## Instrument validation

`selftest.json`, phase 0, all passed:

- field arithmetic and curve law against independent checks;
- the Weil-descent builder against direct evaluation at 25 random Boolean
  assignments per cell, plus the squaring shortcut against general multiply;
- symbolic expansion bounds against numerical verification;
- the vectorised cost surface against the scalar one at n ∈ {100, 301, 571} ×
  both readings × typed/untyped;
- `log2(m!)` against exact integers at m ∈ {1, 2, 5, 12, 100, 500};
- `c'` by bisection against `sqrt(2 ln 2)` to 1e-59;
- **the exact convolution against independent brute-force enumeration** for
  both the typed product family and the untyped multiset family;
- all five invalid inputs rejected, plus a positive control that a legitimate
  draw passes the same guards.

## Two things worth a reader's attention

**Table 3 under `ceil(n/m)` is not reproducible, and that is a contract defect
rather than a reproduction failure.** Under the un-ceiled `n/m` the table comes
back at 35/36 within 0.7% (the single miss is 0.704%, inside the table's own
3-significant-figure printed rounding), and the stage-1 argmin reproduces the
paper's chosen m at **all 12** values of n. Under `ceil(n/m)`, 16 of 36 cells
miss, by up to 211%, and the argmin matches at 1 of 12. Table 3's arithmetic
uses the non-integer `n/m`; requiring the same printed numbers under both
readings is not satisfiable. Both readings are reported in full.

**The interior optimum has an exact closed form.** Under `k = n/m` the yield
exponent `n - mk` vanishes identically and the typed objective reduces to
`T(m) = (1+ω')(n/m + log2 m) + 4ω log2 n`. Stationarity gives `m = n ln 2`
exactly — matching the numerical argmin at every n from 100 to 10^5 — and the
depth below the `m = n` boundary is `(1+ω')(1 - 1/ln 2 - log2(ln 2))`, i.e.
**0.0860713 bits per `(1+ω')`, independent of n**. The rising term that creates
it is `log2 m`, entering from GG's substitution of the typed relation store
`m·2^k` for the untyped `2^k`. That is the missed rising term the falsification
criterion asks to be named.

## Standing limits on everything above

- **No degree was measured.** No d_reg, no first-fall degree, no d_F4, not even
  "plausibly 4". `magma`, `sage`, `Singular` and `msolve` were probed and are all
  absent (recorded in `environment.json`). Arm C reports F_2-degrees of
  explicitly constructed coordinate polynomials, which is a different quantity
  from a solving degree.
- **HEUR-A1T remains unvalidated on this host.** Every typed cost number here is
  conditional on it.
- **Measured versus modeled.** Arms D, B and C are exact counts. Every cost
  surface, saving in bits, argmin, width, floor, corner and nearby-object value
  is a closed-form evaluation of the model, not a timing. The split and the
  optimistic assumptions are listed in `manifest.yaml` →
  `contract_declarations.measured_versus_modeled`.
- **Scale.** The enumeration arms ran at n ∈ {12, 15, 17}, group orders 3984 to
  130992. Untyped images there are tens of elements, so a ratio is dominated by
  which x-values happen to lie on the curve. No asymptotic statement transfers
  from them without an argument this run does not make.
- The polynomial-time branch of the cost model is a **reductio** against a
  premise, never a claimed algorithm. No claim is made about the security of any
  deployed curve, in either direction.
