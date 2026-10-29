"""Descriptive shifted-cover export; no field-shift scan or scientific collection."""
import argparse
import copy
import gzip
import importlib.util
import json
import os
from pathlib import Path
from common import HERE, ROOT, INPUTS, digest, write_once


def load(path):
    options=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(options)>1:raise ValueError('ambiguous retained encodings')
    if not options:return None
    opener=gzip.open if options[0].suffix=='.gz' else open
    with opener(options[0],'rt') as stream:return json.load(stream)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();execution=load(args.run/'execution.json');host=load(args.run/'host.json')
    protocol=load(args.protocol);survey=load(args.run/'raw/survey.json');verification=load(args.run/'raw/verification.json')
    fixtures=json.loads(INPUTS.read_text())['fixtures'];metrics=[m['id'] for m in protocol['metrics']['primary']]
    if survey is not None and (survey.get('schema')!='prime-field-shifted-cover-survey/v1' or survey.get('complete') is not True or survey.get('inputs_sha256')!=digest(INPUTS)):raise ValueError('wrong survey schema')
    actual={} if survey is None else {c['fixture_uid']:c for c in survey['cells']}
    if survey is not None and (len(actual)!=len(survey['cells']) or set(actual)-{f['uid'] for f in fixtures}):raise ValueError('duplicate/unexpected fixture cells')
    verified={} if verification is None else {c['fixture_uid']:c for c in verification['cells']}
    if verification is not None and (len(verified)!=len(verification['cells']) or set(verified)-{f['uid'] for f in fixtures}):raise ValueError('duplicate/unexpected oracle fixtures')
    oracle_complete=verification is not None and verification.get('checked') is True and verification.get('frames_checked')==8198 and verification.get('source_points_checked')==128
    cells=[]
    for index,f in enumerate(fixtures):
        value=actual.get(f['uid']);check=verified.get(f['uid'])
        cell=dict(fixture_uid=f['uid'],instance_id=str(index),status='unknown',verified=False,**{m:None for m in metrics})
        if value is not None:
            if any(value[k]!=f[k] for k in ('p','a','b','r')) or value['source_order']!=f['width_binding']['source_order'] or value['curve_uid']!=f['ec1']['curve_uid']:
                raise ValueError('retained fixture/curve/source identity differs')
            rows=value['rows']
            if len(rows)!=4099 or [r['h'] for r in rows]!=list(range(4099)):raise ValueError('incomplete shift order')
            eligible=[]
            for row in rows:
                for key,width in [('base_square_mask',16),('base_zero_mask',16),('source_square_mask',64),('source_zero_mask',64)]:
                    if len(row[key])!=width or set(row[key])-{'0','1'}:raise ValueError('invalid membership mask')
                if any(z=='1' and q!='1' for z,q in zip(row['base_zero_mask'],row['base_square_mask'])) or any(z=='1' and q!='1' for z,q in zip(row['source_zero_mask'],row['source_square_mask'])):raise ValueError('zero absent from square mask')
                if row['eligible'] != (not row['singular'] and row['base_square_mask']=='1'*16):raise ValueError('eligibility differs from recorded masks')
                if row['eligible']:eligible.append(row['h'])
            if value['eligible_h']!=eligible:raise ValueError('eligible shift list differs from rows')
            cell.update(status='collected_unverified',frames=len(rows),eligible_frames=len(eligible),nonzero_eligible_frames=sum(h!=0 for h in eligible),singular_frames=sum(r['singular'] for r in rows),public_source_lifts_for_eligible=sum(r['source_square_mask'].count('1') for r in rows if r['eligible']))
            if oracle_complete and check and check.get('checked') is True and check.get('frames_checked')==4099 and check.get('source_points_checked')==64:
                cell.update(verified=True,status='verified')
        elif check is not None:raise ValueError('oracle fixture without survey cell')
        cells.append(cell)
    complete=execution['returncode']==0 and not execution['timeout'] and not execution.get('exception') and execution['source_unchanged_after'] and all(c['verified'] for c in cells)
    analysis=dict(schema='prime-field-cover-retained-analysis/v1',cells=cells,panel_complete=complete,unknown_cells=sum(c['status']=='unknown' for c in cells),physical_executions=1,performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',analysis)
    spec=importlib.util.spec_from_file_location('_cover_protocol_tools',ROOT/'tools/experiment_protocol.py');tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export=tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','cover-survey-'+args.run.name)
    export['producer']=dict(runtime='codex',model=None,session=None,role='executor')
    export['source']=dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={k:host[k] for k in export['host']['summary']})
    export['runs']=[]
    for cell in cells:
        row=tools.run_row(run_id='cover-'+args.run.name+'-'+cell['instance_id'],arm='survey',instance_id=cell['instance_id'],seed=0,replicate=0,warmup=False,status='succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'interrupted',measurements=dict(counted={k:cell[k] for k in metrics if cell[k] is not None},counters={} if actual.get(cell['fixture_uid']) is None else actual[cell['fixture_uid']].get('counters',{}),wall_seconds=None,wall_valid=False,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),isolation=dict(tier=None,contended=None,blockers=['shared host; no isolated performance clock']),verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='Integrated complete roots-set membership and separate public-source arithmetic oracle; not independent scientific review'),started_at=execution['started_at'],finished_at=execution['finished_at'],worker=execution['owner'])
        export['runs'].append(row)
        reference=copy.deepcopy(row);reference.update(run_id=row['run_id']+'-oracle',arm='roots_set_oracle');reference['measurements']['counters']={};export['runs'].append(reference)
    export['backend_record']=dict(physical_executions=1,shared_process_ownership='ownership.json',shared_diagnostic_resources={k:execution[k] for k in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},native_counter_ownership='Each survey fixture row only; reference rows empty. Explicit membership pow calls/setup Curve group calls exclude helper primality guards, coefficient arithmetic, oracle and total work.',wall_valid=False,phase_journal='raw/phases.jsonl',counting_scope='Two fixture survey cells and two integrated reference method cells share one physical process. Duplicate method counts must not be summed. Reference resources/counters empty; setup/membership and whole-process resources occur once here. No collector/rank/complete-S costs.')
    for arm in export['arms']:arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files']=[tools.file_entry(args.run,str(p.relative_to(args.run)),'raw') for p in sorted(args.run.rglob('*')) if p.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size));export['analysis']['outputs']=[tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow']=tools.compute_flow(export['runs']);errors=tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:raise ValueError(json.dumps(errors))
    write_once(args.run/'export.json',export)
    print(json.dumps(dict(panel_complete=complete,unknown_cells=analysis['unknown_cells'])))


if __name__=='__main__':main()
