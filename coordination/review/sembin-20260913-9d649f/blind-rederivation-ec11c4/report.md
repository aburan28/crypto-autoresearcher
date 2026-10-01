# Blind re-derivation — joint J6-BLIND

- **Round:** REVIEW-SEMBIN-20260913-9d649f
- **Task:** TASK-20260913-ec11c4 (validator, `review-adversarial`, independent session)
- **Record under re-derivation:** `COST-SEMBIN-8d123b` in
  `experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/`
- **Verdict on my joint:** `breaks` — not the record's arithmetic, but the
  review plan's statement of the quantity. See "What the verdict means".

## The two figures

|  | my blind re-derivation | the record | agree? |
| --- | --- | --- | --- |
| crossover `n` under (time × memory), sparse reading | **306** | **375** | no, 69 apart |
| signed margin in bits at `n = 409`, same measure | **+29.77** | **+11.5175** | no, 18.25 bits apart |

Both of mine were written to `figures-before-reading.json`
(sha256 `301cbd861809dd3f2bb997621541c59be487743d1e320bc2280f61dfe8e67596`,
mtime 2026-09-13 15:10:42 UTC) and hashed before I opened anything in
`blind_from` at 15:11:22 UTC. Sign agrees (the attack is ahead at n = 409 under
both); magnitude does not.

## Where the difference localises

**It is one term, and it is the review plan's fault, not either
implementation's.** Everything else in the comparison agrees to four decimal
places at all five of the record's parameter sets:

| quantity at n = 409 | mine | record | Δ |
| --- | --- | --- | --- |
| optimal `m` | 11 | 11 | — |
| attack time | 166.5438 | 166.5438 | 0.0000 |
| baseline time | 204.3254 | 204.3254 | 0.0000 |
| baseline memory | 40.2609 | 40.2609 | 0.0000 |
| attack memory, **dense** | 86.8371 | 86.8371 | 0.0000 |
| attack memory, **sparse** | 48.2715 | 66.5250 | **18.2535** |

The same pattern holds at n = 163, 233, 283 and 571: time, baseline and dense
memory agree exactly; sparse memory differs by 13.5 to 20.3 bits. My
implementation independently reproduces the record's *entire dense branch* —
memory 86.8371, margin −8.7946, crossover 435 — with no substitution at all.

The sparse working set is the single disagreeing term. The plan's `parameters`
block describes it as the degree-≤4 monomial count:

> Working set from the number of degree-<=4 monomials in `N = m*ceil(n/m) + 2n`
> variables.

and my brief added that the sparse reading "charges the width itself (one field
element per nonzero); a dense reading would charge width²". The producer's code
charges something else entirely
(`memory_charged_cost.py`, `semaev_memory_log2`, `storage="semaev_sparse"`):

```python
cols_log2 = 4.0 * math.log2(n * m) - math.log2(24.0)     # (nm)^4 / 24 columns
nz_per_row_log2 = 3.0 * math.log2(n) - math.log2(m)      # n^3 / m nonzeros per row
working_set_bits = cols_log2 + nz_per_row_log2
```

Substituting **only** that formula into my otherwise untouched implementation
reproduces the record exactly: crossover **375** and margin **+11.5175** at
n = 409 (`localisation.json`, `substitution_test_producer_sparse_formula`). The
localisation is therefore complete and single-term.

Two separate misstatements in the plan combine into it:

1. **`N` is the wrong variable.** The producer's Macaulay variable count is
   `(m-2)n + m*ceil(n/m)` — Section 4.5.1 of the frozen text, and the count the
   permitted `inputs/SEMAEV-2015-310/tables.yaml` itself uses (4099 at
   n = 409, m = 11). The plan's `m*ceil(n/m) + 2n` is the producer's *relation
   row width* (`row_bits`, 1236), a different local variable in the same
   function. The plan conflated two adjacent quantities.
2. **The sparse reading is not a reading of that width at all.** It is Semaev's
   own sparsity estimate from his 2015-04-20 comment in the ellipticnews thread,
   recorded at `KN-LIT-e77232`: "each Boolean equation has at most about `n^3/m`
   monomials and the whole system about `(n*m)^4/4!`", with row count taken of
   the order of the column count. At n = 409 that is 23.1 bits *above* the
   monomial width, which is the whole disagreement.

Defect 1 turns out to be immaterial to my figures: under the plan as written the
relation store binds at every n (48.27 against a width of 36.50 or 43.42), so
both readings of `N` give the identical 306 / +29.77. Defect 2 is the entire
difference.

**Direction matters.** The plan's stated model is *more favourable to the
attack* than the producer's: +29.77 against +11.52 at n = 409. A reviewer
working from the plan's parameters alone would have over-credited the attack.
The plan as written is not sufficient to reproduce 375 / +11.52, so the
re-derivation it commissioned could not have confirmed those figures from the
stated inputs — which is a defect in the plan worth recording independently of
the science.

## What the verdict means

