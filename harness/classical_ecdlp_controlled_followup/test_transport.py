"""Fixed disclosed F11 byte fixtures only. SDK is mocked; no fresh draw."""
import ast
import copy
import enum
import types
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import controller as c
import driver


def fixture():
    interface=c.read(os.environ.get('CONTROLLED_INTERFACE',str(Path(__file__).with_name('engine-interface.json'))))
    records=copy.deepcopy(interface['embedded_deterministic_F11_records'])
    public={'nonce':'00'*32,'curves':[{'curve_id':'fixture-F11','model':{'p':11,'a':1,'b':6,'r':13},'base':[2,7],'targets':[{'target_id':'target7','point':[7,2]}]}]}
    public_bytes=c.canonical(public)+b'\n'
    provenance={'protocol_sha256':'00'*32,'source_fingerprint':'00'*32,'cohort_sha256':c.sha_bytes(public_bytes)}
    # Original-only calibration fixture: no paired cells are manufactured.
    records['trace']['incremental']=None;records['trace']['equal']=None
    expected={'setups':1,'intents':1,'singles':1,'traces':1,'cells':0}
    records['summary'].update(expected=expected,observed=expected,provenance=provenance)
    files={}
    for name,key in [('attempt-intents.jsonl','intent'),('setups.jsonl','setup'),('single-points.jsonl','single-point'),('traces.jsonl','trace')]:files['raw/'+name]=c.canonical(records[key])+b'\n'
    files['raw/decoder-cells.jsonl']=b''
    files['raw/engine-summary.json']=c.canonical(records['summary'])+b'\n'
    completion=records['completion'];completion['provenance']=provenance
    completion['files']={Path(name).name:{'sha256':c.sha_bytes(blob),'bytes':len(blob),'records':(len(blob.splitlines()) if name.endswith('.jsonl') else 1)} for name,blob in files.items()}
    files['raw/engine-completion.json']=c.canonical(completion)+b'\n'
    plan={'expected':expected,'setup_ids':['fixture-F11/circuit1.a5'],'single_ids':[records['single-point']['single_id']],
          'trace_ids':[records['trace']['trace_id']],'paired_trace_ids':[],'provenance':provenance,
          'engine_interface_canonical_sha256':c.sha_bytes(c.canonical(interface))}
    files['public-cohort.json']=public_bytes;files['host-plan.json']=c.canonical(plan)+b'\n';files['worker.stdout']=b'disclosed F11 mock\n';files['worker.stderr']=b''
    return files,plan,interface


class FileType(enum.Enum):
    FILE = 'file'
    DIRECTORY = 'directory'
    SYMLINK = 'symlink'


class Filesystem:
    # Exact installed SDK1.6.2 positional signatures; no Sandbox.open escape.
    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.info_mutant = None
        self.copy_mutant = None
        self.metadata = b'{}'
    def stat(self, remote_path):
        self.sandbox.events.append(('stat', remote_path))
        directories = {'/', '/opt', '/opt/study', '/work', '/work/result', '/work/result/raw'}
        kind = FileType.DIRECTORY if remote_path in directories else FileType.FILE
        size = 0 if kind == FileType.DIRECTORY else len(self.blob(remote_path))
        info = types.SimpleNamespace(type=kind, size=size, symlink_target=None)
        if self.info_mutant: self.info_mutant(remote_path, info)
        return info
    def blob(self, remote_path):
        return self.metadata if remote_path.startswith('/opt/study/') else self.sandbox.files[remote_path.removeprefix('/work/result/')]
    def read_bytes(self, remote_path):
        self.sandbox.events.append(('read_bytes', remote_path))
        return self.blob(remote_path)
    def write_bytes(self, data, remote_path):
        assert isinstance(data, bytes) and remote_path.startswith('/')
        self.sandbox.events.append(('write_bytes', remote_path))
        self.sandbox.stage[remote_path] = data
    def copy_to_local(self, remote_path, local_path):
        self.sandbox.events.append(('copy_to_local', remote_path))
        if self.copy_mutant: return self.copy_mutant(remote_path, Path(local_path))
        Path(local_path).write_bytes(self.blob(remote_path))


