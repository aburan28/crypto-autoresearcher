"""Independent source/custody review. No producer tests/controllers are executed.

The --watch mode monitors only its checker and journaled fixture children.
All simulated OS calls are made against a replacement namespace, never real FDs.
The three real fixtures use current-user pipes and children with no privileges,
network, cgroup, Docker or pressure actions. A failed predicate is retained.
"""
from __future__ import annotations
import argparse, ast, base64, ctypes, difflib, hashlib, importlib.util, json
import os, pathlib, resource, signal, stat, subprocess, sys, time, traceback
from contextlib import contextmanager
from dataclasses import asdict, replace
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

TASK = 'TASK-20260911-fab863'
PRODUCER = 'coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260910-f299db'
CID = 'c'*64
NONCE = 'd'*12
IMAGE_ID = 'sha256:'+'e'*64
CASES = []
OBS = {}
JOURNAL = None
SOURCE = None
REPO = None
s = c = h = None

def now(): return datetime.now(timezone.utc).isoformat()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def enc(raw): return base64.b64encode(raw).decode('ascii')
def dec(raw): return base64.b64decode(raw, validate=True)
def dump(path, data):
    with open(path, 'x', encoding='utf-8') as f:
        json.dump(data, f, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
def note(event, **fields):
    row = dict(event=event, at_UTC=now(), monotonic_ns=time.monotonic_ns(), **fields)
    with open(JOURNAL, 'a', encoding='utf-8') as f:
        f.write(json.dumps(row, sort_keys=True)+'\n'); f.flush(); os.fsync(f.fileno())
def need(ok, detail='predicate failed'):
    if not ok: raise AssertionError(detail)
def thrown(fn, typ=Exception):
    try: fn()
    except typ as error: return error
    raise AssertionError('required exception absent')
def add(name, fn): CASES.append((name, fn))
def load_modules():
    global s,c,h
    for name in ('container','supervisor','host'):
        spec=importlib.util.spec_from_file_location(name,SOURCE/(name+'.py'))
        mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod)
    c=sys.modules['container']; s=sys.modules['supervisor']; h=sys.modules['host']

def facts(): return s.MountFacts('Linux','cgroup2',s.CGROUP2_SUPER_MAGIC,'/injected',True,'injected')
def handle(fd=401, path=None, inode=41): return s.DirectoryHandle(fd,path or 'docker/'+CID,9,inode,facts())
def st(inode, mode=stat.S_IFDIR): return SimpleNamespace(st_dev=9,st_ino=inode,st_mode=mode)

class FakeOS:
    """Closed OS surface; unknown calls fail instead of reaching the host."""
    O_RDONLY=os.O_RDONLY; O_WRONLY=os.O_WRONLY; O_DIRECTORY=os.O_DIRECTORY; O_NOFOLLOW=os.O_NOFOLLOW
    WNOHANG=os.WNOHANG
    def __init__(self):
        self.calls=[]; self.faults={}; self.opens=500; self.fd_inode={401:41,402:42}
        self.names={'docker':51,CID:52,'guard-worker':42,'guard-supervisor':42}
        self.blocks=[b'0\n',b'']; self.entries=['foreign','cgroup.procs']
    def call(self,name,*args,**kw):
        self.calls.append([name,list(args),kw])
        fault=self.faults.get(name)
        if callable(fault): return fault(*args,**kw)
        if isinstance(fault,BaseException): raise fault
    def open(self,name,flags,**kw):
        override=self.call('open',name,flags,**kw)
        if override is not None:return override
        self.opens+=1; self.fd_inode[self.opens]=self.names.get(name,50); return self.opens
    def close(self,fd): return self.call('close',fd)
    def fstat(self,fd): return self.call('fstat',fd) or st(self.fd_inode[fd])
    def stat(self,name,**kw): return self.call('stat',name,**kw) or st(self.names.get(name,60),stat.S_IFREG if name=='cgroup.procs' else stat.S_IFDIR)
    def listdir(self,fd): self.call('listdir',fd); return self.entries
    def mkdir(self,*a,**kw): return self.call('mkdir',*a,**kw)
    def rmdir(self,*a,**kw): return self.call('rmdir',*a,**kw)
    def read(self,fd,n):
        v=self.call('read',fd,n)
        if v is not None:return v
        v=self.blocks.pop(0)
        if isinstance(v,BaseException):raise v
        return v
    def write(self,fd,data):
        v=self.call('write',fd,data.hex()); return len(data) if v is None else v
    def getpid(self): return 7001
    def waitstatus_to_exitcode(self,x): return os.waitstatus_to_exitcode(x)
    def kill(self,*args): return self.call('kill',*args)
    def setgroups(self,*args): return self.call('setgroups',*args)
    def setgid(self,*args): return self.call('setgid',*args)
    def setuid(self,*args): return self.call('setuid',*args)

class Groups:
    """Independent stateful cgroup interface with no-internal-process rule."""
    def __init__(self, fault=''):
        self.fault=fault; self.root='docker/'+CID; self.members={self.root:[7001]}
        self.files={}; self.enabled=False; self.calls=[]; self.after=False
    def open_verified_container_root(self,cid): return self.root
    def relative_path(self,d): return ('foreign/'+CID) if self.fault=='wrong_root' else d
    def mount_facts(self,d):
        f=asdict(facts())
        if self.fault=='mount': f['filesystem_type']='tmpfs'
        return f
    def read_text(self,d,n):
        if n=='cgroup.type': return 'domain'
        if n=='cgroup.controllers': return 'memory'
        if n=='cgroup.subtree_control': return 'memory' if self.enabled else ''
        if n=='memory.events':
            g,k=(1,2) if self.after else (0,0)
            if self.fault=='stale_counter':g,k=4,7
            if self.fault=='missing_counter':return 'oom_kill 2\n'
            return f'oom_group_kill {g}\noom_kill {k}\n'
        if n=='cgroup.events':return 'populated '+str(int(bool(self.members.get(d))))+'\n'
        if n=='memory.peak' and self.fault=='optional_close_uncertainty':
            error=s.GuardError('cgroup_read_too_large','memory.peak')
            error.descriptor_disposition={'fd':599,'disposition':'unknown'}
            error.operation_observations={'action':'read_text','received_base64':enc(b'123'),'decoded_complete':False}
            raise error
        if n in ('memory.current','memory.peak','cpu.stat'):return '0'
        value=self.files.get((d,n),'0')
        if self.fault=='profile' and n=='memory.max':return '7'
        return value
    def write_text(self,d,n,v):
        self.calls.append(('write',d,n,v))
        if n=='cgroup.subtree_control':
            if v=='+memory':need(not self.members[self.root],'internal process on enable')
            if v=='-memory' and self.fault=='disable': raise s.GuardError('injected_disable')
            self.enabled=v=='+memory'
        else:self.files[d,n]=v
    def create_child(self,p,n): self.calls.append(('create',n)); d=p+'/'+n; self.members[d]=[]; return d
    def list_children(self,d):return ['foreign'] if self.fault=='preexisting' else []
    def list_direct_members(self,d):
        if d.endswith('guard-supervisor') and self.fault=='initial_membership' and not self.after:return []
        if d.endswith('guard-supervisor') and self.fault=='final_membership' and self.after:return []
        return self.members.get(d,[])
    def move_pid(self,d,pid):
        self.calls.append(('move',d,pid))
        if d==self.root:need(not self.enabled,'internal process on return')
        if d.endswith('guard-worker') and self.fault=='migration':raise s.GuardError('injected_migration')
        for v in self.members.values():
            if pid in v:v.remove(pid)
        self.members[d].append(pid)
    def child_is_populated(self,d):return bool(self.members.get(d))
    def remove_empty_child(self,p,n,original):
        need(original==p+'/'+n,'original child must reach cleanup')
        need(not self.members.get(original),'populated child')
        self.calls.append(('remove',n)); self.members.pop(original,None)
        if self.fault=='remove':raise s.GuardError('injected_remove')
    def close_handle(self,d):self.calls.append(('close',d))

