#!/usr/bin/env python3
"""Draw the 2026-10-30 atlas review figure from the committed rows (no new data).

  python3 figures.py   # from this directory; writes dispositions.svg and
                       # dispositions.json (the counts the SVG and the PDF draw)

Plain SVG, standard library only (matplotlib is not required). Colours follow
the 2026-10-24 report; the page background switches with prefers-color-scheme.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "tools"))
import lead_atlas as la  # noqa: E402

COLORS = {"closed_obstructed": "#3b5b92", "closed_known": "#6f8fc2",
          "closed_dominated": "#a9bde0", "exhausted_at_scale": "#8c8c8c",
          "open_next_step": "#d9822b", "open_blocked": "#c0392b",
          "open_unexamined": "#f2c14e"}
CHANGED = {"LEAD-ICP-pkm-tower-algebraic-oracle": "new",
           "LEAD-ICP-coppersmith-smallroot-semaev": "closed"}


def counts():
    rows = la.load_leads()
    fams = list(la.FAMILIES)
    table = {f: {d: sum(r["family"] == f and r["disposition"] == d for r in rows)
                 for d in la.DISPOSITIONS} for f in fams}
    return rows, fams, table


def svg(rows, fams, table):
    W, row_h, left, top, unit = 760, 34, 110, 64, 16
    H = top + row_h * len(fams) + 120
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" font-family="system-ui, -apple-system, '
           'Segoe UI, Helvetica, Arial, sans-serif">',
           '<style>.bg{fill:#ffffff}.fg{fill:#1f2328}.mute{fill:#59636e}'
           '@media (prefers-color-scheme: dark){.bg{fill:#0d1117}'
           '.fg{fill:#e6edf3}.mute{fill:#9198a1}}</style>',
           f'<rect class="bg" width="{W}" height="{H}"/>',
           f'<text class="fg" x="16" y="28" font-size="16" font-weight="600">'
           f'ECDLP lead atlas, 2026-10-30: {len(rows)} leads by family and '
           'disposition</text>',
           '<text class="mute" x="16" y="48" font-size="12">Counts from '
           'knowledge/leads/ecdlp/ (tools/lead_atlas.py). Marked: '
           '+1 new open_blocked (ic-prime), 1 open_next_step to '
           'closed_obstructed (ic-prime).</text>']
    for i, f in enumerate(fams):
        y = top + i * row_h
        out.append(f'<text class="fg" x="{left - 8}" y="{y + 20}" font-size="13" '
                   f'text-anchor="end">{f}</text>')
        x = left
        for d in la.DISPOSITIONS:
            n = table[f][d]
            if n:
                out.append(f'<rect x="{x}" y="{y + 6}" width="{n * unit}" '
                           f'height="{row_h - 12}" fill="{COLORS[d]}">'
                           f'<title>{f}: {n} {d}</title></rect>')
                x += n * unit
        tot = sum(table[f].values())
        mark = "  (ic-prime: +1 new, 1 closed)" if f == "ic-prime" else ""
        out.append(f'<text class="fg" x="{x + 6}" y="{y + 20}" font-size="12">'
                   f'{tot}{mark}</text>')
    ly = top + row_h * len(fams) + 24
    lx = 16
    for d in la.DISPOSITIONS:
        out.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" '
                   f'fill="{COLORS[d]}"/>')
        label = d.replace("_", " ")
        out.append(f'<text class="fg" x="{lx + 16}" y="{ly + 11}" '
                   f'font-size="11">{label}</text>')
        lx += 22 + 7 * len(label)
        if lx > W - 120:
            lx, ly = 16, ly + 22
    out.append(f'<text class="mute" x="16" y="{H - 14}" font-size="11">'
               'Derived from committed lead rows; no new measurement.</text>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


def main():
    rows, fams, table = counts()
    with open(os.path.join(HERE, "dispositions.svg"), "w") as fh:
        fh.write(svg(rows, fams, table))
    with open(os.path.join(HERE, "dispositions.json"), "w") as fh:
        json.dump({"leads": len(rows), "families": fams,
                   "dispositions": list(la.DISPOSITIONS), "table": table,
                   "changed": CHANGED}, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