I did **not** find an arithmetic error in the record. Every figure I could check
against its own stated basis checks out, and the record's headline framing — a
46.6-bit swing between two defensible storage readings, straddling zero at
n = 409, with the paper stating no memory model — survives my re-derivation
intact. My `breaks` verdict is on the *re-derivation joint as the plan
specified it*: the plan misstates the quantity, so this joint did not
independently confirm the number it was commissioned to confirm.

## Findings the round should carry forward

These are the reasons the joint matters beyond the localisation.

### 1. The load-bearing number has no independent recomputation anywhere

`COST-SEMBIN-8d123b` names `independent_arith.py` as its
`independent_arithmetic_ref`. That file re-derives all 36 Table 3 cells, `n^12`,
stage 2, the relation-store exponents (31 / 38 / 48), the variable counts
(2790 / 4099 / 6286), the degree-4 widths (41.2 / 43.4 / 45.9) and the **dense**
square (91.8) — but it never evaluates `(nm)^4/24 · n^3/m`. Its own record
states it is "method-independent, NOT agent-blind".

So `semaev_memory_log2_sparse` is computed in exactly one place in the
repository, and it is the number that flips the n = 409 verdict from −8.8 to
+11.5. My blind pass could not check it either, because the plan did not state
it. **After this round the sparse branch of the load-bearing row remains
singly-implemented and never re-derived.** The round should not be composed as
though it were validated.

### 2. A crossover inherits the *n-dependence* of the memory formula, and that is unsourced

