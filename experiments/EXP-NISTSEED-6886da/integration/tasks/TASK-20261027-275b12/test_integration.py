"""Deterministic synthetic integration controls. No real execution is allowed.

Generated fixtures are retained under this task's _mock_artifacts directory;
failed attempts must not be deleted or overwritten. Root retains the complete
native stdout/stderr and exit status in test-report.txt. No outcome is asserted
by this source file before the suite is actually executed.
"""
from __future__ import annotations
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
ORIGINAL_RUN=subprocess.run
ORIGINAL_POPEN=subprocess.Popen
TOTALS={'forbidden_calls':0,'synthetic_boundary_calls':0,'local_quiet_cli_processes':0}

def sha(body): return hashlib.sha256(body).hexdigest()
def put(path,body):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(body)
def dump(path,value): put(path,(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
def load(path): return json.loads(path.read_text())
def source(path,name):
    specification=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(specification)
    specification.loader.exec_module(result)
    return result

def forbidden(*args,**kwargs):
    TOTALS['forbidden_calls']+=1
    raise AssertionError('forbidden process, VM, scientific boundary or storage seam reached')

@contextlib.contextmanager
def tripwires():
    with contextlib.ExitStack() as stack:
        for name in ('run','Popen','check_output','check_call','call'):
            stack.enter_context(mock.patch.object(subprocess,name,forbidden))
        for name in ('system','popen','fork','posix_spawn','posix_spawnp','execv','execve','execl','execlp','execvp','execvpe','spawnv','spawnve','spawnvp','spawnvpe'):
            if hasattr(os,name): stack.enter_context(mock.patch.object(os,name,forbidden))
        stack.enter_context(mock.patch.object(socket,'socket',forbidden))
        blocked={}
        for name in ('qemu_controls','cohort_case','artifact_store','boto3','botocore'):
            item=types.ModuleType(name)
            for function in ('vm','execute_case','read_bytes','upload','download','client','resource','main'):
                setattr(item,function,forbidden)
            blocked[name]=item
        stack.enter_context(mock.patch.dict(sys.modules,blocked))
        yield

runner=None
checker=None

def modules():
    global runner,checker
    if runner is None: runner=source(HERE/'integrated_runner.py','_synthetic_runner')
    if checker is None: checker=source(HERE/'integrated_checker.py','_synthetic_checker')
    return runner,checker

def command(cache,image):
    return ['/opt/homebrew/bin/qemu-system-i386','-machine','pc,accel=tcg','-cpu','max','-m','256','-smp','1',
            '-nodefaults','-no-user-config','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot',
            '-device','isa-debug-exit,iobase=0xf4,iosize=4','-kernel',str(cache/'vmlinuz-lts'),
            '-initrd',str(cache/'images'/(image+'.cpio.gz')),
            '-append','console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on']

def framed(body,certificate=None,child=0,timeout=0):
    result=b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n'+body+f'\n__ECPP_CHILD_EXIT__ {child} timeout={timeout}\n'.encode()
    if certificate is not None: result+=b'__ECPP_CERTIFICATE_BEGIN__\n'+certificate+b'\n__ECPP_CERTIFICATE_END__\n'
    return result+b'__ECPP_GUEST_COMPLETE__\n'

class Fixture:
    def __init__(self,root,index=0):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.r,self.c=modules(); self.context=self.c.source_context()
        self.index=index; self.row=self.context['rows'][index]; self.runtime=self.context['runtime']
        self.output=self.root/'trial'; self.capture=self.root/'capture'; self.binding=self.root/'binding.json'
        self.output.mkdir(); catalog=self.root/'trace-catalog'; catalog.mkdir()
        put(catalog/'ecpp.DfD',b'(() 0 0)\n(() 15 0)\n')
        self.profile={'scope':'EXPLICIT_SYNTHETIC_FIXTURE_ONLY','catalog_directory':str(catalog),
                      'image_sha256':{'prover':sha(b'explicit synthetic prover image'),'checker':sha(b'explicit synthetic checker image')}}
        v9=source(ROOT/'experiments/EXP-NISTSEED-6886da/implementation/cohort_runner.py','_fixture_v9')
        manifest={'schema':'crypto.autoresearch.nistseed_ecpp_trial_binding.v1','cohort_index':index,
                  'output_directory':str(self.output),'driver_capture_directory':str(self.capture),
                  'frozen_input_sha256':v9.verify_frozen(),'limits':v9.LIMITS,'primary_configuration':v9.PRIMARY}
        dump(self.binding,manifest)
        argv=['python3','integrated_runner.py','--index',str(index),'--output',str(self.output),
              '--input-binding-manifest',str(self.binding),'--driver-capture-directory',str(self.capture)]
        dump(self.output/'launch.json',{'argv':argv,'authority':{'task':'TASK-20261027-275b12','kind':'explicit synthetic fixture'}})
        dump(self.output/'environment.json',{'scope':'explicit synthetic fixture'})
        dump(self.output/'command.txt',argv)
        put(self.output/'stdout.log',b'supervisor stdout provenance\n')
        put(self.output/'stderr.log',b'supervisor stderr provenance\n')
        self.before={name:(self.output/name).read_bytes() for name in self.r.SUPERVISOR}
        self.calls=0
    def identity(self,child):
        dump(child/'identity.json',{'curve':self.row,
            'cohort_sha256':self.context['frozen']['research/nist_seed_ecpp_compat_20261024/cohort-inputs.json'],
            'bindings_sha256':self.context['frozen']['research/nist_seed_ecpp_compat_20261024/runtime-bindings.json'],
            'launcher_sha256':self.context['frozen']['research/nist_seed_ecpp_compat_20261024/cohort_case.py'],
            'fresh_process_rng':'original ModInitialize: srandom(1)','prover_guest_limit_seconds':300,
            'prover_host_limit_seconds':390,'classification_scope':'legacy prover/checker behavior on an already-certified prime integer'})
    def started(self,stage,payload):
        proving=stage=='prover'; artifacts={Path(item['logical_path']).name:item['sha256'] for item in self.runtime['artifacts']}
        return {'utc':'2026-10-27T00:00:00+00:00','command':command(self.output/'runtime-cache',self.profile['image_sha256'][stage]),
                'program_sha256':artifacts['runecpp' if proving else 'checkcertif'],'init_sha256':artifacts['qemu-init'],
                'initramfs_sha256':self.profile['image_sha256'][stage],'input_sha256':sha(payload),'stdin_sha256':sha(b''),
                'data_mode':'full' if proving else None,'guest_limit_seconds':300 if proving else 30,'host_limit_seconds':390 if proving else 90}
    def boundary(self,mode='complete',mutation=None):
        def fake(index,child,cache):
            self.calls+=1; TOTALS['synthetic_boundary_calls']+=1
            assert index==self.index and not child.exists() and not cache.exists()
            print('explicit fake driver stdout')
            print('explicit fake driver stderr',file=sys.stderr)
            if mode=='early': raise RuntimeError('explicit fake before child')
            child.mkdir(); self.identity(child)
            payload=(self.row['n']+'\n').encode(); certificate=f"{self.row['n']} -1 0 {self.row['n']} 0 0".encode()
            dump(child/'prover/started.json',self.started('prover',payload))
            if mode=='launch_only': raise RuntimeError('explicit fake after launch intent, before child process')
            if mode=='guest_only':
                put(child/'prover/serial.raw',b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n')
                raise RuntimeError('explicit fake before exec')
            if mode=='partial':
                put(child/'prover/serial.raw',b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n% Starting phase 1: building the sequence of primes\n% Factor= 2^')
                raise RuntimeError('explicit fake partial serial')
            pbody=b'% Starting phase 1: building the sequence of primes\n% D[[0]]=15\n% Factor= 2^3\nThis number is prime\n'
            cbody=b'  0: -1 1 0.00s\n'
            if mode=='wrong_root': certificate=b'103 -1 0 103 0 0'
            if mode=='checker_step': cbody=b'  0: -1 0 0.00s\n'
            if mode=='composite_label': pbody=pbody.replace(b'is prime',b'is composite')
            ps=framed(pbody,certificate,child=139 if mode=='nonzero_child' else 0)
            cs=framed(cbody)
            replacements={
              'begin_absent':(b'__ECPP_GUEST_BEGIN__\n',b''),
              'exit_absent':(b'__ECPP_CHILD_EXIT__ 0 timeout=0\n',b''),
              'complete_absent':(b'__ECPP_GUEST_COMPLETE__\n',b''),
              'abi_bad':(b'__ECPP_INIT_ABI__ 4 4 4',b'__ECPP_INIT_ABI__ 8 8 8'),
              'begin_duplicate':(b'__ECPP_GUEST_BEGIN__\n',b'__ECPP_GUEST_BEGIN__\n__ECPP_GUEST_BEGIN__\n'),
              'certificate_truncated':(b'__ECPP_CERTIFICATE_END__\n',b'__ECPP_CERTIFICATE_EN'),
              'markers_misordered':(b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n',b'__ECPP_GUEST_BEGIN__\n__ECPP_INIT_ABI__ 4 4 4\n')}
            if mode in replacements: ps=ps.replace(*replacements[mode])
            if mode=='checker_malformed': cs=cs.replace(b'__ECPP_GUEST_COMPLETE__\n',b'__ECPP_GUEST_COMPLETE')
            statuses={}
            for stage,serial,body,data,count in (('prover',ps,pbody,payload,1),('checker',cs,cbody,certificate,0)):
                dump(child/stage/'started.json',self.started(stage,data))
                status={'vm_valid':True,'qemu_exit':None if mode=='watchdog' and stage=='prover' else 33,
                        'child_exit':139 if mode=='nonzero_child' and stage=='prover' else 0,
                        'reason':'host_watchdog' if mode=='watchdog' and stage=='prover' else None,
                        'elapsed_host_seconds':1,'serial_sha256':sha(serial),'certificate_count':count}
                dump(child/stage/'result.json',status); put(child/stage/'serial.raw',serial)
                put(child/stage/'program.stdout',body); put(child/stage/'qemu.stderr',b'')
                statuses[stage]=status
            put(child/'prover/certificate.cformat',certificate)
            if mutation: mutation(child,self)
            return {'prover':statuses['prover'],'checker':statuses['checker'],'certificate_admitted':True,
                    'certificate_steps':[{'n':int(self.row['n']),'D':-1,'h':0,'pratt':[int(self.row['n'])]}],
                    'certificate_sha256':sha(certificate)}
        return fake
    def run(self,mode='complete',mutation=None):
        self.r.run_trial(self.index,self.output,self.binding,self.capture,legacy_call=self.boundary(mode,mutation),synthetic_profile=self.profile)
        return self.output
    def check(self): return self.c.check(self.output,self.binding,synthetic_profile=self.profile)
    def resign_outer(self):
        envelope=load(self.output/'integration-envelope.json')
        for name in list(envelope['sidecars']):
            path=self.output/name
            if path.is_file() and not path.is_symlink(): envelope['sidecars'][name]={'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}
        dump(self.output/'integration-envelope.json',envelope)

class Tests(unittest.TestCase):
    def setUp(self):
        self.guards=tripwires(); self.guards.__enter__(); self.addCleanup(self.guards.__exit__,None,None,None)
        (HERE/'_mock_artifacts').mkdir(exist_ok=True)
        self.root=Path(tempfile.mkdtemp(prefix=self._testMethodName+'-',dir=HERE/'_mock_artifacts'))
        self.r,self.c=modules(); self.sequence=0
    def fixture(self):
        self.sequence+=1
        return Fixture(self.root/str(self.sequence))
    def ordinary(self):
        fixture=self.fixture(); fixture.run(); verdict=fixture.check()
        self.assertTrue(verdict['synthetic_admission']); self.assertFalse(verdict['scientific_admission'])
        self.assertTrue(verdict['custody_valid'])
        for name,body in fixture.before.items(): self.assertEqual((fixture.output/name).read_bytes(),body)
        return fixture
    def refusal(self,fixture,gate):
        with self.assertRaisesRegex(self.c.CheckFailure,gate): fixture.check()
    def test_complete_admission_identity_and_schema(self):
        fixture=self.ordinary(); envelope=load(fixture.output/'integration-envelope.json')
        self.assertEqual(envelope['identity']['ordered_cohort'],fixture.context['rows'])
        self.assertEqual(len({row['curve_uid'] for row in envelope['identity']['ordered_cohort']}),21)
        self.assertEqual(fixture.calls,1)
        counters=load(fixture.output/'counter-evidence.json')
        self.assertEqual(counters['boundary_calls_attempted'],{'real':0,'synthetic':1})
        self.assertIsNone(counters['exact_program_start_total'])
        self.c.validate_schema(envelope); self.c.validate_schema(counters,'counters')
    def test_early_exception_no_child(self):
        fixture=self.fixture(); fixture.run('early'); verdict=fixture.check()
        self.assertTrue(verdict['custody_valid']); self.assertFalse(verdict['synthetic_admission'])
        self.assertEqual(verdict['counters']['stages']['prover']['launch_intent'],0)
    def test_launch_intent_only_is_not_program_entry(self):
        fixture=self.fixture(); fixture.run('launch_only'); verdict=fixture.check(); stage=verdict['counters']['stages']['prover']
        self.assertEqual((stage['launch_intent'],stage['guest_init_observed'],stage['program_output_observed']),(1,0,0))
        self.assertIsNone(stage['exact_program_starts'])
    def test_guest_begin_before_exec_is_not_program_entry(self):
        fixture=self.fixture(); fixture.run('guest_only'); verdict=fixture.check(); stage=verdict['counters']['stages']['prover']
        self.assertEqual((stage['launch_intent'],stage['guest_init_observed'],stage['program_output_observed']),(1,1,0))
        recovery=load(fixture.output/'integration-recovery.json')
        self.assertEqual(recovery['boundary_exceptions'][0]['message'],'explicit fake before exec')
        self.assertIsNotNone(recovery['original_exception'])
    def test_original_program_output_without_completion(self):
        fixture=self.fixture(); fixture.run('partial'); verdict=fixture.check(); stage=verdict['counters']['stages']['prover']
        self.assertEqual(stage['program_output_observed'],1); self.assertEqual(stage['stage_completed_success'],0)
        self.assertFalse(verdict['synthetic_admission'])
    def test_bounded_secondary_recovery_failure_retains_raw(self):
        fixture=self.fixture()
        with mock.patch.object(self.r,'frame_probe',side_effect=ValueError('explicit secondary parser failure')): fixture.run('partial')
        verdict=fixture.check(); self.assertTrue(verdict['custody_valid'])
        recovery=load(fixture.output/'integration-recovery.json')
        self.assertTrue(any(error['message']=='explicit secondary parser failure' for error in recovery['stages']['prover']['errors']))
        self.assertTrue((fixture.output/'integration-failure.json').is_file())
        self.assertIn(b'% Factor= 2^',(fixture.output/'legacy-child/prover/serial.raw').read_bytes())
    def test_checker_secondary_parser_guard_is_bounded(self):
        fixture=self.ordinary()
        with mock.patch.object(self.c,'probe_frame',side_effect=ValueError('independent parser refusal')):
            self.refusal(fixture,'recovery_record')
        self.assertTrue((fixture.output/'raw-artifacts.tar.gz').is_file())
    def test_watchdog_is_not_admission(self):
        self.ordinary(); fixture=self.fixture(); fixture.run('watchdog'); verdict=fixture.check()
        self.assertFalse(verdict['synthetic_admission']); self.assertIn('prover_status',verdict['admission_failures'])
    def test_nonzero_child_completed_failure_is_separate(self):
        self.ordinary(); fixture=self.fixture(); fixture.run('nonzero_child'); verdict=fixture.check()
        stage=verdict['counters']['stages']['prover']; self.assertEqual(stage['stage_completed_failure'],1)
        self.assertEqual(stage['stage_completed_success'],0); self.assertFalse(verdict['synthetic_admission'])
    def test_changed_uid_order_label_index_refuse_static_gate(self):
        for field,value in (('curve_uid','urn:ec-record:1:sha256:'+'0'*64),('n','103'),('label','published')):
            with self.subTest(field=field):
                fixture=self.ordinary(); envelope=load(fixture.output/'integration-envelope.json')
                envelope['identity']['curve'][field]=value; dump(fixture.output/'integration-envelope.json',envelope)
                self.refusal(fixture,'static_identity')
        fixture=self.ordinary(); envelope=load(fixture.output/'integration-envelope.json'); envelope['cohort_index']=1
        dump(fixture.output/'integration-envelope.json',envelope); self.refusal(fixture,'static_identity')
    def test_source_runtime_configuration_and_argv_identity(self):
        for field in ('source_pins','runtime','primary_configuration','prover_argv'):
            with self.subTest(field=field):
                fixture=self.ordinary(); envelope=load(fixture.output/'integration-envelope.json')
                if field=='prover_argv':
                    envelope['identity'][field]=['/program','-f','/input']
                    dump(fixture.output/'integration-envelope.json',envelope); self.refusal(fixture,'schema')
                else:
                    envelope['identity'][field]={}; dump(fixture.output/'integration-envelope.json',envelope)
                    self.refusal(fixture,'static_identity')
    def test_started_input_program_init_image_command_and_limits_identity(self):
        for field,value in (('input_sha256','0'*64),('program_sha256','0'*64),('init_sha256','0'*64),('initramfs_sha256','0'*64),('command',['/wrong']),('data_mode','empty'),('guest_limit_seconds',999)):
            with self.subTest(field=field):
                self.ordinary(); fixture=self.fixture()
                def mutate(child,unused,field=field,value=value):
                    path=child/'prover/started.json'; record=load(path); record[field]=value; dump(path,record)
                fixture.run(mutation=mutate); self.refusal(fixture,'launch_identity')
    def test_copied_binding_mutation_refuses_binding_gate(self):
        fixture=self.ordinary(); path=fixture.output/'input-binding-manifest.json'; value=load(path); value['cohort_index']=1
        dump(path,value); fixture.resign_outer(); self.refusal(fixture,'copied_binding')
    def test_supervisor_log_mutation(self):
        fixture=self.ordinary(); put(fixture.output/'stdout.log',b'mutated'); self.refusal(fixture,'supervisor_identity')
    def test_changed_missing_extra_symlinked_raw_member(self):
        actions={'changed':lambda f:put(f.output/'legacy-child/prover/qemu.stderr',b'changed'),
                 'missing':lambda f:(f.output/'legacy-child/checker/qemu.stderr').unlink(),
                 'extra':lambda f:put(f.output/'legacy-child/unexpected.raw',b'unexpected'),
                 'symlink':lambda f:(f.output/'legacy-child/link').symlink_to(f.output/'stdout.log')}
        for name,action in actions.items():
            with self.subTest(name=name):
                fixture=self.ordinary(); action(fixture)
                self.refusal(fixture,'path_safety' if name=='symlink' else 'capsule_custody')
    def test_capsule_inventory_and_sidecar_tampering(self):
        for name in ('raw-artifacts.tar.gz','raw-artifact-inventory.json','observation.json','driver.stdout.log'):
            with self.subTest(name=name):
                fixture=self.ordinary(); path=fixture.output/name; put(path,path.read_bytes()+b'changed')
                self.refusal(fixture,'outer_sidecar_custody')
    def test_supplemental_trace_mutation_after_consistent_resigning(self):
        fixture=self.ordinary(); path=fixture.output/'supplemental-trace.json'; value=load(path)
        value['stages']['prover']['printed_trace']['events']=[]; dump(path,value)
        capsule=source(ROOT/'experiments/EXP-NISTSEED-6886da/integration/capsule.py','_test_resigner')
        (fixture.output/'raw-artifacts.tar.gz').unlink(); (fixture.output/'raw-artifact-inventory.json').unlink()
        capsule.create(fixture.output); fixture.resign_outer(); self.refusal(fixture,'supplemental_trace')
    def test_invented_start_count_refuses_schema(self):
        fixture=self.ordinary(); path=fixture.output/'counter-evidence.json'; value=load(path)
        value['stages']['prover']['exact_program_starts']=1; dump(path,value); fixture.resign_outer()
        self.refusal(fixture,'schema')
    def test_invented_observed_count_refuses_independent_counter_gate(self):
        fixture=self.ordinary(); path=fixture.output/'counter-evidence.json'; value=load(path)
        value['stages']['checker']['program_output_observed']=1; dump(path,value); fixture.resign_outer()
        self.refusal(fixture,'counter_mismatch')
    def test_reused_and_aliased_output_refuse_before_boundary(self):
        fixture=self.ordinary(); calls=fixture.calls
        with self.assertRaises(self.r.Refusal): fixture.run()
        self.assertEqual(fixture.calls,calls)
        fresh=self.fixture()
        with self.assertRaisesRegex(self.r.Refusal,'equal or nested'):
            self.r.run_trial(fresh.index,fresh.output,fresh.binding,fresh.output/'capture',legacy_call=fresh.boundary(),synthetic_profile=fresh.profile)
        self.assertEqual(fresh.calls,0)
    def test_missing_real_admission_never_reaches_deferred_boundary(self):
        fixture=self.fixture()
        with mock.patch.object(self.r,'runtime_material',return_value={}),mock.patch.object(self.r,'deferred_real_boundary',side_effect=forbidden):
            with self.assertRaisesRegex(self.r.Refusal,'later admitted packet'):
                self.r.run_trial(fixture.index,fixture.output,fixture.binding,fixture.capture)
        self.assertEqual(fixture.calls,0)
    def test_real_checker_cannot_use_synthetic_profile(self):
        fixture=self.ordinary()
        self.refusal_without_profile(fixture)
    def refusal_without_profile(self,fixture):
        with self.assertRaisesRegex(self.c.CheckFailure,'runtime_identity'):
            self.c.check(fixture.output,fixture.binding)
    def test_nested_schema_mutations_are_rejected(self):
        fixture=self.ordinary(); envelope=load(fixture.output/'integration-envelope.json')
        value=copy.deepcopy(envelope); value['finalization']['extra']=True
        with self.assertRaisesRegex(self.c.CheckFailure,'schema'): self.c.validate_schema(value)
        counters=load(fixture.output/'counter-evidence.json'); counters['stages']['prover']['evidence'][0]['extra']=True
        with self.assertRaisesRegex(self.c.CheckFailure,'schema'): self.c.validate_schema(counters,'counters')
    def test_existing_aa_producer_validity_precedes_comparison(self):
        aa=source(ROOT/'experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py','_integration_existing_aa')
        self.assertEqual(sha((ROOT/'experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py').read_bytes()),'d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18')
        kernel=b'explicit synthetic A/A kernel'; artifacts={'qemu-init':b'fake init','runecpp':b'fake prover','checkcertif':b'fake checker'}
        runtime={'kernel':{'kernel_sha256':sha(kernel)},'artifacts':[]}
        def bound(path):
            candidate=load(path)
            if candidate!={'fixture':aa.FIXTURE,'limits':aa.LIMITS,'primary_configuration':aa.PRIMARY,'input_bindings':aa.SOURCE_HASHES}: raise aa.Refusal('synthetic A/A fixed binding mismatch')
            return {**candidate,'runtime':runtime,'_manifest_sha256':sha(path.read_bytes())}
        def expectation(output,cache,unused,stage,payload):
            image=b'explicit synthetic A/A image '+stage.encode()
            return {'program':'runecpp' if stage=='prover' else 'checkcertif','image':image,
                    'image_path':cache/'images'/(sha(image)+'.cpio.gz'),'command':command(cache,sha(image)),
                    'data_mode':'full' if stage=='prover' else None,'guest':300 if stage=='prover' else 30,
                    'host':390 if stage=='prover' else 90,'artifacts':artifacts,'payload':payload}
        certificate=b'101 -1 0 101 0 0'; calls=[]
        def boundary(invalid=False):
            def fake(output,cache,payload,configuration):
                TOTALS['synthetic_boundary_calls']+=1; calls.append(output)
                assert payload==b'101\n'; cache.mkdir(); (cache/'images').mkdir(); put(cache/'vmlinuz-lts',kernel)
                raw=output/'raw'; put(raw/'input.txt',payload)
                for stage,body,input_bytes in (('prover',b'% N_0=101\nThis number is composite\n' if invalid else b'% N_0=101\nThis number is prime\n',payload),('checker',b' 0: -1 1 0.00s\n',certificate)):
                    serial=framed(body,certificate if stage=='prover' else None); expected=expectation(output,cache,runtime,stage,input_bytes)
                    put(expected['image_path'],expected['image']); put(raw/stage/'serial.raw',serial); put(raw/stage/'program.stdout',body); put(raw/stage/'qemu.stderr',b'')
                    started={'utc':'2026-10-27T00:00:00Z','command':expected['command'],'program_sha256':sha(artifacts[expected['program']]),
                             'init_sha256':sha(artifacts['qemu-init']),'initramfs_sha256':sha(expected['image']),'input_sha256':sha(input_bytes),'stdin_sha256':sha(b''),
                             'data_mode':expected['data_mode'],'guest_limit_seconds':expected['guest'],'host_limit_seconds':expected['host']}
                    dump(raw/stage/'started.json',started)
                    dump(raw/stage/'result.json',{'vm_valid':True,'qemu_exit':33,'child_exit':0,'reason':None,'elapsed_host_seconds':1,
                         'serial_sha256':sha(serial),'certificate_count':1 if stage=='prover' else 0})
                put(raw/'prover/certificate.cformat',certificate)
            return fake
        binding=self.root/'aa-binding.json'; dump(binding,{'fixture':aa.FIXTURE,'limits':aa.LIMITS,'primary_configuration':aa.PRIMARY,'input_bindings':aa.SOURCE_HASHES})
        with mock.patch.object(aa,'binding',side_effect=bound),mock.patch.object(aa,'stage_expectation',side_effect=expectation),mock.patch.object(aa,'default_legacy_boundary',side_effect=forbidden):
            with mock.patch.object(aa,'archived_compare',wraps=aa.archived_compare) as comparison:
                result=aa.build_pair(self.root/'aa-left',self.root/'aa-right',binding,boundary())
                self.assertEqual(comparison.call_count,1); self.assertTrue(self.c.check_aa_documents(result['left'],result['right'])['equal'])
            with mock.patch.object(aa,'archived_compare',wraps=aa.archived_compare) as comparison:
                with self.assertRaisesRegex(aa.Refusal,'labels'): aa.build_pair(self.root/'invalid-left',self.root/'invalid-right',binding,boundary(True))
                self.assertEqual(comparison.call_count,0)
        invalid=copy.deepcopy(result['left']); invalid['labels']=['composite']
        with self.assertRaisesRegex(self.c.CheckFailure,'aa_validity'): self.c.check_aa_documents(invalid,invalid)
        self.assertEqual(len(calls),4)
    def test_quiet_explicit_fake_cli_after_actual_process_exit(self):
        workspace=self.root/'cli'; workspace.mkdir()
        argv=[sys.executable,str(HERE/'integrated_runner.py'),'--explicit-fake','--workspace',str(workspace)]
        environment=dict(os.environ); environment['PYTHONDONTWRITEBYTECODE']='1'
        with mock.patch.object(subprocess,'Popen',ORIGINAL_POPEN):
            result=ORIGINAL_RUN(argv,capture_output=True,timeout=90,env=environment)
        TOTALS['local_quiet_cli_processes']+=1
        put(self.root/'quiet-cli.stdout',result.stdout); put(self.root/'quiet-cli.stderr',result.stderr)
        dump(self.root/'quiet-cli.receipt.json',{'argv':argv,'returncode':result.returncode,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr)})
        self.assertEqual(result.returncode,0); self.assertEqual(result.stdout,b''); self.assertEqual(result.stderr,b'')

# Each malformed fixture runs an ordinary complete control first, then the
# actual additive driver and independent checker for the named mutation.
def malformed_test(mode,gate):
    def test(self):
        self.ordinary(); fixture=self.fixture(); fixture.run(mode); verdict=fixture.check()
        self.assertTrue(verdict['custody_valid']); self.assertFalse(verdict['synthetic_admission'])
        self.assertIn(gate,verdict['admission_failures'])
    return test
for _mode,_gate in [('begin_absent','prover_framing'),('exit_absent','prover_framing'),('complete_absent','prover_framing'),
                    ('abi_bad','prover_framing'),('begin_duplicate','prover_framing'),('markers_misordered','prover_framing'),
                    ('certificate_truncated','prover_framing'),('checker_malformed','checker_framing'),
                    ('checker_step','checker_body'),('wrong_root','certificate_grammar_root'),('composite_label','prover_labels')]:
    setattr(Tests,'test_mutation_'+_mode,malformed_test(_mode,_gate))

def quiet_cli(workspace):
    with tripwires():
        fixture=Fixture(workspace/'fixture'); fixture.run(); verdict=fixture.check()
        return verdict['synthetic_admission'] and not verdict['scientific_admission'] and all((fixture.output/name).read_bytes()==body for name,body in fixture.before.items())

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'schema':'nistseed.synthetic_test_execution.v1','tests_run':result.testsRun,
                     'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
                     'instrumented_counts':TOTALS,'actual_real_vm_executions':0,'actual_real_program_executions':0,
                     'actual_scientific_cohort_runs':0,'actual_storage_operations':0,
                     'scope':'guarded synthetic fixtures and one explicit local fake CLI subprocess only'},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
