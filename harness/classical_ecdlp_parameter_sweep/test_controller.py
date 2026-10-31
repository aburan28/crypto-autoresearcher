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
spec = importlib.util.spec_from_file_location('sweep_controller_test_subject', HERE/'controller.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


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
        self.git('init','-q')
        self.git('config','user.name','Synthetic fixture')
        self.git('config','user.email','fixture@example.invalid')
        self.git('add','package')
        self.git('commit','-qm','Synthetic source closure')
        self.manifest = {'schema':C.SOURCE_SCHEMA, 'source_revision_c':self.git('rev-parse','HEAD').strip(),
                         'source_prefix':'package', 'native_source_a':C.NATIVE_A, 'image_adapter_source_b':C.IMAGE_B,
                         'files':{p.name:C.sha_file(p) for p in self.package.iterdir()}}
        self.path = self.root/'source-manifest.json'
        self.path.write_text(json.dumps(self.manifest))
        real = C.transport(REPO)
        patch = mock.patch.object(C,'transport',return_value=real)
        patch.start();self.addCleanup(patch.stop)

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.root,text=True)

    def test_exact_five_module_committed_closure_and_working_drift_refusal(self):
        manifest, raw, files = C.source_payload(self.root,self.path)
        self.assertEqual(set(files),C.SOURCE_NAMES)
        self.assertEqual(C.sha(raw),C.sha(self.path.read_bytes()))
        (self.package/'engine.py').write_text('# changed working source\n')
        with self.assertRaisesRegex(ValueError,'working source differs'):
            C.source_payload(self.root,self.path)

    def test_manifest_rejects_extra_upload_path_and_wrong_commit_hash(self):
        self.manifest['files']['private.txt']='a'*64
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'five-module'):
            C.source_payload(self.root,self.path)
        self.manifest['files'].pop('private.txt')
        self.manifest['files']['engine.py']='a'*64
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,'committed sweep source differs'):
            C.source_payload(self.root,self.path)

    def frozen_plan_fixture(self):
        receipt_path=REPO/'harness/classical_ecdlp_endpoint_reuse/modal/receipts-b2/image-build.json'
        receipt=json.loads(receipt_path.read_bytes())
        for key in ('binary_sha256','build_info_sha256','adapter_manifest_sha256'):
            self.manifest[key]=receipt[key]
        self.path.write_text(json.dumps(self.manifest))
        original={'schema':'classical.ecdlp.endpoint-public-inputs/v1','protocol_sha256':'d'*64,'files':[]}
        public=json.dumps(original).encode()
        bundle=self.root/'public.tar.gz'
        with tarfile.open(bundle,'w:gz') as archive:
            info=tarfile.TarInfo('public/inputs-manifest.json');info.size=len(public)
            archive.addfile(info,io.BytesIO(public))
        protocol=json.loads((REPO/'experiments/EXP-ECDLP-2b4ff1/protocol.modal-vm.v1.json').read_bytes())
        protocol['protocol_id']='EXP-ECDLP-f50061'
        protocol['extensions']['parameter_sweep']={
            'source_manifest_sha256':C.sha_file(self.path),
            'image_receipt_sha256':C.sha_file(receipt_path),
            'public_bundle_sha256':C.sha_file(bundle),'inputs_manifest_sha256':C.sha(public),
            'source_input_protocol_sha256':'d'*64}
        path=self.root/'protocol.json'
        self.save_frozen(protocol,path)
        return receipt_path,path,bundle,C.sha(public),protocol

    @staticmethod
    def save_frozen(protocol,path):
        body={k:v for k,v in protocol.items() if k!='freeze'}
        protocol['freeze']['protocol_sha256']=C.sha(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
        path.write_text(json.dumps(protocol))

    def test_new_frozen_protocol_can_explicitly_reuse_distinct_old_public_protocol(self):
        receipt,path,bundle,input_hash,protocol=self.frozen_plan_fixture()
        plan,files,manifest=C.make_plan(self.root,receipt,path,bundle,self.path,input_hash)
        self.assertEqual(plan['source_input_protocol_sha256'],'d'*64)
        self.assertNotEqual(plan['new_protocol_sha256'],'d'*64)
        self.assertEqual(set(files),C.SOURCE_NAMES)
        protocol['extensions']['parameter_sweep']['source_input_protocol_sha256']='e'*64
        self.save_frozen(protocol,path)
        with self.assertRaisesRegex(ValueError,'original protocol/hash'):
            C.make_plan(self.root,receipt,path,bundle,self.path,input_hash)

    def test_frozen_source_manifest_pin_cannot_be_replaced(self):
        receipt,path,bundle,input_hash,protocol=self.frozen_plan_fixture()
        protocol['extensions']['parameter_sweep']['source_manifest_sha256']='f'*64
        self.save_frozen(protocol,path)
        with self.assertRaisesRegex(ValueError,'frozen sweep source/image/public binding differs'):
            C.make_plan(self.root,receipt,path,bundle,self.path,input_hash)

    def test_fixed_trial_driver_refuses_another_experiment_before_any_sdk_call(self):
        receipt,path,bundle,input_hash,protocol=self.frozen_plan_fixture()
        protocol['protocol_id']='EXP-SYNTHETIC-000001'
        self.save_frozen(protocol,path)
        with self.assertRaisesRegex(ValueError,'bound to EXP-ECDLP-f50061'):
            C.make_plan(self.root,receipt,path,bundle,self.path,input_hash)


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
                'probe_passed':True,'returncode':0,'scientific_submission':False,'native_children_allowed':0,
                'plan':{'planned_children':5248,'target_arm_cases':335872,'measurement_started':False}}).encode()
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
                   'build_provenance_sha256':C.sha(b'provenance'),'inputs_manifest_sha256':'a'*64,
                   'lifecycle':{'sandbox_timeout_seconds':5400,'staging_timeout_seconds':600,
                                'command_timeout_seconds':4200,'collection_grace_seconds':600}}
        self.sources={name:b'# synthetic\n' for name in C.SOURCE_NAMES}
        self.paths=[]
        for name in ('receipt','protocol','bundle','manifest'):
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
        return C.run(REPO,*self.paths[:3],self.paths[3],'a'*64,self.root/'output',modal_module=sdk)

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
        self.assertEqual(launch['engine_argv'][1],'/work/source/engine.py')
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


