#!/usr/bin/env python3
"""Zero-compute superseding analysis of EXP-CMFB-cea1d2 (recorded t8 RUN-CMFB-2010d3 left untouched).

Reads only the recorded raw results of RUN-CMFB-{2373be,5905c0,66b0fe,3dc120,42a578,e13f0e,c71d35}
through the frozen implementation/analyze.py, unmodified on disk. Two in-process changes bring the
analysis in line with the frozen specification text (defects D1, D2 of DEC-20261019-f33f3e):

  D1  MDE = 3.61 * rms_j sd_j / sqrt(n) with no inflation factor
      (code: 3.61 * sqrt(3) * 1.0025 * rms sd / sqrt(n)).
  D2  I10 null-spread reference 1.4 / sqrt(N)
      (code: count.sigma_rel_formula, the superseded independent-balls occupancy value).

Step 1 re-runs the UNCHANGED frozen analysis and must reproduce the recorded t8 exactly.
Step 2 applies D1 and D2 and reports every field that differs.  Nothing here is an official run.

    python3 superseding_analysis.py --out superseding_result.json
"""
import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
sys.path.insert(0, str(EXP / "implementation"))
sys.dont_write_bytecode = True

import analyze  # noqa: E402
import count  # noqa: E402

RUNS = EXP / "runs"
RECORDED = RUNS / "RUN-CMFB-2010d3" / "raw-result.json"


def scrub(o):
    """JSON-safe copy: numpy scalars and arrays to python."""
    if isinstance(o, dict):
        return {str(k): scrub(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [scrub(v) for v in o]
    if hasattr(o, "tolist"):
        return o.tolist()
    return o


def diff(a, b, path=""):
    """Leaf-level differences between two nested JSON values."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((f"{path}/{k}", "<absent>", b[k]))
            elif k not in b:
                out.append((f"{path}/{k}", a[k], "<absent>"))
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif isinstance(a, float) and isinstance(b, float):
        if not (a == b or abs(a - b) <= 1e-12 * max(1.0, abs(a), abs(b))):
            out.append((path, a, b))
    elif a != b:
        out.append((path, a, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    recorded = json.loads(RECORDED.read_text())

    # Step 1: the unchanged frozen analysis must reproduce the recorded t8.
    base = scrub(analyze.run_analysis(RUNS, official=True))
    # peak_rss_bytes is a process metric the driver adds to the raw result; timings are wall-clock.
    repro = [d for d in diff(recorded, base)
             if not d[0].startswith("/timings") and d[0] != "/peak_rss_bytes"]

    # Step 2: contract-text constants, in this process only.
    analyze.VAR_INFLATION = 1.0
    analyze.mde = lambda sigma_rel, n: analyze.Z_MDE * sigma_rel / math.sqrt(n)
    count.sigma_rel_formula = lambda B, N: 1.4 / math.sqrt(N)
    sup = scrub(analyze.run_analysis(RUNS, official=False))
    changes = diff(base, sup)

    result = {
        "schema": "crypto.autoresearch.cmfb.superseding-analysis.v1",
        "experiment_id": "EXP-CMFB-cea1d2",
        "supersedes_recorded": "RUN-CMFB-2010d3 (left untouched)",
        "official": False,
        "changes_applied": {"D1": "MDE without inflation factor sqrt(3)*1.0025",
                            "D2": "I10 reference 1.4/sqrt(N)"},
        "reproduction_of_recorded_t8": {"identical_outside_timings_and_peak_rss": not repro,
                                        "differences": [list(map(str, d)) for d in repro]},
        "superseding": sup,
        "changed_fields": [[d[0], d[1], d[2]] for d in changes],
    }
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True, default=str))
    print("reproduces recorded t8 outside timings and peak_rss:", not repro, f"({len(repro)} differing leaves)")
    print("classification recorded:", recorded["classification"], "| superseding:", sup["classification"])
    print("powered recorded:", recorded["powered_cells"], "| superseding:", sup["powered_cells"])
    print("fields changed by D1+D2:", len(changes))


if __name__ == "__main__":
    main()
