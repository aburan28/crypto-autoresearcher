"""Render the matched candidate/control four-channel input diagram."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
candidate = json.loads((ROOT / "research/icperf_binary_torsion_k11_xcnf_20261017/manifest.json").read_text())
control = json.loads((ROOT / "research/icperf_binary_torsion_k11_local_control_xcnf_20261017/manifest.json").read_text())
assert len(candidate["arms"]) == len(control["arms"]) == 4
assert candidate["projected_columns"] == control["projected_columns"] == 316
for left, right in zip(candidate["arms"], control["arms"]):
    assert left["channel"] == right["channel"]
    assert left["live_gates"] == right["live_gates"]
    assert left["cnf_clauses"] == right["cnf_clauses"]
    assert left["native_xor_rows"] == right["native_xor_rows"]
    assert left["membership_forbid_clauses"] == right["membership_forbid_clauses"] == 11328

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="390" viewBox="0 0 920 390">
<rect width="920" height="390" fill="white"/>
<style>text{{font-family:Arial,sans-serif;fill:#172033}}.title{{font-size:24px;font-weight:700}}.label{{font-size:17px;font-weight:700}}.small{{font-size:14px;fill:#475569}}</style>
<text class="title" x="50" y="43">Matched binary m8 formula inputs</text>
<text class="small" x="50" y="70">Same 11-bit width, 316 projected columns and four archived raw target channels.</text>
<rect x="52" y="105" width="340" height="115" rx="10" fill="#e8f7ee" stroke="#14965a" stroke-width="2"/>
<text class="label" x="72" y="137">Weighted k11 candidate</text>
<text class="small" x="72" y="167">632 accepted raw coordinates</text>
<text class="small" x="72" y="190">target-blind Hamming cut</text>
<rect x="528" y="105" width="340" height="115" rx="10" fill="#eaf1ff" stroke="#2563eb" stroke-width="2"/>
<text class="label" x="548" y="137">Local random control</text>
<text class="small" x="548" y="167">632 accepted raw coordinates</text>
<text class="small" x="548" y="190">SHA-256 sample from liftable block</text>
<path d="M392 162 H528" stroke="#64748b" stroke-width="2"/>
<text class="small" x="460" y="150" text-anchor="middle">matched</text>
<rect x="170" y="255" width="580" height="78" rx="10" fill="#f1f5f9" stroke="#94a3b8"/>
<text class="label" x="460" y="282" text-anchor="middle">Four channels each · seven Pφ,3 equations</text>
<text class="small" x="460" y="309" text-anchor="middle">11,328 membership clauses per file · equal per-channel gate counts</text>
<path d="M220 221 L320 255 M700 221 L600 255" stroke="#64748b" stroke-width="2"/>
<text class="small" x="460" y="370" text-anchor="middle">Verified serialized inputs; no solver, relations, rank or complete-cost result.</text>
</svg>'''
Path(__file__).with_name("2026-10-17-binary-torsion-k11-local-control-xcnf.svg").write_text(svg + "\n")
