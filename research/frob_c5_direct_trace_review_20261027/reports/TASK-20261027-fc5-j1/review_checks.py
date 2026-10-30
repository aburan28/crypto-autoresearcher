#!/usr/bin/env python3
"""Source-informed bounded fixture replay; no Sage or scientific trials."""
import argparse, copy, hashlib, json, platform, subprocess, sys, tempfile
from pathlib import Path

P = argparse.ArgumentParser()
P.add_argument('--root', type=Path, required=True)
P.add_argument('--out', type=Path, required=True)
P.add_argument('--controls-only', action='store_true')
a = P.parse_args()
root, out = a.root.resolve(), a.out.resolve()
checker_rel = 'docs/reports/2026-10-25-frob-c5-direct-trace/recheck_direct_trace.py'
replay_rel = 'docs/reports/2026-10-25-frob-c5-direct-trace/replay.json'
prior_rel = 'docs/reports/2026-10-22-frob-c5-factor-kernels/c5-matrix-replay.json'
manifest_rel = 'research/frob_c5_direct_trace_review_20261027/inputs.json'
def digest(b): return hashlib.sha256(b).hexdigest()
def require(ok, msg):
    if not ok: raise RuntimeError(msg)
def emit(p, obj): p.write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
def load_checker():
    ns = {'__name__':'review_import', '__file__':str(root/checker_rel)}
    exec(compile((root/checker_rel).read_bytes(), str(root/checker_rel), 'exec'), ns)
    return ns

if a.controls_only:
    m = load_checker()
    entries = {r['cell']:r for r in json.loads((root/prior_rel).read_text())['cells']}
    q13 = entries['FROB-NOLATTICE-q13n5']
    results=[]
    def reject(name, fn, substring):
        try: fn()
        except Exception as exc:
            row={'name':name,'exception':type(exc).__name__,'message':str(exc),'expected_substring':substring,'passed':substring in str(exc)}
        else: row={'name':name,'passed':False,'error':'unexpected acceptance'}
        results.append(row)
        require(row['passed'], name)
    def changed(**kw):
        e=copy.deepcopy(q13); e.update(kw); return e
    mutant=copy.deepcopy(q13['frobenius_matrix']);mutant[1][1]=3
    reject('q13_entry_1_1_mutation',lambda:m['check_cell'](root, changed(frobenius_matrix=mutant)), 'direct trace differs from h(M)')
    reject('native_bad_hash',lambda:m['check_cell'](root,changed(archived_output_sha256='0'*64)), 'native output hash changed')
    reject('replay_parameter_change',lambda:m['check_cell'](root,changed(q=11)), 'source-bound replay parameters changed')
    reject('matrix_bad_shape',lambda:m['check_cell'](root,changed(frobenius_matrix=[[0]])), 'bad matrix shape')
    bad=copy.deepcopy(mutant);bad[1][1]=13
    reject('matrix_out_of_range',lambda:m['check_cell'](root,changed(frobenius_matrix=bad)), 'bad matrix entry')
    with tempfile.TemporaryDirectory(prefix='frob-c5-j1-controls-',dir='/var/tmp') as td:
        temp=Path(td); native=temp/m['RUN']/f"{q13['cell']}.out.json";native.parent.mkdir(parents=True)
        original=(root/m['RUN']/native.name).read_bytes()
        def fixture(data):
            native.write_bytes(data)
            e=changed(archived_output_sha256=digest(data))
            return m['check_cell'](temp,e)
        reject('rebound_hash_wrong_envelope',lambda:fixture(original.replace(b'RESULT_JSON_BEGIN',b'WRONG_BEGIN')), 'unexpected native output envelope')
        reject('rebound_hash_extra_line',lambda:fixture(b'noise\n'+original), 'unexpected native output envelope')
        obj=m['read_native'](root/m['RUN']/native.name)
        def encoded(o):return ('RESULT_JSON_BEGIN\n'+json.dumps(o)+'\nRESULT_JSON_END\n').encode()
        badobj=copy.deepcopy(obj);badobj['q']=11
        reject('rebound_hash_wrong_native_q',lambda:fixture(encoded(badobj)), 'native parameters changed')
        badobj=copy.deepcopy(obj);badobj['C5']['dim_ker_T']=3
        reject('rebound_hash_wrong_native_dimension',lambda:fixture(encoded(badobj)), 'direct trace dimension disagrees')
        badobj=copy.deepcopy(obj);badobj['C5']['T_equals_hM']=False
        accepted=fixture(encoded(badobj))
        results.append({'name':'historical_flag_is_metadata','passed':accepted['archived_T_equals_hM_flag'] is False,'note':'check_cell accepts false historical flag after deliberate hash rebinding; reports it without treating it as current proof'})
        rp=temp/m['REPLAY'];rp.parent.mkdir(parents=True);rp.write_bytes((root/prior_rel).read_bytes()+b' ')
        reject('top_level_prior_hash',lambda:m['run'](temp), 'source-bound replay hash changed')
    original_mat=q13['frobenius_matrix']
    square=m['mat_product'](original_mat,original_mat,13)
    alt=m['check_cell'](root,changed(frobenius_matrix=square))
    results.append({'name':'trace_does_not_authenticate_matrix','passed':square != original_mat and alt['direct_equals_h_of_source_bound_matrix'],'matrix_squared_rows':square,'note':'check_cell accepts M^2 because its five powers permute those of M; top-level replay digest prevents replacing the pinned matrix'})
    original_product=m['mat_product'];original_sum=m['mat_geometric_sum']
    def forbidden(*args,**kwargs):raise RuntimeError('matrix path accessed during direct construction')
    m['mat_product']=forbidden;m['mat_geometric_sum']=forbidden
    direct=m['direct_trace_matrix']([1,0,0,0,8,1],13)
    results.append({'name':'direct_path_matrix_helpers_unavailable','passed':direct[0]==[5,5,12,8,1] and all(not any(r) for r in direct[1:])})
    require(all(r['passed'] for r in results),'control failed')
    print(json.dumps({'optimize':sys.flags.optimize,'python':platform.python_version(),'controls':results},indent=2,sort_keys=True))
    sys.exit(0)

