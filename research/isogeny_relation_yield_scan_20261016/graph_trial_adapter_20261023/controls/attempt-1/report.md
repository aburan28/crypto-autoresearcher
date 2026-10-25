# Graph trial adapter implementation control

2026-10-22, P29 vertex 0, fixed public roots from the archived preparation
control. The `low_x`, `graph_transport`, and `u2_transport` arms each used the
same eight target coefficients and 256 signed x-orbits (512 points). All three
adapter runs completed with `completed_control`; the independent checker
replayed group law, reported triples, ordered count, and rank. The two
transported arms matched the native source target by target. In these eight
targets, useful target count and rank increments were both zero for all three
arms. This small control checks plumbing and conservation only.

The first two attempts failed before or during `input_verify`: the selected
Python lacked `psutil`, then the isolated environment lacked `sympy`. Their
failure outputs remain in `/tmp/ectd_graph_trial_adapter_control` and
`/tmp/ectd_graph_trial_adapter_control2` on the producing host; the final
control used an isolated Python environment with `psutil 7.2.2` and
`sympy 1.14.0`. The final three complete outputs are copied beside this report.
The Rust collector was compiled with `rustc --edition=2021 -O`; the independent
C++ count oracle with `clang++ -O3 -std=c++17`. Binary hashes and exact runtime
commands appear in each `run/raw-result.json` and `run/manifest.yaml`
(`native/` holds the run files directly). The binaries lived under
`/tmp/ectd_graph_trial_adapter_bin` and are reproducible from the committed
sources, subject to a SHA-256 match before relocated replay.

The output archives preserve the prepared input, prepared manifest, raw phase
files, logs, and receipts. The original run manifests retain producing-host
absolute paths. The independent checker accepts relocated inputs by digest.
In a separate copied run, changing the first count-output row caused the
checker to exit nonzero with `count phase digest or status differs`.
The adjacent diagram shows the check chain. Scientific arm admission and full
graph execution remain open.
