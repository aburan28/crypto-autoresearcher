# SYNTHESIS-ISOU-20260814 — what the within-class cost census established, and what it established about itself

**Scope.** `EXP-ISOU-2ac81f` (four executed runs), its successor contract
`EXP-ISOU-bfba73` (never executed), and the three independent reviews that
judged them: `TASK-20260813-e183e6` (Validator, on the runs),
`TASK-20260814-aa735d` (Validator, on the successor contract),
`TASK-20260814-c7f6cf` (Red Team, on the successor contract).

**Status.** Not a decision record. Decisions are `DEC-20260813-e0077d`
(approval), `DEC-20260813-61e8a3` (revise). Evidence is `EV-ISOU-7c6405`,
scoped to `RUN-ISOU-2ac81f-20BIT-B` and `RUN-ISOU-2ac81f-24BIT-B` only. Nothing
here moves a status, promotes a claim, or discharges an obstruction. Claim tier
throughout: **toy**. P-256 is the shape the base curves imitate, never the
object measured.

---

## 1. The one-sentence result

The census ran cleanly, produced certificate-carrying artifacts, and **cannot
answer the question it was built for** — not because of a series of bugs, but
because three of its gates could not fail, its headline confirmation traces to
an undeclared parameter, and its third leg is a cost model that was never
written as one.

## 2. Every defect was in the specification. None was in the execution.

Seven defects were found in `EXP-ISOU-2ac81f`, six more in `EXP-ISOU-bfba73`.
Not one was an Executor error.

The clearest case is the run-record schema. The contract's `required_artifacts`
matched the repository's own run schema nowhere — no nested `run:` key, none of
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`raw-result.json`. The Executor was told to write nothing outside the declared
paths, complied, carried the required content inside `manifest.yaml`, and
recorded the conflict verbatim in `stdout_stderr_note` **before anyone
noticed**. The defect surfaced only when `tools/validate_ledger.py` rejected the
archived runs, after the snapshot commit. It was repaired by supersession in
`d5b16bcc9` — and the Validator then found the successor contract had **not**
adopted the repair and would reproduce it (`NEW-01`).

This is the shape of the whole episode: the instrument was specified badly and
executed faithfully.

## 3. The census was calibrated against itself at every level

This is the structural finding, and it recurred at four scales:

| level | checked against | what it missed |
|---|---|---|
| runs | the contract | the repository run schema (`NEW-01`) |
| contract v1 | its author's own arithmetic | the negation-map constant, the undesignated statistic |
| contract v2 | its author's own arithmetic again | the density-law factor, the κ/N′ conflict |
| third leg | nothing | it is a cost model with no cost-model record |

The Coordinator broke the chain once, deliberately, by **refusing to approve its
own cure** — on the stated grounds that approving its own unreviewed derivation
would reproduce the failure the batch had just paid for. That refusal is the
single most valuable procedural act in the episode, and it is what routed the
contract to the two reviews that found everything below.

The Red Team's answer to "what is still checked only against itself" was: the
cost model. `templates/research-records.md` defines a `cost_model` record
carrying `optimistic_assumptions`, `overestimating_factors` and
`time_memory_tradeoff`. Q3 **is** a cost model and carries none of them.

## 4. Three gates that could not fail

A gate that cannot fail is not a control; it is a decoration that reads as rigor.

**Q3 is sign-locked by its own selection filter.** `base_curve_selection`
requires the a=−3 model, and a=−3 is the *only* within-class per-operation lever
the hypothesis admits. The base curve therefore sits at the minimum of a
two-valued distribution **by construction**, so no member can be cheaper per
operation. What remains of Q3 is seed noise against walk cost. The nearby object
for which the conclusion would be false — a base curve without a=−3 — is
excluded by the filter that defines the experiment.

