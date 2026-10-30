#!/usr/bin/env python3
"""Archive a complete native-lift batch without converting unknown into false."""
import argparse
import json
from pathlib import Path
import shutil
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    study=Path(__file__).resolve().parent;sys.path.insert(0,str(study.parent.parent))
    from tools import experiment_protocol as ep
    plan=json.loads((study/'lift-plan.json').read_text())
    protocol=json.loads((study/'lift-protocol.json').read_text())
    sources=[]
    for item in plan['items']:
        paths=sorted((args.raw/item['id']).glob('attempt-*/result.json'))
        if not paths:raise RuntimeError('Batch is incomplete; no finished record for '+item['id'])
        sources.append((item,paths[-1]))
    args.out.mkdir(parents=True,exist_ok=False);out=args.out.resolve()
    e=ep.export_skeleton(protocol,'../../lift-protocol.json','local','SEMAEV-NATIVE-LIFT-HISTORICAL-001')
    e['producer'].update(runtime='codex',role='executor')
    e['source'].update(commit=protocol['arms'][0]['instrument']['commit'],dirty=True)
    e['host']['summary']['isolation_tier_max']='L0'
    e['analysis']['script']=ep.file_entry(out,'../../run_lifts.py','analysis')
    for a,p in zip(e['arms'],protocol['arms']):
        a['commit']=p['instrument']['commit'];a['binary_sha256']=p['instrument']['binary_sha256']
    summaries=[]
    for index,(item,path) in enumerate(sources):
        r=json.loads(path.read_text())
        assert r['plan_sha256']==ep.sha256_file(study/'lift-plan.json')
        target=out/'raw'/item['id']/path.parent.name;target.mkdir(parents=True)
        for src in path.parent.iterdir():
            if src.is_file() and src.name!='certificate.bin':
                shutil.copyfile(src,target/src.name)
        if r['status']=='certificate_verified':
            ack=study/'archive'/(item['id']+'.publication.json')
            publication=json.loads(ack.read_text())
            assert publication['certificate_sha256']==r['certificate_sha256']
            shutil.copyfile(ack,target/'certificate-publication.json')
        for src in sorted(target.iterdir()):
            e['files'].append(ep.file_entry(out,str(src.relative_to(out)),'raw'))
        artifact=ep.file_entry(out,str((target/'result.json').relative_to(out)),'raw')
        count=r['steps'].get('count')
        if count is None:raise RuntimeError('Unattempted counter needs explicit infrastructure export handling')
        count_ok=count['returncode']==0 and 'exact_solutions' in r
        produced=r['status'] in ('certificate_verified','projection_kills_one')
        for arm,ok in [('producer',produced),('exact-count',count_ok)]:
            measured={}
            if arm=='producer' and r.get('certified_codimension_lower_bound') is not None:
                measured['certified_codimension_lower_bound']=r['certified_codimension_lower_bound']
            if arm=='exact-count' and count_ok:measured['exact_solutions']=r['exact_solutions']
            verified=(r['status']=='certificate_verified') if arm=='producer' else (count_ok and r.get('matches_historical_solution_count',False))
            e['runs'].append(ep.run_row(run_id=item['id']+'-'+arm,arm=arm,instance_id=str(index),seed=20261029,
                status='succeeded' if ok else 'failed',measurements={'counted':measured},
                isolation={'tier':'L0','contended':True,'blockers':['Shared-host clock invalid; no timing inference.']},
                verification={'status':'verified' if verified else 'no_claim','verifier':'Original independent closure checker' if arm=='producer' and verified else ('Pinned exact counter and agreement with historical count' if verified else None)},artifacts=[artifact]))
        if r['last_fall_degree_lower_bound']:
            assert r['status']=='certificate_verified' and r['exact_solutions']<r['certified_codimension_lower_bound']
        summaries.append(dict(id=item['id'],seed=item['seed_id'],status=r['status'],exact_solutions=r.get('exact_solutions'),certified_codimension=r.get('certified_codimension_lower_bound'),lfd_lower_bound=r['last_fall_degree_lower_bound']))
    e['flow']=ep.compute_flow(e['runs'])
    e['notes']=[dict(kind='observation',by='Codex',text='Both producer and count stages executed on all thirteen inputs. Projection_kills_one remains inconclusive for membership in the true closure. Stage completion is not a certified bound.')]
    (out/'summary.json').write_text(json.dumps(summaries,indent=2,sort_keys=True)+'\n')
    e['files'].append(ep.file_entry(out,'summary.json','summary'))
    lines=['# Native degree-five historical lift batch','',
        'All thirteen frozen historical inputs were attempted. A certificate is accepted only after the original independent checker; LFD >= 6 additionally requires the exact solution count to be strictly smaller than its checked codimension.', '',
        '| Seed | Outcome | Exact solutions | Checked codimension | LFD lower bound from D5 |',
        '|---|---|---:|---:|---:|']
    for v in summaries:
        lines.append('| '+' | '.join(str(v[k]) if v[k] is not None else 'unknown' for k in ['seed','status','exact_solutions','certified_codimension','lfd_lower_bound'])+' |')
    lines+=['','`projection_kills_one` means the constructed quotient kills the constant. Its seed kernel is only independently known to contain W4, so this outcome is not a proved refutation in W5 and does not establish an upper bound. A certificate with codimension equal to the solution count gives no degree-six lower bound.','',
        'The first owner stopped after T33a because an upstream merge reapplied sparse patterns. The new directory was added permanently, frozen hashes were verified, and the terminated owner was confirmed. The resumed runner reused T33a and processed the remaining inputs. No completed elimination was rerun.','',
        'Sources: raw records, public certificate acknowledgements, summary.json, export.json and ../../lift-protocol.json. Original trace output is retained. The n47..51 frontier panel remains a separate unfinished requirement.','', '![Native outcomes](outcomes.svg)']
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    height=90+29*len(summaries)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#182332"><text x="20" y="28" font-size="19">Native degree-five construction outcomes</text><text x="20" y="49" font-size="12">Blue: independently accepted map. Gray: inconclusive quotient outcome. Not upper-bound evidence.</text>']
    for i,v in enumerate(summaries):
        y=68+29*i;color='#276ba1' if v['status']=='certificate_verified' else '#aeb5bd'
        svg.extend([f'<text x="20" y="{y+15}">{v["seed"]}</text>',f'<rect x="95" y="{y}" width="18" height="18" fill="{color}"/>',f'<text x="130" y="{y+15}">{v["status"]}; LFD lower bound: {v["lfd_lower_bound"] or "unknown"}</text>'])
    svg.append('</g></svg>');(out/'outcomes.svg').write_text('\n'.join(svg)+'\n')
    cells=[]
    for v in summaries:cells.extend([v['seed'],v['status'].replace('_',' '),str(v['exact_solutions']),str(v['certified_codimension']) if v['certified_codimension'] is not None else 'unknown',str(v['lfd_lower_bound']) if v['lfd_lower_bound'] is not None else 'unknown'])
    table=', '.join('['+x+']' for x in ['Seed','Outcome','Solutions','Codimension','D5 LFD bound']+cells)
    typ='''#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Native degree-five historical lift batch

All thirteen fixed historical inputs were attempted. Acceptance requires the original independent checker. A last-fall-degree lower bound of six additionally requires a strictly smaller exact solution count than the checked codimension.

#table(columns: (auto, 1fr, auto, auto, auto), inset: 4pt, '''+table+''')

#image("outcomes.svg", width: 100%)

A quotient killing the constant is inconclusive for membership in W5: its seed kernel was independently checked as a superspace, not as exactly W4. No upper bound is inferred from that outcome. Equal solution count and checked codimension give no lower bound of six.

The first owner stopped after T33a when an upstream merge reapplied sparse patterns. The directory was restored permanently and frozen hashes rechecked. The resumed owner reused T33a and processed the remaining inputs. No completed elimination was repeated.

Raw records, checker transcripts, count logs and certificate publication acknowledgements are retained beside `export.json`. Protocol: `../../lift-protocol.json`. Source and binaries are pinned; no timing metric is valid on the shared host. The n47–51 frontier panel remains unfinished.
'''
    (out/'report.typ').write_text(typ)
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
    for name in ['report.md','outcomes.svg','report.typ','report.pdf']:e['analysis']['outputs'].append(ep.file_entry(out,name,'report'))
    with open(out/'export.json','x') as f:json.dump(e,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(e['flow'],sort_keys=True))


if __name__=='__main__':main()
