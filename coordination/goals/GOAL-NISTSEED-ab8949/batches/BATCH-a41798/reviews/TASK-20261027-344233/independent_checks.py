"""Independent engineering checks for TASK-20261027-344233.

Written in the independent validator session; executed only by the parent.
No integrated_runner import, producer test import, process, VM, legacy,
curve, network or remote-storage operation is permitted. Fixtures are synthetic
format exercises. Integer formatting here is not a primality evaluation.
Every fixture remains beneath this review directory for diagnosis.
"""
from __future__ import annotations
import ast
import base64
import contextlib
import copy
import gzip
import hashlib
import importlib.abc
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tarfile
import tempfile
import traceback
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
REL = 'experiments/EXP-NISTSEED-6886da'
EXP = ROOT / REL
PRODUCER = EXP / 'integration/tasks/TASK-20261027-275b12'
COMPAT = ROOT / 'research/nist_seed_ecpp_compat_20261024'
BATCH = ROOT / 'coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-a41798'
COUNTS = {'forbidden_calls': 0, 'local_processes': 0, 'real_vm': 0, 'real_program': 0, 'cohort': 0, 'storage': 0}
RESULTS = []
SOURCES = set()
SUP = ('launch.json', 'environment.json', 'command.txt', 'stdout.log', 'stderr.log')
PARGV = ['/program', '-l', '/ecpp/', '-f', '/input', '-Fc', '-C', '/tmp/certificate']
CARGV = ['/program', '-f', '/input']
PHASE = {'source':'ECPP/Ecpp/C/c/ecpp.c',
 'source_sha256':'16766d2b73a5424b4252d0d75ba5a4346fae1d908ecc04eb7bca8bf1930071e2',
 'archive_sha256':'0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f',
 'rule':'^% Starting phase (1: building the sequence of primes|2: proving)$',
 'scope':'Printed original-program output signature; not proof of successful exec or complete computation.'}

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p):
    p = Path(p)
    try:
        if not p.absolute().is_relative_to(HERE):
            SOURCES.add(p.relative_to(ROOT).as_posix())
    except ValueError:
        pass
    return p.read_bytes()
def load(p): return json.loads(read(p))
def put(p, b):
    p = Path(p)
    assert p.resolve(strict=False).is_relative_to(HERE), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
