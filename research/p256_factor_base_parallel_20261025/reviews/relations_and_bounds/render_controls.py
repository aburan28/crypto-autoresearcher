#!/usr/bin/env python3
"""Render previously recorded exact review results; no new scientific trial."""
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

H=Path(__file__).resolve().parent
d=json.loads((H/'independent-results.json').read_text())['sections']
fig,axes=plt.subplots(1,3,figsize=(14,4.3))
graphs=d['F4']['details']['graphs']
names=['Combined','One outside','Two outside','Unsigned triangle']
for off,idx,label,color in [(-.24,0,'All columns','#475569'),(0,1,'Outside columns','#d97706'),(.24,2,'After cancellation','#0891b2')]:
    axes[0].bar([i+off for i in range(4)],[g['ranks'][idx] for g in graphs],width=.24,label=label,color=color)
axes[0].set_xticks(range(4),names,rotation=22,ha='right')
axes[0].set_ylabel('Exact rank over F_r')
axes[0].set_title('F4: rank after signed cancellation')
axes[0].legend(fontsize=7)

capacity=d['F6']['details']['capacity_minimum_B']
ceilings=[64,256*5/96]
for off,vals,label,color in [(-.18,ceilings,'Relaxed family ceiling (strict)','#d97706'),(.18,[math.log2(capacity[str(s)]) for s in [2,3]],'Necessary capacity threshold','#0891b2')]:
    axes[1].bar([i+off for i in range(2)],vals,width=.36,label=label,color=color)
axes[1].set_xticks(range(2),['Two summands','Three summands'])
axes[1].set_ylabel('log2(B), interval c through c+B')
axes[1].set_title('F6: sufficient window vs capacity')
axes[1].legend(fontsize=7)

ranks=d['F8']['details']['ranks']
axes[2].bar(['Known S','Raw R','Stacked','Compressed'],[ranks[x] for x in ['symmetry','full','joint','compressed']],color=['#d97706','#475569','#64748b','#0891b2'])
axes[2].set_ylabel('Exact rank over F_r')
axes[2].set_title('F8: 47 - 40 = 7')
for ax in axes:
    ax.set_axisbelow(True)
    ax.grid(axis='y',alpha=.2)
    ax.spines[['top','right']].set_visible(False)
fig.suptitle('TASK-20261025-6d88b2: local exact checks, no performance measurement',fontsize=12)
fig.tight_layout()
fig.savefig(H/'review-controls.svg')
plt.close(fig)

svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="320" viewBox="0 0 1000 320">
<style>text{font-family:DejaVu Sans,sans-serif;font-size:15px;fill:#0f172a}.box{fill:#e0f2fe;stroke:#0369a1;stroke-width:2}.limit{fill:#fff7ed;stroke:#c2410c;stroke-width:2}.line{stroke:#475569;stroke-width:2;fill:none}</style>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#475569"/></marker></defs>
<rect x="20" y="40" width="280" height="90" rx="8" class="box"/><text x="35" y="65">Independent uniform labels</text><text x="35" y="90">Point-only c, c mod r nonzero</text><text x="35" y="115">F3: B uniform in F_r</text>
<rect x="360" y="40" width="280" height="90" rx="8" class="box"/><text x="375" y="65">Complete arithmetic certificates</text><text x="375" y="90">F4: signed kernel, F6: norm</text><text x="375" y="115">F8: exact scalar quotient</text>
<path d="M300,85 L355,85" class="line" marker-end="url(#arrow)"/>
<rect x="700" y="40" width="280" height="90" rx="8" class="limit"/><text x="715" y="65">Ordinary-target success and cost</text><text x="715" y="90">Extraction, rank growth, reuse</text><text x="715" y="115">Remain separate obligations</text>
<path d="M640,85 L695,85" class="line" stroke-dasharray="6 5" marker-end="url(#arrow)"/>
<rect x="20" y="180" width="960" height="100" rx="8" class="limit"/><text x="35" y="205">Rejected controls: zero-Q / label-dependent selection; inverse-only rows; unsigned triangle;</text><text x="35" y="230">one polynomial without finite extraction; known-root offsets as unknown-target evidence;</text><text x="35" y="255">false compressed full-rank relation; unequal symmetry access for comparisons.</text>
<text x="20" y="305">Local sealed inputs; no official review gate, publication, or scientific state transition.</text>
</svg>'''
(H/'scope-diagram.svg').write_text(svg)
print('Rendered review-controls.svg and scope-diagram.svg from retained exact checks.')
