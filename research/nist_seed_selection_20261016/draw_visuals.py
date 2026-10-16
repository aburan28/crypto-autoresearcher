#!/usr/bin/env python3
"""Draw editable SVG views from the immutable audit summary."""

import html
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_chart(summary):
    labels = ["B-233", "B-283", "B-409", "B-571", "P-192"]
    family = [summary["binary"][name]["earlier_family_profile_count"] for name in labels[:4]] + [len(summary["P-192"]["earlier_family_profile"])]
    x9 = [summary["binary"][name]["earlier_x9_255_reference_count"] for name in labels[:4]] + [summary["P-192"]["earlier_strict_x9_255_reference_count"]]
    width, height = 920, 500
    left, top, chart_height = 92, 76, 320
    maximum = max(16, *x9)
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Earlier candidates satisfying public reference criteria">',
            '<rect width="100%" height="100%" fill="#fffdf8"/>',
            '<text x="36" y="34" font-family="sans-serif" font-size="23" font-weight="700" fill="#172b3a">Earlier eligible candidates in complete streams</text>',
            '<text x="36" y="58" font-family="sans-serif" font-size="14" fill="#42586a">Exact orders; 255-smooth X9.62 reference cofactor; P-192 also matches the strict seed mapping</text>']
    for tick in range(0, maximum + 1, 2):
        y = top + chart_height - tick / maximum * chart_height
        body.append(f'<line x1="{left}" y1="{y:.1f}" x2="860" y2="{y:.1f}" stroke="#d5dee1" stroke-width="1"/>')
        body.append(f'<text x="75" y="{y+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="13" fill="#42586a">{tick}</text>')
    for i, label in enumerate(labels):
        center = 160 + 150 * i
        for offset, value, color in ((-24, family[i], "#1d5670"), (24, x9[i], "#c16a20")):
            height_bar = value / maximum * chart_height
            x = center + offset - 18
            y = top + chart_height - height_bar
            body.append(f'<rect x="{x}" y="{y:.1f}" width="36" height="{height_bar:.1f}" fill="{color}" rx="3"/>')
            body.append(f'<text x="{x+18}" y="{max(top+15,y-7):.1f}" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="700" fill="#172b3a">{value}</text>')
        body.append(f'<text x="{center}" y="424" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#172b3a">{html.escape(label)}</text>')
    body.extend(['<rect x="166" y="453" width="18" height="14" fill="#1d5670"/>',
                 '<text x="192" y="466" font-family="sans-serif" font-size="14" fill="#172b3a">Published family cofactor profile</text>',
                 '<rect x="490" y="453" width="18" height="14" fill="#c16a20"/>',
                 '<text x="516" y="466" font-family="sans-serif" font-size="14" fill="#172b3a">X9.62 reference minimum</text>',
                 '</svg>'])
    (ROOT / "selection_counts.svg").write_text("\n".join(body) + "\n")


def write_pipeline():
    stages = [
        ("Reported clock + index", "31,945 target/index pairs"),
        ("lrand48 and SHA-1", "14 seeds and coefficients anchored"),
        ("Basis / root checks", "prime branches and binary b"),
        ("Prime-order census", "six streams complete"),
        ("Public acceptance", "family profile; X9 subset"),
    ]
    body = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 188" role="img" aria-label="Audit pipeline with completed and pending stages">',
            '<rect width="100%" height="100%" fill="#fffdf8"/>']
    for i, (heading, detail) in enumerate(stages):
        x = 14 + 216 * i
        fill = "#d7eef0" if i < 3 else "#f7e7c6" if i == 3 else "#e1e9f1"
        body.append(f'<rect x="{x}" y="34" width="196" height="105" rx="11" fill="{fill}" stroke="#7792a0"/>')
        body.append(f'<text x="{x+98}" y="74" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="700" fill="#172b3a">{html.escape(heading)}</text>')
        body.append(f'<text x="{x+98}" y="101" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#42586a">{html.escape(detail)}</text>')
        if i < len(stages)-1:
            body.append(f'<path d="M{x+199},87 L{x+213},87" stroke="#42586a" stroke-width="2" marker-end="url(#arrow)"/>')
    body.insert(2, '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#42586a"/></marker></defs>')
    body.extend(['<text x="20" y="167" font-family="sans-serif" font-size="12" fill="#42586a">Cofactor-one prime census cross-checked. Exact near-prime orders and historical private filters remain open.</text>', '</svg>'])
    (ROOT / "audit_pipeline.svg").write_text("\n".join(body) + "\n")


