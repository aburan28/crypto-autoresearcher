# Joint J6-BLIND — phase-two verification and reconciliation

- **Round:** REVIEW-SEMBIN-20260913-9d649f
- **Task:** TASK-20260913-ec11c4 (validator, `review-adversarial`, xhigh)
- **This file is NOT blind and does not claim to be.** It was written after
  reading `blind_from`, for the purpose of comparison.
- **Companion files:** `report.md` and `attestation.yaml` were written by a
  different session/instance of this same task. This file does not replace
  them; see "Two sessions, one task" below.
- **My verdict on J6-BLIND:** `incomplete` — see "Verdict, and where I differ".

## 1. The two frozen figures

Read from `figures-before-reading.json` before I opened anything under
`blind_from`:

| quantity | frozen blind value |
| --- | --- |
| crossover `n`, (time × memory), sparse reading | **306** |
| signed margin in bits at `n = 409`, same measure | **+29.77** |

The file records `written_before_reading_blind_from: true`, exact rational
interval arithmetic at 2^-256 relative precision, primary model
`closed/time/sparse/plan`, and — importantly — it distinguishes a *persistent*
crossover (`crossover_region_detail.final_crossover = 306`) from the literal
smallest cheaper `n` (`smallest_cheaper = 3`).

## 2. Do the frozen figures reproduce from the frozen script?

**Yes, exactly.** I reran `rederivation.py` standalone to a separate output path
(`verification/rerun-figures.json`, 8.3 s, 15 MB peak) and compared the full
JSON, not just the headline pair:

- identical to `figures-before-reading.json` in **every field except
  `produced_at`** — including the whole sensitivity grid, the margin curve, the
  crossover region detail, and all five controls;
- the frozen file's sha256 is unchanged at
  `301cbd861809dd3f2bb997621541c59be487743d1e320bc2280f61dfe8e67596`, and
  `rederivation.py` at
  `8f2f7bd6ce78e7060da1b0257e2579f53292f9eef1b077b28a908c6e9f534a9c`.

So the re-derivation is deterministic and its recorded figures are its script's
actual output. Had they disagreed, the artifact would have been worthless and
this report would say so instead.

All five of its controls pass against permitted sources only: Table 3's 36 cells
within 0.70% with the argmin over `m` matching the paper at every row; the
degree-≤4 monomial exponents 41.2 / 43.4 / 45.9; the relation counts
2^31 / 2^38 / 2^48; seven eq. (11) `P_theoretical` cells; and the time-only
crossover of 302.

## 3. Did the frozen script answer the plan's question?

**Mostly yes, and the one place it could not is the plan's fault rather than the
script's.** Checking the frozen script line by line against the
`blind_rederivation` block of the review plan (which I extracted
programmatically, reading neither `claim_under_review` nor `coordinator_prior`):

| plan parameter | frozen script | matches |
| --- | --- | --- |
| stage 1 `m! · 2^{n/m} · n^{4ω}`, ω = 3 | `stage1_time_closed` | yes |
| stage 2 `2^{2n/m}`, exponent 2 | `stage2_time` | yes |
| minimise over integer `m ∈ [2,20]` | `M_RANGE = range(2,21)` | yes |
| relation store `2^{ceil(n/m)}` rows of `m·ceil(n/m) + 2n` bits | `relation_store_bits` | yes |
| working set = degree-≤4 monomials in `N = m·ceil(n/m) + 2n` | `boolean_monomials_upto(macaulay_variables_plan)` | yes |
| baseline time `0.886 · 2^{n/2}` | `baseline_time` | yes |
| baseline memory 2^30 points × 3n bits | `baseline_memory_bits` | yes |
| yield eq. (11), `t = m`, `k = ceil(n/m)` | `_one_minus_exp_neg_bounds` | see below |

Two honest notes:

- **Eq. (11) is redundant with the plan's own stage-1 formula.** `m! · 2^{n/m}`
  is eq. (15) with the yield already folded in at `k = n/m`; stating eq. (11)
  separately specifies a second, different computation. The script handles this
  correctly rather than silently picking one: the primary model takes the plan's
  literal stage-1 formula, and an `exact` variant evaluating eq. (11) directly
  appears in the sensitivity grid (307 / +42.37). Neither is suppressed.
- **The Boolean monomial count is squarefree** (`sum_{i≤4} C(N,i)`), not
  `C(N+4,4)`. For N = 1236 the two differ by ≈0.02 bits. Immaterial, and the
  Boolean reading is the right one for a Weil-descended system.

So the frozen script did compute the plan's quantity with the plan's parameters.
It answered the question it was asked. That question, it turns out, is not the
question the record answers — which is section 5.

## 4. Comparison against the record

| | frozen blind | record `COST-SEMBIN-8d123b` | agree? |
| --- | --- | --- | --- |
| crossover `n` | 306 | **375** | no, 69 apart |
| margin at `n = 409` | +29.77 | **+11.5175** | no, 18.25 bits apart |

