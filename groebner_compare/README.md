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
   A `warm` baseline performs ordinary solves in one persistent worker without
   tracing; compare it to `learn_apply` to avoid attributing process/package
   startup savings to the trace algorithm.
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
CPU seconds include the runner plus reaped worker children; descendants that
detach or outlive their worker are not guaranteed to be accounted by that OS
counter. Use external cgroup accounting when complete process-tree telemetry
is required.

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
| XOR-aware SAT | `python -m groebner_compare.research_worker cryptominisat` uses `pycryptosat`'s native XOR clauses, Tseitin AND gates, and a *witness* receipt; `xor-sat` is a bounded pure-Python XOR control |
| Block-aware batch F4 prototype | `python -m groebner_compare.research_worker block-f4` chooses the explicitly frozen ordered blocks; independently certified in the Boolean quotient |
| ElimLin → F4 | `python -m groebner_compare.research_worker elimlin-f4` derives affine ideal consequences with a bounded Macaulay scan, then runs global Boolean F4; zero derived consequences is a valid negative result |
| Hybrid guess → F4 | `python -m groebner_compare.research_worker hybrid-f4` fixes the three most involved variables on the ECC fixture, checks each branch basis, and returns a *witness* |
| Hybrid guess → CryptoMiniSat | `python -m groebner_compare.research_worker hybrid-cryptominisat` specializes the same variables and sends each surviving Boolean system to native XOR SAT; all failed branches are charged, but their UNSAT result is not independently certified |
| Original M5GB C++ | `python -m groebner_compare.research_worker m5gb` invokes an **externally built** bridge for the actual upstream source at `manschga/M5GB` commit `2d063f748e8a16ac5a1d74641c79725df29f67ac`; missing binary, upstream errors, uncertified output and watchdog exits are recorded, not replaced with F5 |
| Magma Boolean F4, msolve, hybrid XL/Crossbred | Not implemented here; use the worker contract below only after field-correct adapters and independent checks exist |

Build and select the M5GB bridge from separately obtained upstream source:

```sh
git clone https://github.com/manschga/M5GB.git /tmp/m5gb-upstream
git -C /tmp/m5gb-upstream checkout 2d063f748e8a16ac5a1d74641c79725df29f67ac
python -m groebner_compare.build_m5gb /tmp/m5gb-upstream /tmp/m5gb-bridge
export M5GB_BINARY=/tmp/m5gb-bridge
python -m unittest groebner_compare.test_research -v
```

The published M5GB source host returned HTTP 502 when checked; this separate
public author repository builds but has a hardcoded sample-file `main.cpp`.
Our bridge supplies frozen GF(2) equations to its unmodified algorithm.
The upstream process may crash or return an output that fails certification;
neither is a verified result. Do not extrapolate this prototype to ECC2K83/131.

`cryptanalysis` additionally freezes three planted ECC2K17, three-summand,
three-coordinate Weil-descended inputs in `ecc2k17_five_way.json`. Run that
manifest after versioning the fixture and solver code:

```sh
python -m groebner_compare.runner groebner_compare/ecc2k17_five_way.json \
  --output /tmp/ecc2k17-five-way-fresh
```

This compares identical equations and watchdogs and charges every failed
target. `pdp_verifier.py` independently regenerates each system and checks
the curve point-sum relation after each algebraic root. The derived metrics
are verified bases, verified algebraic witnesses, and verified curve witnesses.
The planted inputs are correctness controls. They cannot establish ordinary
relation yield, independent rank, a 2× cost-per-new-relation improvement, or a
full DLP speedup. Missing worker binaries remain `unavailable` in the journal.
For this Boolean stage protocol, generated fixtures and full preprocessing are
outside the charged interval, as shown in every receipt. At scale, account for
them separately before making an IC claim.
`freeze_pdp.py --include-hybrid-sat OUTPUT` adds the specialization + native
XOR challenger to a second frozen manifest without altering first-pass inputs.

Julia dependencies are Groebner, AbstractAlgebra and JSON3. CI resolves them
and retains its Project/Manifest; scientific runs must pin and archive their
own environment. The Julia adapter recomputes polynomials from each request,
adds all field equations, checks canonical supports before applying a trace,
and leaves output certification to Python. Over GF(2), fixed nonzero support
fixes the coefficients: an identical-support repeat is only a reuse control,
not evidence of useful speedup across distinct targets. Changed constants can
invalidate support and must count as rejected applications.

`candidates.json` is a ready-to-run synthetic adapter comparison, including
both warm F4 and learn/apply. It expects the pinned Julia environment at
`.groebner-julia`; absent programs produce explicit unavailable attempts.
The identical-system repeat is labeled a control. Provision the environment
first and retain its lockfile with scientific receipts. Magma and other
unimplemented adapters are deliberately absent from this runnable matrix.

Reference API: [Groebner.jl learn/apply](https://sumiya11.github.io/Groebner.jl/interface/).
The exact certificate follows the zeros-and-staircase argument already used
in `cryptanalysis/experiments/pdp-scaling/boolean_basis.py`.

## Worker contract

Commands are argv arrays, executed directly from the repository root, never
shell strings. Only run trusted local workers. Each stdin JSON line contains
`schema`, `request_id`, `operation`, `ring`, `encoding`, and `instance`.
Operations are `solve`, `learn`, `apply`, `verify_witnesses`, or `verify_relations`; apply includes
`trace_id`. Return exactly one flushed JSON line echoing `request_id` and
`status` (`ok`, `unknown`, `incompatible`, `unavailable`, `error`). Diagnostics go to stderr.
Requests/responses are bounded to one MiB. Unexpected IDs, malformed messages,
partial lines, exits, and watchdog expiries fail the attempt.

A successful solver response supplies `basis_terms` as lists of monomial
masks, with optional `solver_version` and `metrics` (`highest_degree`,
`largest_matrix_rows`, `largest_matrix_columns`). Learn also supplies an opaque
nonempty string `trace_id`. Traces are process-local; they are never loaded from
pickle or used across rings. The runner independently checks every `ok` basis.
Alternatively, a solver can return `solutions` with distinct assignment masks;
the runner checks them against the original Boolean equations and records
`verified_witness` instead of claiming a complete Gröbner basis. `basis_blocks`
must match the frozen instance's `blocks` and is certified with the block order.
F4 progress markers are copied to archived stderr and included as optional
highest degree and matrix maxima, even if a later watchdog kills the worker.

`witness_verifier` independently checks the original mathematical relation
for every returned algebraic root. In the cryptanalysis fixture the verifier
rebuilds the original PDP by seed, compares every equation and the target,
and checks actual lifted curve-point sums. An unknown or empty group check
cannot become a verified curve witness.

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
