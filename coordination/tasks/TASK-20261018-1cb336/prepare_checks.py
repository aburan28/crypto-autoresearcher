#!/usr/bin/env python3
"""Compile sources and run SYNTHETIC controls only; never frozen worksheets."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("metadata", HERE / "envelope.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if not output.is_relative_to(HERE):
        raise ValueError("preparation output must remain in the handoff's own scope")
    output.mkdir()  # exclusive even for compilation/synthetic observations
    receipt = {"kind": "compile-and-synthetic-controls-only", "frozen_worksheet_executed": False,
               "commands": [], "sources": {}}
    codes = ["95f69f", "c9110e", "c9c5a4", "d68ac9", "efafc0", "f7310e"]
    passed = True
    for code in codes:
        config = M.read(M.ROOT / "experiments" / ("EXP-ECDLP-" + code) / "implementation" / "config.json")
        for route in ("a", "b"):
            binary = output / (code + "-" + route)
            source = config["routes"][route]
            header = HERE / ("native_" + route + ".hpp")
            receipt["sources"][source] = M.digest(M.ROOT / source)
            receipt["sources"][header.relative_to(M.ROOT).as_posix()] = M.digest(header)
            compiler = config["compiler"]
            M.same_hash(compiler["path"], compiler["sha256"])
            for item in compiler["system_dependencies"]:
                M.same_hash(item["path"], item["sha256"])
            build = M.subprocess_receipt([compiler["path"], *compiler["flags"], source, "-o", str(binary)])
            entry = {"experiment_id": config["experiment_id"], "route": route, "compile": build}
            try:
                if build["returncode"] == 0:
                    entry["binary_sha256"] = M.digest(binary)
                    # This is the ONLY invocation of the compiled native source.
                    entry["synthetic_control"] = M.subprocess_receipt([str(binary), "--self-test"])
                else:
                    passed = False
                passed &= entry.get("synthetic_control", {}).get("returncode") == 0
            finally:
                binary.unlink(missing_ok=True)
            receipt["commands"].append(entry)
            print(code, route, "compile", build["returncode"], "synthetic", entry.get("synthetic_control", {}).get("returncode"), flush=True)
    receipt["metadata_tests"] = M.subprocess_receipt([
        sys.executable, "-B", "-m", "unittest", "discover", "-s", str(HERE), "-p", "test_envelope.py", "-v"])
    passed &= receipt["metadata_tests"]["returncode"] == 0
    receipt["passed"] = passed
    M.write(output / "receipt.json", receipt)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
