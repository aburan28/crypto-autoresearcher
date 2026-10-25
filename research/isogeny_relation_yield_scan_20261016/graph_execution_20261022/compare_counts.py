"""Compare fixed public source and check-vertex ordered-count vectors."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "control-5-source"
GRAPH = HERE / "control-4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    receipt = json.loads((directory / "attempt/receipt.json").read_text())
    if receipt["status"] != "completed_control":
        raise ValueError("fixed control did not complete")
    lines = (directory / "attempt/count.stdout").read_text().splitlines()
    values = [int(line.split("\t")[2]) for line in lines[1:]]
    if len(values) != manifest["target_count"]:
        raise ValueError("count-vector length differs")
    return manifest, values


def main():
    source, left = counts(SOURCE)
    graph, right = counts(GRAPH)
    if (source["stratum"], source["index"], source["arm"],
            graph["stratum"], graph["index"], graph["arm"]) != (
            "P29", 0, "low_x", "P29", 8, "graph_transport"):
        raise ValueError("source/check-vertex pair identity differs")
    if (source["target_count"] != graph["target_count"] or
            source["target_root_sha256"] != graph["target_root_sha256"] or
            source["target_vector_sha256"] == graph["target_vector_sha256"]):
        raise ValueError("target root or transported-point identity differs")
    if left != right:
        raise ValueError("exact source/graph targetwise ordered counts differ")
    source_collector = SOURCE / "attempt/collector.stdout"
    graph_collector = GRAPH / "attempt/collector.stdout"
    if source_collector.read_bytes() != graph_collector.read_bytes():
        raise ValueError("source/graph collector records differ")
    source_rank = json.loads((SOURCE / "attempt/rank_verify.stdout").read_text())
    graph_rank = json.loads((GRAPH / "attempt/rank_verify.stdout").read_text())
    for key in ("useful_targets", "useful_triples", "rank_increments", "unknown_columns"):
        if source_rank[key] != graph_rank[key]:
            raise ValueError("source/graph rank metric differs: " + key)
    print(json.dumps({"schema": "ectd.fixed-public-count-transport.v2", "status": "pass",
                      "targets": len(left), "nonempty_targets": sum(value > 0 for value in left),
                      "ordered_triples": sum(left), "source_count_sha256": sha(SOURCE / "attempt/count.stdout"),
                      "graph_count_sha256": sha(GRAPH / "attempt/count.stdout"),
                      "collector_sha256": sha(source_collector),
                      "targetwise_ordered_equal": True, "collector_records_equal": True,
                      "useful_targets": source_rank["useful_targets"],
                      "useful_triples": source_rank["useful_triples"],
                      "rank_increments": source_rank["rank_increments"],
                      "unknown_columns": source_rank["unknown_columns"],
                      "scope": "fixed public implementation control; no discovery inference"},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
