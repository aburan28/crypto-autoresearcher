# Experiment log: solving degree vs chain depth k for six-point Riemann–Roch decompositions over a 2-adic chain factor base

Date: 2026-10-15 (UTC). Study directory: `research/rr_2adic_chain_dreg_20261015/`.
PDF: [`report.pdf`](report.pdf). Graph: [`dmax_vs_k.svg`](dmax_vs_k.svg) (PNG beside it).

This is a measurement log. It records what ran and what was measured. It changes
no hypothesis status and makes no Coordinator decision. Each statement is labelled
**measured** (read from a run record), **derived** (computed from measured
values, with the computation shown), **literature**, or **inference**.

## 1. Question

The lead: P-224 has p−1 = 2^96(2^128−1) and P-192 has p+1 = 2^64(2^128−1). So
each prime has a factor base S of x-coordinates whose membership test is a short
chain of k squaring maps. A six-point relation is a function f = A(x) + y·C(x)
with deg A ≤ 3, C monic of degree 2 and f(−T) = 0. This leaves 5 unknowns. The
condition is that all six roots of q = (E·C² − A²)/(x − x_T) lie in S.

Reaching an N^{1/3} ECDLP cost needs |S| ≈ N^{1/6} (k ≈ 37 for P-224). It also
needs each decomposition system decided in about N^{1/6}/720 ≈ 2^27.8
operations. This experiment measures how the Gröbner solving degree of that
system grows with k, on toy primes. This was the decisive test proposed in the
preceding analysis.

**Literature:** this is the Petit–Kosters–Messeng construction (PKC 2016, DOI
10.1007/978-3-662-49387-8_1): smooth-subgroup cosets and auxiliary-curve isogeny
fibres as factor bases, with chain variables. It is mapped in
`notes/ecdlp_recursive_expansion_literature_map_20260717.md` §3.1. What is new
here is the Riemann–Roch parametrisation (f = A + yC) in place of Semaev
polynomials, and the Dickson-chain factor base for p+1.

## 2. Setup

**Arms (factor base S, |S| = 2^k x-values):**

| arm | prime p | shape | membership of X in S |
|---|---|---|---|
| `mult` | 268496897 = m·2^12+1 | P-224 (p−1 2-smooth part) | X^(2^k) = c, chain x ↦ x² |
| `dickson` | 268562431 = m·2^12−1 | P-192 (p+1 2-smooth part) | D_{2^k}(X) = c, chain x ↦ x² − 2 (x = z + 1/z, z in the norm-1 torus) |

**Encodings:**

- **direct**: the 5 unknowns u only. The six equations are the coefficients of
  (chain^k(X) mod q) − c. The input degree is 6 at k=3 and **22 at k=4**
  (measured).
- **circuit**: u (5 variables), the coefficients of q (6 variables), and one
  quotient and one remainder per squaring, R_{i+1} = R_i² − Q_i·q.
  - Every equation has degree ≤ 2.
  - n = 11k − 19 variables and n + 1 equations, so 14, 25, 36, 47, 58 for k = 3–7.

**Instances:**

- **planted** (positive control): T is the sum of six random factor-base points
  with distinct x. The builder computes the unique f through those points and
  −T, and asserts that this witness satisfies every equation of both encodings
  (`witness_checked: true` in every planted record).
- **random**: T is a uniform random point. The expected number of relations is
  about |F|^6/(720p), which is ≪ 1 at these sizes.

**Curve:** y² = x³ + ax + b, chosen at random per seed and resampled until at
least 6 x-values of S lie on it.

**Solver and host:** msolve 0.10.1 (passagemath-msolve wheel), F4, grevlex,
1 thread. Intel Xeon @ 2.10 GHz, 4 vCPU, 15 GiB RAM, Linux 6.18.

**Metric:** the maximum F4 step degree reached (`deg` column of `msolve -v 2`).
For a completed run this is the solving degree in msolve's grevlex F4. For a
stopped run, the highest degree whose step started is a **lower bound**.

**Code:** `code/build_systems.py` (system builder and witness check),
`code/run_sweep.py` (driver), `code/analyze.py` (tables and graph).

- `build_systems.py` is unchanged since commit 6dee0662f2.
- Phase 1 ran with the first committed `run_sweep.py` (6dee0662f2). Phases 2–3
  ran with fd0db54170, which adds the grid override and stop-degree capture.