class Processes:
    def __init__(self,g):self.g=g; self.child=None;self.released=False;self.done=False;self.acked=False
    def supervisor_pid(self):return 7001
    def fork_paused(self,action,inherited):
        need(all((self.g.root+'/guard-worker',n) in self.g.files for n in ('memory.max','memory.swap.max','memory.oom.group')),'profile before fork')
        self.child=s.ChildHandle(7002,'synthetic-only');self.g.members[self.g.root+'/guard-supervisor'].append(7002);return self.child
    def release(self,ch):need(self.g.members[self.g.root+'/guard-worker']==[7002]);self.released=True
    def confirm_membership(self,ch,pid):need(pid==7003);self.acked=True
    def wait_terminal(self,ch,timeout,event_observer=None,poll_observer=None):
        group=self.g; case=OBS['case']; worker=group.root+'/guard-worker'
        events=[{'event':'privilege_drop_verified','uid':65534,'gid':65534,'capabilities_cleared':True,'oom_score_adj':0}]
        if case=='small_group_oom':
            group.members[worker]=[7002,7003]
            events += [{'event':'auxiliary_spawned','pid':7003},{'event':'auxiliary_ready','pid':7003}]
            if group.fault=='auxiliary':group.members[worker]=[7002,7004]
            event_observer(tuple(events));need(self.acked)
            events += [{'event':'membership_acknowledged','pid':7003},{'event':'before_allocation'}]
            poll_observer()
        else:events.append({'event':'profile_accepted'} if case=='exact_profile' else {'event':'typed_configuration_refusal','reason':'memory_guard_unavailable'})
        group.members[worker]=[];group.after=True;self.done=True
        t=s.WorkerTerminal(0 if case=='exact_profile' else 42 if case=='group_zero_refused' else None,
             'SIGKILL' if case=='small_group_oom' else None,False,tuple(events),65534,65534,True,0,
             case=='small_group_oom',int(case=='small_group_oom'),int(case=='small_group_oom'),True,7002,True,True)
        changes={'uid':{'effective_uid':0},'capability':{'capabilities_cleared':False},'protected':{'oom_score_adj':-1000},
          'not_reaped':{'reaped':False},'not_closed':{'descriptors_closed':False},'report':{'report_complete':False},
          'manual':{'manual_kill':True},'watchdog':{'watchdog':True},'group0_stress':{'allocations_started':1}}
        return replace(t,**changes.get(group.fault,{}))
    def finalize_owned_child(self,ch,terminate):
        self.done=True
        for v in self.g.members.values():
            if 7002 in v:v.remove(7002)
            if 7003 in v:v.remove(7003)
        return {'reaped':True,'descriptors_closed':True,'pid':ch.pid}
    def active_owned_children(self):return [] if self.done or self.child is None else [7002]

def supervisor(case='exact_profile',fault=''):
    OBS['case']=case;g=Groups(fault);p=Processes(g)
    out=s.GroupOomSupervisor(g,p).run(s.SupervisorRequest.fixed(case,CID))
    return out,g,p

def image_data():return {'Id':IMAGE_ID,'Os':'linux','Architecture':'arm64','RepoDigests':[c.PINNED_IMAGE]}
def inspect_data():
    return {'Id':CID,'Image':IMAGE_ID,'Config':{'Image':c.PINNED_IMAGE,'Labels':{'crypto.autoresearch.task':c.TASK_ID,'crypto.autoresearch.nonce':NONCE},'User':'0:0','OpenStdin':True,'AttachStdin':True,'Tty':False,'Cmd':['python3','-B','/opt/group-oom/container.py']},
      'HostConfig':{'NetworkMode':'none','ReadonlyRootfs':True,'CapDrop':['ALL'],'CapAdd':['SETUID','SETGID'],'SecurityOpt':['no-new-privileges:true'],'CgroupnsMode':'host','PidMode':'private','PidsLimit':32,'NanoCpus':1000000000,'Memory':8*1024**3,'MemorySwap':8*1024**3,'Tmpfs':{'/tmp':'rw,size=16m'},'Privileged':False,'AutoRemove':False},
      'State':{'Running':False,'ExitCode':0,'OOMKilled':False},'Mounts':[{'Type':'bind','Source':'/sys/fs/cgroup','Destination':'/host-cgroup','RW':True}]}
def result(argv,stdin,timeout,out='',code=0):
    return h.CommandResult(tuple(argv),now(),now(),code,out,'',False,timeout,0.0,len(stdin or b''),sha(stdin) if stdin is not None else None,None,None,True,stdout_base64=enc(out.encode()),stderr_base64='')
