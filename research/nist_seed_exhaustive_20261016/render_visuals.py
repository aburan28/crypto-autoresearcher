#!/usr/bin/env python3
"""Render editable SVGs from the archived bounded-search summaries."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/run-20261016T2329Z"
ORBIT = HERE / "orbit-runs/run-20261016T2344Z"


def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def coverage():
    data = json.loads((RUN / "summary.json").read_text())["streams"]
    width, height = 980, 470
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#fffdf7"/>',
             '<text x="32" y="36" font-family="Arial" font-size="24" font-weight="700" fill="#172b36">Six stream extensions: exact order work</text>',
             '<text x="32" y="59" font-family="Arial" font-size="13" fill="#4a5962">Each row: 1,024 new seed blocks; pale bar = coefficient root exists; dark bar = point-counter rows completed.</text>']
    labels = {"prime239v3": "239-bit ANSI", "prime192v2": "P-192 field", "secp521r1": "P-521 field", "prime256v1": "P-256 field", "secp384r1": "P-384 field", "secp224r1": "P-224 field"}
    for k, row in enumerate(data):
        y = 92 + 53 * k
        total = row["point_count_candidates"]
        done = row["point_count_rows"]
        parts += [f'<text x="32" y="{y+18}" font-family="Arial" font-size="16" fill="#172b36">{esc(labels[row["field"]])}</text>',
                  f'<rect x="220" y="{y}" width="520" height="25" rx="4" fill="#d7e6e6"/>',
                  f'<rect x="220" y="{y}" width="{520*done/total:.2f}" height="25" rx="4" fill="#{"26786f" if row["status"]=="complete" else "bb7b35"}"/>',
                  f'<text x="754" y="{y+18}" font-family="Arial" font-size="14" fill="#172b36">{done}/{total} rows</text>',
                  f'<text x="885" y="{y+18}" font-family="Arial" font-size="14" font-weight="700" fill="#{"26786f" if row["status"]=="complete" else "a55e24"}">{"complete" if row["status"]=="complete" else "censored"}</text>']
        if row["accepted"]:
            parts.append(f'<text x="220" y="{y+43}" font-family="Arial" font-size="13" fill="#1d675d">prime-order survivor: block {row["accepted"][0]["ordinal"]}</text>')
    parts += ['<line x1="32" y1="410" x2="948" y2="410" stroke="#c6d3d5"/>',
              '<text x="32" y="433" font-family="Arial" font-size="13" fill="#4a5962">Source: run-20261016T2329Z/summary.json and six count receipts. Censored rows assert nothing about unprocessed seeds.</text>',
              '<text x="32" y="452" font-family="Arial" font-size="13" fill="#4a5962">One separate P-256 numeric orbit shard scanned 65,536 / 2^46 starts and found 32,835 root-admitting coefficients.</text>', '</svg>']
    (HERE / "coverage.svg").write_text("\n".join(parts) + "\n")


def pipeline():
    nodes = [
        ("48-bit start state", "x = 4i + 1"),
        ("20 output bytes", "one candidate seed"),
        ("SHA-1 coefficient", "fixed field prime, a = -3"),
        ("square-root screen", "b exists for about half"),
        ("exact order", "PARI/GP or censored"),
        ("candidate class", "published choice unknown"),
    ]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="210" viewBox="0 0 1080 210">', '<rect width="100%" height="100%" fill="#fffdf7"/>',
             '<text x="24" y="30" font-family="Arial" font-size="22" font-weight="700" fill="#172b36">What this search computes</text>']
    for k, (a, b) in enumerate(nodes):
        x = 23 + k * 176
        parts += [f'<rect x="{x}" y="65" width="158" height="93" rx="8" fill="#{"dcece7" if k<4 else "f7e7d2"}" stroke="#809ba0"/>',
                  f'<text x="{x+8}" y="91" font-family="Arial" font-size="15" font-weight="700" fill="#172b36">{esc(a)}</text>',
                  f'<text x="{x+8}" y="118" font-family="Arial" font-size="12" fill="#4a5962">{esc(b)}</text>']
        if k < len(nodes) - 1:
            parts.append(f'<path d="M{x+159} 111 L{x+174} 111" stroke="#55747a" stroke-width="2" marker-end="url(#arrow)"/>')
    parts += ['<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#55747a"/></marker></defs>',
              '<text x="24" y="187" font-family="Arial" font-size="13" fill="#4a5962">The historical keep/skip decision was not observed. The numeric orbit shard ends after the square-root screen.</text>', '</svg>']
    (HERE / "pipeline.svg").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    coverage()
    pipeline()
