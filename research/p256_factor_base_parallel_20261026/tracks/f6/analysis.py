#!/usr/bin/env python3
"""Analyze retained F6 rows only; never constructs inputs or runs a solver."""
import argparse
import hashlib
import html
import json
from pathlib import Path


def write_once(path, text):
    with path.open("x") as stream:
        stream.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads((args.run/"execution.json").read_text())
    cases = json.loads((args.run/"case-index.json").read_text())
    rows = [json.loads(s) for s in (args.run/"rows.jsonl").read_text().splitlines() if s.strip()]
    assert receipt["track"] == "F6" and {row["arm"] for row in rows} == {"producer", "checker"} and len(rows) == 2
    assert all(receipt["completed_internal_cases"] == len(cases) == row["completed_cases"] for row in rows)
    args.out.mkdir(parents=True, exist_ok=False)
    observations = receipt["result"]
    summary = {"task": receipt["task"], "status": receipt["status"], "reason": receipt["reason"],
               "observations": observations, "planned_cases": receipt["planned_internal_cases"],
               "completed_cases": receipt["completed_internal_cases"],
               "uncompleted_case_ids": receipt["uncompleted_case_ids"],
               "exact_scope": "two-summand P-256 f3 relation, declared total-degree shifts and finite boxes",
               "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "not_established": ["a useful-capacity guaranteed window", "general multivariate extraction",
                                   "performance advantage", "ordinary-target success probability", "official scientific review"]}
    write_once(args.out/"result.json", json.dumps(summary, indent=2)+"\n")
    screens = [r for r in cases if r["case_id"].startswith("m")]
    graph_data = {"completed_screen_cases": len(screens),
                  "sufficient_bound_holds": sum(bool(r["bound_holds"]) for r in screens),
                  "positive_extraction_detected": observations.get("positive_extraction_detected"),
                  "ordinary_relations": observations.get("ordinary_rational_relations"),
                  "source": str(args.run/"case-index.json")}
    write_once(args.out/"graph-data.json", json.dumps(graph_data, indent=2)+"\n")
    text = ["F6: exact two-summand staircase screen",
            f"Completed declared cases: {len(cases)} / {receipt['planned_internal_cases']}",
            f"Screen cells with sufficient bound: {graph_data['sufficient_bound_holds']} / {len(screens)}",
            f"Ordinary finite-box relations: {observations.get('ordinary_rational_relations', 'unknown')}",
            f"Known-root extraction detector: {observations.get('positive_extraction_detected', 'unknown')}",
            "Shortness, zero lifting, and finite extraction are separate gates."]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="950" height="285" viewBox="0 0 950 285">\n'
    svg += '<rect width="950" height="285" fill="#f6f8fb"/>\n'
    for i, line in enumerate(text):
        svg += f'<text x="24" y="{37+i*39}" font-family="Liberation Sans" font-size="20" fill="#183247">{html.escape(line)}</text>\n'
    svg += '</svg>\n'
    write_once(args.out/"diagram.svg", svg)
    report = f'''# F6 second pass: source-free staircase and extraction audit

Observation report for `{receipt['task']}`. This report summarizes retained
outputs only; it does not decide a hypothesis or claim an algorithmic advantage.

Run status: **{receipt['status']}**. Reason: {receipt['reason'] or 'none recorded'}.
Completed internal cases: {len(cases)} of {receipt['planned_internal_cases']}.
The exact run receipt is `{args.run / 'execution.json'}`; its frozen protocol
hash is `{receipt['protocol_sha256']}`. All clocks are diagnostic,
`wall_valid=false`, on a shared managed host.

The relation is `f3(x,y,xQ)=0` for **two summands** on the published P-256
field. The declared width screen ends at `B=2^84`, below the necessary
two-summand half-target capacity scale. It is not an arity-three capacity test.
Natural target and offsets are hash-derived without consulting a solution.
The separate known-root control deliberately derives offsets from a public
solution; it is never reported as ordinary-target recovery.

| Recorded quantity | Value |
| --- | --- |
| Completed staircase width cells | {len(screens)} |
| Strict sufficient inequalities holding | {graph_data['sufficient_bound_holds']} |
| Ordinary 8-by-8 rational relation count | {observations.get('ordinary_rational_relations', 'unknown')} |
| Positive extractor detected known root | {observations.get('positive_extraction_detected', 'unknown')} |
| Ordinary extraction state | {observations.get('ordinary_extraction', 'unknown')} |

Each family retains exact triangular rank/determinant factorization and
independent coefficient reconstruction; two fixed LLL cases additionally
retain their matrices, unimodular transforms, actual vector norms and
elimination states. The bound gives at most a guaranteed short vector, not
automatically enough independent integer-zero polynomials. Missing or stopped
extraction is open. If the positive detector did not find its root, it has not
qualified an ordinary-target null conclusion.

Uncompleted case IDs: `{json.dumps(receipt['uncompleted_case_ids'])}`.
All failures and partial artifacts remain in the run directory; no retry or
replacement is hidden. Counts apply only to the fixed cases and do not
establish a natural success law, useful-width construction or total ECDLP cost.

Primary literature actually read: Galbraith's corrected chapters 17 (Theorem
17.2.12(5)) and 19 (section 19.2), and SEC 2 v2 section 2.4.2. Exact URLs,
assumptions and source gaps are in `../../literature.md` relative to this report.
No shared canonical graph changes: this is a scoped implementation observation,
not an official evidence decision.

![Recorded exact cases and extraction gates](diagram.svg)
'''
    write_once(args.out/"report.md", report)
    print(json.dumps({"analysis": str(args.out), "status": receipt["status"], "cases": len(cases)}))


if __name__ == "__main__":
    main()