- Phase 1 started while these files were still uncommitted. Their content
  matches 6dee0662f2.
- Per-file SHA-256 values are in §6.

### Phases

| phase | started (UTC) | grid | per-run limit | parallel jobs |
|---|---|---|---|---|
| 1 | 20261015T0518Z | both arms; circuit and direct, k = 3–4; planted and random; seeds 1–3 | 600 s | 3 |
| 2 | 20261015T0635Z | both arms; circuit, k = 4; planted and random; seed 1 | 2400 s | 1 |
| 3 | 20261015T0829Z | mult; circuit, k = 5–7; planted; seed 1 | 2400 s | 1 |

Notes on how the phases ended:

- Phase 1 was meant to run k = 3–10. It was stopped after k = 4 because all 12
  circuit k=4 runs were killed at ≈ 6–12 GB each with three jobs sharing
  memory.
- Phase 2 re-ran circuit k=4 one job at a time with the whole machine. It was
  stopped once its k=4 batch finished.
- Phase 3 extended to k = 5–7 with one instance per k, to bound the wall time.

## 3. Results (measured)

Exit −9 means the process was killed by the kernel out-of-memory killer at the
container limit (peak RSS ≈ 13.6 GB in every phase-2 and phase-3 case). Per-run
values are in `runs.csv` and `results_all.jsonl`; raw msolve inputs, logs and
outputs are in `data/phase*/runs/`.

| k | encoding | arm(s) | n vars | runs | stop | max F4 degree | largest matrix |
|---|---|---|---|---|---|---|---|
| 3 | circuit | mult, dickson | 14 | 12 | all complete (0.2–0.4 s) | **5** (all 12) | 3748 × 3275 |
| 3 | direct | mult, dickson | 5 | 12 | all complete (≈ 0.2 s) | **8** (all 12) | — |
| 4 | direct | mult, dickson | 5 | 12 | all timeout (600 s, 1.9 GB) | ≥ **24** | 5652 × 49785 |
| 4 | circuit | mult, dickson | 25 | 12 (phase 1) | all OOM, 3 jobs (377–587 s) | ≥ **7**¹ | 165551 × 195969 |
| 4 | circuit | mult, dickson | 25 | 4 (phase 2) | all OOM, 1 job (1517–1916 s) | ≥ **7** | 647230 × 655761 |
| 5 | circuit | mult | 36 | 1 | OOM (947 s) | ≥ **6** | 851697 × 1274254 |
| 6 | circuit | mult | 47 | 1 | OOM (636 s) | ≥ **6** | 2223917 × 4142298 |
| 7 | circuit | mult | 58 | 1 | OOM (333 s) | ≥ **6**¹ | 170233 × 363442 |

¹ The degree-7 step (k=4, phase 1) and the degree-6 step (k=7) had selected
their pairs, but their matrices never finished. That degree is the lower bound.

**Correctness controls (measured):**

- Every complete planted run returned exactly one solution (`n_solutions = 1`).
- Every complete random run returned `[-1]`, meaning no solution over the
  algebraic closure. This holds for both arms and both encodings at k = 3.
- Every planted instance passed the builder's witness assertion.

**Phase-1 caveat:** the phase-1 circuit k=4 kills were caused by three jobs
sharing memory. Phase 2 repeats them one job at a time.

### Width of the F4 matrix at a fixed degree

Circuit encoding, `mult` arm, planted seed 1 (`matrix_by_degree.csv`; the k=4
row is from phase 2). Columns of the largest F4 matrix at each degree:

| k (n) | D=3 | D=4 | D=5 | D=6 | D=7 |
|---|---|---|---|---|---|
| 3 (14) | 490 | 1619 | 3275 | — (complete) | — |
| 4 (25) | 506 | 4140 | 39040 | 195969 | 655761 (OOM) |
| 5 (36) | 813 | 6846 | 144749 | 1274254 (OOM) | — |
| 6 (47) | 1116 | 10408 | 253573 | 4142298 (OOM) | — |
| 7 (58) | 1419 | 13970 | 363442 | not reached (OOM while building) | — |

## 4. Derived quantities