class Sandbox:
    object_id='sb-MOCK-F11'
    def __init__(self,files):
        self.files=files;self.stage={};self.events=[];self.fail_terminate=False
        self.filesystem = Filesystem(self)
    def exec(self,*argv,**kwargs):
        self.events.append(('exec',argv[0]))
        entries=[{'path':p,'sha256':c.sha_bytes(b),'size':len(b)} for p,b in self.files.items()]
        return type('Proc',(),{'wait':lambda s:0,'stdout':io.StringIO(json.dumps({'engine_returncode':0,'uid1000_quiescent':True,'files':entries})), 'stderr':io.StringIO('')})()
    def terminate(self,wait):
        self.events.append(('terminate',wait))
        if self.fail_terminate:raise RuntimeError('retained termination failure')
        return -15


def sdk_for(sb):
    return type('SDK',(),{'__version__':'1.6.2',
        'App':type('App',(),{'lookup':staticmethod(lambda *a,**kw:type('AppInstance',(),{'app_id':c.APP_ID})())}),
        'Image':type('Image',(),{'from_id':staticmethod(lambda image:type('ImageInstance',(),{'object_id':image})())}),
        'Sandbox':type('SandboxFactory',(),{'create':staticmethod(lambda *a,**kw:sb)})})


def mocked_run(root,termination_failure=False, configure=None):
    files,hplan,interface=fixture();sb=Sandbox(files);sb.fail_terminate=termination_failure
    if configure: configure(sb)
    limits={'max_total_bytes':1<<26,'max_file_bytes':1<<25,'max_jsonl_line_bytes':1<<20,'command_seconds':30,'sandbox_seconds':120}
    config={'inputs':{'protocol':{'sha256':'00'*32}},'seed_rules':{'fixture_only':'fixed00_no_entropy'}}
    inputs={'image_receipt':{'app_name':'fixture','environment_name':'fixture',**{k:c.sha_bytes(b'{}') for k in ['build_info_sha256','adapter_manifest_sha256','build_provenance_sha256']}},'engine_plan':{**hplan,'sampler':{}},'engine_interface':interface,
            'sampler':{},'prior_exclusions':{},'protocol':{'protocol_id':'TEST-F11','version':1,'repository':'fixture-only','freeze':{'protocol_sha256':'00'*32},'arms':[{'id':'candidate-batch','role':'candidate'}],'extensions':{'controlled_followup':{'export_arm':'candidate-batch'}}}}
    plan={'schema':c.SCHEMA+'transport-plan/v1','source_fingerprint':'00'*32,'limits':limits}
    workers={c.PREFIX+'/'+n:b'# inert mocked staging source\n' for n in c.WORKER}
    out=Path(root)/'trial'
    def snapshot(repo,config_path,config,inputs,out):
        c.write(out/'config.json',config)
        for role,value in inputs.items():c.write(out/(role+'.json'),value)
    with patch.object(c,'make_plan',return_value=(plan,config,inputs,workers)),patch.object(c,'snapshot_inputs',side_effect=snapshot):
        record=c.run(root,'not-read-mock-config',out,sdk_for(sb))
    record['supervisor_identity']={'experiment_id':'TEST-F11','run_id':'RUN-FIXTURE'}
    (out/'controller-receipt.json').unlink();c.write(out/'controller-receipt.json',record)
    return out,record,sb


