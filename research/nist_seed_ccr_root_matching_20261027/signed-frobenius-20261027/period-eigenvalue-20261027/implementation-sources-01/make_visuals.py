"""Render retained counts and source boundaries; performs no curve arithmetic."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

P = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'svg.fonttype': 'none'})


def save(fig, name):
    fig.savefig(P/(name+'.svg'), bbox_inches='tight', metadata={'Date': None})
    f = P/(name+'.svg')
    f.write_text('\n'.join(line.rstrip() for line in f.read_text().splitlines())+'\n')
    fig.savefig(P/(name+'.png'), bbox_inches='tight', dpi=220)
    plt.close(fig)


fig, ax = plt.subplots(figsize=(8.4, 3.1))
ax.set(xlim=(0, 1), ylim=(0, 1))
ax.axis('off')
boxes = [
    (.02, .64, .29, .27, 'RECOVERED SOURCE\nMa94: 29 July 1994\n130 pages; exact PS hash'),
    (.365, .64, .29, .27, 'DOCUMENTED MECHANISMS\nCRT and baby-step bounds\nType2 repeated-fiber gap'),
    (.71, .64, .27, .27, 'RETAINED COHORT CHECK\n21 curves, six streams\n0 repeated fibers / 2071'),
    (.17, .10, .66, .25, 'HISTORICAL USE UNESTABLISHED\nOriginal caller, table bytes, defaults and visitation still missing'),
]
for i, (x, y, w, h, label) in enumerate(boxes):
    color = '#E7F0FA' if i < 2 else '#E7F4ED' if i == 2 else '#FFF0D8'
    ax.add_patch(FancyBboxPatch((x,y), w,h, boxstyle='round,pad=0.008',
                               facecolor=color, edgecolor='#345370',
                               linestyle='--' if i == 3 else '-', linewidth=1.1))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=8.3, linespacing=1.5)
for a,b in [((.315,.775),(.355,.775)),((.66,.775),(.70,.775)),((.845,.60),(.69,.38))]:
    ax.annotate('', xy=b, xytext=a, arrowprops={'arrowstyle':'->','color':'#526477'})
ax.text(.5, .005, 'T-5518 implementation-sources-01 | Source interpretation of existing evidence; no new scientific trials',
        ha='center', va='bottom', fontsize=7.5, color='#45546A')
save(fig, 'source-chain')

rows = list(csv.DictReader((P/'cohort-crosswalk.csv').open()))
fig, ax = plt.subplots(figsize=(8.4, 6.3))
y = list(range(len(rows)))
a = [int(r['type1_source_and_fricke_fibers']) for r in rows]
b = [int(r['type2_fibers']) for r in rows]
ax.barh(y, a, color='#4D759D', label='Type1 source and Fricke target fibers')
ax.barh(y, b, left=a, color='#D89435', label='Type2 fibers')
labels = [f"{int(r['p']).bit_length()} bit | ordinal {r['ordinal']} | {'published' if r['label']=='published' else 'omitted'}" for r in rows]
ax.set_yticks(y, labels, fontsize=8)
ax.invert_yaxis()
ax.set_xlabel('Retained fibers with exact derivative certificates (count)')
ax.set_title('Coverage of every reconstructed omission and publication', loc='left', fontsize=12, pad=36)
ax.text(0, 1.025, '21 curves x 61 levels; 1772 type1 + 299 type2 = 2071 fibers. All repeated-fiber counts are zero.',
        transform=ax.transAxes, fontsize=8.4)
ax.legend(loc='upper left', bbox_to_anchor=(0, -.10), fontsize=8, frameon=False)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='x', alpha=.15)
ax.set_axisbelow(True)
fig.text(.02, .005, 'Existing modular-coordinate-guards evidence, later LiDIA tables, ell=3..293. Counts are exact; historical table identity is unknown.',
         fontsize=7.2)
fig.subplots_adjust(left=.33, top=.88, bottom=.18)
save(fig, 'fiber-coverage')
