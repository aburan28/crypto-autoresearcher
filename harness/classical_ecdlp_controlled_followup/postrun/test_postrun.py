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
            def verifier(raw,evidence,plan,interface,emit=None):
                called.append(True)
                self.assertTrue(evidence['termination_ack']['acknowledged'])
                self.assertEqual(c.sha_bytes(bytes.fromhex(plan['public_cohort_bytes_hex'])),plan['provenance']['cohort_sha256'])
                return {'status':'checked','observed':plan['expected'],'wall_valid':False,'counter_replay_qualified':False}
            destination=Path(root)/'postrun';result=run_postrun.run(out,destination,os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=verifier,interface=fixture()[2])
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
            destination=Path(root)/'postrun';result=run_postrun.run(out,destination,os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'),verifier=forbidden,interface=fixture()[2])
            self.assertEqual(result['status'],'incomplete');self.assertTrue(result['errors'])
            self.assertTrue((destination/'report.pdf').is_file())
    def test_real_host_api_f11_seal_bsgs_uniform_packed_null(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root);evidence=c.custody_for(out/'collected',record)
            repo=Path(os.environ.get('CONTROLLED_REPO','/workspace/classical-ecdlp-validation-ready'))
            host=c.module(repo/c.PREFIX/'host/verify.py','verify')
            reference=c.module(repo/c.PREFIX/'host/reference.py','reference')
            plan=c.read(out/'collected/host-plan.json');plan['public_cohort_bytes_hex']=(out/'collected/public-cohort.json').read_bytes().hex()
            checked=host.verify_bundle(out/'collected/raw',evidence,plan,fixture()[2])
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


if __name__=='__main__':unittest.main()
