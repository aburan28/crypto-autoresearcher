from pathlib import Path
p=Path(__file__).resolve().parent
boxes=[('Frozen seed-1729 trial','2048 MiB; unchanged protocol','#dbeafe'),('Scientific-body finish','Operational event only; no saved result','#e2e8f0'),('Artifact preparation','MemoryError in _json_safe(result)','#fee2e2'),('Raw / manifest / separate checker','Absent / absent / not run','#f1f5f9')]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="370" viewBox="0 0 1000 370"><rect width="1000" height="370" fill="white"/><g font-family="sans-serif" text-anchor="middle" fill="#172033">','<text x="500" y="30" font-size="20">RUN-IC-fe080b: retained operational failure path</text>']
for i,(title,detail,color) in enumerate(boxes):
 y=54+i*73
 svg.append(f'<rect x="75" y="{y}" width="850" height="55" rx="8" fill="{color}" stroke="#64748b"/><text x="500" y="{y+23}" font-size="17">{title}</text><text x="500" y="{y+44}" font-size="14">{detail}</text>')
 if i<3:svg.append(f'<path d="M500 {y+56}v13l-5-5m5 5l5-5" stroke="#64748b" fill="none"/>')
svg.append('<text x="500" y="360" font-size="13">One failed attempt. No reconstruction of missing roots, rank, controls or certificates.</text></g></svg>')
(p/'failure-path.svg').write_text(''.join(svg))
