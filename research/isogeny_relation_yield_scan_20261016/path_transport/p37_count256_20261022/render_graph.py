"""Draw the saved public targetwise ordered counts; no new sampling."""
from pathlib import Path
import sys
root = Path(sys.argv[1])
out = Path(sys.argv[2])
def counts(path):
    lines = path.read_text().splitlines()
    return [int(row.split('\t')[2]) for row in lines[1:]]
source = counts(root / 'source.count')
transported = counts(root / 'transported.count')
if len(source) != 128 or len(transported) != 128:
    raise ValueError('unexpected target count')
x = lambda i: 90 + 640*i/127
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="380" viewBox="0 0 800 380">',
     '<rect width="800" height="380" fill="white"/>',
     '<style>text{font-family:Arial,sans-serif;fill:#243447;font-size:13px}.axis{stroke:#44566c;stroke-width:1.2}.grid{stroke:#dbe4ed}.source{stroke:#356b9b;stroke-width:4}.transported{stroke:#c85e36;stroke-width:4}</style>',
     '<text x="90" y="28" font-size="17" font-weight="bold">P37 public control: ordered triples on 128 paired targets</text>',
     '<text x="90" y="62">Source base</text><text x="90" y="204">Transported base at vertex 256</text>']
for baseline, data, cls in ((170,source,'source'),(312,transported,'transported')):
    s.append(f'<line class="axis" x1="90" y1="{baseline}" x2="730" y2="{baseline}"/>')
    for i, n in enumerate(data):
        if n: s.append(f'<line class="{cls}" x1="{x(i):.1f}" y1="{baseline}" x2="{x(i):.1f}" y2="{baseline-6*n}"/>')
    for i in (0,32,64,96,127): s.append(f'<text x="{x(i):.1f}" y="{baseline+20}" text-anchor="middle">{i}</text>')
s.extend(['<text x="410" y="358" text-anchor="middle">Target index (same public scalar on both endpoints)</text>',
          '<text x="500" y="86">Bar height: 6 px per ordered triple</text>',
          '</svg>'])
out.write_text('\n'.join(s)+'\n')
