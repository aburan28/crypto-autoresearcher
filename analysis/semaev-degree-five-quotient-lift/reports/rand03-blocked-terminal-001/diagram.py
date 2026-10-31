from pathlib import Path
from xml.sax.saxutils import escape
boxes=[('D4 seed','Checked codim >= 61,196','#e7f2fd'),('Exact count','2 solutions','#eaf8e6'),('D5 producer','Started; no output','#fff1e5')]
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="180" viewBox="0 0 960 180">','<rect width="960" height="180" fill="white"/>']
for i,(title,body,color) in enumerate(boxes):
 x=25+i*320
 parts += [f'<rect x="{x}" y="30" width="275" height="105" rx="7" fill="{color}" stroke="#7290a8"/>',f'<text x="{x+14}" y="66" font-size="19" font-weight="bold" fill="#1c2d3a">{escape(title)}</text>',f'<text x="{x+14}" y="104" font-size="17" fill="#1c2d3a">{escape(body)}</text>']
 if i<2: parts.append(f'<text x="{x+288}" y="89" font-size="23" fill="#1c2d3a">→</text>')
parts.append('</svg>')
Path(__file__).with_name('diagram.svg').write_text(''.join(parts)+'\n')