class Commands:
    def __init__(self,case,fault='',inner=None):self.case=case;self.fault=fault;self.calls=[];self.inspects=0;self.inner=inner
    def run(self,argv,stdin,timeout):
        action=argv[3];self.calls.append(action)
        if action in ('kill','rm') and action in self.fault:
            if 'typed' in self.fault:raise h.CommandTransportFailure({'primary_exception':{'type':'OSError','message':'injected'},'launch_state':'not_started','process_pid':None,'exit_code':None,'terminal_observed':None,'stdout_base64':None,'stderr_base64':None,'cleanup_failures':[]})
            raise OSError('injected '+action)
        if action=='image':out=json.dumps([image_data()])
        elif action=='create':out=CID+'\n'
        elif action=='inspect':
            raw=inspect_data();self.inspects+=1
            if self.inspects==1:
                if self.fault=='nonce_missing':raw['Config']['Labels'].pop('crypto.autoresearch.nonce')
                if self.fault=='nonce_wrong':raw['Config']['Labels']['crypto.autoresearch.nonce']='f'*12
                if self.fault=='id_wrong':raw['Id']='a'*64
            elif self.fault=='missing_running':raw['State'].pop('Running')
            out=json.dumps([raw])
        elif action=='start':
            body=self.inner
            if body is None:body=supervisor(self.case,'remove' if 'kill' in self.fault else '')[0].as_dict()
            doc=c.source_result(c.StartupIdentity(c.TASK_ID,CID,self.case),body)
            if self.fault=='schema':doc['schema']='fabricated.v1'
            if self.fault=='startup':doc=c.source_startup_failure(ValueError('injected'))
            if self.fault=='false_cleanup':doc['outcome']['cleanup_complete']=False
            out=json.dumps(doc)
        else:out=''
        return result(argv,stdin,timeout,out)
def host(case='exact_profile',fault='',inner=None):
    cmd=Commands(case,fault,inner); hashes={name:sha((SOURCE/name).read_bytes()) for name in h.HELPERS}
    outcome=h.DockerHostAdapter(cmd,SOURCE,hashes,lambda:NONCE).run_case(case)
    return outcome,cmd

def descriptor_control(kind):
    fake=FakeOS();d=s.DescriptorCgroupTransport();p=handle();original=handle(402,p.relative_path+'/guard-worker',42)
    primary=OSError('independent primary');secondary=OSError('independent close'); observed={}
    with patch.object(s,'os',fake):
        if kind.startswith('enumerate_'):
            et={'permission':PermissionError,'disappear':FileNotFoundError,'other':OSError}.get(kind[10:])
            if et:fake.faults['stat']=et('independent affected entry');e=thrown(lambda:d.list_children(p));need(e.code=='cgroup_child_stat_failed' and 'foreign' in e.detail)
            else:need(d.list_children(p)==['foreign'])
        elif kind.startswith('child_'):
            fake.faults['fstat']=primary
            if kind.endswith('close'):fake.faults['close']=secondary
            e=thrown(lambda:d._open_child(p,'guard-worker'));need(e is primary)
            need([x[1][0] for x in fake.calls if x[0]=='close']==[501])
            need(s._descriptor_uncertainty(e)==kind.endswith('close'));observed=s._exception_observation(e)
        elif kind.startswith('io_'):
            mode=kind[3:];fake.faults['close']=secondary
            if mode=='read':fake.blocks=[b'prefix',primary]
            if mode=='decode':fake.blocks=[b'\xff',b'']
            if mode=='limit':fake.blocks=[b'123',b'']
            if mode=='write':fake.faults['write']=primary
            with patch.object(s,'MAX_EVENT_BYTES',2 if mode=='limit' else 1048576):
                e=thrown(lambda:d.write_text(p,'memory.max','9') if mode.startswith('write') else d.read_text(p,'memory.peak'))
            need(s._descriptor_uncertainty(e));observed=s._exception_observation(e)
            if mode in ('read','write'):need(e is primary)
            if mode=='decode':need(isinstance(e,UnicodeDecodeError))
            if mode in ('read_ok','write_ok'):need(e is secondary)
        elif kind.startswith('remove_'):
            mode=kind[7:];d._created_children[(9,41,'guard-worker')]=original
            if mode=='unowned':d._created_children.clear()
            if mode=='closed':original.closed=True
            if mode=='wrong_parent':original.relative_path='elsewhere/guard-worker'
            if mode=='parent_drift':fake.fd_inode[401]=99
            if mode=='original_drift':fake.fd_inode[402]=99
            if mode=='replacement':fake.names['guard-worker']=99
            if mode=='rmdir':fake.faults['rmdir']=primary
            if mode in ('replacement_close','success_close'):
                fake.faults['close']=secondary
                if mode=='replacement_close':fake.names['guard-worker']=99
            with patch.object(d,'child_is_populated',return_value=mode=='populated'),patch.object(d,'list_direct_members',return_value=[]):
                if mode=='success':d.remove_empty_child(p,'guard-worker',original);need(not d._created_children)
                else:
                    e=thrown(lambda:d.remove_empty_child(p,'guard-worker',original));observed=s._exception_observation(e)
                    if mode=='success_close':need(e is secondary and e.operation_observations['name_removed'])
                    elif mode=='replacement_close':need(e.code=='cgroup_removal_identity_changed' and s._descriptor_uncertainty(e))
                    if mode not in ('rmdir','success_close'):need(not any(x[0]=='rmdir' for x in fake.calls))
        elif kind.startswith('create_'):
            mode=kind[7:];fake.faults['fstat']=primary
            if mode=='unknown_identity':fake.faults['stat']=primary
            if mode in ('rollback','both'):fake.faults['rmdir']=OSError('independent rollback')
            if mode=='both':fake.faults['close']=secondary
            if mode=='replacement':
                count=[0]
                def named(*a,**kw):count[0]+=1;return st(42 if count[0]==1 else 99)
                fake.faults['stat']=named
            e=thrown(lambda:d.create_child(p,'guard-worker'));need(e is primary);observed=s._exception_observation(e)
            need(e.pending_created_directory['disposition']==('removed' if mode=='normal' else 'unresolved'))
            if mode=='both':need(len(e.cleanup_failures)==2)
        elif kind.startswith('relative_'):
            mode=kind[9:];calls=[0]
            def fs(fd):
                calls[0]+=1
                if mode=='fstat' and calls[0]==2:raise primary
                return st(fake.fd_inode[fd])
            fake.faults['fstat']=fs
            if mode=='transfer_close':
                def close(fd):
                    if fd==502:raise primary
                fake.faults['close']=close
            if mode=='verify':verifier=SimpleNamespace(verify=lambda *a:(_ for _ in ()).throw(primary))
            else:verifier=SimpleNamespace(verify=lambda *a:facts())
            d=s.DescriptorCgroupTransport('/injected',verifier)
            e=thrown(lambda:d._open_relative_dir('docker/'+CID));need(e is primary)
            observed=s._exception_observation(e);closed=[x[1][0] for x in fake.calls if x[0]=='close'];opened=[501+i for i,x in enumerate([r for r in fake.calls if r[0]=='open'])]
            need(sorted(closed)==opened and len(closed)==len(set(closed)))
        elif kind=='root_refusal':
            d=s.DescriptorCgroupTransport(membership_reader=SimpleNamespace(own_relative_path=lambda cid:'docker/'+cid))
            bad=handle(501,'docker/'+'a'*64);fake.faults['close']=secondary
            with patch.object(d,'_open_relative_dir',return_value=bad):e=thrown(lambda:d.open_verified_container_root(CID))
            need(s._descriptor_uncertainty(e));observed=s._exception_observation(e)
        elif kind=='close_no_retry':
            fake.faults['close']=InterruptedError('uncertain')
            thrown(lambda:d.close_handle(p));e=thrown(lambda:d.close_handle(p));need(e.code=='descriptor_close_disposition_unknown');need(len(fake.calls)==1)
        elif kind=='inherited_close':
            fake.faults['close']=InterruptedError('uncertain')
            runtime=s.PosixWorkerRuntime(lambda:{},lambda:[],[p,original],lambda e:None,lambda p:None,lambda:None)
            e=thrown(runtime.bootstrap_after_migration);need(len([x for x in fake.calls if x[0]=='close'])==2);need(not any(x[0].startswith('set') for x in fake.calls));observed=s._exception_observation(e)
    return {'observed':observed,'injected_os_calls':fake.calls}

