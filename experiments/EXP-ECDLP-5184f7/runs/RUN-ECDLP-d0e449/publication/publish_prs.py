#!/usr/bin/env python3
"""Publish ready stacked PRs after normal GitHub credentials become available."""
import datetime
import json
import os
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=Path('/workspace/solinas-run')
PLAN=json.loads((ROOT/'publication-plan.json').read_text())
env=dict(os.environ)
env['GIT_TERMINAL_PROMPT']='0'
results={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':PLAN['repo'],
         'PRs':[],'status':'not_started','commands':[]}


def call(cmd):
    r=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,text=True)
    results['commands'].append({'argv':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    if r.returncode:raise RuntimeError(r.stderr.strip() or r.stdout.strip())
    return r.stdout.strip()


try:
    call(['gh','api','repos/'+PLAN['repo'],'--jq','{full_name,default_branch,permissions}'])
    call(['git','-c','credential.helper=!gh auth git-credential','push','--atomic','origin']+[r['head']for r in PLAN['branches']])
    for row in PLAN['branches']:
        existing=json.loads(call(['gh','pr','list','--repo',PLAN['repo'],'--head',row['head'],'--base',row['base'],
            '--state','open','--json','number,url,isDraft']))
        body=str(ROOT/row['body'])
        if existing:
            pr=existing[0]
            call(['gh','pr','edit',str(pr['number']),'--repo',PLAN['repo'],'--title',row['title'],'--body-file',body])
            if pr['isDraft']:call(['gh','pr','ready',str(pr['number']),'--repo',PLAN['repo']])
            url=pr['url']
        else:
            url=call(['gh','pr','create','--repo',PLAN['repo'],'--head',row['head'],'--base',row['base'],
                      '--title',row['title'],'--body-file',body])
        results['PRs'].append({'head':row['head'],'base':row['base'],'url':url,'draft':False})
    results['status']='published_ready'
except RuntimeError as e:
    results['status']='publication_failed'
    results['error']=str(e)
finally:
    results['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p=ROOT/('publication-result-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'.json')
    with p.open('x')as f:json.dump(results,f,indent=2);f.write('\n')
    print(json.dumps({'status':results['status'],'PRs':results['PRs'],'record':str(p),'error':results.get('error')},indent=2))
if results['status']!='published_ready':raise SystemExit(1)
