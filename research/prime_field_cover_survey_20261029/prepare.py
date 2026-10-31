"""Bind/freeze shifted-cover before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_cover_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRIME-FIELD-COVER-SURVEY-20261029',
     'version': 1,
     'created': '2026-10-29',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_cover_survey_20261029',
     'authors': ['Shifted-cover execution-contract coordinator; model identity unverified'],
     'links': {'literature': 'literature.md'},
     'question': 'Which of all4099 affine shifts on each retained p4099 curve give a nonsingular shifted '
                 'even-sextic cover admitting every one of the same16base atoms, and how many of the '
                 'same64public sources lift?',
     'claims': [{'id': 'cover-finite-admissibility',
                 'text': 'All shifts are enumerated with complete base/source square and zero masks, and checked '
                         'by separate roots-set membership and independent public-source arithmetic. No '
                         'collector, rank or advantage conclusion follows.',
                 'class': 'exact_computation',
                 'decided_by': ['C-oracle']}],
     'arms': [{'id': 'survey',
               'role': 'candidate',
               'description': 'One all-shifts survey on two fixed fixtures; eighty memberships at every shift, '
                              'no early stop.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_cover_survey_20261029/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'shift_order': 'all_field_elements_ascending',
                              'base_atoms': 16,
                              'source_count': 64}},
              {'id': 'roots_set_oracle',
               'role': 'reference',
               'description': 'Integrated roots-set oracle and independent original public-source arithmetic; no '
                              'separate process or independent cost is invented.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_cover_survey_20261029/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'shift_order': 'all_field_elements_ascending',
                              'base_atoms': 16,
                              'source_count': 64},
               'same_instrument_as': 'survey'}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Complete deterministic finite survey with a separately '
                                                  'implemented exact membership oracle, no noisy comparative '
                                                  'metric.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No shift is assumed eligible. Existing marked-small '
                                                        'software tests check the shifted cover maps; actual '
                                                        'square/zero mask positives are checked exhaustively by '
                                                        'roots-set oracle.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Every singular or ineligible shift is retained with its '
                                                        'masks; oracle checks exclusions, not a hypothesized '
                                                        'null population.'}},
     'variable_ledger': {'independent': [{'name': 'method', 'levels': ['survey', 'roots_set_oracle']},
                                         {'name': 'fixture', 'levels': []}],
                         'factors': [{'name': 'curve_base_sources',
                                      'treatment': 'fixed',
                                      'value': 'Exact original two fixtures,16atoms and64seed0source-order '
                                               'points',
                                      'how': 'Committed source/input lock; no target/base draw or yield '
                                             'selection.'},
                                     {'name': 'shifts',
                                      'treatment': 'fixed',
                                      'value': 'All h0..4098 in increasing order',
                                      'how': 'Exactly8198frames;80membership tests each, including singular '
                                             'shifts; no early stop.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'Shared managed host; all clocks diagnostic, wall_valid=false.'}],
                         'comparisons': [{'id': 'C-oracle',
                                          'arms': ['survey', 'roots_set_oracle'],
                                          'differs_in': ['method'],
                                          'design': 'absolute',
                                          'threshold': 'Every coefficient, square/zero mask, singularity and '
                                                       'eligibility decision equals the separate finite '
                                                       'oracle.'}],
                         'aa_not_applicable': 'Complete deterministic finite identity checking.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Survey followed by integrated verification in one physical process; '
                                           'fixed ascending shifts and original fixture/source order.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'Both unchanged retained fixtures; every field shift, no '
                                                     'draw or replacement.',
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
                                           'estimated_total_seconds': 3600,
                                           'measured_on': 'No retained all-shifts survey has run.3600seconds is '
                                                          'a protective process watchdog, not measured runtime, '
                                                          'speed prediction or spending cap.'}},
     'metrics': {'primary': [{'id': 'frames',
                              'name': 'frames',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'All field shifts retained per fixture.',
                              'source': 'analysis.json cells[].frames',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'eligible_frames',
                              'name': 'eligible frames',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Nonsingular shifts admitting all16nativebase atoms.',
                              'source': 'analysis.json cells[].eligible_frames',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nonzero_eligible_frames',
                              'name': 'nonzero eligible frames',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Eligible shifts h!=0.',
                              'source': 'analysis.json cells[].nonzero_eligible_frames',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'singular_frames',
                              'name': 'singular frames',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Shifts with f(h)=0.',
                              'source': 'analysis.json cells[].singular_frames',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'public_source_lifts_for_eligible',
                              'name': 'public source lifts for eligible',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Total public source entries lifting at eligible shifts, counting a '
                                            'source once per eligible shift; square mask includes zero.',
                              'source': 'analysis.json cells[].public_source_lifts_for_eligible',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'}],
                 'secondary': []},
     'measurement': {'isolation_required': 'none',
                     'warmups': 0,
                     'order': 'sequential',
                     'clock': 'counted',
                     'counters': ['modular_pow_calls',
                                  'base_membership_tests',
                                  'source_membership_tests',
                                  'setup_group_ops'],
                     'record': ['host/source facts',
                                'full rows, bit masks, coefficients and singularity reason',
                                'separate verification',
                                'phase journal',
                                'admission receipt',
                                'stdout/stderr'],
                     'timed_primary_justification': None},
     'execution': {'backend': 'local',
                   'queue': None,
                   'measurement_class': 'search',
                   'timeout_seconds': 3600,
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
     'stopping_rules': [{'rule': 'All4099shifts x2fixtures, all16base+64source membership tests per frame; no '
                                 'early stop, selection or yield-dependent replacement.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'Wrong source, mask or finite oracle invalidates complete observation; preserve '
                                 'all available output and unknown cells.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': '2GiB memory/3600s wall+CPU machine watchdog; interruption is unresolved, never '
                                 'an empty eligible set.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Source/input change or oracle mismatch prevents verified complete observation.',
                            'Missing fixtures remain unknown.',
                            'No isolated timing, collection/rank or ECDLP performance conclusion.'],
     'decision_rule': {'text': 'Describe complete finite admissibility by fixture, with eligible and singular '
                               'counts and public-source lift coverage. No collector experiment or scientific '
                               'state transition.',
                       'comparison_ids': ['C-oracle'],
                       'threshold': 'Complete exact all-shifts masks and separate finite oracle equality.',
                       'statistic': 'Exact finite masks and counted frames.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'None; descriptive finite counts.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '5b51b1089d52e6d8692f8f95495244ce6bb5b9202cd14b574d93998d1a0826c6'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-fixture complete eligible/nonzero-eligible/singular counts and source lift '
                              'coverage; unknown explicitly separated.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Survey before committed exact source, prospective frozen protocol, actual S3 checkpoint '
                      'gate and explicit root release.',
                      'Selecting shifts by collector yield, changing bases/curves or public source order.',
                      'Claiming collector/rank/isogeny/scalar-action or attack advantage from cover '
                      'admissibility.',
                      'Inventing an independent oracle process or duplicating shared resources.'],
     'literature': [{'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf section3.2',
                     'provenance': 'retrieved',
                     'claim': 'Membership representation is separate from relation-solving and linear-algebra '
                              'costs.',
                     'verified_by': '/root/c1_execution_contract,2026-10-29; retained primary page8 reread.'},
                    {'ref': 'src/crypto_autoresearcher/index_calculus/cover_frames.py; '
                            'research/prym_factor_base_width_20261025/README.md',
                     'provenance': 'internal',
                     'claim': 'A shifted even-sextic frame maps to the same original E; its auxiliary E2 is not '
                              'assumed isogenous or a scalar action. Exact old base/public sources remain fixed.',
                     'verified_by': '/root/c1_execution_contract,2026-10-29'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'model_verified': False,
                    'model_identity': None,
                    'official_status_transition': False,
                    'physical_executions': 1,
                    'export_unit': 'Four method/fixture rows share two actual survey fixture cells and one physical process. Reference counts duplicate exact oracle comparisons and must not be summed; reference resources and counters are empty.',
                    'counter_scope': 'Membership and source-point setup counters; no collection, rank or '
                                     'complete-S costs.',
                    'checkpoint_semantics': 'Actual canonical S3 gate; no in-process restore; retries fresh '
                                            'output and invalid clocks.'}}
    fixtures = json.loads(INPUTS.read_text())['fixtures']
    if len(fixtures) != 2 or any(f['p'] != 4099 or len(f['factor_base']) != 16 or len(f['width_binding']['source_order']) != 64 for f in fixtures):
        raise ValueError('wrong retained two-fixture input panel')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
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
        value = dict(schema='prime-field-cover-survey-root-release/v1',execution_authorized=True,
            authority='Explicit root Phase B release under standing user authorization; no research-state promotion.',
            owner=args.owner,source_commit=args.source_commit,source_sha256=source,input_sha256=input_map,
            interpreter_sha256=digest(Path(sys.executable).resolve()),protocol_sha256=protocol['freeze']['protocol_sha256'],
            checkpoint_gate_passed=True,prior_checkpoint=checkpoint,parameters=PARAMETERS,
            memory_bytes=2147483648,watchdog_seconds=3600,
            package_versions={name:importlib.metadata.version(name) for name in ['python-flint','sympy','jsonschema','PyYAML']},
            issued_utc=datetime.now(timezone.utc).isoformat(),model_verified=False,model_identity=None)
        write_once(args.out,value)
        print(json.dumps(dict(release=str(args.out),owner=args.owner,execution_authorized=True)))


if __name__ == '__main__':
    main()