def dump(p, x): put(p, (json.dumps(x, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())
def literal(p, name):
    tree = ast.parse(read(p))
    for item in tree.body:
        if isinstance(item, (ast.Assign, ast.AnnAssign)):
            targets = item.targets if isinstance(item, ast.Assign) else [item.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                return ast.literal_eval(item.value)
    raise AssertionError('literal missing: '+name)
def module(p, name):
    assert Path(p).name not in ('integrated_runner.py', 'test_integration.py', 'cohort_runner.py', 'cohort_case.py', 'qemu_controls.py')
    SOURCES.add(Path(p).relative_to(ROOT).as_posix())
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
def forbidden(*a, **kw):
    COUNTS['forbidden_calls'] += 1
    raise AssertionError('forbidden execution/network/storage seam reached')
class BlockImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'qemu_controls','cohort_case','cohort_runner','integrated_runner','boto3','botocore','artifact_store','sage','cypari2','sympy'}:
            forbidden(fullname)
        return None
@contextlib.contextmanager
def guards():
    finder = BlockImports()
    sys.meta_path.insert(0, finder)
    with contextlib.ExitStack() as stack:
        for name in ('Popen','run','call','check_call','check_output'):
            stack.enter_context(mock.patch.object(subprocess, name, forbidden))
        for name in ('system','popen','fork','posix_spawn','posix_spawnp','execv','execve','execl','execlp','execvp','execvpe','spawnv','spawnve','spawnvp','spawnvpe'):
            if hasattr(os, name): stack.enter_context(mock.patch.object(os, name, forbidden))
        stack.enter_context(mock.patch.object(socket, 'socket', forbidden))
        try: yield
        finally: sys.meta_path.remove(finder)

def audit(event, args):
    if event in {'subprocess.Popen','os.system','os.fork','os.posix_spawn','socket.connect','socket.bind'}:
        forbidden(event)
    if event == 'open':
        path = args[0]
        if isinstance(path, (str, bytes, os.PathLike)):
            p = Path(os.fsdecode(path)).absolute()
            if p.is_relative_to(COMPAT / '.work'):
                forbidden('real-runtime read')
            mode = args[1] if len(args)>1 else None
            flags = args[2] if len(args)>2 else 0
            writing = isinstance(mode,str) and any(x in mode for x in 'wax+')
            writing = writing or (isinstance(flags,int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)))
            if writing and not p.resolve(strict=False).is_relative_to(HERE):
                forbidden('out-of-review write')

def run(name, fn):
    try:
        value = fn()
        RESULTS.append({'name':name, 'execution':'parent', 'outcome':'PASS', 'observation':value})
    except BaseException as e:
        RESULTS.append({'name':name, 'execution':'parent', 'outcome':'FAIL',
                        'error':type(e).__name__+': '+str(e), 'traceback':traceback.format_exc()})

def strict(serial):
    s = serial.replace(b'\r\n', b'\n')
    names = [b'__ECPP_INIT_ABI__',b'__ECPP_GUEST_BEGIN__',b'__ECPP_CHILD_EXIT__',b'__ECPP_GUEST_COMPLETE__']
    patterns = [rb'^__ECPP_INIT_ABI__ 4 4 4\n',rb'^__ECPP_GUEST_BEGIN__\n',
                rb'^__ECPP_CHILD_EXIT__ ([0-9]+) timeout=([0-9]+)\n',rb'^__ECPP_GUEST_COMPLETE__\n']
    found = [list(re.finditer(p,s,re.M)) for p in patterns]
    if any(len(x)!=1 or s.count(n)!=1 for x,n in zip(found,names)): return None
    a,b,e,c = [x[0] for x in found]
    if not a.start()<b.start()<e.start()<c.start() or s[e.start()-1:e.start()]!=b'\n': return None
    cb = list(re.finditer(rb'^__ECPP_CERTIFICATE_BEGIN__\n',s,re.M))
    ce = list(re.finditer(rb'^__ECPP_CERTIFICATE_END__\n',s,re.M))
    if len(cb)!=len(ce) or len(cb)>1 or s.count(b'__ECPP_CERTIFICATE_BEGIN__')!=len(cb) or s.count(b'__ECPP_CERTIFICATE_END__')!=len(ce): return None
    certs=[]
    if cb:
        if not e.end()<=cb[0].start()<ce[0].start()<c.start() or s[ce[0].start()-1:ce[0].start()]!=b'\n': return None
        certs=[s[cb[0].end():ce[0].start()-1]]
    return {'body':s[b.end():e.start()-1], 'certificates':certs, 'child_exit':int(e[1]), 'timeout':int(e[2])}

def framed(body, cert=None, child=0):
    s=b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n'+body+('\n__ECPP_CHILD_EXIT__ %d timeout=0\n'%child).encode()
    if cert is not None: s+=b'__ECPP_CERTIFICATE_BEGIN__\n'+cert+b'\n__ECPP_CERTIFICATE_END__\n'
    return s+b'__ECPP_GUEST_COMPLETE__\n'

def prior_map(rows):
    omitted=load(ROOT/'research/nist_seed_skipped_curves_20261016/assessed.json')['candidate_rows']
    published=load(ROOT/'research/nist_seed_skipped_curves_20261016/traits.json')['published_controls']
    records={x['identity']['curve_uid']:(lab,x) for lab,ls in [('omitted',omitted),('published',list(published.values()))] for x in ls}
    corpus=[json.loads(x) for x in read(ROOT/'research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl').splitlines() if x]
    number=lambda n: int(n,0) if isinstance(n,str) else n
    canonical=lambda x:sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
    answer={}
    for row in rows:
        lab,source=records[row['curve_uid']]; identity=source['identity']; curve=identity['curve']
        assert lab==row['label'] and identity['curve_id']==row['curve_id']
        assert number(identity['field']['characteristic'])==number(row['p']) and number(curve['subgroup_order'])==number(row['n']) and curve['cofactor']==1
        b=number(source['b_hex'])
        selected=[x for x in corpus if x.get('record')=='certificate' and number(x['p'])==number(row['p']) and number(x['n'])==number(row['n']) and number(x['b'])==b and x['index']==row['ordinal'] and x['run']==row['timestamp'] and x['seed'].lower()==row['seed_hex'].lower()]
        assert len(selected)==1
        x=selected[0]; keys=('on_curve','n_prime_pari','n_times_point_identity','order_certified','n_in_hasse_interval','hasse_interval_narrower_than_n')
        assert all(x.get(k) is True for k in keys)
        answer[row['curve_uid']]={'label':lab,'curve_id':row['curve_id'],'p':str(number(row['p'])),'n':str(number(row['n'])),
            'a4':str(number(curve['a4'])),'a6':str(number(curve['a6'])),'b':str(b),'cofactor':1,'corpus_side':x['side'],
            'corpus_record_sha256':canonical(x),'provenance_record_sha256':canonical(source),'prior_booleans':dict.fromkeys(keys,True)}
    return answer

CHECKER=None
CTX=None
WORK=None

class Fixture:
    """Independently authored envelopes; no producer driver or test code."""
    def __init__(self, mode='complete'):
        self.root=Path(tempfile.mkdtemp(prefix=mode+'-',dir=WORK))
        self.out=self.root/'trial'; self.cap=self.root/'capture'; self.binding=self.root/'binding.json'
        self.out.mkdir(); self.cap.mkdir(); catalog=self.root/'catalog'; catalog.mkdir()
        put(catalog/'ecpp.DfD',b'(() 0 0)\n')
        self.profile={'scope':'EXPLICIT_SYNTHETIC_FIXTURE_ONLY','catalog_directory':str(catalog),
                      'image_sha256':{'prover':sha(b'independent fixture prover'),'checker':sha(b'independent fixture checker')}}
        self.row=CTX['rows'][0]; self.cert=(self.row['n']+' -1 0 '+self.row['n']+' 0 0').encode()
        self.payload=(self.row['n']+'\n').encode()
        self.bound={'schema':'crypto.autoresearch.nistseed_ecpp_trial_binding.v1','cohort_index':0,'output_directory':str(self.out),
            'driver_capture_directory':str(self.cap),'frozen_input_sha256':CTX['frozen'],'limits':CTX['limits'],'primary_configuration':CTX['primary']}
        dump(self.binding,self.bound); dump(self.out/'input-binding-manifest.json',self.bound)
        argv=['independent-synthetic-driver','--index','0','--output',str(self.out),'--binding',str(self.binding)]
        dump(self.out/'launch.json',{'argv':argv,'authority':{'task':'TASK-20261027-344233','scope':'independent synthetic bytes only'}})
        dump(self.out/'environment.json',{'scope':'independent synthetic bytes only'}); dump(self.out/'command.txt',argv)
        for name in ('stdout.log','stderr.log'):
            put(self.out/name,b'independent supervisor provenance\n')
            put(self.cap/name,b'')
        put(self.out/'driver.stdout.log',b''); put(self.out/'driver.stderr.log',b'')
        dump(self.out/'integration-boundary-call.json',{'schema':'crypto.autoresearch.nistseed_ecpp_boundary_call.v1','cohort_index':0,
            'mode':'synthetic','evidence_kind':'whole_boundary_call_attempt_not_program_start'})
        self.items={}
        if mode!='early':
            identity={'curve':self.row,'cohort_sha256':CTX['frozen']['research/nist_seed_ecpp_compat_20261024/cohort-inputs.json'],
                'bindings_sha256':CTX['frozen']['research/nist_seed_ecpp_compat_20261024/runtime-bindings.json'],
                'launcher_sha256':CTX['frozen']['research/nist_seed_ecpp_compat_20261024/cohort_case.py'],
                'fresh_process_rng':'original ModInitialize: srandom(1)','prover_guest_limit_seconds':300,'prover_host_limit_seconds':390,
                'classification_scope':'legacy prover/checker behavior on an already-certified prime integer'}
            dump(self.out/'legacy-child/identity.json',identity)
            for stage in ('prover','checker'):
                if mode in ('launch_only','guest_only','partial') and stage=='checker': continue
                p=stage=='prover'; payload=self.payload if p else self.cert
                start=self.launch(stage,payload); dump(self.out/'legacy-child'/stage/'started.json',start)
                if mode=='launch_only': continue
                body=b'This number is prime\n' if p else b' 0: -1 1 0.00s\n'
                serial=framed(body,self.cert if p else None,139 if mode=='nonzero' and p else 0)
                if mode=='guest_only': serial=b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n'
                if mode=='partial': serial=b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n% Starting phase 1: building the sequence of primes\n% Factor= 2^'
                changes={'no_begin':(b'__ECPP_GUEST_BEGIN__\n',b''),'duplicate_begin':(b'__ECPP_GUEST_BEGIN__\n',b'__ECPP_GUEST_BEGIN__\n'*2),
                    'bad_abi':(b'__ECPP_INIT_ABI__ 4 4 4',b'__ECPP_INIT_ABI__ 8 8 8'),
                    'no_exit':(b'__ECPP_CHILD_EXIT__ 0 timeout=0\n',b''),'no_complete':(b'__ECPP_GUEST_COMPLETE__\n',b''),
                    'misorder':(b'__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n',b'__ECPP_GUEST_BEGIN__\n__ECPP_INIT_ABI__ 4 4 4\n'),
                    'truncated_cert':(b'__ECPP_CERTIFICATE_END__\n',b'__ECPP_CERTIFICATE_EN')}
                if p and mode in changes: serial=serial.replace(*changes[mode])
                if mode=='checker_malformed' and not p: serial=serial.replace(b'__ECPP_GUEST_COMPLETE__\n',b'__ECPP_GUEST_COMPLETE')
                if mode=='checker_step' and not p:
                    body=b' 0: -1 0 0.00s\n'; serial=framed(body)
                put(self.out/'legacy-child'/stage/'serial.raw',serial)
                if mode in ('guest_only','partial'): continue
                status={'vm_valid':True,'qemu_exit':None if mode=='watchdog' and p else 33,
                    'child_exit':139 if mode=='nonzero' and p else 0,'reason':'host_watchdog' if mode=='watchdog' and p else None,
                    'elapsed_host_seconds':1,'serial_sha256':sha(serial),'certificate_count':1 if p else 0}
                dump(self.out/'legacy-child'/stage/'result.json',status); put(self.out/'legacy-child'/stage/'program.stdout',body)
                put(self.out/'legacy-child'/stage/'qemu.stderr',b'')
            if mode not in ('launch_only','guest_only','partial'):
                put(self.out/'legacy-child/prover/certificate.cformat',self.cert)
        self.finalize(mode)

    def launch(self,stage,payload):
        p=stage=='prover'; img=self.profile['image_sha256'][stage]; cache=self.out/'runtime-cache'
        args=['/opt/homebrew/bin/qemu-system-i386','-machine','pc,accel=tcg','-cpu','max','-m','256','-smp','1',
            '-nodefaults','-no-user-config','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot',
            '-device','isa-debug-exit,iobase=0xf4,iosize=4','-kernel',str(cache/'vmlinuz-lts'),
            '-initrd',str(cache/'images'/(img+'.cpio.gz')),'-append','console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on']
        artifacts={Path(x['logical_path']).name:x['sha256'] for x in CTX['runtime']['artifacts']}
        return {'utc':'2026-10-27T00:00:00Z','command':args,'program_sha256':artifacts['runecpp' if p else 'checkcertif'],
            'init_sha256':artifacts['qemu-init'],'initramfs_sha256':img,'input_sha256':sha(payload),'stdin_sha256':sha(b''),
            'data_mode':'full' if p else None,'guest_limit_seconds':300 if p else 30,'host_limit_seconds':390 if p else 90}
    def evidence(self,stage,path,kind,offset=None,length=None,rule=None):
        return {'path':path,'sha256':sha(read(self.out/path)),'stage':stage,'kind':kind,'byte_offset':offset,'byte_length':length,'source_rule':rule,'synthetic':True}
    def account(self,stage):
        d=self.out/'legacy-child'/stage
        serial=read(d/'serial.raw') if (d/'serial.raw').exists() else None
        status=load(d/'result.json') if (d/'result.json').exists() else None
        frame=strict(serial) if serial is not None else None
        proofs=[]; launch=(d/'started.json').exists(); guest=False; output=False
        if launch: proofs.append(self.evidence(stage,'legacy-child/'+stage+'/started.json','launch_intent_before_subprocess',rule='qemu_controls.py: vm writes started.json before subprocess.run'))
        if serial is not None:
            path='legacy-child/'+stage+'/serial.raw'
            a=list(re.finditer(rb'^__ECPP_INIT_ABI__ 4 4 4\r?\n',serial,re.M)); b=list(re.finditer(rb'^__ECPP_GUEST_BEGIN__\r?\n',serial,re.M))
            guest=len(a)==len(b)==1 and a[0].start()<b[0].start()
            for kind,events in [('guest_abi',a),('guest_init_begin_before_fork_exec',b)]:
                for x in events: proofs.append(self.evidence(stage,path,kind,x.start(),x.end()-x.start(),'qemu_init.c: ABI and begin precede fork/execv'))
            if stage=='prover':
                for x in re.finditer(rb'^% Starting phase (?:1: building the sequence of primes|2: proving)\r?\n',serial,re.M):
                    output=True; proofs.append(self.evidence(stage,path,'source_backed_program_output',x.start(),x.end()-x.start(),PHASE))
            proofs.append(self.evidence(stage,path,'raw_serial_retained'))
        good=bool(status is not None and frame is not None and status['qemu_exit']==33 and status['child_exit']==frame['child_exit'] and status['reason'] is None and not frame['timeout'] and status['serial_sha256']==sha(serial) and status['certificate_count']==len(frame['certificates']) and read(d/'program.stdout')==frame['body'])
        if status is not None and frame is not None and serial is not None:
            proofs.append(self.evidence(stage,'legacy-child/'+stage+'/result.json','retained_primitive_status'))
        self.items[stage]={'serial':serial,'status':status,'frame':frame}
        return {'launch_intent':int(launch),'guest_init_observed':int(guest),'program_output_observed':int(output),
            'stage_completed_success':int(good and frame['child_exit']==0),'stage_completed_failure':int(good and frame['child_exit']!=0),
            'exact_program_starts':None,'program_start_observed_lower_bound':int(output),
            'program_start_unobserved_or_ambiguous':int(bool(launch or guest or serial is not None) and not output),
            'framing_state':'UNAVAILABLE' if serial is None else 'COMPLETE' if frame else 'MALFORMED',
            'status_state':'UNAVAILABLE' if status is None else 'RECONCILED' if good else 'UNRECONCILED','errors':[],'evidence':proofs}
    def capsule(self):
        paths={p.relative_to(self.out).as_posix():p for p in (self.out/'legacy-child').rglob('*') if p.is_file()} if (self.out/'legacy-child').exists() else {}
        for n in ('driver.stdout.log','driver.stderr.log','supplemental-trace.json'):
            if (self.out/n).exists(): paths[n]=self.out/n
        buffer=io.BytesIO(); rows=[]
        with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT) as t:
                for n,p in sorted(paths.items()):
                    b=read(p); i=tarfile.TarInfo(n); i.size=len(b); i.mode=0o600; i.uid=i.gid=i.mtime=0; i.uname=i.gname=''
                    t.addfile(i,io.BytesIO(b)); rows.append({'path':n,'bytes':len(b),'sha256':sha(b)})
        b=buffer.getvalue(); put(self.out/'raw-artifacts.tar.gz',b)
        dump(self.out/'raw-artifact-inventory.json',{'schema':'crypto.autoresearch.ecpp_raw_capsule.v1','capsule':'raw-artifacts.tar.gz','bytes':len(b),'sha256':sha(b),'members':rows,'excluded_reconstructible_cache':'runtime-cache; frozen kernel/payload/catalog bindings remain separately required'})
    def resign(self, capsule=False):
        if capsule: self.capsule()
        self.env['sidecars']={p.name:{'bytes':p.stat().st_size,'sha256':sha(read(p))} for p in self.out.iterdir() if p.is_file() and p.name not in SUP and p.name!='integration-envelope.json'}
        dump(self.out/'integration-envelope.json',self.env)
    def finalize(self,mode):
        stages={s:self.account(s) for s in ('prover','checker')}
        complete=mode not in ('early','launch_only','guest_only','partial')
        supervisor={n:sha(read(self.out/n)) for n in SUP}
        if complete:
            driver={p.relative_to(self.out/'legacy-child').as_posix():sha(read(p)) for p in (self.out/'legacy-child').rglob('*') if p.is_file()}
            raw={'schema':'crypto.autoresearch.nistseed_ecpp_raw_result.v5','cohort_index':0,'curve':self.row,
                'frozen_input_sha256':CTX['frozen'],'runtime_payloads':CTX['runtime']['artifacts'],'kernel':CTX['runtime']['kernel'],
                'original_data':CTX['runtime']['original_data'],'limits':CTX['limits'],'primary_configuration':CTX['primary'],
                'prior_primality_mapping':CTX['prior'],'named_orders_executed':1,'input_binding_manifest_sha256':sha(read(self.binding)),
                'external_binding_manifest_sha256':sha(read(self.binding)),'supervisor_manifest':self.bound,'supervisor_artifact_sha256':supervisor,
                'driver_artifacts':driver,'classification':'PRIOR_PRIMALITY_EVIDENCE_REQUIRED','censoring':False}
            dump(self.out/'raw-result.json',raw)
            serial=self.items['prover']['serial']; body=b'This number is prime\n'
            obs={'curve_uid':self.row['curve_uid'],'prior_primality_evidence':CTX['prior'][self.row['curve_uid']],
                'certificate_admitted':True,'prover':self.items['prover']['status'],'checker':self.items['checker']['status'],
                'legacy_labels_observation_only':['prime'],'prover_body_sha256':sha(body),'prover_certificate_count':1,
                'trace':{'schema':'trace_schema.json','raw_serial_sha256':sha(serial),'events':[],
                         'unprinted_state':'UNOBSERVED','inference_prohibited':'unprinted branches are not reconstructed as attempted'},
                'certificate_steps':[{'n':int(self.row['n']),'D':-1,'h':0,'pratt':[int(self.row['n'])]}],
                'certificate_sha256':sha(self.cert),'mathematical_classification':'PRIOR_PRIMALITY_EVIDENCE_REQUIRED','stage':'completed'}
            dump(self.out/'observation.json',obs)
        counter={'schema':'crypto.autoresearch.nistseed_ecpp_integration_counters.v1','mode':'synthetic','selected_cohort_indices':[0],
            'boundary_calls_attempted':{'synthetic':1,'real':0},'boundary_evidence_path':'integration-boundary-call.json',
            'boundary_evidence_sha256':sha(read(self.out/'integration-boundary-call.json')),
            'legacy_selected_work_field':{'path':'raw-result.json','field':'named_orders_executed','value':1 if complete else None,'meaning':'frozen selected-work literal; never a program-start count'},
            'stages':stages,'certificate_admitted':None,'certificate_admission_state':'DEFERRED_TO_INDEPENDENT_CHECKER',
            'exact_program_start_total':None,'synthetic_evidence_contributes_to_real_execution_totals':False}
        dump(self.out/'counter-evidence.json',counter)
        recovery={'schema':'crypto.autoresearch.nistseed_ecpp_integration_recovery.v1','original_exception':None,'boundary_exceptions':[],
            'secondary_errors':[],'scope':'independent synthetic reconstruction','stages':{}}
        supplemental={'schema':'crypto.autoresearch.nistseed_ecpp_supplemental_trace.v1','stages':{}}
        grammar=literal(EXP/'integration/printed_trace.py','SOURCE_GRAMMAR')
        for s,item in self.items.items():
            serial,frame=item['serial'],item['frame']
            recovery['stages'][s]={'serial_sha256':sha(serial) if serial is not None else None,'serial_bytes':len(serial) if serial is not None else None,
                'strict_frame_available':frame is not None,'strict_body_sha256':sha(frame['body']) if frame else None,
                'strict_certificate_sha256':[sha(x) for x in frame['certificates']] if frame else None,'status_available':item['status'] is not None,'errors':[]}
            if serial is not None:
                events=[]
                if mode=='partial':
                    line=b'% Factor= 2^'; events=[{'kind':'incomplete_or_unrecognized_factor_line','raw_offset':serial.index(line),
                        'raw_bytes_base64':base64.b64encode(line).decode(),'printed':True,'complete_line':False,'preceding_printed_discriminant':None}]
                supplemental['stages'][s]={'raw_path':'legacy-child/'+s+'/serial.raw','raw_sha256':sha(serial),
                    'printed_trace':{'schema':'crypto.autoresearch.ecpp_printed_factors.v1','source_grammar':grammar,'events':events,
                        'unprinted_state':'UNOBSERVED','scope':'Printed factor tokens, not all attempted factorizations or primality evidence.'}}
        dump(self.out/'integration-recovery.json',recovery)
        if supplemental['stages']: dump(self.out/'supplemental-trace.json',supplemental)
        self.env={'schema':'crypto.autoresearch.nistseed_ecpp_integration.v1','mode':'synthetic','cohort_index':0,
            'identity':{'source_pins':CTX['pins'],'frozen_input_sha256':CTX['frozen'],'curve':self.row,'ordered_cohort':CTX['rows'],
                'prior_primality_mapping':CTX['prior'],'runtime':CTX['runtime'],'limits':CTX['limits'],'primary_configuration':CTX['primary'],
                'prover_argv':PARGV,'checker_argv':CARGV},
            'external_binding':{'path':str(self.binding),'sha256':sha(read(self.binding))},'supervisor_artifact_sha256':supervisor,
            'capture_directory':str(self.cap),'synthetic_profile':self.profile,'real_admission_receipt':None,
            'runtime_cache':{'state':'SYNTHETIC_NO_RUNTIME_CACHE','sha256':{}},'sidecars':{},
            'finalization':{'state':'COMPLETE','errors':[],'capsule':'raw-artifacts.tar.gz','inventory':'raw-artifact-inventory.json'},
            'claim_scope':'Independent synthetic format/custody controls only.'}
        self.resign(capsule=True)
    def check(self): return CHECKER.check(self.out,self.binding,synthetic_profile=self.profile)

