"""Frozen descriptive B1 export; reads retained records, never collects a branch."""
import argparse
from collections import Counter
import gzip
import importlib.util
import json
import os
from pathlib import Path

from common import HERE, ROOT, INPUTS, PARAMETERS, ATTEMPTS_PER_CELL, digest, write_once


def retained(path):
    """Require unambiguous retained bytes; gzip is lossless archival encoding."""
    candidates = [p for p in (path, Path(str(path)+'.gz')) if p.is_file()]
    if len(candidates) > 1:
        raise ValueError('ambiguous duplicate raw encodings: '+str(path))
    return candidates[0] if candidates else None


def load(path):
    path = retained(path)
    if path is None:
        return None
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt') as stream:
        return json.load(stream)


def lines(path):
    path = retained(path)
    if path is None:
        return
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path,'rt') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def projected_rows(result, modulus):
    """Normalize retained affine rows only; no rank solver or branch construction."""
    projection = result['projection']
    for row in result['rows']:
        vector, rhs = [0]*projection['U'], row['source_scalar']
        for coefficient, mapping in zip(row['coefficients'],projection['native_to_projected']):
            if mapping[0] == 'known':
                rhs -= coefficient*mapping[1]
            elif mapping[0] == 'unknown':
                vector[mapping[1]] += coefficient*mapping[2]
        yield [v % modulus for v in vector], rhs % modulus


