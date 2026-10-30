"""Bind/freeze D1 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_d1_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRYM-D1-NATURAL-TARGETS-20261030',
     'version': 1,
     'created': '2026-10-30',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_d1_execution_20261030',
     'authors': ['D1 execution-contract coordinator; inherited model identity unverified'],
     'links': {'literature': 'literature.md', 'prior_criterion': '../prym_leads_20261027/README.md'},
     'question': 'Can full-census naturally generated target rows identify any of eight independently hashed '
                 'public target scalars from the fixed deficient-rank historical matrices, individually or in '
                 'combination, without drawing scalar labels or requiring full factor-base rank?',
     'claims': [{'id': 'D1-natural-interface',
                 'text': 'Every fixed public target follows the prospectively frozen full-EC1-identity hash '
                         'recipe, and complete target relation/recovery/certificate results are replayed '
                         'independently. No recovery or advantage is presumed.',
                 'class': 'exact_computation',
                 'decided_by': ['C-complete-target']}],
     'arms': [{'id': 'natural_target',
               'role': 'candidate',
               'description': 'Full original target-aware cubic census for each of eight independently hashed '
                              'public targets; continue even after recovery.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON',
                                         '-B',
                                         'research/prime_field_factor_base_20261028/run_targets.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}},
              {'id': 'finite_replay',
               'role': 'reference',
               'description': 'Integrated independent hash-recipe, branch and affine recovery replay. Same '
                              'physical process; no separate oracle cost or execution.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON',
                                         '-B',
                                         'research/prime_field_factor_base_20261028/run_targets.py']],
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
                               'not_applicable_reason': 'No target is prescribed to recover. Separate small '
                                                        'software fixtures check positive recovery certificates; '
                                                        'native accepted rows/recovery are independently '
                                                        'replayed and public-point checked.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'No native nonrecovery outcome is presumed. Separate '
                                                        'small software corruptions check hashes/rows/affine '
                                                        'certificates; all native coincidences and failures are '
                                                        'retained.'}},
     'variable_ledger': {'independent': [{'name': 'exact_method', 'levels': ['natural_target', 'finite_replay']},
                                         {'name': 'target_instance', 'levels': []}],
                         'factors': [{'name': 'original_curve_base_preprocessing',
                                      'treatment': 'fixed',
                                      'value': 'Original16atoms/15unknowns and historical B1 M '
                                               'only:97rows/rank13 or67rows/rank9.',
                                      'how': 'Exact embedded input bytes; no B2 augmentation or base draw.'},
                                     {'name': 'target_hash_recipe',
                                      'treatment': 'fixed',
                                      'value': 'SHA256(domain|fullEC1uid|index|counter),j0..3 eachcurve,max10000',
                                      'how': 'Frozen before all eight target generations; no scalar '
                                             'labels/sidecars; all coincidences retained.'},
                                     {'name': 'multipliers',
                                      'treatment': 'fixed',
                                      'value': '1..64 ascending',
                                      'how': 'Complete cubic census per target; no recovery/rank stop.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'Shared host; all phase/whole-process clocks diagnostic, '
                                             'wall_valid=false.'}],
                         'comparisons': [{'id': 'C-complete-target',
                                          'arms': ['natural_target', 'finite_replay'],
                                          'differs_in': ['exact_method'],
                                          'design': 'absolute',
                                          'threshold': 'Complete independent recipe, branch and affine target '
                                                       'recovery certificate equality; recovery is not '
                                                       'required.'}],
                         'aa_not_applicable': 'Complete deterministic finite streams; no noisy primary metric.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Fixed original fixture order, target indices0..3; hash then full '
                                           'collection then independent replay per target; one physical process.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'Exactly two fixed original fixtures x four public hash '
                                                     'indices; full EC1 curve identity independent of base UID; '
                                                     'no replacement after coincidences or failures.',
                                             'independent_of_arm': True},
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Public known curve and arm labels; exact descriptive observation.',
                                    'unmasked_at': None}},
     'sample_size': {'instances': 8,
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
                              'definition': 'Complete target-branch descriptors; independent replay charged '
                                            'separately.',
                              'source': 'analysis.json cells[].attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'witnesses',
                              'name': 'witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted canonical target-aware principal-divisor rows.',
                              'source': 'analysis.json cells[].witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'identified_target',
                              'name': 'identified target',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': '1 exactly when the target unit combination is identifiable in the '
                                            'augmented system, else0 for a completed cell.',
                              'source': 'analysis.json cells[].identified_target',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'single_recovery',
                              'name': 'single recovery',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': '1 when some individual target row is sufficient with preprocessing, '
                                            'else0 for a completed cell.',
                              'source': 'analysis.json cells[].single_recovery',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'combined_recovery',
                              'name': 'combined recovery',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': '1 when preprocessing plus all target rows identifies the target '
                                            'scalar, else0 for a completed cell.',
                              'source': 'analysis.json cells[].combined_recovery',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_rank',
                              'name': 'base rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Fixed historical preprocessing rank, not supplemented by B2.',
                              'source': 'analysis.json cells[].base_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'augmented_rank',
                              'name': 'augmented rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank on original base columns plus target scalar column.',
                              'source': 'analysis.json cells[].augmented_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_nullity',
                              'name': 'base nullity',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Original15columns minus preprocessing rank.',
                              'source': 'analysis.json cells[].base_nullity',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'first_single_attempt',
                              'name': 'first single attempt',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Earliest accepted attempt yielding single-row recovery; absent if '
                                            'none.',
                              'source': 'analysis.json cells[].first_single_attempt',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'first_combined_attempt',
                              'name': 'first combined attempt',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Earliest accepted prefix yielding a combined recovery certificate; '
                                            'absent if none.',
                              'source': 'analysis.json cells[].first_combined_attempt',
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
     'stopping_rules': [{'rule': 'Exactly8targets x2293760descriptors=18350080collection attempts plus equally '
                                 'complete separately charged replay. Hash counters fixed0..9999; stop only on '
                                 'exhaustion/error/watchdog, retaining failure. Never stop after recovery.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Source/input/recipe/certificate mismatch invalidates completeness; collected '
                                 'records survive failed verification and later targets remain unknown.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiB memory/21600s wall+CPU watchdog protect the host, not a research spend '
                                 'cap. Interrupted targets remain unresolved.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Source/input change, nonfullEC1 hash identity, scalar label, altered preprocessing '
                            'or failed complete replay prevents verified observation.',
                            'Missing or interrupted targets remain unknown; no regenerated replacements after '
                            'coincidences.',
                            'No performance claim or complete-cost inference from partial producer counters.'],
     'decision_rule': {'text': 'Report all eight targets, hash recipes/coincidences, exact base/augmented ranks, '
                               'identification and first single/combined recoveries. Deficient base rank is '
                               'allowed. No official transition or advantage claim.',
                       'comparison_ids': ['C-complete-target'],
                       'threshold': 'Complete independent public-hash/branch/recovery verification, regardless '
                                    'of recovery outcome.',
                       'statistic': 'Exact target identification and checked row-combination certificates.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'None; finite interface observations only.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '076dcddafaa338ed20c77ab0384e046c0dbf8fe0da0a34395891416a75ef195a'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-target preprocessing/augmented ranks, identification and first recovery '
                              'coverage; unknown and coincidences explicit.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Target generation before committed exact source, prospective freeze, actual S3 gate and '
                      'explicit root release.',
                      'Drawing scalar labels or replacing targets after coincidences/failure.',
                      'Using B2 results as preprocessing or stopping the census after recovery.',
                      'Requiring full base rank before checking natural target recovery.',
                      'Duplicating integrated oracle counts/resources or claiming complete S/attack speed from '
                      'partial costs.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Membership and local success do not supply complete relation/linear-algebra '
                              'attack costs.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; retained primary reread.'},
                    {'ref': 'research/prym_leads_20261027/README.md',
                     'provenance': 'internal',
                     'claim': 'v is identified exactly when v annihilates old right kernel; natural target '
                              'attachment needs nonzero target coefficient and checked public target recovery. '
                              'Known manufactured weighted pairs are not natural-target successes. '
                              'Pole-completion is separate.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; complete newly available README '
                                    'read.'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Sixteen method/target rows over eight actual target censuses share one '
                                   'physical process. Reference exact counts duplicate oracle equality and must '
                                   'not be summed; reference resources/counters empty.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Partial producer field/group counters omit hash recipe/setup, '
                                        'independent replay, integer bookkeeping, affine/kernel operations, '
                                        'storage and complete S.',
                    'verification_scope': 'Separate hash-recipe and arithmetic full branch/affine recovery '
                                          'replay; not independent scientific review or field-counter audit.',
                    'official_status_transition': False}}
    data=json.loads(INPUTS.read_text());cells=data['cells']
    if (len(cells)!=2 or data['target_domain']!='prime-field-leads/20261028/target/v1' or data['max_target_counters']!=10000 or
        data['multipliers']!=list(range(1,65)) or any(c['target_indices']!=[0,1,2,3] or c['target_curve_uid']!=c['fixture']['ec1']['curve_uid'] or
            len(c['fixture']['factor_base'])!=16 or len(c['source_order'])!=64 for c in cells)):
        raise ValueError('wrong fixed eight-target full-EC1 recipe panel')
    if (sorted((c['fixture']['p'],c['fixture']['a'],c['fixture']['b'],c['fixture']['r']) for c in cells)!=[(4099,2,13,4021),(4099,2,16,4111)] or
        data.get('target_identity')!='full_ec1_curve_uid' or any(c['source_order']!=c['fixture']['width_binding']['source_order'] or
            len(c['preprocessing_rows'])!=(97 if c['fixture']['b']==13 else 67) or any(r.get('target_coefficient',0) for r in c['preprocessing_rows']) for c in cells)):
        raise ValueError('original historical-only preprocessing and source panel required')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build'][0][0]=sys.executable
        arm['parameters']=dict(**PARAMETERS,inputs_sha256=digest(INPUTS))
    protocol['variable_ledger']['independent'][1]['levels']=[c['target_curve_uid']+'#'+str(j) for c in cells for j in c['target_indices']]
    protocol['analysis_plan']['script']['sha256']=digest(HERE/'analyze.py')
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
        value = dict(schema='prime-field-d1-root-release/v1',execution_authorized=True,
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
