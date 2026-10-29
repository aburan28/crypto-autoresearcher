#!/usr/bin/env python3
"""Descriptive failure export using the unchanged frozen numerical extraction."""
import argparse
import json
import os
from pathlib import Path
import export_results as frozen

ep, store = frozen.ep, frozen.artifact_store
ROOT = frozen.ROOT


def build(raw_path, protocol_path, supplemental, out):
    base = out.parent
    base.mkdir(parents=True, exist_ok=True)
    raw = store.read_json(raw_path)
    p = ep.read_json(protocol_path)
    receipt = store.read_json(raw_path.parent / 'execution-receipt.json')
    env = store.read_json(raw_path.parent / 'environment.json')
    launch = store.read_json(raw_path.parent / 'launch.json')
    if receipt['status'] != 'invalid_output' or receipt['returncode'] != 0:
        raise ValueError('expected retained failed native validation')
    for name, digest in receipt['artifact_sha256'].items():
        if store.content_digest(raw_path.parent / name) != digest:
            raise ValueError('changed raw artifact ' + name)
    for name, digest in p['extensions']['source_sha256'].items():
        if env['source_sha256'].get(name) != digest or ep.sha256_file(ROOT/name) != digest:
            raise ValueError('changed frozen source ' + name)
    payloads = {name: store.read_json(raw_path.parent/(name+'.json')) for name in ('encoding','coefficients')}
    sets, counts = frozen.extraction(payloads)
    e = ep.export_skeleton(p, os.path.relpath(protocol_path,base), 'local', p['protocol_id']+'-failure-export')
    e['producer'] = {'runtime':'native_codex','model':None,'session':'prime-sat-followup-20261029','role':'executor'}
    e['source'] = {'repo':p['repository'],'commit':env['commit'],'dirty':None}
    e['arms'] = [{'id':a['id'],'role':a['role'],'binary_sha256':a['instrument']['binary_sha256'],'commit':a['instrument']['commit']} for a in p['arms']]
    ref = lambda path, kind='raw': frozen.ref(path,base,kind)
    host = ref(raw_path.parent/'environment.json')
    e['host']['path'], e['host']['sha256'] = host['path'],host['sha256']
    files = {n:ref(raw_path.parent/(n+'.json')) for n in payloads}
    for a in p['arms']:
        name = a['id']; package,_ = sets[name]; counts[name]['verification_pass'] = 0
        e['runs'].append(ep.run_row(run_id=raw_path.parent.name+'-'+name, arm=name,
            instance_id='0', seed=17, replicate=0, status='failed',
            measurements={'counted':counts[name],'wall_valid':False},
            verification={'status':'error','verifier':'Frozen native checker: explicit-zero census counter mismatch; supplemental replay kept separate'},
            exclusion={'excluded':True,'rule':'invalid native verification: checker mismatch; retained data remain visible'},
            artifacts=list(files.values()) if package=='both' else [files[package]],
            started_at=launch['started_at'],finished_at=receipt['finished_at'],
            backend_ref=raw_path.parent.name,isolation={'tier':'none','contended':None,'blockers':['No timing comparison; native checker failed.']}))
    e['flow'] = ep.compute_flow(e['runs'])
    e['files'] = list(files.values())
    for name in ('raw-result.json','manifest.yaml','launch.json','environment.json','execution-receipt.json','check.stdout.log','check.stderr.log','encoding-cells.jsonl','coefficient-cells.jsonl'):
        e['files'].append(ref(raw_path.parent/name))
    for path in (protocol_path,supplemental,Path(__file__).resolve(),Path(__file__).with_name('supplemental_check.py'),ROOT/'problems/prime-next-zero-counter-verifier.md'):
        e['files'].append(ref(path,'other'))
    # This is the exact frozen numerical extraction function. The post-data
    # failure adapter is identified above, not misrepresented as preregistered.
    e['analysis']['script'] = ref(Path(frozen.__file__).resolve(),'analysis')
    e['notes'] = [{'kind':'observation','by':'executor-failure-adapter','text':x} for x in (
        'Native trial invalid_output. All10 aggregate rows failed, excluded, verification_pass=0. No native success or hypothesis promotion.',
        'Numerical counters extracted by unchanged frozen export_results.extraction. This new failure adapter is post-data descriptive handling; original validated-output exporter correctly refuses this run.',
        'Supplemental zero-counter replay is a separate post-data exploratory observation, not original-protocol verification. Its receipt does not flip rows or native status.',
        'All106 encoding and6coefficient subcells remain represented. Complete and censored producer searches are distinct from native validation and exact model equivalence.',
        'Phase and primitive counter units are not pooled. Shared reference counters repeat beside arms and must not be summed across arms. No timing, regularity, held-out generalization or ECDLP recovery claim.')]
    errors = ep.schema_errors(e,'experiment.export/v1') or ep.lint_export(e,p,base,True)
    if errors:
        raise ValueError('\n'.join(errors))
    ep.write_once(out,e)
    print(json.dumps({'export':str(out),'flow':e['flow'],'native_status':'invalid_output'}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('raw','protocol','supplemental','out'):
        parser.add_argument('--'+arg,required=True,type=Path)
    args=parser.parse_args()
    build(*(getattr(args,k).resolve() for k in ('raw','protocol','supplemental','out')))