def ordinary():
    f=Fixture(); v=f.check()
    assert v['custody_valid'] and v['synthetic_admission'] and not v['scientific_admission'],v
    return f
def refuse(f,gate):
    try: f.check()
    except CHECKER.CheckFailure as e:
        assert str(e).startswith(gate+':'),str(e)
        return {'gate':gate,'error':str(e)}
    raise AssertionError('intended '+gate+' refusal did not occur')
def malformed(mode,expected):
    ordinary(); f=Fixture(mode); v=f.check()
    assert v['custody_valid'] and not v['synthetic_admission'] and not v['scientific_admission'],v
    assert expected in v['admission_failures'],v
    return {'mode':mode,'failures':v['admission_failures'],'stages':v['counters']['stages']}
def aa_doc():
    schema=load(EXP/'aa-admission/aa_fixture_schema.json')
    runtime=schema['$defs']['document']['properties']['runtime']['properties']
    cert=b'101 -1 0 101 0 0'
    return {'fixture':{'id':'public-prime101-default','public_input':'101\n'},
        'trace':{'prover_events':[{'raw_hex':b'This number is prime'.hex()}],'checker_events':[{'raw_hex':b'0: -1 1 '.hex()}]},
        'prover':{'qemu_exit':33,'child_exit':0,'reason':None,'elapsed_host_seconds':1},
        'checker':{'qemu_exit':33,'child_exit':0,'reason':None,'elapsed_host_seconds':1},
        'certificate':{'root':101,'steps':[{'n':101,'D':-1,'h':0,'pratt':[101]}],'bytes_sha256':sha(cert)},
        'classification':'PRIOR_PRIMALITY_EVIDENCE_REQUIRED','labels':['prime'],
        'runtime':{'binding_manifest_sha256':'1'*64,'primary_configuration':runtime['primary_configuration']['const'],'limits':runtime['limits']['const']}}