def equation_set(result, modulus):
    equations = set()
    for vector, rhs in projected_rows(result, modulus):
        augmented = vector+[rhs]
        first = next((v for v in augmented if v),None)
        equations.add(tuple(v*pow(first,-1,modulus) % modulus for v in augmented) if first else tuple(augmented))
    return equations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--protocol',type=Path,required=True)
    args = parser.parse_args()
    execution = load(args.run/'execution.json')
    host = load(args.run/'host.json')
    protocol = load(args.protocol)
    fixtures = json.loads(INPUTS.read_text())['fixtures']
    metrics = [m['id'] for m in protocol['metrics']['primary']]
    phases = list(lines(args.run/'raw/phases.jsonl'))
    cells, values, equations = [], {}, {}
    for index, fixture in enumerate(fixtures):
        for arm in PARAMETERS['arms']:
            stem = fixture['uid']+'-'+arm
            value = load(args.run/'raw'/(stem+'.json'))
            verification = load(args.run/'raw'/(stem+'.verification.json'))
            cell = dict(curve_uid=fixture['uid'],instance_id=str(index),arm=arm,status='unknown',
                        verified=False,**{key:None for key in metrics},collection_counters=None,
                        branch_sha256=None,phase_records=[p for p in phases if p.get('curve_uid') == fixture['uid'] and p.get('arm') == arm])
            events = list(lines(args.run/'raw'/(stem+'.events.jsonl')))
            cell['collection_attempts_lower_bound'] = max([0]+[e.get('attempts',e.get('attempt',0)) for e in events])
            if value is not None:
                if (value.get('curve_uid') != fixture['uid'] or value.get('source_order') != fixture['width_binding']['source_order'] or
                        value.get('include_zero') is not (arm == 'completed_zero') or value.get('complete') is not True or
                        value.get('attempts') != ATTEMPTS_PER_CELL or value.get('inputs_sha256') != digest(INPUTS)):
                    raise ValueError('wrong complete collected cell identity: '+stem)
                values[(index,arm)] = value
                eq = equation_set(value,fixture['r'])
                equations[(index,arm)] = eq
                if len(eq) != value['quality']['unique_affine_equations']:
                    raise ValueError('retained affine equation count differs: '+stem)
                q = value['quality']
                cell.update(status='collected_unverified',collection_attempts=value['attempts'],rank=q['rank'],nullity=q['nullity'],
                            unique_equations=q['unique_affine_equations'],witnesses=len(value['rows']),
                            collection_counters=value['operation_vector'],branch_sha256=value['branch_sha256'])
                if verification is not None:
                    if (verification.get('checked') is not True or verification.get('attempts_replayed') != value['attempts'] or
                            verification.get('source_statuses_checked') is not True or
                            any(verification.get(key) != q[key] for key in ('rank','nullity','rows','columns','unique_affine_equations'))):
                        raise ValueError('separate verification mismatch: '+stem)
                    cell.update(status='verified',verified=True,verification_attempts=verification['attempts_replayed'])
                accepted = [event for event in events if event.get('kind') == 'accepted']
                sources = [event for event in events if event.get('kind') == 'source_complete']
                # Events are retained separately from checked result status blocks.
                # Missing/partial journals do not become zero-witness assertions.
                if len(accepted) == len(value['rows']) and len(sources) == 64:
                    if [event['row'] for event in accepted] != value['rows']:
                        raise ValueError('accepted journal rows differ: '+stem)
                    expected_blocks = [dict(scalar=e['scalar'],attempts=e['attempts'],statuses=e['statuses'],branch_sha256=e['branch_sha256']) for e in sources]
                    if expected_blocks != value['status_blocks']:
                        raise ValueError('source-complete journal differs from checked blocks: '+stem)
                    if any(e['source_zero'] != (e['row']['constraints'][0][0] == 0) or
                           e['constraint_zero'] != any(x == 0 for x,y in e['row']['constraints'][1:])
                           for e in accepted):
                        raise ValueError('zero flags differ from retained witness geometry: '+stem)
                    cell.update(source_zero_witnesses=sum(event['source_zero'] for event in accepted),
                                constraint_zero_witnesses=sum(event['constraint_zero'] for event in accepted))
                if arm == 'completed_zero':
                    syndromes = value.get('old_kernel_syndromes')
                    if syndromes is not None:
                        if len(syndromes) != len(value['rows']):
                            raise ValueError('old-kernel syndrome row coverage differs')
                        cell['nonzero_old_kernel_syndromes'] = sum(any(x % fixture['r'] for x in row) for row in syndromes)
                        cell['distinct_nonzero_old_kernel_syndromes'] = len({tuple(row) for row in syndromes if any(x % fixture['r'] for x in row)})
            elif verification is not None:
                raise ValueError('orphan verification without collected data: '+stem)
            cells.append(cell)
        old, new = (values.get((index,arm)) for arm in PARAMETERS['arms'])
        if old is not None and new is not None:
            if old['projection'] != new['projection'] or not equations[(index,'historical_nonzero')] <= equations[(index,'completed_zero')]:
                raise ValueError('paired projection or historical-equation inclusion differs')
            expected_syndromes = [[sum(a*b for a,b in zip(vector,kernel)) % fixture['r'] for kernel in old['kernel']]
                                  for vector,rhs in projected_rows(new,fixture['r'])]
            if new.get('old_kernel_syndromes') != expected_syndromes:
                raise ValueError('old-kernel syndromes differ from retained row/kernel products')
            cell = cells[-1]
            cell.update(new_distinct_equations=len(equations[(index,'completed_zero')]-equations[(index,'historical_nonzero')]),
                        span_rank_gain=new['quality']['rank']-old['quality']['rank'])
    complete = (execution['returncode'] == 0 and execution['source_unchanged_after'] and
                not execution['timeout'] and not execution.get('exception') and all(c['verified'] for c in cells))
    result = dict(schema='b1-retained-analysis/v1',cells=cells,panel_complete=complete,
                  unknown_cells=sum(c['status'] == 'unknown' for c in cells),
                  collection_attempts_observed=sum(c['collection_attempts'] or 0 for c in cells),
                  collection_attempts_observed_scope='Exact completed-cell attempts only; partial cells retain journal lower bounds, not zero attempts.',
                  collection_attempts_lower_bound=sum(max(c['collection_attempts'] or 0,c['collection_attempts_lower_bound']) for c in cells),
                  verification_attempts_observed=sum(c['verification_attempts'] or 0 for c in cells),
                  counters_scope='Collection-only field/group counts; replay and affine/kernel/elimination/serialization/storage costs absent. Not complete S.',
                  verification_scope='Separate arithmetic implementation replay, not independent scientific review; field counters not independently checked.',
                  timed_primary=False,performance_claim=False,scientific_promotion=False)
    write_once(args.run/'analysis.json',result)
    spec = importlib.util.spec_from_file_location('_b1_protocol_tools',ROOT/'tools/experiment_protocol.py')
    tools = importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)
    export = tools.export_skeleton(protocol,str(args.protocol.resolve()),'local','B1-fixed-panel-'+args.run.name)
    export['producer'] = dict(runtime='codex',model=None,session=None,role='executor')
    export['source'] = dict(repo='crypto-autoresearcher',commit=execution['observed_git_head'],dirty=host['git_dirty'])
    export['host'].update(path='host.json',sha256=digest(args.run/'host.json'),summary={key:host[key] for key in export['host']['summary']})
    export['runs'] = []
    for cell in cells:
        # Whole-process resources live only at backend_record. These phase clocks
        # are separately retained diagnostics and never added to shared costs.
        collected = [p for p in cell['phase_records'] if p.get('phase') == 'collection']
        phase = collected[-1] if collected else None
        status = 'succeeded' if cell['verified'] else 'timeout' if execution['timeout'] else 'failed' if any(p.get('status') == 'failed' for p in cell['phase_records']) else 'interrupted'
        export['runs'].append(tools.run_row(run_id='B1-'+args.run.name+'-'+cell['instance_id']+'-'+cell['arm'],
            arm=cell['arm'],instance_id=cell['instance_id'],seed=0,replicate=0,warmup=False,status=status,
            measurements=dict(counted={key:cell[key] for key in metrics if cell[key] is not None},
                counters=cell['collection_counters'] or {},wall_seconds=None,wall_valid=False,
                cpu_user_seconds=None,cpu_sys_seconds=None,max_rss_bytes=None),
            isolation=dict(tier=None,contended=None,blockers=['shared managed host; no isolation certified']),
            verification=dict(status='verified' if cell['verified'] else 'not_run',verifier='Separate complete arithmetic replay of rows/statuses/digests/projection/rank/kernel; excludes field-counter validation and scientific review'),
            started_at=phase['started_at'] if phase else execution['started_at'],
            finished_at=phase['finished_at'] if phase else execution['finished_at'],worker=execution['owner']))
    export['backend_record'] = dict(physical_executions=1,shared_process_ownership='ownership.json',
        shared_diagnostic_resources={key:execution[key] for key in ('diagnostic_wall_seconds','cpu_user_seconds','cpu_sys_seconds','max_rss_bytes')},
        phase_journal='raw/phases.jsonl'+('.gz' if (args.run/'raw/phases.jsonl.gz').is_file() else ''),
        phase_records=phases,wall_valid=False,
        counting_scope='Four disjoint fixture/arm cells share one process. Collection/replay phase clocks are components of shared process cost, not extra executions. Collection counters exclude replay and are incomplete total cost.')
    for arm in export['arms']:
        arm.update(binary_sha256=host['executable_sha256'],commit=execution['source_commit'])
    export['files'] = [tools.file_entry(args.run,str(path.relative_to(args.run)),'raw') for path in sorted(args.run.rglob('*')) if path.is_file()]
    export['analysis'].update(script=dict(path=os.path.relpath(HERE/'analyze.py',args.run.resolve()),sha256=digest(HERE/'analyze.py'),bytes=(HERE/'analyze.py').stat().st_size))
    export['analysis']['outputs'] = [tools.file_entry(args.run,'analysis.json','analysis')]
    export['flow'] = tools.compute_flow(export['runs'])
    errors = tools.schema_errors(export,'experiment.export/v1') or tools.lint_export(export,protocol,args.run,True)
    if errors:
        raise ValueError('export validation failed: '+json.dumps(errors))
    write_once(args.run/'export.json',export)
    print(json.dumps(dict(panel_complete=complete,unknown_cells=result['unknown_cells'],export=str(args.run/'export.json'))))


if __name__ == '__main__':
    main()
