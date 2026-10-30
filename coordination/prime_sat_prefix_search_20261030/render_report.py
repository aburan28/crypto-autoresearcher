#!/usr/bin/env python3
"""Render observation-only report sources from frozen extraction outputs."""
import argparse
import hashlib
from html import escape
import json
from pathlib import Path
from collections import Counter

def write_new(path,text):
    with path.open('x') as f:f.write(text)

def build(export_path,analysis_path,output):
    e=json.loads(export_path.read_text());a=json.loads(analysis_path.read_text());output.mkdir(parents=True,exist_ok=True)
    counts=[]
    for enc in ('quartic','membership','quadratic','quadratic_aa'):
        rows=[p for p in a['pairs'] if p['encoding']==enc]
        eligible=[p for p in rows if p['eligible_complete_pair']]
        counts.append((enc,len(eligible),sum(x['difference']<0 for x in eligible),sum(x['difference']==0 for x in eligible),sum(x['difference']>0 for x in eligible),12-len(eligible)))
    table='| Encoding | Complete pairs | Fewer model checks | Equal | More | Inconclusive |\n|---|---:|---:|---:|---:|---:|\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in counts)
    flow=a['underlying_flow']
    narrative=f"Native output validated: {a['native_output_validated']}. Frozen inventory observation: {a['fixed_inventory_observation']}. Eligible complete ordinary pairs: {a['eligible_complete_pairs']}/48; joint partial-pruning/model-check signature: {a['mechanism_signature_pairs']}. Search records: {flow['search_present']}/144; solver controls: {flow['control_present']}/9; references: {flow['reference_present']}/12."
    limits='These are fixed finite search observations. Same-backend pairs change only the timing of bounded polynomial theory calls. A partial proof requires assigned_count < n and a contiguous LSB prefix. Complete results require checked arithmetic identities, validated projected witnesses and sparse coverage, with equal complementary-point reference sets. Censored pairs remain inconclusive; gaps are not roots.'
    cost='Legacy arithmetic counters omit some primitive work. Reference instrumentation counts source-function and builtin pow events only. Partial snapshots serialize and fsync the evolving transcript after certificates/models; this I/O is real work, not a counted machine-operation total. Native search, construction, proof checks, verification and reconstruction stay separate. No recorded-vector difference establishes runtime or total-cost advantage.'
    custody=f"Protocol {e['protocol']['protocol_id']}, SHA256 {e['protocol']['sha256']}. Native bundle flow and individual raw records are bound in export.json; exact per-pair differences are in analysis.json. Six export rows are packaging, not six independent samples. The 12 reference executions are charged once. Three positive-prefix, three empty-clause and three viable-prefix controls are separate solver executions; malformed-certificate/model mutations are verifier controls."
    nexts='A positive mechanism observation can justify a separately admitted larger or held-out comparison after independent review. Absence of the signature applies only to this schedule, window and inventory. Invalid/censored data require scoped diagnosis; no silent replay, scale change or direction closure. Shared-coefficient search and local membership construction remain separate candidates. No scalar recovery, new regularity theorem, formal proof or general ECDLP speedup is claimed; the persistent goal remains active.'
    md='# Certified partial-prefix search: fixed inventory observations\n\n'+narrative+'\n\n'+table+'\n'+limits+'\n\n'+cost+'\n\n'+custody+'\n\n'+nexts+'\n'
    write_new(output/'report.md',md)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="380" viewBox="0 0 1080 380"><rect width="1080" height="380" fill="#f8fafc"/><style>text{{font-family:sans-serif;fill:#172033}}.h{{font-size:22px;font-weight:700}}.b{{font-size:16px}}.s{{font-size:14px}}</style><text x="30" y="37" class="h">Certified partial-prefix search — observation chain</text><g fill="#e8efff" stroke="#46639a"><rect x="30" y="65" width="245" height="105" rx="10"/><rect x="310" y="65" width="245" height="105" rx="10"/><rect x="590" y="65" width="205" height="105" rx="10"/><rect x="830" y="65" width="220" height="105" rx="10"/></g><g class="b"><text x="45" y="92">Same CaDiCaL / four encodings</text><text x="45" y="120">model-only versus partial</text><text x="45" y="148">48 pairs + candidate A/A</text><text x="325" y="92">Proof before prefix clause</text><text x="325" y="120">Assigned count strictly &lt; n</text><text x="325" y="148">UNKNOWN emits no cut</text><text x="605" y="92">Models + sparse cover</text><text x="605" y="120">Projected completeness</text><text x="605" y="148">12 reference certificates</text><text x="845" y="92">Report all outcomes</text><text x="845" y="120">Censored = inconclusive</text><text x="845" y="148">No runtime inference</text></g><g stroke="#46639a" stroke-width="2"><path d="M275 118H310M555 118H590M795 118H830"/></g><text x="30" y="213" class="b">Eligible complete pairs: {a['eligible_complete_pairs']} / 48 · Joint mechanism signature: {a['mechanism_signature_pairs']}</text><text x="30" y="248" class="s">All 144 search executions, 9 solver controls and 12 reference cells remain in the raw inventory.</text><text x="30" y="275" class="s">Separate phase counters; missing total machine work, snapshot I/O and source-event units limit cost conclusions.</text><text x="30" y="311" class="s">{escape(a['fixed_inventory_observation'])}</text><text x="30" y="343" class="s">No general ECDLP, scalar-recovery, formal-proof, novelty or degree-of-regularity claim.</text></svg>'''
    write_new(output/'diagram.svg',svg)
    para=lambda x:'#text('+json.dumps(x)+')\n\n'
    typ='#set page(paper: "a4", margin: 16mm)\n#set text(size: 10pt, font: "DejaVu Sans")\n#set par(justify: false)\n#text(size: 19pt, weight: "bold")[Certified partial-prefix search]\n\n'+para(narrative)+'#image("diagram.svg", width: 100%)\n\n'+para(limits)+para(cost)+'#pagebreak()\n#text(size: 16pt, weight: "bold")[Complete paired observations]\n\n'
    typ+='#table(columns: (1.7fr, 1fr, 1fr, 1fr, 1fr, 1fr), inset: 5pt, '+', '.join('['+str(v).replace('_','\\_')+']' for row in [('Encoding','Complete','Fewer','Equal','More','Inconcl.')]+counts for v in row)+')\n\n'+para(custody)+para(nexts)
    write_new(output/'report.typ',typ)
    manifest={'schema':'prime-prefix-search-report/v1','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [export_path,analysis_path]},'authored':{name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ['report.md','diagram.svg','report.typ']},'rendering':{'status':'pending_root','pdf_sha256':None,'page_count':None,'visually_inspected':False},'scope':'Observation report; independent review and actual archive required before scientific interpretation; no status promotion.'}
    write_new(output/'report-manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'report_sources':str(output),'pdf':'pending root render and visual inspection'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--export',type=Path,required=True);ap.add_argument('--analysis',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();build(a.export,a.analysis,a.output)
