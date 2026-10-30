"""Bind/freeze A4 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_a4_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'amendments': [],
     'analysis_plan': {'blinded': False,
                       'frozen_before_data': True,
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'script': {'path': 'analyze.py',
                                  'sha256': '6bbb013af90260162db1fcb69f91d504a17a3837ab63ccdcfaabc6179cd6c2cf'}},
     'arms': [{'id': 'prefix0',
               'role': 'reference',
               'description': 'First0 source blocks from the same complete stream; identical full64 public anchor '
                              'projection and same8 targets. Shared construction/queries are executed once.',
               'instrument': {'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'build': [['/workspace/factor-base-venv/bin/python',
                                         '-B',
                                         'research/prime_field_a3_execution_20261030/driver.py']],
                              'commit': '3ff8c32c15f91b355d18e207d6044a1d2363499f',
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'flags': {},
                              'repo': 'crypto-autoresearcher',
                              'threads': 1},
               'parameters': {}},
              {'id': 'prefix16',
               'role': 'candidate',
               'description': 'First16 source blocks from the same complete stream; identical full64 public anchor '
                              'projection and same8 targets. Shared construction/queries are executed once.',
               'instrument': {'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'build': [['/workspace/factor-base-venv/bin/python',
                                         '-B',
                                         'research/prime_field_a3_execution_20261030/driver.py']],
                              'commit': '3ff8c32c15f91b355d18e207d6044a1d2363499f',
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'flags': {},
                              'repo': 'crypto-autoresearcher',
                              'threads': 1},
               'parameters': {}},
              {'id': 'prefix64',
               'role': 'candidate',
               'description': 'First64 source blocks from the same complete stream; identical full64 public anchor '
                              'projection and same8 targets. Shared construction/queries are executed once.',
               'instrument': {'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'build': [['/workspace/factor-base-venv/bin/python',
                                         '-B',
                                         'research/prime_field_a3_execution_20261030/driver.py']],
                              'commit': '3ff8c32c15f91b355d18e207d6044a1d2363499f',
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'flags': {},
                              'repo': 'crypto-autoresearcher',
                              'threads': 1},
               'parameters': {}}],
     'authors': ['A4 delegated administrative coordinator; configured model identity unverified'],
     'claims': [{'id': 'A4-finite-observation',
                 'text': 'Exact finite direct-source/target coverage, prefix affine identifiability and public '
                         'recovery checks on four prospectively generated fixtures. No population, novelty, scalable '
                         'advantage or full-S claim.',
                 'class': 'exact_computation',
                 'decided_by': ['C-prefix']}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Exact finite arithmetic and certificate replay; no noisy advantage '
                                                  'comparison.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'Software controls exercise recovery certificates and known '
                                                        'public-point identities; no native success presumed or '
                                                        'selected.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Complete independent miss/hit/query replay and software '
                                                        'certificate, recipe and admission corruptions; no native '
                                                        'null population invented.'}},
     'created': '2026-10-30',
     'decision_rule': {'text': 'Report generated fixtures/rejections, exact source and target coverage, each prefix '
                               'rank/nullity, single/joint target certificates and bounded public collisions. Keep '
                               'success with base uncertainty distinct from recovery at full base rank; no official '
                               'transition or attack advantage.',
                       'comparison_ids': ['C-prefix'],
                       'threshold': 'Complete independent recipes, finite E-sum oracle, pair/source/target buckets, '
                                    'affine/kernel/certificate and public scalar checks.',
                       'statistic': 'Exact finite per-fixture prefix observations.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'No population or performance effect inferred.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'execution': {'backend': 'local',
                   'checkpoint': {'after_restore': {'counted_units': 'valid', 'wall_time': 'invalid'},
                                  'grace_seconds': None,
                                  'interval_seconds': None,
                                  'policy': 'none',
                                  'restore_validation': 'none'},
                   'measurement_class': 'search',
                   'placement': {'concurrent_compute_processes': 1,
                                 'isolated_clock_claim': False,
                                 'memory_bytes': 2147483648,
                                 'shared_managed_host': True},
                   'queue': None,
                   'retries': {'infrastructure_only': True, 'max_attempts': 1},
                   'timeout_seconds': 21600},
     'extensions': {'export_unit': '12prefix/fixture observations from ONEphysicalprocess,4tables and4complete '
                                   'source+target streams. Shared collection counters only on prefix0 export rows; '
                                   'allprefix analyses charged disjointly in backend once.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Real canonical S3checkpoint plus explicit exact root release mandatory; '
                                            'no in-row restore; fresh failure directories retain prefixes.',
                    'counter_coverage': 'Metered producer Fp/Fr/group and logical calls for '
                                        'collection/certificates/prefix algebra; fixture generation candidate point '
                                        'tests/selectedfield calls retained separately, not completeoperationmodel. '
                                        'Hash/sort/storage/interpreter/OS and checker arithmetic incomplete. No '
                                        'weightedS/rho claim.',
                    'verification_scope': 'Separate complete curve/target recipe reconstruction, one signed-triple '
                                          'oracle percurve mapped to all source/target points, complete pair/query '
                                          'buckets, affine dense ranks/kernel/carried weights and public recovery. '
                                          'Not staffed scientific review or independent fieldcounteraudit.',
                    'official_status_transition': False,
                    'selection': {'rank': 1,
                                  'scope': 'Next bounded transfer and independent-target-identifiability diagnostic '
                                           'afterA3',
                                  'existing_lead': 'LEAD-ICP-generic-table-decomposition',
                                  'disposition_at_start': 'closed_obstructed',
                                  'changes_disposition': False},
                    'target_policy': 'QueriesQonly; all coincidences retained. Diagnostic multipliers1..64 against '
                                     'signed source1..64, not proof that every other collision mechanism is absent.',
                    'not_applicable': ['C lifting',
                                       'polynomial extraction',
                                       'outside residual-point pool generation']},
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'inadmissible': ['Generating fixtures/targets before frozen committed source and actual admission.',
                      'Redrawing based on rank/recovery or dropping source/base target coincidences.',
                      'Calling prefix0 cold recovery without charging known-public anchors/table/generation.',
                      'Summing shared prefix costs, inclusive clocks, group/Fp/Fr vectors into invented fullS.',
                      'Generic-table novelty, attack speedup/rho crossover, deployment or official-status claims.'],
     'invalidation_rules': ['Native fixture/target generation before admission/freeze, changed '
                            'selection/domain/identity/prefix/mapping, omitted candidate traces, outcome-based '
                            'redraw, dropped query buckets or invalid certificates invalidate affected completeness.',
                            'Missing cells remain unknown; collection snapshots survive prefix-analysis/check '
                            'failure.',
                            'Prefix counts are shared work; no triple charging. Inner stage counters overlap Fp/group '
                            'units and do not form weighted S; outer process and verification clocks are '
                            'inclusive/separate.',
                            'Independent common triple enumeration covers all public source/target points at once; '
                            'report88320actual signed triples, not repeated source-times-triple work that was not '
                            'executed.'],
     'links': {'literature': 'literature.md',
               'prior_A3': '../prime_field_a3_execution_20261030/RESULTS.md',
               'prior_D1': '../prime_field_d1_execution_20261030/RESULTS.md'},
     'literature': [{'ref': 'research/prime_field_a3_execution_20261030/RESULTS.md;research/prime_field_d1_execution_20261030/RESULTS.md',
                     'provenance': 'internal',
                     'claim': 'A3covers fixed p4099direct equivalence only. D1isolated recoveries were explained by '
                              'bounded public-multiple collisions; A4freezes those diagnostics prospectively.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; actual prior results read.'},
                    {'ref': 'https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf sections3.1-3.4',
                     'provenance': 'retrieved',
                     'claim': 'Membership, relation solving, setup and linear algebra are separate costs; direct '
                              'local tables do not establish full attack advantage.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; retained primary pages7-9 read.'}],
     'measurement': {'clock': 'counted',
                     'counters': ['Fp.*',
                                  'Fr.*',
                                  'logical descriptors/queries/pair inserts/lookups/bucket entries/certificates/hash '
                                  'updates'],
                     'isolation_required': 'none',
                     'order': 'sequential',
                     'record': ['Host/source/ownership facts',
                                'disjoint producer innerphase counters/clocks',
                                'separate unmetered arithmetic replay clock',
                                'pair table and complete query/miss/hit certificates',
                                'full curve/target candidate traces and prospective bounded-collision diagnostics'],
                     'timed_primary_justification': None,
                     'warmups': 0},
     'metrics': {'primary': [{'id': 'source_queries',
                              'name': 'source queries',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Complete source query count once per curve; repeated prefix values '
                                            'describe shared work, never additive.',
                              'source': 'analysis.json cells[].source_queries',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'pair_entries',
                              'name': 'pair entries',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Signed distinct-pair entries built once per curve, all buckets retained.',
                              'source': 'analysis.json cells[].pair_entries',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'target_queries',
                              'name': 'target queries',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Queries for8 public Q targets, executed once and reused across prefixes.',
                              'source': 'analysis.json cells[].target_queries',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'accepted_witnesses',
                              'name': 'accepted witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Source signed-triple witnesses in this prefix.',
                              'source': 'analysis.json cells[].accepted_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'distinct_equations',
                              'name': 'distinct equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct normalized affine source equations in this prefix.',
                              'source': 'analysis.json cells[].distinct_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_rank',
                              'name': 'base rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of prefix source matrix on constant public projected base columns.',
                              'source': 'analysis.json cells[].base_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_nullity',
                              'name': 'base nullity',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Base columns minus source rank before target-row cancellation.',
                              'source': 'analysis.json cells[].base_nullity',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'joint_rank',
                              'name': 'joint rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Rank of prefix source rows and all8target-column rows.',
                              'source': 'analysis.json cells[].joint_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'joint_base_nullity',
                              'name': 'joint base nullity',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Remaining base uncertainty after cancelling target columns: base columns '
                                            'minus(rank joint-rank target block).',
                              'source': 'analysis.json cells[].joint_base_nullity',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'target_base_rank_gain',
                              'name': 'target base rank gain',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Additional base information after eliminating target columns.',
                              'source': 'analysis.json cells[].target_base_rank_gain',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'single_identified_targets',
                              'name': 'single identified targets',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Count of distinct targets with a single row satisfying vN=0 on prefix M.',
                              'source': 'analysis.json cells[].single_identified_targets',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'joint_identified_targets',
                              'name': 'joint identified targets',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Count of target-unit functionals identifiable in full joint system.',
                              'source': 'analysis.json cells[].joint_identified_targets',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'joint_recoveries_with_base_uncertainty',
                              'name': 'joint recoveries with base uncertainty',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Identified target units while joint base nullity remains positive.',
                              'source': 'analysis.json cells[].joint_recoveries_with_base_uncertainty',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'bounded_collision_targets',
                              'name': 'bounded collision targets',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Targets with any prospective t1..64 collision against signed public1..64 '
                                            'sources; diagnostic not discarded cases.',
                              'source': 'analysis.json cells[].bounded_collision_targets',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'}],
                 'secondary': []},
     'protocol_id': 'PRIME-FIELD-A4-HOLDOUT-TARGET-20261030',
     'question': 'What direct three-sum relation ranks and independently hashed target recoveries occur on four '
                 'prospectively selected larger-field fixtures, at source-row prefixes 0/16/64, with complete '
                 'target-unit certificates and prospectively bounded public-collision diagnostics?',
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Fields8191then65537; curve indices0then1; one source/target stream each '
                                           'then prefixes0/16/64. All physical generation and collection shared once.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Seed0 administrative label; SHA256 byte recipes/domain, no random '
                                                   'scalar draws.'},
                       'instance_sampling': {'rule': 'Four recipes frozen before generated fixture data:2eligible '
                                                     'distinct a2 curves per field, selected by '
                                                     'order/nonsingularity/base-capacity only. No outcome selection.',
                                             'independent_of_arm': True},
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Public exact finite descriptive observations; no secret logs generated.',
                                    'unmasked_at': None}},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'graphs': ['Per-field/prefix rank/nullity and target recovery with/without remaining base '
                              'uncertainty; retained bounded-collision diagnoses and unknowns.'],
                   'report_dir': 'reports/<fresh-run>/',
                   'review_schema': 'experiment.review/v1'},
     'repository': 'crypto-autoresearcher',
     'sample_size': {'instances': 4,
                     'power': {'alpha': 0.05,
                               'correction': 'none',
                               'method': 'exact',
                               'min_attainable_two_sided_p': None,
                               'note': 'Complete finite semantic coverage per completed generated fixture; four '
                                       'fixtures do not estimate a general success probability.',
                               'passes': True,
                               'rank_test_n': None,
                               'tests_in_family': 1},
                     'preflight_runtime': {'estimated_total_seconds': 21600,
                                           'fixed_seconds': None,
                                           'measured_on': 'No affected scientific execution.21600 seconds denotes the '
                                                          'protective machine watchdog, not measured runtime or '
                                                          'spending cap; required engineering-field placeholder.',
                                           'per_sample_seconds': None,
                                           'threads': 1},
                     'replicates': 1,
                     'warmups': 0},
     'schema': 'experiment.protocol/v1',
     'stopping_rules': [{'rule': 'Exactly4rule-selected fixtures,64public source blocks,8independent targets per '
                                 'fixture, full pair/source/target query coverage, prefixes0/16/64; no rank or '
                                 'recovery stop.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': '128curve/target candidates,2048retained source/target rows,4096pair entries are '
                                 'protective refusal gates preserving prefixes, never truncation or replacement '
                                 'rules.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': 'Oneprocess/thread2GiB21600sCPU/wall machine watchdog; not spending cap.',
                         'kind': 'budget',
                         'preregistered': True}],
     'study_dir': 'research/prime_field_a4_execution_20261030',
     'variable_ledger': {'independent': [{'name': 'source_prefix', 'levels': [0, 16, 64]},
                                         {'name': 'field', 'levels': [8191, 65537]}],
                         'factors': [{'name': 'curve_selection',
                                      'treatment': 'fixed',
                                      'value': 'a2;2distinct eligible curves per field; hash-derived b;128candidate '
                                               'cap; prime order!=p; nonzeroB/nonsingular; original describe base/P '
                                               'rule',
                                      'how': 'Freeze rules before any generated fixtures; retain all rejection '
                                             'traces; never use rank, target or yield for selection.'},
                                     {'name': 'public_projection',
                                      'treatment': 'fixed',
                                      'value': 'Known public sources1..64 identical across all prefixes',
                                      'how': 'Prefix0 means zero collected rows, not zero public information. All '
                                             'anchor derivations retained.'},
                                     {'name': 'target_selection',
                                      'treatment': 'fixed',
                                      'value': '8unique canonical-y hash-x targets per fullEC1UID,128candidates each; '
                                               'all source/base coincidences retained',
                                      'how': 'No scalar labels, target-success redraw or filtering. Query Q only; '
                                             't1..64 used solely for collision diagnosis.'},
                                     {'name': 'table_reuse',
                                      'treatment': 'fixed',
                                      'value': 'One complete signed distinct-pair table per curve for source64 and '
                                               'target8 queries',
                                      'how': 'All buckets/infinity, j<k<third; source blocks sorted by '
                                             'SHA(domain|source|EC1UID|scalar). Prefixes reanalyze retained rows.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'One process/thread, shared host diagnostic clocks only.'}],
                         'comparisons': [{'id': 'C-prefix',
                                          'arms': ['prefix0', 'prefix16', 'prefix64'],
                                          'differs_in': ['source_prefix'],
                                          'design': 'one_factor',
                                          'threshold': 'Complete exact finite records, independent '
                                                       'arithmetic/recipe/query/affine/kernel/certificate checks; '
                                                       'descriptive outcomes only.'}],
                         'aa_not_applicable': 'Exact finite descriptive study; no advantage or p-value.',
                         'crosses_map': False},
     'version': 1}
    data=json.loads(INPUTS.read_text())
    expected=dict(schema='prime-field-holdout-rules/v1',domain='prime-field-holdout-targets/20261030/v1',
        fields=[dict(p=8191,base_size=16),dict(p=65537,base_size=32)],curves_per_field=2,a=2,
        maximum_curve_candidates=128,sources=64,targets=8,maximum_target_candidates=128,
        prefixes=[0,16,64],collision_multipliers=64,max_retained_rows=2048,max_pair_entries=4096)
    if any(data.get(k)!=v for k,v in expected.items()) or 'cells' in data:
        raise ValueError('exact prospective holdout rules required; no generated fixtures in inputs')
    for arm in protocol['arms']:
        arm['instrument'].update(commit=commit,binary_sha256=digest(Path(sys.executable).resolve()))
        arm['instrument']['build']=[[sys.executable,'-B','research/prime_field_a4_execution_20261030/driver.py']]
        arm['parameters']={**PARAMETERS,'inputs_sha256':digest(INPUTS)}
    definitions={'source_rows':'Source witnesses in this prefix.','target_rows':'Natural target witnesses in shared complete target stream.','base_columns':'Constant projected unknown width after full64 public anchors.','base_rank_after_target_cancellation':'Joint rank minus rank of8target-column block.','single_targets':'Distinct single-row recovered target count.','joint_targets':'Distinct joint-system recovered target count.','early_single_targets':'Single recoveries with prefix base nullity positive.','early_joint_targets':'Joint recoveries with base uncertainty remaining after target cancellation.'}
    protocol['metrics']['primary'] += [dict(id=k,name=k.replace('_',' '),unit='objects',kind='exact',definition=v,source='analysis.json cells[].'+k,aggregation='per_row',resolution='1',uncertainty='none_exact') for k,v in definitions.items()]
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
        value = dict(schema='prime-field-a4-root-release/v1',execution_authorized=True,
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
