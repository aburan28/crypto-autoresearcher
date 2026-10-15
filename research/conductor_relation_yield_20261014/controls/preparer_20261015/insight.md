# Prepared-input algebraic control

- **Question:** Does the deterministic preparer use the same target stream for the native and random bases, transport that stream and the native base correctly under `u=2`, and construct valid points on each specified endpoint?
- **Workload:** Six specified endpoints (P29 crater, E1/E2/E3 floors, P37 crater/floor), four arms each, eight fixed public test targets per arm. The fixed test seeds are in `test_preparer.py`; they are not the post-freeze scientific seeds. The manifest marks the target count as outside the formal 32,768-target protocol.
- **Baseline and candidate:** Native base/targets as the reference; random base with identical native targets; transported native base/targets versus pointwise `u=2` mapping; rebuilt first-B base on the transformed curve. Each result is parsed independently and checked against its group equation.
- **Raw measurements:** [Receipt](receipt.json) binds the original source hashes, exact command, environment, elapsed time and raw [stdout](stdout) and [stderr](stderr). The command exited 0. No relation yield was measured.
- **Correctness:** For each endpoint, exact trial-division primality of `p` and `r`, a prime-order generator, and the Hasse bound imply group order `r`. The test checks every base point and target equation, target uniqueness, distinct random-base x-orbits, same targets for the native/random arms, and pointwise equality of the two transported target streams.
- **Cost and limits:** The receipt records total elapsed time and the host's raw child RSS field; it is a control cost, not a full endpoint estimate. Conductor, source-spec, and isogeny certificates remain to be bound. No full-size completeness or launcher control has run.

The preparer source and test were amended after the original receipt to add per-vector hashes and an explicit protocol target-count marker. The later version passed under its separate [receipt](amended_receipt.json), [stdout](amended.stdout), and [stderr](amended.stderr); the earlier raw capture remains unchanged.

A further amendment added `p` and `r` to the prepared manifest for the execution wrapper. The same algebraic control passed under [its own receipt](launcher_binding_receipt.json), [stdout](launcher_binding.stdout), and [stderr](launcher_binding.stderr).
