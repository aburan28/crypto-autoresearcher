# Checkpointed source-base transport

This directory implements the preparation control for the archived P29 and
P37 degree-7 walks. It transports the fixed source `low_x` signed base through
each saved isogeny, writes one immutable checkpoint per vertex, and verifies
the chain independently with integer arithmetic. It does not collect
relations or time an ECDLP solver.

The first two edges were completed under T-3350. After Conductor's service
recovery, T-3361 extended those same write-once chains to the first scheduled
all-point check vertices: P29 index 8 and P37 index 4. The retained failed
Sage-launch attempt and successful continuations are under `controls/`.

From the repository root, use the installed Sage shell to run the producer:

```sh
gtimeout 300 sage -sh -c 'DOT_SAGE="$PWD/research/isogeny_relation_yield_scan_20261016/path_transport/.sage" PYTHONDONTWRITEBYTECODE=1 python3 research/isogeny_relation_yield_scan_20261016/path_transport/transport_path.py --stratum P29 --max-edges 8 --output-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p29-twoedge-attempt1 --resume'
```

The `sage` wrapper resets `DOT_SAGE`; set it inside `sage -sh -c`, as above.
Use a fresh output directory for a new chain. A resume requires the exact
producer script hash and graph hash recorded in its manifest. The producer
never overwrites a checkpoint. Recheck a chain with:

```sh
python3 -B research/isogeny_relation_yield_scan_20261016/path_transport/verify_chain.py --stratum P29 --checkpoint-dir research/isogeny_relation_yield_scan_20261016/path_transport/controls/p29-twoedge-attempt1
```

Use `P37` and its corresponding directory for the other stratum. The verifier
checks every stored base point and generator across every edge, the checkpoint
hash chain, model and raw codomain identities, source-base definition, and
the fixed check-vertex schedule. The report in this directory records exact
results and limits.
