"""Bind/freeze A2 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_a2_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRYM-A2-NORM-COMPLETION-20261030',
     'version': 1,
     'created': '2026-10-30',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_a2_execution_20261030',
     'authors': ['A2 standalone execution-contract coordinator; inherited model identity unverified'],
     'links': {'literature': 'literature.md', 'prior_A1': '../prime_field_a1_execution_20261030/README.md'},
     'question': 'On both unchanged original curves, how much base-only affine information is added by admitting '
                 'rational distinct residual pairs whose E images are negatives, without residual-pool '
                 'membership or any new unknown columns?',
     'claims': [{'id': 'A2-norm-interface',
                 'text': 'Complete shared norm-pair streams and original-column rank/kernel information are '
                         'independently replayed on both fixed curves. Smooth and norm-completed filters share '
                         'one collection per curve; no positive rank gain or efficiency claim is presumed.',
                 'class': 'exact_computation',
                 'decided_by': ['C-norm']}],
     'arms': [{'id': 'smooth',
               'role': 'reference',
               'description': 'Nested rows with both residual E endpoints in the oldbase.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a2_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}},
              {'id': 'norm_completed',
               'role': 'candidate',
               'description': 'All smooth rows plus rational distinct residual pairs whose E images sum to zero, '
                              'irrespective of pool membership; no new unknowns.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a2_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {}}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Complete deterministic finite stream with independent '
                                                  'arithmetic/dense rank replay; no noisy performance primary.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No gain is presumed on either fixed curve. Small '
                                                        'software fixtures test valid norm-pair cancellation and '
                                                        'full native replay verifies any accepted rows.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Smooth is the same-stream reference. Separate '
                                                        'corruption/noncancelling-pair controls test rejection; '
                                                        'no native zero outcome presumed.'}},
     'variable_ledger': {'independent': [{'name': 'residual_acceptance', 'levels': ['smooth', 'norm_completed']},
                                         {'name': 'original_curve', 'levels': []}],
                         'factors': [{'name': 'original_curve_base_M_sources_cover_poles',
                                      'treatment': 'fixed',
                                      'value': 'Both originalp4099curves,16native/15unknowncolumns, '
                                               'historical97/rank13 or67/rank9 rows, '
                                               'source64,h0/completedzero,poles3,3',
                                      'how': 'Exact input/source commitments; no A1/B2/D1 rows or recovered '
                                             'labels added.'},
                                     {'name': 'collection',
                                      'treatment': 'fixed',
                                      'value': 'One full norm-completed census per curve',
                                      'how': 'Smooth is nested by residual oldbase acceptance; no pool '
                                             'hashing/outside columns/rank stop.'},
                                     {'name': 'norm_pair_rule',
                                      'treatment': 'fixed',
                                      'value': 'Rational distinct C residual points with equal E x-coordinate '
                                               'and opposite E y-coordinate',
                                      'how': 'Principal-divisor, original-E and auxiliary equations checked '
                                             'separately; additional rows carry only oldbase coefficients.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'One process/thread, shared host; all clocks diagnostic, '
                                             'wall_valid=false.'}],
                         'comparisons': [{'id': 'C-norm',
                                          'arms': ['smooth', 'norm_completed'],
                                          'differs_in': ['residual_acceptance'],
                                          'design': 'one_factor',
                                          'threshold': 'Exact new/combined rank and old-kernel action; '
                                                       'independent complete replay on both curves, no gain '
                                                       'required.'}],
                         'aa_not_applicable': 'Exact finite census, no noisy comparison.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Original fixed curve order, one complete norm stream then both '
                                           'nested analyses/replay; no arm-specific collection or yield '
                                           'selection.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'Both original fixed fixtures, never only the earlier '
                                                     'A1firstcurve; no pool, target or replacement draw.',
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
     'metrics': {'primary': [{'id': 'logical_attempts',
                              'name': 'logical attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Complete shared-stream attempts per curve; repeats across methods, '
                                            'do not sum as physical work.',
                              'source': 'analysis.json cells[].logical_attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'accepted_witnesses',
                              'name': 'accepted witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Accepted principal-divisor witnesses in the nested arm.',
                              'source': 'analysis.json cells[].accepted_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'norm_completed_witnesses',
                              'name': 'norm completion witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Witnesses newly admitted by the explicit norm-completion flag.',
                              'source': 'analysis.json cells[].norm_completed_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'distinct_equations',
                              'name': 'distinct equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct normalized affine equations on unchanged fifteen projected '
                                            'columns.',
                              'source': 'analysis.json cells[].distinct_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'new_rank',
                              'name': 'new rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of new rows alone.',
                              'source': 'analysis.json cells[].new_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'combined_rank',
                              'name': 'combined rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of original M plus new rows.',
                              'source': 'analysis.json cells[].combined_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'rank_gain',
                              'name': 'rank gain',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Combined rank minus original historical rank; no outside columns.',
                              'source': 'analysis.json cells[].rank_gain',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_nullity_after',
                              'name': 'base nullity after',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Original fifteen columns minus combined rank.',
                              'source': 'analysis.json cells[].base_nullity_after',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nonzero_old_kernel_syndromes',
                              'name': 'nonzero old kernel syndromes',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'New rows with nonzero product against a complete original '
                                            'right-kernel basis.',
                              'source': 'analysis.json cells[].nonzero_old_kernel_syndromes',
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
     'stopping_rules': [{'rule': 'Both originalcurves, complete2293760branches each=4587520physical collection '
                                 'attempts and same separate full replay; two nested filters percurve, no '
                                 'rank/recovery stop.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Protective maxretainedrows2048 is a refusal with prefixes retained, never '
                                 'truncation/success. Source/geometry/row/rank/kernel mismatch leaves incomplete '
                                 'records unresolved.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiBmemory/21600sCPU+wall watchdog protects the host, not measured runtime or '
                                 'spending cap.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Changed original inputs, columns, M, sources, cover/poles/zero policy or failed '
                            'complete independent replay invalidates verified completeness.',
                            'Rationality/distinctness and residual E-pair cancellation must be checked, not '
                            'inferred from a missing pool column.',
                            'Unknown arms remain null; collection snapshots survive analysis/replay failure.',
                            'Shared stream counters/resources occur once; no complete-S/cost-rate claim from '
                            'partial counters.'],
     'decision_rule': {'text': 'Report both nested arms on both original curves: completion labels, distinct '
                               'equations, old-kernel action and same-column rank gains. No status or speedup '
                               'claim.',
                       'comparison_ids': ['C-norm'],
                       'threshold': 'Full geometry/point/rank/kernel replay, regardless of positive gain.',
                       'statistic': 'Exact finite base-only affine equations and ranks.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'Descriptive rank change only, no comparative performance claim.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '076dcddafaa338ed20c77ab0384e046c0dbf8fe0da0a34395891416a75ef195a'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-curve smooth/norm-completed witness and base-rank observations, unknowns and '
                              'shared-cost scope.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Reusing A1freeze/release or running before new exact source commitment/prospective '
                      'protocol/actualS3gate/rootrelease.',
                      'Selecting only b13, importing A1/B2/D1 rows or recovered scalar labels.',
                      'Generating pools/targets or adding new outside unknowns.',
                      'Accepting residual pairs without complete original-E/auxiliary/principal certificates.',
                      'Charging four records as four native censuses or claiming novelty, completeS or speedup.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Relation solving and linear algebra remain separate costs; added local equations '
                              'do not prove complete attack efficiency.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; retained primary reviewed.'},
                    {'ref': 'research/prime_field_a1_execution_20261030/core.py;research/prime_field_a1_execution_20261030/check.py;research/prym_leads_20261027/README.md',
                     'provenance': 'internal',
                     'claim': 'A1firstcurve distinguishes direct from cross-row cancellation. The standard E '
                              'identity P+(-P)=O motivates a separately frozen all-norm residual rule on both '
                              'original curves; full base-only rank/kernel information is checked.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; native sources and firstcurve '
                                    'independent summary read, no A2census executed.'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Four nested arm/curve records share two complete rawstreams in one physical '
                                   'process. Logicalattempts repeat; native counters only smooth rows, resources '
                                   'once in backend.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Partial native field/group counters exclude some setup, integer work, '
                                        'inline verification, affine/kernel operations, replay and storage. No '
                                        'pool hash cost or complete-S/rate claim.',
                    'verification_scope': 'Independent principal/E/auxiliary geometry, full status/branch and '
                                          'dense rank/kernel replay; implementation check, not independent '
                                          'staffed scientific review/counter audit.',
                    'official_status_transition': False}}
    if not isinstance(PARAMETERS,dict):raise ValueError('final scientific parameters not yet bound')
    data=json.loads(INPUTS.read_text());cells=data['cells']
    if (len(cells)!=2 or sorted((c['fixture']['p'],c['fixture']['a'],c['fixture']['b'],c['fixture']['r']) for c in cells)!=[(4099,2,13,4021),(4099,2,16,4111)] or
        data.get('arms')!=['smooth','norm_completed'] or 'pool_recipe' in data or 'pool_prefixes' in data or
        any(len(c['fixture']['factor_base'])!=16 or c['source_order']!=c['fixture']['width_binding']['source_order'] or len(c['source_order'])!=64 or
            len(c['preprocessing_rows'])!=(97 if c['fixture']['b']==13 else 67) for c in cells)):
        raise ValueError('original historical-only two-curve no-pool panel required')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build'][0][0]=sys.executable
        arm['parameters']={**PARAMETERS,'inputs_sha256':digest(INPUTS)}
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
        value = dict(schema='prime-field-a2-root-release/v1',execution_authorized=True,
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
