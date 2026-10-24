# P29 graph-arm phased execution: fixed public controls

**Date:** 2026-10-22 PDT. **Conductor:** T-4750 followed by T-4753 after an
expired service lease. **Raw code and records:** `bb8caa9722`; exact local
executables and build receipt: `3813ea4635`. This report describes
implementation-control observations only. It does not approve or analyze the
prospective discovery experiment.

## Object and question

The source is `E/F_320092037: y²=x³+105931039x+284015384`, prime order
`r=320091991`, generator `G=(0,50656410)`. The archived eight-edge path of
degree-7 separable maps over `F_320092037` reaches canonical vertex 8,
`y²=x³+218000848x+38636553`, with transported
`G=(148951155,154566416)` [internal: archived
`../path_transport/controls/p29-twoedge-attempt1/edge-0008.json` and
independent chain replay in `../path_transport/full_path_20261016/report.md`].
The check asks whether the existing exact triple collector, independent
ordered-count oracle, and rank verifier can run under a graph-specific
write-once wrapper, and whether fixed public source/check targets conserve
their exact relation records under the archived base transport.

## Program, inputs, and retained failures

`preparation/execute_graph_prepared.py` runs four bounded phases: independent
prepared-input check, Rust collector, C++ ordered-count oracle, and Python
relation/rank replay. It retains every phase command, stdout, stderr, elapsed
time, sampled RSS, executable/source digests, host and interpreter identity in
`attempt/receipt.json` and `attempt/events.jsonl`. Scientific mode requires a
clean frozen source, exact stage quota, a post-freeze seed commitment, and a
Coordinator admission matching all input, source, binary, schedule and
checkpoint digests. The repository experiment runner still owns dispatch and
official admission. Control mode is capped at 128 fixed public targets.

The public test roots were `B×32` for base generation and `T×32` for target
generation. Both 128-target arms used the same derived coefficients; Q was
transported through the common generator rule. The source used native
`low_x` at vertex 0, and vertex 8 used `graph_transport` of that source base.
The exact commands and prepared inputs are in each `control-*/command.json`,
`prepared.txt`, and `manifest.json`. [`build.json`](build.json) binds the
retained macOS executables to Rust 1.93.1 and Apple clang 17.0.0, the source
hashes, and the build commands. The controls ran on a dirty implementation
worktree before their raw commit; the receipts record that state.

| Attempt | Requested targets | Outcome | Cause or exact control result |
| --- | ---: | --- | --- |
| `control-1` | 8 | failed before phases | Checkout Python 3.13 lacked `psutil`. |
| `control-2` | 8 | failed input check | Wrapper initially passed positional arguments to a flag-only verifier; phase returned code 2. |
| `control-3` | 8 | completed control | Input, oracle and rank checks passed; all eight fixed targets had zero triples. |
| `control-4` | 128 | completed control | Vertex 8: five nonempty/useful targets; 30 raw ordered triples; five independent coefficient rows and rank increments. |
| `control-5-source` | 128 | completed control | Source: the same five useful targets, 30 ordered triples and rank five. |

The two failures were retained rather than reused or overwritten. The
successful controls used the installed Python 3.12.8 environment with
`psutil 7.2.2`. At vertex 8, the recorded phase elapsed times were 0.457 s
input verification, 0.108 s collector, 0.097 s count oracle, and 0.091 s
rank replay. These are per-process observations on this loaded host, not a
campaign runtime or speed comparison [internal: `control-4/attempt/receipt.json`].

## Exact transport observation

The independent C++ ordered-count vector is byte-identical for the 128
source and vertex-8 targets: SHA-256
`0c6154c7b13f31283b2561e1b09bd1ae62f8ae8fca56e0d1a2b6b5983b87d479`.
The Rust collector's complete target/triple output is also byte-identical:
SHA-256 `18b36e791aa0922a9259e9ad9542ba7b9a4ae96458060658bff7da85f8567440`.
Each arm's verifier independently matched every target's ordered count and
replayed the five reported group-law triples and rank increments. The
[`count-comparison-v2.json`](count-comparison-v2.json) record and saved phase
outputs support these statements [internal]. The editable
[`plot_counts.py`](plot_counts.py) and [SVG](counts.svg) plot the raw per-target
vector and its cumulative count; no uncertainty interval applies to equality
of this fixed finite vector.

## Limits and next action

This is a fixed public control, outside both post-freeze discovery and fresh
confirmation. The 128-target result does not estimate graph-wide relation
yield. It does not time a Semaev/Gröbner decomposition solver or complete an
ECDLP cost comparison. P37 full-size collector RSS and runtime remain to be
measured under a runnable approved contract. The next action is to bind this
wrapper, exact check-arm quotas, seed custody, and output paths to a versioned
graph experiment; the Coordinator can approve only after the execution-state
checker reports ready. The earlier P29/P37 graph diagrams were checked: this
control adds no new vertex or map and changes no canonical graph edge.
