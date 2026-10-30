#!/usr/bin/env python3
"""Report retained composite transport controls without inventing arm rows."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile


def main():
    ap=argparse.ArgumentParser()
    for name in ('evidence','protocol','plan','out'):
        ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();study=Path(__file__).resolve().parent
    sys.path.insert(0,str(study.parent.parent))
    from tools import experiment_protocol as ep
    a.out.mkdir(parents=True,exist_ok=False);out=a.out.resolve()
    r=json.loads((a.evidence/'result.json').read_text());manifest=json.loads((a.evidence/'raw-manifest.json').read_text())
    assert r['plan_sha256']==ep.sha256_file(a.plan)
    with tarfile.open(a.evidence/'raw-evidence.tar.gz','r:gz') as t:
        assert set(t.getnames())==set(manifest)
        for entry in t:
            b=t.extractfile(entry).read();m=manifest[entry.name]
            assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
    for name in ('result.json','raw-manifest.json','raw-evidence.tar.gz'):
        shutil.copyfile(a.evidence/name,out/name)
    shutil.copyfile(a.protocol,out/'protocol.json');shutil.copyfile(a.plan,out/'plan.json')
    protocol=json.loads(a.protocol.read_text())
    script=study/protocol['analysis_plan']['script']['path']
    assert ep.sha256_file(script)==protocol['analysis_plan']['script']['sha256']
    shutil.copyfile(script,out/'analysis.py')
    export=ep.export_skeleton(protocol,'protocol.json','local','SEMAEV-TRANSPORT-'+a.out.name.upper())
    export['producer'].update(runtime='codex',role='executor')
    export['source'].update(commit=protocol['freeze']['commit'],dirty=True)
    export['host']['summary']['isolation_tier_max']='L0'
    for arm,pinned in zip(export['arms'],protocol['arms']):
        arm.update(commit=pinned['instrument']['commit'],binary_sha256=pinned['instrument']['binary_sha256'])
    artifact=ep.file_entry(out,'result.json','raw')
    for row in r['cases']:
        export['runs'].append(ep.run_row(run_id=row.get('retention','candidate')+'-'+row['case'],arm=row.get('retention','candidate'),instance_id=row.get('instance_id',row['case']),seed=row.get('seed'),
            status='succeeded' if row['passed'] else 'failed',measurements={'counted':{'controls_passed':int(row['passed'])}},
            isolation={'tier':'L0','contended':True,'blockers':['Shared host; no timing comparison']},
            verification={'status':'verified' if row['passed'] else 'error','verifier':'Frozen local fake-AWS assertion harness'},artifacts=[artifact]))
    export['flow']=ep.compute_flow(export['runs'])
    export['analysis']['script']=ep.file_entry(out,'analysis.py','analysis')
    export['files']=[ep.file_entry(out,name,'raw') for name in ('result.json','raw-manifest.json','raw-evidence.tar.gz','plan.json')]
    export['notes']=[dict(kind='observation',by='Codex',text='Exactly one composite case per actually executed configuration row. No copied control rows. Fake-S3 software evidence only; no real cloud or frontier inference.')]
    findings=ep.lint_export(export,protocol,out,verify_files=True)
    save=lambda name,obj:(out/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    save('export-validation.json',dict(valid=not findings,findings=findings))
    passed=sum(row['passed'] for row in r['cases']);total=len(r['cases'])
    scope=f'{passed} of {total} fixed local fake-S3 controls passed. The archive contains {len(manifest)} hash-verified files. This is not actual cloud permission or durability evidence and establishes no LFD bound.'
    gap=('Export validation passed for the composite case rows.' if not findings else
         'Export is incomplete: the frozen protocol declares separate arms but the harness recorded composite candidate cases. Missing arm rows are not fabricated. A prospective corrected-protocol replay is required for a valid export.')
    lines=['# Checkpoint transport controls','',scope,'',gap,'','| Configuration | Case | Passed | Child steps |','|---|---|---:|---:|']
    for row in r['cases']:lines.append(f'| {row.get("retention","candidate")} | {row["case"]} | {row["passed"]} | {row["steps"]} |')
    detail='The workload uses a filesystem-only fake AWS executable. Controls cover interrupted PUT/GET, corruption, idempotence, verified pruning, fallback, context mismatch, incomplete listing, and native replay against retained reference certificate bytes. Child commands and their original stdout/stderr are in the evidence archive. Each child has a 1 GiB cap and 120-second watchdog; timings are L0 telemetry only. Inputs, code and native binary hashes are in plan.json. The source revision is pinned in protocol.json. Actual cloud publish, replacement-worker restore and independent certificate checking remain required. No canonical mathematical graph changes; this diagram records software-control status only.'
    (out/'report.md').write_text('\n'.join(lines)+'\n\n'+detail+'\n\n![Control outcome](outcomes.svg)\n')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="150"><rect width="900" height="150" fill="white"/><g font-family="sans-serif" font-size="20"><text x="20" y="35">Local fake-S3 controls: {passed}/{total} passed</text><rect x="20" y="55" width="{min(800,passed*25)}" height="30" fill="#468763"/><text x="20" y="125">Actual cloud recovery and frontier bound: not established</text></g></svg>'
    (out/'outcomes.svg').write_text(svg)
    cells=', '.join('['+str(v).replace('_','\\_')+']' for row in r['cases'] for v in (row.get('retention','candidate'),row['case'],row['passed'],row['steps']))
    (out/'report.typ').write_text('#set page(paper:"a4",margin:18mm)\n#set text(size:9pt)\n= Checkpoint transport controls\n\n'+scope+'\n\n'+gap+'\n\n#image("outcomes.svg",width:100%)\n\n#table(columns:(auto,3fr,auto,auto),[Mode],[Case],[Passed],[Steps],'+cells+')\n\n'+detail+'\n')
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
    for name in ('report.md','report.typ','report.pdf','outcomes.svg','export-validation.json'):
        export['analysis']['outputs'].append(ep.file_entry(out,name,'report'))
    save('export.json',export)
    print(json.dumps(dict(passed=passed,total=total,export_valid=not findings,findings=findings)))


if __name__=='__main__':
    main()
