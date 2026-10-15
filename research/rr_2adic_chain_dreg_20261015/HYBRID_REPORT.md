# Experiment log: hybrid guessing of 1–2 unknowns in the six-point Riemann–Roch / 2-adic chain system

Date: 2026-10-15 (UTC). Follow-up to [`REPORT.md`](REPORT.md) (same study directory).
PDF: [`hybrid_report.pdf`](hybrid_report.pdf). Graph: [`hybrid_dmax_vs_k.svg`](hybrid_dmax_vs_k.svg) (PNG beside it).
Table: [`hybrid_runs.csv`](hybrid_runs.csv). Raw data: `data/hybrid1/`.

This is a measurement log. It changes no hypothesis status and makes no
Coordinator decision. Statements are labelled **measured**, **derived** or
**inference**.

## 1. Question

`REPORT.md` measured the circuit encoding with all five unknowns free (g = 0):

- k = 3: solving degree 5;
- k = 4: at least 7 before running out of memory;
- k ≥ 5: memory ran out at degree 6.

The hybrid approach fixes g of the unknowns to guessed values and solves the
smaller system. This experiment asks two things. Does the solving degree of the
specialised systems stay flat as k grows? And how much does one specialised
system cost, for the consistent branch (correct guess) and for the inconsistent
branches (wrong guess, random T)?

## 2. Setup

Everything is as in `REPORT.md` §2, except for the following.

**Guessed unknowns:**

- g = 1 fixes c1, the x-coefficient of C(x).
- g = 2 fixes c1 and c0, which makes C(x) fully known.
- Guessed variables are substituted out, so the systems have n − g variables
  (`code/hybrid.py`).

**Branches:** three per (k, g).

| branch | instance | guessed values |
|---|---|---|
| `planted/true` | planted relation | the planted witness's values (the one consistent branch) |
| `planted/wrong` | planted relation | random, different from the witness |
| `random/wrong` | uniformly random T | random |

**Grid:** `mult` arm only, p = 268496897. Circuit encoding, k = 3–7, g ∈ {1, 2},
seed 1, one job at a time, 1800 s per system.

- A (g, branch) cell that does not complete at some k is skipped at larger k.
  This is the `skipped_smaller_k_incomplete` status in `data/hybrid1/results.jsonl`.
- The g = 0 comparison rows come from the earlier sweep: circuit, `mult`, seed 1,
  with k = 4 from phase 2 (one job) and k = 5–7 from phase 3.

**Code and run start:** `code/hybrid.py` and `code/run_hybrid.py` at commit
8ceaf173b3. `run_sweep.py` was refactored to expose `run_msolve` in the same
commit. `build_systems.py` there adds only a `ustar` field to its output. The
run started at 20261015T1626Z from a checkout of main at 28635820b5, with these
files not yet committed. Their content matches 8ceaf173b3.

**Host and solver:** the same as `REPORT.md` (msolve 0.10.1, 4 vCPU,
15 GiB RAM).

## 3. Results (measured)

| k | g | n vars | branches | stop | max F4 degree | wall per system | peak RSS |
|---|---|---|---|---|---|---|---|
| 3 | 0 | 14 | planted, random | complete | **5** | 0.2–0.4 s | 13 MB |
| 3 | 1 | 13 | true, wrong, random | complete | **4** | 0.2 s | 13 MB |
| 3 | 2 | 12 | true, wrong, random | complete | **3** | 0.2 s | 13 MB |
| 4 | 0 | 25 | planted, random | OOM | ≥ 7 | 1517–1552 s | 13.6 GB |
| 4 | 1 | 24 | true, wrong, random | complete | **5** | 1683–1711 s | 2.2 GB |
| 4 | 2 | 23 | true, wrong, random | complete | **4** | 10.2–10.6 s | 94 MB |
| 5 | 0 | 36 | planted | OOM | ≥ 6 | 947 s | 13.6 GB |
| 5 | 1 | 35 | true, wrong, random | timeout 1800 s | ≥ 5 | 1800 s | 2.5 GB |
| 5 | 2 | 34 | true, wrong, random | timeout 1800 s | ≥ 5 | 1800 s | 5.1 GB |
| 6–7 | 1, 2 | — | — | skipped (k = 5 incomplete) | — | — | — |

