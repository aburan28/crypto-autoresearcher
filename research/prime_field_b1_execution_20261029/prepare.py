"""Bind/freeze B1 before data; root authorization is an explicit later command."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from common import HERE, ROOT, NATIVE, INPUTS, PARAMETERS, bindings, digest, git, write_once


def protocol_tools():
    spec = importlib.util.spec_from_file_location('_b1_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRYM-B1-ZERO-COMPLETION-20261029',
     'version': 1,
     'created': '2026-10-29',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_b1_execution_20261029',
     'authors': ['B1 execution-contract coordinator subagent; inherited model identity unverified'],
     'links': {'literature': 'literature.md', 'prior_work': '../prym_factor_base_width_20261025/README.md'},
     'question': 'On the exact two retained p4099 curves, sixteen-atom bases and sixty-four-source orders, what '
                 'distinct equations and old-kernel syndromes are added by permitting affine x=0 sources and '
                 'constraints under the unchanged cubic law?',
     'claims': [{'id': 'B1-fixed-panel',
                 'text': 'A complete cell describes the exact fixed source/triple/options stream and passes a '
                         'separate arithmetic replay of rows, branch statuses/digests, rank and kernel. No rank '
                         'gain or speed advantage is presumed.',
                 'class': 'exact_computation',
                 'decided_by': ['C-zero']}],
     'arms': [{'id': 'historical_nonzero',
               'role': 'reference',
               'description': 'Historical source/constraint zero exclusions retained.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON',
                                         '-B',
                                         'research/prime_field_factor_base_20261028/run_prym.py']],
                              'binary_sha256': 'BINARY',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'arms': ['historical_nonzero', 'completed_zero'],
                              'factor_base_size': 16,
                              'source_count': 64,
                              'attempts_per_cell': 2293760}},
              {'id': 'completed_zero',
               'role': 'candidate',
               'description': 'Only legitimate affine x=0 source/constraint exclusions are removed; infinity and '
                              'repeated coordinates remain rejected.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON',
                                         '-B',
                                         'research/prime_field_factor_base_20261028/run_prym.py']],
                              'binary_sha256': 'BINARY',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'arms': ['historical_nonzero', 'completed_zero'],
                              'factor_base_size': 16,
                              'source_count': 64,
                              'attempts_per_cell': 2293760}}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Exact deterministic paired enumeration; no noisy comparative '
                                                  'metric.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No guaranteed accepted witness in these fixed '
                                                        'scientific fixtures. Existing separate marked-small '
                                                        'software controls exercise accepted rows; independent '
                                                        'complete replay verifies any actual accepted rows.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Historical_nonzero is the matched unchanged reference. '
                                                        'Separate software corruption controls test '
                                                        'row/status/rank rejection; native cells have no '
                                                        'presumed zero outcome.'}},
     'variable_ledger': {'independent': [{'name': 'zero_policy',
                                          'levels': ['historical_nonzero', 'completed_zero']},
                                         {'name': 'curve_uid', 'levels': []}],
                         'factors': [{'name': 'curve_base_sources_cubic_law',
                                      'treatment': 'fixed',
                                      'value': 'Exact retained fixtures and source bytes',
                                      'how': 'Committed source/input locks; two curves, sixteen atoms, '
                                             'sixty-four sources; original source order and lexicographic '
                                             'descriptors.'},
                                     {'name': 'threads',
                                      'treatment': 'fixed',
                                      'value': 1,
                                      'how': 'One compute process, OMP/OpenBLAS1.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'Shared managed host; diagnostic phase and whole-process clocks, '
                                             'wall_valid=false.'},
                                     {'name': 'cell_order',
                                      'treatment': 'fixed',
                                      'value': 'fixture order, historical then completed',
                                      'how': 'No success/rank stop or replacement.'}],
                         'comparisons': [{'id': 'C-zero',
                                          'arms': ['historical_nonzero', 'completed_zero'],
                                          'differs_in': ['zero_policy'],
                                          'design': 'one_factor',
                                          'threshold': 'Descriptive exact equation-set difference, old-kernel '
                                                       'action and span-rank difference; no expected gain '
                                                       'required.'}],
                         'aa_not_applicable': 'Exact fixed-stream enumeration, no noisy metric.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Same fixed panel and original source ordering. Historical followed '
                                           'by completed arm per fixture within one process; no isolated '
                                           'comparative clock.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'The original two fixtures, each with its own unchanged '
                                                     'materialized sixty-four-source order.',
                                             'independent_of_arm': True},
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Public known curve and arm labels; exact descriptive observation.',
                                    'unmasked_at': None}},
     'sample_size': {'instances': 2,
                     'replicates': 1,
                     'warmups': 0,
                     'power': {'method': 'exact',
                               'alpha': 0.05,
                               'tests_in_family': 1,
                               'correction': 'none',
                               'rank_test_n': None,
                               'min_attainable_two_sided_p': None,
                               'passes': True,
                               'note': 'Complete finite enumeration within each completed cell; no '
                                       'population-power inference.'},
                     'preflight_runtime': {'fixed_seconds': None,
                                           'per_sample_seconds': None,
                                           'threads': 1,
                                           'estimated_total_seconds': 21600,
                                           'measured_on': 'No affected scientific execution.21600 seconds '
                                                          'denotes the protective machine watchdog, not measured '
                                                          'runtime or spending cap; required engineering-field '
                                                          'placeholder.'}},
     'metrics': {'primary': [{'id': 'collection_attempts',
                              'name': 'collection attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Completed collection descriptors; original full cell2293760.',
                              'source': 'analysis.json cells[].collection_attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'verification_attempts',
                              'name': 'verification attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Separately charged independently replayed descriptors, never added '
                                            'to collection counters.',
                              'source': 'analysis.json cells[].verification_attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'rank',
                              'name': 'rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Exact projected base matrix rank.',
                              'source': 'analysis.json cells[].rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nullity',
                              'name': 'nullity',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Projected column count minus rank.',
                              'source': 'analysis.json cells[].nullity',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'unique_equations',
                              'name': 'unique equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct nonzero-normalized augmented affine equations.',
                              'source': 'analysis.json cells[].unique_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'witnesses',
                              'name': 'witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted canonical witness rows.',
                              'source': 'analysis.json cells[].witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'source_zero_witnesses',
                              'name': 'source zero witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted events with affine source x=0.',
                              'source': 'analysis.json cells[].source_zero_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'constraint_zero_witnesses',
                              'name': 'constraint zero witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted events with an interpolation constraint x=0.',
                              'source': 'analysis.json cells[].constraint_zero_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'new_distinct_equations',
                              'name': 'new distinct equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Completed-arm affine equations absent from same-fixture historical '
                                            'arm.',
                              'source': 'analysis.json cells[].new_distinct_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nonzero_old_kernel_syndromes',
                              'name': 'nonzero old kernel syndromes',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Completed witness rows with nonzero action on the old kernel.',
                              'source': 'analysis.json cells[].nonzero_old_kernel_syndromes',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'span_rank_gain',
                              'name': 'span rank gain',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Completed rank minus historical rank, after equation inclusion '
                                            'check.',
                              'source': 'analysis.json cells[].span_rank_gain',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'}],
                 'secondary': []},
     'measurement': {'isolation_required': 'none',
                     'warmups': 0,
                     'order': 'sequential',
                     'clock': 'counted',
                     'counters': ['operation_vector.*'],
                     'record': ['cpu_model',
                                'logical_cpus',
                                'memory_bytes',
                                'kernel',
                                'executable_sha256',
                                'source_commit',
                                'observed_git_head',
                                'git_dirty',
                                'source_unchanged_after',
                                'diagnostic_wall_cpu_rss',
                                'raw result/events/status blocks/verification/phase journal hashes'],
                     'timed_primary_justification': None},
     'execution': {'backend': 'local',
                   'queue': None,
                   'measurement_class': 'search',
                   'timeout_seconds': 21600,
                   'placement': {'shared_managed_host': True,
                                 'memory_bytes': 2147483648,
                                 'concurrent_compute_processes': 1,
                                 'isolated_clock_claim': False},
                   'checkpoint': {'policy': 'none',
                                  'interval_seconds': None,
                                  'grace_seconds': None,
                                  'restore_validation': 'none',
                                  'after_restore': {'wall_time': 'invalid', 'counted_units': 'valid'}},
                   'retries': {'infrastructure_only': True, 'max_attempts': 1}},
     'stopping_rules': [{'rule': 'Exactly2fixtures x2arms x64sources x C(16,3) x64options =9175040 collection '
                                 'attempts; independent replay charges the same full attempts separately. No '
                                 'rank/success stop or sample replacement.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Source change, replay mismatch or wrong identity invalidates affected '
                                 'completeness; retain raw collected data and failed prefixes.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiB memory and21600s wall/CPU watchdog protect the machine. A stop remains '
                                 'unknown, never a zero yield.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Source/input change, identity mismatch or failed independent replay prevents '
                            'verified-cell observation.',
                            'Missing cells remain unknown; collected but unverified cells remain explicitly '
                            'unverified.',
                            'Clocks and collection-only field/group counters are not complete S, isolated '
                            'timings or performance evidence.'],
     'decision_rule': {'text': 'Describe per-curve/arm rank, nullity, equation and witness counts, '
                               'zero-source/constraint witnesses, new equations and old-kernel action. No '
                               'official scientific transition or performance claim.',
                       'comparison_ids': ['C-zero'],
                       'threshold': 'Complete fixed stream and separate exact arithmetic replay for each '
                                    'verified cell.',
                       'statistic': 'Exact retained object counts and set differences.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'Descriptive paired differences only; no effect claim',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py', 'sha256': 'ANALYSIS'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-curve/arm exact rank, equation/zero-witness counts and old-kernel action; '
                              'incomplete cells separated.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Executing before exact committed source, frozen protocol, actual canonical S3 gate and '
                      'explicit root release.',
                      'Source/base/order/cubic-law changes between paired cells.',
                      'Interpreting unknown as empty or silently discarding collected data after replay failure.',
                      'Adding whole-process resources to per-phase diagnostics or treating shared resources as '
                      'four independent process executions.',
                      'Complete S, ECDLP/attack advantage, independent scientific review or official status '
                      'claims.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Relation solver and linear algebra costs remain distinct; collection field '
                              'counters are incomplete total cost.',
                     'verified_by': '/root/c1_execution_contract,2026-10-29; retained primary page8 reread.'},
                    {'ref': 'research/prym_factor_base_width_20261025/README.md; '
                            'research/prym_experiment_design_20261019/implementation/census.py; '
                            'research/prime_field_factor_base_20261028/prym_completion.py',
                     'provenance': 'internal',
                     'claim': 'Historical affine zero exclusions and isolated completion; exact '
                              'base/source/cubic-law retained.',
                     'verified_by': '/root/c1_execution_contract,2026-10-29'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Four arm/fixture cells share one physical process. Whole-process resources '
                                   'are recorded only at backend_record; per-phase clocks are nonoverlapping '
                                   'collection/replay diagnostics with wall_valid=false.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Collection-only field/group operation_vector excludes replay, integer '
                                        'normalization, branch/status serialization, storage, kernel/affine '
                                        'elimination and complete S.',
                    'verification_scope': 'Separate arithmetic replay checks exact rows, statuses/digests, '
                                          'projection/rank/kernel; it does not independently check field '
                                          'counters or constitute independent scientific review.',
                    'official_status_transition': False}}
    fixtures = json.loads(INPUTS.read_text())['fixtures']
    if len(fixtures) != 2 or any(len(f['factor_base']) != 16 or len(f['width_binding']['source_order']) != 64 for f in fixtures):
        raise ValueError('exact retained two-fixture sixteen-atom sixty-four-source panel required')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit, binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build'][0][0] = sys.executable
        arm['parameters']['inputs_sha256'] = digest(INPUTS)
    protocol['variable_ledger']['independent'][1]['levels'] = [f['uid'] for f in fixtures]
    protocol['analysis_plan']['script']['sha256'] = digest(HERE/'analyze.py')
    return protocol


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action',required=True)
    proto = sub.add_parser('protocol')
    proto.add_argument('--source-commit',required=True)
    proto.add_argument('--out',type=Path,required=True)
    proto.add_argument('--freeze',action='store_true')
    proto.add_argument('--draft-preview',action='store_true')
    release = sub.add_parser('release')
    release.add_argument('--source-commit',required=True)
    release.add_argument('--protocol',type=Path,required=True)
    release.add_argument('--out',type=Path,required=True)
    release.add_argument('--owner',required=True)
    release.add_argument('--authorize-root',action='store_true',required=True)
    args = p.parse_args()
    tools = protocol_tools()
    if args.action == 'protocol':
        if args.freeze and args.draft_preview:
            raise ValueError('a draft preview cannot be frozen')
        if args.out.resolve().parent != HERE:
            raise ValueError('protocol belongs beside its pinned analysis source')
        if not args.draft_preview:
            bindings(args.source_commit)
        value = make_protocol(args.source_commit)
        errors = tools.schema_errors(value,'experiment.protocol/v1') or tools.lint_protocol(value,HERE)
        if errors:
            raise ValueError(json.dumps(errors))
        write_once(args.out,value)
        if args.freeze:
            tools.freeze(args.out,args.source_commit,True)
        print(json.dumps(dict(protocol=str(args.out),frozen=args.freeze)))
    else:
        source,input_map = bindings(args.source_commit)
        protocol = json.loads(args.protocol.read_text())
        if protocol['freeze']['status'] != 'frozen' or protocol['freeze']['filed_before_affected_data'] is not True:
            raise ValueError('prospectively frozen protocol required')
        if protocol['freeze']['commit'] != args.source_commit or any(
                arm['instrument']['commit'] != args.source_commit for arm in protocol['arms']):
            raise ValueError('release source commit differs from frozen protocol instruments')
        errors = tools.schema_errors(protocol,'experiment.protocol/v1') or tools.lint_protocol(protocol,args.protocol.parent)
        if errors:
            raise ValueError(json.dumps(errors))
        relative = str(args.protocol.resolve().relative_to(ROOT))
        if subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT) != args.protocol.read_bytes():
            raise ValueError('protocol must already be committed unchanged')
        check = subprocess.run(['bash','scripts/checkpoint.sh','status'],cwd=ROOT,capture_output=True,text=True,check=True)
        if 'last push : current (' not in check.stdout:
            raise ValueError('a prior actual canonical checkpoint of the current state is required')
        checkpoint = (ROOT/'.resume/.last-push').read_text().strip()
        if not re.fullmatch(r'[0-9a-f]{64} \S+ s3://setec-astronomy-artifacts/checkpoints/\S+/',checkpoint):
            raise ValueError('canonical checkpoint receipt has unexpected shape')
        value = dict(schema='prime-field-b1-root-release/v1',execution_authorized=True,
            authority='Explicit root Phase B release under standing user authorization; no research-state promotion.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=input_map,
            interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],
            checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=21600,
            package_versions={name:importlib.metadata.version(name) for name in ['python-flint','sympy','jsonschema','PyYAML']},
            issued_utc=datetime.now(timezone.utc).isoformat(),model_verified=False,model_identity=None)
        write_once(args.out,value)
        print(json.dumps(dict(release=str(args.out),owner=args.owner,execution_authorized=True)))


if __name__ == '__main__':
    main()
