# First check-vertex targetwise count control — 16 October 2026

**Scope and question.** This is a public implementation control for task T-3387. Do the complete signed source `low_x` bases and their saved degree-7 transports have identical exact ordered three-point decomposition counts on the same 128 fixed target scalars at P29 index 8 and P37 index 4? These are control points, not the graph-wide discovery or confirmation streams. This report records observations only; it makes no hypothesis-status, relation-yield advantage, or ECDLP-cost decision.

## Inputs and method

The source inputs are the archived P29/P37 graph files and the independently replayed checkpoint chains in `../controls/`. The P29 source has `p=320092037`, `r=320091991`, 256 x-orbits and 512 signed base points; P37 has `p=81640512137`, `r=81640511861`, 1,600 x-orbits and 3,200 signed points. Source and destination checkpoints are indices 0/8 and 0/4. The control generator is the saved transported generator. `transport_count_control.py` independently replays each checkpoint chain, verifies the base and group equation, and writes a paired prepared-input file for each endpoint. Its committed SHA-256 is `c6c55a0d5538059514627bbd7b31b9d71bd1a6c691a12dfe39ee0ff5e9ad8619` at run revision `94efd47f02ff21671b895d561876e06c81fee8d2` (the source commit was `90f5ac1c94`). The worktree had this untracked evidence directory and no tracked edits at execution. [internal: `p29-attempt1/manifest.json`, `p37-attempt1/manifest.json`, git]

The 128 target scalars in each stratum are deterministic, distinct, nonzero labels derived from the public string `ectd-transport-count-control-v1`, stratum, and draw index. Their `beta` cycles through 1..7, `Q=[7]G`, and `alpha=(s-7 beta) mod r`, so `R=[alpha]G+[beta]Q=[s]G`. This is a fixed public control selection; no random-sampling interval applies. The complete signed bases and target points are in the two `*.txt` files per stratum. The independent C++ ordered-count oracle is `research/conductor_relation_yield_20261014/count_verify.cpp`, SHA-256 `79aec82f6cc73bd7aba208f198976e293c59e5ace46e7cdc91be656ba22ddd7f`; the compiled binary SHA-256 is `f5a7babfda22365e6c91134936f9f869d6e27ac824367eec459d1b0bf902574e`. [internal: source, input manifests]

On macOS arm64, Apple clang 17.0.0 and Python 3.12.8, preparation and compilation completed with exit code zero. The exact commands, each with stdout/stderr redirection to correspondingly named files under this directory, were:

```sh
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/transport_count_control.py prepare --stratum P29 --output research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p29-attempt1
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/transport_count_control.py prepare --stratum P37 --output research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p37-attempt1
gtimeout 120 c++ -std=c++17 -O2 research/conductor_relation_yield_20261014/count_verify.cpp -o research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/count_verify
gtimeout 300 /usr/bin/time -l research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/count_verify research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p29-attempt1/source.txt
gtimeout 300 /usr/bin/time -l research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/count_verify research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p29-attempt1/transported.txt
gtimeout 300 /usr/bin/time -l research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/count_verify research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p37-attempt1/source.txt
gtimeout 300 /usr/bin/time -l research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/count_verify research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p37-attempt1/transported.txt
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/transport_count_control.py compare --output research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p29-attempt1
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/transport_count_control.py compare --output research/isogeny_relation_yield_scan_20261016/path_transport/count_control_20261016/p37-attempt1
```

## Observations

| Stratum / endpoint | Targets compared | Nonempty targets | Ordered relations | Counter wall / CPU user+sys | Max RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| P29 source | 128 | 15 | 90 | 1.19 / 0.07 s | 8,994,816 B |
| P29 index 8 | 128 | 15 | 90 | 1.08 / 0.09 s | 9,011,200 B |
| P37 source | 128 | 7 | 48 | 66.11 / 3.29 s | 288,407,552 B |
| P37 index 4 | 128 | 7 | 48 | 79.38 / 4.27 s | 288,096,256 B |

The `source.count` and `transported.count` files are byte-identical within each stratum: SHA-256 `d7c0e65b34938f846884b6bcc59483bde36652975f85145d5660fe1dc90fae55` for P29 and `f799d1cd80cdacd125d4ad0e1681ce5e704da836c569b3e12b11763ba144d473` for P37. `comparison.json` records 128/128 equal ordered counts in each stratum. P29 has fifteen targets with count 6; P37 has six with count 6 and one with count 12. `counts.svg`, generated by `render_report.py` from the raw `.count` files, shows every nonzero target position. [internal: paired `.count`, `comparison.json`, native `*.time.stderr`]

The large P37 wall-to-CPU discrepancy was observed in both runs. No processor pinning, concurrent-load trace, or repeat distribution was captured, so these wall times are diagnostic observations and cannot support a relative speed claim. Each process was limited to 300 seconds; no memory kill guard was installed. The observed maximum RSS stayed below 300 MB. No count run timed out or failed. The first pre-freeze import smoke failed because the sparse checkout lacked the `tools` dependency; materializing that existing directory fixed it before the source commit and did not alter any scientific input. [internal: command logs; development smoke output in session]

## What this establishes and leaves open

The exact ordered-count oracle independently evaluated both full signed bases at the first check vertices and found targetwise equality for these fixed public points. The counter uses the same C++ implementation on both endpoints, so this check does not independently certify the counter's completeness for every point in either large group. The previous small-group exhaustive oracle and two-edge planted controls cover narrower correctness checks. The main study still needs full-path transport, the post-freeze discovery target stream, native factor-base comparisons at all scheduled vertices, rank replay, and complete same-point solve costs. The graph-wide protocol remains a draft; these control counts are excluded from its inferential sample.

The existing `../chain.svg` and study `../../graph.svg` were checked. They depict path geometry and source-base transport and contain no targetwise count series, so their source and rendering remain accurate. This control's new count series is in `counts.svg` and the inspected `report.pdf`. [internal: named graph sources]
