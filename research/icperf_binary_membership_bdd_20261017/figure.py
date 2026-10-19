"""Render the exact-input membership diagram and clause-count graph as SVG."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE / "result.json").read_text())
ROWS = RESULT["rows"]
SCALE = 600 / 12000


def bar(x: int, y: int, value: int, color: str, label: str) -> str:
    width = value * SCALE
    return (f'<text x="{x - 12}" y="{y + 23}" text-anchor="end" class="small">{label}</text>'
            f'<rect x="{x}" y="{y}" width="{width:.1f}" height="32" rx="4" fill="{color}"/>'
            f'<text x="{x + width + 9:.1f}" y="{y + 22}" class="small bold">{value:,}</text>')


def main() -> None:
    weighted = ROWS["weighted"]
    control = ROWS["local_random"]
    forbid = weighted["archived_forbidden_clauses_for_8_blocks"]
    assert forbid == control["archived_forbidden_clauses_for_8_blocks"]
    w_bdd = weighted["bdd_lsb_first"]["clauses_for_8_blocks"]
    c_bdd = control["bdd_lsb_first"]["clauses_for_8_blocks"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 565" role="img" aria-labelledby="title desc">
<title id="title">Exact binary factor-base membership: proposed BDD encoding</title>
<desc id="desc">Workflow diagram and derived eight-block clause counts for weighted and matched random bases. No solver or speed measurement.</desc>
<style>
  text {{ font-family: Arial, Helvetica, sans-serif; fill: #193047; }}
  .title {{ font-size: 23px; font-weight: 700; }}
  .sub {{ font-size: 14px; fill: #506477; }}
  .small {{ font-size: 13px; }}
  .bold {{ font-weight: 700; }}
  .box {{ fill: #eef4f8; stroke: #9eb2c1; stroke-width: 1.5; }}
  .axis {{ stroke: #91a4b3; stroke-width: 1; }}
</style>
<rect width="960" height="565" fill="white"/>
<text x="36" y="42" class="title">Exact 11-bit membership encoding candidate</text>
<text x="36" y="65" class="sub">GF(2^61), 60-bit prime subgroup · 316 columns per base · 8 summands · input structure only</text>
<text x="36" y="101" class="small bold">Predicate path</text>
<rect x="36" y="116" width="178" height="76" rx="9" class="box"/>
<text x="125" y="147" text-anchor="middle" class="small bold">11-bit affine input</text>
<text x="125" y="169" text-anchor="middle" class="small">2,048 values</text>
<path d="M214 154 H248" class="axis"/><path d="M248 154 l-8 -5 v10 z" fill="#91a4b3"/>
<rect x="250" y="116" width="178" height="76" rx="9" class="box"/>
<text x="339" y="147" text-anchor="middle" class="small bold">Exact membership</text>
<text x="339" y="169" text-anchor="middle" class="small">632 accepted values</text>
<path d="M428 154 H462" class="axis"/><path d="M462 154 l-8 -5 v10 z" fill="#91a4b3"/>
<rect x="464" y="116" width="206" height="76" rx="9" class="box"/>
<text x="567" y="147" text-anchor="middle" class="small bold">Reduced ordered BDD</text>
<text x="567" y="169" text-anchor="middle" class="small">188 / 212 nodes</text>
<path d="M670 154 H704" class="axis"/><path d="M704 154 l-8 -5 v10 z" fill="#91a4b3"/>
<rect x="706" y="116" width="216" height="76" rx="9" class="box"/>
<text x="814" y="147" text-anchor="middle" class="small bold">Conditional CNF</text>
<text x="814" y="169" text-anchor="middle" class="small">then retain full point filter</text>
<text x="36" y="232" class="small bold">Membership clauses across eight independent input blocks</text>
<line x1="236" y1="444" x2="836" y2="444" class="axis"/>
<line x1="236" y1="260" x2="236" y2="444" class="axis"/>
<line x1="436" y1="440" x2="436" y2="448" class="axis"/>
<line x1="636" y1="440" x2="636" y2="448" class="axis"/>
<line x1="836" y1="440" x2="836" y2="448" class="axis"/>
<text x="236" y="465" text-anchor="middle" class="small">0</text>
<text x="436" y="465" text-anchor="middle" class="small">4,000</text>
<text x="636" y="465" text-anchor="middle" class="small">8,000</text>
<text x="836" y="465" text-anchor="middle" class="small">12,000 clauses</text>
{bar(236, 270, forbid, '#a3afba', 'Weighted: forbids')}
{bar(236, 318, w_bdd, '#167f88', 'Weighted: BDD')}
{bar(236, 366, forbid, '#a3afba', 'Control: forbids')}
{bar(236, 414, c_bdd, '#d17b38', 'Control: BDD')}
<text x="36" y="508" class="sub">BDD bars are derived encoding counts after exhaustive predicate replay; no BDD formula was solver-tested.</text>
<text x="36" y="531" class="sub">ANF degree is 9 for both bases. Any solver, regularity, relation, rank or full-cost effect remains open.</text>
</svg>'''
    path = HERE / "figure.svg"
    expected = svg + "\n"
    if path.exists():
        assert path.read_text() == expected, "existing SVG differs from source and result"
    else:
        with path.open("x") as output:
            output.write(expected)
    print(f"figure.svg: forbidden={forbid}, weighted_bdd={w_bdd}, control_bdd={c_bdd}")


if __name__ == "__main__":
    main()