def setup():
    global CHECKER,CTX,WORK
    receipt=BATCH/'archives/TASK-20261027-2ce9dc/snapshot-receipt.json'
    assert sha(read(receipt))=='61a773b93f695a8434436c5350d307f57a671701cb03769f419b342cfe32b423'
    archive=load(receipt)
    for p,h in archive['path_sha256'].items(): assert sha(read(ROOT/p))==h,(p,h)
    manifest_path=ROOT/'coordination/goals/GOAL-NISTSEED-ab8949/integration-admission-20261027/source-inputs.json'
    assert sha(read(manifest_path))=='47341a3e609a595e80c82042029377eec129dc9a29347bf75430e1e1d4339f62'
    manifest=load(manifest_path); pins={manifest_path.relative_to(ROOT).as_posix():sha(read(manifest_path))}
    assert len(manifest['inputs'])==23
    for x in manifest['inputs']:
        assert sha(read(ROOT/x['path']))==x['sha256'],x['path']; pins[x['path']]=x['sha256']
    contract=read(BATCH/'INTEGRATION_CONTRACT.md').decode()
    for p,h in re.findall(r'^- ([^\s:]+): ([0-9a-f]{64})$',contract,re.M):
        assert sha(read(ROOT/p))==h,p; pins[p]=h
    frozen=literal(EXP/'implementation/cohort_checker.py','FROZEN')
    for p,h in frozen.items(): assert sha(read(ROOT/p))==h,p
    rows=load(COMPAT/'cohort-inputs.json')['rows']; assert len(rows)==len({x['curve_uid'] for x in rows})==21
    assert sum(x['label']=='omitted' for x in rows)==11 and sum(x['label']=='published' for x in rows)==10
    CTX={'rows':rows,'runtime':load(COMPAT/'runtime-bindings.json'),'frozen':frozen,'pins':pins,
        'limits':literal(EXP/'implementation/cohort_checker.py','LIMITS'),'primary':literal(EXP/'implementation/cohort_checker.py','PRIMARY'),
        'prior':prior_map(rows)}
    CHECKER=module(PRODUCER/'integrated_checker.py','independent_subject_checker')
    WORK=HERE/'_independent_fixtures'; WORK.mkdir(exist_ok=True)
    return {'archived_paths_checked':len(archive['path_sha256']),'source_bindings':len(pins),'rows':len(rows),'omitted':11,'published':10}

