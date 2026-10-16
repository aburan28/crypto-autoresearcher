#!/usr/bin/env python3
"""Draw the exhaustive X9 comparison and its historical decision boundary."""

import argparse
import hashlib
import html
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
NAMES = ("prime239v1", "prime239v2", "prime239v3", "P-192", "prime192v3",
         "prime192v2", "P-224", "P-256", "P-384", "P-521")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(value):
    return html.escape(str(value))


def bar_chart(summary, source_sha, attempt):
    targets = summary["named_targets"]
    values = [targets[name]["mappings"][mapping]["earlier_eligible_seed_count"]
              for name in NAMES for mapping in ("unmasked", "strict_x9")]
    scale = max(values + [1])
    width, height = 1080, 145 + 54 * len(NAMES)
    x0, length = 225, 720
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#1d2733}.title{font-size:21px;font-weight:700}.sub{font-size:12px;fill:#526171}.name{font-size:14px;font-weight:600}.value{font-size:12px}.tick{font-size:11px;fill:#526171}</style>',
           '<text class="title" x="28" y="34">Earlier X9-reference eligible seed slots</text>',
           '<text class="sub" x="28" y="56">Exact six-stream census (no sampling uncertainty); both seeded roots; lmax 255, r &gt; 2¹⁶⁰, r &gt; 4√p, MOV-20</text>',
           '<rect x="28" y="73" width="13" height="13" fill="#2674a6"/><text class="sub" x="47" y="84">Published-compatible SHA-1 mapping</text>',
           '<rect x="332" y="73" width="13" height="13" fill="#db8846"/><text class="sub" x="351" y="84">Strict 1998 X9 draft mapping</text>']
    for k in range(5):
        value = scale * k / 4
        x = x0 + length * k / 4
        out.append(f'<line x1="{x:.1f}" y1="104" x2="{x:.1f}" y2="{height-35}" stroke="#e1e6eb"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="101" text-anchor="middle">{value:.0f}</text>')
    for row, name in enumerate(NAMES):
        y = 119 + row * 54
        end = targets[name]["published_index"]
        out.append(f'<text class="name" x="28" y="{y+16}">{label(name)}</text>')
        out.append(f'<text class="tick" x="28" y="{y+32}">{end-1:,} earlier positions</text>')
        for offset, mapping, color in ((0, "unmasked", "#2674a6"), (19, "strict_x9", "#db8846")):
            count = targets[name]["mappings"][mapping]["earlier_eligible_seed_count"]
            w = length * count / scale
            out.append(f'<rect x="{x0}" y="{y+offset}" width="{w:.1f}" height="15" rx="2" fill="{color}"/>')
            out.append(f'<text class="value" x="{x0+w+7:.1f}" y="{y+offset+12}">{count}</text>')
    out.append(f'<text class="sub" x="28" y="{height-9}">Source: {label(attempt)}/x9_summary.json SHA-256 {source_sha[:16]}…; counts are conditional on each recovered stream.</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def scope_diagram(summary, source_sha, attempt):
    positions = summary["candidate_positions"]
    valid = {mapping: sum(summary["mapping_states"][rep].get(mapping + ":valid_coefficient", 0)
                          for rep in summary["mapping_states"])
             for mapping in ("unmasked", "strict_x9")}
    survivors = {mapping: len({(rep, row["index"]) for rep, variants in
                               summary["accepted_roots_by_stream"].items()
                               for row in variants.get(mapping, [])})
                 for mapping in ("unmasked", "strict_x9")}
    blocks = [
        (20, "Six recovered", "timestamp starts", "observed coordinates"),
        (250, f"{positions:,} prime", "stream positions", "fixed recipe and fields"),
        (480, "Two SHA-1 mappings", f"valid: {valid['unmasked']:,} / {valid['strict_x9']:,}", "both coefficient roots"),
        (710, "X9 public test", f"eligible: {survivors['unmasked']:,} / {survivors['strict_x9']:,}", "exact orders, near-prime"),
    ]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="330" viewBox="0 0 940 330">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#1d2733}.title{font-size:20px;font-weight:700}.main{font-size:14px;font-weight:700}.sub{font-size:11px;fill:#526171}</style>',
           '<text class="title" x="20" y="31">What the reconstructed stream fixes</text>']
    for x, top, middle, foot in blocks:
        out.append(f'<rect x="{x}" y="69" width="207" height="102" rx="8" fill="#edf4f8" stroke="#2674a6"/>')
        out.append(f'<text class="main" x="{x+12}" y="98">{label(top)}</text>')
        out.append(f'<text class="main" x="{x+12}" y="121">{label(middle)}</text>')
        out.append(f'<text class="sub" x="{x+12}" y="149">{label(foot)}</text>')
        if x < 710:
            out.append(f'<path d="M{x+207} 120 L{x+227} 120" stroke="#526171" stroke-width="2"/>')
            out.append(f'<path d="M{x+222} 116 L{x+227} 120 L{x+222} 124" fill="none" stroke="#526171" stroke-width="2"/>')
    out += [
        '<rect x="20" y="213" width="900" height="67" rx="8" fill="#fff8ec" stroke="#b47a28" stroke-dasharray="5 4"/>',
        '<text class="main" x="35" y="239">Outside this census: earlier field choice, other clock starts, generator changes, private keep/skip rule, base-point search</text>',
        '<text class="sub" x="35" y="263">These are unknown historical choices; the dashed box is not a measured search count.</text>',
        f'<text class="sub" x="20" y="311">Source: {label(attempt)}/x9_summary.json SHA-256 {source_sha[:16]}…</text>',
        '</svg>']
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="modalfull2")
    args = parser.parse_args()
    source = HERE / "raw" / f"modal_campaign_{args.attempt}" / "x9_summary.json"
    summary = json.loads(source.read_text())
    if summary["scope"] != "complete exact near-prime X9 public-reference count for six distinct prime streams":
        raise AssertionError("summary is incomplete")
    outputs = {"acceptance_counts.svg": bar_chart(summary, digest(source), args.attempt),
               "selection_scope.svg": scope_diagram(summary, digest(source), args.attempt)}
    for name, body in outputs.items():
        path = HERE / name
        if path.exists():
            raise FileExistsError(path)
        path.write_text(body)
        print(f"{path} {digest(path)}")


if __name__ == "__main__":
    main()
