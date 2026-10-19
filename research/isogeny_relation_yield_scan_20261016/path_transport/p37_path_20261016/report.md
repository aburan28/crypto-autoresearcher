# P37 source-base transport to check vertex 20 — 16 October 2026

**Question and scope.** Task T-3406 continued the archived P37 source `low_x` signed base from edge 4 to the prespecified degree-7 check vertex 20. This is an implementation control and observation report. It makes no native-base relation-yield, rank, ECDLP-cost, or hypothesis-status decision.

The archived P37 graph `../../walk-p37-256.jsonl` has SHA-256 `523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281`, field `p=81640512137`, prime group order `r=81640511861`, `D_K=-19`, and source `f_pi=f_E=131101`. The first four edge checkpoints and source were already archived. The source base contains 1,600 x-orbits and 3,200 signed points. The producer and independent verifier are `../transport_path.py` and `../verify_chain.py` at run revision `4ff21a087f9ea69874c4f1338550bb28245d3fbb`. Sage was 10.10.rc0 on macOS arm64; newly written checkpoints and logs were untracked during execution, with no tracked source edits. [internal: archived graph, checkpoint manifest, git]

The exact producer command, run from the repository root with stdout/stderr redirected to `p37-resume-to20.stdout` and `p37-resume-to20.time.stderr`, was:

```sh
gtimeout 420 /usr/bin/time -l sage -sh -c 'DOT_SAGE="$PWD/research/isogeny_relation_yield_scan_20261016/path_transport/p37_path_20261016/.sage" PYTHONDONTWRITEBYTECODE=1 python3 research/isogeny_relation_yield_scan_20261016/path_transport/transport_path.py --stratum P37 --max-edges 20 --output-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p37-twoedge-attempt1 --resume'
```

It exited zero after writing edges 5–20. The saved chain now has 21 checkpoints including the source. The terminal edge-20 SHA-256 is `c7b4ef4b29ca188108c96fefaa357608f4d5c15283f0ffd8e60eabcb4aad8cc2`. The process resource log recorded 345.33 s wall, 18.16 s user, 2.59 s system, and 229,146,624 B maximum RSS. These figures cover the continuation only; no CPU pinning, concurrent-load trace, repeat distribution, or memory kill guard was recorded. A seven-minute process watchdog bounded this attempt. Per-edge internal elapsed values for the new edges sum to 305.856 s; their difference from wall includes startup, checkpoint I/O and other work. These are diagnostics, not a solver-speed comparison. [internal: named process logs and checkpoints]

The final independent replay command was:

```sh
gtimeout 180 /usr/bin/time -l python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/verify_chain.py --stratum P37 --checkpoint-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p37-twoedge-attempt1
```

It exited zero. `p37-check20-verify.stdout` reports 20 edges checked, 64,000 point images replayed and the same terminal checkpoint hash. The verifier recomputes the source base, graph/model identity, rational point maps, generator images, scheduled check-vertex orbit counts, curve membership and every checkpoint hash link. The producer separately checks 17 Sage map/dual sample points per new edge. The verifier resource log recorded 19.87 s wall, 0.99 s user, 0.23 s system, and 70,942,720 B maximum RSS. [internal: named verifier outputs, `../verify_chain.py`]

`edge_times.svg` plots the 20 archived per-edge internal elapsed values, with edges 1–4 shown as the earlier control. Its editable source is `render_report.py`; the PDF was rendered and inspected. The earlier `../chain.svg` continues to depict the first P29/P37 check vertices and the study `../../graph.svg` depicts the graph plan, so their stated scopes remain accurate. P29 now has a separate complete 2,048-edge transport archive (`../full_path_20261016/`). P37 edges 21–256, the post-freeze discovery target stream, graph-wide native-base relation collection, useful rank and complete same-point solve costs remain open.
