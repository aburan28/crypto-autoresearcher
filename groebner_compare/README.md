# Verified Boolean Gröbner comparison protocol

This is executable **solver-stage infrastructure**, bounded to synthetic or
otherwise authorized Boolean systems with 1–12 variables. It implements frozen
inputs, fresh-process baselines, persistent learn/apply workers, independent
certification, charged fallback, and append-only attempt receipts. It does not
implement an ECC attack, change any scientific state, or establish a speedup.

From the repository root (Python 3.11+, Unix):

```sh
python -m pip install sympy==1.14.0
python -m unittest groebner_compare.test_protocol -v
python -m groebner_compare.runner groebner_compare/smoke.json --output /tmp/boolean-comparison-new
```

Use a new output directory every time. The manifest, input hashes, harness
source hashes, Python/platform identity, raw worker requests/stdout/stderr,
fsynced attempt journal, per-backend summaries, and comparison JSON are retained.
Killed runs retain the frozen inputs and completed journal entries; absence of
a final summary means incomplete execution, never a successful benchmark.
The shipped smoke data are correctness controls, not performance evidence.

## Algorithm

1. Validate and freeze one ordered instance list, exact GF(2) quotient,
   variable ordering, encoding identity, backend provenance, threads, and
   per-request machine-protection watchdog. Repeated terms cancel modulo two;
   mask 0 is the constant 1, and bit i represents x_i.
2. For a `cold` backend, start a new worker for every instance and request
   `solve`. For `learn_apply`, learn on the first instance, then apply its
   in-memory trace to subsequent instances in the same worker. The learning
   instance is part of the same workload and is charged once.
3. Independently prove each returned basis has the original Boolean zeros and
   the correct leading ideal using exhaustive zeros plus staircase dimension.
   A backend's completion flag or its own `isgroebner` result is insufficient.
4. On a failed/incompatible apply or invalid certificate, discard the worker
   and trace and perform a fresh solve. Charge both attempts, startup, and
   verification. The rest of this batch uses ordinary solves; a new learning
   policy requires a new manifest. No silent retries or free relearning.
5. Optionally call a separately implemented, trusted relation verifier with
   the original instance and certified roots. Incrementally compute rank of
   its verified vectors modulo the declared prime, deduplicating dependent
   relations through elimination. This bounded implementation accepts primes
   up to 65521. Absent this verifier, all relation metrics are null.
6. Retain every unknown/timeout/unavailable outcome. Report verified instance
   throughput and, when configured, verified rank increase / total wall time.
   A timeout is never UNSAT; only a certified empty zero set proves that.

Total wall time runs from backend initialization through cleanup, including
learning, failed applications, fallback, conversion inside workers, independent
verification, rank calculation, and journal I/O. Upstream instance generation,
environment installation, downstream DLP stages, and final summary writing are
explicitly outside this solver-stage boundary. Compare paired instance lists;
run repetitions and reversed backend order under a separate frozen experiment
contract before making performance claims. There is no automatic winner or
extrapolation to degree 19, n=131, or full DLP cost.

`peak_worker_process_rss_bytes` is Linux VmHWM for the largest observed worker
process, not simultaneous process-tree RSS or host memory. It is null where
unavailable. Thread environment variables are fixed (default 1); these are not
an OS CPU quota. The watchdog kills the process group, but this is not a memory
sandbox. Use the host's existing resource controls for external workers.
Degree and matrix maxima are optional backend telemetry, explicitly labeled
backend-reported; missing values stay null, and row/column maxima need not
belong to the same matrix. They are never inferred from output basis degree.

## Adapters and remaining work

| Backend | Command / availability |
|---|---|
| SymPy reference | `python -m groebner_compare.worker sympy`; small correctness reference only |
| Existing Boolean F5B | `python -m groebner_compare.worker repository-f5b`; available in `cryptanalysis/experiments/pdp-scaling` |
| Sage / PolyBoRi | `sage -python -m groebner_compare.worker polybori`; requires a Sage installation |
| Groebner.jl F4 | `julia --project=YOUR_PINNED_ENV groebner_compare/worker.jl`; cold and learn/apply |
| Magma Boolean F4, msolve, M4GB, hybrid XL/Crossbred | Not implemented here; use the worker contract below only after a field-correct adapter and independent regression checks exist |

Julia dependencies are Groebner, AbstractAlgebra and JSON3. CI resolves them
and retains its Project/Manifest; scientific runs must pin and archive their
own environment. The Julia adapter recomputes polynomials from each request,
adds all field equations, checks canonical supports before applying a trace,
and leaves output certification to Python. Over GF(2), fixed nonzero support
fixes the coefficients: an identical-support repeat is only a reuse control,
not evidence of useful speedup across distinct targets. Changed constants can
invalidate support and must count as rejected applications.

Reference API: [Groebner.jl learn/apply](https://sumiya11.github.io/Groebner.jl/interface/).
The exact certificate follows the zeros-and-staircase argument already used
in `cryptanalysis/experiments/pdp-scaling/boolean_basis.py`.

## Worker contract

Commands are argv arrays, executed directly from the repository root, never
shell strings. Only run trusted local workers. Each stdin JSON line contains
`schema`, `request_id`, `operation`, `ring`, `encoding`, and `instance`.
Operations are `solve`, `learn`, `apply`, or `verify_relations`; apply includes
`trace_id`. Return exactly one flushed JSON line echoing `request_id` and
`status` (`ok`, `incompatible`, `unavailable`, `error`). Diagnostics go to stderr.
Requests/responses are bounded to one MiB. Unexpected IDs, malformed messages,
partial lines, exits, and watchdog expiries fail the attempt.

A successful solver response supplies `basis_terms` as lists of monomial
masks, with optional `solver_version` and `metrics` (`highest_degree`,
`largest_matrix_rows`, `largest_matrix_columns`). Learn also supplies an opaque
nonempty string `trace_id`. Traces are process-local; they are never loaded from
pickle or used across rings. The runner independently checks every `ok` basis.

An optional manifest `relation_verifier` contains `command`, `provenance`,
`modulus`, and `width`. It receives certified `solutions` plus the original
instance and must check the original curve/group relation, subgroup membership,
factor-base identity and coefficient/sign conventions itself. It returns
`vectors` only for verified relations, or an error. The runner checks dimensions
and computes rank, but **does not supply or certify that domain-specific curve
verifier**. Solver-supplied relation vectors are ignored. Verifier errors make
`relation_verification_complete` false; any reported rank is then a verified
lower bound from completed checks. No verifier is enabled in shipped fixtures.

## Repository integration

The same `groebner_compare/` implementation is vendored in `crypto`,
`crypto-autoresearcher`, and `cryptanalysis`; keep changes synchronized and
review the source hashes when comparing receipts. No repository imports a
mutable checkout of another. The `repository-f5b` adapter discovers only its
own repository's existing source and otherwise reports unavailable.

In `crypto`, this is a stage diagnostic, with `candidate_id` and
`full_dlp_speedup` null; it does not update the IC scoreboard. In
`crypto-autoresearcher`, it is a command-based tool usable by the existing `run`
path, not a new execution skill, campaign, ledger transition, or automated
research dispatch. In `cryptanalysis`, the repeated-target experiment is a
secondary batch diagnostic and does not replace the primary single-target
online IC measurement. Native Macaulay cache entries and learn/apply traces
remain distinct mechanisms.
