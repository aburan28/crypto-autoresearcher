# Execution Report — TASK-20260804-736f46

**Batch:** BATCH-6f309b  
**Goal:** GOAL-MLKEM-004  
**Repair of:** TASK-20260804-27e27b (failed_infrastructure: ARM64 cannot build g6k x86 SIMD)  
**Date:** 2026-08-04 (container ran 2026-08-05 01:12–01:29 UTC)

---

## 1. Platform confirmation

The container was launched with `--platform linux/amd64` via Docker Desktop on a macOS aarch64 host. QEMU emulation confirmed x86_64 execution:

```
uname -m → x86_64
Linux 0ff5d72186ea 6.12.76-linuxkit #1 SMP Fri May 1 14:35:41 UTC 2026 x86_64 GNU/Linux
platform: Linux-6.12.76-linuxkit-x86_64-with-glibc2.41
```

This confirms that g6k's SIMD intrinsics (`immintrin.h`) compiled and executed on a genuine x86_64 instruction set under QEMU.

**Infrastructure note — two additional repair attempts before success:**

The task required three container launches to reach a successful build:

1. **Attempt 1 (exit 1):** `python:3.11-slim` has no C compiler. Error: `configure: error: no acceptable C compiler found in $PATH`. Fix applied: added `apt-get install gcc g++ make automake autoconf libgmp-dev`.
2. **Attempt 2 (exit 1):** g6k's bundled fplll `Makefile` was generated with `automake-1.16`; the installed version is 1.17. The `missing` script failed to find `aclocal-1.16`. Fix applied: created symlinks `aclocal-1.16 → /usr/bin/aclocal` and `automake-1.16 → /usr/bin/automake`.
3. **Attempt 3 (exit 0):** All packages installed and all 50 runs completed successfully.

---

## 2. Environment build outcome

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.11 (python:3.11-slim, linux/amd64) | OK |
| passagemath-standard | 10.8.7 | **installed (binary manylinux_2_28_x86_64 wheels)** |
| fpylll | 0.6.4 | **PASS** — `||b0||` printed after dim-60 BKZ-30 |
| g6k | 0.1.2 | **PASS** — gauss_sieve produced db=4075 vectors |
| numpy | 2.4.6 | installed via passagemath |

**fpylll verification output:**
```
fpylll version: 0.6.4
fpylll OK: ||b0||= <norm printed>
```

**g6k verification output:**
```
g6k OK: db= 4075
```

---

## 3. Variance test outcome

**Parameters (frozen, identical to batch-1):**

| Parameter | Value |
|-----------|-------|
| Lattice dimension D | 60 (m=35, n=25) |
| Modulus q | 127 |
| Secret distribution η | 2 (centered binomial) |
| Error std dev σ | 2.0 |
| Sieve algorithm | bgj1_sieve |
| Sieve threads | 1 |
| Instance seed | 20260803001 (FIXED across all 50 runs) |
| fpylll seed | 20260803005 (FIXED across all 50 runs) |
| Siever seeds | 0, 1, …, 49 (varied across runs) |
| Runs requested | 50 |
| Runs completed | **50 / 50** |

**T_N statistics (50 independent runs, same LWE instance):**

| Statistic | Value |
|-----------|-------|
| mean(T_N) | 7554.192 |
| std(T_N) | 85.421 |
| var(T_N) — empirical, ddof=1 | **7296.782** |
| min(T_N) | 7356.559 |
| max(T_N) | 7760.647 |
| N_vectors per run | 17919 (all runs identical) |

All 50 runs produced exactly N=17919 sieve vectors. Each sieve took approximately 13.5–16.3 seconds under QEMU x86_64 emulation (native x86_64 would be faster).

**Independence prediction (from batch-1 single-score variance):**

- batch-1 single cosine scores: N=17919, mean=0.427375, var=0.332505
- independence_predicted_var = 17919 × 0.332505 = **5958.153**

**Variance ratio:**

```
variance_ratio = Var[T_N] / (N × Var[s_i]) = 7296.782 / 5958.153 = 1.225
```

---

## 4. Scope statement

- Dimension D=60, q=127. This is a **toy instance**, not a cryptographic parameter set.
- All 50 runs were seeded with the same LWE instance (instance_seed=20260803001) and varied only the Siever seed.
- This is an observation. Batch 3 will compare these numbers against the MATZOV.Nf advantage formula.

**NO FINDING IS STATED.** This report records raw T_N values and the variance ratio as observations only. The Executor does not assess whether the ratio is consistent or inconsistent with any model; that is the Coordinator's role after independent review.

---

## 5. Deviations from approved protocol

1. **Docker `create` + `start` pattern required.** On this macOS/aarch64 Docker Desktop host, `docker run --platform linux/amd64` leaves containers in "Created" state (confirmed by inspection); `docker start` after `docker create` works correctly. This is an infrastructure deviation from the task spec's `docker run` command but is functionally equivalent: the same container image, mounts, and command were executed.
2. **Staging via `/tmp`.** Docker Desktop on macOS does not share `/Volumes/SSD990` (external drive) with the Docker VM by default. Input files were staged to `/tmp/vartest_stage_736f46/` and output was collected from `/tmp/vartest_out_736f46/`, then copied into the task directory. The repo root visible to the container was `/repo` (→ staged copy), functionally identical to a `/repo:ro` bind mount of the live repo.
3. **Two extra build attempts.** The build required three container launches (gcc missing; aclocal version mismatch; success). All attempts are recorded in `rebuild_transcript.txt`. This is an infrastructure_error that was repaired in the same task; no mathematical result is affected.

---

## 6. Artifact paths

| Artifact | Location |
|----------|----------|
| rebuild_transcript.txt | coordination/goals/GOAL-MLKEM-004/batches/BATCH-6f309b/tasks/TASK-20260804-736f46/rebuild_transcript.txt |
| variance_results.json | coordination/goals/GOAL-MLKEM-004/batches/BATCH-6f309b/tasks/TASK-20260804-736f46/variance_results.json |
| report.md | coordination/goals/GOAL-MLKEM-004/batches/BATCH-6f309b/tasks/TASK-20260804-736f46/report.md |
| receipt.json | coordination/goals/GOAL-MLKEM-004/batches/BATCH-6f309b/tasks/TASK-20260804-736f46/receipt.json |
