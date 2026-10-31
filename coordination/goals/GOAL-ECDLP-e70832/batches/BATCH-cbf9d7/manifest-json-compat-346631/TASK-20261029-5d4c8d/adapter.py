#!/usr/bin/env python3
"""Representation-only bridge; never imports candidate/host mathematics or SDKs.

prepare verifies sealed storage and writes only a derived descriptor/JSON manifest.
materialize repeats verification and creates a fresh readonly complete view.
Neither action invokes driver.check or postrun. Original native bytes stay exact.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, importlib.util, json, math, os, re, shutil, stat, subprocess, sys, tarfile
import yaml

REL='coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7'
CONTROL=REL+'/manifest-json-compat-346631'
RUN='experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237'
VIEW=REL+'/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1'
SNAP=REL+'/archives/TASK-20261029-5635b4/snapshot-receipt.json'
AUTH='6ce9937047cb26279f61a128ecc45751dc135a78'
WITNESS='7898ed6b86985fa31955fa8f21bccdb4deee6cc389165071fbc89d274205de37'
IDENT={'experiment_id':'EXP-ECDLP-080f41','run_id':'RUN-ECDLP-939237'}

def need(test, message):
    if not test: raise ValueError(message)

def sha(data): return hashlib.sha256(data).hexdigest()
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def unique(pairs):
    d={}
    for k,v in pairs:
        need(k not in d,'duplicate JSON key');d[k]=v
    return d

def nonfinite(x):raise ValueError('nonfinite JSON scalar')
def finite(x):
    v=float(x);need(math.isfinite(v),'nonfinite JSON float');return v

def jload(data):return json.loads(data,object_pairs_hook=unique,parse_constant=nonfinite,parse_float=finite)
def read(path):return jload(Path(path).read_text())
def encoding(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()

def strict_equal(a,b):
    if type(a) is not type(b):return False
    if type(a) is dict:return set(a)==set(b) and all(strict_equal(a[k],b[k]) for k in a)
    if type(a) is list:return len(a)==len(b) and all(strict_equal(x,y) for x,y in zip(a,b))
    return a==b

def subset(a,b):
    need(type(a) is type(b),'strict subset type mismatch')
    if type(a) is dict:
        need(set(a)<=set(b),'missing witness key')
        for k in a:subset(a[k],b[k])
    elif type(a) is list:
        need(len(a)==len(b),'witness list length')
        for x,y in zip(a,b):subset(x,y)
    else:need(a==b,'witness scalar mismatch')

def strict_yaml(data):
    # Closed JSON-compatible YAML types; no aliases, duplicate keys or coercive
    # YAML1.1 yes/on/octal/timestamp/binary/custom tags are admitted.
    node=yaml.compose(data,Loader=yaml.SafeLoader);seen=set()
    def walk(n):
        need(n is not None and id(n) not in seen,'empty YAML or aliases/cycles');seen.add(id(n))
        tag=n.tag.rsplit(':',1)[-1]
        if isinstance(n,yaml.MappingNode):
            need(tag=='map','nonstandard YAML mapping');out={}
            for k,v in n.value:
                need(isinstance(k,yaml.ScalarNode) and k.tag=='tag:yaml.org,2002:str','nonstring YAML key')
                key=k.value;need(key not in out,'duplicate YAML key');out[key]=walk(v)
            return out
        if isinstance(n,yaml.SequenceNode):
            need(tag=='seq','nonstandard YAML sequence');return [walk(v) for v in n.value]
        need(isinstance(n,yaml.ScalarNode),'unsupported YAML node')
        if tag=='str':return n.value
        if tag=='null':need(n.value=='null','coercive YAML null');return None
        if tag=='bool':need(n.value in ('true','false'),'coercive YAML bool');return n.value=='true'
        if tag=='int':need(re.fullmatch(r'-?(0|[1-9][0-9]*)',n.value) is not None,'nondecimal YAML integer');return int(n.value)
        if tag=='float':return finite(n.value)
        raise ValueError('unsupported YAML scalar tag '+tag)
    result=walk(node);need(strict_equal(result,jload(encoding(result))),'full YAML/JSON type roundtrip');return result

def safe(base,rel):
    p=PurePosixPath(rel);need(type(rel) is str and str(p)==rel and not p.is_absolute() and '..' not in p.parts and rel not in ('','.','/'),'unsafe relative path')
    base=Path(base).resolve();current=base
    for part in p.parts:
        current=current/part;need(not current.is_symlink(),'symlink in path '+rel)
    need(current.resolve().is_relative_to(base),'path escape');return current

def git(repo,*args):return subprocess.check_output(['git',*args],cwd=repo)

def check_files(run, inventory):
    expected={x['path']:x for x in inventory['files']}
    need(len(expected)==51 and inventory['file_count']==51,'original inventory size')
    for rel,e in expected.items():
        p=safe(run,rel);need(p.is_file() and p.stat().st_size==e['bytes'] and digest(p)==e['sha256'],'native bytes mismatch '+rel)
    # Published storage wrappers remain outside the original native namespace.
    allowed=set(expected)|{'.artifacts.json','.gitignore','modal-evidence.tar.gz.blob.json'}
    actual=set()
    for p in run.rglob('*'):
        need(not p.is_symlink() and (p.is_dir() or p.is_file()),'unsafe source tree')
        if p.is_file():actual.add(p.relative_to(run).as_posix())
    need(actual==allowed,'unexpected/missing source files')
    return expected

def verify(repo):
    repo=Path(repo).resolve();run=repo/RUN;control=repo/CONTROL
    inventory=read(control/'original-native-files.json');facts=read(control/'source-evidence.json');pub=read(control/'native-publication-receipt.json');snapshot=read(repo/SNAP)
    files=check_files(run,inventory)
    native=strict_yaml((run/'manifest.yaml').read_text());receipt=read(run/'execution-receipt.json');raw=read(run/'raw-result.json');launch=read(run/'launch.json');environment=read(run/'environment.json')
    need(digest(run/'manifest.yaml')==facts['native_manifest_sha256'] and digest(run/'execution-receipt.json')==facts['native_receipt_sha256'] and digest(run/'raw-result.json')==facts['raw_result_sha256'],'native pinned metadata')
    need(receipt['status']=='invalid_output' and receipt['returncode']==0 and receipt['check_returncode']==1 and receipt['published'] is False and receipt['scientific_conclusion'] is None,'original checker failure/status')
    need(receipt['authority']['commit']==AUTH and strict_equal(receipt['authority'],launch['authority']) and environment['commit']==AUTH,'source authority')
    need(raw['experiment_id']==IDENT['experiment_id'] and raw['run_id']==IDENT['run_id'] and receipt['run_id']==IDENT['run_id'],'native identity')
    need('JSONDecodeError' in (run/'check.stderr.log').read_text(),'original checker error absent')
    for rel,hashed in receipt['artifact_sha256'].items():need(rel in files and files[rel]['sha256']==hashed,'receipt native artifact digest')
    completion=receipt['manifest_completion'];text=completion['driver_manifest_text'];need(sha(text.encode())==WITNESS==completion['driver_manifest_sha256'],'original driver witness digest')
    subset(jload(text),native);need(strict_equal(native,jload(encoding(native))),'full native type preservation')
    need(native['run']['id']==IDENT['run_id'] and native['run']['experiment_id']==IDENT['experiment_id'] and native['run']['status']=='completed' and native['run']['code']['commit']==AUTH,'completed native envelope facts')
    need(native['run']['inputs']['plan_sha256']==receipt['plan_sha256']==launch['plan_sha256'],'plan binding')
    planpath=native['run']['inputs']['trial_plan'];need(digest(safe(repo,planpath))==receipt['plan_sha256'] and sha(git(repo,'show',AUTH+':'+planpath))==receipt['plan_sha256'],'approved trial plan source')
    plan=read(repo/planpath);need(plan['approved_by']==native['run']['approved_by']=='DEC-20261029-fe55a2' and plan['execution_authorized'] is True and plan['frozen'] is True,'frozen approval')
    need(native['run']['code']['command']==(run/'command.txt').read_text().strip() and jload(native['run']['code']['command'])==launch['argv'] and jload(native['run']['code']['check_command'])==launch['check_argv'],'actual command binding')
    for rel,hashed in environment['source_sha256'].items():need(digest(safe(repo,rel))==hashed and sha(git(repo,'show',AUTH+':'+rel))==hashed,'executing source changed '+rel)
    need(digest(safe(repo,plan['specification']))==environment['specification_sha256']==plan['specification_sha256'] and sha(git(repo,'show',AUTH+':'+plan['specification']))==plan['specification_sha256'],'specification source')
    controller=read(run/'modal/controller-receipt.json');need(strict_equal(controller,raw['controller']),'duplicated controller differs')
    need(controller['status']=='complete' and controller['engine_returncode']==0 and controller['collection_complete'] is True and controller['uid1000_quiescent'] is True and controller['vm_creates']==1 and controller['engine_execs']==1 and controller['automatic_retry'] is False,'completion/quiescence counters')
    ack=controller['termination_ack'];need(ack==inventory['completed_worker_and_termination_ack'] and ack['acknowledged'] is True and ack['uid']==1000 and ack['provider_returncode']==137,'actual termination acknowledgement')
    for role,b in controller['plan']['inputs'].items():
        need(digest(safe(repo,b['path']))==b['sha256'] and sha(git(repo,'show',AUTH+':'+b['path']))==b['sha256'] and digest(run/'modal'/(role+'.json'))==b['sha256'],'static input/source pin '+role)
    for role in ('worker','host'):
        manifest=read(run/('modal/'+role+'_manifest.json'))
        for rel,hashed in manifest['files'].items():need(digest(safe(repo,rel))==hashed,'source manifest '+rel)
    for e in controller['files']:
        key='modal/collected/'+e['path'];need(key in files and files[key]['bytes']==e['size'] and files[key]['sha256']==e['sha256'],'collected seal entry')
    members=read(run/'modal-evidence-manifest.json')['files'];expected={x['path']:x for x in members}
    need(len(members)==len(expected)==39 and set(expected)=={p for p in files if p.startswith('modal/')},'member coverage')
    seen=set()
    with tarfile.open(run/'modal-evidence.tar.gz','r|gz') as archive:
        for member in archive:
            safe(run,member.name);need(member.isfile() and member.name in expected and member.name not in seen,'unsafe/missing/extra archive member');seen.add(member.name)
            e=expected[member.name];need(member.size==e['bytes']==files[member.name]['bytes'] and e['sha256']==files[member.name]['sha256'],'member metadata')
            h=hashlib.sha256();source=archive.extractfile(member)
            for b in iter(lambda:source.read(1<<20),b''):h.update(b)
            need(h.hexdigest()==e['sha256'],'archive content mismatch')
    need(seen==set(expected),'archive incomplete')
    archive=facts['archive_payload'];pointer=read(run/'modal-evidence.tar.gz.blob.json');modern=read(run/'.artifacts.json')
    need(pointer==snapshot['supported_legacy_identity_pointers'][RUN+'/modal-evidence.tar.gz'],'snapshot pointer mismatch')
    need(pointer['encoding']=='identity' and pointer['sha256']==pointer['content_sha256']==archive['sha256'] and pointer['size']==pointer['content_size']==archive['bytes'] and pointer['uri']=='s3://setec-astronomy-artifacts/store/sha256/'+archive['sha256'][:2]+'/'+archive['sha256'],'identity pointer payload')
    need(modern['files']['modal-evidence.tar.gz']=={'sha256':archive['sha256'],'bytes':archive['bytes']},'modern same-payload binding')
    need(pub['all_full_s3_gets_verified'] is True and pub['readbacks']==snapshot['actual_full_S3_readback_receipt']['readbacks'] and all(x['full_s3_get_verified'] is True and x['sha256']==archive['sha256'] and x['bytes']==archive['bytes'] for x in pub['readbacks']),'recorded actual full GET proof')
    need(strict_equal(inventory,snapshot['original_native_all_51_files']),'raw snapshot original inventory')
    source=snapshot['source_head']
    for logical,stored in snapshot['logical_to_stored_forms'].items():need(sha(git(repo,'show',source+':'+stored))==snapshot['archive_binding']['path_sha256'][logical] and digest(safe(repo,stored))==snapshot['archive_binding']['path_sha256'][logical],'actual stored Git snapshot '+logical)
    # Schema uses original path and unchanged checker. This is NOT driver.check.
    sys.path.insert(0,str(repo/'tools'));import validate_ledger as vl
    ctx=vl.Ctx(set());vl.check_run(str(run/'manifest.yaml'),ctx);need(not ctx.errors,'original native schema: '+str(ctx.errors))
    return native,files,{'schema_errors':ctx.errors,'native_file_count':51,'archive_member_count':39,'full_GET':'verified prior root receipt bound to immutable archive digest; no new network call','native_status':'invalid_output','native_checker_returncode':1,'original_driver_witness_sha256':WITNESS,'authority_commit':AUTH,'source_plan_protocol_pins_verified':True,'full_native_roundtrip_and_strict_original_subset':True,'ACK_and_quiescence_verified':True,'driver_check_invoked':False,'host_math_or_labels_or_entropy_or_new_science_invoked':False}

def fixtures():
    base={'x':True,'n':None,'f':1.0,'a':[1,'1']};need(strict_equal(base,jload(encoding(base))),'fixed roundtrip fixture')
    cases=[('bool-int',lambda:subset({'x':True},{'x':1})),('float-int',lambda:subset({'x':1.0},{'x':1})),('null-string',lambda:subset({'x':None},{'x':'null'})),('missing-added',lambda:need(strict_equal({'x':1,'added':2},{'x':1}),'full-tree omission')),('duplicate-json',lambda:jload('{"x":1,"x":2}')),('nonfinite-json',lambda:jload('{"x":NaN}')),('duplicate-yaml',lambda:strict_yaml('x: 1\nx: 2\n')),('coercive-bool-yaml',lambda:strict_yaml('x: yes\n')),('timestamp-yaml',lambda:strict_yaml('x: 2026-10-29\n')),('alias-yaml',lambda:strict_yaml('x: &a [1]\ny: *a\n')),('nonfinite-yaml',lambda:strict_yaml('x: .inf\n')),('nonstring-key',lambda:strict_yaml('1: x\n'))]
    rejected=[]
    for name,fn in cases:
        try:fn()
        except ValueError:rejected.append(name)
        else:raise ValueError('mutant accepted '+name)
    return {'fixed_roundtrip':'pass','refused_mutants':rejected,'new_science':0}

def write_new(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(data)

def build(repo, destination, materialize):
    native,files,checks=verify(repo);repo=Path(repo).resolve();destination=Path(destination).absolute();need(not destination.exists(),'fresh destination required')
    need(not any(p.is_symlink() for p in [destination,*destination.parents]),'symlink in destination path');destination.mkdir(parents=True)
    view=destination/'supervisor';view.mkdir();manifest=encoding(native);mapping=[];run=repo/RUN
    for rel,e in files.items():
        source=safe(run,rel);mode=stat.S_IMODE(source.stat().st_mode);method='json_full_native' if rel=='manifest.yaml' else ('readonly_hardlink' if mode&0o222==0 else 'private_copy')
        out=view/rel;actual='descriptor_only'
        if rel=='manifest.yaml':write_new(out,manifest);out.chmod(0o444);actual='json_full_native'
        elif materialize:
            out.parent.mkdir(parents=True,exist_ok=True)
            if method=='readonly_hardlink':os.link(source,out);actual=method
            else:
                with source.open('rb') as src,out.open('xb') as dst:shutil.copyfileobj(src,dst,1<<20)
                out.chmod(0o444);actual=method
            need(out.stat().st_size==e['bytes'] and digest(out)==e['sha256'],'materialized bytes mismatch')
            need(stat.S_IMODE(source.stat().st_mode)==mode,'source chmod changed')
        stored=RUN+'/'+rel if not rel.startswith('modal/') else RUN+'/modal-evidence.tar.gz.blob.json#'+rel
        if rel=='modal-evidence.tar.gz':stored=RUN+'/modal-evidence.tar.gz.blob.json'
        mapping.append({'path':rel,'source_logical_path':RUN+'/'+rel,'source_payload_sha256':e['sha256'],'source_bytes':e['bytes'],'published_stored_form':stored,'view_sha256':sha(manifest) if rel=='manifest.yaml' else e['sha256'],'view_bytes':len(manifest) if rel=='manifest.yaml' else e['bytes'],'source_mode_octal':oct(mode),'materialization_method':actual,'planned_materialization_method':method})
    if materialize:
        for p in sorted(view.rglob('*'),key=lambda p:len(p.parts),reverse=True):
            if p.is_dir():p.chmod(0o555)
        view.chmod(0o555)
        # Original verification after materialization includes exact51/source modes.
        check_files(run,read(repo/(CONTROL+'/original-native-files.json')))
    provenance={'schema':'classical.ecdlp.readonly-fullnative-json-view/v1','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'materialized':materialize,'view_root':VIEW+'/supervisor','original_run':RUN,'native_status_unchanged':'invalid_output/check1/publishedfalse','sole_byte_delta':'manifest.yaml full native YAML encoded as JSON with type-strict fulltree equality','original_witness_sha256':WITNESS,'original_manifest_sha256':files['manifest.yaml']['sha256'],'derived_manifest_sha256':sha(manifest),'raw_snapshot_receipt':SNAP,'raw_snapshot_receipt_sha256':digest(repo/SNAP),'bridge_contract_sha256':digest(repo/(CONTROL+'/bridge-contract.json')),'source_evidence_sha256':digest(repo/(CONTROL+'/source-evidence.json')),'producer_adapter_sha256':digest(Path(__file__)),'checks':checks,'file_mapping':mapping,'storage_bindings':{'logical_to_stored_forms':read(repo/SNAP)['logical_to_stored_forms'],'stored_form_sha256':read(repo/SNAP)['archive_binding']['path_sha256'],'archive_payload':read(repo/(CONTROL+'/source-evidence.json'))['archive_payload'],'publication_receipt_sha256':digest(repo/(CONTROL+'/native-publication-receipt.json'))},'reconstruction':'Run committed adapter materialize with --repo-root and fresh --destination; hydrate immutable native tar and all39 modal members by original inventory first. No SDK or network used by adapter.','independent_bridge_validation':'pending TASK-20261029-3b5feb; no host work authorized by this record'}
    write_new(destination/'view-provenance.json',encoding(provenance));write_new(destination/'.gitignore',b'/supervisor/*\n!/supervisor/manifest.yaml\n')
    return checks,provenance

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['fixtures','prepare','materialize']);p.add_argument('--repo-root',type=Path);p.add_argument('--destination',type=Path);a=p.parse_args()
    if a.action=='fixtures':result=fixtures()
    else:
        need(a.repo_root is not None and a.destination is not None,'repo and destination required');result,_=build(a.repo_root,a.destination,a.action=='materialize')
    print(json.dumps(result,sort_keys=True,allow_nan=False));return 0
if __name__=='__main__':raise SystemExit(main())
