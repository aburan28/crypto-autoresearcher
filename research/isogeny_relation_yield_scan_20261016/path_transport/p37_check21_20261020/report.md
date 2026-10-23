# P37 source-base transport: edge 21 control (2026-10-20)

This is an observation-only implementation control. It extends the archived degree-7 P37 path by one edge and independently replays the saved source base. It does not collect relation targets or measure relation yield, rank, or ECDLP cost.

## Inputs and identity

- Source stratum: P37 over `F_81640512137`, prime group order `81640511861`, with 1,600 x-orbits and both signs (3,200 points).
- Archived walk digest: `523686cad4acf24d6c54dc73e25c9527fcd6337912643053674ca5b87129d281`. Producer script digest: `2829ef00e3727216f91bda4cccb386f3ea54db7fcdedf87954b5eab3362cc84e`. Sage version recorded in the chain manifest: `10.10.rc0`.
- Previous committed checkpoint: edge 20; new checkpoint: [`edge-0021.json`](../controls/p37-twoedge-attempt1/edge-0021.json), SHA-256 `d2e283edb3ab0cbb4078d8c01b587c8ab25b0dcf11194324d8e8eef7eb982f54`.
- Edge 21 destination `j`: `49775280396`. Saved base digest: `d4415611af920a97baefd526cf845ca71c8392d118ccc10ef72b0858c065b841`. This edge was an extra terminal control; the scheduled check stride is four.
- Producer source checkout was at `19540ee829` with no tracked dirty files. The checkpoint was committed as `befd8ca280` and its branch later merged current main.

## Exact commands and measured observations

Producer from repository root:

```sh
gtimeout 360 /usr/bin/time -l sage -sh -c 'DOT_SAGE=/tmp/ectd-p37-edge21-sage PYTHONDONTWRITEBYTECODE=1 python3 research/isogeny_relation_yield_scan_20261016/path_transport/transport_path.py --stratum P37 --max-edges 21 --output-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p37-twoedge-attempt1 --resume'
```

Independent replay from repository root:

```sh
gtimeout 240 /usr/bin/time -l python3 research/isogeny_relation_yield_scan_20261016/path_transport/verify_chain.py --stratum P37 --checkpoint-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p37-twoedge-attempt1
```

The producer saved edge 21 in **7.393 s** of its per-edge timer. The shell meter recorded **25.83 s wall, 3.84 s user CPU, 1.12 s system CPU**, and **263,651,328 bytes maximum RSS** for the whole resume command. The independent verifier reported `status: pass`, **21 edges** and **67,200 point images** replayed, with terminal hash `d2e283edb3ab0cbb4078d8c01b587c8ab25b0dcf11194324d8e8eef7eb982f54`. Its shell meter recorded **5.56 s wall, 1.14 s user CPU, 0.14 s system CPU**, and **76,316,672 bytes maximum RSS**. The two meters recorded zero swaps. These are host-contended timings, not comparative performance evidence.

Raw outputs: [producer stdout](producer.stdout), [producer stderr](producer.stderr), [verifier stdout](verify.stdout), [verifier stderr](verify.stderr). The [SVG](edge_times.svg) plots checkpoint-recorded per-edge time through edge 21; [render_graph.py](render_graph.py) regenerates it. The first 20 plotted values are earlier archived controls, and only edge 21 was produced here.

## Scope and next check

The replay checks the hash chain, independent Vélu codomain, canonical scaling, all signed-base point images, generator image and curve membership on scheduled or terminal vertices. It establishes consistency for these saved 21 edges under the verifier's arithmetic. The remaining P37 edges 22–256, graph-wide target streams, relation collection, rank comparison and complete ECDLP timing remain open. The next scheduled check vertex is edge 24.