**Controls (measured):**

- Every complete `planted/true` system returned exactly one solution.
- Every complete `planted/wrong` and `random/wrong` system returned no solution
  over the algebraic closure (`[-1]`).

**Branch cost:** within each (k, g), the three branches have the same maximum F4
degree and wall times within 2% of each other. Deciding that a wrong guess is
inconsistent costs as much as finding the solution on the correct branch.

**Where the k = 5 runs stopped:**

- g = 2: a degree-5 F4 step with a 267807 × 285940 matrix (1% dense) had
  started and not finished.
- g = 1: a degree-5 step with a 164866 × 246582 matrix had started and not
  finished.

For comparison, the complete k = 4, g = 1 run spent 1649 s in its three
degree-5 rounds. Its largest matrix was 73111 × 56197, about 3% dense.

## 4. Derived

- **Solving degree with two unknowns guessed:** 3, 4 and ≥ 5 for k = 3, 4, 5. It
  is one higher for each step in k across the range where runs complete.
- **Solving degree with one unknown guessed:** 4, 5 and ≥ 5. Without guessing
  (g = 0) it is 5 and ≥ 7.
- **Effect of each guess:** at k = 3 and k = 4, each guessed unknown lowers the
  solving degree by 1. At k = 4 the second guess cut the wall time by a factor of
  about 165 (1700 s → 10.4 s).
- **Cost of a guess at P-224 size:** a guessed unknown is an element of F_p.
  Exhaustive guessing therefore multiplies the number of systems by p^g. That is
  2^224 per guess for P-224, against a per-relation budget of about 2^27.8
  (`REPORT.md` §1).

  Equivalently, fixing g coefficients leaves an expected
  |S|^6/(720·p) · p^(−g) relations per specialised family. At the N^{1/3}
  parameters, that is ≈ 2^(−9.5 − 224g).

## 5. Inference, limitations, next checks

**Inference (not a decision record):**

1. Guessing removes a constant from the solving degree but does not stop it
   growing with k. At g = 2 the degree rises 3 → 4 → ≥ 5 over k = 3–5, in line
   with the unguessed trend (5 → ≥ 7).
2. Guessing over F_p cannot pay for itself in the relation-finding setting.
   Each guess divides the expected number of relations in a family by p. That
   loss is far larger than any reduction in solving cost seen here.

The degree evidence rests on complete runs at k ≤ 4 and lower bounds at k = 5.
It is consistent with growth in k but does not establish a law.

**Limitations:**

- One seed and one arm (`mult`; the earlier sweep found `dickson` identical).
- Only one choice of guessed variables: the coefficients of C, not those of A or
  any auxiliary variable.
- Timeouts are operational facts, not refutations.
- A 15 GiB host.

**Next checks:**

1. Guess the remainder or quotient variables of the last squaring steps instead
   of u, since those are where the k-dependence enters.
2. Rerun k = 5 with g = 2 at a larger time limit to obtain an exact degree there.
3. Restrict guesses to a structured subset, such as coefficients forced into a
   small subfield or a coset. This changes the counting in §4 and needs its own
   relation-count model before any cost claim.

## 6. Files

- `code/hybrid.py`: builds a specialised system.
- `code/run_hybrid.py`: hybrid sweep driver.
- `code/analyze_hybrid.py`: table and graph.
- `data/hybrid1/`: `results.jsonl`, `progress.log`, `started`, `commit`, and
  `runs/<tag>.{ms,json,log,out}`.
- `hybrid_runs.csv`, `hybrid_dmax_vs_k.svg` / `.png`, `hybrid_report.typ` /
  `hybrid_report.pdf`.

Reproduce:

```sh
python3 code/run_hybrid.py OUT <venv>/bin/python <msolve> 1800 \
  '{"ks": [3,4,5,6,7], "gs": [1,2], "arms": ["mult"], "cells": [["planted","true"],["planted","wrong"],["random","wrong"]], "seeds": [1]}'
python code/analyze_hybrid.py . data/hybrid1/results.jsonl runs.csv
```
