# Implementation Contract V1

## Authority

Status: `review_required`.

This document authorizes nothing by itself. It freezes a proposed source and
development boundary for independent review. The experiment specification
continues to have `approved_by=null`, zero active resources, and
`maximum_runs=0`.

The only possible next transition is approval for source implementation.
Registered curve seeds, factor-base seeds, matrix rows, launch-plan design, and
experiment execution remain unreachable until later explicit decisions.

## Pinned protocol

- Protocol commit:
  `c0c7f0e5abd0a1220454a2def5b836c639ab2b69`.
- Protocol version: `6`.
- Main contract SHA-256:
  `89b91674bc901173916f276a3ea7fb46476d9f3c1004d52724bf068c51ec9f9f`.
- Specification SHA-256:
  `68bd527d4545fac6b1b18edb2537adb08e406d3738d0ea84216e5276fd1280b3`.
- Inherited producer SHA-256:
  `f9dc78ca8ff3b8d41d1e99b62a5d82a09c180ef1953dbb7401171882209dcea8`.
- Inherited verifier SHA-256:
  `4310f6d5eeacace558a79670c944c55961f89f0c1db4aaee4d8b20d361501199`.

These hashes must be reconciled by the implementation-design receipt.

## Proposed source boundary

The implementation may create only:

- `src/sgcp_secant_producer.py`;
- `src/sgcp_secant_optimizer_worker.py`;
- `src/verify_sgcp_secant.py`;
- `tests/test_sgcp_secant_rep.py`.

The paths are relative to this experiment except for the repository test.

The producer may hash-check and load the pinned inherited producer solely for
curve arithmetic, exact generated-curve and factor-base derivation, formal
evaluation, graph construction, model metrics, pair-output construction, and
the exact optimizer. It must add the v6 chart, slope, hash-control, table,
transcript, and orchestration logic in the new source.

The independent verifier must not import, execute, or parse Python objects from
the new producer, the optimizer worker, either inherited SGCP source, or any
prior SGCP verifier. It must separately implement EC arithmetic, transcript
derivation, fibers, slopes, controls, charts, formal compiler, graph, objective
replay, accounting checks, and terminal classification. An AST and loaded-module
audit must enforce this boundary.

No shared Python module is allowed. Immutable JSON manifests may be shared as
inputs, but the verifier must validate their pinned SHA-256 values before use.

## Derivation boundary

Source implementation must reproduce the pinned inherited
`generated_curve(...)` and `factor_base(...)` transcripts byte for byte.
Registered execution additionally requires a differential receipt over at
least one nonregistered seed per accepted and rejected branch. That receipt is
not authorized by this design and does not yet exist.

Future canonical attempt ceilings are:

- curve attempts: `1024` per registered curve seed;
- factor-base attempts: `256` per curve/factor-base seed;
- optimizer attempts: exactly one per compiler/cap cell;
- verifier attempts: exactly one per compiler/cap cell.

Attempt-cap exhaustion is `INCONCLUSIVE`. Attempts are append-only and charged.

## Canonical JSON

Every artifact is an exact JSON object encoded with:

```text
sort_keys=true
separators=(",",":")
ensure_ascii=true
allow_nan=false
terminal_newline=true
```

Digests of JSON values exclude the terminal newline unless the field explicitly
says `file_sha256`. Exact parsers reject duplicate keys, floats, non-ASCII
bytes, unknown keys, integers outside `0..2^63-1`, and booleans where integers
are required.

The raw result has exact top-level keys:

```text
schema, protocol_version, experiment_id, claim_status, bindings, execution,
parameters, controls, fixtures, matrix, accounting, terminal, result_sha256
```

`schema` is `sgcp-secant-representative-result-v6`.
`result_sha256` hashes the canonical object with that field omitted.

## Command surface

Development controls:

```bash
python3 -I -S -B experiments/EXP-SGCP-SECANT-REP-001/src/sgcp_secant_producer.py \
  --mode controls \
  --fixtures experiments/EXP-SGCP-SECANT-REP-001/control-manifest-v1.json \
  --output RUN/raw-result.json

python3 -I -S -B experiments/EXP-SGCP-SECANT-REP-001/src/verify_sgcp_secant.py \
  --input RUN/raw-result.json \
  --fixtures experiments/EXP-SGCP-SECANT-REP-001/control-manifest-v1.json \
  --output RUN/verification.json \
  --maximum-nodes 5000000
```

The producer alone may spawn:

```bash
python3 -I -S -B experiments/EXP-SGCP-SECANT-REP-001/src/sgcp_secant_optimizer_worker.py \
  --input CELL/input.json --output CELL/result.json --node-cap N
```

Artifacts use exclusive atomic publication. Stdout is one canonical receipt
with exact keys `schema,status,output,output_sha256,exit_code`. Diagnostics use
stderr only. Exit codes are `0` complete, `2` malformed/usage, `3` confirmed
invalid, and `4` incomplete/resource failure.

The controls mode rejects all registered curve and factor-base seeds. A future
canonical mode must remain absent until a reviewed launch plan adds it.

## Fresh-state rule

Every optimizer and verifier cell starts through `posix_spawn` plus `exec`.
The startup receipt requires:

- a unique 256-bit state nonce;
- no checkpoint reads or undeclared file descriptors;
- empty replay, primary, metric, and full-model caches;
- null incumbent;
- empty frontier;
- empty-frontier SHA-256
  `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`;
- one branch-order digest shared by all 32 compiler types.

Same-process second-cell use, nonempty state, or compiler-dependent branch
order is `INVALID`.

## Workload ceiling

The registered matrix would contain:

- 36 chart fixtures;
- 1,152 compiler packets;
- 4,608 optimizer cells;
- 4,608 deterministic verifier replays;
- 4,608 independent verifier proofs.

At inherited ceilings this permits 41,472,000,000 search nodes and 10,416 child
processes before failures. This is a pre-run upper bound, not authorization.
Duplicate control tables and duplicate chart digests may not be pooled.

## Development-only budget

After a separate source-implementation approval, implementation may use at most
13 serial child invocations, each at most 60 seconds and 512 MiB peak RSS, with
64 MiB combined temporary and retained output. Parallelism is one.

The 13 invocations are exactly:

- three happy-path role controls;
- three fresh-state controls;
- three injected role failures after nonzero work;
- three exclusive-publication or I/O controls;
- one RSS-limit control.

Every receipt must say `scope=development_control` and
`evidence_eligible=false`. Development artifacts are not matrix rows,
experiment runs, hypothesis evidence, or ledger results.

## Post-implementation gate

No development invocation may run until all proposed sources exist and a
reviewed receipt freezes:

- source and test hashes;
- transitive dependency closure;
- control, mutation, and accounting-manifest hashes;
- focused static tests;
- exact command vectors and environment;
- resource containment;
- theory, accounting, and red-team `GO` decisions.

Registered execution requires a later launch plan and a later coordinator
decision. `maximum_runs` remains zero throughout implementation.

## Next concrete action

Review this contract and its three manifests at one exact commit. If all
reviewers return `GO`, authorize source implementation only.
