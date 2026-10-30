# Formal target pointer coverage at `2165804a`

Date: 2026-10-30 UTC. This is a navigation audit of one immutable Git tree, not an evidence review, experiment replay, theorem audit, or scientific decision. [Inventory](inventory.json), [drawing source](draw_coverage.py), and [SVG graph](coverage.svg) are retained here. The inspected PDF is content-addressed by [.artifacts.json](.artifacts.json); hydrate it with `python3 tools/artifacts/artifacts.py pull docs/reports/2026-10-30-formal-pointer-coverage`.

## Observation

| Count at commit `2165804af6c622d7b71d8893655b28fd93c1996b` | Value |
|---|---:|
| Experiment directories with `EXP-*` IDs | 2,790 |
| Registered formal target YAML files | 91 |
| Experiment IDs with a literal exact pointer in a registered target, its declared source, or its theorem source | 6 |
| Experiment IDs without such a pointer | 2,784 |
| Formal targets with such a pointer | 20 |
| Formal targets without such a pointer | 71 |

The [graph](coverage.svg) plots the two different denominators separately. It must not be read as a fraction of experiments proved. The six linked IDs are `EXP-BINSTD-8bdf86`, `EXP-FROB-91ee9c`, `EXP-FROB-b8cf21`, `EXP-GFPN-05ff43`, `EXP-NCP-001`, and `EXP-SEMBIN-4fa22c`.

All 91 target YAMLs parsed, and each declared source and theorem source resolved in its declared workspace. In particular, `scoped-odd-torsion-translation.yaml` uses the nested workspace `formal/scoped-obstructions`, so its theorem file resolves to `formal/scoped-obstructions/ScopedObstructions/Torsion.lean`.

## Method and provenance

`build_inventory.py` reads `git ls-tree` and `git show` at the frozen commit; it does not rely on which files a sparse checkout materializes. It enumerates all tracked files under `experiments/`, derives distinct `EXP-*` directory names, then scans each registered `formal/targets/*.yaml`, its declared `source`, and its `<workspace>/<theorem_file>` for exact directory-ID tokens. Every witness carries the scanned Git path and its SHA-256. Composite claim IDs such as `EXP-FROB-91ee9c-C4-ORDER-ARITHMETIC` are not counted as standalone target-spec tokens; a source file containing the exact ID can still link that target. The full path list digest and both tree IDs are in `inventory.json`.

Reproduce: `uv run --no-project --python 3.11 --with pyyaml python docs/reports/2026-10-30-formal-pointer-coverage/build_inventory.py . 2165804af6c622d7b71d8893655b28fd93c1996b > inventory.json`, then `python3 docs/reports/2026-10-30-formal-pointer-coverage/draw_coverage.py`. The committed inventory is the original frozen output; reruns should compare counts, paths, hashes and tree IDs while ignoring JSON formatting.

## Interpretation and next validation

An exact pointer makes a target easier to find. It does **not** prove that the Lean theorem states the research claim, that the theorem builds at current `main`, that historical experiments ran as described, or that a performance result is valid. The 2,784 IDs without a pointer may still have a relevant theorem under another name. The next work is to trace claims to exact theorem statements and hypotheses, run the pinned Lean build and axiom audit under the shared build admission gate, independently review semantic fidelity, and replay or verify the empirical evidence.

No canonical performance graph is changed by this pointer inventory. Other dashboards remain outside this report's verified scope.