The signs agree — the attack is ahead at n = 409 under both — and the
magnitudes do not.

I verified the record's figures against the record's own raw output rather than
taking the COST yaml at its word: `raw-result.json` carries
`crossovers_per_metric.time_memory_product.semaev_sparse.crossover_n = 375`,
`margin_at_409 = 11.5175`, `semaev_log2_memory_bits = 66.525`, and
`monotone_after_crossover = true`. The COST record transcribes its own run
faithfully (`verification/verification.json`, section B).

I also verified the `RECORD` transcription block inside `localise.py` against
`COST-SEMBIN-8d123b.yaml` cell by cell for all five parameter sets. It is
correct. This mattered because the session that wrote that transcription could
not check it independently.

## 5. Localisation: one term, and it is the plan's statement

Everything except one term agrees to four decimal places at all five of the
record's parameter sets — optimal `m`, attack time, baseline time, baseline
memory, and the **entire dense branch** (86.8371, −8.7946, crossover 435), which
the frozen implementation reproduces with no substitution at all.

The single differing term is the **sparse Macaulay working set**:

```python
# memory_charged_cost.py, semaev_memory_log2, storage="semaev_sparse"
cols_log2      = 4.0 * math.log2(n * m) - math.log2(24.0)   # (nm)^4 / 24 columns
nz_per_row_log2 = 3.0 * math.log2(n) - math.log2(m)         # n^3 / m nonzeros per row
working_set_bits = cols_log2 + nz_per_row_log2
```

The plan instead says the working set is "the number of degree-≤4 monomials in
N = m·ceil(n/m) + 2n variables", charged as the width itself, "one field element
per nonzero".

**The decomposition at n = 409, m = 11** (`verification.json`, section E):

| term | log2 bits |
| --- | --- |
| producer's column count `(nm)^4/24` | 43.9566 |
| degree-4 monomials in the paper's N = 4099 | 43.4186 |
| degree-4 monomials in the plan's N = 1236 | 36.4986 |
| nonzeros per row `n^3/m` | 22.5684 |
| relation store | 48.2715 |
| **attack memory, plan as written** | **48.2715** (relation store binds) |
| **attack memory, producer** | **66.5250** (working set binds) |
| **gap** | **18.2535** |

and the margin gap is 29.7710 − 11.5175 = **18.2535**. The memory gap equals the
margin gap to four decimal places: the localisation is exact and single-term.

Three things follow that are worth separating:

1. **The plan's wording drops a factor, it does not name a different matrix.**
   The producer's `(nm)^4/24` and the paper-N degree-4 monomial count agree to
   0.54 bits, so dense and sparse genuinely are two storage conventions on the
   same matrix. What the plan's "one field element per nonzero" omits is the
   `n^3/m ≈ 2^22.6` nonzeros *per row*. (This is a narrowing of the companion
   report's finding F3, which reads the 0.54 bits as "different column counts";
   the arithmetic supports the milder reading.)
2. **The plan's secondary misstatement of `N` is immaterial here.** Plan-N and
   paper-N give the identical 306 / +29.77, because the relation store binds
   under either. The frozen sensitivity row `closed/time/sparse/paper` confirms
   it.
3. **The producer is not in error.** The formula is Semaev's own, from the
   ellipticnews thread recorded at `KN-LIT-e77232`, whose
   `citation_provenance` is `retrieved` with a receipt at
   `inputs/ELLIPTICNEWS-CHAR2-2015/provenance.json`, and which re-checks the
   arithmetic itself: `(nm)^4/24 = 2^46.38` columns and `n^3/m = 2^23.89`
   nonzeros at n = 571, giving 2^70.3 — matching the record's 70.2718. The
   producer implemented a sourced model; the plan paraphrased it wrongly when
   writing the blind brief.

**Direction:** the plan's model is *more* favourable to the attack than the
producer's. A reviewer working from the plan alone would over-credit the attack.

## 6. The crossover definition is ambiguous, independently of the numbers

The plan asks for "the smallest integer n at which the attack is cheaper". Under
the plan's own parameters that phrase has two answers, because the margin is not
monotone: `ceil(n/m)` steps at each multiple of m and doubles the relation
store, so the comparison saws.

Under the plan's reading the cheaper set is `{3} ∪ [306, 1200]`. The n = 3 point
is an artefact of charging the baseline a fixed 2^30-point distinguished-point
store in a group of 2^3 elements. So the literal answer is 3 and the intended
answer is 306.

I checked whether the record's 375 has the same defect, and **it does, in the
same way**: substituting the producer's sparse formula into the frozen
implementation and scanning from n = 3 gives cheaper runs `[3,3]` and
`[375,700]`. The producer's `crossover_curve` hardcodes `n_lo = 250` and takes
the first winning n, so it never sees the artefact. That window is undeclared,
but the producer does record `monotone_after_crossover: true`, which is the
persistence check that makes 375 the right number under the intended reading.