def posix_close(mode):
    fake=FakeOS();state=s._PosixChildState(401,402,7002,wait_status=0,reaped=True,report_eof=True)
    p=s.PosixProcessTransport(lambda *a:None);ch=s.ChildHandle(7002,'injected');p._children[ch.token]=state
    if mode=='failure':fake.faults['close']=OSError('uncertain descriptor close')
    else:
        seen=[False]
        def closing(fd):
            if fd==401 and not seen[0]:seen[0]=True;raise InterruptedError('may have closed')
        fake.faults['close']=closing
    with patch.object(s,'os',fake):
        err=None
        try:record=p.finalize_owned_child(ch,True)
        except Exception as e:err=s._exception_observation(e);record=p.custody_record(ch)
    OBS['posix_close_'+mode]={'custody':record,'error':err,'calls':fake.calls}
    if mode=='failure':need(not record or not record.get('descriptors_closed'), 'close OSError must not produce descriptors_closed=true')
    else:need(len([x for x in fake.calls if x[:2]==['close',[401]]])==1,'interrupted close must not retry stale fd integer')

def barrier(secondary):
    p=s.PosixProcessTransport(lambda *a:None);child=s.ChildHandle(7002,'injected');p._children['injected']=s._PosixChildState(401,402,7002)
    primary=OSError('independent barrier');other=s.GuardError('independent_finalize')
    with patch.object(p,'_write_all',side_effect=primary),patch.object(p,'finalize_owned_child',side_effect=other if secondary else None,return_value={}):e=thrown(lambda:p.release(child))
    need(e is primary)
    if secondary:need(e.cleanup_failures[0]['code']=='barrier_release_cleanup_failed')
    g=Groups();gp=Processes(g)
    with patch.object(gp,'release',side_effect=e):out=s.GroupOomSupervisor(g,gp).run(s.SupervisorRequest.fixed('exact_profile',CID))
    serialized=c.source_result(c.StartupIdentity(c.TASK_ID,CID,'exact_profile'),out.as_dict())
    need('independent barrier' in json.dumps(serialized))
    if secondary:need('independent_finalize' in json.dumps(serialized))
    return {'serialized':serialized}

def subprocess_case(mode):
    class Process:
        pid=850001;returncode=None
        def __init__(self):self.n=0
        def communicate(self,**kw):
            self.n+=1
            if mode=='communication' and self.n==1:raise OSError('primary communication')
            if mode=='timeout' and self.n==1:raise subprocess.TimeoutExpired('injected',0.1,output=b'pre',stderr=b'er')
            self.returncode=-9 if self.n>1 else 0
            return b'prefix\xff',b'error'
    process=Process();fake=SimpleNamespace(killpg=lambda *a:None)
    with patch.object(h.subprocess,'Popen',side_effect=OSError('launch') if mode=='launch' else None,return_value=process),patch.object(h,'os',fake):
        if mode in ('launch','communication'):
            e=thrown(lambda:h.SubprocessTransport().run(['injected'],b'in',.1));obs=e.observations
            if mode=='launch':need(obs['launch_state']=='not_started' and obs['stdout_base64'] is None and obs['exit_code'] is None)
            else:need(obs['terminal_observed'] and dec(obs['stdout_base64'])==b'prefix\xff')
        else:
            r=h.SubprocessTransport().run(['injected'],b'in',.1);obs=asdict(r);need(dec(r.stdout_base64)==b'prefix\xff')
    return obs

@contextmanager
def real_custody():
    parent=os.getpid();pids=set();fds={};errors=[]
    rf,rw,rp,rc=os.fork,os.waitpid,os.pipe,os.close
    def fork():
        pid=rf()
        if os.getpid()==parent and pid>0:pids.add(pid);note('fixture_created',pid=pid,observer_pid=parent)
        return pid
    def pipe():
        pair=rp()
        if os.getpid()==parent:
            for fd in pair:
                z=os.fstat(fd);fds[fd]=(z.st_dev,z.st_ino);note('descriptor_created',fd=fd,identity=fds[fd])
        return pair
    def close(fd):
        value=rc(fd)
        if os.getpid()==parent and fd in fds:fds.pop(fd);note('descriptor_closed',fd=fd)
        return value
    def wait(pid,options):
        a,b=rw(pid,options)
        if os.getpid()==parent and a in pids:pids.remove(a);note('fixture_terminal',pid=a,wait_status=b,exit_code=os.waitstatus_to_exitcode(b),reaped=True)
        return a,b
    try:
        with patch.object(os,'fork',fork),patch.object(os,'pipe',pipe),patch.object(os,'close',close),patch.object(os,'waitpid',wait):yield
    finally:
        for pid in list(pids):
            try:
                a,b=rw(pid,os.WNOHANG)
                if a==0:os.kill(pid,signal.SIGKILL);a,b=rw(pid,0)
                if a==pid:pids.remove(pid);note('fixture_terminal',pid=pid,wait_status=b,exit_code=os.waitstatus_to_exitcode(b),reaped=True,observer_cleanup=True)
            except BaseException as e:errors.append(str(e))
        for fd,identity in list(fds.items()):
            try:
                z=os.fstat(fd);need((z.st_dev,z.st_ino)==identity,'descriptor reused');rc(fd);fds.pop(fd);note('descriptor_closed',fd=fd,observer_cleanup=True)
            except BaseException as e:errors.append(str(e))
        note('fixture_custody_end',live_pids=sorted(pids),unclosed_fds=sorted(fds),errors=errors)
        need(not pids and not fds and not errors,'real fixture custody incomplete')

