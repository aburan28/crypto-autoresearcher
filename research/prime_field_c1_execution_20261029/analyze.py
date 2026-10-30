"""Prospective descriptive export of retained C1 files; never solves a case."""
import argparse
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path

from common import HERE, ROOT, INPUTS, digest, write_once


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--protocol', type=Path, required=True)
    args = p.parse_args()
    execution = json.loads((args.run/'execution.json').read_text())
    protocol = json.loads(args.protocol.read_text())
    host = json.loads((args.run/'host.json').read_text())
    inputs = json.loads(INPUTS.read_text())
    rows = []
    counters = Counter()
    for case in inputs['cases']:
        path = args.run/'raw'/(case['id']+'.json')
        value = json.loads(path.read_text()) if path.is_file() else None
        if value is not None and value.get('case_id') != case['id']:
            raise ValueError('retained case identity differs')
        row = dict(case_id=case['id'], kind=case['kind'], status='not_completed' if value is None else value['status'],
                   symmetric_states=None, signed_solutions=None, oracle_checked=False)
        if value and case['kind'] == 'triple' and value['status'] == 'complete':
            row.update(symmetric_states=sum(len(s['states']) for s in value['strata']),
                       signed_solutions=len(value['solutions']), oracle_checked=value['finite_reference']['checked'])
            if not row['oracle_checked']:
                raise ValueError('completed triple lacks finite oracle check')
            for stratum in value['strata']:
                for prefix, key in [('tensor', 'counters'), ('recovery', 'recovery_counters')]:
                    counters.update({stratum['stratum']+'.'+prefix+'.'+k: v for k,v in stratum[key].items()})
        rows.append(row)
    metrics = dict(cases_completed=sum(r['status'] in ('complete', 'control_passed') for r in rows),
                   complete_triple_cases=sum(r['kind'] == 'triple' and r['status'] == 'complete' for r in rows),
                   symmetric_states=sum(r['symmetric_states'] or 0 for r in rows),
                   signed_solutions=sum(r['signed_solutions'] or 0 for r in rows),
                   controls_passed=sum(r['kind'] != 'triple' and r['status'] in ('complete', 'control_passed') for r in rows),
                   unknown_cases=sum(r['status'] in ('unknown', 'not_completed') for r in rows))
    complete = execution['returncode'] == 0 and execution['source_unchanged_after'] and metrics['cases_completed'] == 7
    result = dict(schema='c1-retained-analysis/v1', cases=rows, metrics=metrics,
                  native_counters=dict(counters), panel_complete=complete,
                  timed_primary=False, performance_claim=False, scientific_promotion=False)
    write_once(args.run/'analysis.json', result)
    spec = importlib.util.spec_from_file_location('_c1_protocol_tools', ROOT/'tools/experiment_protocol.py')
    tools = importlib.util.module_from_spec(spec); spec.loader.exec_module(tools)
    export = tools.export_skeleton(protocol, str(args.protocol.resolve()), 'local', 'C1-fixed-panel-'+args.run.name)
    export['producer'] = dict(runtime='codex', model=None, session=None, role='executor')
    export['source'] = dict(repo='crypto-autoresearcher', commit=execution['observed_git_head'], dirty=host['git_dirty'])
    export['host'].update(path='host.json', sha256=digest(args.run/'host.json'), summary={k:host[k] for k in export['host']['summary']})
    status = 'succeeded' if complete else 'timeout' if execution['timeout'] else 'failed'
    export['runs'] = [tools.run_row(run_id='C1-'+args.run.name, arm='extractor', instance_id='0',
        seed=2026102601, replicate=0, warmup=False, status=status,
        measurements=dict(counted=metrics, counters=dict(counters), wall_seconds=execution['diagnostic_wall_seconds'],
                          wall_valid=False, cpu_user_seconds=execution['cpu_user_seconds'],
                          cpu_sys_seconds=execution['cpu_sys_seconds'], max_rss_bytes=execution['max_rss_bytes']),
        isolation=dict(tier=None, contended=None, blockers=['shared managed host; no isolation certified']),
        verification=dict(status='verified' if complete else 'not_run', verifier='F1 separate finite resultant/point oracle and embedded controls'),
        started_at=execution['started_at'], finished_at=execution['finished_at'], worker=execution['owner'])]
    import copy
    reference = copy.deepcopy(export['runs'][0])
    reference.update(run_id='C1-reference-'+args.run.name,arm='finite_reference')
    reference['measurements'].update(counters={},wall_seconds=None,cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None)
    export['runs'].append(reference)
    export['backend_record'] = dict(physical_executions=1,shared_process_ownership='ownership.json',
        shared_cost_record=export['runs'][0]['run_id'],reference_cost_record=None,
        counting_scope='Two exact-method cells share one physical panel. Do not sum their object counts or treat them as independent process replicates.')
    for arm in export['arms']:
        arm.update(binary_sha256=host['executable_sha256'], commit=execution['source_commit'])
    export['files'] = [tools.file_entry(args.run, str(path.relative_to(args.run)), 'raw')
                       for path in sorted(args.run.rglob('*')) if path.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py', args.run.resolve()),
                                          sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size))
    export['analysis']['outputs'] = [tools.file_entry(args.run, 'analysis.json', 'analysis')]
    export['flow'] = tools.compute_flow(export['runs'])
    errors = tools.schema_errors(export, 'experiment.export/v1') or tools.lint_export(export, protocol, args.run, True)
    if errors:
        raise ValueError('export validation failed: '+json.dumps(errors))
    write_once(args.run/'export.json', export)
    print(json.dumps(dict(metrics=metrics, panel_complete=complete, export=str(args.run/'export.json'))))


if __name__ == '__main__':
    main()
