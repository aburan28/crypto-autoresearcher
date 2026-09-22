# DEC-20260921-dc6134 — frozen approval of RUN-KIC-e3dbed

**Decision:** approve the bounded continuation described in `protocol.json` for
execution after the listed source closure and runner preflight are committed.

This is an additive continuation of `koblitz.vs_rho.n53_probe` and the selected
Stage99 direct implementation at source commit
`dec66600d5d1613526f1c50229fb71953953bfd9`.  It does not reinterpret the
older eta=1/16 fixture or alter any existing receipt.

The user’s standing authorization for ideas, experiment design, and execution
under `AGENTS.md` supplies the authorization. The experiment is nevertheless
approved only with its frozen scientific boundary: public-synthetic,
explicit-scalar, known-answer N=53 Koblitz targets; a serial one-thread direct
versus one-thread rho comparison; per-target cold setup; no retained logs,
shared state, batch amortization, imported targets, or private-key recovery.

The prior does not predict a five-percent held-out win. The directly read
internal Stage99 gate reported a same-target four-thread direct/rho median ratio
of 0.969444, which missed its 0.95 gate; its earlier CPU0 result favored rho on
whole-process wall time. Those observations motivate the small density panel,
but do not support a generalization. They are not pooled with this run.

The protocol fixes 96 scientific children. Forty-eight direct calibration
children first compare the unmodified eta=1/128 Stage99 source to an
allocation-only eta=1/128 candidate on the same 12 targets, then measure the
allocation candidate at eta denominators 128, 256, and 512. Exact base,
relation, rank, scalar, equation, and result-digest equivalence is a gate before
the smaller-density ranking. The selected allocation configuration then faces
24 untouched scalar pairs, each with one direct and one rho process. It selects
a density solely from calibration direct timing, records the selection, and
performs the held-out comparison without retries.

The allocation-only source change is narrowly pinned: `full_pairs` has zero
initial capacity unless `PairMode::Full` is selected, and retains its existing
capacity in that mode. It targets an unconditional unused HashMap allocation in
the selected signed-expanded mode and changes no mathematical method. The
baseline source archive, origin manifest, generated offline `Cargo.lock`,
baseline build-preparation receipt, and candidate diff/binary are frozen before
scientific timing. Every process uses `RAYON_NUM_THREADS=1`, disables both
support-expansion paths because the pipelined path creates its own three-thread
pool, receives a fresh working directory, and is metered for whole-process
wall, CPU, and RSS. Build and toolchain cost is captured separately.

Before the first scientific process, the exact allocation-candidate diff,
baseline and candidate binary hashes, generated offline dependency closure,
case manifest with SHA-256-derived numeric seeds, analysis program, and control
checker must be committed and hash-pinned. Per-child resource data uses `wait4`
or the child receipt; the Darwin aggregate `RUSAGE_CHILDREN` maximum is not a
per-child RSS measurement. The 8 GiB figure is an honest cooperative cap only
when the runner records the available sampling/enforcement method.

The admission gate also consists of exactly three **untimed** serial one-worker
conformance children: baseline direct IC, allocation-only direct IC, and rho,
all on `binary 13`, `a=0`, eta `1/2`, numeric seed `13001`, and explicit public
known-answer scalar `17`. The direct form is
`binary 13 0 1 2 13001 signed_expanded independent pair_pair_parallel_4096 1 17`;
the rho form is `binary 13 0 signed_frobenius 1 packed 13001 17`. Full proof
checks are retained, but no timing, CPU, or RSS from those children is analyzed
or presented as science. Exact baseline/candidate equivalence on the prescribed
mathematical receipt fields is required before any of the 96 scientific
children begins.

The finite held-out signal predicate, artifact set, receipt checks, 240-second
per-child watchdog, 8 GiB per-child memory cap, and anomaly stop rule are all
in `protocol.json`. A timeout, crash, cap reach, or malformed receipt is an
implementation/instrumentation result, never mathematical negative evidence.
No threshold outcome changes a hypothesis status, claims an asymptotic result,
or asserts a cryptanalytic break. It first receives the predeclared independent
review after the exact source-and-artifact snapshot.

The reserved handoff sequence is:

- `TASK-20260921-362caa` — executor implementation, preflight, and bounded run;
- `TASK-20260921-a78926` — Coordinator snapshot of exact source and artifacts;
- `TASK-20260921-6ae79e` — independent `review-adversarial` review at xhigh;
- `TASK-20260921-d86664` — archive and ledger disposition.

**Evidence provenance:** the Stage99 figures above are `internal`, from the
directly read primary gate record. No external literature source was retrieved;
there is therefore no novelty or known-work conclusion in this decision.
