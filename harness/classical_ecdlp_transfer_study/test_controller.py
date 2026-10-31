"""Synthetic composition checks; no account calls or native solver execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import tarfile
import io
from types import SimpleNamespace
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/classical-ecdlp-validation-ready')
spec = importlib.util.spec_from_file_location('transfer_controller_test_subject', HERE/'controller.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


SYNTHETIC_EXPECTED = {'candidate_attempts_planned':80,'baseline_attempts_planned':160,
                      'total_attempts_planned':240,'fixture_count_planned':2,
                      'arm_ids':['synthetic-arm-'+str(i) for i in range(11)]}


def synthetic_plan(started=False):
    return {**SYNTHETIC_EXPECTED,
            'measurement_started':started,'fresh_cohort_generated':False,'candidate_attempts_executed':0,
            'provider_runtime_requirements_enforced':True,
            'runtime_facts':{'resuid':[1000,1000,1000],'resgid':[1000,1000,1000],
                'supplementary_groups':[],'environment_values_collected':False,
                'input_access':{name:{'exists':True,'writable':False}
                    for name in C.SOURCE_NAMES | {'protocol','source_manifest','provider_context','prior_exclusions'}}}}


class CommittedSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root/'package'
        self.package.mkdir()
        for name in C.SOURCE_NAMES:
            body = (HERE/'controller.py').read_bytes() if name == 'controller.py' else b'# synthetic module\n'
            (self.package/name).write_bytes(body)
        # Git-object boundary is mocked. This task performs no Git commands.
        self.committed={p.name:p.read_bytes() for p in self.package.iterdir()}
        self.manifest = {'schema':C.SOURCE_SCHEMA, 'source_revision_c':'c'*40,
                         'source_prefix':'package', 'native_source_a':C.NATIVE_A, 'image_adapter_source_b':C.IMAGE_B,
                         'files':{p.name:C.sha_file(p) for p in self.package.iterdir()}}
        self.path = self.root/'source-manifest.json'
        self.path.write_text(json.dumps(self.manifest))
        real = C.transport(REPO)
        patchers=[mock.patch.object(C,'transport',return_value=real),
                  mock.patch.object(C.subprocess,'run',side_effect=self.git_ancestor),
                  mock.patch.object(C.subprocess,'check_output',side_effect=self.git_blob)]
        for patch in patchers:patch.start();self.addCleanup(patch.stop)

    def git_ancestor(self,argv,**kwargs):
        self.assertEqual(argv,['git','merge-base','--is-ancestor','c'*40,'HEAD'])
        return SimpleNamespace(returncode=0)

    def git_blob(self,argv,**kwargs):
        self.assertEqual(argv[:2],['git','show'])
        prefix='c'*40+':package/'
        self.assertTrue(argv[2].startswith(prefix))
        return self.committed[argv[2][len(prefix):]]

    def test_exact_seven_module_committed_closure_and_working_drift_refusal(self):
        manifest, raw, files = C.source_payload(self.root,self.path)
        self.assertEqual(set(files),C.SOURCE_NAMES)
        self.assertEqual(C.sha(raw),C.sha(self.path.read_bytes()))
        (self.package/'compute.py').write_text('# changed working source\n')
        with self.assertRaisesRegex(ValueError,'working source differs'):
            C.source_payload(self.root,self.path)

    def test_manifest_rejects_extra_upload_path_and_wrong_commit_hash(self):
        self.manifest['files']['private.txt']='a'*64
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'seven-module'):
            C.source_payload(self.root,self.path)
        self.manifest['files'].pop('private.txt')
        self.manifest['files']['compute.py']='a'*64
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'committed transfer source differs'):
            C.source_payload(self.root,self.path)

    def frozen_plan_fixture(self):
        receipt_path=REPO/'harness/classical_ecdlp_endpoint_reuse/modal/receipts-b2/image-build.json'
        receipt=json.loads(receipt_path.read_bytes())
        for key in ('binary_sha256','build_info_sha256','adapter_manifest_sha256'):
            self.manifest[key]=receipt[key]
        self.path.write_text(json.dumps(self.manifest))
        exclusions=self.root/'prior-exclusions.json'
        exclusions.write_text(json.dumps({'schema':'classical.ecdlp.transfer-study.exclusions/v1','curve_keys':[]}))
        compute_plan=self.root/'compute-plan.json'
        compute_plan.write_text(json.dumps({'schema':'classical.ecdlp.transfer-study.compute-plan/v1','status':'frozen',
            'experiment_id':C.EXPERIMENT_ID,'run_id':C.RUN_ID,'source_manifest_sha256':C.sha_file(self.path),
            'cohort':{'exclusion_file_sha256':C.sha_file(exclusions)},'expected':SYNTHETIC_EXPECTED}))
        protocol=json.loads((REPO/'experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json').read_bytes())
        protocol['protocol_id']=C.EXPERIMENT_ID
        template=protocol['arms'][0]
        protocol['arms']=[{**template,'id':arm_id,
            'instrument':{**template['instrument'],'commit':self.manifest['source_revision_c']}}
            for arm_id in SYNTHETIC_EXPECTED['arm_ids']]
        protocol['extensions']['transfer_study']={
            'source_manifest_sha256':C.sha_file(self.path),
            'image_receipt_sha256':C.sha_file(receipt_path),
            'compute_plan_sha256':C.sha_file(compute_plan),
            'source_revision_c':self.manifest['source_revision_c'],
            'expected':SYNTHETIC_EXPECTED,'prior_exclusions_sha256':C.sha_file(exclusions)}
        path=self.root/'protocol.json'
        self.save_frozen(protocol,path)
        return receipt_path,path,compute_plan,exclusions,protocol

    @staticmethod
    def save_frozen(protocol,path):
        body={k:v for k,v in protocol.items() if k!='freeze'}
        protocol['freeze']['protocol_sha256']=C.sha(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
        path.write_text(json.dumps(protocol))

    def test_distinct_transfer_plan_exact_committed_source_and_no_native_invocation(self):
        receipt,path,compute_plan,exclusions,protocol=self.frozen_plan_fixture()
        plan,files,manifest=C.make_plan(self.root,receipt,path,compute_plan,self.path,exclusions)
        self.assertEqual(plan['experiment_id'],C.EXPERIMENT_ID)
        self.assertFalse(plan['native_binary_executed'])
        self.assertEqual(plan['compute_plan_sha256'],C.sha_file(compute_plan))
        self.assertEqual(set(files),C.SOURCE_NAMES)
        self.assertIn('/work/source/compute.py',C.engine_argv(plan))
        self.assertNotIn('/usr/local/bin/endpoint_reuse',C.engine_argv(plan))
        altered=json.loads(compute_plan.read_bytes());altered['synthetic_tamper']=True
        compute_plan.write_text(json.dumps(altered))
        with self.assertRaisesRegex(ValueError,'frozen transfer source/image/compute-plan/exclusions binding differs'):
            C.make_plan(self.root,receipt,path,compute_plan,self.path,exclusions)

    def test_frozen_source_manifest_pin_cannot_be_replaced(self):
        receipt,path,compute_plan,exclusions,protocol=self.frozen_plan_fixture()
        protocol['extensions']['transfer_study']['source_manifest_sha256']='f'*64
        self.save_frozen(protocol,path)
        with self.assertRaisesRegex(ValueError,'frozen transfer source/image/compute-plan/exclusions binding differs'):
            C.make_plan(self.root,receipt,path,compute_plan,self.path,exclusions)

    def test_fixed_trial_driver_refuses_another_experiment_before_any_sdk_call(self):
        receipt,path,compute_plan,exclusions,protocol=self.frozen_plan_fixture()
        protocol['protocol_id']='EXP-SYNTHETIC-000001'
        self.save_frozen(protocol,path)
        with self.assertRaisesRegex(ValueError,'bound to its allocated transfer experiment'):
            C.make_plan(self.root,receipt,path,compute_plan,self.path,exclusions)


class FakeFS:
    def __init__(self, files):self.files=dict(files)
    def write_bytes(self,data,path):self.files[path]=data
    def read_bytes(self,path):return self.files[path]
    def stat(self,path):return SimpleNamespace(type='file',size=len(self.files[path]))


class FakeProcess:
    def __init__(self,code=0):
        self.code=code
        self.stdout=SimpleNamespace(read=lambda:'')
        self.stderr=SimpleNamespace(read=lambda:'')
    def wait(self):return self.code


class FakeSandbox:
    object_id='sb-synthetic'
    def __init__(self,files,ambiguous_engine=False):
        self.filesystem=FakeFS(files);self.calls=[];self.terminated=False;self.ambiguous_engine=ambiguous_engine
    def exec(self,*argv,**kwargs):
        self.calls.append((argv,kwargs))
        if '_prepare' in argv:
            self.filesystem.files['/work/stage/engine-plan-probe.json']=json.dumps({
                'probe_passed':True,'returncode':0,'scientific_submission':False,'candidate_evaluations_allowed':0,'cohort_draws_allowed':0,
                'plan':synthetic_plan()}).encode()
        if '_launch' in argv and self.ambiguous_engine:raise RuntimeError('Synthetic ambiguous engine RPC')
        return FakeProcess()
    def terminate(self):self.terminated=True


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.helper=C.transport(REPO)
        self.files={'/opt/study/build-info.json':b'build','/opt/study/adapter-manifest.json':b'adapter',
                    '/opt/study/modal-image-build.json':b'provenance'}
        self.plan={'app_name':'synthetic','environment_name':'main','app_id':'ap-synthetic','image_id':'im-synthetic',
                   'build_info_sha256':C.sha(b'build'),'adapter_manifest_sha256':C.sha(b'adapter'),
                   'build_provenance_sha256':C.sha(b'provenance'),'expected':SYNTHETIC_EXPECTED,
                   'lifecycle':{'sandbox_timeout_seconds':5400,'staging_timeout_seconds':600,
                                'command_timeout_seconds':4200,'collection_grace_seconds':600}}
        self.sources={name:b'# synthetic\n' for name in C.SOURCE_NAMES}
        self.paths=[]
        for name in ('receipt','protocol','compute-plan','manifest','prior-exclusions'):
            path=self.root/name;path.write_bytes(b'{}');self.paths.append(path)
        self.patchers=[mock.patch.object(C,'transport',return_value=self.helper),
            mock.patch.object(C,'make_plan',return_value=(self.plan,self.sources,b'{}'))]
        for p in self.patchers:p.start();self.addCleanup(p.stop)

    def sdk(self,sandbox,create_error=False):
        calls=[]
        def create(*args,**kwargs):
            calls.append((args,kwargs))
            if create_error:raise RuntimeError('Synthetic ambiguous create RPC')
            return sandbox
        module=SimpleNamespace(__version__='1.6.2',
            App=SimpleNamespace(lookup=lambda *a,**k:SimpleNamespace(app_id='ap-synthetic')),
            Image=SimpleNamespace(from_id=lambda value:SimpleNamespace(object_id=value)),
            Sandbox=SimpleNamespace(create=create))
        return module,calls

    def invoke(self,sdk):
        return C.run(REPO,*self.paths[:3],self.paths[3],self.paths[4],self.root/'output',modal_module=sdk)

    def test_one_vm_one_engine_fixed_resources_no_workload_credentials(self):
        sb=FakeSandbox(self.files);sdk,calls=self.sdk(sb)
        with mock.patch.object(self.helper,'collect',return_value={'complete':True,'engine_returncode':0}):
            record=self.invoke(sdk)
        self.assertTrue(record['success']);self.assertTrue(sb.terminated)
        self.assertEqual(len(calls),1)
        kwargs=calls[0][1]
        for key,value in [('runtime','vm'),('cpu',(2,2)),('memory',(12288,12288)),
                          ('block_network',True),('secrets',[]),('include_oidc_identity_token',False)]:
            self.assertEqual(kwargs[key],value)
        self.assertEqual(sum('_launch' in argv for argv,_ in sb.calls),1)
        self.assertEqual(record['engine_exec_calls'],1)
        staged=sb.filesystem.files
        self.assertTrue(all('/work/source/'+name in staged for name in C.SOURCE_NAMES))
        launch=json.loads(staged['/work/stage/launch.json'])
        self.assertEqual(launch['engine_argv'][:4],['/usr/bin/timeout','--signal=TERM','--kill-after=30','3600'])
        self.assertIn('/work/source/compute.py',launch['engine_argv'])
        self.assertFalse(record['automatic_retry'])
        self.assertEqual(record['plan_probe_exec_calls'],1)

    def test_ambiguous_create_has_no_second_create_or_engine_submission(self):
        sdk,calls=self.sdk(FakeSandbox(self.files),True)
        record=self.invoke(sdk)
        self.assertEqual(len(calls),1);self.assertEqual(record['engine_exec_calls'],0)
        self.assertTrue(record['submission_ambiguous']);self.assertFalse(record['success'])

    def test_ambiguous_engine_retains_same_sandbox_when_collection_incomplete(self):
        sb=FakeSandbox(self.files,True);sdk,calls=self.sdk(sb)
        with mock.patch.object(self.helper,'collect',return_value={'complete':False}):
            record=self.invoke(sdk)
        self.assertEqual(len(calls),1);self.assertEqual(record['engine_exec_calls'],1)
        self.assertTrue(record['submission_ambiguous']);self.assertTrue(record['sandbox_preserved_for_collection'])
        self.assertFalse(sb.terminated);self.assertFalse(record['success'])

    def test_probe_wrong_count_refuses_science_without_second_vm(self):
        sb=FakeSandbox(self.files);sdk,calls=self.sdk(sb)
        original=sb.exec
        def execute(*argv,**kwargs):
            result=original(*argv,**kwargs)
            if '_prepare' in argv:
                path='/work/stage/engine-plan-probe.json'
                value=json.loads(sb.filesystem.files[path]);value['plan']['total_attempts_planned']=239
                sb.filesystem.files[path]=json.dumps(value).encode()
            return result
        sb.exec=execute
        with mock.patch.object(self.helper,'collect',return_value={'complete':False}):
            record=self.invoke(sdk)
        self.assertEqual(len(calls),1);self.assertEqual(record['engine_exec_calls'],0)
        self.assertFalse(any('_launch' in argv for argv,_ in sb.calls))
        self.assertTrue(record['sandbox_preserved_for_collection']);self.assertFalse(record['success'])

    def test_actual_image_file_mismatch_refuses_before_staging_or_science(self):
        sb=FakeSandbox({**self.files,'/opt/study/build-info.json':b'changed'});sdk,calls=self.sdk(sb)
        with mock.patch.object(self.helper,'collect',return_value={'complete':False}):
            record=self.invoke(sdk)
        self.assertEqual(len(calls),1);self.assertEqual(record['engine_exec_calls'],0)
        self.assertEqual(sb.calls,[])
        self.assertFalse(any(name.startswith('/work/source/') for name in sb.filesystem.files))
        self.assertIn('actual code image differs',record['error']['message'])


class PlanProbeTests(unittest.TestCase):
    def test_same_uid_environment_plan_only_and_zero_candidate_evaluations(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'probe.json'
            runner=mock.Mock(return_value=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps(synthetic_plan())))
            result=C.run_plan_probe(['python3','/work/source/compute.py'],output,SYNTHETIC_EXPECTED,runner)
            self.assertTrue(result['probe_passed']);self.assertEqual(result['candidate_evaluations_allowed'],0)
            argv=runner.call_args.args[0]
            self.assertEqual(argv[-1],'--plan-only');self.assertIn('--reuid=1000',argv)
            self.assertEqual(argv[:2],['env','-i']);self.assertEqual(output.stat().st_mode&0o777,0o444)

    def test_nonzero_or_measurement_started_is_retained_and_refuses(self):
        for code,started in ((2,False),(0,True)):
            with self.subTest(code=code,started=started),tempfile.TemporaryDirectory() as temp:
                output=Path(temp)/'probe.json'
                runner=mock.Mock(return_value=SimpleNamespace(returncode=code,stderr='synthetic error',stdout=json.dumps(synthetic_plan(started))))
                with self.assertRaisesRegex(ValueError,'scientific launch refused'):
                    C.run_plan_probe(['python3','/work/source/compute.py'],output,SYNTHETIC_EXPECTED,runner)
                self.assertTrue(output.is_file());self.assertFalse(json.loads(output.read_bytes())['probe_passed'])

    def test_runtime_uid_permissions_and_enforcement_cannot_be_omitted(self):
        for mutation in ('uid','writable','enforcement','cohort_drawn','candidate_executed'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temp:
                plan=synthetic_plan()
                if mutation=='uid':plan['runtime_facts']['resuid']=[0,0,0]
                if mutation=='writable':plan['runtime_facts']['input_access']['compute.py']['writable']=True
                if mutation=='enforcement':plan.pop('provider_runtime_requirements_enforced')
                if mutation=='cohort_drawn':plan['fresh_cohort_generated']=True
                if mutation=='candidate_executed':plan['candidate_attempts_executed']=1
                runner=mock.Mock(return_value=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps(plan)))
                with self.assertRaisesRegex(ValueError,'scientific launch refused'):
                    C.run_plan_probe(['python3','/work/source/compute.py'],Path(temp)/'probe.json',SYNTHETIC_EXPECTED,runner)


class TrialDriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        spec=importlib.util.spec_from_file_location('transfer_driver_test_subject',HERE/'driver.py')
        self.driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.driver)

    def produce(self,engine_code=0):
        args=SimpleNamespace(out=self.root/'run',run_id=C.RUN_ID,repo_root=REPO,
            image_receipt=self.root/'image.json',protocol=self.root/'protocol.json',
            compute_plan=self.root/'compute-plan.json',source_manifest=self.root/'source.json',prior_exclusions=self.root/'prior-exclusions.json')
        args.out.mkdir()
        for p in [args.image_receipt,args.protocol,args.compute_plan,args.source_manifest,args.prior_exclusions]:p.write_bytes(b'{}')
        record={'success':engine_code==0,'engine_command_returncode':engine_code,
                'collection':{'complete':True,'engine_returncode':engine_code},
                'plan':{key:C.sha(b'{}') for key in ('protocol_file_sha256','compute_plan_sha256','source_manifest_sha256','prior_exclusions_sha256')}}
        def run(*values):
            dest=values[-1];dest.mkdir();(dest/'controller-receipt.json').write_text(json.dumps(record))
            for name in ('protocol.json','compute-plan.json','source-manifest.json','prior-exclusions.json'):
                (dest/name).write_bytes(b'{}')
            (dest/'synthetic-partial.txt').write_text('synthetic retained controller evidence\n')
            return record
        with mock.patch.object(self.driver.controller,'run',side_effect=run):
            code=self.driver.run(args)
        return args,code

    def test_transport_only_success_has_checked_archive_and_source_manifest_binding(self):
        args,code=self.produce()
        self.assertEqual(code,0);self.assertEqual(self.driver.check(args.out),0)
        raw=json.loads((args.out/'raw-result.json').read_bytes())
        self.assertFalse(raw['attack_claimed']);self.assertFalse(raw['independent_public_verification'])
        self.assertEqual(raw['scientific_validity'],'not_assessed')
        self.assertEqual(raw['source_manifest_sha256'],C.sha(b'{}'))
        self.assertEqual(raw['prior_exclusions_sha256'],C.sha(b'{}'))

    def test_failed_engine_remains_failed_with_complete_partial_transport(self):
        args,code=self.produce(3)
        self.assertEqual(code,1);self.assertEqual(self.driver.check(args.out),1)
        self.assertTrue((args.out/'modal/synthetic-partial.txt').is_file())

    def test_raw_controller_duplicate_cannot_mask_archived_failure(self):
        args,code=self.produce(3)
        raw=json.loads((args.out/'raw-result.json').read_bytes())
        raw['controller']['engine_command_returncode']=0
        (args.out/'raw-result.json').write_text(json.dumps(raw))
        with self.assertRaisesRegex(ValueError,'raw controller duplicate differs'):
            self.driver.check(args.out)

    def test_raw_input_hash_cannot_disagree_with_archived_controller_inputs(self):
        args,code=self.produce()
        raw=json.loads((args.out/'raw-result.json').read_bytes())
        raw['compute_plan_sha256']='f'*64
        (args.out/'raw-result.json').write_text(json.dumps(raw))
        with self.assertRaisesRegex(ValueError,'frozen input hash differs'):
            self.driver.check(args.out)


if __name__=='__main__':unittest.main()
