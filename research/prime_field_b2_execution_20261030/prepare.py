"""Bind/freeze B2 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_b2_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRYM-B2-MATCHED-SUBSETS-20261030',
     'version': 1,
     'created': '2026-10-30',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_b2_execution_20261030',
     'authors': ['B2 execution-contract coordinator; inherited model identity unverified'],
     'links': {'literature': 'literature.md',
               'candidate_selection': '../prime_field_cover_survey_20261029/RESULTS.md'},
     'question': 'For every one of the five membership-selected common-atom subsets, how do h0 and its shifted '
                 'cover act on the same pre-existing full-base affine kernel, with identical active '
                 'constraints/residual acceptance, public sources and complete-zero policy?',
     'claims': [{'id': 'B2-fixed-stream',
                 'text': 'Complete fixed subset/cover streams are replayed independently; new affine information '
                         'is measured against existing preprocessing rows on unchanged original columns. No rank '
                         'gain, cost rate or advantage is presumed.',
                 'class': 'exact_computation',
                 'decided_by': ['C-shift']}],
     'arms': [{'id': 'baseline',
               'role': 'reference',
               'description': 'Completed-zero h0 collector restricted to the same active subset for constraints '
                              'and residual acceptance.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_b2_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}},
              {'id': 'shifted',
               'role': 'candidate',
               'description': 'Completed-zero selected shifted cover on exactly the same active subset; all five '
                              'membership ties retained.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_b2_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Exact deterministic paired enumeration; no noisy comparative '
                                                  'metric.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No guaranteed witness in any fixed subset cell; '
                                                        'independent complete replay checks every observed '
                                                        'witness. Separate small software controls validate '
                                                        'producer/checker paths.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Baseline h0 is matched by active subset, original '
                                                        'columns, preprocessing and sources; no presumed zero '
                                                        'yield. Separate software corruptions test rejection.'}},
     'variable_ledger': {'independent': [{'name': 'cover_shift', 'levels': ['baseline', 'shifted']},
                                         {'name': 'candidate_cell', 'levels': []}],
                         'factors': [{'name': 'original_curve_base_columns_sources_preprocessing',
                                      'treatment': 'fixed',
                                      'value': 'Exact full16native atoms/15unknown columns, old historical rows '
                                               'and original64seed0sources.',
                                      'how': 'Frozen source/input lock; preprocessing included in inputs, '
                                             'original public projection retained.'},
                                     {'name': 'active_subset',
                                      'treatment': 'fixed',
                                      'value': 'All five membership-maximal nonzero-shift ties',
                                      'how': 'Same subset for both arms constraints and residual acceptance; no '
                                             'relation-yield selection.'},
                                     {'name': 'zero_policy',
                                      'treatment': 'fixed',
                                      'value': 'completed',
                                      'how': 'Affine zero allowed identically in both arms.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'Shared host; diagnostic phase clocks, wall_valid=false.'}],
                         'comparisons': [{'id': 'C-shift',
                                          'arms': ['baseline', 'shifted'],
                                          'differs_in': ['cover_shift'],
                                          'design': 'one_factor',
                                          'threshold': 'Descriptive new/combined rank and old-kernel action; all '
                                                       'retained streams independently replayed, no gain '
                                                       'assumed.'}],
                         'aa_not_applicable': 'Exact fixed finite enumeration; no noisy primary metric.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'All five fixed input cells in original order, baseline then shifted, '
                                           'one process; no success/rank stop.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'All five post-survey membership-selected ties, frozen '
                                                     'before relation data; no further candidate or source '
                                                     'draws.',
                                             'independent_of_arm': True},
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Public known curve and arm labels; exact descriptive observation.',
                                    'unmasked_at': None}},
     'sample_size': {'instances': 5,
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
     'metrics': {'primary': [{'id': 'attempts',
                              'name': 'attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Complete collection descriptors; replay charged separately.',
                              'source': 'analysis.json cells[].attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'witnesses',
                              'name': 'witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted canonical principal-divisor rows.',
                              'source': 'analysis.json cells[].witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'unique_equations',
                              'name': 'unique equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct new augmented affine equations.',
                              'source': 'analysis.json cells[].unique_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'new_rank',
                              'name': 'new rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of new rows alone on unchanged projected columns.',
                              'source': 'analysis.json cells[].new_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'combined_rank',
                              'name': 'combined rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of preprocessing M plus new rows.',
                              'source': 'analysis.json cells[].combined_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'rank_gain',
                              'name': 'rank gain',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Combined rank minus preprocessing rank; not larger pool size.',
                              'source': 'analysis.json cells[].rank_gain',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nonzero_old_kernel_syndromes',
                              'name': 'nonzero old kernel syndromes',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'New rows with nonzero product against retained complete old kernel.',
                              'source': 'analysis.json cells[].nonzero_old_kernel_syndromes',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'source_zero_witnesses',
                              'name': 'source zero witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted rows with cover source x=0.',
                              'source': 'analysis.json cells[].source_zero_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'constraint_zero_witnesses',
                              'name': 'constraint zero witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted rows with at least one cover constraint x=0.',
                              'source': 'analysis.json cells[].constraint_zero_witnesses',
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
     'stopping_rules': [{'rule': 'Exactly five matched pairs, twoarms each:1863680 attempts per size15cell '
                                 'and1490944 per size14cell;15654912 collection attempts plus separately charged '
                                 'complete replay. No sampling or early rank stop.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Source/input change or independent replay mismatch invalidates completeness; '
                                 'preserve all prefixes and unknown cells.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiB memory and21600s wall/CPU watchdog protect the machine, not a research '
                                 'spend cap. Stopped cells remain unresolved.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Changed source/input, active subset, original projection/preprocessing or failed '
                            'complete replay prevents verified observation.',
                            'Unknown/missing cells remain null, collected-but-unverified cells remain explicit.',
                            'Partial collection counters do not establish complete cost or Delta-per-cost.'],
     'decision_rule': {'text': 'Report every matched subset/cover cell and exact new/combined ranks, rank gain '
                               'over old M, syndrome and zero-witness counts. No scientific state or speed '
                               'claim.',
                       'comparison_ids': ['C-shift'],
                       'threshold': 'Complete fixed stream and separate independent arithmetic replay.',
                       'statistic': 'Exact retained row equations, ranks and old-kernel products.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'Descriptive paired differences only.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '5b51b1089d52e6d8692f8f95495244ce6bb5b9202cd14b574d93998d1a0826c6'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-cell baseline/shifted rank gain and old-kernel action, with unknowns and '
                              'verification status.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Executing before committed exact source, prospective freeze, canonical S3 gate and '
                      'explicit root release.',
                      'Changing active subset between matched arms or accepting residuals outside it.',
                      'Replacing original columns/preprocessing/public sources or selecting by relation yield.',
                      'Adding shared process resources to phase components.',
                      'Complete S, Delta-per-cost, attack advantage or independent scientific review claim from '
                      'partial counters.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Membership eligibility is separate from relation solving and linear algebra; '
                              'complete cost is needed for efficiency claims.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; retained primary section3.2 '
                                    'reread.'},
                    {'ref': 'research/prime_field_cover_survey_20261029/RESULTS.md; '
                            'research/prym_experiment_design_20261019/implementation/relations.py',
                     'provenance': 'internal',
                     'claim': 'All five membership-selected ties are frozen and compared to matched h0 subsets; '
                              'historical exact principal-divisor construction and original E/log columns '
                              'retained.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Ten disjoint arm/candidate cells share one physical process; whole-process '
                                   'resources only in backend_record. Per-cell phase diagnostics are components, '
                                   'not extra executions.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Partial collection field/group counters omit independent replay, '
                                        'integer bookkeeping, affine/kernel work, preprocessing, storage and '
                                        'complete S; no cost rate claimed.',
                    'verification_scope': 'Separate arithmetic checker replays '
                                          'branches/rows/statuses/new+combined ranks and old-kernel action; not '
                                          'independent scientific review or field-counter audit.',
                    'official_status_transition': False}}
    cells = json.loads(INPUTS.read_text())['cells']
    if len(cells) != 5 or sorted(len(c['active_atoms']) for c in cells) != [14,14,14,14,15] or any(len(c['source_order']) != 64 for c in cells):
        raise ValueError('wrong fixed five-candidate subset panel')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build'][0][0] = sys.executable
        arm['parameters'] = dict(**PARAMETERS,inputs_sha256=digest(INPUTS))
    protocol['variable_ledger']['independent'][1]['levels'] = [c['id'] for c in cells]
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
        value = dict(schema='prime-field-b2-root-release/v1',execution_authorized=True,
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
