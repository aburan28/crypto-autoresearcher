"""Regenerate P37 edge-time SVG from immutable transport checkpoints."""
from pathlib import Path
import json, math, sys
cp=Path(sys.argv[1]); out=Path(sys.argv[2])
rows=[json.loads((cp/f'edge-{i:04d}.json').read_text()) for i in range(1,25)]
M=math.ceil(max(r['elapsed_seconds'] for r in rows)/10)*10
x=lambda i:80+660*(i-1)/23
y=lambda v:300-240*v/M
s=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="390" viewBox="0 0 800 390">','<rect width="800" height="390" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#243447;font-size:13px}.axis{stroke:#44566c;stroke-width:1.5}.grid{stroke:#dbe4ed}.series{fill:none;stroke:#3d6b91;stroke-width:2.5}.prior{fill:#3d6b91}.new{fill:#cc3f3f}</style>','<text x="80" y="28" font-size="17" font-weight="bold">P37 saved edge times through check vertex 24</text>']
for t in range(0,M+1,10):s += [f'<line class="grid" x1="80" y1="{y(t):.1f}" x2="740" y2="{y(t):.1f}"/>',f'<text x="53" y="{y(t)+4:.1f}" text-anchor="end">{t}</text>']
s += ['<line class="axis" x1="80" y1="60" x2="80" y2="300"/>','<line class="axis" x1="80" y1="300" x2="740" y2="300"/>']
for i in (1,4,8,12,16,20,24):s.append(f'<text x="{x(i):.1f}" y="322" text-anchor="middle">{i}</text>')
s += ['<text x="410" y="350" text-anchor="middle">Edge index</text>','<text x="18" y="195" transform="rotate(-90 18 195)" text-anchor="middle">Producer edge time (s)</text>']
s.append('<polyline class="series" points="'+' '.join(f'{x(i):.1f},{y(r["elapsed_seconds"]):.1f}' for i,r in enumerate(rows,1))+'"/>')
for i,r in enumerate(rows,1):s.append(f'<circle class="{"new" if i>=22 else "prior"}" cx="{x(i):.1f}" cy="{y(r["elapsed_seconds"]):.1f}" r="{6 if i>=22 else 3}"/>')
for i in (22,23,24):s.append(f'<text x="{x(i):.1f}" y="{y(rows[i-1]["elapsed_seconds"])-13-(i-22)*15:.1f}" text-anchor="middle">{i}: {rows[i-1]["elapsed_seconds"]:.3f} s</text>')
s.append('<text x="80" y="377">Checkpoint elapsed_seconds; red points 22–24 were produced in this session. No relation targets.</text></svg>')
out.write_text('\n'.join(s)+'\n')
