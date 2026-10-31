"""Bind/freeze A3 before data; root authorization is an explicit later command."""
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
    spec = importlib.util.spec_from_file_location('_a3_protocol_tools', ROOT/'tools/experiment_protocol.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_protocol(commit):
    protocol = {'schema': 'experiment.protocol/v1',
     'protocol_id': 'PRIME-FIELD-A3-DIRECT-MATCH-20261030',
     'version': 1,
     'created': '2026-10-30',
     'repository': 'crypto-autoresearcher',
     'study_dir': 'research/prime_field_a3_execution_20261030',
     'authors': ['A3 delegated administrative coordinator; model identity unverified'],
     'links': {'literature': 'literature.md', 'prior_A2': '../prime_field_a2_execution_20261030/RESULTS.md'},
     'question': 'Do exhaustive signed distinct-three-sum enumeration and a complete pair-table collector '
                 'produce exactly the same direct E relations on both original fixtures, with explicit '
                 'stage/counter coverage, while containing archived A2norm-only descriptors as a subset?',
     'claims': [{'id': 'A3-exact-interface',
                 'text': 'Both direct collectors and independent complete E enumeration/pair-query replay agree '
                         'on all signed distinct-three-sum rows and affine results. Archived A2norm-only rows '
                         'embed as a subset, not an equal semantic set or matched-cost baseline.',
                 'class': 'exact_computation',
                 'decided_by': ['C-direct']}],
     'arms': [{'id': 'enumeration',
               'role': 'reference',
               'description': 'Exhaustive64*C(16,3)*8 signed distinct triples per curve.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a3_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'arms': ['smooth', 'norm_completed'],
                              'include_zero': True,
                              'cover_shift': 0,
                              'max_retained_rows': 2048,
                              'inputs_sha256': '1fb3f7904c6b2d27f765bb7db13f2bd6b44af65c7c2b969b8efafc9339866b7a'}},
              {'id': 'pair_table',
               'role': 'candidate',
               'description': 'All480signedpairs and2048source/third/sign queries per curve, all bucket entries '
                              'retained, j<k<third filter and infinity keys included.',
               'instrument': {'repo': 'crypto-autoresearcher',
                              'commit': 'PLACEHOLDER',
                              'build': [['PYTHON', '-B', 'research/prime_field_a3_execution_20261030/driver.py']],
                              'binary_sha256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                              'flags': {},
                              'env': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'},
                              'threads': 1},
               'parameters': {'arms': ['smooth', 'norm_completed'],
                              'include_zero': True,
                              'cover_shift': 0,
                              'max_retained_rows': 2048,
                              'inputs_sha256': '1fb3f7904c6b2d27f765bb7db13f2bd6b44af65c7c2b969b8efafc9339866b7a'}}],
     'controls': {'aa': {'present': False,
                         'comparison': None,
                         'not_applicable_reason': 'Exact complete finite relation equality is primary; no noisy '
                                                  'performance comparison or p-value.'},
                  'positive': {'present': False,
                               'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'Archived A2norm-only descriptors are checked as known '
                                                        'subset certificates; software positives independently '
                                                        'exercise both direct engines.'},
                  'negative': {'present': False,
                               'arm': None,
                               'null_population': None,
                               'not_applicable_reason': 'Full independent miss/hit, pair/query, duplicate, row, '
                                                        'rank/kernel and admission corruption checks; no native '
                                                        'zero outcome presumed.'}},
     'variable_ledger': {'independent': [{'name': 'direct_method', 'levels': ['enumeration', 'pair_table']},
                                         {'name': 'original_curve', 'levels': []}],
                         'factors': [{'name': 'curve_base_sources_preprocessing',
                                      'treatment': 'fixed',
                                      'value': 'Originaltwo '
                                               'p4099curves,16atoms/15unknowns,source64,historical97/rank13 '
                                               'and67/rank9 M only',
                                      'how': 'Frozen original input identities, no new draws or A2rank '
                                             'augmentation.'},
                                     {'name': 'semantic_set',
                                      'treatment': 'fixed',
                                      'value': 'D={(s,j<k<l,eps∈{±1}³):sum eps*B=sP}',
                                      'how': 'Allsources including cover-unliftable cases; no repeats, all sign '
                                             'choices.'},
                                     {'name': 'elimination_order',
                                      'treatment': 'fixed',
                                      'value': 'Same canonical(source_scalar,triple,signs) roworder',
                                      'how': 'Both complete sets sorted identically before '
                                             'certification/projection/normalization/rank.'},
                                     {'name': 'archived_A2',
                                      'treatment': 'fixed',
                                      'value': 'Only norm_completed=true witnesses,92/105, embedded with '
                                               'sourcehashes',
                                      'how': 'Subset diagnostic only; smooth five-term rows excluded; never '
                                             'require D=A2 or compare oldtimings.'},
                                     {'name': 'host',
                                      'treatment': 'measured',
                                      'how': 'One process/thread; all clocks diagnostic, wall_valid=false.'}],
                         'comparisons': [{'id': 'C-direct',
                                          'arms': ['enumeration', 'pair_table'],
                                          'differs_in': ['direct_method'],
                                          'design': 'one_factor',
                                          'threshold': 'Exact descriptor, row, normalized affine and dense-rank '
                                                       'equality plus complete native replay; no cost advantage '
                                                       'threshold.'}],
                         'aa_not_applicable': 'Exact deterministic full finite set equality.',
                         'crosses_map': False},
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Originalcurve order, enumeration then pair_table, independent replay '
                                           'per curve. Each direct arm charges its own setup/sign/source and '
                                           'collection work; shared process costs once.',
                       'seed_derivation': {'method': 'explicit_list',
                                           'seeds': [0],
                                           'nonce': None,
                                           'note': 'Retained materialized seed0 source shuffle, no new draw.'},
                       'instance_sampling': {'rule': 'Both unchanged originalcurves and fulloriginal64source '
                                                     'arrays. No liftability or success filtering, no new '
                                                     'targets.',
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
     'metrics': {'primary': [{'id': 'attempts',
                              'name': 'attempts',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Method units:286720enumerationdescriptors or2048MITMqueries; unlike '
                                            'units, no attempt-rate ratio.',
                              'source': 'analysis.json cells[].attempts',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'pair_entries',
                              'name': 'pair entries',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'All signedpair table entries:480 for pair_table, not '
                                            'applicable/zero for enumeration.',
                              'source': 'analysis.json cells[].pair_entries',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'accepted_witnesses',
                              'name': 'accepted witnesses',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Complete unique canonical signed distinct-three-sum rows.',
                              'source': 'analysis.json cells[].accepted_witnesses',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'distinct_equations',
                              'name': 'distinct equations',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Distinct normalized original-column affine equations.',
                              'source': 'analysis.json cells[].distinct_equations',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'new_rank',
                              'name': 'new rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'New direct rows coefficient rank.',
                              'source': 'analysis.json cells[].new_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'combined_rank',
                              'name': 'combined rank',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Historical M plus direct rows rank.',
                              'source': 'analysis.json cells[].combined_rank',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'rank_gain',
                              'name': 'rank gain',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Combined minus historical rank on same fifteen projected columns.',
                              'source': 'analysis.json cells[].rank_gain',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'base_nullity_after',
                              'name': 'base nullity after',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Fifteen original columns minus combined rank.',
                              'source': 'analysis.json cells[].base_nullity_after',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'},
                             {'id': 'nonzero_old_kernel_syndromes',
                              'name': 'nonzero old kernel syndromes',
                              'unit': 'objects',
                              'kind': 'exact',
                              'definition': 'Direct row action on complete historical right kernel.',
                              'source': 'analysis.json cells[].nonzero_old_kernel_syndromes',
                              'aggregation': 'per_row',
                              'resolution': '1',
                              'uncertainty': 'none_exact'}],
                 'secondary': []},
     'measurement': {'isolation_required': 'none',
                     'warmups': 0,
                     'order': 'sequential',
                     'clock': 'counted',
                     'counters': ['Fp.*',
                                  'Fr.*',
                                  'logical descriptors/queries/pair inserts/lookups/bucket '
                                  'entries/certificates/hash updates'],
                     'record': ['Host/source/ownership facts',
                                'disjoint producer innerphase counters/clocks',
                                'separate unmetered arithmetic replay clock',
                                'pair table and complete query/miss/hit certificates',
                                'archived A2subset provenance'],
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
     'stopping_rules': [{'rule': 'Both originalcurves:286720enumerationdescriptors,480signedpairs,2048queries '
                                 'each; no rankstop. Full separate E and pair/query replay.',
                         'kind': 'fixed_n',
                         'preregistered': True},
                        {'rule': 'maxretainedrows2048/maxpairentries4096 are protective refusals with retained '
                                 'prefixes, never truncation. Wrong set/query/certificate or changed source '
                                 'invalidates completeness.',
                         'kind': 'invalidation',
                         'preregistered': True},
                        {'rule': 'Oneprocess/thread,2GiBmemory/21600sCPU+wall watchdog; protective hostlimits, '
                                 'not research spend cap.',
                         'kind': 'budget',
                         'preregistered': True}],
     'invalidation_rules': ['Changed original curve/base/source/M, dropped table bucket/infinity/repeatedatom '
                            'filter or failed complete independent replay invalidates completeness.',
                            'D equality is required only between the two direct engines; archived A2norm-only '
                            'subset is different and need not exhaust D.',
                            'Unknown/incomplete cells remain null; collection snapshots survive analysis '
                            'failure.',
                            'Never sum outerprocess clocks with innerphase components or Fp/Fr/logical counts '
                            'into invented complete S.'],
     'decision_rule': {'text': 'Report exact direct relation equivalence, separate archivednorm subset, '
                               'same-column affine ranks and method-specific counted work/stage diagnostics. No '
                               'novelty, speedup, asymptotic or officialstatus claim.',
                       'comparison_ids': ['C-direct'],
                       'threshold': 'Complete independent E/table/query/affine/kernel replay and exact direct '
                                    'set equality.',
                       'statistic': 'Exact finite descriptors and normalized equations.',
                       'interval': 'none_exact',
                       'multiple_comparison_correction': 'none',
                       'effect_size_measure': 'None; diagnostic/control and local implementation observations '
                                              'only.',
                       'verdict_vocabulary': ['completed_within_scope', 'invalid_measurement', 'inconclusive']},
     'analysis_plan': {'script': {'path': 'analyze.py',
                                  'sha256': '45cfe0ad80b8d683cccbd915a0859a50491f0aec0fdf4deb6d8bae22cf24730e'},
                       'inputs': ['<run>/execution.json', '<run>/raw/*.json[.gz]', '<run>/raw/*.jsonl[.gz]'],
                       'outputs': ['<run>/analysis.json', '<run>/export.json'],
                       'blinded': False,
                       'frozen_before_data': True},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'review_schema': 'experiment.review/v1',
                   'graphs': ['Per-curve direct set/rank agreement and separately labelled stage/counter '
                              'vectors, archivednorm subset coverage, unknowns.'],
                   'report_dir': 'reports/<fresh-run>/'},
     'inadmissible': ['Freeze/release before exact source commitment or run before '
                      'actualS3gate/explicitrootrelease.',
                      'Claiming generic pair tables revive closed_obstructed '
                      'LEAD-ICP-generic-table-decomposition, novelty or subrho progress.',
                      'Requiring direct rows to equal all A2smooth/norm rows or claiming matched '
                      'archivedA2cost/fullS.',
                      'Comparing descriptor and query attempt counts as identical work units.',
                      'Omitting cold pair build/source/sign/setup, bucket scanning, '
                      'certification/normalization/elimination/kernel costs or summing nested clocks.'],
     'literature': [{'ref': 'knowledge/leads/ecdlp/ic-prime/LEAD-ICP-generic-table-decomposition.yaml;src/crypto_autoresearcher/index_calculus/README.md '
                            'section3',
                     'provenance': 'internal',
                     'claim': 'Existing generic enumeration/table decomposition has a recorded cost obstruction '
                              'and measured above-rho behavior; A3is a semantic diagnostic/control, not a '
                              'revived attack lead.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; canonicalYAML and '
                                    'underlyinglocal/crypto sources read.'},
                    {'ref': 'https://www.shoup.net/papers/dlbounds1.pdf Theorem1; '
                            'https://henrycg.com/pubs/eurocrypt18discrete/',
                     'provenance': 'retrieved',
                     'claim': 'Generic no-advice lower bound and advice/online tradeoff must be kept distinct; '
                              'no new bound or lower-bound escape is claimed.',
                     'verified_by': '/root/c1_execution_contract,2026-10-30; ShoupTheorem1 viaPDF/OCR and '
                                    'CGKauthorabstract read; fullCGKPDF403.'}],
     'amendments': [],
     'freeze': {'status': 'draft',
                'protocol_sha256': None,
                'commit': None,
                'frozen_at': None,
                'filed_before_affected_data': None},
     'extensions': {'export_unit': 'Four separately executed direct arm/curve methods in one supervised physical '
                                   'panel; not nested semantic duplicates. Independent verification resources '
                                   'once in backend.',
                    'model_verified': False,
                    'model_identity': None,
                    'checkpoint_semantics': 'Actual canonical S3 gate mandatory; no in-row restore; retries use '
                                            'fresh directories and do not retain clock validity.',
                    'counter_coverage': 'Producer Fp/Fr calls and namedlogical operations checked for '
                                        'conservation. Python '
                                        'hashing/sorting/comparison/serialization/interpreter, allocator/OS '
                                        'costs and independent arithmetic replay operations are not completely '
                                        'counted; clocks sharedhostdiagnostics only. No completeS/rho '
                                        'comparison.',
                    'verification_scope': 'Separate full E enumeration, all pair/query certificates, '
                                          'denseaffine/kernel and originalA2norm subset check; not archivedC '
                                          'replay, producerfieldcounteraudit or staffed scientificreview.',
                    'official_status_transition': False,
                    'selection': {'rank': 1,
                                  'scope': 'Next bounded exact diagnostic/control of A2 and generic '
                                           'localcollector implementation',
                                  'existing_lead': 'LEAD-ICP-generic-table-decomposition',
                                  'disposition_at_start': 'closed_obstructed',
                                  'changes_disposition': False},
                    'not_applicable': ['C lifting', 'polynomial extraction', 'outside-column cancellation']}}
    data=json.loads(INPUTS.read_text());cells=data['cells']
    if (data.get('schema')!='prime-field-direct-inputs/v1' or len(cells)!=2 or data.get('arms')!=PARAMETERS['arms'] or
        sorted((c['fixture']['p'],c['fixture']['a'],c['fixture']['b'],c['fixture']['r']) for c in cells)!=[(4099,2,13,4021),(4099,2,16,4111)] or
        any(len(c['fixture']['factor_base'])!=16 or c['source_order']!=c['fixture']['width_binding']['source_order'] or len(c['source_order'])!=64 or
            len(c['preprocessing_rows'])!=(97 if c['fixture']['b']==13 else 67) or any(r.get('norm_completed') is not True for r in c['archived_norm_rows']) for c in cells)):
        raise ValueError('original complete two-curve direct/archived-norm panel required')
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
        value = dict(schema='prime-field-a3-root-release/v1',execution_authorized=True,
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