out.mkdir(parents=True,exist_ok=True)
inputs=json.loads((root/manifest_rel).read_text());rows=[]
for entry in inputs['inputs']:
    data=(root/entry['path']).read_bytes()
    blob=subprocess.run(['git','show',inputs['source_commit']+':'+entry['path']],cwd=root,capture_output=True,check=True).stdout
    row={**entry,'actual_bytes':len(data),'actual_sha256':digest(data),'producer_git_blob_sha256':digest(blob),'passed':len(data)==entry['bytes'] and digest(data)==entry['sha256'] and data==blob}
    rows.append(row);require(row['passed'],'input binding: '+entry['path'])
emit(out/'input_hashes.json',{'inputs':rows,'source_commit':inputs['source_commit'],'all_passed':True})
commands=[]
def command(name,argv,expected=0):
    r=subprocess.run(argv,cwd=root,capture_output=True,text=True)
    (out/(name+'.stdout.txt')).write_text(r.stdout);(out/(name+'.stderr.txt')).write_text(r.stderr)
    commands.append({'name':name,'argv':argv,'cwd':str(root),'exit_code':r.returncode,'expected_exit_code':expected})
    require(r.returncode==expected,name+' exit status');return r
for mode,flags in [('normal',[]),('optimized',['-O'])]:
    result=out/('replay-'+mode+'.json')
    command('replay-'+mode,[sys.executable,'-B',*flags,str(root/checker_rel),'--repo-root',str(root),'--output',str(result)])
    require(result.read_bytes()==(root/replay_rel).read_bytes(),'byte reproduction '+mode)
    command('controls-'+mode,[sys.executable,'-B',*flags,str(Path(__file__).resolve()),'--root',str(root),'--out',str(out),'--controls-only'])
command('prior-matrix-replay',[sys.executable,'-B',str(root/'docs/reports/2026-10-22-frob-c5-factor-kernels/recheck_matrix.py'),'--check'])
command('prior-matrix-optimized-refusal',[sys.executable,'-B','-O',str(root/'docs/reports/2026-10-22-frob-c5-factor-kernels/recheck_matrix.py'),'--check'],expected=1)
require('requires Python assertions' in (out/'prior-matrix-optimized-refusal.stderr.txt').read_text(),'prior -O reason')
prior=json.loads((root/prior_rel).read_text());run='experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/'
bindings={'source_sha256':'docs/reports/2026-10-22-frob-c5-factor-kernels/recheck_matrix.py','fixtures_sha256':run+'fixtures.json','specification_sha256':'experiments/EXP-FROB-91ee9c/specification.yaml','sage_core_sha256':run+'work/core.py','sage_lattice_sha256':run+'work/lattice.py','sage_driver_sha256':run+'implementation.py','archived_checker_sha256':run+'checker.py'}
bound=[]
for key,path in bindings.items():
    actual=digest((root/path).read_bytes());require(actual==prior[key],'prior source '+key);bound.append({'path':path,'sha256':actual,'matches_prior_receipt':True})
emit(out/'prior_source_bindings.json',bound)
ns=load_checker();native=[]
for cell in prior['cells']:
    path=root/ns['RUN']/(cell['cell']+'.out.json');obj=ns['read_native'](path)
    native.append({'path':str(path.relative_to(root)),'line_count':len(path.read_text().splitlines()),'top_level_keys':list(obj),'C5':obj['C5'],'cell':obj['cell'],'q':obj['q'],'n':obj['n'],'field_modulus':obj['field_modulus'],'matrix_key_present':any('matrix' in k.lower() for k in obj)})
emit(out/'native_envelopes.json',native)
emit(out/'commands.json',commands)
emit(out/'summary.json',{'python':platform.python_version(),'executable':sys.executable,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'inputs_count':len(rows),'replay_sha256':digest((root/replay_rel).read_bytes()),'ordinary_and_optimized_byte_exact':True,'controls_per_mode':13,'prior_replay_byte_exact':True,'prior_optimized_refused':True,'historical_custody_authenticated':False})
print('PASS: 14 input hashes/git blobs; two byte-exact direct replays; 13 controls per mode; prior replay exact and -O refusal; seven prior source hashes')