def aa_bad_steps():
    good=aa_doc(); assert CHECKER.check_aa_documents(good,copy.deepcopy(good))['equal']
    bad=copy.deepcopy(good)
    bad['certificate']['steps']=[{'n':101,'D':-1,'h':0,'pratt':[103]}]
    bad['certificate']['bytes_sha256']=sha(b'101 -1 0 103 0 0')
    try:
        observed=CHECKER.check_aa_documents(bad,copy.deepcopy(bad))
    except CHECKER.CheckFailure as e:
        return {'required':'validity refusal','observed':'refusal','detail':str(e)}
    raise AssertionError('AA_INVALID_PRATT_ROOT_ACCEPTED: '+json.dumps(observed,sort_keys=True))

def mutate_outer(kind):
    f=ordinary()
    if kind=='uid':
        f.env['identity']['curve']=copy.deepcopy(f.row); f.env['identity']['curve']['curve_uid']='urn:ec-record:1:sha256:'+'0'*64; f.resign(); return refuse(f,'static_identity')
    if kind=='order':
        f.env['identity']['curve']=copy.deepcopy(f.row); f.env['identity']['curve']['n']='103'; f.resign(); return refuse(f,'static_identity')
    if kind=='label':
        f.env['identity']['curve']=copy.deepcopy(f.row); f.env['identity']['curve']['label']='published' if f.row['label']=='omitted' else 'omitted'; f.resign(); return refuse(f,'static_identity')
    if kind=='index':
        f.env['cohort_index']=1; f.resign(); return refuse(f,'static_identity')
    if kind=='binding':
        x=load(f.out/'input-binding-manifest.json'); x['cohort_index']=1; dump(f.out/'input-binding-manifest.json',x); f.resign(); return refuse(f,'copied_binding')
    if kind=='supervisor':
        put(f.out/'stdout.log',b'altered'); return refuse(f,'supervisor_identity')
    if kind in ('extra','missing','changed','symlink'):
        p=f.out/'legacy-child/checker/qemu.stderr'
        if kind=='extra': put(f.out/'legacy-child/extra.raw',b'extra')
        elif kind=='missing': p.unlink()
        elif kind=='changed': put(p,b'changed')
        else: (f.out/'legacy-child/link').symlink_to(f.out/'stdout.log')
        return refuse(f,'path_safety' if kind=='symlink' else 'capsule_custody')
    if kind=='counter':
        p=f.out/'counter-evidence.json'; x=load(p); x['stages']['checker']['program_output_observed']=1; dump(p,x); f.resign(); return refuse(f,'counter_mismatch')
    if kind=='exact_start':
        p=f.out/'counter-evidence.json'; x=load(p); x['stages']['prover']['exact_program_starts']=1; dump(p,x); f.resign(); return refuse(f,'schema')
    if kind=='trace':
        p=f.out/'supplemental-trace.json'; x=load(p); x['stages']['prover']['printed_trace']['events']=[{'invented':True}]; dump(p,x); f.resign(capsule=True); return refuse(f,'supplemental_trace')
    if kind=='inventory':
        p=f.out/'raw-artifact-inventory.json'; x=load(p); x['members']=[]; dump(p,x); f.resign(); return refuse(f,'capsule_custody')
    if kind=='capsule':
        p=f.out/'raw-artifacts.tar.gz'; put(p,read(p)+b'extra'); f.resign(); return refuse(f,'capsule_custody')

