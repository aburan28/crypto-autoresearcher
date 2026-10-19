# Complete P29 checkpointed base transport — 16 October 2026

**Question and scope.** Task T-3394 continued the fixed P29 `low_x` source base through the archived 2,048-edge degree-7 walk. This is a transport implementation control and an observation report. It makes no graph-wide native-base relation-yield, rank, ECDLP-cost, or hypothesis-status decision.

## Frozen input and commands

The P29 graph is `../../walk-p29-2048-attempt2.jsonl`, SHA-256 `bf8f72ca28101947e14306e603dc0f117a8da983989fc1c17dc4af99c91cfc45`. Its source has `p=320092037`, prime group order `r=320091991`, `D_K=-19`, and source `f_pi=f_E=8209`. The signed source `low_x` base contains 512 points in 256 x-orbits. The archived checkpoint manifest binds producer SHA-256 `2829ef00e3727216f91bda4cccb386f3ea54db7fcdedf87954b5eab3362cc84e`, Sage 10.10.rc0, the graph digest, and the eight-edge prior control. The independent verifier SHA-256 is `5d8ff3338ac4661c3de3cb118efe040b6ebcd0be528dfe4e622f5383be2885cc`. The run branch began at `886d4cf56369f055d9d04bad6787ada5082c1a30`; new checkpoints and logs were untracked during execution, with no tracked edits. [internal: graph, checkpoint manifest, git]

From the repository root, attempt 1 used the following command with stdout and stderr redirected to `p29-resume.stdout` and `p29-resume.time.stderr` in this directory:

```sh
gtimeout 540 /usr/bin/time -l sage -sh -c 'DOT_SAGE="$PWD/research/isogeny_relation_yield_scan_20261016/path_transport/full_path_20261016/.sage" PYTHONDONTWRITEBYTECODE=1 python3 research/isogeny_relation_yield_scan_20261016/path_transport/transport_path.py --stratum P29 --max-edges 2048 --output-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p29-twoedge-attempt1 --resume'
```

It exited 124 at the 540-second watchdog after writing edge 1907; no `.partial` checkpoint remained. The tool did not flush a `/usr/bin/time -l` summary on forced termination, so peak RSS and measured wall/CPU time for this attempt are missing. Its stdout retains one record per completed edge. This is a bounded process stop, not a failed map or a mathematical result. The independent prefix verifier then exited zero, reporting 1,907 checked edges, 976,384 point images, and terminal checkpoint SHA-256 `05281e8dd67134943b52817576723778d37e41cd66ee5b24d65e5b77347dbcd3`. The verifier's raw stdout and native resource log are `p29-prefix1907-verify.*`. [internal: exact named files]

With a renewed Conductor claim, attempt 2 used the same `sage -sh -c` inner command and output directory, under `gtimeout 240 /usr/bin/time -l`, redirected to `p29-resume-attempt2.*`. It exited zero and reported 2,049 checkpoints including the source, terminal edge 2,048, and checkpoint SHA-256 `39d17f4eff4bd408f86b59c6a5cbf10980d99b3ddd5f4c3680c9e4b3607737f3`. The native log recorded 82.18 s wall, 5.61 s user, 1.64 s system, and 249,167,872 B maximum RSS for this continuation only. No CPU pinning or concurrent-load trace was captured, so these times are diagnostic, not an isogeny or ECDLP advantage measurement. [internal: `p29-resume-attempt2.stdout`, `.time.stderr`]

The final independent replay command was:

```sh
gtimeout 300 /usr/bin/time -l python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/verify_chain.py --stratum P29 --checkpoint-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p29-twoedge-attempt1
```

It exited zero. `p29-full-verify.stdout` reports all 2,048 edges and 1,048,576 saved point images replayed, with the same terminal checkpoint digest. The verifier independently recomputed point maps, source base, group/model identities, graph-linked kernels and every hash link; all 257 scheduled check vertices, indices divisible by eight including the source and endpoint, retain 256 distinct x-orbits and on-curve points. Its native log recorded 42.44 s wall, 6.78 s user, 0.77 s system, and 80,494,592 B maximum RSS. The producer separately checked 17 Sage map/dual sample points per new edge. [internal: `p29-full-verify.*`, `../verify_chain.py`, saved checkpoints]

## Observation and limits

The complete P29 source-base transport chain is saved and independently replayed on this fixed graph. `edge_times.svg` plots the 2,048 archived internal per-edge elapsed values (sum 557.017 s, median 0.216 s, maximum 3.407 s). These values omit process startup, checkpoint I/O, independent replay, and scheduler effects; the sum is not total wall time. The plot source is `render_report.py`; the PDF was rendered and inspected. [internal: all `edge-????.json`, chart source]

The existing `../chain.svg` depicts only the earlier first check vertices, and the study `../../graph.svg` depicts the archived graph. Both remain accurate within their stated scopes. This new figure records the complete P29 transport coverage. P37 remains checked through edge 4 of 256. Full targetwise equality has been exercised only on 128 fixed public control targets at the first check vertices (`../count_control_20261016/`), not on a post-freeze discovery stream. The native factor-base sweep, rank comparison, complete same-point solver, and matched rho accounting remain open.
