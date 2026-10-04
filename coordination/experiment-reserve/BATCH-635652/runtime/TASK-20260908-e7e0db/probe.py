"""Three fixed local Docker resource controls. No experimental or arithmetic runner."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,re,resource,subprocess,sys,time,uuid
TASK='TASK-20260908-e7e0db'
DECISION='DEC-20260908-4f847e'
IMAGE='docker.io/library/python@sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4'
DIGEST=IMAGE.rsplit('@',1)[1]
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
COMMANDS=[]
CHILD=r"""
import datetime,json,os,platform,resource,sys
from pathlib import Path
mode=sys.argv[1];expected=int(sys.argv[2])
def emit(d):
    d['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print(json.dumps(d,sort_keys=True),flush=True)
try:
    base=Path('/sys/fs/cgroup')
    values={n:(base/n).read_text().strip() for n in ['memory.max','memory.swap.max','cpu.max','pids.max','memory.current','memory.events']}
    cpu=values['cpu.max'].split()
    mismatch=[]
    if platform.system()!='Linux' or platform.machine() not in ['aarch64','arm64']:mismatch.append('platform')
    if os.geteuid()!=65534:mismatch.append('uid')
    if values['memory.max']!=str(expected):mismatch.append('memory.max')
    if values['memory.swap.max']!='0':mismatch.append('memory.swap.max')
    if values['pids.max']!='32':mismatch.append('pids.max')
    if len(cpu)!=2 or cpu[0]=='max' or (int(cpu[0])<=0 or int(cpu[0])!=int(cpu[1])):mismatch.append('cpu.max')
    membership=Path('/proc/self/cgroup').read_text()
    if '0::/' not in membership:mismatch.append('cgroup_membership')
    emit({'event':'configuration','mode':mode,'required_memory_bytes':expected,'values':values,'cgroup_membership':membership,'uid':os.geteuid(),'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'mismatches':mismatch})
    if mismatch:
        emit({'event':'typed_configuration_refusal','reason':'resource_profile_mismatch','mismatches':mismatch});raise SystemExit(42)
    if mode=='oom':
        emit({'event':'before_allocation','requested_bytes':128*1024*1024})
        data=bytearray(128*1024*1024)
        for offset in range(0,len(data),4096):data[offset]=1
        emit({'event':'unexpected_allocation_survival','bytes':len(data)})
    else:emit({'event':'profile_accepted'})
except Exception as exc:
    emit({'event':'probe_error','type':type(exc).__name__,'message':str(exc)});raise SystemExit(70)
"""
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def command(argv,timeout=30):
    start=now();t=time.perf_counter();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    row={'argv':argv,'started_at_UTC':start,'timeout_seconds':timeout}
    try:
        r=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
        row.update(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,timed_out=False)
    except subprocess.TimeoutExpired as exc:
        def decoded(x):return x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
        row.update(exit_code=None,stdout=decoded(exc.stdout),stderr=decoded(exc.stderr),timed_out=True,timeout_effect='Python terminated the owned Docker CLI process; container state must be inspected and separately stopped if necessary.')
    finally:
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        row.update(ended_at_UTC=now(),wall_seconds=time.perf_counter()-t,host_cli_cpu_seconds=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime))
        COMMANDS.append(row)
    return row

def require_success(r):
    if r['timed_out'] or r['exit_code']!=0:raise RuntimeError('administrative command failed; inspect retained command record')
    return r['stdout'].strip()

def docker_endpoint(exe):
    endpoint=os.environ.get('DOCKER_HOST','')
    if not endpoint:endpoint=require_success(command([exe,'context','inspect','--format','{{.Endpoints.docker.Host}}'],15))
    if not endpoint.startswith('unix://') or 'bedrock' in endpoint.lower():raise RuntimeError('refused nonlocal or prohibited-token endpoint before Docker network/container work')
    return endpoint

def image_and_daemon(cli,prior_pulls):
    fmt='{"OSType":{{json .OSType}},"Architecture":{{json .Architecture}},"CgroupVersion":{{json .CgroupVersion}},"MemTotal":{{json .MemTotal}},"NCPU":{{json .NCPU}},"ServerVersion":{{json .ServerVersion}}}'
    daemon=json.loads(require_success(command(cli+['info','--format',fmt],20)))
    if daemon['OSType']!='linux' or daemon['Architecture'] not in ['aarch64','arm64'] or str(daemon['CgroupVersion'])!='2':raise RuntimeError('local daemon is not the frozen Linux arm64 cgroup-v2 environment')
    fmt='{"Id":{{json .Id}},"RepoDigests":{{json .RepoDigests}},"Os":{{json .Os}},"Architecture":{{json .Architecture}},"Entrypoint":{{json (index .Config "Entrypoint")}}}'
    inspection=command(cli+['image','inspect',IMAGE,'--format',fmt],20)
    pulled=False
    if inspection['exit_code']!=0 or inspection['timed_out']:
        if inspection['timed_out'] or 'No such image:' not in inspection['stderr'] or prior_pulls>=1:
            raise RuntimeError('image inspection failed; no extra pull or silent metadata fallback permitted')
        require_success(command(cli+['pull','--platform','linux/arm64',IMAGE],300));pulled=True
        inspection=command(cli+['image','inspect',IMAGE,'--format',fmt],20)
    image=json.loads(require_success(inspection))
    if image['Os']!='linux' or image['Architecture']!='arm64' or not any(x.endswith('@'+DIGEST) for x in image['RepoDigests']) or image['Entrypoint'] not in [None,[]]:raise RuntimeError('actual helper image identity/platform/entrypoint mismatches pinned descriptor')
    binding={'task_id':TASK,'recorded_at_UTC':now(),'pinned_reference':IMAGE,'actual_image':image,'daemon_observation':daemon,'image_pulled_this_invocation':pulled,'scope':'Helper image and daemon observation only; not an experiment arithmetic dependency or launch admission.'}
    path=HERE/'image-binding.json'
    if path.exists():
        old=json.loads(path.read_text())
        if old['actual_image']!=image or old['pinned_reference']!=IMAGE:raise RuntimeError('existing image binding differs; refuse overwrite')
    else:
        with path.open('x') as f:json.dump(binding,f,indent=2);f.write('\n')
    return binding

def case(cli,label,memory,expected,mode):
    row={'id':label,'started_at_UTC':now(),'start_attempt_count':0,'container_id':None,'passed':False,'watchdog':False,'cleanup_complete':False};cid=None;t=time.perf_counter()
    try:
        name='codex-guard-e7e0db-'+label.replace('_','-')+'-'+uuid.uuid4().hex[:8]
        argv=cli+['create','--name',name,'--label','crypto.autoresearch.task='+TASK,'--platform','linux/arm64','--user','65534:65534','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--cgroupns','private','--pids-limit','32','--cpus','1','--memory',str(memory),'--memory-swap',str(memory),'--tmpfs','/tmp:rw,size=16m','-e','PYTHONDONTWRITEBYTECODE=1','-e','PYTHONUNBUFFERED=1',IMAGE,'python3','-B','-c',CHILD,mode,str(expected)]
        cid=require_success(command(argv,30))
        if not re.fullmatch('[0-9a-f]{64}',cid):raise RuntimeError('create returned no exact container ID')
        row['container_id']=cid;row['start_attempt_count']=1
        attached=command(cli+['start','--attach',cid],60)
        row['watchdog']=attached['timed_out']
        if attached['timed_out']:command(cli+['kill',cid],15)
        inspection=json.loads(require_success(command(cli+['inspect',cid],20)))[0]
        if inspection['State']['Running']:
            row['unexpected_running_after_client_return']=True;command(cli+['kill',cid],15)
            inspection=json.loads(require_success(command(cli+['inspect',cid],20)))[0]
        row['terminal_state']=inspection['State']
        # Keep only needed isolation metadata; never capture unrelated daemon/config data.
        row['actual_isolation']={k:inspection['HostConfig'].get(k) for k in ['NetworkMode','ReadonlyRootfs','CapDrop','SecurityOpt','PidsLimit','NanoCpus','Memory','MemorySwap','Binds','CgroupnsMode','Tmpfs']}
        records=[]
        for line in attached['stdout'].splitlines():
            try:records.append(json.loads(line))
            except json.JSONDecodeError:row.setdefault('non_json_stdout',[]).append(line)
        row['child_records']=records
        cfg=next((x for x in records if x.get('event')=='configuration'),None)
        iso=row['actual_isolation']
        isolation_ok=(iso['NetworkMode']=='none' and iso['ReadonlyRootfs'] is True and 'ALL' in (iso['CapDrop'] or []) and any(x.startswith('no-new-privileges') for x in iso['SecurityOpt'] or []) and iso['PidsLimit']==32 and iso['NanoCpus']==1000000000 and iso['Memory']==memory and iso['MemorySwap']==memory and not iso['Binds'] and iso['CgroupnsMode']=='private' and iso['Tmpfs']=={'/tmp':'rw,size=16m'})
        common=(cfg is not None and isolation_ok and not row['watchdog'] and not row.get('unexpected_running_after_client_return') and not inspection['State']['Running'])
        if label=='profile_exact':row['passed']=common and not cfg['mismatches'] and inspection['State']['ExitCode']==0 and any(x.get('event')=='profile_accepted' for x in records)
        elif label=='profile_mismatch_rejected':row['passed']=common and cfg['values']['memory.max']==str(memory) and cfg['mismatches']==['memory.max'] and inspection['State']['ExitCode']==42 and any(x.get('event')=='typed_configuration_refusal' for x in records)
        else:row['passed']=common and not cfg['mismatches'] and inspection['State']['OOMKilled'] is True and inspection['State']['ExitCode']==137 and any(x.get('event')=='before_allocation' and x.get('requested_bytes')==134217728 for x in records)
    except Exception as exc:row['error']={'type':type(exc).__name__,'message':str(exc)}
    finally:
        if cid and re.fullmatch('[0-9a-f]{64}',cid):
            current=command(cli+['inspect','--format','{{json .State}}',cid],15)
            if current['exit_code']==0:
                state=json.loads(current['stdout'])
                if state['Running']:
                    command(cli+['kill',cid],15)
                    row['cleanup_killed_owned_container']=True
                removed=command(cli+['rm',cid],15)
                row['cleanup_complete']=removed['exit_code']==0 and not removed['timed_out']
        row['ended_at_UTC']=now();row['wall_seconds']=time.perf_counter()-t
        row['passed']=bool(row['passed'] and row['cleanup_complete'])
    return row

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--prior-cases',type=int,default=0);parser.add_argument('--final-reserve',type=int,default=3);parser.add_argument('--prior-pulls',type=int,default=0);args=parser.parse_args()
    if not args.execute:parser.error('explicit --execute required under the published task claim')
    if args.prior_pulls not in [0,1]:parser.error('at most one image pull across this task')
    if args.prior_cases<0 or args.final_reserve<0 or args.prior_cases+3+args.final_reserve>6:parser.error('frozen six-container cumulative reservation exceeded')
    result={'schema':'crypto.autoresearch.runtime_control_probe.v1','task_id':TASK,'decision_id':DECISION,'started_at_UTC':now(),'prior_case_start_attempts':args.prior_cases,'pre_reserved_case_start_attempts':3,'final_reserve':args.final_reserve,'maximum_case_start_attempts':6,'scientific_runs':0,'commands':COMMANDS,'cases':[],'probe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    t=time.perf_counter()
    try:
        exe='/usr/local/bin/docker';endpoint=docker_endpoint(exe);cli=[exe,'--host',endpoint];result['endpoint_scope']='verified local Unix socket';result['image_binding']=image_and_daemon(cli,args.prior_pulls)
        for label,memory,expected,mode in [('profile_exact',8589934592,8589934592,'profile'),('profile_mismatch_rejected',67108864,8589934592,'profile'),('oom_small_limit',67108864,67108864,'oom')]:result['cases'].append(case(cli,label,memory,expected,mode))
    except Exception as exc:result['infrastructure_error']={'type':type(exc).__name__,'message':str(exc)}
    result.update(ended_at_UTC=now(),wall_seconds=time.perf_counter()-t,case_start_attempts=sum(x['start_attempt_count'] for x in result['cases']),passed_cases=sum(x['passed'] for x in result['cases']),host_cli_cpu_seconds=sum(x['host_cli_cpu_seconds'] for x in COMMANDS),host_process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024))
    result['prior_image_pull_attempts']=args.prior_pulls
    result['image_pull_attempts_this_invocation']=sum(len(c['argv'])>3 and c['argv'][1]=='--host' and c['argv'][3]=='pull' for c in COMMANDS)
    result['complete_suite_pass']=len(result['cases'])==3 and result['passed_cases']==3
    result['limitations']=['8GiB configuration readback is not8GiB pressure testing orproof of physical8GiB availability.','OOM control is scoped only to64MiB in this helper image; child post-OOM CPU/RSS is unavailable. Host Docker CLI CPU is not container CPU.','No scientific implementation,arithmetic dependency,launch signature ormeasurement admission was tested.','Only task-created containers are removed; the pinned helper image remains in the local cache.']
    print(json.dumps(result,indent=2,allow_nan=False));return 0 if result['complete_suite_pass'] else 2
if __name__=='__main__':raise SystemExit(main())
