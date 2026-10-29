#!/usr/bin/env python3
"""Frozen descriptive analysis of recorded F2 rows; performs no new curve run."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_seal(directory):
    seal = json.loads((directory/"manifest.json").read_text())
    for item in seal["files"]:
        path = directory/item["path"]
        if len(path.read_bytes()) != item["bytes"] or sha(path) != item["sha256"]:
            raise ValueError("raw file differs from seal: "+item["path"])
    return seal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=HERE/"protocol.json")
    args = parser.parse_args(argv)
    raw = args.run.resolve()
    out = args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError("analysis output must be fresh and inside assigned F2 scope")
    seal = read_seal(raw)
    rows = [json.loads(line) for line in (raw/"rows.jsonl").read_text().splitlines() if line]
    if len(rows) != 2 or {row["arm"] for row in rows} != {"producer", "oracle"}:
        raise ValueError("recorded implementation grid is not the frozen two-arm grid")
    protocol = json.loads(args.protocol.read_text())
    summary = json.loads((raw/"summary.json").read_text())
    source = json.loads((raw/"source-observed.json").read_text())
    completed = all(row["status"] == "succeeded" for row in rows)
    if completed and summary.get("completion_sentinel") != "F2_PASS2_PANEL_COMPLETE":
        raise ValueError("successful rows lack completion sentinel")
    result = {
        "schema": "p256-pass2-f2-descriptive-analysis/v1",
        "task": "TASK-20261026-e8fd72", "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": protocol["freeze"]["protocol_sha256"],
        "analysis_sha256": sha(__file__), "source": source,
        "raw_manifest_sha256": sha(raw/"manifest.json"), "raw_status": seal["status"],
        "implementation_rows": [{key: row[key] for key in (
            "arm", "status", "classified_x", "completed_queries", "solution_count",
            "controls_passed", "pair_states")} for row in rows],
        "complete_panel": completed, "full_fibre": summary.get("full_fibre"),
        "queries": summary.get("queries", summary.get("partial_state", {}).get("queries", [])),
        "failure": None if completed else {"error": summary.get("error"),
                                          "scope": "not a complete mathematical empty result"},
        "scientific_performance_claim": False, "official_state_transition": False,
        "independent_implementation": True, "independent_session_review": False,
        "model_verified": False,
        "counts_scope": "exact events in the two fixed implementation traversals; not total ECDLP cost",
        "unmeasured": ["fast implicit-chain solving", "general/natural relation yield",
                       "full ECDLP cost and target attachment", "formal or canonical review"],
    }
    out.mkdir(parents=True)
    (out/"result.json").write_text(json.dumps(result, indent=2)+"\n")
    lines = [
        "# F2 second pass: recorded full-fibre and decomposition checks",
        "",
        "Observations only. This report describes the frozen finite panel; it "
        "does not assign a scientific verdict, estimate general yield, or promote a hypothesis.",
        "",
        "Task: TASK-20261026-e8fd72. Raw package: "+str(raw)+".",
        "Protocol canonical hash: "+str(result["protocol_sha256"])+".",
        "Observed source implementation commit: "+str(source["instrument_commit"])+".",
        "Observed runtime HEAD: "+str(source["runtime_head"])+".",
        "Raw status: "+seal["status"]+". The two implementation rows are sequential "
        "traversals inside one wrapper, with a shared fixed input panel.",
        "",
        "| Implementation | Classified coordinates | Completed queries | Solution certificates | Refusal controls | Pair states |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['arm']} | {row['classified_x']} | {row['completed_queries']} | "
                     f"{row['solution_count']} | {row['controls_passed']} | {row['pair_states']} |")
    if completed:
        full = result["full_fibre"]
        lines += [
            "", "The complete fixed generic fibre has "+str(full["rows"])+" distinct x "
            "coordinates, "+str(full["accepted"])+" target lifts and "+str(full["rejected"])+
            " non-lifts. These counts are exact for this fibre. They are not sampled "
            "acceptance probabilities.",
            "",
            "Target subgroup membership follows from the retained prime-order "
            "generator and unique-Hasse-multiple certificate, then separate curve checks "
            "for every accepted point. Individual [r] tests per lift: zero.",
            "",
            "| Query | Kind | M | Solutions | Repeated-coordinate | Cancellation |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
        for query in result["queries"]:
            values = query["counts"]
            lines.append(f"| {query['case']} | {query['kind']} | {query['matched_M']} | "
                         f"{values['solutions']} | {values['repeated_coordinate_solutions']} | "
                         f"{values['cancellation_solutions']} |")
    else:
        lines += ["", "The panel did not complete. Retained prefix counts describe "
                  "executed events only; missing cases and unfinished sets remain unknown.",
                  "", "Recorded error: "+str(summary.get("error"))+"."]
    lines += [
        "", "## Method and control scope",
        "",
        "Producer pair tables enumerate unordered signed pairs including repeats and "
        "inverse pairs, then join a third point. The separately implemented Jacobian "
        "oracle traverses pair/complement states and returns the complete unordered "
        "signed triples. The generic fibre replay uses the frozen coset and a distinct "
        "projective recurrence. The negative-control file records corrupt target y, "
        "omitted first fibre point, finite-fibre poles and completion-guard refusals. "
        "Positive and cancellation targets are explicitly constructed. The two "
        "unplanted hash-to-point targets are common across all six bases.",
        "",
        "A/A uncertainty is not estimated: these are deterministic exact-set checks, "
        "with independent arithmetic agreement as the stated reference. Joint wrapper "
        "wall/CPU/RSS observations are diagnostic and have wall_valid=false. No arm "
        "receives an individual clock sample.",
        "",
        "## Cost and transfer limits",
        "",
        "Pair-state and native function-call counters exclude full primitive field "
        "pricing, file I/O, hashing/compression, historical chain setup and target "
        "attachment. The method explicitly enumerates the base and O(M squared) pair "
        "states. It is a finite-domain reference, not a fast implicit-chain solver. "
        "The auxiliary and P-256 groups have different coprime orders; coordinate "
        "selection transfers no scalar labels.",
        "",
        "## Sources and custody",
        "",
        "Primary sources actually read: Petit, Kosters and Messeng (PKC 2016), "
        "sections 3.1–3.5 and 4.1, "
        "https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf; "
        "SEC2 document https://www.secg.org/sec2-v2.pdf, section 2.4.2 "
        "(its header states Draft version 2.0). See the prospective literature.md "
        "for assumptions and exact read scope.",
        "",
        "First-pass source and raw certificates remain immutable. The native model "
        "binding is unprobed. Arithmetic diversity here is not independent-session "
        "review, formal certification, or canonical scientific admission.",
        "",
        "Next obligation: a complete implicit-chain extraction method and its cost "
        "at useful base widths, with rank and target attachment. These checks alone "
        "supply neither a general yield law nor an ECDLP advantage.",
    ]
    (out/"report.md").write_text("\n".join(lines)+"\n")
    p = next(row for row in rows if row["arm"] == "producer")
    o = next(row for row in rows if row["arm"] == "oracle")
    caption = html.escape(f"Recorded coordinates: producer {p['classified_x']}; "
                          f"oracle {o['classified_x']}. Complete queries: {p['completed_queries']}.")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="250" viewBox="0 0 960 250">'
        '<rect width="960" height="250" fill="#fff"/>'
        '<g font-family="Liberation Sans,sans-serif" fill="#153047">'
        '<text x="30" y="35" font-size="21">F2 exact finite-domain pipeline</text>'
        '<g fill="#edf3f8" stroke="#476d8d">'
        '<rect x="30" y="65" width="205" height="85" rx="7"/>'
        '<rect x="265" y="65" width="205" height="85" rx="7"/>'
        '<rect x="500" y="65" width="205" height="85" rx="7"/>'
        '<rect x="735" y="65" width="195" height="85" rx="7"/></g>'
        '<g font-size="17"><text x="45" y="95">Certified coset</text>'
        '<text x="45" y="123">all 65,536 coordinates</text>'
        '<text x="280" y="95">Target lift / non-lift</text><text x="280" y="123">retain every decision</text>'
        '<text x="515" y="95">Signed triple search</text><text x="515" y="123">six fixed matched bases</text>'
        '<text x="750" y="95">Separate replay</text><text x="750" y="123">complete-set equality</text></g>'
        '<path d="M235 105H265 M470 105H500 M705 105H735" stroke="#476d8d" stroke-width="3"/>'
        f'<text x="30" y="190" font-size="16">{caption}</text>'
        '<text x="30" y="225" font-size="15">TASK-20261026-e8fd72; exact events, no clock or ECDLP advantage claim.</text>'
        '</g></svg>\n'
    )
    (out/"diagram.svg").write_text(svg)
    print(json.dumps({"report": str(out/"report.md"), "raw_status": seal["status"],
                      "implementation_rows": len(rows)}))


if __name__ == "__main__":
    main()