**The completeness gate was a selection filter** in v1 (`DEV-3`): "the declared
degrees generate cl(O)" was applied when *choosing* candidates, so
vertex-count-equals-h held by construction in all four runs. Completeness was
independently **true** — h recomputed by form-counting, all 1652 vertices
certified order N, hence in the class by Tate — but the gate's diagnostic value
was zero. In v2 the gate can genuinely fail, yet an *undeclared* h-range filter
moves its failure probability by ~50× (provable failure rate 34.3% at h<40,
0.66% at h∈(160,800], because `2^(t−1) | h`).

**The corrected fixture cannot reject the error it corrects.** The v2
reproduction band contains the negation-map constant that the cure declares
wrong with probability **0.5807**, and does so in 2 of the 4 actual
BATCH-009b1b bands. The contract observes that its two clauses are not in
opposition — true, but because one of them cannot fail. A corrected constant
with no power to reject its predecessor is bookkeeping.

## 5. The one "confirmed" result is an artifact of an undeclared parameter

Q2 was the clean leg: best-to-worst 1.0262–1.0304, taking exactly two values,
partitioned exactly by the a=−3 fourth-power test, far under the 1.5×
falsification threshold. It looked like the predicted mechanism at the predicted
size.

It is not the mechanism. **`a` does not enter the Jacobian addition formula.**
From the committed data, `q2_add_field_mults_per_op` is 16.0 for every member in
every model; only doubling differs, 8.0 against 10.0. The measured doubling
fraction 0.1991/0.1993 predicts a ratio of 1.0276 against the recorded
1.026243/1.028293. The number is set by `census.py`'s
`adding_branches: 16, doubling_branches: 4` — a **walk parameter**, declared
nowhere in either contract.

The successor says only *"r = 20 partition adding walk"*. Read literally: zero
doubling branches, at which **Q2 = 1.000 exactly** and the confirmed mechanism
disappears. The program's one positive result is a property of the random walk
it chose, not of the isogeny class it measured.

## 6. The nulls were wrong in both directions, and the right one was free

- The contract's mandated nominal expectation for the band screen is **low by
  ~1.5×**. The "64 against 37.1" recorded in `EV-ISOU-7c6405` is a
  calibration-plus-centering artifact carrying no member information.
- F4's "nominal false-flag count" is undefined, and the only reading the word
  supports is wrong by **3.5×** (true H₀ rate 8.69% one-sided against a nominal
  2.5%). **F4 can fire on noise.**
- Three different null statistics appear in three places, one of them deciding a
  mandatory stop.

The decisive control was a **seed-column permutation** on the already-committed
`solve_records.jsonl` — 400 permutations, **zero additional solves**:

| | observed | contract nominal | permutation null |
|---|---|---|---|
| 24BIT-B outside band | 60 | 35.2 | 53.7 [43, 66] |
| 24BIT-B below band | 7 | 17.6 | 6.7 [3, 12] |
| 20BIT-B outside band | 4 | 5.8 | 6.1 [2, 11] |

Observed counts sit on the null. The F4-relevant below-band counts land exactly
on it — **better support for the Q1 null than anything the census itself
produced**, obtained after the fact, for free, from data already in hand.

The lesson generalizes: when a screen's null can be obtained by permuting the
existing data, computing a nominal expectation from a distributional assumption
is strictly worse and costs more.

## 7. Scale-dependence was never modeled, and it inverts the answer

`walk/solve` is `O(log p / √p) → 0`. Measured 0.0558 and 0.0597 against savings
of 0.0256 and 0.0275 — the two quantities are comparable **only at toy scale**.
The break-even instance count is **2.18 at 20 bits and 2.17 at 24 bits** on the
measured basis (~1850 on the modelled). Two prime sizes agreeing to half a
percent is a strong signal of a real law, and the number appears in **no
record**.

This is the deepest design error. Toy scale was chosen so the class could be
enumerated completely — a good reason. But it is also the only regime in which
Q3's two costs are the same order. At cryptographic scale the walk is
negligible against the solve and Q3's answer is fixed by an exponent, not
discovered by a measurement. The census measured a crossover, not a constant.

## 8. What actually survived

Not everything failed, and the parts that held are worth stating precisely:

- **Certificates.** 1652/1652 members re-verified by the Validator with *third*
  arithmetic, recovered k a singleton equal to the frozen k across 26,331
  records. The independence requirement worked exactly as intended.
- **Completeness.** Independently true, by an argument (form-counting h, all
  vertices order N, Tate) that owes nothing to the producer's own gate.
- **The corrected constants.** All five verify to six digits: median
  `√(2N·ln2) = 1.177410√N`, mean `√(πN/2) = 1.253314√N`, negation-map mean
  `√(πN/4) = 0.886227√N`, ratio exactly `√2`, CV `√(4/π−1) = 0.522723`.
- **Zero Montgomery/Edwards members** across all four runs, confirming the
  prime-order / no-2-torsion argument.
- **Reproducibility**, partially: 20BIT-A re-ran byte-identical from its
  recorded command — though `summary.json` derives from an *unarchived* scratch
  file, so the archive cannot regenerate it.

And the negative that matters: **obstruction 4 of `EV-ECDLP-b3e847` is not
discharged.** Two admissible toy runs against a defective contract do not
convert an asserted obstruction into a measured one. The closure of
`SG-ECDLP-002` still rests on three proven obstructions and one empirical
assertion, exactly as it did before this experiment ran.

## 9. What a correct version of this experiment looks like

The reviews converge on a redesign that is *smaller*, not larger:

1. **Derive Q2; do not measure it.** Per-operation cost is determined by the
   model and the walk's branch mix, both known before any curve is chosen. A
   census cannot discover a quantity fixed by the code that runs it. Declare the
   branch mix as a frozen protocol constant.
2. **Charge the walk analytically.** `O(log p/√p)` is a statement about
   exponents. Report the break-even instance count as a formula with its
   measured constants, and file it as a `cost_model` record carrying
   `optimistic_assumptions` and `overestimating_factors`.
3. **Keep exactly one empirical question** — whether Q1 is uniform across the
   class — and answer it against a **permutation null** on the class's own solve
   records, not a distributional nominal.
4. **Choose a base curve that does not sit at the optimum.** Without that, Q3's
   sign is fixed before the first solve.
5. **Declare the parameters.** Nine were referenced as "declared" while declared
   nowhere; the bootstrap seed alone moved a band edge 8.41%.
6. **Bind `required_artifacts` to `tools/validate_ledger.py`** and make a clean
   validator run a completion gate, so a schema defect cannot survive to the
   archive.

Under that design most of the census disappears, which is the point.

## 10. Cost, honestly

Four runs: **313 s of CPU**, 0.045 GB peak, no budget limit hit. Three
independent reviews and four Coordinator sessions cost orders of magnitude more
than the compute they governed.

That ratio is the episode's practical lesson. The expensive resource was never
CPU; it was specification. Every defect that cost real effort was introduced
before a single solve ran, and the cheapest control found — the one that
produced the best result in the record — cost **zero additional solves** and was
run after the fact on data already committed.

---

## Record index

| record | role |
|---|---|
| `EXP-ISOU-2ac81f` | executed contract, superseded |
| `H-ISOU-c5bfea` | hypothesis, superseded |
| `EXP-ISOU-bfba73` | successor contract, `review_required`, two blocking reviews |
| `H-ISOU-5748b6` | superseding hypothesis |
| `EV-ISOU-7c6405` | evidence, scoped to 20BIT-B and 24BIT-B |
| `DEC-20260813-e0077d` | approval of the defective contract |
| `DEC-20260813-61e8a3` | revise; supersession |
| `RUN-ISOU-2ac81f-{20BIT-A,20BIT-B,24BIT-A,24BIT-B}` | four runs, schema-completed by supersession |
| `TASK-20260813-e183e6` | Validator on the runs — REVISE |
| `TASK-20260814-aa735d` | Validator on the successor — REVISE |
| `TASK-20260814-c7f6cf` | Red Team on the successor — REVISE |

Corrections to this document are by supersession, never by edit.
