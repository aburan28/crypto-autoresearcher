"""Portfolio analysis: uncertainty intervals, non-composable frontiers, and HTML report.

The HTML is standalone and escapes all source labels. No inferred speedups.
"""
import argparse
import hashlib
import html
import json
import math
import pathlib
import random
import statistics

from tools.progress_fidelity import evaluate, InvalidClaim

def bootstrap_paired(record, replicates=2000, confidence=0.95):
    """Deterministic paired bootstrap for local speedups; descriptive, not proof."""
    evaluate(record)
    if record["level"] != "local":
        return None
    b, c = record["baseline"]["observations"], record["candidate"]["observations"]
    n = len(b)
    if n < 5:
        return {"status": "insufficient_pairs", "n": n}
    seed = int.from_bytes(hashlib.sha256(json.dumps(record, sort_keys=True).encode()).digest()[:8], "big")
    rng = random.Random(seed)
    throughput = record["unit"] in {"relations_per_second", "iterations_per_second"}
    ratios = []
    for _ in range(replicates):
        indices = [rng.randrange(n) for _ in range(n)]
        x = statistics.median(b[i] for i in indices)
        y = statistics.median(c[i] for i in indices)
        ratios.append(y / x if throughput else x / y)
    ratios.sort()
    tail = (1 - confidence) / 2
    return {"status": "descriptive_only", "n": n,
            "lower": ratios[int(tail * (replicates - 1))],
            "upper": ratios[int((1-tail) * (replicates - 1))],
            "method": "paired_bootstrap_median_ratio",
            "warning": "Not valid for dependent observations or selected best runs"}

def inspect(directory):
    results = []
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text())
            result = evaluate(record)
            result["uncertainty"] = bootstrap_paired(record)
            result["curve_id"] = record["scope"]["curve_id"]
            result["scale"] = record["scale"]
            result["metric"] = record["metric"]
            result["path"] = str(path)
            results.append(result)
        except (InvalidClaim, ValueError, TypeError, KeyError, OSError) as exc:
            results.append({"path": str(path), "qualified_schema": False, "error": str(exc)})
    return results

def frontiers(results):
    """Best observed speedup per identical claim scope, never multiply speedups."""
    groups = {}
    for r in results:
        if not r["qualified_schema"]:
            continue
        key = (r["curve_id"], r["scale"], r["metric"], r["unit"], r["level"], r["evidence"])
        if key not in groups or r["speedup"] > groups[key]["speedup"]:
            groups[key] = r
    return list(groups.values())

def render_html(results):
    rows = []
    for r in results:
        valid = r["qualified_schema"]
        columns = [r.get("claim_id", r.get("path", "")), r.get("curve_id", "—"),
                   r.get("level", "—"), r.get("evidence", "—"),
                   (format(r["speedup"], ".4g") + "×") if valid else "unqualified",
                   r.get("error", "Schema qualified; independent review required")]
        rows.append("<tr>" + "".join("<td>" + html.escape(str(v)) + "</td>" for v in columns) + "</tr>")
    return """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Cryptanalytic Progress & Fidelity</title>
<style>body{font:16px system-ui;max-width:1200px;margin:3rem auto;padding:0 1rem;color:#17202a}
table{border-collapse:collapse;width:100%}td,th{padding:.7rem;border-bottom:1px solid #ccd;text-align:left}
thead{background:#eef2f7}.note{color:#555}</style>
<h1>Cryptanalytic Progress & Fidelity</h1>
<p class="note">Schema-qualified does not mean independently verified.
Local, end-to-end, and projected speedups are not interchangeable.</p>
<table><thead><tr><th>Claim</th><th>Curve</th><th>Level</th><th>Evidence</th><th>Speedup</th><th>Review</th></tr></thead>
<tbody>""" + "".join(rows) + "</tbody></table></html>"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("claims", type=pathlib.Path)
    parser.add_argument("--json", type=pathlib.Path)
    parser.add_argument("--html", type=pathlib.Path)
    args = parser.parse_args()
    results = inspect(args.claims)
    report = {"claims": results, "frontiers": frontiers(results),
              "disclaimer": "Qualified schema is not independent verification"}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2))
    if args.html:
        args.html.write_text(render_html(results))
    if not args.json and not args.html:
        print(json.dumps(report, indent=2))
    return int(any(not r["qualified_schema"] for r in results))

if __name__ == "__main__":
    raise SystemExit(main())
