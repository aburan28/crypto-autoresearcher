#!/usr/bin/env python3
"""Analyze retained F8 rows only; never generates points or relations."""
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
    assert receipt["track"] == "F8" and {row["arm"] for row in rows} == {"producer", "checker"} and len(rows) == 2
    assert all(receipt["completed_internal_cases"] == len(cases) == row["completed_cases"] for row in rows)
    args.out.mkdir(parents=True, exist_ok=False)
    observed = receipt["result"]
    summary = {"task": receipt["task"], "status": receipt["status"], "reason": receipt["reason"],
               "observations": observed, "planned_cases": receipt["planned_internal_cases"],
               "completed_cases": receipt["completed_internal_cases"],
               "uncompleted_case_ids": receipt["uncompleted_case_ids"],
               "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "scope": "fixed deterministic signed orbits and complete three-summand queries only",
               "not_established": ["natural large-base success law", "a new symmetry gain over a fair baseline",
                                   "ordinary-target logarithm recovery", "performance or exponent gain", "official scientific review"]}
    write_once(args.out/"result.json", json.dumps(summary, indent=2)+"\n")
    values = {key: observed.get(key) for key in ["ordinary_queries", "ordinary_relations", "zero_relations",
              "pure_symmetry_rows", "quotient_rank", "positive_relations", "oracle_multisets"]}
    values["source"] = str(args.run/"execution.json")
    write_once(args.out/"graph-data.json", json.dumps(values, indent=2)+"\n")
    lines = ["F8: fixed signed-orbit relation observations",
             f"Ordinary queries / relations: {values['ordinary_queries']} / {values['ordinary_relations']}",
             f"Zero-target rows / pure symmetry: {values['zero_relations']} / {values['pure_symmetry_rows']}",
             f"Independent representative-log rank: {values['quotient_rank']}",
             f"Complete baseline multiset states: {values['oracle_multisets']}",
             "Both solvers receive the same signed automorphisms."]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="950" height="285" viewBox="0 0 950 285">\n'
    svg += '<rect width="950" height="285" fill="#f6f8fb"/>\n'
    for i, line in enumerate(lines):
        svg += f'<text x="24" y="{37+i*39}" font-family="Liberation Sans" font-size="20" fill="#183247">{html.escape(line)}</text>\n'
    svg += '</svg>\n'
    write_once(args.out/"diagram.svg", svg)
    report = f'''# F8 second pass: unplanted signed-orbit relation collection

Observation report for `{receipt['task']}`. These are retained exact
finite-domain outputs, not a hypothesis verdict or a speed comparison.

Run status: **{receipt['status']}**. Reason: {receipt['reason'] or 'none recorded'}.
Completed internal cases: {len(cases)} of {receipt['planned_internal_cases']}.
The raw receipt is `{args.run / 'execution.json'}` and the frozen protocol
hash is `{receipt['protocol_sha256']}`. The source, host, rejected fixture draws,
commands and diagnostic resource values remain with the run. No isolated
clock is claimed; `wall_valid=false`.

Eight deterministic public secp256k1 representatives receive all six signed
order-three images. Their discrete-log scalar labels are neither computed nor
supplied. The hash-to-abscissa fixture law is declared explicitly; it is not
claimed uniform, RFC-conformant, or a hardness proof. Eight separately hashed
target points are unplanted. The constructed positive target and historical
96 constructed matrix rows remain separate detector/regression controls.

| Recorded exact quantity | Value |
| --- | --- |
| Ordinary queries | {values['ordinary_queries']} |
| Ordinary query relations, total | {values['ordinary_relations']} |
| Zero-target relation rows | {values['zero_relations']} |
| Pure symmetry rows removed | {values['pure_symmetry_rows']} |
| Independent compressed rank | {values['quotient_rank']} |
| Constructed positive target relations | {values['positive_relations']} |
| Canonical multiset states in independent baseline | {values['oracle_multisets']} |

The pair-table method and a separately implemented projective complete-domain
enumerator use exactly the same signed point set and support repeated indices.
Every admitted output has a point certificate. The full/symmetry/stacked and
compressed ranks are checked with custom modular elimination and SymPy domain
arithmetic. Rows whose compressed coefficient vector is zero are pure known
symmetry and supply no new equation on representative logs. The false-row
rank increase and wrong-action controls are rejections, never accepted rows.

Uncompleted case IDs: `{json.dumps(receipt['uncompleted_case_ids'])}`.
Empty sets concern these complete finite domains; interrupted work is unknown.
No relation density for useful-size bases, ordinary-target recovery,
end-to-end cost, performance gain or new exponent follows from these counts.
The same automorphism and reusable setup are available to every comparator.

Literature actually read includes SEC 2 v2 section 2.4.1 and the linked prior
exact derivations/reviews; the FGHR full-text access gap is recorded in the
track's `literature.md`. No result is attributed to that unread paper. Shared
canonical graphs are unchanged because no official research decision is made.

![Recorded relation counts after symmetry](diagram.svg)
'''
    write_once(args.out/"report.md", report)
    print(json.dumps({"analysis": str(args.out), "status": receipt["status"], "cases": len(cases)}))


if __name__ == "__main__":
    main()