def real_fixture(mode):
    def factory(report,*args):return SimpleNamespace(emit=report)
    p=s.PosixProcessTransport(factory)
    def action(rt):
        if mode=='watchdog':time.sleep(1.0)
        if mode=='drain':
            for i in range(8):rt.emit({'event':'benign_payload','i':i,'text':'a'*8192})
        rt.emit({'event':'privilege_drop_verified','uid':65534,'gid':65534,'capabilities_cleared':True,'oom_score_adj':0})
        return 0
    with real_custody():
        child=p.fork_paused(action,())
        try:
            if mode=='barrier':
                with patch.object(p,'_write_all',side_effect=OSError('benign barrier fault')):thrown(lambda:p.release(child))
            else:p.release(child);p.wait_terminal(child,.12 if mode=='watchdog' else 2.0)
        finally:record=p.finalize_owned_child(child,True)
        need(record['reaped'] and record['descriptors_closed'])
        need(not p.active_owned_children())
    return {'custody':record,'deliberate_payload_bytes':65536 if mode=='drain' else 0}

def integrated_removal(which, removed):
    fake=FakeOS();d=s.DescriptorCgroupTransport();parent=handle();original=handle(402,parent.relative_path+'/'+which,42)
    d._created_children[(9,41,which)]=original;fake.names[which]=42 if removed else 99
    fake.faults['close']=OSError('integrated uncertain close')
    g=Groups();p=Processes(g);normal=g.remove_empty_child
    def remove(pth,name,expected):
        if name!=which:return normal(pth,name,expected)
        with patch.object(s,'os',fake),patch.object(d,'child_is_populated',return_value=False),patch.object(d,'list_direct_members',return_value=[]):
            d.remove_empty_child(parent,which,original)
    with patch.object(g,'remove_empty_child',side_effect=remove):out=s.GroupOomSupervisor(g,p).run(s.SupervisorRequest.fixed('exact_profile',CID))
    wire=c.source_result(c.StartupIdentity(c.TASK_ID,CID,'exact_profile'),out.as_dict())
    need(not out.cleanup_complete and out.status=='failed_custody')
    rows=[x for x in wire['outcome']['cleanup'] if x['action']=='remove_empty_'+which.replace('-','_')]
    need(len(rows)==1 and not rows[0]['ok'])
    error=rows[0]['exception']
    if removed:need(error['operation_observations']['name_removed'] and error['descriptor_disposition']['disposition']=='unknown')
    else:need(error['code']=='cgroup_removal_identity_changed' and error['cleanup_failures'][0]['descriptor']['disposition']=='unknown')
    ho,_=host(inner=out.as_dict());need(ho.status=='failed');return {'container':wire,'host':ho.as_dict()}

def readonly_worker(mode, failed):
    primary=OSError('independent readonly primary');secondary=OSError('independent readonly close');directory=handle(501,'docker/'+CID+'/guard-worker')
    def read(*a):
        if failed:raise primary
        return '0'
    cg=SimpleNamespace(open_verified_worker_readonly=lambda *a:directory,read_text=read,list_direct_members=lambda *a:read(),close_handle=lambda *a:(_ for _ in ()).throw(secondary))
    runtime=s.make_posix_runtime_factory(cg,CID)(lambda e:None,[directory],lambda pid:None,lambda:None)
    error=thrown(runtime.read_profile if mode=='profile' else runtime.read_membership)
    need(error is (primary if failed else secondary));need(s._descriptor_uncertainty(error));return s._exception_observation(error)

def native_bootstrap(capability):
    fake=FakeOS();fake.geteuid=lambda:65534;fake.getegid=lambda:65534;events=[]
    def path(name):return SimpleNamespace(read_text=lambda **kw:('CapEff:\t'+('0000000000000000' if capability else '0000000000000001')+'\n') if name.endswith('status') else '0')
    runtime=s.PosixWorkerRuntime(lambda:{},lambda:[],[handle(401)],events.append,lambda p:None,lambda:None)
    with patch.object(s,'os',fake),patch.object(s,'Path',side_effect=path):
        if capability:runtime.bootstrap_after_migration()
        else:need(thrown(runtime.bootstrap_after_migration).code=='child_security_postcondition_failed')
    names=[r[0] for r in fake.calls];need(names==['close','setgroups','setgid','setuid']);need(events[0]['capabilities_cleared']==capability)
    return {'calls':fake.calls,'events':events}

def worker_readback(mode):
    events=[];pressure=[];required=s.required_worker_profile('exact_profile');profile=dict(required.as_files())
    if mode=='group':profile['memory.oom.group']='0'
    if mode=='memory':profile['memory.max']='7'
    rt=SimpleNamespace(bootstrap_after_migration=lambda:events.append('bootstrap'),read_profile=lambda:profile,read_membership=lambda:[7001] if mode!='membership' else [7009],emit=lambda e:events.append(e),run_fixed_small_group_oom=lambda:pressure.append(True))
    with patch.object(s,'os',SimpleNamespace(getpid=lambda:7001)):
        if mode=='membership':need(thrown(lambda:s._worker_action('exact_profile',required)(rt)).code=='worker_membership_readback_mismatch')
        else:need(s._worker_action('exact_profile',required)(rt)==(0 if mode=='good' else 42))
    need(not pressure);return {'events':events}

def native_mount(mode):
    magic=s.CGROUP2_SUPER_MAGIC if mode!='magic' else 0
    def fstatfs(fd,pointer):need(fd==401);pointer._obj.f_type=magic;return 0
    flags='ro' if mode=='readonly' else 'rw'
    text=f'22 11 0:23 / /injected {flags} - cgroup2 cgroup {flags}\n'
    if mode=='ambiguous':text+=text
    with patch.object(s.platform,'system',return_value='Darwin' if mode=='system' else 'Linux'),patch.object(s.ctypes,'CDLL',return_value=SimpleNamespace(fstatfs=fstatfs)),patch.object(s,'Path',return_value=SimpleNamespace(read_text=lambda **kw:text)):
        if mode=='good':need(s.NativeMountVerifier().verify(401,'/injected').read_write)
        else:thrown(lambda:s.NativeMountVerifier().verify(401,'/injected'))

def command_precall(mode):
    outcome=h.HostOutcome(c.TASK_ID,'exact_profile',now())
    def call(argv,stdin,timeout):
        need(len(outcome.commands)==1);row=outcome.commands[0]
        need(row['argv']==list(argv) and row['stdin_sha256']==sha(b'x') and row['launch_state']=='unknown' and row['started_at_UTC'])
        if mode=='generic':raise OSError('precall generic')
        return result(argv,stdin,timeout,'ok')
    adapter=h.DockerHostAdapter(SimpleNamespace(run=call),SOURCE,{})
    if mode=='generic':thrown(lambda:adapter._run(outcome,('injected',),b'x'));need(outcome.commands[0]['terminal_observed'] is None)
    else:adapter._run(outcome,('injected',),b'x')
    return outcome.as_dict()