class TransportTests(unittest.TestCase):
    def test_mock_complete_stream_check_and_exact_worker_stage(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root)
            self.assertEqual(record['status'],'complete');self.assertTrue(driver.check(out,allow_inner=True)['transport_evidence_integrity'])
            self.assertEqual({Path(p).name for p in sb.stage if '/source/' in p},c.WORKER)
            self.assertEqual(sb.events[-1],('terminate',True))
            self.assertEqual(record['vm_creates'],1);self.assertEqual(record['engine_execs'],1)
    def test_pinned_installed_sdk_ast_contract_no_import(self):
        sdk = Path(os.environ.get('CONTROLLED_SDK_FILESYSTEM_SOURCE', '/workspace/classical-ecdlp-endpoint-reuse/runtime-20261028/lib/python3.12/site-packages/modal/sandbox/_filesystem.py'))
        data = sdk.read_bytes()
        self.assertEqual(c.sha_bytes(data), '19d90c3556a13e95297ee634e07c165b06723080f76dcbadecf1d7356388a588')
        tree = ast.parse(data)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == '_SandboxFilesystem')
        methods = {n.name:n for n in cls.body if isinstance(n, ast.AsyncFunctionDef)}
        expected = {'stat':['self','remote_path'], 'read_bytes':['self','remote_path'],
                    'write_bytes':['self','data','remote_path'], 'copy_to_local':['self','remote_path','local_path']}
        fake = ast.parse(Path(__file__).read_bytes())
        fake_cls = next(n for n in fake.body if isinstance(n, ast.ClassDef) and n.name == 'Filesystem')
        fake_methods = {n.name:n for n in fake_cls.body if isinstance(n, ast.FunctionDef)}
        for name, args in expected.items():
            self.assertEqual([a.arg for a in methods[name].args.args], args)
            self.assertEqual([a.arg for a in fake_methods[name].args.args], args)
        self.assertIn('not the target', ast.get_docstring(methods['stat']))
        copy_tree = methods['copy_to_local']
        self.assertTrue(any(isinstance(n, ast.AsyncFor) for n in ast.walk(copy_tree)))
        self.assertFalse(hasattr(Sandbox({}), 'open'))
        controller = ast.parse(Path(c.__file__).read_bytes())
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                             and n.func.attr == 'open' and isinstance(n.func.value, ast.Name)
                             and n.func.value.id in {'sb','sandbox'} for n in ast.walk(controller)))

    def test_metadata_bounds_type_length_and_hash_refuse_before_engine(self):
        def size_mutant(remote, info):
            if remote.endswith('build-info.json'): info.size = (1 << 20) + 1
        def type_mutant(remote, info):
            if remote.endswith('build-info.json'): info.type = FileType.DIRECTORY
        def link_mutant(remote, info):
            if remote == '/opt': info.type = FileType.SYMLINK; info.symlink_target = '/elsewhere'
        configurations = [lambda sb:setattr(sb.filesystem,'info_mutant',size_mutant),
                          lambda sb:setattr(sb.filesystem,'info_mutant',type_mutant),
                          lambda sb:setattr(sb.filesystem,'info_mutant',link_mutant),
                          lambda sb:setattr(sb.filesystem,'metadata',b'[]'),
                          lambda sb:setattr(sb.filesystem,'read_bytes',lambda remote_path:b'{} '),
                          lambda sb:setattr(sb.filesystem,'read_bytes',None),
                          lambda sb:setattr(sb.filesystem,'write_bytes',lambda remote_path:None)]
        for configure in configurations:
            with self.subTest(configure=configure), tempfile.TemporaryDirectory() as root:
                out, record, sb = mocked_run(root, configure=configure)
                self.assertEqual(record['status'], 'failed')
                self.assertEqual(record['engine_execs'], 0)
                self.assertFalse(record['collection_complete'])
                self.assertIsNone(record['termination_ack'])

    def test_collection_streams_and_refuses_remote_type_size_partial_and_hash(self):
        for mutant in ['oversize','size','type','symlink','ancestor','partial','hash','short','local-symlink','copy-error']:
            with self.subTest(mutant=mutant), tempfile.TemporaryDirectory() as root:
                files = {'raw/traces.jsonl':b'disclosed F11 fixture\n'}
                sb = Sandbox(files); fs = sb.filesystem
                entry = {'path':'raw/traces.jsonl','sha256':c.sha_bytes(files['raw/traces.jsonl']), 'size':len(files['raw/traces.jsonl'])}
                def info_mutant(remote, info):
                    if remote == '/work/result/raw' and mutant == 'ancestor':
                        info.type = FileType.SYMLINK; info.symlink_target='/elsewhere'
                    if remote.endswith('traces.jsonl'):
                        if mutant == 'oversize': info.size = 1 << 32
                        if mutant == 'size': info.size += 1
                        if mutant == 'type': info.type = FileType.DIRECTORY
                        if mutant == 'symlink': info.type = FileType.SYMLINK; info.symlink_target='/elsewhere'
                fs.info_mutant = info_mutant
                def bad_copy(remote, local):
                    if mutant == 'local-symlink': local.symlink_to(Path(root)/'truth'); return
                    if mutant == 'copy-error': raise OSError('fixed copy failure')
                    local.write_bytes(b'x' if mutant in {'partial','short'} else b'x' * entry['size'])
                    if mutant == 'partial': raise OSError('fixed partial copy failure')
                if mutant in {'partial','hash','short','local-symlink','copy-error'}: fs.copy_mutant = bad_copy
                # Collection must never use the buffering API, even for tiny fixtures.
                fs.read_bytes = lambda remote: (_ for _ in ()).throw(AssertionError('buffered collection'))
                with self.assertRaises((ValueError, OSError)):
                    c.collect_stream(sb, Path(root)/'collected', [entry], {'max_file_bytes':1024,'max_total_bytes':1024})
                self.assertFalse((Path(root)/'collected/raw/traces.jsonl').exists())
                self.assertTrue((Path(root)/'collected.partial').is_dir())
                self.assertNotIn(('terminate',True), sb.events)

    def test_hash_mutant(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root)
            p=out/'collected/raw/traces.jsonl';p.chmod(0o644);p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaises(ValueError):driver.check(out,allow_inner=True)
    def test_no_fake_termination_ack(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,sb=mocked_run(root,True)
            self.assertEqual(record['status'],'failed');self.assertIsNone(record['termination_ack'])
            self.assertTrue((out/'collected/raw/traces.jsonl').is_file())
            self.assertEqual(driver.check(out,allow_inner=True)['operational_status'],'failed')
            with self.assertRaises(ValueError):c.custody_for(out/'collected',record)
    def test_partial_collection_retained_without_retry(self):
        with tempfile.TemporaryDirectory() as root:
            files,_,_=fixture();entries=[{'path':p,'sha256':c.sha_bytes(b),'size':len(b)} for p,b in files.items()]
            entries[1]['sha256']='ff'*32
            with self.assertRaises(ValueError):c.collect_stream(Sandbox(files),Path(root)/'partial',entries,{'max_file_bytes':1<<24,'max_total_bytes':1<<26})
            self.assertTrue((Path(root)/'partial.partial').is_dir())
    def test_failed_copy_retains_partial_and_never_claims_termination_ack(self):
        def configure(sb):
            def copy(remote, target):
                Path(target).write_bytes(b'fixed partial')
                raise OSError('fixed collection refusal')
            sb.filesystem.copy_mutant = copy
        with tempfile.TemporaryDirectory() as root:
            out, record, sb = mocked_run(root, configure=configure)
            self.assertEqual(record['status'], 'failed')
            self.assertEqual(record['engine_execs'], 1)
            self.assertFalse(record['collection_complete'])
            self.assertTrue(record['remote_preserved_for_collection'])
            self.assertIsNone(record['termination_ack'])
            self.assertTrue((out/'collected.partial').is_dir())
            self.assertNotIn(('terminate', True), sb.events)

    def test_paths_duplicates_schema_resource_bounds(self):
        with tempfile.TemporaryDirectory() as root:
            for p in ['../truth','/truth','a/../b','a//b','a\\b']:
                with self.assertRaises(ValueError):c.safe(root,p)
            with self.assertRaises(ValueError):json.loads('{"truth":0,"truth":1}',object_pairs_hook=c.unique)
            entry={'path':'raw/traces.jsonl','sha256':'00'*32,'size':8}
            for entries in [[entry,entry],[{**entry,'path':'../truth'}],[{**entry,'size':999}],[{**entry,'truth':7}]]:
                with self.assertRaises(ValueError):c.validate_entries(entries,{'max_file_bytes':10,'max_total_bytes':20})
    def test_committed_source_hash_and_manifest_mutants(self):
        with tempfile.TemporaryDirectory() as root:
            files={c.PREFIX+'/'+n:b'import hashlib\n' for n in c.WORKER}
            for name,data in files.items():
                path=Path(root)/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            manifest={'schema':c.SCHEMA+'worker-source-manifest/v1','source_revision':'a'*40,'files':{n:c.sha_bytes(b) for n,b in files.items()}}
            path=Path(root)/'manifest.json';c.write(path,manifest)
            with patch.object(c.subprocess,'run'),patch.object(c.subprocess,'check_output',side_effect=lambda args,**kw:files[args[2].split(':',1)[1]]):
                c.source_payload(root,path,'worker')
                (Path(root)/c.PREFIX/'engine.py').write_bytes(b'# mismatched source\n')
                with self.assertRaises(ValueError):c.source_payload(root,path,'worker')
            manifest['source_revision']=None;path.unlink();c.write(path,manifest)
            with self.assertRaises(ValueError):c.source_payload(root,path,'worker')

    def test_supervisor_envelopes_and_zero_data_failure_archive(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)/'supervisor';out.mkdir()
            with patch.object(c,'run',side_effect=ValueError('fixed source binding failure')):
                raw=driver.run(root,'not-read-fixture',out,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
            self.assertEqual(raw['operational_status'],'failed')
            self.assertEqual(driver.check(out)['operational_status'],'failed')
            for name in ['manifest.yaml','raw-result.json','modal-evidence.tar.gz','modal-evidence-manifest.json']:
                self.assertTrue((out/name).is_file())
            self.assertIsNone(raw['controller']);self.assertEqual(raw['driver_error']['type'],'ValueError')

    def test_worker_plan_only_no_draw_or_candidate(self):
        runtime=c.module(Path(c.importlib.util.find_spec('worker_runtime').origin),'_fixture_worker_runtime')
        import types
        cohort=types.SimpleNamespace(plan=lambda:{'source_only':True})
        engine=types.SimpleNamespace()
        with patch.dict('sys.modules',{'cohort':cohort,'engine':engine}),patch.object(runtime.os,'urandom',side_effect=AssertionError('entropy forbidden in plan-only')):
            result=runtime.run({},'/not-written',plan_only=True)
        self.assertEqual(result['fresh_draws'],0);self.assertEqual(result['candidate_queries'],0)
        self.assertEqual(set(result['worker_files']),c.WORKER)

    def test_incomplete_sampler_retains_exact_public_without_candidate(self):
        runtime=c.module(Path(c.importlib.util.find_spec('worker_runtime').origin),'_incomplete_fixture_worker')
        import types
        public={'nonce':'00'*32,'curves':[]};ledger=[{'status':'CAPPED_PROPOSALS','fixture_only':True}]
        cohort=types.SimpleNamespace(build_public=lambda config:{'status':'incomplete','public':public,'ledger':ledger,'jobs':[]})
        engine=types.SimpleNamespace(run_public=lambda *a:(_ for _ in ()).throw(AssertionError('candidate must not run')))
        request={'sampler':{'curve_proposal_limit':1,'point_proposal_limit':1,'target_proposal_limit':1},'prior_exclusions':{'excluded_p_j':[]}}
        with tempfile.TemporaryDirectory() as root,patch.dict('sys.modules',{'cohort':cohort,'engine':engine}),patch.object(runtime,'runtime_check'),patch.object(runtime.os,'urandom',return_value=bytes(32)):
            result=runtime.run(request,Path(root)/'raw')
            self.assertEqual(result['status'],'incomplete')
            self.assertEqual(c.read(Path(root)/'public-cohort.json'),public)
            self.assertEqual(c.read(Path(root)/'cohort-ledger.json'),ledger)
            self.assertTrue((Path(root)/'sampler-failure.json').is_file());self.assertFalse((Path(root)/'raw').exists())

    def test_successful_supervisor_envelope_archive_check(self):
        import shutil
        with tempfile.TemporaryDirectory() as root:
            source,record,sb=mocked_run(root)
            protocol=Path(root)/'fixture-protocol.json';c.write(protocol,{'protocol_id':'EXP-FIXTURE'})
            config={'inputs':{'protocol':{'path':protocol.name}}}
            out=Path(root)/'supervisor';out.mkdir()
            def completed(repo,config_path,dest,sdk=None,supervisor_identity=None):
                record['supervisor_identity']=supervisor_identity
                shutil.copytree(source,dest)
                (dest/'protocol.json').unlink();c.write(dest/'protocol.json',{'protocol_id':'EXP-FIXTURE'})
                (dest/'controller-receipt.json').unlink();c.write(dest/'controller-receipt.json',record)
                return record
            with patch.object(c,'run',side_effect=completed):
                result=driver.run(root,config,out,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
            self.assertEqual(result['operational_status'],'completed')
            self.assertEqual(driver.check(out)['operational_status'],'complete')
            self.assertTrue((out/'manifest.yaml').is_file())

    def test_dependency_closure(self):
        good={n:b'import hashlib\n' for n in c.WORKER};c.audit_closure(good)
        for payload in [b'import host.verify\n',b'import reference\n',b'__import__("host")\n']:
            with self.assertRaises(ValueError):c.audit_closure({**good,'engine.py':payload})


    def test_strict_static_json_rejects_nonfinite_overflow_and_duplicates(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'input.json'
            for data in [b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1e999}',b'{"x":0,"x":1}']:
                path.write_bytes(data)
                with self.assertRaises(ValueError):c.read(path)

    def test_custody_capability_rejects_duplicate_and_missing_required_entries(self):
        for mutant in ['duplicate','host-plan','public-cohort']:
            with self.subTest(mutant=mutant),tempfile.TemporaryDirectory() as root:
                out,record,_=mocked_run(root)
                if mutant=='duplicate':record['files'].append(copy.deepcopy(record['files'][0]))
                else:record['files']=[e for e in record['files'] if e['path']!=mutant+'.json']
                with self.assertRaises(ValueError):c.custody_for(out/'collected',record)

    def test_inner_transport_scope_is_explicit(self):
        with tempfile.TemporaryDirectory() as root:
            out,record,_=mocked_run(root)
            with self.assertRaisesRegex(ValueError,'supervisor envelope required'):driver.check(out)
            self.assertEqual(driver.check(out,allow_inner=True)['integrity_scope'],'inner_transport_only')

    def test_supervisor_resealed_identity_status_member_and_receipt_mutants(self):
        import shutil
        for mutant in ['manifest-id','raw-id','manifest-status','controller-id','protocol-id','extra-member','missing-member','duplicate-member','duplicate-receipt']:
            with self.subTest(mutant=mutant),tempfile.TemporaryDirectory() as root:
                source,record,_=mocked_run(root)
                c.write(Path(root)/'protocol.json',{'protocol_id':'EXP-FIXTURE'})
                out=Path(root)/'supervisor';out.mkdir()
                def completed(repo,cfg,dest,sdk=None,supervisor_identity=None):
                    record['supervisor_identity']=supervisor_identity
                    shutil.copytree(source,dest)
                    for name,value in [('protocol.json',{'protocol_id':'EXP-FIXTURE'}),('controller-receipt.json',record)]:
                        (dest/name).unlink();c.write(dest/name,value)
                    return record
                with patch.object(c,'run',side_effect=completed):
                    driver.run(root,{'inputs':{'protocol':{'path':'protocol.json'}}},out,experiment_id='EXP-FIXTURE',run_id='RUN-FIXTURE')
                self.assertEqual(driver.check(out)['run_id'],'RUN-FIXTURE')
                raw=c.read(out/'raw-result.json');manifest=c.read(out/'manifest.yaml')
                if mutant=='manifest-id':manifest['run']['id']='RUN-WRONG'
                if mutant=='raw-id':raw['run_id']='RUN-OTHER'
                if mutant=='manifest-status':manifest['run']['status']='failed'
                if mutant=='controller-id':raw['controller']['supervisor_identity']['run_id']='RUN-OTHER'
                if mutant=='protocol-id':
                    (out/'modal/protocol.json').unlink();c.write(out/'modal/protocol.json',{'protocol_id':'EXP-OTHER'})
                if mutant=='extra-member':c.write(out/'modal/unbound.json',{'extra':True})
                if mutant=='missing-member':(out/'modal/controller-receipt.json').unlink()
                if mutant=='duplicate-receipt':raw['controller']['engine_execs']=99
                if mutant=='duplicate-member':
                    member=c.read(out/'modal-evidence-manifest.json');member['files'].append(copy.deepcopy(member['files'][0]))
                    (out/'modal-evidence-manifest.json').unlink();c.write(out/'modal-evidence-manifest.json',member)
                    raw['evidence']['member_manifest_sha256']=c.sha_file(out/'modal-evidence-manifest.json')
                for name,value in [('manifest.yaml',manifest),('raw-result.json',raw)]:
                    (out/name).unlink();c.write(out/name,value)
                with self.assertRaises((ValueError,FileNotFoundError)):driver.check(out)

    def test_audit_static_scope_does_not_claim_alias_isolation(self):
        good={n:b'import hashlib\n' for n in c.WORKER}
        # A known alias gap is retained explicitly; this screen is not isolation.
        c.audit_closure({**good,'engine.py':b'import importlib as loader\nh=loader.import_module("host.verify")\n'})
        self.assertIn('outside this screen',c.audit_closure.__doc__)


if __name__=='__main__':unittest.main()
