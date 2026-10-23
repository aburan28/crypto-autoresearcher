"""Render exact XCNF input counts for the two planted k11 positive controls."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/icperf_binary_k11_planted_xcnf_20261017/complete/manifest.json"
OUTPUT = Path(__file__).with_name("2026-10-17-binary-k11-planted-xcnf.svg")


def render() -> str:
    data = json.loads(SOURCE.read_bytes())
    assert data["schema"] == "icperf-binary-k11-planted-xcnf-v1"
    rows = data["arms"]
    assert [row["base_kind"] for row in rows] == ["weighted", "local_random"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="600" viewBox="0 0 960 600">',
        '<rect width="960" height="600" fill="white"/>',
        '<text x="50" y="42" font-family="sans-serif" font-size="22" font-weight="bold">k11 planted SAT controls: exact input counts</text>',
        '<text x="50" y="68" font-family="sans-serif" font-size="14">Two 316-column bases, separately constructed known-point targets; no solver run</text>',
    ]
    plots = [("CNF clauses", "cnf_clauses", 100000, 105, 275),
             ("Native XOR rows", "native_xor_rows", 70000, 345, 515)]
    for title, key, maximum, top, bottom in plots:
        left, right = 170, 850
        parts += [f'<text x="170" y="{top-17}" font-family="sans-serif" font-size="17" font-weight="bold">{title}</text>',
                  f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>']
        for tick in (0, maximum//2, maximum):
            y = bottom - tick / maximum * (bottom-top)
            parts += [f'<path d="M{left} {y:.1f}H{right}" stroke="#e2e6e8"/>',
                      f'<text x="155" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick:,}</text>']
        for i, row in enumerate(rows):
            value = row["input_counts"][key]
            x = left + 170 + i*300
            y = bottom - value/maximum*(bottom-top)
            color = "#bb5933" if i==0 else "#317aa6"
            label = "weighted" if i==0 else "local random"
            parts += [f'<rect x="{x}" y="{y:.1f}" width="95" height="{bottom-y:.1f}" fill="{color}"/>',
                      f'<text x="{x+47.5:.1f}" y="{y-7:.1f}" text-anchor="middle" font-family="sans-serif" font-size="13">{value:,}</text>',
                      f'<text x="{x+47.5:.1f}" y="{bottom+22}" text-anchor="middle" font-family="sans-serif" font-size="13">{label}</text>']
    parts += ['<text x="50" y="574" font-family="sans-serif" font-size="11">Both constructed full assignments satisfy every serialized clause and XOR row. Counts are input size, not solving cost.</text>',
              '</svg>']
    return "\n".join(parts)+"\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
