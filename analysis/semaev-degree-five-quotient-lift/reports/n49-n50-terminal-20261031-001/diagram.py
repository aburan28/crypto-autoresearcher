from pathlib import Path
import json
p=Path(__file__).parent
d=json.loads((p/'diagram-data.json').read_text())
a=d['n49'];b=d['n50']
svg=f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360" viewBox="0 0 1000 360"><rect width="1000" height="360" fill="#fff"/><style>text{{font-family:Arial,sans-serif;fill:#17243a}}.h{{font-size:20px;font-weight:bold}}.t{{font-size:16px}}.s{{font-size:13px;fill:#4b5668}}</style><text x="35" y="32" class="h">Two exact frontier attempts (31 Oct 2026)</text><rect x="35" y="55" width="930" height="120" rx="10" fill="#eef4ff" stroke="#5374a8"/><text x="55" y="84" class="h">{a['id']}</text><text x="55" y="112" class="t">D4 independently checked: codim ≥ {a['d4_codimension']}; exact solutions = {a['exact_solutions']}</text><text x="55" y="140" class="t">D5 producer: timed out after {a['d5_timeout_seconds']:.1f} s; no D5 certificate</text><rect x="35" y="194" width="930" height="120" rx="10" fill="#fff4e9" stroke="#af7135"/><text x="55" y="223" class="h">{b['id']}</text><text x="55" y="251" class="t">Fresh exact solutions = {b['exact_solutions']}; D3 producer reported W3_one = 1</text><text x="55" y="279" class="t">No D3 seed certificate; D4 and D5 were not attempted</text><text x="35" y="340" class="s">Source: n49-poly00-d5-local-terminal-002 and n50-poly00-cascade-local-terminal-001</text></svg>"""
(p/'diagram.svg').write_text(svg)