class PlanProbeTests(unittest.TestCase):
    def test_same_uid_environment_plan_only_and_zero_native_schedule(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'probe.json'
            runner=mock.Mock(return_value=SimpleNamespace(returncode=0,stderr='',stdout=json.dumps({
                'planned_children':5248,'target_arm_cases':335872,'measurement_started':False})))
            result=C.run_plan_probe(['python3','/work/source/engine.py'],output,runner)
            self.assertTrue(result['probe_passed']);self.assertEqual(result['native_children_allowed'],0)
            argv=runner.call_args.args[0]
            self.assertEqual(argv[-1],'--plan-only');self.assertIn('--reuid=1000',argv)
            self.assertEqual(argv[:2],['env','-i']);self.assertEqual(output.stat().st_mode&0o777,0o444)

    def test_nonzero_or_measurement_started_is_retained_and_refuses(self):
        for code,started in ((2,False),(0,True)):
            with self.subTest(code=code,started=started),tempfile.TemporaryDirectory() as temp:
                output=Path(temp)/'probe.json'
                runner=mock.Mock(return_value=SimpleNamespace(returncode=code,stderr='synthetic error',stdout=json.dumps({
                    'planned_children':5248,'target_arm_cases':335872,'measurement_started':started})))
                with self.assertRaisesRegex(ValueError,'scientific launch refused'):
                    C.run_plan_probe(['python3','/work/source/engine.py'],output,runner)
                self.assertTrue(output.is_file());self.assertFalse(json.loads(output.read_bytes())['probe_passed'])


class TrialDriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        spec=importlib.util.spec_from_file_location('sweep_driver_test_subject',HERE/'driver.py')
        self.driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.driver)

    def produce(self,engine_code=0):
        args=SimpleNamespace(out=self.root/'run',run_id='RUN-SYNTHETIC-000000',repo_root=REPO,
            image_receipt=self.root/'image.json',protocol=self.root/'protocol.json',
            public_bundle=self.root/'public.tar.gz',source_manifest=self.root/'source.json',inputs_manifest_sha256='a'*64)
        args.out.mkdir()
        for p in [args.image_receipt,args.protocol,args.public_bundle,args.source_manifest]:p.write_bytes(b'{}')
        record={'success':engine_code==0,'engine_command_returncode':engine_code,
                'collection':{'complete':True,'engine_returncode':engine_code}}
        def run(*values):
            dest=values[-1];dest.mkdir();(dest/'controller-receipt.json').write_text(json.dumps(record))
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


if __name__=='__main__':unittest.main()
