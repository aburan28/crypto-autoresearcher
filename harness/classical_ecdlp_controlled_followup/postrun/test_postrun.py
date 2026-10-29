"""Postrun fixture exports retain complete/partial states; host import cannot be early."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
import os
import subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import controller as c
from test_transport import mocked_run,fixture
run_postrun=c.module(Path(__file__).with_name('run_postrun.py'),'_test_controlled_postrun')


class PostrunTests(unittest.TestCase):
    def test_complete_fixture_and_pdf(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root);called=[]
            def verifier(raw,evidence,plan,interface,emit=None,authenticated_inputs=None):
                called.append(True)
                self.assertTrue(evidence['termination_ack']['acknowledged'])
                self.assertEqual(c.sha_bytes(bytes.fromhex(plan['public_cohort_bytes_hex'])),plan['provenance']['cohort_sha256'])
                return {'status':'checked','observed':plan['expected'],'wall_valid':False,'counter_replay_qualified':False}
            destination=Path(root)/'postrun';result=run_postrun.run(out,destination,os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=verifier,interface=fixture()[2],inner_transport=True,fixture_law='fixed-F11-calibration/v1')
            self.assertEqual(result['status'],'complete');self.assertEqual(called,[True])
            tool=Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))/'tools/experiment_protocol.py'
            checked=subprocess.run([sys.executable,str(tool),'validate',str(destination/'export.json'),'--verify-files'],capture_output=True,text=True)
            self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)
            validation=c.read(destination/'export.validation.json')
            self.assertTrue(validation['schema_compliant'])
            self.assertFalse(validation['protocol_qualified'])  # No scientific fixture protocol is invented.
            for name in ['export.json','analysis.json','report.md','report.svg','report.pdf']:
                self.assertTrue((destination/name).is_file())
    def test_early_host_forbidden_and_failure_export_pdf(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root,True)
            def forbidden(*args,**kwargs):raise AssertionError('early host verification')
            destination=Path(root)/'postrun';result=run_postrun.run(out,destination,os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=forbidden,interface=fixture()[2],inner_transport=True,fixture_law='fixed-F11-calibration/v1')
            self.assertEqual(result['status'],'incomplete');self.assertTrue(result['errors'])
            self.assertTrue((destination/'report.pdf').is_file())
    def test_real_host_api_f11_seal_bsgs_uniform_packed_null(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root);evidence=c.custody_for(out/'collected',record)
            repo=Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))
            host=c.module(Path(__file__).resolve().parents[1]/'host/verify.py','verify')
            reference=c.module(repo/c.PREFIX/'host/reference.py','reference')
            plan=c.read(out/'collected/host-plan.json');plan['public_cohort_bytes_hex']=(out/'collected/public-cohort.json').read_bytes().hex()
            checked=host.verify_bundle(out/'collected/raw',evidence,plan,fixture()[2],authenticated_inputs={'workload_law':'fixed-F11-calibration/v1','max_jsonl_line_bytes':1<<20})
            self.assertEqual(checked['status'],'checked')
            seal=host.open_sealed(out/'collected/raw',evidence)
            oracle=host.Oracle(seal,{'p':11,'a':1,'b':6,'r':13},[2,7])
            self.assertEqual(oracle.logs[(7,2)],7)
            solved=reference.BSGS(seal,oracle.group,oracle.base).solve((7,2))
            self.assertEqual(solved['scalar'],7)
            uniform=reference.uniform_list(seal,oracle.group,oracle.base,(7,2),1,bytes(32))
            self.assertEqual(uniform['effective_M'],1)
            mask={point:oracle.evaluate(point,-2,-1,1)['bit'] is not None for point in oracle.points}
            null=reference.mask_reference(seal,oracle,mask,bytes(32),arm_id='circuit2.a1')
            self.assertEqual(null['draw_count'],1023)
            self.assertEqual(null['status'],'complete')
            stats=reference.retained_bank_statistics(seal,oracle,null,[7],[7],observed=None)
            self.assertEqual(len(stats['reference_statistics']),1023)
            destination=Path(root)/'references';destination.mkdir()
            run_postrun.run_references(host,reference,out/'collected/raw',evidence,plan,c.read(out/'collected/public-cohort.json'),bytes(32),destination,1<<20)
            self.assertTrue((destination/'calibration.json').is_file())
            self.assertTrue((destination/'references.json').is_file())

    def test_zero_data_source_failure_report_without_fabricated_export(self):
        import driver
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)/'supervisor';out.mkdir()
            driver.run(root,{'inputs':{}},out,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
            destination=Path(root)/'failed-postrun'
            result=run_postrun.run(out,destination,os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=lambda *a,**k:(_ for _ in ()).throw(AssertionError('early host')))
            self.assertEqual(result['status'],'incomplete')
            self.assertTrue((destination/'report.pdf').is_file())
            self.assertFalse((destination/'export.json').exists())
            self.assertFalse(c.read(destination/'export.validation.json')['schema_compliant'])

    def test_actual_decoder_schema_without_curve_id(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root)
            interface=fixture()[2]
            cell=interface['embedded_deterministic_F11_records']['decoder-cell']
            self.assertNotIn('curve_id',cell)
            path=out/'collected/raw/decoder-cells.jsonl';path.chmod(0o644);path.write_bytes(c.canonical(cell)+b'\n')
            summary=run_postrun.analysis.summarize(out/'collected/raw')
            row=summary['per_curve_six_cell'][0]
            self.assertEqual(row['curve_id'],'fixture-F11');self.assertEqual(row['attempts'],1)
            self.assertIn('decoder_component_batch_cost_per_success',row)
            self.assertNotIn('batch_cost_per_success',row)
            self.assertEqual(len(summary['physical_trace_components_once']),1)

    def test_partial_jsonl_detected_no_padding(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'partial';p.write_bytes(b'{"a":1}')
            with self.assertRaises(ValueError):list(run_postrun.analysis.rows(p,1024))
            p.write_bytes(b'{}\n{}\n');self.assertEqual(len(list(run_postrun.analysis.rows(p,1024))),2)
            with self.assertRaises(ValueError):list(run_postrun.analysis.rows(p,1))


    def test_production_wrong_pins_before_module_or_entropy(self):
        import copy
        with tempfile.TemporaryDirectory() as root:
            out,record,_=mocked_run(root)
            expected=copy.deepcopy(record['plan'])
            invocation=c.read(out/'config.json')
            plan=c.read(out/'collected/host-plan.json')
            plan['provenance'].update(protocol_sha256='ff'*32,source_fingerprint='ee'*32)
            c.write(Path(root)/'wrong-plan.json',plan)
            f=out/'collected/host-plan.json';f.chmod(0o644);f.write_bytes(c.canonical(plan)+b'\n')
            for entry in record['files']:
                if entry['path']=='host-plan.json':entry.update(size=f.stat().st_size,sha256=c.sha_file(f))
            for name,value in [('controller-receipt.json',record),('custody.json',c.custody_for(out/'collected',record))]:
                p=out/name;p.unlink();c.write(p,value)
            # Ordinary production branch, no injected verifier and no fixture law.
            with patch.object(c,'make_plan',return_value=(expected,invocation,{},{})),patch.object(run_postrun.os,'urandom',side_effect=AssertionError('entropy reached')),patch.object(c,'module',wraps=c.module) as modules:
                result=run_postrun.run(out,Path(root)/'postrun',os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),inner_transport=True)
            self.assertEqual(result['status'],'incomplete')
            self.assertIn('independent invocation',result['errors'][0]['message'])
            self.assertFalse(any(call.args[1] in {'verify','reference'} for call in modules.call_args_list))

    def test_fixed_injected_seam_wrong_pins_before_verifier(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,_=mocked_run(root)
            plan=c.read(out/'collected/host-plan.json')
            plan['provenance'].update(protocol_sha256='ff'*32,source_fingerprint='ee'*32)
            # Authentication is checked directly with genuine fixture invocation pins.
            with self.assertRaisesRegex(ValueError,'worker provenance'):
                run_postrun.authenticate_inputs(out,root,record,plan,'fixed-F11-calibration/v1')

    def test_default_inner_tree_is_rejected_before_verifier(self):
        with tempfile.TemporaryDirectory() as root:
            out,_,_=mocked_run(root)
            called=[]
            result=run_postrun.run(out,Path(root)/'postrun',os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=lambda *a,**k:called.append(True))
            self.assertEqual(result['status'],'incomplete');self.assertEqual(called,[])


    def test_supervisor_rejections_before_import_entropy_verifier(self):
        import driver,shutil
        for mutant in ('archive','missing-member','duplicate-receipt','zero-data'):
            with self.subTest(mutant=mutant),tempfile.TemporaryDirectory() as root:
                supervisor=Path(root)/'supervisor';supervisor.mkdir()
                if mutant=='zero-data':
                    driver.run(root,{'inputs':{}},supervisor,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
                else:
                    source,record,_=mocked_run(root)
                    c.write(Path(root)/'protocol.json',{'protocol_id':'EXP-FIXTURE'})
                    def completed(repo,cfg,dest,sdk=None,supervisor_identity=None):
                        record['supervisor_identity']=supervisor_identity
                        shutil.copytree(source,dest)
                        for name,value in [('protocol.json',{'protocol_id':'EXP-FIXTURE'}),('controller-receipt.json',record)]:
                            (dest/name).unlink();c.write(dest/name,value)
                        return record
                    with patch.object(c,'run',side_effect=completed):
                        driver.run(root,{'inputs':{'protocol':{'path':'protocol.json'}}},supervisor,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
                    if mutant=='archive':(supervisor/'modal-evidence.tar.gz').write_bytes(b'CORRUPT-ARCHIVE')
                    if mutant=='missing-member':(supervisor/'modal/controller-receipt.json').unlink()
                    if mutant=='duplicate-receipt':
                        raw=c.read(supervisor/'raw-result.json');raw['controller']['engine_execs']=99
                        (supervisor/'raw-result.json').unlink();c.write(supervisor/'raw-result.json',raw)
                with patch.object(run_postrun.os,'urandom',side_effect=AssertionError('early entropy')),patch.object(c,'module',wraps=c.module) as modules:
                    result=run_postrun.run(supervisor,Path(root)/'postrun',os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))
                self.assertEqual(result['status'],'incomplete')
                self.assertFalse(any(call.args[1] in {'verify','reference'} for call in modules.call_args_list))
                # Same default production CLI path must exit1 with its failure report.
                cli=subprocess.run([sys.executable,str(Path(run_postrun.__file__)),'--out',str(supervisor),'--destination',str(Path(root)/'cli'),'--repo-root',os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready')],capture_output=True,text=True)
                self.assertEqual(cli.returncode,1,cli.stdout+cli.stderr)

    def test_paginated_all_rows_findings_calibration_reference_canaries(self):
        renderer=c.module(Path(__file__).with_name('render_report.py'),'_test_renderer_canaries')
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            rows=[{'curve_id':'F11-render-'+str(i),'cell':'t0.e0','successes':0,'attempts':1,'outcomes':{'UNDEFINED':1}} for i in range(20)]
            c.write(root/'analysis.json',{'per_curve_six_cell':rows})
            c.write(root/'calibration.json',{'CANARY_CALIBRATION':'present'})
            c.write(root/'references.json',{'CANARY_REFERENCE':'present','CANARY_COST':'zero costs retained','curves':[{'curve_id':'fixture-F11','null_file':'null-fixture.json','uniform_file':None}]})
            c.write(root/'null-fixture.json',{'CANARY_NULL':'support duplicates ties'})
            c.write(root/'postrun-result.json',{'status':'incomplete','errors':[{'message':'CANARY_FAILURE_RETAIN_ME'}],'export_findings':['CANARY_EXPORT']})
            c.write(root/'export.validation.json',{'findings':['CANARY_EXPORT'],'schema_compliant':False})
            with patch.object(os,'urandom',side_effect=AssertionError('renderer entropy forbidden')):renderer.render(root)
            readback=subprocess.run(['pdftotext',str(root/'report.pdf'),'-'],capture_output=True,text=True)
            self.assertEqual(readback.returncode,0)
            for canary in ('F11-render-0','F11-render-19','CANARY_FAILURE_RETAIN_ME','CANARY_CALIBRATION','CANARY_REFERENCE','CANARY_NULL','CANARY_COST','CANARY_EXPORT'):
                self.assertIn(canary,readback.stdout)


    def test_copied_static_input_and_manifest_mutants_before_host(self):
        import copy
        roles=('protocol','image_receipt','engine_plan','prior_exclusions','worker_manifest','host_manifest','engine_interface','host_interface')
        for role in roles:
            with self.subTest(role=role),tempfile.TemporaryDirectory() as root:
                out,record,_=mocked_run(root)
                static={name:{'fixture_role':name} for name in roles}
                for name,value in static.items():
                    p=out/(name+'.json')
                    if p.exists():p.unlink()
                    c.write(p,value)
                invocation={'inputs':{name:{'path':name+'.json','sha256':c.sha_file(out/(name+'.json'))} for name in roles}}
                invocation['inputs']['protocol']['sha256']=c.sha_file(out/'protocol.json')
                config=out/'config.json';config.unlink();c.write(config,invocation)
                worker={'provenance':{'protocol_sha256':invocation['inputs']['protocol']['sha256'],'source_fingerprint':record['plan']['source_fingerprint']}}
                mutant=out/(role+'.json');mutant.write_bytes(c.canonical({'mutated':True})+b'\n')
                with patch.object(c,'make_plan',return_value=(record['plan'],invocation,static,{})),patch.object(c,'source_payload',side_effect=AssertionError('source/host reached before copied binding')),patch.object(os,'urandom',side_effect=AssertionError('entropy reached')):
                    with self.assertRaisesRegex(ValueError,'copied input hash mismatch'):
                        run_postrun.authenticate_inputs(out,root,record,worker)

    def test_unified_export_keeps_allocated_run_and_supervisor_envelope(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,_=mocked_run(root)
            destination=Path(root)/'derived';destination.mkdir()
            c.write(destination/'analysis.json',{'per_curve_six_cell':[]})
            outer=Path(root)/'supervisor';outer.mkdir()
            for name in ['manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json']:(outer/name).write_bytes(b'fixture envelope member\n')
            repo=Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))
            ep=c.module(repo/'tools/experiment_protocol.py','_test_export_real')
            bundle,findings=run_postrun.make_export(ep,out,destination,record,{'status':'complete'},outer)
            self.assertEqual(bundle['runs'],[])  # Original-only calibration is no paired observation.
            self.assertEqual(bundle['protocol']['protocol_id'],'TEST-F11')
            linked={Path(item['path']).name for item in bundle['files']}
            self.assertTrue({'manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json'}<=linked)
            self.assertTrue(findings)  # Deliberate skeletal fixture remains unqualified.





def full_fixture_protocol():
    """Complete test-only contract; never the future scientific protocol."""
    return {'amendments': [],
     'analysis_plan': {'blinded': False,
                       'frozen_before_data': True,
                       'inputs': ['raw/traces.jsonl'],
                       'outputs': ['analysis.json'],
                       'script': None},
     'arms': [{'description': 'Actually retained original strict evaluator',
               'id': 'confirmation_original',
               'instrument': {'binary_sha256': None,
                              'build': [],
                              'commit': None,
                              'env': {},
                              'flags': {},
                              'repo': 'fixture-only',
                              'threads': 1},
               'parameters': {'method': 'original'},
               'role': 'baseline'},
              {'description': 'Actually retained incremental strict evaluator',
               'id': 'confirmation_incremental',
               'instrument': {'binary_sha256': None,
                              'build': [],
                              'commit': None,
                              'env': {},
                              'flags': {},
                              'repo': 'fixture-only',
                              'threads': 1},
               'parameters': {'method': 'incremental'},
               'role': 'candidate'}],
     'authors': ['TASK-20261029-b9f48c'],
     'claims': [{'class': 'out_of_scope',
                 'decided_by': [],
                 'id': 'C1',
                 'text': 'Export format and retained counts only; no scientific or performance claim.'}],
     'controls': {'aa': {'comparison': None,
                         'not_applicable_reason': 'No stochastic or timing inference; deterministic byte/count '
                                                  'custody fixture.',
                         'present': False},
                  'negative': {'arm': None,
                               'not_applicable_reason': 'No null population inference; '
                                                        'malformed/missing/duplicate export controls are unit '
                                                        'tests.',
                               'null_population': None,
                               'present': False},
                  'positive': {'arm': None,
                               'expected_detection': None,
                               'not_applicable_reason': 'No detection claim; actual strict recovery and shared '
                                                        'decoder outcomes are asserted separately.',
                               'present': False}},
     'created': '2026-10-29',
     'decision_rule': {'comparison_ids': ['format-pair'],
                       'effect_size_measure': 'none',
                       'interval': 'none',
                       'multiple_comparison_correction': 'none',
                       'statistic': 'Actual retained counts',
                       'text': 'Report actual format validation observations only.',
                       'threshold': 'No scientific criterion',
                       'verdict_vocabulary': ['inconclusive', 'invalid_measurement']},
     'execution': {'backend': 'local',
                   'checkpoint': {'after_restore': {'counted_units': 'valid', 'wall_time': 'invalid'},
                                  'grace_seconds': None,
                                  'interval_seconds': None,
                                  'policy': 'none',
                                  'restore_validation': 'none'},
                   'measurement_class': 'throughput',
                   'placement': {},
                   'queue': None,
                   'retries': {'infrastructure_only': True, 'max_attempts': 1},
                   'timeout_seconds': 120},
     'extensions': {'controlled_followup': {'export_arms': {'incremental': 'confirmation_incremental',
                                                            'original': 'confirmation_original'},
                                            'export_instance_id': 'candidate-vm',
                                            'export_observation_unit': 'paired-confirmation evaluator aggregate; '
                                                                       'both share one physical supervisor/VM',
                                            'export_row_id_rule': 'allocated_parent_RUN + .original / '
                                                                  '.incremental',
                                            'fixture_only': 'disclosed F11/F23 injected/export seam; not '
                                                            'production validation'}},
     'freeze': {'commit': None,
                'filed_before_affected_data': False,
                'frozen_at': None,
                'protocol_sha256': None,
                'status': 'draft'},
     'hypotheses': [],
     'inadmissible': ['Inventing method observations, successes, VM runs or counts.',
                      'Interpreting disclosed fixtures as production confirmation tiers.'],
     'invalidation_rules': ['Missing or partial paired method remains absent or excluded; no planned counts.',
                            'No wall-clock or worker counter replay qualification.'],
     'links': {'scope': 'Test-only disclosed deterministic F11/F23, no production tier or scientific protocol'},
     'literature': [{'claim': 'Export schema coverage, frozen source and failure retention contract',
                     'provenance': 'internal',
                     'ref': 'docs/experiment-protocol.md',
                     'verified_by': 'TASK-20261029-b9f48c'}],
     'measurement': {'clock': 'counted',
                     'counters': ['actual method primitive families'],
                     'isolation_required': 'none',
                     'order': 'sequential',
                     'record': ['source hash', 'actual retained counts'],
                     'timed_primary_justification': None,
                     'warmups': 0},
     'metrics': {'primary': [{'aggregation': 'sum',
                              'definition': 'Number of nonempty retained original/incremental strict attempt '
                                            'records, excluding calibration.',
                              'id': 'retained_attempts',
                              'kind': 'counted',
                              'name': 'actual paired attempts',
                              'resolution': '1',
                              'source': 'traces.jsonl method predicate_trace',
                              'uncertainty': 'none_exact',
                              'unit': 'retained attempt'}],
                 'secondary': []},
     'protocol_id': 'TEST-PAIRED-F11-F23',
     'question': 'Can actual paired evaluator observations be exported without duplicating a physical '
                 'invocation?',
     'randomization': {'arm_order': 'fixed',
                       'arm_order_reason': 'Deterministic source test, clocks invalid; original then incremental '
                                           'on identical public inputs.',
                       'blinding': {'analysis_labels_masked': False,
                                    'how': 'Source fixture has named methods, no inference.',
                                    'unmasked_at': None},
                       'instance_sampling': {'independent_of_arm': True,
                                             'rule': 'One fixed paired aggregate over disclosed F11/F23 targets, '
                                                     'no population sampling.'},
                       'seed_derivation': {'method': 'harness_drawn',
                                           'nonce': None,
                                           'note': 'Explicit fixture-only fixed00 nonce; no entropy. Production '
                                                   'public cohort nonce rule is unchanged.',
                                           'seeds': []}},
     'reporting': {'export_schema': 'experiment.export/v1',
                   'graphs': ['No scientific inference; raw count record'],
                   'report_dir': 'derived',
                   'review_schema': 'experiment.review/v1'},
     'repository': 'other',
     'sample_size': {'instances': 1,
                     'power': {'alpha': 0.05,
                               'correction': 'none',
                               'method': 'exact',
                               'min_attainable_two_sided_p': None,
                               'note': 'Format regression only; no power or scientific inference.',
                               'passes': True,
                               'rank_test_n': None,
                               'tests_in_family': 1},
                     'preflight_runtime': {'estimated_total_seconds': 1,
                                           'fixed_seconds': 0,
                                           'measured_on': 'Advisory test timeout estimate only; no benchmark.',
                                           'per_sample_seconds': 0,
                                           'threads': 1},
                     'replicates': 1,
                     'warmups': 0},
     'schema': 'experiment.protocol/v1',
     'stopping_rules': [{'kind': 'fixed_n',
                         'preregistered': True,
                         'rule': 'Stop after the disclosed two paired fixture attempts; retain missing/partial '
                                 'failures.'}],
     'study_dir': 'disclosed-fixture-only',
     'variable_ledger': {'aa_not_applicable': 'Deterministic format fixture; no timing inference.',
                         'comparisons': [{'id':'format-pair','arms':['confirmation_original','confirmation_incremental'],'differs_in':['method'],'design':'one_factor'}],
                         'crosses_map': False,
                         'factors': [{'how': 'Same actual paired confirmation traces and nonce00; no new targets '
                                             'or entropy.',
                                      'name': 'public inputs',
                                      'treatment': 'fixed',
                                      'value': 'disclosed F11/F23'}],
                         'independent': [{'levels': ['original', 'incremental'], 'name': 'method'}]},
     'version': 1}


def paired_export_fixture(root):
    """Actual disclosed arithmetic only, fixed public inputs, no SDK or draw.

    This direct exporter seam is not production host verification. Production
    still requires its authenticated 48-curve frozen workload before labels.
    """
    import engine
    from constructor import prepare
    from curve import Curve
    root=Path(root);out=root/'paired';raw=out/'collected/raw';raw.mkdir(parents=True)
    destination=root/'derived';destination.mkdir()
    ep=c.module(Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))/'tools/experiment_protocol.py','_paired_export_protocol')
    protocol=full_fixture_protocol()
    script=Path(run_postrun.__file__).with_name('analysis.py')
    protocol['analysis_plan']['script']={'path':str(script),'sha256':c.sha_file(script)}
    c.write(out/'protocol.json',protocol)
    ep.freeze(out/'protocol.json',None,False)
    traces=[];cells=[];setups=[];public=[]
    for name,model,base,target,alpha,beta,a in [
        ('F11',{'p':11,'a':1,'b':6,'r':13},(2,7),(7,2),1,-4,5),
        ('F23',{'p':23,'a':11,'b':5,'r':17},(5,22),(5,22),-2,-1,1)]:
        curve=Curve(model['p'],model['a'],model['b']);prepared=prepare(model,curve.multiply(base,a),{'kind':'candidate','alpha':alpha,'beta':beta})
        pair=engine.paired_attempt(prepared,base,target,a,1);tid='disclosed-'+name+'/paired'
        traces.append(engine.record('trace',trace_id=tid,curve_id='disclosed-'+name,target_id='target',target=list(target),arm_id='fixture',base_multiplier=a,target_multiplier=1,draw=None,original=pair['original'],incremental=pair['incremental'],equal=True))
        cells.extend(engine.record('decoder-cell',trace_id=tid,cell_id=tid+f"/t{x['radius']}.e{x['erasure_cap']}",**x) for x in pair['cells'])
        setups.append({'curve_id':'disclosed-'+name,'arm_id':'fixture','setup_reason':prepared.setup_reason,'counts':{'common':curve.counter.snapshot(),'setup':prepared.setup_counts}})
        public.append({'curve_id':'disclosed-'+name,'model':model,'base':list(base),'targets':[{'target_id':'target','point':list(target)}]})
    # Actual original-only calibration work stays separate from paired totals.
    _,calibration=engine.ungated_attempt(prepared,base,target,a,1,True)
    traces.append({**traces[-1],'trace_id':'disclosed-F23/calibration','original':calibration,'incremental':None,'equal':None})
    for name,values in [('traces',traces),('decoder-cells',cells),('setups',setups),('single-points',[])]:
        (raw/(name+'.jsonl')).write_bytes(b''.join(c.canonical(x)+b'\n' for x in values))
    c.write(out/'collected/public-cohort.json',{'nonce':'00'*32,'curves':public})
    c.write(out/'collected/host-plan.json',{'paired_trace_ids':[t['trace_id'] for t in traces[:2]]})
    record={'status':'complete','engine_execs':1,'vm_creates':1,'sandbox_id':'sb-DISCLOSED-ONLY','files':[],
        'supervisor_identity':{'experiment_id':protocol['protocol_id'],'run_id':'RUN-DISCLOSED-ONLY'},
        'plan':{'limits':{'max_jsonl_line_bytes':1<<20}}}
    c.write(out/'controller-receipt.json',record)
    c.write(destination/'analysis.json',run_postrun.analysis.summarize(raw))
    return ep,out,destination,record,traces


class PairedExportTests(unittest.TestCase):
    def test_complete_frozen_protocol_actual_paired_f11_f23(self):
        with tempfile.TemporaryDirectory() as root:
            ep,out,dest,record,traces=paired_export_fixture(root)
            protocol=c.read(out/'protocol.json')
            self.assertEqual(ep.schema_errors(protocol,'experiment.protocol/v1'),[])
            self.assertEqual(ep.lint_protocol(protocol,out),[])
            bundle,findings=run_postrun.make_export(ep,out,dest,record,{'status':'complete'})
            self.assertEqual(findings,[])
            self.assertEqual(ep.schema_errors(bundle,'experiment.export/v1'),[])
            self.assertEqual(ep.lint_export(bundle,protocol,dest,True),[])
            self.assertEqual(len(bundle['runs']),2);self.assertEqual(record['vm_creates'],1)
            self.assertEqual(bundle['flow']['completed'],2)
            self.assertEqual({r['backend_ref'] for r in bundle['runs']},{'RUN-DISCLOSED-ONLY'})
            self.assertEqual({r['worker'] for r in bundle['runs']},{'sb-DISCLOSED-ONLY'})
            for row,method in zip(bundle['runs'],('original','incremental')):
                self.assertEqual(row['run_id'],'RUN-DISCLOSED-ONLY.'+method)
                self.assertEqual(row['seed'],'00'*32)
                counted=row['measurements']['counted'];self.assertEqual(counted['retained_attempts'],2)
                self.assertEqual(counted['retained_predicate_queries'],sum(len(t[method]['predicate_trace']) for t in traces[:2]))
                self.assertEqual(counted['strict_recovered_events'],sum(t[method]['status']=='RECOVERED' for t in traces[:2]))
                self.assertEqual(counted['unique_targets_retained'],2)
                self.assertEqual(counted['unique_targets_recovered'],len({(t['curve_id'],t['target_id']) for t in traces[:2] if t[method]['status']=='RECOVERED'}))
                self.assertFalse(row['measurements']['wall_valid'])
                for family in traces[0][method]['counts']:
                    for primitive in traces[0][method]['counts'][family]:
                        self.assertEqual(row['measurements']['counters'][family+'/'+primitive],sum(t[method]['counts'].get(family,{}).get(primitive,0) for t in traces[:2]))
                self.assertFalse(any(k.startswith(('setup/','common/','wrapper/')) for k in row['measurements']['counters']))
            self.assertEqual(len(run_postrun.analysis.summarize(out/'collected/raw')['per_curve_six_cell']),12)
            self.assertNotEqual(traces[1]['original']['status'],'RECOVERED')
            cells=list(run_postrun.analysis.rows(out/'collected/raw/decoder-cells.jsonl',1<<20))
            self.assertEqual(next(x for x in cells if x['cell_id']=='disclosed-F23/paired/t2.e2')['status'],'RECOVERED')
            c.write(dest/'export.json',bundle)
            tool=Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))/'tools/experiment_protocol.py'
            for args in [('validate',str(out/'protocol.json')),('check-export',str(dest/'export.json'),'--protocol',str(out/'protocol.json'),'--verify-files')]:
                checked=subprocess.run([sys.executable,str(tool),*args],capture_output=True,text=True)
                self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)

    def test_missing_partial_zero_and_duplicate_actual_work(self):
        import copy
        for mutant in ('missing-method','unexecuted','partial-query','missing-trace','duplicate-trace','zero-start'):
            with self.subTest(mutant=mutant),tempfile.TemporaryDirectory() as root:
                ep,out,dest,record,traces=paired_export_fixture(root)
                if mutant=='missing-method':
                    for t in traces[:2]:t['incremental']=None
                if mutant=='unexecuted':
                    for t in traces[:2]:t['incremental']['predicate_trace']=[]
                if mutant=='partial-query':traces[0]['incremental']['predicate_trace'].pop()
                if mutant=='missing-trace':traces.pop(0)
                if mutant=='duplicate-trace':traces.append(copy.deepcopy(traces[0]))
                if mutant=='zero-start':record['engine_execs']=0
                (out/'collected/raw/traces.jsonl').write_bytes(b''.join(c.canonical(t)+b'\n' for t in traces))
                bundle,findings=run_postrun.make_export(ep,out,dest,record,{'status':'incomplete'})
                self.assertTrue(findings,mutant)
                self.assertFalse(any(r['status']=='succeeded' for r in bundle['runs']))
                if mutant in ('missing-method','unexecuted'):self.assertEqual([r['arm'] for r in bundle['runs']],['confirmation_original'])
                if mutant=='zero-start':self.assertEqual(bundle['runs'],[])
                if mutant=='partial-query':self.assertEqual(bundle['runs'][1]['measurements']['counted']['retained_predicate_queries'],10)

    def test_unchanged_checker_rejects_duplicate_missing_padded_cells_and_file_mutant(self):
        import copy
        with tempfile.TemporaryDirectory() as root:
            ep,out,dest,record,_=paired_export_fixture(root);protocol=c.read(out/'protocol.json')
            correct,findings=run_postrun.make_export(ep,out,dest,record,{'status':'complete'});self.assertEqual(findings,[])
            for mutant,reason in [('duplicate-id','duplicate run_id'),('duplicate-cell','duplicate execution cell'),('missing-method','protocol arms with no run'),('padded','measured rows')]:
                value=copy.deepcopy(correct)
                if mutant=='duplicate-id':value['runs'][1]['run_id']=value['runs'][0]['run_id']
                if mutant=='duplicate-cell':value['runs'][1]['arm']=value['runs'][0]['arm']
                if mutant=='missing-method':value['runs'].pop()
                if mutant=='padded':value['runs'].append(copy.deepcopy(value['runs'][0]))
                value['flow']=ep.compute_flow(value['runs'])
                self.assertTrue(any(reason in x for x in ep.lint_export(value,protocol,dest,True)),mutant)
            (out/'collected/raw/traces.jsonl').write_bytes(b'changed\n')
            self.assertTrue(any('file changed since export' in x for x in ep.lint_export(correct,protocol,dest,True)))


if __name__=='__main__':unittest.main()
