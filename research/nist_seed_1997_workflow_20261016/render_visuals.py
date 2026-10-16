"""Render editable historical-workflow diagrams from the recorded census.

Only layout and tallying are done here. The six accepted-ordinal lists are read
from the immutable copied census; the published ordinals are the standards'
published seeds reproduced in the seed-provenance report.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parent / "nist_seed_provenance_20261016" / "census" / "summary.json"
ROWS = json.loads(CENSUS.read_text())
PUBLISHED = {
    863711343: {2185, 2320, 3048},
    863966734: {139, 5228, 6013},
    871002724: {1136},
    871696354: {1842},
    872952608: {2688},
    891607927: {7026},
}
LABELS = ["239-bit ANSI · May 15", "192-bit ANSI · May 18", "P-521 · Aug 8", "P-256 · Aug 16", "P-384 · Aug 30", "P-224 · Apr 3, 1998"]


def esc(s: str) -> str:
    return html.escape(s)


def write_workflow() -> None:
    boxes = [
        ("1. Fix field sizes and fast prime moduli", "NIST 1999 rationale · documented", "#dbeafe"),
        ("2. Fix a = −3; draw 20-byte candidate seed", "Efficiency documented · drand48 stream recovered", "#dbeafe"),
        ("3. SHA-1 seed → c → coefficient b", "ANSI/FIPS method · published relation verified", "#dbeafe"),
        ("4. Count points; test prime order and known attacks", "Standard screens documented · historical implementation missing", "#e0f2fe"),
        ("5. Choose records for ANSI/NIST publication", "Exact keep/skip rule unknown · 10 published, 11 passed over", "#fef3c7"),
        ("6. Assign base point G and publish parameters", "May 1997 FreeLIP pass recovered · later G sources open", "#e0f2fe"),
    ]
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="705" viewBox="0 0 1120 705">',
         '<rect width="1120" height="705" fill="#f8fafc"/>',
         '<text x="50" y="47" font-family="Arial" font-size="26" font-weight="700" fill="#0f172a">1997–98 curve generation: known stages and one open decision</text>']
    for i, (title, subtitle, fill) in enumerate(boxes):
        y = 77 + i * 99
        dash = ' stroke-dasharray="10 7"' if i == 4 else ''
        p.append(f'<rect x="48" y="{y}" width="1024" height="78" rx="13" fill="{fill}" stroke="#475569" stroke-width="1.5"{dash}/>')
        p.append(f'<text x="70" y="{y + 32}" font-family="Arial" font-size="21" font-weight="700" fill="#0f172a">{esc(title)}</text>')
        p.append(f'<text x="70" y="{y + 59}" font-family="Arial" font-size="15" fill="#334155">{esc(subtitle)}</text>')
        if i < 5:
            p.append(f'<path d="M 560 {y + 78} V {y + 99}" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>')
    p.insert(2, '<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>')
    p.append('<text x="50" y="684" font-family="Arial" font-size="13" fill="#475569">Sources: FIPS 186-2; ANSI X9.62-1998; Anthropic 2026; internal 21-curve census. Dashed box = unresolved historical step.</text>')
    p.append('</svg>')
    (HERE / "workflow.svg").write_text("\n".join(p) + "\n")


def write_counts() -> None:
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="550" viewBox="0 0 1120 550">',
         '<rect width="1120" height="550" fill="#f8fafc"/>',
         '<text x="48" y="46" font-family="Arial" font-size="26" font-weight="700" fill="#0f172a">Known qualifying blocks in six recovered streams</text>',
         '<text x="48" y="72" font-family="Arial" font-size="15" fill="#475569">Counts through each last published block · 21 total = 10 published + 11 passed over</text>',
         '<rect x="770" y="90" width="16" height="16" fill="#1d4ed8"/><text x="795" y="104" font-family="Arial" font-size="15">Published</text>',
         '<rect x="900" y="90" width="16" height="16" fill="#d97706"/><text x="925" y="104" font-family="Arial" font-size="15">Passed over</text>']
    total_pub = total_skip = 0
    for i, row in enumerate(ROWS):
        t = int(row["run"].split("(")[1].split(")")[0])
        published = PUBLISHED[t]
        accepted = set(row["accepted"])
        assert published <= accepted
        n_pub = len(published)
        n_skip = len(accepted) - n_pub
        total_pub += n_pub
        total_skip += n_skip
        y = 132 + i * 62
        p.append(f'<text x="48" y="{y + 22}" font-family="Arial" font-size="17" fill="#0f172a">{esc(LABELS[i])}</text>')
        p.append(f'<rect x="300" y="{y}" width="{n_pub * 78}" height="32" rx="3" fill="#1d4ed8"/>')
        if n_skip:
            p.append(f'<rect x="{300 + n_pub * 78}" y="{y}" width="{n_skip * 78}" height="32" rx="3" fill="#d97706"/>')
        p.append(f'<text x="{310 + (n_pub + n_skip) * 78}" y="{y + 23}" font-family="Arial" font-size="16" fill="#334155">{n_pub} / {n_skip}</text>')
    assert (total_pub, total_skip) == (10, 11)
    p.append('<text x="48" y="518" font-family="Arial" font-size="13" fill="#475569">Source: research/nist_seed_provenance_20261016/census/summary.json; published ordinals bound by the reproduced standards seeds.</text>')
    p.append('</svg>')
    (HERE / "stream_counts.svg").write_text("\n".join(p) + "\n")


if __name__ == "__main__":
    write_workflow()
    write_counts()
