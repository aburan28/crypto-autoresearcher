"""Fixed public preparation controls for the graph-transported base arm."""
from __future__ import annotations

import json
from pathlib import Path
import sys

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY / "preparation"))
from prepare_graph_input import SCHEDULE, prepare

ROOTS = (b"B" * 32, b"T" * 32)
WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}


def base_x(payload):
    lines = payload.decode().splitlines()
    size = int(lines[0].split()[5])
    return {int(lines[i].split()[2]) for i in range(1, size + 1, 2)}


def main():
    rows = []
    for stratum, walk in WALKS.items():
        for index in (0, SCHEDULE[stratum]["power_stride"]):
            graph, graph_meta = prepare(walk, index, "graph_transport", "discovery", *ROOTS, 8)
            native, native_meta = prepare(walk, index, "low_x", "discovery", *ROOTS, 8)
            assert graph_meta["generator"] == native_meta["generator"]
            assert graph_meta["Q"] == native_meta["Q"]
            graph_x, native_x = base_x(graph), base_x(native)
            assert len(graph_x) == len(native_x) == SCHEDULE[stratum]["B"]
            rows.append({"stratum": stratum, "index": index, "base_x_orbits": len(graph_x),
                         "native_graph_x_intersection": len(graph_x & native_x),
                         "checkpoint_sha256": graph_meta["checkpoint_sha256"],
                         "same_q_and_generator": True, "target_count": 8})
    print(json.dumps({"schema": "ectd.graph-arm-implementation-control.v1", "rows": rows,
                      "scope": "fixed public input preparation only"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
