"""Draw the conditional proper-subfield rank gate from its exact integer record."""
from __future__ import annotations
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
rows = json.loads((root / 'research/icperf_subfield_rank_gate_20261017/hasse_bounds.json').read_text())['rows']
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="410" viewBox="0 0 1050 410">',
         '<rect width="1050" height="410" fill="white"/>',
         '<text x="28" y="37" font-family="sans-serif" font-size="23" font-weight="bold" fill="#18303a">Proper-subfield x bases on descended binary curves</text>',
         '<text x="28" y="72" font-family="sans-serif" font-size="16" fill="#274451">x(P) ∈ Fq → Frobeniusq(P) = ±P → order(P) ≤ q + 1 + ⌊2√q⌋</text>']
for i, row in enumerate(rows):
    y = 102 + i * 84
    d = max(c['subfield_degree'] for c in row['proper_subfields'])
    bound = row['maximum_hasse_ceiling']
    floor = row['large_prime_lower_bound']
    parts.extend([f'<rect x="28" y="{y}" width="994" height="73" rx="8" fill="#eaf2f6"/>',
                  f'<text x="48" y="{y+30}" font-family="sans-serif" font-size="17" font-weight="bold" fill="#18303a">n={row["field_degree"]}; largest proper d={d}</text>',
                  f'<text x="48" y="{y+56}" font-family="sans-serif" font-size="16" fill="#274451">maximum point-order ceiling: {bound:,}    &lt;    large-prime threshold: {floor:,}</text>'])
parts.extend(['<text x="28" y="376" font-family="sans-serif" font-size="14" fill="#3c4c56">Conditional on E descending to Fq and a prime target subgroup r ≥ 2^(n−1). No ordinary-binary non-descended claim.</text>',
              '</svg>'])
out = Path(__file__).with_name('2026-10-17-binary-subfield-base-rank-gate.svg')
out.write_text('\n'.join(parts) + '\n')
print(out)
