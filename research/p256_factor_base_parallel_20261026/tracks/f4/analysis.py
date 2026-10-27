"""Frozen descriptive analysis of recorded F4 rows; never generates cases."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path


def write_once(path, value):
    with Path(path).open("x") as handle:
        handle.write(value)


def analyze(run, out):
    run, out = Path(run), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(line) for line in (run/"rows.jsonl").read_text().splitlines() if line]
    arms = {row["arm"]: row for row in rows}
    if set(arms) != {"natural", "natural-order-aa", "positive", "negative"} or len(rows) != 4:
        raise ValueError("The fixed four arm-panels are not all recorded")
    cases = []
    for path in sorted((run/"natural").glob("*.json")):
        record = json.loads(path.read_text())
        cases.append({"path": str(path.relative_to(run)), "record": record})
    natural = arms["natural"]
    per_anchor = []
    for anchor in range(1, 9):
        subset = [case["record"] for case in cases if case["record"]["anchor_scalar"] == anchor]
        per_anchor.append({"anchor_scalar": anchor, "recorded": len(subset),
                           "verified": sum(x.get("verification") == "verified" for x in subset),
                           "fully_rational": sum(x.get("fully_rational", False) for x in subset),
                           "failures": sum(x.get("verification") != "verified" for x in subset)})
    consistent = all(arms["natural"][key] == arms["natural-order-aa"][key]
                     for key in ["outside_rank", "kernel_dimension", "cancelled_rank"])
    summary = {
        "schema": "p256-f4-pass2-recorded-analysis/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "flow": {"planned_arm_panels": 4, "recorded_arm_panels": len(rows),
                 "completed_arm_panels": sum(r["status"] in ["succeeded", "failed"] for r in rows),
                 "failed_arm_panels": sum(r["status"] == "failed" for r in rows),
                 "unique_natural_functions_requested": 128,
                 "unique_natural_function_records": len(cases)},
        "per_anchor": per_anchor,
        "natural": {key: value for key, value in natural.items()
                    if key not in ["native_counters", "role"]},
        "aa_structural_ranks_agree": consistent,
        "aa_is_not_resampling": True,
        "finite_observed_fraction": {"numerator": natural["fully_rational"],
                                     "denominator": 128,
                                     "definition": "Fully rational certified functions among all128 fixed generated functions; not a population probability or speed metric."},
        "conditional_theory_reference": "(r-1)/(2p) under ideal uniform slope; see prospective theory.md",
        "no_inferential_yield_or_performance_claim": True,
        "all_clocks_diagnostic": True,
        "official_scientific_state_transition": False,
    }
    write_once(out/"summary.json", json.dumps(summary, indent=2)+"\n")
    height, width = 420, 800
    bars = []
    for at, row in enumerate(per_anchor):
        left = 70+at*86
        rational, failed = row["fully_rational"], row["failures"]
        nonsplit = row["recorded"]-rational-failed
        offset = 330
        for count, color in [(rational, "#276b91"), (nonsplit, "#acb9c4"), (failed, "#b74942")]:
            size = count*14
            bars.append(f'<rect x="{left}" y="{offset-size}" width="48" height="{size}" fill="{color}"/>')
            offset -= size
        bars.append(f'<text x="{left+24}" y="353" text-anchor="middle">{row["anchor_scalar"]}G</text>')
        bars.append(f'<text x="{left+24}" y="{offset-8}" text-anchor="middle">{rational}/{row["recorded"]}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
           '<rect width="100%" height="100%" fill="white"/>\n'
           '<g font-family="Liberation Sans, sans-serif" font-size="15" fill="#15293b">\n'
           '<text x="28" y="34" font-size="21">F4: all128 fixed anchored sections over P-256</text>\n'
           '<text x="28" y="61">Counts per anchor; labels show fully rational / all recorded</text>\n'
           +"\n".join(bars)+
           '\n<text x="28" y="390">Blue: rational; gray: retained nonsplit; red: failed certificate/process.</text>\n'
           '</g>\n</svg>\n')
    write_once(out/"counts.svg", svg)
    report = f'''# F4 second-pass recorded panel

Observations only. Run directory: `{run.name}`. No performance comparison,
general useful-relation law, ECDLP advantage or official scientific decision.

The fixed panel requested 128 anchored functions and retained {len(cases)}
natural case records. Of those, {natural['fully_rational']} were certified
fully rational and {natural['eligible_rows']} entered signed outside
incidence reduction. Nonsplit and failed cases remain in the raw directory.
The natural graph has outside rank {natural['outside_rank']}, kernel
dimension {natural['kernel_dimension']} and cancelled base-row rank
{natural['cancelled_rank']}. These are different quantities.

The reversed-order A/A replay uses exactly the same raw functions, with zero
additional samples. Its structural ranks agree: {consistent}. Arithmetic
reduction counts or DAG size may differ by input order; no cost ratio is
computed. Positive control panels completed {arms['positive']['controls_passed']}
of {arms['positive']['controls_total']} recorded control checks; the negative
panel completed {arms['negative']['controls_passed']} of
{arms['negative']['controls_total']}. Read their individual records and
failure files before interpreting these counts.

![Recorded function counts](counts.svg)

The natural fraction above is a descriptive fraction of the exact fixed
hash-derived inputs. The prospective ideal-uniform identity is
(r-1)/(2p). Neither this identity nor the finite fraction estimates natural
collision yield or useful rank on another base. Eight base anchors condition
the law; all scalar-known graph positives are correctness controls.

`summary.json` derives its numbers solely from raw JSON and `rows.jsonl`.
Wall and CPU clocks are diagnostic on the shared host and have wall_valid
false. Source, protocol, commands, host facts and immutable raw certificates
are retained beside this analysis; the unified export binds their hashes.
No source was executed again to make the graph or this report.
'''
    write_once(out/"report.md", report)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.run, args.out)["flow"]))


if __name__ == "__main__":
    main()
