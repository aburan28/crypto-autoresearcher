# Experiment log: guessing remainders and sign patterns in the six-point Riemann–Roch / 2-adic chain system

Date: 2026-10-15/16 (UTC). Follow-up to [`REPORT.md`](REPORT.md) and [`HYBRID_REPORT.md`](HYBRID_REPORT.md).
PDF: [`guessing_report.pdf`](guessing_report.pdf). Graph: [`guessing_compare.svg`](guessing_compare.svg) (PNG beside it).
Table: [`guessing_runs.csv`](guessing_runs.csv) (all strategies, 67 msolve runs, `mult` arm, seed 1).

This is a measurement log. It changes no hypothesis status and makes no
Coordinator decision. Statements are labelled **measured**, **derived** or
**inference**.

## 1. Question

`HYBRID_REPORT.md` guessed coefficients of C(x). This log adds three more ways
of guessing part of the solution and measures, for each, the solving degree of
the remaining system against k:

1. **Remainder coefficients.** Fix g coefficients of the last remainders of the
   squaring chain, R_L = X^(2^(L+1)) mod q, highest coefficient first.
   - g = 6 fixes R_L completely.
   - g = 12 fixes R_L and R_(L−1).
2. **One-level sign split.** On each root of q, X^(2^(k−1)) = ±s, where
   s² = c. Up to the order of the roots, the sign pattern is
   m = #{roots with +s}, so there are 7 guesses. The system becomes
   q = q₊·q₋, with q₊ | X^(2^(k−1)) − s and q₋ | X^(2^(k−1)) + s. Each factor
   needs only a depth-(k−1) chain. Code: `code/split_build.py`.
3. **Two-level sign split.** X^(2^(k−2)) takes one of the four fourth roots
   y_j of c. The guess is a composition (m₀, m₁, m₂, m₃) of 6, with 84 options
   (at most 68 when each part must be ≤ 2^(k−2) = 4 at k = 4). The factors
   f_j | X^(2^(k−2)) − y_j are nested inside the one-level split
   (q₊ = f₀f₂, q₋ = f₁f₃), so every equation stays quadratic. Code:
   `code/split2_build.py`.

The important difference between these strategies is the size of the guess
space:

- Coefficient guesses (C or remainders) range over F_p, so g guessed
  coefficients mean p^g possible guesses.
- A sign-pattern guess ranges over a set of fixed size: 7 at one level, 84 at
  two levels.

## 2. Setup

The setup follows `REPORT.md` §2.

- **Arm and solver:** `mult` arm, p = 268496897, seed 1, circuit encoding.
  msolve 0.10.1, F4, grevlex, one job at a time.
- **Planted controls:** every planted instance asserts a witness for its true
  guess. That covers the full circuit witness for remainder guesses, and the
  true m or composition for splits.
- **Memory:** this container restarted twice under memory pressure. From the
  split queue's restart onward (20261016T0010Z), msolve ran under
  `ulimit -v 9000000` (8.6 GB). An allocation failure under that cap exits with
  −11 and is recorded as `memory`. Earlier `memory` rows are kernel OOM kills
  (−9) at about 13.6 GB.
- **Skip rule:** a role or cell that does not complete at some k is skipped at
  larger k.

| run set | started (UTC) | grid | limit |
|---|---|---|---|
| `data/remainder1/` | 20261015T2252Z | remainder g ∈ {1, 2, 6, 12}, k = 4 (k = 5 interrupted, not recorded) | 1800 s |
| `data/remainder2/` | 20261016T0207Z | remainder g ∈ {6, 12, 2}, k = 5–6 | 1200 s, 8.6 GB |
| `data/split1/` | 20261015T2315Z | one-level split, k = 4, planted, m = 0, 1 (stopped at a container restart) | 1800 s |
| `data/splitq/` | 20261015T2327Z, resumed 20261016T0010Z | representative one- and two-level guesses, k = 4–6 | 1200 s (8.6 GB after resume) |

In `splitq`, each k got the following jobs:

| level | instance | guesses run |
|---|---|---|
| one-level | planted | the true m, true m − 1, true m + 1 |
| one-level | random T | m = 3, m = 0 |
| two-level | planted | the true composition, a rearrangement of it, a composition of another shape |
| two-level | random T | the true composition, (1, 1, 1, 3) |

**Code commits:**

- 62cfb6dba5 and ae4a58a7a0: one-level split and remainder guessing.
- 683194f487: two-level split and the queue.
- The resume change is 8df2f17fa8.
- `analyze_guessing.py` draws the comparison.

## 3. Results (measured)

Maximum F4 degree per specialised system. "≥" marks a lower bound: the run
stopped at its time limit or its memory cap. Rows marked "none" are from
`REPORT.md`, and rows marked "C coeffs" are from `HYBRID_REPORT.md`.

| strategy | guess space | k = 4 | k = 5 | k = 6 |
|---|---|---|---|---|
| none | — | ≥ 7 (memory) | ≥ 6 (memory) | ≥ 6 (memory) |
| C coeffs, g = 1 / g = 2 | p / p² | 5 (≈ 1700 s) / 4 (≈ 10 s) | ≥ 5 / ≥ 5 (1800 s) | skipped |
| remainder coeffs, g = 1 | p | 5 (5–7 s) | not run | not run |
| remainder coeffs, g = 2 | p² | 4 (0.2 s) | ≥ 5 (memory, ≈ 600 s) | skipped |
| remainder coeffs, g = 6 | p⁶ | true 4, wrong 2 (0.2 s) | true 4, wrong 3 (0.2 s) | true 4, wrong 3 (0.2 s) |
| remainder coeffs, g = 12 | p¹² | — (only one remainder at k = 4) | true 4, wrong 2 (0.2 s) | true 4, wrong 2 (0.2 s) |
| one-level split | 7 | true m: ≥ 7 (1200 s); wrong m = 3: ≥ 7; m = 1, 5: 6 (≈ 170–190 s); m = 0: 5 (0.2 s) | wrong m = 3: ≥ 5 (memory); m = 0: ≥ 6 (memory) | skipped |
| two-level split | ≤ 84 | true (1,2,1,2): **6** (1190 s); wrong rearranged: ≥ 6 (1200 s); (1,1,1,3): 6 (28 s) | true and all wrong: ≥ 6 (memory, 312–759 s) | skipped |

