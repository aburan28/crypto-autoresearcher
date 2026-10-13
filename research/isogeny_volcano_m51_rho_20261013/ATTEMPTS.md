# Pre-launch attempts: m=51 conductor-271 rho study

This file is append-only operational history. It is deliberately excluded from
`FROZEN.sha256`; every execution- or inference-critical source and document is
included in that commitment. Entries here do not amend `PROTOCOL.md` or
`spec.json`.

## 2026-10-13 — design and core smoke checks (non-evidence)

- Reconstructed the frozen plan as 320 primary and 80 A/A jobs, each with
  exactly 64 targets: 400 jobs and 25,600 records total.
- Checked five-arm block membership, common planted-scalar roots, common
  primary streams, independent A/A streams, balanced 16-orbit assignment, and
  at most four pinned workers.
- Built the exact `rho.c`/`params.h` sources with the frozen warning-clean GCC
  command and ran all 35 curve/mode selftests twice. No `rho run` scientific
  job was launched.
- Exercised normalization with 25,600 synthetic records and checked rejection
  of substituted scalars, counter mismatches, failed verification, missing
  rows, nonzero exits, and malformed output.

These are implementation smoke checks only. Selftests establish the stated
group/action invariants for the toy core; synthetic records contain no measured
collision-walk outcome and supply no evidence about conductor-level ECDLP
hardness, a weak curve, or a transfer speedup.

## 2026-10-13 — independent pre-launch review and hardening (non-evidence)

Independent review identified two blocking evidence-integrity gaps: the first
analyzer revision trusted declarative normalized artifacts without rebuilding
the exact plan/raw correspondence, and the initial freeze path did not fully
close frozen-input/TOCTOU races. Review also identified missing rejection of
CSV overflow columns and uint64 overflow, no compiler timeout, incomplete
peer/interrupt cancellation, incomplete fsync durability, incomplete
selftest-stdout comparison, and an inference-label collision when equivalence
and a direction were both supported.

The harness was changed before launch to:

- commit every execution/inference input through `FROZEN.sha256`, snapshot and
  fsync it into a new empty run root, verify one clean Git state before and
  after the copy, and build only the snapshot;
- independently reconstruct all 400 jobs, schedule/core assignments, commands,
  receipts, raw rows, normalized rows, selftests, binary, session, provenance,
  and the complete sealed file tree in `analyze.py`;
- fail closed on extra columns, non-uint64 values, nonzero exits, timeouts,
  cancellation, count/counter/pairing/verification mismatches, partials, or any
  missing/extra artifact;
- cap compilation at 120 seconds, stop process groups after the first peer
  failure or launcher interrupt, and fsync files/directories before publishing
  atomic final names;
- report practical equivalence and measured direction as separate fields.

No scientific m=51 rho benchmark had been launched and no scientific outcome
had been observed when the critical-source freeze was created. Final clean-tree
selftest-only, full mocked-archive, relocation, and adversarial checks are to be
appended below; they remain harness validation, not study evidence.

## 2026-10-13 — final frozen-harness verification (non-evidence)

- In a temporary clean Git repository, `run_replication.py --selftest-only`
  completed the exact GCC build and all 35 real selftests. The executable hash
  was `4db25d2113bc39cce71e24b317b4c3ded69a7e177a23f86c4dbb2277bafdb3e0`;
  the selftest-only seal covered 19 files and contained no partial artifact.
- A fake `taskset` test shim delegated every `selftest` call to the real frozen
  executable but generated deterministic structurally valid CSV for every
  `run` call. This exercised the complete 400-job scheduler, four pinned worker
  lanes, 25,600-row normalization, receipts, session, run manifest, and
  424-entry tree seal without executing a scientific rho solve.
- `analyze.py` accepted that sealed synthetic archive, independently validated
  400 job receipts, 400 raw files, 35 selftests, and 25,600 normalized records,
  then also accepted a byte-identical archive relocated to a different root.
- With the checksum seal and dependent hashes deliberately repaired, the
  analyzer still rejected a changed plan/core assignment and a missing raw job.
  Direct gates also rejected a substituted scalar, inconsistent counter,
  `ok=0`, short job, trailing CSV cells, and values above `2^64-1`.
- A two-worker injected failure test propagated exit status 7, terminated the
  peer process group, and returned in 0.304 seconds. An injected hanging
  compiler was terminated by the build timeout in 1.003 seconds. Reusing the
  completed output root was rejected before build or selftest execution.

All observations in this entry concern harness behavior. The synthetic
analysis labels and numbers are intentionally non-scientific and must not be
reported as m=51 curve measurements. No scientific `rho run` outcome existed
at the end of these checks.

## 2026-10-13 — post-review redesign and replacement verification (non-evidence)

A statistics review found three pre-launch design blockers. The original
4,096-block analysis reused the first 64 offsets in each orbit for both the
level/model contrasts and A/A, treated orbit resampling as primary despite all
16 sampled orbits being a census, and lacked full orbit x arm distributions.
Before launch, the frozen design was replaced so that:

- offsets `64..255` are the 3,072-block inferential sample (192 per orbit),
  while offsets `0..63` are a disjoint 1,024-block A/A holdout;