def optional_native_chain():
    fake=FakeOS();fake.blocks=[b'123',b''];fake.faults['close']=OSError('native optional close uncertainty')
    with patch.object(s,'os',fake),patch.object(s,'MAX_EVENT_BYTES',2):
        error=thrown(lambda:s.DescriptorCgroupTransport().read_text(handle(),'memory.peak'))
    need(error.code=='cgroup_read_too_large' and s._descriptor_uncertainty(error))
    g=Groups();p=Processes(g);read=g.read_text
    def injected(directory,name):
        if name=='memory.peak':raise error
        return read(directory,name)
    with patch.object(g,'read_text',side_effect=injected):out=s.GroupOomSupervisor(g,p).run(s.SupervisorRequest.fixed('exact_profile',CID))
    ho,_=host(inner=out.as_dict());OBS['optional_native_chain']={'adapter_error':s._exception_observation(error),'supervisor':out.as_dict(),'host':ho.as_dict()}
    need(not out.cleanup_complete and ho.status=='failed','native optional metric close uncertainty reached false complete host')

def register():
    for case in c.CASES:
        def good(case=case):
            out,g,p=supervisor(case);need(out.status=='inner_complete' and out.cleanup_complete,out.failure_code)
            steps=[x[0] for x in g.calls];disable=next(i for i,x in enumerate(g.calls) if x[:3]==('write',g.root,'cgroup.subtree_control') and x[3]=='-memory')
            move=next(i for i,x in enumerate(g.calls) if x==('move',g.root,7001));need(disable<move)
            ho,cmd=host(case,inner=out.as_dict());need(ho.status=='complete',ho.failures)
            return {'inner':out.as_dict(),'host':ho.as_dict()}
        add('integrated_'+case,good)
    for fault in ('wrong_root','mount','preexisting','profile','initial_membership','final_membership','migration','disable','remove','uid','capability','protected','not_reaped','not_closed','report'):
        def bad(fault=fault):
            out,g,p=supervisor(fault=fault);need(out.status!='inner_complete',fault);return out.as_dict()
        add('supervisor_refuses_'+fault,bad)
    for fault in ('stale_counter','missing_counter','auxiliary','manual','watchdog'):
        add('oom_refuses_'+fault,lambda fault=fault: (lambda out: (need(out.status!='inner_complete'),out.as_dict())[1])(supervisor('small_group_oom',fault)[0]))
    add('group_zero_no_allocation',lambda:need(supervisor('group_zero_refused','group0_stress')[0].status!='inner_complete'))
    def optional():
        out=supervisor(fault='optional_close_uncertainty')[0];OBS['optional_metric']=out.as_dict();need(not out.cleanup_complete,'optional metric must preserve descriptor uncertainty')
    add('optional_metric_preserves_close_uncertainty',optional)
    for path in ('','/','../docker/'+CID,'foreign/'+CID,'docker/'+CID+'/guard-worker','docker//'+CID):
        add('path_refusal_'+str(len(CASES)),lambda path=path:thrown(lambda:c.require_exact_cgroup_relative_path(CID,path)))
    for kind in ('enumerate_permission','enumerate_disappear','enumerate_other','enumerate_valid','child_fstat','child_fstat_close','io_read','io_decode','io_write','io_read_ok','io_write_ok','io_limit','remove_unowned','remove_closed','remove_wrong_parent','remove_parent_drift','remove_original_drift','remove_replacement','remove_populated','remove_rmdir','remove_success','remove_replacement_close','remove_success_close','create_normal','create_rollback','create_both','create_replacement','create_unknown_identity','relative_verify','relative_fstat','relative_transfer_close','root_refusal','close_no_retry','inherited_close'):
        add('descriptor_'+kind,lambda kind=kind:descriptor_control(kind))
    for mode in ('failure','interrupted'):add('posix_close_'+mode,lambda mode=mode:posix_close(mode))
    for secondary in (False,True):add('barrier_secondary_'+str(secondary),lambda secondary=secondary:barrier(secondary))
    for mode in ('launch','communication','timeout','utf8'):add('subprocess_'+mode,lambda mode=mode:subprocess_case(mode))
    for fault in ('nonce_missing','nonce_wrong','id_wrong','schema','startup','false_cleanup','kill','kill_typed','rm','rm_typed','kill_rm'):
        def badhost(fault=fault):
            out,cmd=host(fault=fault);need(out.status=='failed');need(out.ended_at_UTC is not None)
            if fault.startswith('nonce') or fault=='id_wrong':need(not set(cmd.calls)&{'cp','start','kill','rm'})
            if 'rm' in fault:need(not out.exact_container_removed)
            return out.as_dict()
        add('host_refuses_'+fault,badhost)
    def running():
        out,cmd=host(fault='missing_running');OBS['missing_running']=out.as_dict();need(out.status!='complete','missing State.Running cannot establish terminal state')
    add('host_requires_running_observation',running)
    for mode in ('drain','barrier','watchdog'):add('real_'+mode,lambda mode=mode:real_fixture(mode))
    for which in ('guard-worker','guard-supervisor'):
        for removed in (False,True):add('integrated_removal_'+which+'_'+str(removed),lambda which=which,removed=removed:integrated_removal(which,removed))
    for mode in ('profile','membership'):
        for failed in (False,True):add('readonly_'+mode+'_'+str(failed),lambda mode=mode,failed=failed:readonly_worker(mode,failed))
    for capability in (False,True):add('native_bootstrap_'+str(capability),lambda capability=capability:native_bootstrap(capability))
    for mode in ('good','group','memory','membership'):add('worker_readback_'+mode,lambda mode=mode:worker_readback(mode))
    for mode in ('good','system','magic','readonly','ambiguous'):add('native_mount_'+mode,lambda mode=mode:native_mount(mode))
    for mode in ('good','generic'):add('command_precall_'+mode,lambda mode=mode:command_precall(mode))
    add('optional_metric_native_to_host_chain',optional_native_chain)

