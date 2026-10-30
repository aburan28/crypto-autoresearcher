#!/usr/bin/env python3
"""Package completed structural profiles; no closure execution or new metric."""
import argparse
import json
from pathlib import Path
import shutil
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    study = Path(__file__).resolve().parent
    repo = study.parent.parent
    sys.path.insert(0, str(repo))
    from tools import experiment_protocol as ep
    protocol = json.loads((study/'profile-protocol-v2.json').read_text())
    plan = json.loads((study/'profile-plan.json').read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    out = args.out.resolve()
    raw = out/'raw'; raw.mkdir()
    e = ep.export_skeleton(protocol, '../../profile-protocol-v2.json', 'local', 'SEMAEV-QUOTIENT-PROFILE-001')
    e['producer'].update(runtime='codex', role='executor')
    e['source'].update(commit=protocol['arms'][0]['instrument']['commit'], dirty=True)
    e['host']['summary']['isolation_tier_max'] = 'L0'
    e['analysis']['script'] = ep.file_entry(out, '../../capacity_profile.py', 'analysis')
    values = []
    for index, item in enumerate(plan['items']):
        name = item['id']
        source = args.raw/(name+'.json'); target = raw/source.name
        shutil.copyfile(source,target)
        v = json.loads(target.read_text()); values.append(v)
        assert v['status']=='completed', 'A failed profile needs an explicit incomplete export'
        assert v['plan_sha256']==ep.sha256_file(study/'profile-plan.json')
        assert v['source_sha256']==ep.sha256_file(study/'capacity_profile.py')
        assert v['seed_sha256']==item['expected_sha256']
        assert v['working_coordinates']==v['reference_working_coordinates']
        artifact = ep.file_entry(out, 'raw/'+source.name, 'raw')
        e['files'].append(artifact)
        for arm, key in [('profile','working_coordinates'),('reference-profile','reference_working_coordinates')]:
            e['runs'].append(ep.run_row(run_id=name+'-'+arm,arm=arm,instance_id=str(index),seed=20261029,
                measurements={'counted':{'working_coordinates':v[key]}},
                isolation={'tier':'L0','contended':True,'blockers':['Shared host; no timing metric or runtime inference.']},
                verification={'status':'verified','verifier':'Two enumeration directions agree; retained seed digest and triangularity checked.'},
                artifacts=[artifact]))
    for a in e['arms']:
        a['commit']=protocol['arms'][0]['instrument']['commit']
    e['flow']=ep.compute_flow(e['runs'])
    e['notes']=[dict(kind='observation',by='Codex',text='Instance indices map in order to profile-plan.json. Both algorithm arms executed on every retained seed. No degree-five closure was run and no LFD inference follows from these counts.')]
    shutil.copyfile(study/'profile-plan.json',out/'profile-plan.json')
    e['files'].append(ep.file_entry(out,'profile-plan.json','protocol'))
    lines=['# Historical seed quotient-lift capacity','',
        'All 13 frozen historical maps passed hash identity and triangularity checks. Both independent enumeration directions agreed for every map. This is structural analysis of existing certificates, not a degree-five closure run.', '',
        '| Seed | Variables | Seed coordinates | New border | Working coordinates | Provisional map GiB | Relation basis ceiling GiB |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for v in values:
        lines.append('| '+ ' | '.join([v['id'],str(v['variables']),str(v['seed_codimension']),str(v['border_coordinates']),str(v['working_coordinates']),f"{v['provisional_map_payload_bytes']/2**30:.3f}",f"{v['relation_basis_payload_ceiling_bytes']/2**30:.3f}"])+' |')
    lines += ['', 'The payload columns count bits in the proposed representation only. They exclude seed storage, export coexistence, indices, multiplication tables, allocator overhead, the independent checker and other workspaces. They do not establish measured RSS, runtime, a valid admission limit, or any frontier bound.', '',
        'The next step is a native producer with checked allocation accounting, validation against the reference prototype and dense engine, followed by a separately frozen degree-five run. A candidate map must pass the original independent checker; its checked codimension must exceed the exact solution count to establish LFD >= 6.', '',
        'Protocol: `../../profile-protocol-v2.json`. Export: `export.json`. Version 1 has no executions; version 2 prospectively corrected the committed instrument identity. Every raw result remains under `raw/`. No source or result was overwritten.', '', '![Working coordinates](coordinates.svg)']
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    height=100+27*len(values); maximum=max(v['working_coordinates'] for v in values)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#172331"><text x="20" y="26" font-size="18">Provisional degree-five quotient coordinates</text><text x="20" y="48" font-size="12">Blue: existing seed coordinates. Orange: additional border. Derived counts, not closure results.</text>']
    for i,v in enumerate(values):
        y=65+27*i; low=510*v['seed_codimension']/maximum; high=510*v['border_coordinates']/maximum
        svg.extend([f'<text x="20" y="{y+15}">{v["id"]}</text>',f'<rect x="90" y="{y}" width="{low}" height="19" fill="#276ba1"/>',f'<rect x="{90+low}" y="{y}" width="{high}" height="19" fill="#d78320"/>',f'<text x="620" y="{y+15}">{v["working_coordinates"]:,}</text>'])
    svg.append('</g></svg>');(out/'coordinates.svg').write_text('\n'.join(svg)+'\n')
    table=[]
    for v in values:
        table.extend([v['id'],str(v['seed_codimension']),str(v['border_coordinates']),str(v['working_coordinates']),f"{v['provisional_map_payload_bytes']/2**30:.3f}"])
    cells=', '.join('['+s+']' for s in ['Seed','Seed coordinates','New border','Working coordinates','Map GiB']+table)
    typ='''#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Quotient lifting: historical seed capacity

All 13 frozen historical maps passed hash identity and triangularity checks. Two independent enumeration directions agreed on all 13 inputs. These are exact structural counts from degree-four certificates; no degree-five closure or new LFD bound is claimed.

#table(columns: 5, inset: 4pt, '''+cells+''')

#image("coordinates.svg", width: 100%)

The map column is a calculated bit payload, not measured RSS. It excludes seed storage, export coexistence, indices, multiplication tables, allocator overhead, the checker and other workspaces. No speed or frontier-admission claim follows.

The small-instance reference implementation passed 144 full-space closure comparisons and four native-producer/original-checker integration fixtures. Four corrupted constant images were rejected. These are software controls, not the frontier experiment.

Next: implement a native producer with checked allocations, cross-check it against the reference and dense engine, then freeze a new degree-five run. A lower bound of six requires independent certificate acceptance and a checked codimension strictly larger than the exact solution count. Killing the constant in an over-approximating quotient is inconclusive for the true closure.

Evidence: raw/*.json, export.json, profile-plan.json; frozen protocol ../../profile-protocol-v2.json. Shared-host timing is invalid. Version 1 had no executions; version 2 corrected the source commit before profiling.
'''
    (out/'report.typ').write_text(typ)
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
    for name in ['report.md','coordinates.svg','report.typ','report.pdf']:
        e['analysis']['outputs'].append(ep.file_entry(out,name,'report'))
    with open(out/'export.json','x') as f:json.dump(e,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(e["flow"], sort_keys=True))


if __name__=='__main__':main()