- the primary contrast and A/A intervals keep all 16 orbits exactly once and
  resample paired blocks within orbit; orbit resampling is reported only as a
  modeled-superpopulation sensitivity;
- every required metric receives an 80-row orbit x arm distribution table,
  and per-orbit contrast points are labelled descriptive/exploratory; and
- interpretation is limited to a same-action sampled level/model association.
  The one crater model, sampled floor models, generator construction, and hash
  behavior remain bundled, so the study cannot isolate a causal conductor
  effect.

Runner/analyzer review also found that fully resealed archives could carry
extra contradictory fields in otherwise successful plan, manifest, receipt,
or session objects. Exact schemas now reject those fields. The review further
closed uint64 and overflow-column acceptance, frozen-input/TOCTOU races,
compiler timeout, elapsed-receipt tolerance, worker-start/progress/interrupt
failure propagation, unsafe CLI abbreviations/duplicates, and file/directory
durability. These were launch blockers or hardening defects, not scientific
findings.

The replacement frozen manifest has SHA-256
`4a29804365a6a21c0a39d098d3be18df937687c9dd5b68dbea3d6f0b3af01a3c`.
In clean temporary repository `/tmp/m51-final-repo.qfWIGH`:

- `run_replication.py --selftest-only` produced
  `/tmp/m51-final-selftest.O7BEQc`, passed the exact build and 35 real
  selftests, sealed 19 files, launched zero rho jobs, and retained binary hash
  `4db25d2113bc39cce71e24b317b4c3ded69a7e177a23f86c4dbb2277bafdb3e0`;
- a fake `taskset` shim delegated selftests to the real binary but generated
  deterministic structurally valid run CSVs. It produced the non-scientific
  400-job/25,600-row archive `/tmp/m51-final-synthetic.o28lUs`; and
- `analyze.py` accepted that archive into
  `/tmp/m51-final-analysis.a1wVsA`, reporting the exact 3,072/1,024 split,
  96 descriptive orbit-contrast rows, 80 orbit x arm rows, five A/A rows, and
  a rendered SVG. It also accepted the relocated byte-identical archive
  `/tmp/m51-final-relocation.jsxAp7/run`.

After recomputing every dependent hash and the complete archive seal, eight
adversarial copies were rejected: extra plan fields, extra run-manifest fields,
contradictory nested session failure metadata, extra build/selftest/job failure
fields and non-null receipt working directories, a compensating setup/walk
counter split, and a missing raw job. Separate checks rejected no-resume,
duplicate/abbreviated CLI options, uint64 overflow, and trailing CSV columns.
The 2-second bookkeeping tolerance accepted `limit+1.9` and rejected
`limit+2.1`. Injected compiler timeout, peer exit, launcher interrupt,
worker-thread start failure, and progress-log failure tests all propagated;
compiler and peer cancellation completed in 1.003 and 0.304 seconds, and the
interrupt stopped both recorded process groups in 0.104 seconds.

All replacement runs above are design, core-selftest, or synthetic harness
checks. The fake-run archive's session schema necessarily says
`scientific_run=true`, but its run CSVs were generated by the documented test
shim rather than `rho run`; therefore none of its labels, intervals, or values
are scientific evidence. No m=51 collision-walk benchmark was launched, no
scientific rho outcome was observed, and no weak-curve, conductor-effect,
transfer, or ECDLP-hardness conclusion exists at freeze time.

## 2026-10-13 — final parser-parity correction (non-evidence)

After the replacement verification above, independent review found that an
explicit empty `--cores=` was treated by the runner as if the option had been
omitted, while the analyzer correctly rejected the resulting empty recorded
core list. The runner now rejects an explicitly empty core option before
creating an output root. This one-line fail-early correction superseded the
unlaunched `4a298043...` commitment recorded above; that older entry is kept as
append-only history.

The final `FROZEN.sha256` SHA-256 is
`149a9028aeda673dd833fb699543b9c7f6d7ed59dff17e5f1d18d96a505508d9`.
Against clean repository `/tmp/m51-release-repo.bbHQRT`, the final-hash
replacement checks were:

- exact build plus 35 real selftests, zero rho jobs, and a 19-entry seal in
  `/tmp/m51-release-selftest.tFOYjC`;
- 400 mocked 64-target jobs, 25,600 normalized rows, and a 424-entry seal in
  `/tmp/m51-release-synthetic.z10wkt`;
- accepted analysis and SVG in `/tmp/m51-release-analysis.XfaMzA`, with 3,072
  inferential blocks, 1,024 held-out A/A blocks, and 80 orbit x arm rows;
- accepted relocated archive `/tmp/m51-release-relocation.fwAqU1/run`; and
- rejection of all eight fully resealed plan, manifest, session, receipt,
  counter, and missing-raw adversarial copies under
  `/tmp/m51-release-tamper-*`.

Both separated and nonempty `--option=value` forms were exercised by the
replacement runs. Explicit empty `--cores=` exited nonzero without creating
its requested output. The final frozen manifest verifies in full. These remain
harness and selftest observations only: no scientific benchmark, measured rho
outcome, or weak-curve conclusion was produced.