def custody_audit():
    """Decode retained data only; never import producer tests or controllers."""
    hand=json.loads((REPO/'ledger/handoffs'/f'{TASK}.yaml').read_text())['handoff']; bindings=[]
    for i,row in enumerate(hand['source_bindings']):
        raw=(REPO/row['path']).read_bytes();ref='17b0160c21' if i==105 else '9f6125c2785520237089e88c8607ea413d98144d'
        result=subprocess.run(['git','show',ref+':'+row['path']],cwd=REPO,capture_output=True,timeout=30)
        bindings.append({'path':row['path'],'expected':row['sha256'],'actual':sha(raw),'matched':sha(raw)==row['sha256'],'commit':ref,'commit_matched':result.returncode==0 and result.stdout==raw})
    receipt=json.loads((REPO/PRODUCER/'check-receipt.json').read_text()); files={}; inventory=[]; payloads=[]
    def scan(obj,path):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if (k.endswith('_base64') or k.endswith('_b64') or k=='base64') and isinstance(v,str):
                    try:b=dec(v);payloads.append({'path':path+'/'+k,'bytes':len(b),'sha256':sha(b)})
                    except Exception as e:payloads.append({'path':path+'/'+k,'error':str(e)})
                elif isinstance(v,(dict,list)):scan(v,path+'/'+k)
        elif isinstance(obj,list):
            for i,v in enumerate(obj):scan(v,path+'/'+str(i))
    scan(receipt,'receipt')
    historical_payload_inventory=[]
    for binding in hand['source_bindings']:
        path=binding['path']
        if path.endswith('.json') and path!=PRODUCER+'/check-receipt.json':
            begin=len(payloads);scan(json.loads((REPO/path).read_text()),path)
            historical_payload_inventory.append({'path':path,'decoded_payloads':len(payloads)-begin})
    for row in receipt['retained_files']:
        b=dec(row['content_base64']);key=(row['attempt_directory'],row['relative_path']);files[key]=b
        inventory.append({k:v for k,v in row.items() if k!='content_base64'}|{'hash_matches':sha(b)==row['sha256'],'size_matches':len(b)==row['bytes']})
        if row['relative_path'].endswith('.json'):
            scan(json.loads(b),'retained/'+row['attempt_directory']+'/'+row['relative_path'])
    attempts=[]
    for a in receipt['attempts']:
        stdout=dec(a['raw_stdout_base64']);raw=json.loads(stdout);r=a['reservation'];ad=pathlib.Path(r['argv'][2]).parent
        if ad.name=='source':ad=ad.parent
        ad=str(ad); suite=raw.get('results',[]); jr=[json.loads(x) for x in dec(a.get('raw_journal_base64','')).splitlines()]
        starts=[x for x in jr if x.get('event')=='created'];ends=[x for x in jr if x.get('event')=='terminal_wait']
        sampled=set();missing_samples=[];sums=[]
        for sample in a['samples']:
            rows=sample.get('processes',[sample]);vals=[]
            for row in rows:
                sampled.add(row.get('pid'))
                if isinstance(row.get('rss_bytes'),int):vals.append(row['rss_bytes'])
                else:missing_samples.append(row)
            sums.append(sum(vals))
        expected={a['worker_pid']}|{x['pid'] for x in starts}
        source_comparison={name:sha(files[ad,'source/'+name])==value for name,value in r['source_sha256'].items()}
        records=[json.loads(b) for (directory,name),b in files.items() if directory==ad and name.startswith('outer-tool-')]
        original_attempt=json.loads(files[ad,'attempt.json'])
        attempt_base_matches=all(a.get(k)==v for k,v in original_attempt.items())
        descriptor_lifetimes=[];active_fds={};active_pids=set();max_active=0
        for row in jr:
            if row['event']=='created':active_pids.add(row['pid']);max_active=max(max_active,len(active_pids))
            if row['event']=='terminal_wait':active_pids.discard(row['pid'])
            if row['event']=='descriptor_created':active_fds[row['fd']]=row
            if row['event']=='descriptor_closed':
                created=active_fds.pop(row['fd'],None);descriptor_lifetimes.append({'created':created,'closed':row})
        unavailable_timing=[]
        for sample in a['samples']:
            for row in sample.get('processes',[]):
                if row.get('rss_bytes') is None:
                    terminal=next((e for e in ends if e['pid']==row['pid']),None)
                    unavailable_timing.append({'sample':sample,'terminal_journal':terminal,'sample_minus_terminal_journal_seconds':sample['monotonic']-terminal['monotonic_ns']/1e9 if terminal else None})
        attempts.append({'phase':a.get('phase','suite'),'directory':ad,'worker_pid':a['worker_pid'],'worker_exit_code':a['worker_exit_code'],'source_sha256':r['source_sha256'],'source_copies_match':source_comparison,'results':suite,'controls':len(suite),'passed':sum(x['passed'] for x in suite),'failed':[x for x in suite if not x['passed']], 'registry_count':raw.get('registered_case_count'),'registry_zero_executions':raw.get('test_cases_executed'), 'created':starts,'terminal':ends,'fixture_lifetimes_seconds':[ (next(x for x in ends if x['pid']==y['pid'])['monotonic_ns']-y['monotonic_ns'])/1e9 for y in starts], 'journal_case_starts':sum(x.get('event')=='case_start' for x in jr),'journal_case_results':sum(x.get('event')=='case_result' for x in jr),'journal_terminal_custody':[x for x in jr if x.get('event')=='case_custody_terminal'], 'sampled_pids':sorted(sampled),'unexpected_sampled_pids':sorted(sampled-expected),'unavailable_samples':missing_samples,'peak_sum_of_available_rss':max(sums),'declared_peak':a.get('peak_observed_aggregate_rss_bytes'),'outer_tool_responses':records,'stdout_matches_retained':stdout==files[ad,'stdout'],'stderr_matches_retained':dec(a['raw_stderr_base64'])==files[ad,'stderr'],'journal_matches_retained':not jr or dec(a['raw_journal_base64'])==files[ad,'case-fixture-journal.jsonl'],'suite_matches_raw':not suite or a.get('suite')==raw,'wall_seconds':a['wall_seconds'],'children_user_CPU_seconds':a['children_user_CPU_seconds'],'children_system_CPU_seconds':a['children_system_CPU_seconds'],'original_attempt_fields_match':attempt_base_matches,'descriptor_lifetimes':descriptor_lifetimes,'unclosed_fds':active_fds,'max_concurrent_fixtures':max_active,'unreaped_fixtures':sorted(active_pids),'unavailable_timing':unavailable_timing})
    d1=attempts[1]['directory'];d2=attempts[3]['directory']
    diff=''.join(difflib.unified_diff(files[d1,'source/tests.py'].decode().splitlines(True),files[d2,'source/tests.py'].decode().splitlines(True),fromfile='attempt1/tests.py',tofile='attempt2/tests.py'))
    # Compare registry function bodies as data and bind all test functions through AST.
    ast_inventory=[]
    tree=ast.parse((SOURCE/'tests.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
            text=ast.get_source_segment((SOURCE/'tests.py').read_text(),node)
            ast_inventory.append({'name':node.name,'line':node.lineno,'end_line':node.end_lineno,'sha256':sha(text.encode())})
    current_protocol=json.loads((REPO/PRODUCER/'protocol-binding.json').read_text());old_protocol=json.loads(files[d2,'source/protocol-binding.json'])
    metadata_delta={k:{'attempt2':old_protocol.get(k),'delivered':current_protocol.get(k)} for k in set(old_protocol)|set(current_protocol) if old_protocol.get(k)!=current_protocol.get(k)}
    return {'bindings':bindings,'retained_files':inventory,'decoded_payloads':payloads,'historical_payload_inventory':historical_payload_inventory,'attempts':attempts,'total_controls':sum(x['controls'] for x in attempts),'total_passed':sum(x['passed'] for x in attempts),'total_failed':sum(len(x['failed']) for x in attempts),'total_benign_starts':sum(len(x['created']) for x in attempts),'test_correction_diff':diff,'test_ast_inventory':ast_inventory,'delivered_protocol_delta_from_final_suite':metadata_delta,'historical_missing_outer_response_reconstructed':False}

def suite():
    load_modules();register();need(len(CASES)<=128);need(len(set(n for n,f in CASES))==len(CASES))
    audit=custody_audit();dump(JOURNAL.parent/'custody-audit.json',audit)
    results=[];started=time.monotonic();cpu=time.process_time()
    def alarm(*args):raise TimeoutError('fixed control exceeded ten seconds')
    signal.signal(signal.SIGALRM,alarm)
    for name,fn in CASES:
        note('case_start',case_id=name);t=time.monotonic();u=time.process_time();signal.setitimer(signal.ITIMER_REAL,10)
        row={'id':name,'started_at_UTC':now()}
        try:
            detail=fn();row.update(passed=True,detail=detail if isinstance(detail,(dict,list,str,int,float,bool,type(None))) else {'exception_observed':str(detail)})
        except BaseException as e:row.update(passed=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc())
        finally:signal.setitimer(signal.ITIMER_REAL,0)
        row.update(ended_at_UTC=now(),wall_seconds=time.monotonic()-t,cpu_seconds=time.process_time()-u);results.append(row);note('case_result',case_id=name,result=row)
        need(time.monotonic()-started<1800,'aggregate watchdog')
    report={'task_id':TASK,'fixed_controls':len(results),'passed':sum(x['passed'] for x in results),'results':results,'observations':OBS,'suite_wall_seconds':time.monotonic()-started,'suite_cpu_seconds':time.process_time()-cpu,'scientific_runs':0,'live_operations':0}
    dump(JOURNAL.parent/'suite.json',report);print(json.dumps({'controls':len(results),'passed':report['passed'],'failures':[x['id'] for x in results if not x['passed']]}),flush=True)
    return 0 if all(x['passed'] for x in results) else 2

def watch(attempt):
    r=json.loads((attempt/'reservation.json').read_text());started=now();began=time.monotonic();u=resource.getrusage(resource.RUSAGE_CHILDREN)
    lib=ctypes.CDLL('/usr/lib/libproc.dylib',use_errno=True);samples=[];p=None;primary=None;cleanup=[]
    def sample(pid):
        buffer=ctypes.create_string_buffer(96);ctypes.set_errno(0);n=lib.proc_pidinfo(pid,4,0,buffer,96);err=ctypes.get_errno()
        raw=buffer.raw[:max(0,n)];return {'pid':pid,'returned_bytes':n,'errno':err,'raw_base64':enc(raw),'rss_bytes':int.from_bytes(raw[8:16],sys.byteorder) if n==96 else None,'basis':'darwin_proc_pidinfo_PROC_PIDTASKINFO'}
    with open(attempt/'stdout','xb') as out,open(attempt/'stderr','xb') as err:
        try:
            p=subprocess.Popen(r['argv'],cwd=r['cwd'],stdout=out,stderr=err,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},start_new_session=True)
            dump(attempt/'launch.json',{'pid':p.pid,'at_UTC':now(),'argv':r['argv']})
            while p.poll() is None:
                journal_bytes=(attempt/'journal.jsonl').read_bytes() if (attempt/'journal.jsonl').exists() else b''
                # Only completed rows are admissible while the owner is appending.
                rows=[json.loads(x) for x in journal_bytes.split(b'\n')[:-1] if x]
                made={x['pid']:x for x in rows if x['event']=='fixture_created'};ended={x['pid'] for x in rows if x['event']=='fixture_terminal'}
                active=set(made)-ended;sample_rows=[sample(pid) for pid in [p.pid,*sorted(active)]]
                snap={'at_UTC':now(),'monotonic':time.monotonic(),'processes':sample_rows,'available_sum_rss':sum(x['rss_bytes'] or 0 for x in sample_rows),'complete':all(x['rss_bytes'] is not None for x in sample_rows)}
                samples.append(snap)
                with open(attempt/'samples.jsonl','a') as f:f.write(json.dumps(snap)+'\n')
                need(len(active)<=2,'fixture concurrency');need(len(made)<=r['benign_starts_reserved'],'fixture start bound')
                need(all((time.monotonic_ns()-made[pid]['monotonic_ns'])/1e9<=3 for pid in active),'fixture lifetime watchdog')
                need(snap['available_sum_rss']<=2*1024**3,'sampled RSS watchdog');need(time.monotonic()-began<1800,'checker watchdog')
                time.sleep(.05)
            p.wait()
        except BaseException as e:
            primary={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
        finally:
            if p is not None and p.poll() is None:
                try:p.kill();p.wait(timeout=5)
                except BaseException as e:cleanup.append({'type':type(e).__name__,'message':str(e)})
    raw_out=(attempt/'stdout').read_bytes();raw_err=(attempt/'stderr').read_bytes();v=resource.getrusage(resource.RUSAGE_CHILDREN)
    record={'reservation':r,'started_at_UTC':started,'ended_at_UTC':now(),'wall_seconds':time.monotonic()-began,'checker_pid':p.pid if p else None,'exit_code':p.returncode if p else None,'primary_error':primary,'cleanup_errors':cleanup,'raw_stdout_base64':enc(raw_out),'raw_stderr_base64':enc(raw_err),'samples':samples,'peak_available_rss_sum':max([x['available_sum_rss'] for x in samples] or [0]),'post_exit_sample':sample(p.pid) if p else None,'children_user_cpu':v.ru_utime-u.ru_utime,'children_system_cpu':v.ru_stime-u.ru_stime,'hard_memory_guard_claim':False}
    dump(attempt/'attempt.json',record);print(json.dumps({'attempt':str(attempt),'checker_exit':record['exit_code'],'primary_error':primary,'sample_count':len(samples)}),flush=True)
    return record['exit_code'] if not primary else 3

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--watch',type=pathlib.Path);parser.add_argument('--suite',action='store_true');parser.add_argument('--repo',type=pathlib.Path);parser.add_argument('--source',type=pathlib.Path);parser.add_argument('--journal',type=pathlib.Path);args=parser.parse_args()
    if args.watch:raise SystemExit(watch(args.watch))
    REPO=args.repo;SOURCE=args.source;JOURNAL=args.journal
    if args.suite:raise SystemExit(suite())
    raise SystemExit('explicit --watch or --suite required; no implicit execution')