def launch_attack(field,value):
    f=ordinary(); p=f.out/'legacy-child/prover/started.json'; x=load(p); x[field]=value; dump(p,x)
    raw=load(f.out/'raw-result.json'); raw['driver_artifacts']['prover/started.json']=sha(read(p)); dump(f.out/'raw-result.json',raw)
    f.resign(capsule=True); return refuse(f,'launch_identity')

def counter_control(mode,expected):
    f=Fixture(mode); v=f.check(); s=v['counters']['stages']['prover']
    assert v['custody_valid'] and not v['synthetic_admission'] and not v['scientific_admission'],v
    observed=[s[k] for k in ('launch_intent','guest_init_observed','program_output_observed','stage_completed_success')]
    assert observed==expected,(observed,expected)
    assert s['exact_program_starts'] is None
    return {'mode':mode,'observed':observed,'exact_program_starts':None,'lower_bound':s['program_start_observed_lower_bound'],'ambiguous':s['program_start_unobserved_or_ambiguous']}

def static_runner():
    text=read(PRODUCER/'integrated_runner.py').decode(); tree=ast.parse(text)
    assert 'boundary_attempts += 1' in text and 'return boundary(selected, child, cache)' in text
    assert text.index('boundary_attempts += 1')<text.index('return boundary(selected, child, cache)')
    assert "with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture)" in text
    assert text.index("# Both driver handles are closed")<text.index("payload = (rows[index]['n']")
    assert 'finally:' in text and "'recover_' + stage" in text and "'write_integration_failure'" in text
    return {'scope':'source ordering checks only','actual_driver_execution':'unrun','outer_quiet_process_exit':'unrun','whole_recovery_parser_injection':'unrun'}