So: **both numbers are persistent crossovers and neither is a scan-window
artefact.** The defect is in the plan's phrasing, which does not say whether it
wants the first crossing or the last sign change, and states no scan domain for
n. A plan that had said "the smallest n from which the attack is cheaper for all
larger n" would have been unambiguous at no cost.

## 7. The blind brief disclosed the answer it was asking for

The plan's `blind_rederivation.quantity` field itself reads: "The record asserts
375 and +11.52 respectively; do not read those figures before you have your own."
The task brief that launched this session repeats them.

This is a defect in the blind protocol worth recording on its own. The blindness
obtained was to the *implementations and the run record* — which is the failure
mode the joint exists to catch — and was never blindness to the target values.
The evidence that the derivation was not steered toward the targets is the
disagreement itself, together with the fact that the sensitivity grid contains a
variant (`exact/time/dense/plan`) landing at 373 / +14.62 which could have been
presented as agreement and was not.

## 8. What no longer has an independent recomputation

`COST-SEMBIN-8d123b` names `independent_arith.py` as its
`independent_arithmetic_ref`. I read that file's own statement of coverage and
its output keys. It recomputes Table 3's 36 cells, `n^12`, stage 2, the
relation-store exponents, the variable counts 2790 / 4099 / 6286, the degree-4
widths, and the **dense** square — and it never evaluates `(nm)^4/24 · n^3/m`.
Its own docstring states its independence is "METHOD independence, not agent
independence".

So after this round the sparse working set — the term that moves the n = 409
verdict from −8.8 to +11.5 — is computed in exactly one implementation in the
repository, corroborated at exactly one parameter point (n = 571) by the
knowledge record it came from, and **it is the one term this blind joint was
unable to check, because the plan did not state it.** That is the finding the
round should carry forward.

## 9. Two sessions, one task — disclosed

`report.md` and `attestation.yaml` in this directory were **not written by this
session.** They appeared at 15:21:13 and 15:21:24 UTC while I was running my
verification, are addressed to this task id, and are written in the first person
about this joint. Their companion `attestation.yaml` in turn discloses my
`verification/` directory as a foreign artifact it did not author. Both
statements are true: two instances of TASK-20260913-ec11c4 ran concurrently in
this worktree.

What I did about it:

- **I did not overwrite or edit either file.** An attestation is a personal
  statement about what one agent read and when; replacing another agent's would
  be recording an attestation I did not obtain. I copied both to
  `verification/report.md.phase-one-snapshot` and
  `verification/attestation.yaml.phase-one-snapshot` so the round has a fixed
  record of what they said at the moment I read them.
- **I verified their load-bearing claims rather than adopting them.** The
  reproduction of the frozen figures, the `localise.py` transcription against
  the COST yaml, the COST record against `raw-result.json`, and the
  substitution test reproducing 375 / +11.5175 all check out under my own
  re-execution.
- **Where we differ I say so** (the F3 narrowing in section 5, and the verdict
  below).

The blindness claim in this directory covers the session that *wrote* the
figures, at 15:10:42 UTC, before its first `blind_from` read at 15:11:22 UTC.
**I am not that session and I am not blind.** My own first exposure to
`blind_from`-derived content was at 15:17:26 UTC, deliberately, in order to
perform the comparison this file reports. I offer the file mtimes and hashes as
an ordering receipt, not as proof: nothing binds a working-tree file until a
Coordinator snapshot commit.

## 10. Verdict, and where I differ

The companion attestation records `breaks`, scoped explicitly to "the joint as
specified rather than the record's arithmetic". I agree with every fact behind
it and record a different word: **`incomplete`**.

`breaks` on a joint reads downstream as "the load-bearing step does not hold",
and that is not what happened. The load-bearing quantity was not refuted — it
was *not tested*, because the statement handed to the re-derivation specified a
different memory model. The record survived everything that could be checked
against it: its arithmetic spine (attack time, baseline time, baseline memory,
argmin m, the entire dense branch) reproduces exactly from a genuinely
independent implementation, and its sparse term is faithfully implemented from a
`retrieved` source that re-checks it at n = 571.

So the honest composition is: **the blind check of the load-bearing quantity did
not happen.** Not because the derivation failed, but because the plan's
`parameters` field did not satisfy its own promise that "every one of them is
stated here so that you never need the producer's code to obtain them."

This distinction is not cosmetic. `breaks` invites a Coordinator to discount the
record; `incomplete` tells it the record is unimpeached and the verification it
commissioned still needs doing. The second is what the evidence supports.

## 11. What this report does not say

Nothing here supports any claim about the security of B-409, K-409, B-571 or
K-571. Both cost models are heuristic estimates conditional on Semaev's
Assumption 1, with non-identical operation units on the two sides and no
conversion factor, as the record itself discloses. No solve, relation, or
certificate is computed. The record's own `degree_bound_sensitivity` notes that
a degree bound of 5 adds 19.4 bits at n = 409 — larger than every effect
discussed above, and untouched by any of this.
