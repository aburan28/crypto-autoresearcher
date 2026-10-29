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
            self.assertEqual(bundle['runs'][0]['run_id'],'RUN-FIXTURE')
            self.assertEqual(bundle['protocol']['protocol_id'],'TEST-F11')
            linked={Path(item['path']).name for item in bundle['files']}
            self.assertTrue({'manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json'}<=linked)
            self.assertTrue(findings)  # Deliberate skeletal fixture remains unqualified.


if __name__=='__main__':unittest.main()
