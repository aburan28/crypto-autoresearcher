#!/usr/bin/env python3
"""Finite independent expectations and actual native supervisor boundary controls.

Only fixed F23/r17 and abstract Z17/Z29 are executed. No retained scientific
source is imported or executed. Test outputs are write-once and kept in the
explicit control root. This is producer testing, not independent validation.
"""
import argparse
import copy
from datetime import datetime,timedelta,timezone
import hashlib
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from predicate import Group,Prepared,PRIMARY,CELLS,interval,literal_decode,words
from driver import HERE,SOURCES,RUNTIME_SOURCES,MEMBERS,FLAGS,canon,sha,strict,dump,now,open_logical
from check import validate

CONTROL_ROOT=None
REPO=None
EVIDENCE=[]

def record_tree(root):
    return {str(p.relative_to(root)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(root.rglob('*')) if p.is_file()}

def reseal(out):
    ex=strict(out/'export.json')
    for n in MEMBERS: ex['backend_record']['members'][n]=dict(bytes=(out/n).stat().st_size,sha256=sha(out/n))
    ex['files']=[dict(path=n,sha256=b['sha256'],bytes=b['bytes'],kind='raw') for n,b in sorted(ex['backend_record']['members'].items())]
    ex['runs'][0]['artifacts']=ex['files'];ex['host']['sha256']=sha(out/'process.json.gz')
    (out/'export.json').write_text(canon(ex)+'\n')
    raw=strict(out/'raw-result.json');raw['export_sha256']=sha(out/'export.json');raw['summary_sha256']=sha(out/'summary.json.gz')
    (out/'raw-result.json').write_text(canon(raw)+'\n')
    man=strict(out/'manifest.yaml');man['run']['exact_density']=dict(export_sha256=sha(out/'export.json'),raw_result_sha256=sha(out/'raw-result.json'))
    (out/'manifest.yaml').write_text(canon(man)+'\n')

class ExactDensityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=CONTROL_ROOT;cls.root.mkdir(parents=True,exist_ok=False)
        cls.fixture=cls.root/'fixture'
        # Bind actual fixed-control argv, source bytes, times and stdout/stderr.
        cls.before={n:(HERE/n).read_bytes() for n in SOURCES}
        argv=[sys.executable,'-B',str(HERE/'driver.py'),'fixtures','--out',str(cls.fixture),'--repo',str(REPO)]
        started=now()
        with (cls.root/'fixture.stdout.log').open('xb') as so,(cls.root/'fixture.stderr.log').open('xb') as se:
            p=subprocess.run(argv,stdout=so,stderr=se,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        EVIDENCE.append(dict(kind='fixed_public_fixture',argv=argv,started_at=started,finished_at=now(),returncode=p.returncode,files=record_tree(cls.root)))
        if p.returncode: raise AssertionError('fixture refused: '+(cls.root/'fixture.stderr.log').read_text())
        with open_logical(cls.fixture/'states.jsonl.gz') as f:cls.records=[json.loads(x) for x in f]

    def test_01_legal_words_independent_scalar_bins(self):
        # Each scalar k owns exactly the word floor(D*k/r). This expectation
        # uses all k, never the enumerator's ceil/interval formula.
        for r in (17,29):
            L=r.bit_length()+1;D=1<<L
            owned={D*k//r:k for k in range(r)}
            for V in range(D):
                k,ok=interval(r,L,V)
                self.assertEqual(ok,V in owned)
                if ok:self.assertEqual(k,owned[V])

    def test_02_native_against_full_scalar_filter(self):
        # Independent candidate set: scan every public scalar's dyadic word
        # and test its defined-bit disagreement count, no completion loops.
        with open_logical(self.fixture/'preparations.jsonl.gz') as f:prep=[json.loads(x) for x in f]
        for row in self.records:
            ci,s,V,mask,e,hd,cells=row;r=17;D=64;L=6
            for (t,cap),c in zip(CELLS,cells):
                candidates=[]
                if e<=cap:
                    candidates=[k for k in range(r) if (((D*k//r)^V)&~mask).bit_count()<=t]
                self.assertEqual(c[2],len(candidates))
                self.assertEqual(c[4],int(0 in candidates))
                self.assertEqual(c[5],len([k for k in candidates if k]))
                self.assertEqual(c[6],int(s in candidates))
        by={i:[r for r in self.records if r[0]==i] for i in range(4)}
        for row in by[1]:self.assertTrue(all(c[6]==1 for c in row[-1]))
        for row in by[2]:self.assertTrue(all(c[6]==0 for c in row[-1]))
        for row in by[3]:self.assertTrue(all(c[1]==c[5]==c[6]==0 for c in row[-1]))

    def test_03_erasures_caps_order_and_zero(self):
        for r in (17,29):
            L=r.bit_length()+1;D=1<<L
            for s in range(1,r):
                true=D*s//r
                for erase in ((),(0,),(0,1),(0,1,2),tuple(range(L))):
                    mask=sum(1<<(L-1-i) for i in erase)
                    bits=[None if i in erase else true>>(L-1-i)&1 for i in range(L)]
                    for t,cap in CELLS:
                        d=literal_decode(bits,r,t,cap,checks=lambda k,x:(k==s,x==s),strict_status='UNDEFINED' if erase else 'RECOVERED')
                        want=[] if len(erase)>cap else [k for k in range(r) if (((D*k//r)^true)&~mask).bit_count()<=t]
                        self.assertEqual(d['distinct_nonzero_candidates'],[k for k in want if k])
                        self.assertEqual(d['zero_candidate_checks'],int(0 in want))
                        self.assertEqual(d['recovered_scalars'],[s] if s in want else [])
                        if (t,cap)==(0,0) and erase:self.assertEqual(d['status'],'UNDEFINED')
        seq=list(words([None,0,1,None],1))
        self.assertEqual([(w['erasure_assignment'],w['flipped_indices']) for w in seq[:3]], [([0,0],[]),([0,0],[1]),([0,0],[2])])
        self.assertEqual(len(seq),len({w['value'] for w in seq}))

    def test_04_both_checks_and_conversion(self):
        r=17;L=6;a=5;b=7;x=3;s=b*x*pow(a,-1,r)%r
        V=(1<<L)*s//r;bits=[V>>(L-1-i)&1 for i in range(L)]
        calls=[]
        def checks(k,converted):calls.append((k,converted));return k==s,converted==x
        d=literal_decode(bits,r,2,2,a,b,checks,'RECOVERED')
        self.assertEqual(d['recovered_scalars'],[x]);self.assertEqual(len(calls),sum(w['legal'] for w in d['words']))
        for pair in ((True,False),(False,True),(False,False)):
            d=literal_decode(bits,r,2,2,a,b,lambda k,x:pair,'RECOVERED')
            self.assertEqual(d['recovered_scalars'],[])
        for a,b in ((0,1),(1,0),(17,1),(1,17)):
            with self.assertRaises(ValueError):literal_decode(bits,r,0,0,a,b,strict_status='RECOVERED')

    def test_05_predicate_exception_definitions(self):
        g=Group(dict(p=23,a=11,b=5,r=17));P=(5,22)
        self.assertTrue(g.member(P));self.assertIsNone(g.mul(17,P))
        self.assertEqual(len({g.mul(k,P) for k in range(17)}),17)
        p=Prepared(g.model,P)
        self.assertEqual(p.evaluate(None),dict(status='BIT',bit=0,reason=None,z=0,g=None,anchor=p.anchor,normalized=None))
        for q in ([-1,0],[23,0],[0,0]):
            with self.assertRaises(ValueError):p.evaluate(q)
        unsupported=Prepared(dict(p=23,a=11,b=5,r=23),P)
        self.assertEqual(unsupported.evaluate(None)['reason'],'DOMAIN_UNSUPPORTED')
        zero_y=Prepared(dict(p=7,a=1,b=0,r=3),[0,0]);self.assertEqual(zero_y.reason,'ZERO_BASE_Y')
        zero_anchor=Prepared(g.model,P,PRIMARY|dict(alpha=-1));self.assertEqual(zero_anchor.reason,'ZERO_ANCHOR')
        # Fixed F23 public orbit verifies Miller's doubling identity independently.
        for k in range(17):
            R=g.mul(k,P);W,m=g.addline(R,R)
            self.assertEqual(g.z(W),(2*g.z(R)+m)%23)
        for arm in (PRIMARY,dict(kind='wrong_root',id='root',alpha=0,beta=0,base_multiplier=1)):
            pp=Prepared(g.model,P,arm)
            vals=[pp.evaluate(g.mul(k,P)) for k in range(17)]
            self.assertTrue(all(q['status'] in ('BIT','UNDEFINED') for q in vals))

    def test_06_strict_boundary_mutations(self):
        import jsonschema
        schema=strict(REPO/'schemas/experiment-export.v1.json')
        jsonschema.Draft202012Validator(schema).validate(strict(self.fixture/'export.json'))
        self.assertEqual(validate(self.fixture,REPO)['status'],'complete_output_checked')
        mutations={
            'malformed_json':lambda o:(o/'raw-result.json').write_text('{'),
            'yaml_only_json':lambda o:(o/'raw-result.json').write_text('status: complete\n'),
            'yaml_only_manifest':lambda o:(o/'manifest.yaml').write_text('run:\n  status: completed\n'),
            'duplicate_json':lambda o:(o/'raw-result.json').write_text('{"status":1,"status":2}'),
            'missing_member':lambda o:(o/'summary.json.gz').unlink(),
            'hash_mismatch':lambda o:(o/'states.jsonl.gz').write_bytes((o/'states.jsonl.gz').read_bytes()+b'corruption'),
            'seal_mismatch':lambda o:self.edit(o/'raw-result.json',lambda q:q.update(export_sha256='0'*64)),
            'abnormal_termination':lambda o:self.edit(o/'process.json.gz',lambda q:q.update(returncode=-15,termination='signal')),
            'partial_flag':lambda o:self.edit(o/'partial.json',lambda q:q.update(status='incomplete')),
            'wrong_curve':lambda o:self.edit_lines(o/'states.jsonl.gz',lambda rows:rows[0].__setitem__(0,99)),
            'missing_state':lambda o:self.edit_lines(o/'states.jsonl.gz',lambda rows:rows.pop(0)),
            'missing_zero_checks':lambda o:self.edit_lines(o/'states.jsonl.gz',self.remove_zero),
            'zero_in_M':lambda o:self.edit_lines(o/'states.jsonl.gz',self.include_zero),
            'source_snapshot':lambda o:self.edit(o/'provenance.before.json.gz',lambda q:q['files']['predicate.py'].update(sha256='0'*64)),
        }
        for name,mutate in mutations.items():
            target=self.root/('mutation-'+name);shutil.copytree(self.fixture,target);mutate(target)
            # Resealed mutations challenge semantics rather than only a seal.
            if name in ('abnormal_termination','partial_flag','wrong_curve','missing_state','missing_zero_checks','zero_in_M','source_snapshot'):reseal(target)
            try:validate(target,REPO)
            except (ValueError,OSError,KeyError,IndexError,TypeError) as e:
                EVIDENCE.append(dict(kind='boundary_negative',mutation=name,refusal=str(e),files=record_tree(target)))
            else:self.fail('accepted known-false boundary: '+name)

    @staticmethod
    def edit(path,change):
        q=strict(path);change(q);data=(canon(q)+'\n').encode();path.write_bytes(gzip.compress(data,mtime=0) if str(path).endswith('.gz') else data)
    @staticmethod
    def edit_lines(path,change):
        with open_logical(path) as f:rows=[json.loads(x) for x in f]
        change(rows);data=''.join(canon(x)+'\n' for x in rows).encode();path.write_bytes(gzip.compress(data,mtime=0) if str(path).endswith('.gz') else data)
    @staticmethod
    def remove_zero(rows):
        for row in rows:
            for c in row[-1]:
                if c[4]:c[4]=0;return
        raise AssertionError('zero fixture absent')
    @staticmethod
    def include_zero(rows):
        for row in rows:
            for c in row[-1]:
                if c[4]:c[5]+=1;return
        raise AssertionError('zero fixture absent')

    def test_07_aa_order_and_chunking(self):
        # Independent serialization order control over fixed records only.
        rows=copy.deepcopy(self.records)
        baseline=''.join(canon(x)+'\n' for x in rows)
        reversed_input=list(reversed(rows));reversed_input.sort(key=lambda r:(r[0],r[1]))
        self.assertEqual(baseline,''.join(canon(x)+'\n' for x in reversed_input))
        self.assertEqual(hashlib.sha256(baseline.encode()).digest(),hashlib.sha256(b''.join(baseline.encode()[i:i+7] for i in range(0,len(baseline.encode()),7))).digest())

    def test_08_stored_form_readback(self):
        stored=self.root/'stored-forms';shutil.copytree(self.fixture,stored)
        for name in ('states.jsonl.gz','process.json.gz','provenance.before.json.gz','provenance.after.json.gz','preparations.jsonl.gz'):
            p=stored/name
            with gzip.open(str(p)+'.gz','wb') as f:f.write(p.read_bytes())
            p.unlink()
        self.assertEqual(validate(stored,REPO)['status'],'complete_output_checked')
        EVIDENCE.append(dict(kind='stored_gzip_readback',files=record_tree(stored)))
        pointer_root=self.root/'identity-pointer';shutil.copytree(self.fixture,pointer_root)
        p=pointer_root/'states.jsonl.gz';data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
        cache=self.root/'local-fixture-cache';cached=cache/'sha256'/digest[:2]/digest
        cached.parent.mkdir(parents=True);cached.write_bytes(data)
        pointer=dict(schema='crypto.autoresearch.blob_pointer.v1',sha256=digest,size=len(data),encoding='identity',content_sha256=digest,content_size=len(data),uri='file:///unused-format-fixture/'+digest)
        p.with_name(p.name+'.blob.json').write_text(canon(pointer)+'\n');p.unlink()
        prior=os.environ.get('CRYPTO_AR_BLOB_CACHE');os.environ['CRYPTO_AR_BLOB_CACHE']=str(cache)
        try:self.assertEqual(validate(pointer_root,REPO)['status'],'complete_output_checked')
        finally:
            if prior is None:os.environ.pop('CRYPTO_AR_BLOB_CACHE',None)
            else:os.environ['CRYPTO_AR_BLOB_CACHE']=prior
        EVIDENCE.append(dict(kind='precompressed_native_identity_pointer_cached_readback',network=False,files=record_tree(pointer_root)))

    def test_09_actual_native_completion_route(self):
        # Unchanged supervisor helper, actual child fixture output, real clocks,
        # fixed in-memory format facts. No admission or claim is simulated.
        sys.path.insert(0,str(REPO/'tools'));sys.path.insert(0,str(REPO))
        import experiment_execution as native
        context=self.root/'native-context';(context/'tools').mkdir(parents=True)
        shutil.copyfile(REPO/'tools/artifact_store.py',context/'tools/artifact_store.py')
        route=context/'native-route';route.mkdir()
        plan=dict(experiment_id='EXP-FIXTURE-000000',task_id='TASK-FIXTURE-000000',approved_by=None,fixture_only=True,frozen=True,source_sha256={**{'harness/classical_ecdlp_exact_density/'+n:sha(HERE/n) for n in SOURCES},**{n:sha(context/n) for n in RUNTIME_SOURCES}})
        trial=dict(id='fixed_public_format',run_id='RUN-FIXTURE-000000',parameters=dict(scope='fixed_public_format_only',modes=['fixtures']))
        plan_path=context/'format-plan.json'
        argv=[sys.executable,'-B',str(HERE/'driver.py'),'fixtures','--out',str(route),'--repo',str(context),'--trial-plan',str(plan_path),'--trial-id',trial['id']]
        checker=[sys.executable,'-B',str(HERE/'check.py'),'--out',str(route),'--repo',str(context)]
        plan['trials']=[trial];dump(plan_path,plan)
        plan_rel=plan_path.relative_to(context).as_posix();ph=sha(plan_path)
        authority=dict(commit=sha(HERE/'driver.py'),meaning='fixed format-test fact; no scientific admission or Git claim')
        env=dict(python=sys.version,platform=sys.platform,commit=authority['commit'],source_sha256=plan['source_sha256'],specification_sha256=ph,runtime_lock=None,runtime_lock_sha256=None)
        dump(route/'environment.json',env);(route/'command.txt').write_text(json.dumps(argv)+'\n')
        started=now()
        dump(route/'launch.json',dict(plan_sha256=ph,trial_id=trial['id'],run_id=trial['run_id'],started_at=started,authority=authority,argv=argv,check_argv=checker,supervisor_pid=os.getpid(),fixture_only=True))
        with (route/'stdout.log').open('xb') as so,(route/'stderr.log').open('xb') as se:
            child=subprocess.run(argv,stdout=so,stderr=se,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        finished=now();self.assertEqual(child.returncode,0,(route/'stderr.log').read_text())
        body=strict(route/'manifest.yaml')['run']
        original=(route/'manifest.yaml').read_bytes()
        result=native.complete_manifest(route,plan,plan_rel,ph,trial,authority,argv,checker,started,finished)
        self.assertEqual(result['action'],'unchanged');self.assertEqual((route/'manifest.yaml').read_bytes(),original)
        checked=subprocess.run(checker,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (route/'check.stdout.log').write_bytes(checked.stdout);(route/'check.stderr.log').write_bytes(checked.stderr)
        self.assertEqual(checked.returncode,0,checked.stderr.decode())
        EVIDENCE.append(dict(kind='actual_complete_manifest_route',started_at=started,finished_at=finished,child_argv=argv,child_returncode=child.returncode,checker_argv=checker,checker_returncode=checked.returncode,completion=result,files=record_tree(route)))
        for name,mutate in (
            ('wrong_run',lambda q:q.update(id='RUN-FIXTURE-111111')),
            ('wrong_commit',lambda q:q['code'].update(commit='0'*64)),
            ('wrong_command',lambda q:q['code'].update(command=['false'])),
            ('wrong_plan_hash',lambda q:q['inputs'].update(plan_sha256='0'*64)),
            ('wrong_environment',lambda q:q['environment'].update(commit='0'*64)),
            ('outside_clock',lambda q:q['timing'].update(started_at='2000-01-01T00:00:00+00:00')),
            ('typed_bool',lambda q:q.update(attack_claimed=0)),
        ):
            bad=copy.deepcopy(body);mutate(bad);(route/'manifest.yaml').write_text(canon({'run':bad})+'\n')
            with self.assertRaises(native.EnvelopeRefused) as caught:native.complete_manifest(route,plan,plan_rel,ph,trial,authority,argv,checker,started,finished)
            EVIDENCE.append(dict(kind='native_contradiction',mutation=name,refusal=str(caught.exception),manifest_sha256=sha(route/'manifest.yaml')))
        (route/'manifest.yaml').write_bytes(original)

    def test_10_native_abstract29_and_actual_failures(self):
        import driver
        driver.RUNTIME_REPO=REPO
        binary=self.fixture/'census.bin'
        for oracle in ('true_half','negated_half','undefined','invalid_table','terminated_before_input'):
            before=driver.snapshot(binary);argv=[str(binary)];started=now()
            labels=[-1 if oracle=='undefined' else 0 if k==0 else int(k>14)^(oracle=='negated_half') for k in range(29)]
            data=('29 6 4\n'+' '.join(map(str,labels))+'\n').encode()
            if oracle=='invalid_table':data=b'29 6 4\n'
            if oracle=='terminated_before_input':
                proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                proc.terminate();so,se=proc.communicate();rc=proc.returncode;data=b''
            else:
                result=subprocess.run(argv,input=data,capture_output=True);so,se,rc=result.stdout,result.stderr,result.returncode
            (self.root/(oracle+'.stdout.log')).write_bytes(so);(self.root/(oracle+'.stderr.log')).write_bytes(se)
            EVIDENCE.append(dict(kind='fixed_abstract29_or_native_refusal',oracle=oracle,argv=argv,stdin_base64=__import__('base64').b64encode(data).decode(),returncode=rc,signal=-rc if rc<0 else None,started_at=started,finished_at=now(),source_before=before,source_after=driver.snapshot(binary),stdout_sha256=hashlib.sha256(so).hexdigest(),stderr_sha256=hashlib.sha256(se).hexdigest()))
            if oracle=='invalid_table':self.assertEqual(rc,2);self.assertEqual(so,b'');continue
            if oracle=='terminated_before_input':self.assertEqual(rc,-15);continue
            self.assertEqual(rc,0)
            rows=[json.loads(line) for line in so.splitlines()];self.assertEqual(len(rows),28)
            for row in rows:
                ci,k,V,mask,e,hd,cells=row;self.assertEqual(ci,4)
                for (t,cap),c in zip(CELLS,cells):
                    want=[] if e>cap else [j for j in range(29) if (((64*j//29)^V)&~mask).bit_count()<=t]
                    self.assertEqual((c[2],c[4],c[5],c[6]),(len(want),int(0 in want),len([j for j in want if j]),int(k in want)))
        copied=self.root/'source-mutation';copied.mkdir()
        for name in SOURCES:shutil.copyfile(HERE/name,copied/name)
        with (copied/'predicate.py').open('a') as f:f.write('\n# deliberate fixed-control source mismatch\n')
        out=self.root/'actual-source-refusal'
        argv=[sys.executable,'-B',str(copied/'driver.py'),'fixtures','--out',str(out),'--repo',str(REPO)]
        started=now();result=subprocess.run(argv,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (self.root/'source-refusal.stdout.log').write_bytes(result.stdout);(self.root/'source-refusal.stderr.log').write_bytes(result.stderr)
        self.assertEqual(result.returncode,2);self.assertEqual(strict(out/'partial.json')['status'],'incomplete')
        self.assertEqual(strict(out/'raw-result.json')['metrics'],{'complete':False})
        self.assertEqual(strict(out/'export.json')['backend_record']['status'],'incomplete')
        self.assertNotIn('q',strict(out/'raw-result.json'))
        EVIDENCE.append(dict(kind='actual_source_mismatch_partial_export',argv=argv,started_at=started,finished_at=now(),returncode=result.returncode,files=record_tree(copied)|{'output/'+k:v for k,v in record_tree(out).items()}))

    @classmethod
    def tearDownClass(cls):
        for n,data in cls.before.items():
            if (HERE/n).read_bytes()!=data: raise AssertionError('fixed invocation source changed: '+n)
        dump(cls.root/'evidence.json',dict(scope='fixed_public_unit_and_format_controls_only',scientific_runs=0,events=EVIDENCE,final_files=record_tree(cls.root)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--control-root',required=True);p.add_argument('--repo',required=True);a,remaining=p.parse_known_args()
    CONTROL_ROOT=Path(a.control_root).resolve();REPO=Path(a.repo).resolve()
    unittest.main(argv=[sys.argv[0],*remaining])
