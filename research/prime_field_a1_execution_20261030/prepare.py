"""Bind/freeze A1 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_a1_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRYM-A1-RESIDUAL-OUTSIDE-20261030',
     'version': 1,
     'created': '2026-10-30',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_a1_execution_20261030',
     'authors': ['A1 standalone execution-contract coordinator; inherited model identity unverified'],
     'links': {'literature': 'literature.md',
               'prior_B2': '../prime_field_b2_execution_20261030/RESULTS.md',
               'prior_D1': '../prime_field_d1_execution_20261030/RESULTS.md'},
     'question': 'On the unchanged original two curves/bases/sources and historical matrices, how much '
                 'additional base-only information survives cancellation of signed unknown outside residual '
                 'points from nested independently hashed pools16/32, compared with smooth rows from the same '
                 'complete stream?',
     'claims': [{'id': 'A1-cancelled-information',
                 'text': 'A complete shared residual stream is replayed independently; nested partial rows are '
                         'scored only after outside-column cancellation, with original-row weights and a dense '
                         'rank oracle. No rank gain or cost advantage is presumed.',
                 'class': 'exact_computation',
                 'decided_by': ['C-pool16', 'C-pool32']}],
     'arms': [{'id': 'smooth',
               'role': 'reference',
               'description': 'Nested residual pool prefix0, filtered from the same sole pool32stream per curve. '
                              'Constraints remain oldbase; no independent arm collection.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a1_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}},
              {'id': 'pool16',
               'role': 'candidate',
               'description': 'Nested residual pool prefix16, filtered from the same sole pool32stream per '
                              'curve. Constraints remain oldbase; no independent arm collection.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a1_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}},
              {'id': 'pool32',
               'role': 'candidate',
               'description': 'Nested residual pool prefix32, filtered from the same sole pool32stream per '
                              'curve. Constraints remain oldbase; no independent arm collection.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a1_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Complete deterministic shared stream with independent finite '
                                                  'replay/dense rank oracle; no noisy performance primary.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No outside cycle or positive Delta is presumed; '
                                                        'separate small software cancellation controls and '
                                                        'complete carried-weight/dense-oracle checks validate '
                                                        'any actual result.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Smooth is the nested empty-outside reference from the '
                                                        'same rawstream. Independent complete replay checks '
                                                        'rejected branches/rows and false cancellation '
                                                        'certificates; no native null outcome presumed.'}},
     'variable_ledger': {'independent': [{'name': 'pool_prefix', 'levels': ['smooth', 'pool16', 'pool32']},
                                         {'name': 'original_curve', 'levels': []}],
                         'factors': [{'name': 'curve_base_preprocessing_sources_cover_poles',
                                      'treatment': 'fixed',
                                      'value': 'Originalp4099curves,16atoms/15projectedcolumns, '
                                               'historical97/rank13 or67/rank9 rows, '
                                               'original64sources,h0/completedzero/poles3,3',
                                      'how': 'All embedded input/source bytes pinned; no B2/D1 rows or scalar '
                                             'labels.'},
                                     {'name': 'outside_pool',
                                      'treatment': 'fixed',
                                      'value': '32canonical signed E representatives, fullEC1SHA256recipe frozen '
                                               'before generation',
                                      'how': 'Pool independent of collection/yield; exclude signed '
                                             'oldbase/previouspool, retain/project known public-source '
                                             'coincidences.'},
                                     {'name': 'physical_collection',
                                      'treatment': 'fixed',
                                      'value': 'One complete pool32stream per curve',
                                      'how': 'Nested arms filter by original pool ordinal, not by reduced '
                                             'unknown-column width; no rank stop.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'One process/thread, shared host; phase/whole-process clocks '
                                             'diagnostic, wall_valid=false.'}],
                         'comparisons': [{'id': 'C-pool16',
                                          'arms': ['smooth', 'pool16'],
                                          'differs_in': ['pool_prefix'],
                                          'design': 'one_factor',
                                          'threshold': 'Exact cancelled Delta and certificates compared '
                                                       'descriptively; no gain assumed.'},
                                         {'id': 'C-pool32',
                                          'arms': ['smooth', 'pool32'],
                                          'differs_in': ['pool_prefix'],
                                          'design': 'one_factor',
                                          'threshold': 'Exact cancelled Delta and certificates compared '
                                                       'descriptively; no gain assumed.'}],
                         'aa_not_applicable': 'Exact finite shared-stream enumeration, not a noisy comparison.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Original fixed curve order: generate frozen32pool, collect once, '
                                           'derive all three nested filters and independently replay. No '
                                           'separate arm process or yield selection.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'Exactly the two original fixed fixtures; independently '
                                                     'hashed32pool before branches. '
                                                     'FullEC1UID/domain/indices/counter limits prospectively '
                                                     'frozen, all public coincidences retained.',
                                             'independent_of_arm': True},
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Public known curve and arm labels; exact descriptive observation.',
                                    'unmasked_at': None}},
     'sample_size': {'instances': 2,
                     'replicates': 1,
                     'warmups': 0,
                     'power': {'method': 'exact',
                               'alpha': 0.05,
                               'tests_in_family': 2,
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
     'metrics': {'primary': [{'id': 'logical_attempts',
                              'name': 'logical attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Complete shared-stream descriptors per curve. Repeated across '
                                            'nested arm rows; do not sum as physical work.',
                              'source': 'analysis.json cells[].logical_attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'accepted_witnesses',
                              'name': 'accepted witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted original witness rows retained by the nested pool prefix.',
                              'source': 'analysis.json cells[].accepted_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'distinct_equations',
                              'name': 'distinct equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct normalized affine partial equations on declared base and '
                                            'unknown outside columns.',
                              'source': 'analysis.json cells[].distinct_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'outside_unknown_columns',
                              'name': 'outside unknown columns',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Signed canonical outside unknown columns after public-source scalar '
                                            'projection.',
                              'source': 'analysis.json cells[].outside_unknown_columns',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'outside_rank',
                              'name': 'outside rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Exact rank of outside coefficient block U.',
                              'source': 'analysis.json cells[].outside_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'stacked_rank',
                              'name': 'stacked rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Exact rank of stacked [M,0;B,U].',
                              'source': 'analysis.json cells[].stacked_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_rank_before',
                              'name': 'base rank before',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Original historical preprocessing coefficient rank.',
                              'source': 'analysis.json cells[].base_rank_before',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_rank_after',
                              'name': 'base rank after',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Base rank after carried-weight outside cancellation.',
                              'source': 'analysis.json cells[].base_rank_after',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'delta',
                              'name': 'delta',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'rank([M,0;B,U])-rank(U)-rank(M), equal cancelled base rank gain.',
                              'source': 'analysis.json cells[].delta',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'cancellation_equations',
                              'name': 'cancellation equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Retained cancellation equations with original partial-row weights.',
                              'source': 'analysis.json cells[].cancellation_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'known_public_pool_points',
                              'name': 'known public pool points',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Pool-prefix representatives with known signed public-source '
                                            'scalars; never counted as unknowns.',
                              'source': 'analysis.json cells[].known_public_pool_points',
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
     'stopping_rules': [{'rule': 'Exactly2curves x2293760branches=4587520physical collection attempts plus '
                                 'separately charged full replay. One32pool stream per curve, three nested '
                                 'filters; no rank stop or replacement.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Pool indices0..31/counters0..9999 fixed before generation; counter exhaustion '
                                 'or failed recipe/branch/cancellation check retains prefix and unresolved '
                                 'remainder.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiBmemory/21600sCPU+wall watchdog protects host; not a spending cap or '
                                 'measured runtime prediction.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Changed source/input, pool recipe, original M/projection, curve/source/cover/pole '
                            'policy or failed independent replay invalidates verified completeness.',
                            'Unknown/missing cases remain null. Additional unknown columns are eliminated before '
                            'measuring base-only information.',
                            'Known-source coincidences are retained with signed scalar projection; never '
                            'introduced as false unknowns.',
                            'Shared collection/replay costs occur once. Partial counters do not establish '
                            'complete S or Delta-per-total-cost.'],
     'decision_rule': {'text': 'Describe all nested arm counts, signed outside ranks, cancellation certificates '
                               'and exact Delta against original M. No scientific state transition or cost '
                               'advantage claim.',
                       'comparison_ids': ['C-pool16', 'C-pool32'],
                       'threshold': 'Full independent pool/branch/row/cancellation replay and dense rank oracle '
                                    'equality, regardless of Delta.',
                       'statistic': 'Exact cancelled rank identity with carried original-row weights.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'Descriptive finite Delta only, no performance-rate claim.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '076dcddafaa338ed20c77ab0384e046c0dbf8fe0da0a34395891416a75ef195a'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-curve nested-arm witness/outside-rank/Delta observations, unknowns and '
                              'shared-cost scope explicit.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Native pool generation before exact committed sources, prospective protocol freeze, '
                      'actualS3gate and explicit root release.',
                      'Choosing/replacing pools by relation yield or importing B2/D1 recovered scalar labels.',
                      'Counting signed aliases/known-source exposures as extra unknowns or scoring stacked rank '
                      'before subtracting outside rank.',
                      'Charging the same shared stream as six native executions.',
                      'Claiming complete S, Delta-per-total-cost, novelty or attack advantage from partial '
                      'counters.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Membership, relation solving and linear algebra costs remain separate; row count '
                              'is not useful base information or complete cost.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; retained primary page8 reread.'},
                    {'ref': 'research/prime_field_b2_execution_20261030/RESULTS.md;research/prime_field_d1_execution_20261030/RESULTS.md;src/crypto_autoresearcher/index_calculus/relation_quality.py',
                     'provenance': 'internal',
                     'claim': 'B2 had no outside columns; D1 partial cancellation was post-hoc target-row reuse. '
                              'A1 prospectively tests residual-outside pools and uses standard '
                              'outside-cancellation rank identity with original-row weights.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; complete reports and '
                                    'carried-cancellation implementation read.'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Six nested arm/curve records over two shared rawstreams in one physical '
                                   'process. Logicalattempt metrics repeat and must not be summed; native '
                                   'counters only smooth rows, whole-process resources once in backend.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Shared collection/setup/pool hashing and elimination/replay components '
                                        'retained where measured; producer operation counters incomplete, no '
                                        'complete-S or total-cost rate claim.',
                    'verification_scope': 'Independent roots-set/public-group pool recipe, '
                                          'fullbranch/witness/cancellation replay and dense rank oracle; '
                                          'implementation check, not independent scientific review or counter '
                                          'audit.',
                    'official_status_transition': False}}
    if not isinstance(PARAMETERS,dict):raise ValueError('final scientific parameters not yet bound')
    data=json.loads(INPUTS.read_text());cells=data['cells']
    protocol['sample_size']['power'].update(correction='other',note='Complete exact finite identities and two descriptive nested contrasts; no statistical hypothesis tests or p-values, so stochastic multiple-testing correction is inapplicable.')
    protocol['decision_rule']['multiple_comparison_correction']='other'
    if (len(cells)!=2 or sorted((c['fixture']['p'],c['fixture']['a'],c['fixture']['b'],c['fixture']['r']) for c in cells)!=[(4099,2,13,4021),(4099,2,16,4111)] or
        any(len(c['fixture']['factor_base'])!=16 or c['source_order']!=c['fixture']['width_binding']['source_order'] or len(c['source_order'])!=64 or
            len(c['preprocessing_rows'])!=(97 if c['fixture']['b']==13 else 67) for c in cells)):
        raise ValueError('original historical-only two-curve source/preprocessing panel required')
    if (data.get('schema')!='prime-field-residual-inputs/v1' or data.get('pool_prefixes')!=[0,16,32] or
        data.get('pool_recipe')!={'domain':'prime-field-residual-pool/20261030/v1','size':32,'max_counter':10000} or
        any(c['pool_curve_uid']!=c['fixture']['ec1']['curve_uid'] for c in cells)):
        raise ValueError('wrong frozen full-EC1 outside-pool recipe')
    for name,definition in [('direct_base_rank','Rank of oldM plus new rows with identically zero projected outside block.'),('direct_base_gain','Direct base rank minus oldM rank; includes known public-pool coincidences and within-row outside self-cancellation.'),('cross_row_cancellation_gain','Total cancelled Delta minus direct_base_gain, isolating extra information from cross-row outside cancellation.')]:
        protocol['metrics']['primary'].append(dict(id=name,name=name.replace('_',' '),unit='objects',kind='exact',definition=definition,source='analysis.json cells[].'+name,aggregation='per_row',resolution='1',uncertainty='none_exact'))
    protocol['stopping_rules'].append(dict(rule='Protective max_partial_rows2048/max_outside_columns32 are explicit refusals before allocation, never truncation or rank-based success stops; preserve prefixes and mark incomplete.',kind='invalidation',preregistered=True))
    for arm,prefix in zip(protocol['arms'],(0,16,32)):
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build'][0][0]=sys.executable
        arm['parameters']={**PARAMETERS,'pool_prefix':prefix,'inputs_sha256':digest(INPUTS)}
    protocol['variable_ledger']['independent'][1]['levels']=[c['fixture']['uid'] for c in cells]
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
        value = dict(schema='prime-field-a1-root-release/v1',execution_authorized=True,
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
