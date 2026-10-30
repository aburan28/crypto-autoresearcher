from pathlib import Path
import json,html
p=Path(__file__).parent;d=json.loads((p/'observations.json').read_text());rows=[r for r in d['component_views'] if r['scope']=='all_confirmation']
labels={'original':'Strict original','incremental_strict':'Incremental strict','incremental_plus_t1.e2':'Incremental + primary'}
s=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300" viewBox="0 0 900 300"><rect width="900" height="300" fill="white"/><style>text{font-family:DejaVu Sans,sans-serif;font-size:15px}.small{font-size:12px}</style><text x="15" y="25">Recorded chosen-path components</text><text x="220" y="52" class="small">Worker group-add calls (source counter)</text><text x="660" y="52" class="small">Distinct targets recovered</text>']
for i,r in enumerate(rows):
 y=82+i*65;g=r['source_instrumented_components']['group_add_call'];n=r['unique_targets_recovered'];s.extend([f'<text x="15" y="{y+18}">{html.escape(labels[r["choice"]])}</text>',f'<rect x="220" y="{y}" width="{g/4000000*300:.2f}" height="27" fill="#355c86"/>',f'<text x="{230+g/4000000*300:.2f}" y="{y+19}" class="small">{g:,}</text>',f'<rect x="660" y="{y}" width="{n/40*150:.2f}" height="27" fill="#278574"/>',f'<text x="{670+n/40*150:.2f}" y="{y+19}">{n}</text>'])
s.append('<text x="15" y="292" class="small">Same retained 1,536 targets; separate axes/units; all failure work retained. No complete-cost or runtime inference.</text></svg>');(p/'diagram.svg').write_text(''.join(s))
