"""Draw only the exact necessary cardinality bounds already recorded."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT/"counting-screen.json").read_text())["rows"]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="450" viewBox="0 0 1000 450">',
         '<rect width="1000" height="450" fill="white"/>',
         '<g font-family="Liberation Sans" fill="#19344c">',
         '<text x="70" y="30" font-size="20">P-256: necessary base capacity at half target coverage</text>',
         '<text x="70" y="55" font-size="14">Derived exact integer count; fixed signed base; no solver-cost or success lower bound</text>']
for y in range(0,101,20):
    pos = 365-2.8*y
    parts.extend([f'<line x1="90" y1="{pos}" x2="950" y2="{pos}" stroke="#d4dfe7"/>',
                  f'<text x="48" y="{pos+5}" font-size="14">{y}</text>'])
for i,row in enumerate(rows):
    value = float(row["log2_M_approx"])
    x = 130+i*138
    parts.extend([f'<rect x="{x}" y="{365-2.8*value}" width="68" height="{2.8*value}" fill="#416f92"/>',
                  f'<text x="{x+34}" y="{354-2.8*value}" text-anchor="middle" font-size="15">{value:.2f}</text>',
                  f'<text x="{x+34}" y="390" text-anchor="middle" font-size="15">d={row["arity"]}</text>'])
parts.extend(['<text x="90" y="420" font-size="14">Vertical axis: log2(M), canonical base points; d: number of summands.</text>',
              '<text x="90" y="443" font-size="13">Source: counting-screen.json; 2 * binomial(2M+d-1,d) &gt;= r-1 is necessary only.</text>',
              '</g></svg>'])
(ROOT/"counting-screen.svg").write_text("\n".join(parts)+"\n")