`KN-LIT-e77232` records the sparsity formulas as Semaev's, explicitly "not
re-derived", with one numerical anchor: about 2^70 bits at (n = 571, m = 12).
The producer applies the formula across n ∈ [250, 650] to produce the crossover
375. A crossover is fixed by how memory *scales* in n, not by its value at one
point, so the 375 rests on an unverified functional form calibrated at a single
n. I confirm the formula does reproduce the anchor (my retyping gives 70.2714 at
n = 571 against the thread's 2^70.3), which is evidence about the anchor and not
about the slope.

The record's sharpest quantitative claim is
`crossover_shift_attributable_to_memory.semaev_sparse: +72 in n (303 -> 375)`.
I reproduce the 303 endpoint exactly in my own framework (both stages, the 0.886
walk constant, no memory charged). **Under the memory model the plan describes,
the shift is 303 → 306: +3 in n, not +72.** The entire +72 is carried by the one
blog-sourced, singly-implemented formula. That is the finding I would most want a
Coordinator to see.

### 3. Dense and sparse are not two storage readings of one matrix model

The dense branch uses the true degree-≤4 monomial count at `N = (m-2)n + km`
(2^43.42 at n = 409). The sparse branch uses `(nm)^4/24` (2^43.96), a coarsened
stand-in for the same column count — it is 0.54 bits high because
`nm = 4499 > N = 4099`. The two branches therefore assume *different column
counts* for the same Macaulay matrix. The effect is 0.5 bits against a 20-bit
headline, so it changes nothing quantitatively, but "dense versus sparse" is
presented as one matrix charged two ways and it is not quite that.

Relatedly, the two readings disagree about which resource is the bottleneck:
under the plan's reading the relation store binds at every n (a quantity derived
from the frozen paper's own parameters); under the producer's, the F4 working set
binds at every n (a quantity from a blog comment). Which physical resource
dominates is itself model-dependent here, and the record does not say so.

### 4. `max` versus sum

The plan, and my brief, state the attack's memory as the **maximum** of the
relation store and the working set. The code uses `log2_add`, i.e. the sum. At
every parameter set here the terms differ by ≥13 bits, so sum and max agree to
about 2 × 10⁻⁶ bits and nothing is affected. It is a statement/implementation
mismatch that would matter by up to 1 bit where the two terms were comparable.

### 5. Non-monotonicity and a small-n artefact, from my own derivation

The margin is **not** monotone in n: `ceil(n/m)` steps at every multiple of m
and doubles the relation store, so the comparison saws upward. Three different
integers can each be called "the crossover", and I report all three. Under the
plan's reading the last n at which the attack is still dearer is 305, so I
report 306.

There is also a spurious cheaper point at n = 3, an artefact of charging the
baseline a fixed 2^30-point distinguished-point store even when the whole group
has 2^3 elements. The producer's `crossover_curve` scans only n ∈ [250, 650] and
so never sees it. I checked that the window hides nothing real: under the
producer's own formula, widening the scan to n ∈ [100, 900] still gives
375 with a single contiguous winning run, and `monotone_after_crossover` holds.
The restriction is sound but undeclared.

## How I computed it

`rederivation.py`, standard library only, deterministic (verified by re-running
to a second file and diffing). No floating point appears in any comparison:
each cost is a closed rational interval built from exact integer m-th roots at a
declared 2^-256 relative precision, so every reported inequality is rigorous,
and a log2 figure is printed only when its lower and upper bounds round
identically. Eq. (11) is evaluated as rational bounds from the alternating
series for `1 - e^{-x}`. This is a deliberately different representation from
anything a float implementation would produce, so agreement is not agreement
about a shared numerical idiom.

Five controls against permitted sources only, all passing, recorded in
`figures-before-reading.json`:

1. all 36 Table 3 cells reproduce within 0.70% (the paper's 3-significant-figure
   rounding), and my argmin over m matches the paper's printed m at every row;
2. the frozen record's own degree-≤4 monomial exponents 41.2 / 43.4 / 45.9
   reproduce at the paper's variable count;
3. the relation counts 2^31 / 2^38 / 2^48 reproduce;
4. eq. (11) reproduces seven `P_theoretical` cells of Tables 1–2 (the paper
   truncates rather than rounds, so agreement is tested at one unit in the last
   printed place);
5. the frozen record's independently stated time-only crossover of 302
   reproduces exactly.

Controls 1 and 5 matter most here: they establish that my time model *is* the
producer's and the paper's, which is why the disagreement could be localised to
a single memory term rather than argued about.

## Gaps in the plan's parameter statement

Reported as instructed rather than guessed around.

- The sparse working set is misstated, as above. This is the material gap: the
  plan's stated inputs cannot produce the figure the plan asked me to confirm.
- `N` is given as the relation row width rather than the Macaulay variable
  count. Immaterial to my figures, but wrong.
- "Maximum" is stated where the implementation sums.
- The plan says "minimized over integer m in [2, 20]" without saying whether the
  minimand is time or the time × memory product. I took time, the literal
  reading and the paper's own (Section 4.5.2 minimises stage 1). The producer
  minimises stage 1 alone over m ∈ [2, 30]. At every parameter set here all
  three choices give the same m, so nothing turns on it; minimising the product
  instead would give m = 15 and 294 / +34.68 under the plan's reading.
- The plan does not state the scan domain for n, which is what admits the
  small-n artefact in finding 5.

## Artefacts

| file | what it is |
| --- | --- |
| `rederivation.py` | my implementation; standalone, rerunnable, stdlib only |
| `figures-before-reading.json` | my two figures plus intermediates, controls and sensitivity grid, written and hashed before any `blind_from` read |
| `localise.py` | post-blind single-term substitution test; imports my code, retypes the producer's formula, imports nothing from the producer |
| `localisation.json` | term-by-term reconciliation at all five parameter sets |
| `report.md` | this file |
| `attestation.yaml` | `review_attestation` block |

## A write-scope collision, disclosed

A `verification/` subdirectory appeared inside my assigned write scope while I
was working, mtimes 15:15–15:19 UTC. **I did not author it in this session.** It
is addressed to this task id, written in the first person about my joint, and
refers to my own n = 3 artefact finding, so it looks like another session or
instance working the same handoff in the same worktree. I am reporting it rather
than absorbing it: an undisclosed artefact in my deliverable directory would
otherwise read as mine.

My own artefacts are untouched — `rederivation.py` and
`figures-before-reading.json` both still hash to the values I recorded before my
first `blind_from` read. No figure or finding above cites that directory; I read
it only to check whether it conflicted with this report. Where it overlaps me it
agrees (the producer's model also shows the n = 3 artefact; the COST record
transcribes its own raw result faithfully — both of which I verified
independently). Its section C asks my F1 question but answers it with keyword
greps whose single hit is a false positive; my F1 rests instead on reading
`load_bearing_quantities()` in full. I neither endorse nor adopt its conclusions,
and I left it in place.

## Sensitivity grid (plan's reading unless noted)

| model | crossover n | margin at 409 | m* |
| --- | --- | --- | --- |
| **primary: closed yield / argmin time / sparse / plan N** | **306** | **+29.77** | 11 |
| closed / time / sparse / paper N | 306 | +29.77 | 11 |
| closed / argmin cost / sparse / plan N | 294 | +34.68 | 15 |
| closed / time / dense / plan N | 395 | +5.05 | 11 |
| closed / time / dense / **paper N** — *reproduces the record's dense branch* | **435** | **−8.79** | 11 |
| exact eq. (11) yield / time / sparse / plan N | 307 | +42.37 | 12 |
| exact eq. (11) yield / time / dense / plan N | 373 | +14.62 | 12 |
| producer's sparse formula substituted — *reproduces the record* | **375** | **+11.5175** | 11 |

The last two rows are worth reading together as a caution: `exact/time/dense/plan`
lands at 373 / +14.62, close to the record's 375 / +11.52 by coincidence through
a completely different route. Numerical proximity between cost models is not
evidence that they are the same model, which is the general form of the failure
this joint was set up to catch.

## What this report does not say

It does not support any claim about the security of B-409, K-409, B-571 or
K-571. Both cost models compared here are heuristic estimates conditional on
Semaev's Assumption 1, with non-identical operation units on the two sides and
no unit-conversion factor — all of which the record itself discloses. Nothing
here is a solve, a relation, or a certificate. The record's own
`degree_bound_sensitivity` notes that a degree bound of 5 adds 19.4 bits at
n = 409, which exceeds every effect discussed above; that one-sidedness is
untouched by my re-derivation and remains the largest open uncertainty in the
row.
