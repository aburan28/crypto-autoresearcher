"""Build the evidence-linked report and SVGs for attempt-1 only."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CONTROL = Path(__file__).resolve().parent
ATTEMPT = CONTROL / "attempt-1"
REPORT = CONTROL / "reports/attempt-1"
STUDY = ROOT / "research/isogeny_relation_yield_scan_20261016"
sys.path.insert(0, str(ROOT / "tools"))
from curve_identity import curve_identity


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def curve_record(header: dict, model: dict, generator: list[int], tag: str) -> dict:
    field = {"characteristic": header["p"], "degree": 1,
             "representation": "prime field F_p",
             "element_encoding": "canonical integer in [0,p-1]"}
    curve = {
        "model": {"type": "short_weierstrass_y2=x3+a*x+b",
                  "a": model["a"], "b": model["b"], "j_invariant": model["j"]},
        "subgroup_order": header["r"], "cofactor": 1,
        "generator": generator,
        "target_group": "full rational point group E(F_p), prime order r",
    }
    return {"field": field, "curve": curve,
            **curve_identity(field, curve, tag)}


def main() -> None:
    REPORT.mkdir(parents=True, exist_ok=False)
    transfer = json.loads((ATTEMPT / "transfer.json").read_text())
    checked = json.loads((ATTEMPT / "check.json").read_text())
    attempt = json.loads((ATTEMPT / "attempt.json").read_text())
    with (STUDY / "walk-p37-256.jsonl").open(encoding="utf-8") as stream:
        walk_header = json.loads(next(stream))
        edge24 = None
        for line in stream:
            edge = json.loads(line)
            if edge.get("kind") == "edge" and edge.get("index") == transfer["index"]:
                edge24 = edge
                break
    if edge24 is None:
        raise ValueError("saved P37 path does not contain the measured endpoint")
    source_curve = curve_record(walk_header, walk_header["canonical_source"],
                                walk_header["source_generator"], "p37source")
    endpoint_curve = curve_record(walk_header, edge24["canonical_codomain"],
                                  edge24["image_generator"], "p37v0024")
    identities = {"schema": "ectd.path-transfer-control-identities/v1",
                  "source": source_curve, "endpoint": endpoint_curve,
                  "walk_sha256": sha(STUDY / "walk-p37-256.jsonl"),
                  "edge_count": transfer["edge_count"],
                  "edge_degree": 7, "field_of_definition": "F_p",
                  "kernel_chain_sha256": hashlib.sha256(json.dumps([
                      {"index": item["index"], "kernel_polynomial": item["kernel_polynomial"]}
                      for item in [json.loads(line) for line in
                                   (STUDY / "walk-p37-256.jsonl").read_text().splitlines()
                                   if json.loads(line).get("kind") == "edge" and
                                   json.loads(line).get("index", 0) <= transfer["index"]]
                  ], sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                  "subgroup_transport": {
                      "mathematical": "injective on the prime-order r subgroup because r is prime and r != 7",
                      "implementation": "source G,Q mapped and matched to the prepared endpoint pair; independent Sage replay passed",
                  }}
    with (REPORT / "curve-identities.json").open("x", encoding="utf-8") as stream:
        json.dump(identities, stream, indent=2, sort_keys=True)
        stream.write("\n")

    indices = [row["index"] for row in transfer["edges"]]
    setup_ms = [1000 * row["setup_seconds"] for row in transfer["edges"]]
    map_ms = [1000 * row["point_map_seconds"] for row in transfer["edges"]]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520">',
           '<rect width="1200" height="520" fill="white"/>',
           '<text x="600" y="28" text-anchor="middle" font-family="sans-serif" font-size="19" font-weight="bold">P37 path transfer control: measured per-edge times</text>']
    for panel, (title, values, color, top, height) in enumerate((
            ("Map setup (milliseconds)", setup_ms, "#315d8a", 68, 170),
            ("Fast map of G and Q (milliseconds)", map_ms, "#c26c35", 316, 120))):
        maximum = max(values) * 1.10 or 1.0
        x0, width = 82, 1084
        svg.append(f'<text x="{x0}" y="{top-18}" font-family="sans-serif" font-size="14" font-weight="bold">{title}</text>')
        for tick in range(4):
            y = top + height - height * tick / 3
            value = maximum * tick / 3
            svg.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+width}" y2="{y:.1f}" stroke="#dddddd"/>')
            svg.append(f'<text x="{x0-9}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{value:.3g}</text>')
        slot = width / len(values)
        bar = slot * 0.68
        for i, (edge_index, value) in enumerate(zip(indices, values)):
            bh = height * value / maximum
            x = x0 + i * slot + (slot - bar) / 2
            y = top + height - bh
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar:.1f}" height="{bh:.1f}" fill="{color}"/>')
            if edge_index % 2 == 1:
                svg.append(f'<text x="{x+bar/2:.1f}" y="{top+height+16}" text-anchor="middle" font-family="sans-serif" font-size="9">{edge_index}</text>')
    svg.extend(['<text x="600" y="495" text-anchor="middle" font-family="sans-serif" font-size="11">Saved edge index · n=24 distinct edges, one pass per edge, no repeats</text>', '</svg>'])
    write(REPORT / "edge-times.svg", "\n".join(svg) + "\n")

    source_uid = source_curve["curve_uid"]
    endpoint_uid = endpoint_curve["curve_uid"]
    diagram = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="410" viewBox="0 0 1200 410">
<rect width="1200" height="410" fill="#ffffff"/>
<text x="600" y="34" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold">Timed source-to-endpoint path control</text>
<rect x="28" y="90" width="350" height="250" rx="10" fill="#edf3f8" stroke="#315d8a" stroke-width="2"/>
<text x="203" y="122" text-anchor="middle" font-family="sans-serif" font-size="17" font-weight="bold">P37 source curve</text>
<text x="203" y="154" text-anchor="middle" font-family="sans-serif" font-size="13">E: y² = x³ + {walk_header['canonical_source']['a']}x + {walk_header['canonical_source']['b']} over F_p</text>
<text x="203" y="182" text-anchor="middle" font-family="sans-serif" font-size="12">p={walk_header['p']}  r={walk_header['r']}</text>
<text x="203" y="218" text-anchor="middle" font-family="sans-serif" font-size="11">{source_uid[:50]}</text>
<text x="203" y="236" text-anchor="middle" font-family="sans-serif" font-size="11">{source_uid[50:]}</text>
<text x="203" y="285" text-anchor="middle" font-family="sans-serif" font-size="13">Public G,Q pair at path origin</text>
<line x1="378" y1="215" x2="810" y2="215" stroke="#444" stroke-width="3" marker-end="url(#arrow)"/>
<text x="594" y="177" text-anchor="middle" font-family="sans-serif" font-size="15">24 saved degree-7 separable isogenies</text>
<text x="594" y="198" text-anchor="middle" font-family="sans-serif" font-size="12">Each edge over F_p; kernel chain bound to walk SHA-256</text>
<text x="594" y="248" text-anchor="middle" font-family="sans-serif" font-size="12">G and Q mapped at each edge; Sage replay agrees</text>
<rect x="822" y="90" width="350" height="250" rx="10" fill="#eef6ef" stroke="#437b4a" stroke-width="2"/>
<text x="997" y="122" text-anchor="middle" font-family="sans-serif" font-size="17" font-weight="bold">P37 endpoint, vertex 24</text>
<text x="997" y="154" text-anchor="middle" font-family="sans-serif" font-size="13">E: y² = x³ + {edge24['canonical_codomain']['a']}x + {edge24['canonical_codomain']['b']} over F_p</text>
<text x="997" y="182" text-anchor="middle" font-family="sans-serif" font-size="12">same p and prime subgroup order r</text>
<text x="997" y="218" text-anchor="middle" font-family="sans-serif" font-size="11">{endpoint_uid[:50]}</text>
<text x="997" y="236" text-anchor="middle" font-family="sans-serif" font-size="11">{endpoint_uid[50:]}</text>
<text x="997" y="285" text-anchor="middle" font-family="sans-serif" font-size="13">Mapped G,Q match prepared endpoint</text>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#444"/></marker></defs>
<text x="600" y="383" text-anchor="middle" font-family="sans-serif" font-size="11">Subgroup transport: injective for prime r≠7; exact point replay passed (control scope only)</text>
</svg>'''
    write(REPORT / "path-transfer.svg", diagram)

    setup = [row["setup_seconds"] for row in transfer["edges"]]
    point_map = [row["point_map_seconds"] for row in transfer["edges"]]
    verification = [row["map_verification_seconds"] for row in transfer["edges"]]
    runner_wall = next(row["wall_seconds"] for row in attempt["attempts"] if row["phase"] == "runner")
    checker_wall = next(row["wall_seconds"] for row in attempt["attempts"] if row["phase"] == "checker")
    stats = lambda v: {"sum": sum(v), "median": statistics.median(v),
                       "min": min(v), "max": max(v)}
    report = f'''# P37 path-transfer adapter control

**Status: implementation-control observation only.** This report records a fixed-scalar P37 map-path control. It is not relation-yield, rank, or unknown-log data, and it does not authorize a graph-study trial.

## Question and scope

Does the new rootless path-transfer runner map the same public source generator and target through a saved P37 path to vertex 24, and can an independent Sage replay certify the endpoint pair? The control uses 24 of the 256 archived degree-7 edges. The scalar was fixed by the public control fixture and is not retained in output. No discovery, confirmation, collector, solver, or rho trial was run.

## Literature checked

Petit, Kosters, and Messeng, *Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields* (PKC 2016), sections 3.3–3.4 and 4. The paper studies prime-field factor bases built from rational maps, including an auxiliary-curve/isogeny construction, and reports that its experiments are limited to small parameters and do not establish a practical advantage. This control measures only one path-transfer primitive needed for a later complete cost account; it does not implement or evaluate the paper's relation algorithm. [Primary paper](https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf).

## Exact identities and map

- Source: {source_curve['curve_id']}; full UID `{source_uid}`; model `y^2=x^3+{walk_header['canonical_source']['a']}x+{walk_header['canonical_source']['b']}` over `F_p`, `p={walk_header['p']}`, subgroup order `r={walk_header['r']}`, generator `{walk_header['source_generator']}`.
- Endpoint: {endpoint_curve['curve_id']}; full UID `{endpoint_uid}`; model `y^2=x^3+{edge24['canonical_codomain']['a']}x+{edge24['canonical_codomain']['b']}` over the same field, same prime subgroup order, endpoint generator `{edge24['image_generator']}`.
- Route: 24 saved degree-7 separable isogenies over `F_p`, each kernel polynomial in the archived walk. The full walk SHA-256 is `{identities['walk_sha256']}`; the ordered kernel-chain SHA-256 is `{identities['kernel_chain_sha256']}`.
- For prime `r != 7`, each degree-7 kernel has trivial intersection with the order-`r` subgroup, so each isogeny is injective on that subgroup. The test mapped source G and Q edge by edge; the final pair matched the endpoint manifest and an independent Sage implementation replayed all 24 point maps.

## Measured observations

One pass was recorded per distinct edge (`n=24`; no repeated path runs). The timed runner recorded edge setup, the fast map of both points, and a separate direct-Sage validation pass. The independent checker ran afterward.

| Quantity | Total | Per-edge median | Per-edge range |
|---|---:|---:|---:|
| Isogeny/map setup | {sum(setup):.6f} s | {statistics.median(setup):.6f} s | {min(setup):.6f}–{max(setup):.6f} s |
| Fast map of G and Q | {sum(point_map):.6f} s | {statistics.median(point_map):.6f} s | {min(point_map):.6f}–{max(point_map):.6f} s |
| Direct Sage validation inside runner | {sum(verification):.6f} s | {statistics.median(verification):.6f} s | {min(verification):.6f}–{max(verification):.6f} s |
| Runner process wall, including Sage startup | {runner_wall:.6f} s | — | one process |
| Independent checker process wall, including Sage startup | {checker_wall:.6f} s | — | one process |

These timing components are measured on one host and one process execution. Per-edge values are heterogeneous edges, not replicate draws. The plot shows each recorded edge value without an uncertainty interval because no repeats were collected. The path setup total and point-map total are kept separate; neither is an ECDLP cost.

![Per-edge path setup and two-point map time](edge-times.svg)

![Typed source-to-endpoint path](path-transfer.svg)

## Execution evidence

- Control record: `attempt-1/attempt.json`, status `{attempt['status']}`.
- Independent replay: `attempt-1/check.json`, status `{checked['status']}`, {checked['edges_replayed']} edges replayed.
- Source script hashes: runner `{transfer['runner_sha256']}`, checker `{checked['checker_sha256']}`, control driver `{sha(CONTROL / 'run_control.py')}`.
- Raw map record: `attempt-1/transfer.json`; exact commands and fixture-root digests: `attempt-1/command.json`; stdout/stderr are retained beside them.
- Implementation environment: {transfer['platform']}; Sage {transfer['sage_version']}; source checkout `351c9c021c7be044ade54dc7e352b33d3a772244` with other graph-study implementation changes present.

## Limits and next check

This fixed-scalar implementation control exercises one P37 path prefix and does not measure relation yield, rank, discovery/confirmation behavior, or complete ECDLP cost. The direct Sage verification is a correctness check and is reported separately from the fast point-map phase. The experiment contract must bind the path-transfer outputs to each confirmed finalist, retain fresh stage roots, and then charge transfer/setup alongside relation collection, linear algebra, individual-log recovery, scalar verification, and matched same-point rho. The next protocol-level gate remains Coordinator admission; the current configured Coordinator backend is unavailable.
'''
    write(REPORT / "report.md", report)
    typ = f'''#set page(margin: 0.65in)
#set text(size: 9pt)
= P37 path-transfer adapter control

*Implementation-control observation only. This fixed-scalar path check is not relation-yield, rank, or unknown-log data, and it does not authorize a graph-study trial.*

== Scope and literature

The control maps one public source G,Q pair across 24 saved P37 edges, then checks it against the prepared endpoint and independently replays each edge with Sage. It uses a fixed known-scalar fixture and performs no discovery, confirmation, collector, solver, or rho trial.

Petit, Kosters, and Messeng (PKC 2016) study prime-field factor bases defined through rational maps, including an auxiliary-curve/isogeny construction. Their experiments are limited to small parameters and do not establish a practical advantage. This control measures only path transfer, one input to a future end-to-end cost account. [Primary source](https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf).

== Typed path and exact identities

Source `{source_curve['curve_id']}` has UID `{source_uid}` and model y²=x³+{walk_header['canonical_source']['a']}x+{walk_header['canonical_source']['b']} over Fp, where p={walk_header['p']} and prime subgroup order r={walk_header['r']}. Endpoint `{endpoint_curve['curve_id']}` has UID `{endpoint_uid}`. The saved route contains 24 degree-7 separable isogenies over Fp; its walk digest is `{identities['walk_sha256']}` and kernel-chain digest is `{identities['kernel_chain_sha256']}`. Since prime r differs from 7, each edge is injective on the order-r subgroup. The exact G,Q pair reached the prepared endpoint and the independent replay passed.

#figure(image("path-transfer.svg", width: 100%), caption: [Typed source-to-endpoint path and subgroup-transport control.])

== Recorded timings

One pass per distinct edge (n=24; no edge repetitions):

#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  [Quantity], [Total], [Per-edge median], [Per-edge range],
  [Map setup], [{sum(setup):.6f} s], [{statistics.median(setup):.6f} s], [{min(setup):.6f}–{max(setup):.6f} s],
  [Fast map of G,Q], [{sum(point_map):.6f} s], [{statistics.median(point_map):.6f} s], [{min(point_map):.6f}–{max(point_map):.6f} s],
  [Direct Sage validation], [{sum(verification):.6f} s], [{statistics.median(verification):.6f} s], [{min(verification):.6f}–{max(verification):.6f} s],
  [Runner process wall], [{runner_wall:.6f} s], [—], [one process],
  [Independent checker wall], [{checker_wall:.6f} s], [—], [one process],
)

#figure(image("edge-times.svg", width: 100%), caption: [Measured per-edge values; edges are distinct map instances, not replicate draws.])

The runner and checker process wall times include separate Sage startup. No uncertainty interval is reported because each edge was measured once. The verification phase is separate from the fast map time. These are path-transfer measurements only; no curve-level yield or ECDLP cost follows from them.

== Evidence and next check

Control status `{attempt['status']}`; independent check `{checked['status']}` across {checked['edges_replayed']} edges. Raw record `attempt-1/transfer.json`; commands and hashes `attempt-1/command.json`; full report data in `curve-identities.json`. Environment: {transfer['platform']}; Sage {transfer['sage_version']}.

The remaining task is to bind this measurement to each finalist in the frozen experiment protocol, then include transfer and setup alongside relation collection, linear algebra, individual logs, verification, and matched same-point rho. Coordinator admission and committed scientific target roots are not yet available.
'''
    write(REPORT / "report.typ", typ)


if __name__ == "__main__":
    main()
