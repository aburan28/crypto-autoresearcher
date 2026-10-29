#!/usr/bin/env python3
"""Immutable cascade progress report; pending inputs never become measured rows."""
import argparse
import collections
import datetime
import json
from pathlib import Path
import shutil
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('raw','out','archive'):
        ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args()
    study=Path(__file__).resolve().parent
    sys.path.insert(0,str(study.parent.parent))
    from tools import experiment_protocol as ep
    plan=json.loads((study/'cascade-plan.json').read_text())
    protocol=json.loads((study/'cascade-protocol.json').read_text())
    args.out.mkdir(parents=True,exist_ok=False)
    out=args.out.resolve()
    shutil.copyfile(study/'cascade-protocol.json',out/'protocol.json')
    shutil.copyfile(study/'cascade-plan.json',out/'plan.json')
    e=ep.export_skeleton(protocol,'protocol.json','local','SEMAEV-CASCADE-FRONTIER-001')
    e['producer'].update(runtime='codex',role='executor')
    e['source'].update(commit=protocol['arms'][0]['instrument']['commit'],dirty=True)
    e['host']['summary']['isolation_tier_max']='L0'
    shutil.copyfile(study/'run_cascade.py',out/'analysis.py')
    e['analysis']['script']=ep.file_entry(out,'analysis.py','analysis')
    for a,p in zip(e['arms'],protocol['arms']):
        a['commit']=p['instrument']['commit'];a['binary_sha256']=p['instrument']['binary_sha256']
    rows=[]
    missing_publications=[]
    for index,item in enumerate(plan['items']):
        paths=sorted((args.raw/item['id']).glob('attempt-*/result.json'))
        row=dict(id=item['id'],n=item['record']['n'],status='pending',stages=[],bound=None,count=None)
        if paths:
            path=paths[-1];r=json.loads(path.read_text())
            assert r['plan_sha256']==ep.sha256_file(study/'cascade-plan.json')
            for name,entry in r['artifacts'].items():
                source=path.parent/name
                assert source.stat().st_size==entry['bytes'] and ep.sha256_file(source)==entry['sha256'], str(source)
            target=out/'raw'/item['id']/path.parent.name;target.mkdir(parents=True)
            for src in path.parent.iterdir():
                if src.is_file() and src.suffix!='.bin':
                    shutil.copyfile(src,target/src.name)
            for stage in r['stages']:
                ack=args.archive/(item['id']+f'-D{stage["degree"]}.publication.json')
                if ack.exists():
                    a=json.loads(ack.read_text())
                    assert a['certificate_sha256']==stage['certificate_sha256']
                    shutil.copyfile(ack,target/ack.name)
                else:
                    missing_publications.append(item['id']+f'-D{stage["degree"]}')
            for src in sorted(target.iterdir()):
                e['files'].append(ep.file_entry(out,str(src.relative_to(out)),'raw'))
            artifact=ep.file_entry(out,str((target/'result.json').relative_to(out)),'raw')
            final=next((s for s in r['stages'] if s['degree']==5),None)
            count=r['steps'].get('count',{})
            count_ok=count.get('returncode')==0 and 'exact_solutions' in r
            produced=r['status'] in ('certificate_verified','projection_kills_one','seed_without_certificate')
            for arm,ok in [('producer',produced),('exact-count',count_ok)]:
                measured={}
                if arm=='producer' and final:measured['certified_codimension_lower_bound']=final['certified_codimension']
                if arm=='exact-count' and count_ok:measured['exact_solutions']=r['exact_solutions']
                verified=bool(final) if arm=='producer' else count_ok
                e['runs'].append(ep.run_row(run_id=item['id']+'-'+arm,arm=arm,instance_id=str(index),seed=20261029,
                    status='succeeded' if ok else 'failed',measurements={'counted':measured},
                    isolation={'tier':'L0','contended':True,'blockers':['Shared-host clock invalid; no timing inference.']},
                    verification={'status':'verified' if verified else 'no_claim','verifier':('Original independent checker' if arm=='producer' else 'Pinned exhaustive solution counter') if verified else None},artifacts=[artifact]))
            row.update(status=r['status'],stages=r['stages'],bound=r['last_fall_degree_lower_bound'],count=r.get('exact_solutions'))
        rows.append(row)
    counts=dict(collections.Counter(r['status'] for r in rows))
    progress=dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(rows),
        terminal=len(rows)-counts.get('pending',0),statuses=counts,missing_publications=missing_publications,
        lfd_ge6=sum(r['bound'] is not None and r['bound']>=6 for r in rows),rows=rows)
    (out/'progress.json').write_text(json.dumps(progress,indent=2,sort_keys=True)+'\n')
    lines=['# Frontier cascade progress','',progress['created_at'],'',
        f'{progress["terminal"]} / {len(rows)} terminal inputs; {progress["lfd_ge6"]} recorded LFD >= 6 bounds.',
        '', 'Pending means no terminal result, including an input currently running. Intermediate logs from live attempts are not imported as completed rows.', '',
        '| Input | Outcome | Count | Accepted degrees | LFD lower bound |','|---|---|---:|---|---:|']
    cells=[]
    for r in rows:
        values=[r['id'],r['status'],str(r['count']) if r['count'] is not None else 'unknown',','.join(str(s['degree']) for s in r['stages']) or 'none',str(r['bound']) if r['bound'] is not None else 'unknown']
        lines.append('| '+' | '.join(values)+' |');cells.extend(values)
    lines+=['','Resource refusal and quotients killing the constant do not establish upper bounds. A recorded bound comes only from an accepted stage and a strictly smaller exact count. Later uncompleted stages remain unknown.','', '![Outcome counts](outcomes.svg)']
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="'+str(70+34*len(counts))+'"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" fill="#182332"><text x="20" y="25" font-size="18">Frontier cascade outcomes (pending included)</text>']
    for i,(name,count) in enumerate(sorted(counts.items())):
        y=45+34*i
        svg.append(f'<text x="20" y="{y+17}">{name}</text><rect x="245" y="{y}" width="{count*8}" height="23" fill="#6686a0"/><text x="{255+count*8}" y="{y+17}">{count}</text>')
    svg.append('</g></svg>');(out/'outcomes.svg').write_text('\n'.join(svg)+'\n')
    escaped=lambda x:'['+x.replace('_','\\_')+']'
    table=', '.join(map(escaped,['Input','Outcome','Count','Degrees','LFD bound']+cells))
    typ='#set page(paper: "a4", margin: 15mm)\n#set text(size: 8pt)\n= Frontier cascade progress\n\n'+str(progress['terminal'])+' / 50 inputs terminal. LFD >= 6 bounds recorded: '+str(progress['lfd_ge6'])+'.\n\nPending includes live, unfinished inputs. Refusal and killed-constant outcomes give no upper bound. Bounds require an accepted certificate and strictly smaller exact count.\n\n#image("outcomes.svg", width: 100%)\n\n#table(columns: (2fr, 1.3fr, auto, auto, auto), inset: 3pt, '+table+')\n\nRaw terminal records and publication acknowledgements accompany `progress.json`; `protocol.json` and `plan.json` preserve the frozen scope. No clock or population inference.\n'
    (out/'report.typ').write_text(typ)
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
    if progress['terminal']==len(rows) and not missing_publications:
        e['flow']=ep.compute_flow(e['runs'])
        e['notes']=[dict(kind='observation',by='Codex',text='All50 attempts terminal. Lift stages conditional on prior accepted map; only accepted D5 maps populate the D5 codimension metric.')]
        e['files'].append(ep.file_entry(out,'progress.json','summary'))
        for name in ('report.md','report.typ','report.pdf','outcomes.svg'):
            e['analysis']['outputs'].append(ep.file_entry(out,name,'report'))
        (out/'export.json').write_text(json.dumps(e,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:progress[k] for k in ('planned','terminal','statuses','lfd_ge6')}))


if __name__=='__main__':
    main()
