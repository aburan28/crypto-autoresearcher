"""Check the local static reader's comparison and integrity payloads."""

import argparse
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", type=Path)
    args = parser.parse_args()
    data = args.site / "data"
    comparison = json.loads((data / "comparisons.json").read_text())
    integrity = json.loads((data / "integrity.json").read_text())
    meta = json.loads((data / "meta.json").read_text())
    benchmark = comparison["benchmarks"]
    require(benchmark.get("error") is None, "benchmark payload has an error")
    require(len(benchmark["rows"]) == 9, "expected exactly nine benchmark rows")
    require(meta["mode"] == "static", "reader mode is not static")
    require(integrity["unparseable_state"] == "complete", "integrity sweep incomplete")
    print(json.dumps({
        "source_commit": meta["commit"],
        "mode": meta["mode"],
        "benchmark_rows": len(benchmark["rows"]),
        "benchmark_error": benchmark.get("error"),
        "unparseable_records": len(integrity["unparseable"]),
        "unparseable_state": integrity["unparseable_state"],
        "scope": "local generated reader payload; not a deployment or measurement replay",
    }, indent=2))


if __name__ == "__main__":
    main()