def write_prefix_chart():
    plan_path = ROOT / "raw" / "family_campaign" / "retry_plan.json"
    if not plan_path.exists():
        return
    plan = json.loads(plan_path.read_text())
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    names = ("P-224", "P-256", "P-384", "P-521", "prime239v3", "prime192v2")
    segments = {name: [] for name in names}
    for source in plan["source_segments"]:
        name = source["target"]
        path = ROOT / source["path"]
        if digest(path) != source["sha256"]:
            raise ArithmeticError(f"frozen prefix source changed: {path}")
        rows = [json.loads(line) for line in path.read_text().splitlines()[1:]]
        if len(rows) != source["rows"]:
            raise ArithmeticError(f"prefix length changed: {path}")
        accepted = [row["index"] for row in rows
                    if row["index"] < targets[name]["candidate_index"] and
                    (row.get("family_accept_canonical") or row.get("family_accept_other"))]
        segments[name].append((source["start"], source["end"], accepted))
    body = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 470" role="img" aria-label="Exact published-family candidate coverage and earlier survivors in six prime streams">',
            '<rect width="100%" height="100%" fill="#fffdf8"/>',
            '<text x="30" y="39" font-family="sans-serif" font-size="23" font-weight="700" fill="#172b3a">Prime-family search: frozen exact prefix</text>',
            '<text x="30" y="63" font-family="sans-serif" font-size="14" fill="#42586a">Blue = locally counted indices; orange ticks = earlier eligible seeds; gray = not counted in this local prefix</text>']
    x0, length = 190, 640
    for offset, name in enumerate(names):
        y = 100 + 53 * offset
        end = targets[name]["candidate_index"]
        observed = 0
        accepted = set()
        body.append(f'<text x="168" y="{y+6}" text-anchor="end" font-family="sans-serif" font-size="15" fill="#172b3a">{html.escape(name)}</text>')
        body.append(f'<rect x="{x0}" y="{y-9}" width="{length}" height="18" fill="#e4e8e8" rx="3"/>')
        for start, stop, hits in segments[name]:
            left = x0 + (start - 1) / end * length
            right = x0 + stop / end * length
            body.append(f'<rect x="{left:.2f}" y="{y-9}" width="{right-left:.2f}" height="18" fill="#1d5670"/>')
            observed += min(stop, end - 1) - start + 1 if start < end else 0
            accepted.update(hits)
        for index in sorted(accepted):
            x = x0 + (index - 0.5) / end * length
            body.append(f'<line x1="{x:.2f}" y1="{y-14}" x2="{x:.2f}" y2="{y+14}" stroke="#c16a20" stroke-width="3"/>')
        body.append(f'<text x="852" y="{y+6}" font-family="sans-serif" font-size="14" fill="#172b3a">{len(accepted)} / {observed} seen</text>')
    body.extend(['<text x="190" y="433" font-family="sans-serif" font-size="13" fill="#42586a">Gray ranges are covered by the separately merged full census; this chart shows only independent local checks.</text>',
                 '</svg>'])
    (ROOT / "prefix_family.svg").write_text("\n".join(body) + "\n")


def write_full_prime_chart():
    path = ROOT / "raw" / "full_census_crosscheck_v4.json"
    evidence = json.loads(path.read_text())
    if evidence["status"] != "validated" or evidence["totals"]["broad_family_both_seeded_roots"] != 69:
        raise ArithmeticError("full prime chart evidence is not validated")
    streams = (("239-bit ANSI", "prime239v3"), ("192-bit NIST/ANSI", "prime192v2"),
               ("P-521", "P-521"), ("P-256", "P-256"),
               ("P-384", "P-384"), ("P-224", "P-224"))
    categories = (("published", "#1d5670"), ("screen_skipped", "#c16a20"),
                  ("screen_rejected_order_too_wide", "#8c6b9a"),
                  ("seeded_opposite_root_only_prime", "#548874"))
    body = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 495" role="img" aria-label="Six fixed prime streams: published curves and earlier prime-order alternatives">',
            '<rect width="100%" height="100%" fill="#fffdf8"/>',
            f'<!-- source_sha256={digest(path)} -->',
            '<text x="28" y="37" font-family="sans-serif" font-size="23" font-weight="700" fill="#172b3a">Prime-order candidates in six recovered streams</text>',
            '<text x="28" y="62" font-family="sans-serif" font-size="14" fill="#42586a">Seed-level counts: 10 published + 59 earlier alternatives under the broader cofactor-one profile</text>']
    x0, unit = 230, 25
    for row, (label, key) in enumerate(streams):
        y = 95 + row * 52
        data = evidence["streams"][key]
        body.append(f'<text x="208" y="{y+17}" text-anchor="end" font-family="sans-serif" font-size="15" fill="#172b3a">{html.escape(label)}</text>')
        x = x0
        for category, color in categories:
            count = len(data[category])
            if not count:
                continue
            body.append(f'<rect x="{x}" y="{y}" width="{count * unit}" height="24" fill="{color}"/>')
            if count >= 2:
                body.append(f'<text x="{x + count * unit/2:.1f}" y="{y+17}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#ffffff">{count}</text>')
            x += count * unit
        body.append(f'<text x="{x+10}" y="{y+18}" font-family="sans-serif" font-size="14" font-weight="700" fill="#172b3a">{len(data["broad_family_both_seeded_roots"])}</text>')
    legends = (("Published", "#1d5670"), ("Screen skip", "#c16a20"),
               ("Order wider than field", "#8c6b9a"), ("Opposite seeded root only", "#548874"))
    x = 44
    for label, color in legends:
        body.append(f'<rect x="{x}" y="422" width="16" height="16" fill="{color}"/>')
        body.append(f'<text x="{x+23}" y="435" font-family="sans-serif" font-size="13" fill="#172b3a">{html.escape(label)}</text>')
        x += {"Published": 145, "Screen skip": 155, "Order wider than field": 230,
              "Opposite seeded root only": 225}[label]
    body.append('<text x="44" y="468" font-family="sans-serif" font-size="12" fill="#42586a">P-224 quadratic-twist-only cases are outside its two seeded signs; published P-384 has both branches prime and counts once.</text>')
    body.append('</svg>')
    (ROOT / "full_prime_window.svg").write_text("\n".join(body) + "\n")


def main():
    summary = json.loads((ROOT / "raw" / "analysis_summary.json").read_text())
    write_chart(summary)
    write_pipeline()
    write_prefix_chart()
    write_full_prime_chart()
    print("selection_counts.svg audit_pipeline.svg prefix_family.svg full_prime_window.svg")


if __name__ == "__main__":
    main()
