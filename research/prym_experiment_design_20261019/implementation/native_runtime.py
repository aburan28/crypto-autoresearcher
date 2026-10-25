"""Native-launch provenance and observational rendering for the Prym audits."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import traceback
import yaml

ROOT=Path(__file__).resolve().parents[3]


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def dump(path,data):
    with Path(path).open('x') as stream:json.dump(data,stream,indent=2,sort_keys=True);stream.write('\n')


def binding(directory,experiment):
    launch=json.loads((directory/'launch.json').read_text())
    plan_path=ROOT/f'experiments/{experiment}/trial-plan.json'
    plan=json.loads(plan_path.read_text());spec=yaml.safe_load((ROOT/plan['specification']).read_text())['experiment']
    if (launch.get('plan_sha256')!=digest(plan_path) or plan['experiment_id']!=experiment
        or spec.get('frozen') is not True or spec.get('status') not in ['approved','running']
        or spec.get('execution_authorized') is not True or spec.get('approved_by')!=plan['approved_by']
        or digest(ROOT/plan['specification'])!=plan['specification_sha256']):
        raise ValueError('native approval/protocol binding mismatch')
    authority=launch.get('authority',{})
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True)
    if authority.get('commit')!=commit or not authority.get('epoch') or not authority.get('owner') or dirty:
        raise ValueError('clean source/live authority binding mismatch')
    for kind in ['source_sha256','input_sha256']:
        for path,expected in plan[kind].items():
            if digest(ROOT/path)!=expected:raise ValueError('modified frozen '+path)
    for distribution,expected in plan['dependency_versions'].items():
        if version(distribution)!=expected:raise ValueError('dependency mismatch: '+distribution)
    trial=next(t for t in plan['trials'] if t['id']==launch['trial_id'])
    if directory.resolve()!=(ROOT/f"experiments/{experiment}/runs/{trial['run_id']}").resolve():
        raise ValueError('native run path mismatch')
    return plan,commit


def render(directory,result,experiment):
    """Plot only the already recorded projected ranks; no new trial work."""
    cells=result.get('cells',[])
    points=[{'p':v['p'],'seed':v['seed'],'rank':v['projection']['rank'],'U':v['projection']['U']}
            for v in cells]
    dump(directory/'graph-source.json',{'run_id':directory.name,'source':'raw-result.json',
        'metric':'rank and unknown columns, in columns','points':points,
        'uncertainty':'exact finite matrices; no sampling interval'})
    from reportlab.graphics.shapes import Drawing,Rect,String
    from reportlab.graphics import renderSVG
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
    drawing=Drawing(480,190)
    drawing.add(String(5,177,f'{directory.name}: projected rank / unknown columns',fontSize=10))
    for j,row in enumerate(points):
        x=10+j*19
        drawing.add(Rect(x,35,6,row['U']*13,fillColor=HexColor('#b7c5d6'),strokeWidth=0))
        drawing.add(Rect(x+7,35,6,row['rank']*13,fillColor=HexColor('#2454ad'),strokeWidth=0))
        drawing.add(String(x,23,str(row['rank'])+'/'+str(row['U']),fontSize=6))
        drawing.add(String(x,13,str(row['p']),fontSize=5))
    drawing.add(String(5,2,'x=field p, repeated by seed; n='+str(len(points))+'; grey=U, blue=rank; exact counts',fontSize=7))
    renderSVG.drawToFile(drawing,str(directory/'graph.svg'))
    text=(f'# {experiment} / {directory.name}\n\nObservations only; no scientific verdict or ECDLP gain claim.\n\n'
          f"Completed: {result.get('complete')}. Fixed finite cells: {len(cells)}. "
          'Each recorded rank is modulo its target prime r, after public anchors and column normalization. '
          'All-known bases (U=0) provide no new unknown-log recovery evidence.\n\n'
          'Every attempt and rejection is in events.jsonl; explicit public witnesses, ranks and raw operation '
          'vectors are in raw-result.json. Independent checks and their costs are separate in verification.json. '
          'Raw operation units are not a complete weighted S score.\n\n'
          '![Recorded matrix ranks](graph.svg)\n\n'
          'Code revision, exact command/input/source hashes, resources, dependencies and limits: manifest.yaml '
          'and native environment.json. Software controls are deliberately planted, with public known logs; '
          'fresh cells have no supplied log labels. No novel compact router or deployed-curve conclusion.\n')
    (directory/'report.md').write_text(text)
    style=getSampleStyleSheet()
    items=[Paragraph(experiment+' / '+directory.name,style['Title']),Spacer(1,12)]
    for paragraph in text.split('\n\n')[1:]:
        if paragraph.startswith('!['):items.extend([drawing,Spacer(1,12)])
        else:items.extend([Paragraph(paragraph.replace('\n',' '),style['BodyText']),Spacer(1,12)])
    SimpleDocTemplate(str(directory/'report.pdf')).build(items)


def main(experiment,runner):
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--run-dir',required=True,type=Path)
    args=parser.parse_args();directory=args.run_dir
    plan,commit=binding(directory,experiment)
    config=json.loads(args.config.read_text());panel=json.loads((ROOT/config['fixture_file']).read_text())
    started=datetime.now(timezone.utc).isoformat();error=None
    with (directory/'events.jsonl').open('x') as stream:
        def event(record):stream.write(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n')
        try:result=runner(config,panel,event)
        except Exception as exc:
            error=repr(exc);traceback.print_exc()
            result={'complete':False,'cells':[],'error':error,'scope':'incomplete producer; no inference'}
    result.update(experiment_id=experiment,run_id=directory.name,config_sha256=digest(args.config))
    dump(directory/'raw-result.json',result)
    manifest={'run':{'id':directory.name,'experiment_id':experiment,'status':'failed' if error else 'completed',
       'code':{'commit':commit,'dirty_tree':'','command':sys.argv,
               'source_sha256':plan['source_sha256']},
       'inputs':{'config':config,'sha256':plan['input_sha256'],'specification_sha256':plan['specification_sha256']},
       'environment':{'python':platform.python_version(),'platform':platform.platform(),
                       'dependencies':plan['dependency_versions'],'native':'environment.json'},
       'timing':{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
                 'producer_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                 'wall_seconds':result.get('wall_seconds'),'cpu_seconds':result.get('cpu_seconds')},
       'result':{'raw_result':'raw-result.json','outcome':None,'error':error,
                 'limits':['No DLP gain or security claim.','Field operation counters exclude pow internals, Python bookkeeping and verifier work.',
                           'Peak self RSS is measured; native memory guard applies, no sampled process-group RSS supplied.']}}}
    with (directory/'manifest.yaml').open('x') as stream:yaml.safe_dump(manifest,stream,sort_keys=False)
    render(directory,result,experiment)
    print(json.dumps({'complete':result['complete'],'cells':len(result['cells']),'error':error}))
    return 1 if error else 0