- **Encoding effect at k=3 (derived from the table):** the circuit encoding
  lowers the solving degree from 8 (direct) to 5. At k=4 the direct system's
  input degree is 22, matching the "22" in the earlier toy. The circuit input
  degree is 2, but its solving degree is ≥ 7, above the complete k=3 value of 5.
- **Growth of the degree-5 width with k (derived):** the ratio of each D=5
  column count to the previous k's is ×11.9 (k 3→4), ×3.7 (4→5), ×1.75 (5→6)
  and ×1.43 (6→7). In absolute terms it rises from 3.3·10³ to 3.6·10⁵ columns
  over k = 3–7.
- **P-224-size circuit (derived):** k = 37 gives n = 11·37 − 19 = 388
  variables. The dense column count at degree D is C(n+D, D):
  - D = 5: 2^36.1
  - D = 6: 2^42.2
  - D = 7: 2^48.0

  Every one of these exceeds the per-system budget of about 2^27.8 before any
  linear algebra is done.

## 5. Inference, limitations, next checks

**Inference (not a decision record):** at k = 3–7 on p ≈ 2^28, nothing here
shows the solving degree staying flat at 2–3. That is what the N^{1/6}
per-relation target requires (see the earlier cost analysis). The one complete
circuit value is D = 5 at k = 3. At k = 4 the lower bound is D ≥ 7. For k ≥ 5
the runs exhausted 14 GB at degree 6 with matrices of 10⁶–4·10⁶ columns. These
observations are consistent with the solving degree growing with k. They do not
prove it: degrees above 7 at k = 4, or above 6 at k ≥ 5, were never reached.

**Limitations:**

- Only one solver (msolve F4, grevlex, default variable order). No other
  monomial order, variable ordering, signature-based algorithm, or hybrid
  guessing was tried.
- The memory cap was 15 GiB. A larger machine could finish k = 4.
- Only the 2^k part of p ± 1 was used. Odd-smooth factors of 2^128 − 1 (3, 5,
  17, 257, 641, 65537, …) were not.
- The factor bases are tiny relative to p, so random instances are inconsistent
  by construction. Decision cost on inconsistent systems is part of what
  matters, but it is not separated from the planted cost beyond the k=3
  timings.
- The p ≈ 2^28 primes stand in for P-192 and P-224. The structure (chain depth
  k) is what varies, not the size of p.
- Timeouts and OOM kills are operational facts. They are not mathematical
  refutations.

**Next discriminating checks:**

1. Finish circuit k=4 on a host with ≥ 64 GB to get an actual solving degree,
   then k=5. This is the minimum needed to fit D(k).
2. Hybrid approach: guess 1–2 of the u variables and measure the D of the
   specialised systems against k.
3. Encodings that use fewer variables (no quotient variables, with Q eliminated
   linearly), to see whether D tracks n or k.
4. Compare against Petit–Kosters–Messeng's Semaev-chain systems with the same S
   and k.

## 6. Files

- `code/build_systems.py`: builder with the planted-witness control (sha256
  `4ca484f9a2572e90bd11e39c077eda22d6d81c659ebae661597fd6b2d8e9a65c`).
- `code/run_sweep.py`: driver (sha256
  `bdd5b09993e66c0a4ec76c9ea2cd7fc3c279451f45723ec7c9288a6ad562ba86`).
- `code/analyze.py`: tables and graph.
- `data/phase{1,2,3}/`: `results.jsonl`, `progress.log`, `started`, and
  `runs/<tag>.{ms,json,log,out}` (msolve input, instance metadata, F4 trace,
  msolve output).
- `results_all.jsonl`, `runs.csv`, `matrix_by_degree.csv`: derived tables.
- `dmax_vs_k.svg` / `.png`: graph. `report.typ` / `report.pdf`: PDF report.

Reproduce one cell (sage-python from `passagemath-msolve`,
`passagemath-schemes` and `passagemath-singular`):

```sh
python3 code/run_sweep.py OUT <venv>/bin/python <venv>/.../sage_wheels/bin/msolve 2400 1 \
  '{"ks": {"circuit": [4]}, "seeds": [1], "arms": ["mult"], "insts": ["planted"]}'
python code/analyze.py . data/phase1/results.jsonl data/phase2/results.jsonl data/phase3/results.jsonl
```