def main():
    sys.addaudithook(audit)
    with guards():
        run('immutable_snapshot_and_independent21_mapping',setup)
        if CHECKER is not None:
            run('independent_ordinary_full_envelope',lambda: {'custody_valid':ordinary().check()['custody_valid']})
            for mode,expected in [('early',[0,0,0,0]),('launch_only',[1,0,0,0]),('guest_only',[1,1,0,0]),('partial',[1,1,1,0])]:
                run('counter_'+mode,lambda mode=mode,expected=expected:counter_control(mode,expected))
            for mode,gate in [('no_begin','prover_framing'),('duplicate_begin','prover_framing'),('bad_abi','prover_framing'),
                ('no_exit','prover_framing'),('no_complete','prover_framing'),('misorder','prover_framing'),('truncated_cert','prover_framing'),
                ('checker_malformed','checker_framing'),('checker_step','checker_body'),('watchdog','prover_status'),('nonzero','prover_status')]:
                run(mode,lambda mode=mode,gate=gate:malformed(mode,gate))
            for kind in ('uid','order','label','index','binding','supervisor','extra','missing','changed','symlink','counter','exact_start','trace','inventory','capsule'):
                run('mutation_'+kind,lambda kind=kind:mutate_outer(kind))
            for field,value in [('input_sha256','0'*64),('program_sha256','0'*64),('init_sha256','0'*64),('initramfs_sha256','0'*64),('command',['wrong']),('data_mode','empty'),('guest_limit_seconds',999)]:
                run('launch_'+field,lambda field=field,value=value:launch_attack(field,value))
            run('aa_identical_schema_valid_invalid_pratt_root',aa_bad_steps)
            run('runner_static_ordering_and_unrun_gates',static_runner)
    print(json.dumps({'schema':'nistseed.independent_engineering_checks.v1','task_id':'TASK-20261027-344233',
        'execution_owner':'parent session; independent validator authored and derived expectations',
        'independent_validator_executed_project_code':False,'producer_runner_imported':False,
        'results':RESULTS,'counts':COUNTS,'sources_read':sorted(SOURCES),
        'fixture_root':str(WORK) if WORK is not None else None,
        'unrun':['independent actual driver-to-checker invocation','independent quiet CLI after process exit','runner secondary-parser injection','existing A/A build_pair independent invocation'],
        'passed':sum(x['outcome']=='PASS' for x in RESULTS),'failed':sum(x['outcome']=='FAIL' for x in RESULTS)},
        sort_keys=True,indent=2))
    return 0 if all(x['outcome']=='PASS' for x in RESULTS) else 1
if __name__=='__main__': raise SystemExit(main())