**Controls:**

- Every complete correct-guess system returned exactly one solution.
- Every complete wrong-guess and random-T system returned no solution (`[-1]`).
- Wall time and peak memory match between planted and random instances given
  the same guess shape. For example, two-level (1,2,1,2) at k = 4 took 1189.975 s
  planted against 1189.979 s random, and (1,1,1,3) took 28.4 s against 29.0 s.

**Variable counts at k = 4:**

| system | variables |
|---|---|
| none | 25 |
| one-level split | 20–32 |
| two-level split | 34–37 |
| remainder g = 6 | 19 |

## 4. Derived

- **Guessing a whole remainder makes the solving degree flat.** With g = 6 or
  g = 12, the solving degree is 4 at k = 4, 5 and 6, with 0.2 s per system.
  - Reason: once R_L is fixed, the last squaring step says q divides R_L² − c,
    a known polynomial of degree 10. So q is one of at most C(10, 6) = 210
    degree-6 factors, and what remains is close to bookkeeping.
  - Cost: the guess ranges over p⁶. That is 2^1344 for P-224, against a
    per-relation budget of about 2^27.8. Each fixed coefficient also divides
    the expected number of relations in a family by p (`HYBRID_REPORT.md` §4).
- **Guessing fewer remainder coefficients matches guessing C coefficients.**
  g = 1 and g = 2 give degree 5 and 4 at k = 4, and do not complete at k = 5.
  They are much faster than C-coefficient guesses at k = 4 (6 s against
  1700 s for g = 1; 0.2 s against 10 s for g = 2). The guess space is the same
  p^g.
- **Sign-pattern guesses are cheap to make but do not lower the degree.**
  - One-level split: the true branch at k = 4 stays at ≥ 7, the same as no
    guess.
  - Two-level split: the true branch at k = 4 completes at degree 6, below the
    unguessed ≥ 7, at a guess cost of at most 68 compositions. At k = 5 every
    two-level system ran out of memory at degree 6, in line with the unguessed
    k = 5 baseline (≥ 6).
- **Splitting adds variables.** The factor and nested-chain variables outweigh
  the shorter chain at these k: 34–37 variables for a two-level split at k = 4,
  against 25 unguessed.
- **Rough per-instance cost of the two-level split at k = 4.** About 68
  compositions; single runs took between 28 s and over 1200 s. That is about
  10⁴–10⁵ s in total, against a single unguessed system that did not finish
  within 13.6 GB. This estimate is not measured end to end.

## 5. Inference, limitations, next checks

**Inference (not a decision record):**

1. On these systems, the guesses that make the solving degree flat in k are
   the ones whose guess space is a power of p. That trade cannot fit an
   N^(1/6)-per-relation budget.
2. The guesses with a bounded guess space (sign patterns) leave the solving
   degree at or near the unguessed values. At k = 5 they hit the same memory
   wall.
3. Neither kind shows a way to keep the solving degree near 2–3 with bounded
   guessing.

The degree evidence rests on complete runs at k ≤ 4 (k ≤ 6 for whole-remainder
guesses) and lower bounds elsewhere.

**Limitations:**

- One seed and one arm. Representative compositions only, not all 84.
- 1200 or 1800 s limits and an 8.6 GB cap: memory and timeout stops are
  operational facts, not refutations.
- The two-level per-instance total is extrapolated from single runs.
- Two container restarts interrupted runs: one remainder run at k = 5 and one
  one-level run at k = 4 (m = 2). Their partial files were removed and no
  result is recorded for them.

**Next checks:**

1. Sign splits at more levels together with remainder guesses on the factors.
   For example, split two levels, then guess the last remainder of each small
   factor. The remainder of a degree-m_j factor has only m_j coefficients, but
   it still ranges over F_p.
2. A host with more than 64 GB to finish the true branches at k = 5.
3. Count how the number of compositions and the per-system cost combine as the
   number of levels j approaches k. At j = k this becomes exhaustive search
   over S⁶.

## 6. Files

- `code/split_build.py`, `code/split2_build.py`, `code/run_split.py`,
  `code/run_split_queue.py`.
- `code/hybrid.py` (guess set `r`), `code/run_hybrid.py`,
  `code/analyze_guessing.py`.
- `data/remainder1/`, `data/remainder2/`, `data/split1/`, `data/splitq/`: each
  holds `results.jsonl`, `progress.log`, `started`, and
  `runs/<tag>.{ms,json,log,out}`.
- `guessing_runs.csv`, `guessing_compare.{svg,png}`,
  `guessing_report.{typ,pdf}`.

Reproduce (paths are relative to `code/`; this needs a sage-python venv with
msolve):

```sh
python3 run_hybrid.py OUT <venv>/bin/python <msolve> 1200 \
  '{"ks": [4,5,6], "gs": [1,2,6,12], "arms": ["mult"], "cells": [["planted","true"],["planted","wrong"],["random","wrong"]], "seeds": [1], "set": "r"}'
(ulimit -v 9000000; python3 run_split_queue.py OUT2 <venv>/bin/python <msolve> 1200 '[4,5,6]')
cd .. && python code/analyze_guessing.py .
```
