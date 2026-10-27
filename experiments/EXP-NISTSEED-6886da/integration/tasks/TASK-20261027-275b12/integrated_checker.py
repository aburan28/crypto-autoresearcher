"""Independent additive custody/admission reader. Imports are inert.

This module never imports integrated_runner, launches a process, extracts a tar
archive, writes an artifact, or invokes a legacy boundary. Synthetic profiles
are external test inputs and never satisfy real runtime admission.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import stat
import tarfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
EXP = ROOT / 'experiments/EXP-NISTSEED-6886da'
COMPAT = ROOT / 'research/nist_seed_ecpp_compat_20261024'
DATA = COMPAT / '.work/build-v4/ECPP/Ecpp/Data'
MANIFEST = 'coordination/goals/GOAL-NISTSEED-ab8949/integration-admission-20261027/source-inputs.json'
MANIFEST_SHA256 = '47341a3e609a595e80c82042029377eec129dc9a29347bf75430e1e1d4339f62'
EXTRA = {
 'research/nist_seed_ecpp_compat_20261024/qemu_controls.py':'255b415ebf5a8eaa5514a02fbd0fb9886f27a2065f8686586a2c336e9f9372e7',
 'research/nist_seed_ecpp_compat_20261024/qemu_init.c':'1c5a2a11ecabf081a61fdf79f04ae343ea0348dbf7fa08d5ad1be738ca5e56e0',
 'research/nist_seed_ecpp_compat_20261024/guest_framing.py':'ce4f7a8b320826c09d9b947d306883d83b695b83ebfc496ec1d3e38ca6a76bf5',
 'research/nist_seed_ecpp_compat_20261024/certificate_admission.py':'6cf50c95da246c7033dbb2cda8f8d70c07e2d5e366c1f1c9f163e7b115740c68',
 'experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json':'c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087',
 'agents/executor.md':'89eda99ea575b966c5780762d2d13810fd6ed5abe1a5dc76a57ed51680784cc7',
 'agents/validator.md':'33947db8c7cc8663ac79f1eff4b183e75d0546915feb23e77654cd03a249c9d2',
 'orchestration/model-policies.yaml':'a5a86d0e2be07f3c4e0ee67cfacad1cf667228046e832f24fb4e480ec0dc7a92',
 'tools/research_dispatch.py':'5919013342391e9b9ec30811c0f4c458e78030915c1afd8b799340b14fadb437'}
SUPERVISOR = frozenset(('launch.json','environment.json','command.txt','stdout.log','stderr.log'))
PROVER_ARGV = ['/program','-l','/ecpp/','-f','/input','-Fc','-C','/tmp/certificate']
CHECKER_ARGV = ['/program','-f','/input']
PHASE_RULE = {'source':'ECPP/Ecpp/C/c/ecpp.c',
 'source_sha256':'16766d2b73a5424b4252d0d75ba5a4346fae1d908ecc04eb7bca8bf1930071e2',
 'archive_sha256':'0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f',
 'rule':'^% Starting phase (1: building the sequence of primes|2: proving)$',
 'scope':'Printed original-program output signature; not proof of successful exec or complete computation.'}

class CheckFailure(RuntimeError):
    pass

def fail(gate, message):
    raise CheckFailure(gate + ': ' + message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())

def safe(path):
    path=Path(path).absolute()
    if any(item.is_symlink() for item in (path,*path.parents)):
        fail('path_safety','symlink path or ancestor')
    return path.resolve(strict=False)

def read(path):
    path=safe(path)
    if not path.is_file(): fail('custody','missing or nonregular file: '+str(path))
    return path.read_bytes()

def load(path):
    body=read(path)
    if len(body)>16*1024*1024: fail('bounded_json','JSON exceeds bounded reader limit')
    return json.loads(body.decode('utf-8'))

def module(path,name):
    specification=importlib.util.spec_from_file_location(name,path)
    if specification is None or specification.loader is None: fail('source','module unavailable')
    result=importlib.util.module_from_spec(specification)
    specification.loader.exec_module(result)
    return result

def tree(directory):
    directory=safe(directory)
    if not directory.is_dir(): fail('custody','missing directory')
    result={}
    for path in sorted(directory.rglob('*')):
        safe(path)
        if path.is_dir(): continue
        if not path.is_file(): fail('custody','nonregular tree member')
        result[path.relative_to(directory).as_posix()]=sha(read(path))
    return result

def pins():
    payload=read(ROOT/MANIFEST)
    if sha(payload)!=MANIFEST_SHA256: fail('source_identity','source manifest digest')
    manifest=json.loads(payload)
    if manifest.get('source_commit')!='4c7298e5212f523642c782483cd28f4bd5000d66' or len(manifest.get('inputs',[]))!=23:
        fail('source_identity','source manifest identity')
    expected={MANIFEST:MANIFEST_SHA256}
    for row in manifest['inputs']:
        name=row['path']; path=Path(name)
        if path.is_absolute() or '..' in path.parts or path.as_posix()!=name or name in expected:
            fail('source_identity','unsafe or duplicate source path')
        if sha(read(ROOT/path))!=row['sha256']: fail('source_identity',name)
        expected[name]=row['sha256']
    for name,value in EXTRA.items():
        if sha(read(ROOT/name))!=value: fail('source_identity',name)
        expected[name]=value
    return expected

def source_context():
    source=pins()
    v9=module(EXP/'implementation/cohort_checker.py','_integrated_independent_v9')
    frozen=v9.frozen(); rows,runtime=v9.inputs(); prior=v9.independent_prior_map(rows)
    if len(rows)!=21 or len(prior)!=21: fail('cohort_identity','complete 21-row universe required')
    return {'source':source,'v9':v9,'frozen':frozen,'rows':rows,'runtime':runtime,'prior':prior}

def real_material(runtime):
    blobs={}
    for item in runtime['artifacts']:
        relative=Path(item['logical_path'])
        if relative.is_absolute() or '..' in relative.parts: fail('runtime_identity','unsafe payload path')
        body=read(ROOT/relative)
        if len(body)!=item['bytes'] or sha(body)!=item['sha256'] or relative.name in blobs:
            fail('runtime_identity','payload identity')
        blobs[relative.name]=body
    kernel=read(COMPAT/'.work/qemu-runtime/vmlinuz-lts')
    if len(kernel)!=runtime['kernel']['kernel_bytes'] or sha(kernel)!=runtime['kernel']['kernel_sha256']:
        fail('runtime_identity','kernel identity')
    if tree(DATA)!=runtime['original_data']: fail('runtime_identity','complete original Data inventory')
    return {'blobs':blobs,'kernel':kernel,'catalog':DATA}

def reconstructed_image(material,stage,payload):
    proving=stage=='prover'; argv=PROVER_ARGV if proving else CHECKER_ARGV
    directories={'dev','proc','tmp','ecpp','ecpp/Data'}; data=[]; entries=[]
    if proving:
        for path in sorted(material['catalog'].rglob('*')):
            safe(path); name='ecpp/Data/'+path.relative_to(material['catalog']).as_posix()
            if path.is_dir(): directories.add(name)
            elif path.is_file(): data.append((name,read(path)))
            else: fail('runtime_identity','nonregular Data member')
    for name in sorted(directories,key=lambda item:(item.count('/'),item)):
        entries.append((name,stat.S_IFDIR|(0o1777 if name=='tmp' else 0o755),b'',0,0))
    entries.append(('dev/console',stat.S_IFCHR|0o600,b'',5,1))
    files=[('init',material['blobs']['qemu-init'],0o555),
           ('program',material['blobs']['runecpp' if proving else 'checkcertif'],0o555),
           ('argv',('\n'.join(argv)+'\n').encode(),0o444),('input',payload,0o444),
           ('stdin',b'',0o444),('cpu_limit',str(300 if proving else 30).encode(),0o444)]
    entries.extend((name,stat.S_IFREG|mode,body,0,0) for name,body,mode in files)
    entries.extend((name,stat.S_IFREG|0o444,body,0,0) for name,body in data)
    stream=bytearray()
    for ordinal,(name,mode,body,major,minor) in enumerate(entries+[('TRAILER!!!',0,b'',0,0)],1):
        name=name.encode()+b'\0'; fields=(ordinal,mode,0,0,1,0,len(body),0,0,major,minor,len(name),0)
        stream.extend(b'070701'+''.join(f'{number:08x}' for number in fields).encode()+name)
        stream.extend(b'\0'*(-len(stream)%4)); stream.extend(body); stream.extend(b'\0'*(-len(stream)%4))
    stream.extend(b'\0'*(-len(stream)%512))
    return gzip.compress(bytes(stream),mtime=0)

def expected_launch(output,stage,payload,runtime,material,profile):
    image=profile['image_sha256'][stage] if profile is not None else sha(reconstructed_image(material,stage,payload))
    cache=output/'runtime-cache'
    command=['/opt/homebrew/bin/qemu-system-i386','-machine','pc,accel=tcg','-cpu','max','-m','256','-smp','1',
             '-nodefaults','-no-user-config','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot',
             '-device','isa-debug-exit,iobase=0xf4,iosize=4','-kernel',str(cache/'vmlinuz-lts'),
             '-initrd',str(cache/'images'/(image+'.cpio.gz')),
             '-append','console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on']
    artifacts={Path(item['logical_path']).name:item['sha256'] for item in runtime['artifacts']}
    proving=stage=='prover'
    return {'command':command,'program_sha256':artifacts['runecpp' if proving else 'checkcertif'],
            'init_sha256':artifacts['qemu-init'],'initramfs_sha256':image,'input_sha256':sha(payload),
            'stdin_sha256':sha(b''),'data_mode':'full' if proving else None,
            'guest_limit_seconds':300 if proving else 30,'host_limit_seconds':390 if proving else 90}

def probe_frame(serial):
    normalized=serial.replace(b'\r\n',b'\n')
    definitions=[('abi',b'__ECPP_INIT_ABI__',rb'^__ECPP_INIT_ABI__ 4 4 4\n'),
                 ('begin',b'__ECPP_GUEST_BEGIN__',rb'^__ECPP_GUEST_BEGIN__\n'),
                 ('exit',b'__ECPP_CHILD_EXIT__',rb'^__ECPP_CHILD_EXIT__ ([0-9]+) timeout=([0-9]+)\n'),
                 ('complete',b'__ECPP_GUEST_COMPLETE__',rb'^__ECPP_GUEST_COMPLETE__\n')]
    events={}
    for name,prefix,expression in definitions:
        matches=list(re.finditer(expression,normalized,re.M))
        if len(matches)!=1 or normalized.count(prefix)!=1: raise ValueError('incomplete, duplicate or malformed '+name)
        events[name]=matches[0]
    a,b,e,c=(events[name] for name in ('abi','begin','exit','complete'))
    if not a.start()<b.start()<e.start()<c.start() or normalized[e.start()-1:e.start()]!=b'\n':
        raise ValueError('misordered or incomplete body frame')
    starts=list(re.finditer(rb'^__ECPP_CERTIFICATE_BEGIN__\n',normalized,re.M))
    stops=list(re.finditer(rb'^__ECPP_CERTIFICATE_END__\n',normalized,re.M))
    if len(starts)!=len(stops) or len(starts)>1 or normalized.count(b'__ECPP_CERTIFICATE_BEGIN__')!=len(starts) or normalized.count(b'__ECPP_CERTIFICATE_END__')!=len(stops):
        raise ValueError('truncated, duplicate or malformed certificate')
    certificates=[]
    if starts:
        first,last=starts[0],stops[0]
        if not e.end()<=first.start()<last.start()<c.start() or normalized[last.start()-1:last.start()]!=b'\n':
            raise ValueError('certificate ordering')
        certificates=[normalized[first.end():last.start()-1]]
    return {'body':normalized[b.end():e.start()-1],'certificates':certificates,
            'child_exit':int(e.group(1)),'timeout':int(e.group(2))}

def guarded(operation,function,errors):
    try: return function()
    except BaseException as error:
        errors.append({'operation':operation,'type':type(error).__name__,'message':str(error)[:4096]})
        return None

def retained(output,stage):
    directory=output/'legacy-child'/stage; errors=[]; result={}
    for name,filename,parser in (('serial','serial.raw',read),('status','result.json',load),('started','started.json',load)):
        path=directory/filename
        operation={'serial':'read_serial','status':'parse_status','started':'parse_launch_intent'}[name]
        result[name]=guarded(operation,lambda path=path,parser=parser:parser(path),errors) if path.exists() else None
    result['frame']=guarded('parse_framing',lambda:probe_frame(result['serial']),errors) if result['serial'] is not None else None
    result['errors']=errors
    return result

def evidence(output,path,stage,kind,offset=None,length=None,source_rule=None,synthetic=False):
    return {'path':path.relative_to(output).as_posix(),'sha256':sha(read(path)),'stage':stage,'kind':kind,
            'byte_offset':offset,'byte_length':length,'source_rule':source_rule,'synthetic':synthetic}

def derive_stage(output,stage,item,expected,synthetic):
    serial,status,started,frame=(item[key] for key in ('serial','status','started','frame'))
    errors=list(item['errors']); proofs=[]; launch=False; guest=False; activity=False
    if started is not None:
        if not isinstance(started,dict) or expected is None or set(started)!=set(expected)|{'utc'} or not isinstance(started.get('utc'),str) or not started['utc'] or any(started.get(key)!=value for key,value in expected.items()):
            fail('launch_identity','exact retained '+stage+' launch identity does not match independently reconstructed inputs')
        launch=True
        proofs.append(evidence(output,output/'legacy-child'/stage/'started.json',stage,'launch_intent_before_subprocess',source_rule='qemu_controls.py: vm writes started.json before subprocess.run',synthetic=synthetic))
    if serial is not None:
        path=output/'legacy-child'/stage/'serial.raw'
        abi=list(re.finditer(rb'^__ECPP_INIT_ABI__ 4 4 4\r?\n',serial,re.M))
        begin=list(re.finditer(rb'^__ECPP_GUEST_BEGIN__\r?\n',serial,re.M))
        guest=len(abi)==len(begin)==1 and abi[0].start()<begin[0].start()
        for kind,events in (('guest_abi',abi),('guest_init_begin_before_fork_exec',begin)):
            for event in events: proofs.append(evidence(output,path,stage,kind,event.start(),event.end()-event.start(),'qemu_init.c: ABI and begin precede fork/execv',synthetic))
        if stage=='prover':
            signatures=list(re.finditer(rb'^% Starting phase (?:1: building the sequence of primes|2: proving)\r?\n',serial,re.M))
            activity=bool(signatures)
            for event in signatures: proofs.append(evidence(output,path,stage,'source_backed_program_output',event.start(),event.end()-event.start(),PHASE_RULE,synthetic))
        proofs.append(evidence(output,path,stage,'raw_serial_retained',synthetic=synthetic))
    status_ok=False
    if status is not None and frame is not None and serial is not None:
        elapsed=status.get('elapsed_host_seconds') if isinstance(status,dict) else None
        status_ok=(isinstance(status,dict) and type(status.get('vm_valid')) is bool and status.get('vm_valid') is True
                   and type(status.get('qemu_exit')) is int and status['qemu_exit']==33
                   and type(status.get('child_exit')) is int and status['child_exit']==frame['child_exit']
                   and status.get('reason') is None and frame['timeout']==0
                   and status.get('serial_sha256')==sha(serial)
                   and type(status.get('certificate_count')) is int and status['certificate_count']==len(frame['certificates'])
                   and type(elapsed) in (int,float) and math.isfinite(elapsed) and elapsed>=0)
        body=guarded('read_program_stdout',lambda:read(output/'legacy-child'/stage/'program.stdout'),errors)
        status_ok=status_ok and body==frame['body']
        if not status_ok: errors.append({'operation':'status_reconciliation','type':'Refusal','message':'independent complete-frame/status/body reconciliation failed'})
        proofs.append(evidence(output,output/'legacy-child'/stage/'result.json',stage,'retained_primitive_status',synthetic=synthetic))
    active=launch or guest or serial is not None
    return {'launch_intent':int(launch),'guest_init_observed':int(guest),'program_output_observed':int(activity),
            'stage_completed_success':int(status_ok and frame['child_exit']==0),
            'stage_completed_failure':int(status_ok and frame['child_exit']!=0),
            'exact_program_starts':None,'program_start_observed_lower_bound':int(activity),
            'program_start_unobserved_or_ambiguous':int(active and not activity),
            'framing_state':'COMPLETE' if frame is not None else 'UNAVAILABLE' if serial is None else 'MALFORMED',
            'status_state':'UNAVAILABLE' if status is None else 'RECONCILED' if status_ok else 'UNRECONCILED',
            'errors':errors,'evidence':proofs}

def validate_schema(value,definition=None):
    import jsonschema
    schema=load(HERE/'integration_schema.json')
    jsonschema.Draft202012Validator.check_schema(schema)
    if definition is not None: schema={'$schema':schema['$schema'],'$ref':'#/$defs/'+definition,'$defs':schema['$defs']}
    errors=list(jsonschema.Draft202012Validator(schema).iter_errors(value))
    if errors: fail('schema','; '.join(str(error.message) for error in errors[:5]))

def outer_inventory(output):
    result={}
    for path in sorted(output.iterdir()):
        safe(path)
        if path.name in SUPERVISOR or path.name=='integration-envelope.json':
            if not path.is_file(): fail('custody','nonregular supervisor/envelope')
            continue
        if path.name in ('legacy-child','runtime-cache') and path.is_dir():
            tree(path)
            continue
        if not path.is_file(): fail('custody','unexpected outer directory or nonregular member')
        body=read(path); result[path.name]={'bytes':len(body),'sha256':sha(body)}
    return result

def capsule_check(output):
    helper=module(EXP/'integration/capsule_check.py','_independent_capsule_reader')
    try: result=helper.check(output)
    except BaseException as error: fail('capsule_custody',str(error))
    paths={}
    child=output/'legacy-child'
    if child.exists():
        for relative in tree(child): paths['legacy-child/'+relative]=child/relative
    for name in ('driver.stdout.log','driver.stderr.log','supplemental-trace.json'):
        if (output/name).exists(): paths[name]=output/name
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0) as compressed:
        with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
            for name,path in sorted(paths.items()):
                body=read(path); entry=tarfile.TarInfo(name); entry.size=len(body); entry.mode=0o600
                entry.mtime=entry.uid=entry.gid=0; entry.uname=entry.gname=''
                archive.addfile(entry,io.BytesIO(body))
    if buffer.getvalue()!=read(output/'raw-artifacts.tar.gz'): fail('capsule_custody','capsule differs from independently reconstructed deterministic bytes')
    return result

def verify_cache(output,material,items,payload,profile):
    cache=output/'runtime-cache'
    if profile is not None:
        if cache.exists(): fail('runtime_cache','synthetic profile cannot satisfy a real cache')
        return {'state':'SYNTHETIC_NO_RUNTIME_CACHE','sha256':{}}
    if not cache.exists(): return {'state':'ABSENT','sha256':{}}
    expected={'vmlinuz-lts':sha(material['kernel'])}
    for stage in ('prover','checker'):
        if items[stage]['started'] is None: continue
        stage_payload=payload
        if stage=='checker':
            frame=items['prover']['frame']
            if frame is None or len(frame['certificates'])!=1: fail('runtime_cache','checker image requires an intact bound certificate')
            stage_payload=frame['certificates'][0]
        image=reconstructed_image(material,stage,stage_payload)
        expected['images/'+sha(image)+'.cpio.gz']=sha(image)
    if tree(cache)!=expected: fail('runtime_cache','independent exact private cache reconstruction differs')
    return {'state':'VERIFIED_RECONSTRUCTIBLE','sha256':expected}

def check(output:Path,binding:Path,*,synthetic_profile=None,real_admission_receipt=None):
    output,binding=safe(output),safe(binding)
    envelope=load(output/'integration-envelope.json'); validate_schema(envelope)
    context=source_context(); v9=context['v9']; rows=context['rows']; runtime=context['runtime']; index=envelope['cohort_index']
    if type(index) is not int or not 0<=index<21: fail('cohort_identity','invalid index')
    expected_identity={'source_pins':context['source'],'frozen_input_sha256':context['frozen'],'curve':rows[index],
                       'ordered_cohort':rows,'prior_primality_mapping':context['prior'],'runtime':runtime,
                       'limits':v9.LIMITS,'primary_configuration':v9.PRIMARY,'prover_argv':PROVER_ARGV,'checker_argv':CHECKER_ARGV}
    if envelope['identity']!=expected_identity: fail('static_identity','full cohort/source/runtime/configuration identity differs')
    external=load(binding)
    if envelope['external_binding']!={'path':str(binding),'sha256':sha(read(binding))}: fail('external_binding','caller binding does not match envelope')
    copied=output/'input-binding-manifest.json'
    if read(copied)!=read(binding): fail('copied_binding','copied and caller binding bytes differ')
    if external.get('schema')!='crypto.autoresearch.nistseed_ecpp_trial_binding.v1' or external.get('cohort_index')!=index or safe(Path(external.get('output_directory','')))!=output or external.get('frozen_input_sha256')!=context['frozen'] or external.get('limits')!=v9.LIMITS or external.get('primary_configuration')!=v9.PRIMARY:
        fail('external_binding','bound identity/configuration differs')
    capture=safe(Path(envelope['capture_directory']))
    if capture==output or capture.is_relative_to(output) or output.is_relative_to(capture) or external.get('driver_capture_directory')!=str(capture):
        fail('capture_identity','distinct declared capture path required')
    if any(sha(read(output/name))!=value for name,value in envelope['supervisor_artifact_sha256'].items()): fail('supervisor_identity','supervisor bytes changed')
    if set(envelope['supervisor_artifact_sha256'])!=SUPERVISOR: fail('supervisor_identity','exact five supervisor files required')
    launch=load(output/'launch.json'); argv=load(output/'command.txt')
    if not isinstance(argv,list) or not all(isinstance(value,str) for value in argv) or launch.get('argv')!=argv or str(index) not in argv or str(output) not in argv or str(binding) not in argv or not isinstance(launch.get('authority'),dict) or not isinstance(load(output/'environment.json'),dict):
        fail('supervisor_identity','launch argv or provenance differs')
    if outer_inventory(output)!=envelope['sidecars']: fail('outer_sidecar_custody','exact outer membership, size or digest differs')
    for source_name,target in (('stdout.log','driver.stdout.log'),('stderr.log','driver.stderr.log')):
        if read(capture/source_name)!=read(output/target): fail('capture_identity','closed capture and copied sidecar differ')
    if envelope['finalization']['state']!='COMPLETE': fail('finalization','raw finalization was explicitly incomplete')
    custody=capsule_check(output)
    profile=synthetic_profile
    if profile is not None:
        if set(profile)!={'scope','catalog_directory','image_sha256'} or profile['scope']!='EXPLICIT_SYNTHETIC_FIXTURE_ONLY' or set(profile['image_sha256'])!={'prover','checker'}:
            fail('synthetic_profile','explicit external profile schema differs')
        profile={'scope':profile['scope'],'catalog_directory':str(safe(Path(profile['catalog_directory']))),'image_sha256':dict(profile['image_sha256'])}
        if any(re.fullmatch(r'[0-9a-f]{64}',value) is None for value in profile['image_sha256'].values()) or Path(profile['catalog_directory'])==DATA.resolve(strict=False): fail('synthetic_profile','invalid synthetic image/catalog identity')
        if envelope['mode']!='synthetic' or envelope['synthetic_profile']!=profile or envelope['real_admission_receipt'] is not None: fail('synthetic_profile','synthetic/real routing differs')
        material=None; v9.DATA=Path(profile['catalog_directory'])
    else:
        if envelope['mode']!='real' or envelope['synthetic_profile'] is not None: fail('runtime_identity','synthetic envelope cannot satisfy real admission')
        material=real_material(runtime)
        if real_admission_receipt is None or envelope['real_admission_receipt']!=real_admission_receipt: fail('real_admission','independent caller admission receipt required')
        request={'index':index,'row':rows[index],'binding_sha256':sha(read(binding)),'output_directory':str(output),
                 'capture_directory':str(capture),'source_pins':context['source'],'runtime':runtime,'limits':v9.LIMITS,
                 'primary_configuration':v9.PRIMARY,'prover_argv':PROVER_ARGV,'checker_argv':CHECKER_ARGV}
        if real_admission_receipt.get('request_sha256')!=canonical(request): fail('real_admission','admission is not bound to exact request')
    items={stage:retained(output,stage) for stage in ('prover','checker')}
    payload=(rows[index]['n']+'\n').encode('ascii'); stage_counters={}
    for stage in ('prover','checker'):
        stage_payload=payload
        if stage=='checker':
            frame=items['prover']['frame']
            stage_payload=frame['certificates'][0] if frame is not None and len(frame['certificates'])==1 else None
            retained_input=output/'legacy-child/prover/certificate.cformat'
            if stage_payload is None and retained_input.exists(): stage_payload=read(retained_input)
        expected=expected_launch(output,stage,stage_payload,runtime,material,profile) if stage_payload is not None else None
        stage_counters[stage]=derive_stage(output,stage,items[stage],expected,profile is not None)
    cache=verify_cache(output,material,items,payload,profile)
    if cache!=envelope['runtime_cache']: fail('runtime_cache','producer cache report differs')
    trace_module=module(EXP/'integration/printed_trace.py','_independent_supplemental_trace')
    expected_trace={'schema':'crypto.autoresearch.nistseed_ecpp_supplemental_trace.v1','stages':{}}
    for stage,item in items.items():
        if item['serial'] is not None:
            expected_trace['stages'][stage]={'raw_path':f'legacy-child/{stage}/serial.raw','raw_sha256':sha(item['serial']),'printed_trace':trace_module.extract(item['serial'])}
    trace_path=output/'supplemental-trace.json'
    if expected_trace['stages']:
        if not trace_path.exists() or load(trace_path)!=expected_trace: fail('supplemental_trace','independent printed-token extraction differs')
    elif trace_path.exists(): fail('supplemental_trace','trace exists without retained serial')
    recovery=load(output/'integration-recovery.json')
    if set(recovery)!={'schema','original_exception','boundary_exceptions','stages','secondary_errors','scope'} or recovery['schema']!='crypto.autoresearch.nistseed_ecpp_integration_recovery.v1' or set(recovery['stages'])!={'prover','checker'}:
        fail('recovery_record','recovery schema differs')
    for stage,item in items.items():
        recovered=recovery['stages'][stage]; serial=item['serial']
        if recovered.get('serial_sha256')!=(sha(serial) if serial is not None else None) or recovered.get('serial_bytes')!=(len(serial) if serial is not None else None): fail('recovery_record','raw serial recovery identity differs')
        if recovered.get('strict_frame_available'):
            frame=item['frame']
            if frame is None or recovered.get('strict_body_sha256')!=sha(frame['body']) or recovered.get('strict_certificate_sha256')!=[sha(body) for body in frame['certificates']]: fail('recovery_record','claimed strict frame differs')
    raw=None; observation=None; v9_errors=[]
    for filename,key in (('raw-result.json','raw'),('observation.json','observation')):
        path=output/filename
        if path.exists():
            value=guarded('parse_'+filename,lambda path=path:load(path),v9_errors)
            if key=='raw': raw=value
            else: observation=value
    if isinstance(raw,dict):
        expected_fields={'schema':'crypto.autoresearch.nistseed_ecpp_raw_result.v5','cohort_index':index,'curve':rows[index],
                         'frozen_input_sha256':context['frozen'],'runtime_payloads':runtime['artifacts'],'kernel':runtime['kernel'],
                         'original_data':runtime['original_data'],'limits':v9.LIMITS,'primary_configuration':v9.PRIMARY,
                         'prior_primality_mapping':context['prior'],'named_orders_executed':1,
                         'input_binding_manifest_sha256':sha(read(binding)),'external_binding_manifest_sha256':sha(read(binding)),
                         'supervisor_manifest':external,'supervisor_artifact_sha256':envelope['supervisor_artifact_sha256']}
        if any(raw.get(key)!=value for key,value in expected_fields.items()): fail('v9_static_identity','original V9 identity differs')
        try: v9.inventory(raw,output)
        except BaseException as error: fail('v9_inventory',str(error))
    if isinstance(observation,dict) and (observation.get('curve_uid')!=rows[index]['curve_uid'] or observation.get('prior_primality_evidence')!=context['prior'][rows[index]['curve_uid']]): fail('v9_static_identity','original observation identity differs')
    child_identity=output/'legacy-child/identity.json'
    if child_identity.exists():
        identity=load(child_identity)
        expected={'curve':rows[index],'cohort_sha256':context['frozen']['research/nist_seed_ecpp_compat_20261024/cohort-inputs.json'],
                  'bindings_sha256':context['frozen']['research/nist_seed_ecpp_compat_20261024/runtime-bindings.json'],
                  'launcher_sha256':context['frozen']['research/nist_seed_ecpp_compat_20261024/cohort_case.py'],
                  'fresh_process_rng':'original ModInitialize: srandom(1)','prover_guest_limit_seconds':300,
                  'prover_host_limit_seconds':390,'classification_scope':'legacy prover/checker behavior on an already-certified prime integer'}
        if identity!=expected: fail('child_identity','retained child row/configuration identity differs')
    elif any(item['started'] is not None or item['serial'] is not None for item in items.values()): fail('child_identity','retained child activity lacks its original identity')
    marker=output/'integration-boundary-call.json'; attempts=int(marker.exists())
    if attempts and load(marker)!={'schema':'crypto.autoresearch.nistseed_ecpp_boundary_call.v1','cohort_index':index,'mode':envelope['mode'],'evidence_kind':'whole_boundary_call_attempt_not_program_start'}: fail('boundary_counter','attempt evidence differs')
    counters=load(output/'counter-evidence.json'); validate_schema(counters,'counters')
    expected_counters={'schema':'crypto.autoresearch.nistseed_ecpp_integration_counters.v1','mode':envelope['mode'],
        'selected_cohort_indices':[index],'boundary_calls_attempted':{'synthetic':attempts if profile is not None else 0,'real':attempts if profile is None else 0},
        'boundary_evidence_path':marker.name if attempts else None,'boundary_evidence_sha256':sha(read(marker)) if attempts else None,
        'legacy_selected_work_field':{'path':'raw-result.json','field':'named_orders_executed','value':raw.get('named_orders_executed') if isinstance(raw,dict) else None,
          'meaning':'frozen selected-work literal; never a program-start count'},'stages':stage_counters,
        'certificate_admitted':None,'certificate_admission_state':'DEFERRED_TO_INDEPENDENT_CHECKER','exact_program_start_total':None,
        'synthetic_evidence_contributes_to_real_execution_totals':False}
    # Diagnostic wording can differ between independently guarded parsers. Every
    # numeric value, state, evidence path/digest/offset and source rule must agree.
    def comparable(value):
        if isinstance(value,dict): return {key:comparable(item) for key,item in value.items() if key!='errors'}
        if isinstance(value,list): return [comparable(item) for item in value]
        return value
    if comparable(counters)!=comparable(expected_counters): fail('counter_mismatch','independently derived evidence-backed counters differ')
    failures=[]
    for stage in ('prover','checker'):
        if items[stage]['frame'] is None: failures.append(stage+'_framing')
        elif not stage_counters[stage]['stage_completed_success']: failures.append(stage+'_status')
    prover=items['prover']['frame']; checker=items['checker']['frame']; certificate=None
    if prover is not None:
        labels=re.findall(rb'^(?:% )?This number is (prime|composite)\b',prover['body'],re.M)
        if labels!=[b'prime']: failures.append('prover_labels')
        if len(prover['certificates'])!=1: failures.append('certificate_count')
        else:
            certificate=prover['certificates'][0]
            path=output/'legacy-child/prover/certificate.cformat'
            if not path.exists() or read(path)!=certificate: failures.append('certificate_custody')
    if checker is not None and checker['certificates']: failures.append('checker_certificate_count')
    steps=None
    if certificate is not None:
        try: steps=v9.parse(certificate,v9.integer(rows[index]['n']))
        except BaseException: failures.append('certificate_grammar_root')
    if steps is not None and checker is not None and stage_counters['checker']['stage_completed_success']:
        status=items['checker']['status']
        if not v9.admit(status,checker['body'],certificate,v9.integer(rows[index]['n'])): failures.append('checker_body')
    if not isinstance(raw,dict) or not isinstance(observation,dict) or observation.get('certificate_admitted') is not True: failures.append('v9_admission_missing')
    if not failures:
        try: v9.check(output)
        except BaseException as error: fail('v9_admission',str(error))
    admitted=not failures
    return {'accepted':True,'custody_valid':True,'mode':envelope['mode'],
            'scientific_admission':bool(admitted and profile is None),
            'synthetic_admission':bool(admitted and profile is not None),
            'classification':'PRIOR_PRIMALITY_EVIDENCE_REQUIRED' if admitted and profile is None else 'INDETERMINATE',
            'admission_failures':sorted(set(failures)),'counters':expected_counters,
            'capsule':custody,'v9_envelope_parse_errors':v9_errors,
            'scope':'Retained software/custody component only; no historical, primality, curve-security or research-state conclusion.'}

def check_aa_documents(left,right):
    """Validity precedes equality; this function does not produce an A/A pair."""
    import jsonschema
    pins()
    schema=load(EXP/'aa-admission/aa_fixture_schema.json')
    definition={'$schema':schema['$schema'],'$ref':'#/$defs/document','$defs':schema['$defs']}
    validator=jsonschema.Draft202012Validator(definition)
    for document in (left,right):
        errors=list(validator.iter_errors(document))
        if errors: fail('aa_validity',errors[0].message)
        steps=document['certificate']['steps']
        if not isinstance(steps[0],dict) or steps[0].get('n')!=101: fail('aa_validity','root-bound steps required before comparison')
    v9=module(EXP/'implementation/cohort_checker.py','_integrated_aa_comparator')
    return v9.aa_compare(left,right)
