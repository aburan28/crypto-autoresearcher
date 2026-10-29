"""ONLY disclosed F11/F23 fixtures and deterministic negative mutations."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import verify as v
import reference as ref

FIXTURES=(('F11',{'p':11,'a':1,'b':6,'r':13},[2,7]),
          ('F23',{'p':23,'a':11,'b':5,'r':17},[5,22]))


def custody(root):
    rows=[]
    for name in v.FILES:
        data=(root/name).read_bytes()
        rows.append({'path':name,'sha256':v.digest(data),'size':len(data)})
    return {'schema':v.PREFIX+'host-custody/v1','sealed':True,
        'collection_complete':True,'uid1000_quiescent':True,
        'termination_ack':{'acknowledged':True,'uid':1000,'transport_id':'fixture-only-no-worker'},
        'files':rows,'tree_sha256':v.tree_digest(rows)}


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        for name in v.FILES:
            (self.root/name).write_bytes(b'{}\n')
        self.evidence=custody(self.root)
        self.seal=v.open_sealed(self.root,self.evidence)

    def tearDown(self): self.tmp.cleanup()

    def test_custody_rejects_before_oracle(self):
        for key in ('sealed','collection_complete','uid1000_quiescent','termination_ack'):
            mutant=copy.deepcopy(self.evidence)
            mutant.pop(key)
            with self.assertRaises(ValueError),patch.object(v.Group,'orbit',side_effect=AssertionError('early orbit')):
                v.open_sealed(self.root,mutant)
        mutant=copy.deepcopy(self.evidence)
        mutant['tree_sha256']='0'*64
        with self.assertRaises(ValueError): v.open_sealed(self.root,mutant)
        (self.root/v.FILES[0]).write_text('tampered')
        with self.assertRaises(ValueError): v.open_sealed(self.root,self.evidence)
        for _,model,P in FIXTURES:
            with self.assertRaises(ValueError): v.Oracle(None,model,P)

    def test_custody_extras_symlinks_and_duplicate_paths(self):
        (self.root/'extra').write_text('x')
        with self.assertRaises(ValueError): v.open_sealed(self.root,self.evidence)
        (self.root/'extra').unlink()
        mutant=copy.deepcopy(self.evidence)
        mutant['files'].append(mutant['files'][0])
        with self.assertRaises(ValueError): v.open_sealed(self.root,mutant)
        data=(self.root/v.FILES[0]).read_bytes()
        (self.root/v.FILES[0]).unlink()
        outside=self.root.parent/(self.root.name+'-fixture')
        try:
            outside.write_bytes(data)
            (self.root/v.FILES[0]).symlink_to(outside)
            with self.assertRaises(ValueError): v.open_sealed(self.root,self.evidence)
        finally: outside.unlink()

    def test_arithmetic_primitive_and_covariance(self):
        for name,model,P in FIXTURES:
            o=v.Oracle(self.seal,model,P)
            o.slope_sum_check()
            g=o.group
            for R in o.points:
                self.assertEqual(o.z[g.neg(R)],-o.z[R]%g.p)
                for S in o.points:
                    self.assertEqual(o.z[g.add(R,S)],(o.z[R]+o.z[S]+g.slope(R,S))%g.p)
            u=2
            transformed={'p':g.p,'r':g.r,'a':g.a*u**4%g.p,'b':g.b*u**6%g.p}
            Phi=lambda R:None if R is None else (R[0]*u*u%g.p,R[1]*u*u*u%g.p)
            other=v.Oracle(self.seal,transformed,Phi(tuple(P)))
            for R in o.points:
                self.assertEqual(other.z[Phi(R)],u*o.z[R]%g.p)
                for alpha,beta in ((1,-4),(-2,-1)):
                    left=o.evaluate(R,alpha,beta,1)
                    right=other.evaluate(Phi(R),alpha,beta,1)
                    self.assertEqual(left['bit'],right['bit'])
                    if 'normalized' in left:self.assertEqual(left['normalized'],right['normalized'])
            if name=='F11':
                self.assertEqual(o.z[tuple(P)],3)
                self.assertEqual(o.z[(5,2)],3)
                self.assertEqual(o.evaluate((5,2),1,-4,1)['normalized'],9)
                # Correct beta unchanged: wrong beta scaling changes normalized value.
                wrong=other.evaluate(Phi((5,2)),1,-4*u*u,1)
                self.assertNotEqual(wrong['normalized'],9)
            print(json.dumps({'fixture':name,'assertion':'all cocycle pairs/slope sums/covariance',
                              'host_counts':dict(g.counts)},sort_keys=True))

    def test_perfect_half_all_disclosed_scalars(self):
        for name,model,P in FIXTURES:
            o=v.Oracle(self.seal,model,P)
            g=o.group
            L=g.r.bit_length()+1
            retained={'complete':0,'capped':0,'empty_intervals':0,'zero_checked':0}
            for x in range(1,g.r):
                Q=o.points[x]
                for a,b in ((1,1),(2,3),(3,2)):
                    s=x*b*pow(a,-1,g.r)%g.r
                    truth=[int(s*pow(2,i,g.r)%g.r>g.r//2) for i in range(L)]
                    self.assertEqual(v.interval(g.r,L,sum(t<<(L-i-1) for i,t in enumerate(truth))),s)
                    for radius,cap in v.CELLS:
                        bits=list(truth)
                        if cap==2: bits[0]=None
                        if radius: bits[1]^=1
                        result=v.decode(g,tuple(P),Q,a,b,bits,radius,cap)
                        self.assertEqual(set(result['verified']),{x})
                        self.assertEqual(len(result['words']),len(set(row['word'] for row in result['words'])))
                        self.assertEqual(result['M'],len(set(z for z in result['legal'] if z)))
                        geom=v.geometry(o,Q,a,b,bits)
                        self.assertLessEqual(len(geom['errors']),radius)
                        self.assertLessEqual(len(geom['erasures']),cap)
                        retained['complete']+=1
                        retained['empty_intervals']+=result['host_counts'].get('empty_interval',0)
                        retained['zero_checked']+=result['zero_checked']
                    capped=v.decode(g,tuple(P),Q,a,b,[None]*L,2,2)
                    self.assertEqual(capped['status'],'capped')
                    retained['capped']+=1
            zero=v.decode(g,tuple(P),tuple(P),1,1,[0]*L,0,0)
            self.assertEqual(zero['zero_checked'],1)
            self.assertEqual(zero['M'],0)
            self.assertEqual(zero['verified'],[])
            print(json.dumps({'fixture':name,'perfect_half_retained':retained},sort_keys=True))

    def test_mutants_list_interval_sign_conversion_order_erasure(self):
        for name,model,P in FIXTURES:
            o=v.Oracle(self.seal,model,P)
            g=o.group
            L=g.r.bit_length()+1
            Q=o.points[3]
            bits=v.geometry(o,Q,2,3,[0]*L)['truth']
            expected=v.decode(g,tuple(P),Q,2,3,bits,1,2)
            self.assertIn(3,expected['verified'])
            for field,changed in (('words',expected['words'][:-1]),('M',expected['M']+1),
                ('zero_checked',expected['zero_checked']+1),('verified',[g.r-3]),
                ('legal',list(reversed(expected['legal'])))):
                mutant=copy.deepcopy(expected)
                mutant[field]=changed
                if mutant==expected:continue
                with self.assertRaises(ValueError):v.check_cell(g,tuple(P),Q,2,3,bits,mutant)
            mutant=copy.deepcopy(expected)
            mutant['words'][0]['x']=(mutant['words'][0].get('x',0)+1)%g.r
            with self.assertRaises(ValueError):v.check_cell(g,tuple(P),Q,2,3,bits,mutant)
            # This rejects dropping erasures rather than querying complete L.
            erased=bits.copy();erased[0]=None
            with self.assertRaises(ValueError):v.check_cell(g,tuple(P),Q,2,3,erased,expected)
            # Boundary V=0 has k=0; k=1 is NOT inside the strict upper endpoint.
            self.assertEqual(v.interval(g.r,L,0),0)
            self.assertIsNone(v.interval(g.r,L,(1<<L)-1))
            # Wrong sign bits or a/b scale cannot certify the true word under radius0.
            wrong=v.decode(g,tuple(P),Q,2,3,[1-t for t in bits],0,0)
            self.assertEqual(wrong['verified'],[])
            with self.assertRaises(ValueError):v.exact_ids([{'id':'x'},{'id':'x'}],'id',['x'])
            with self.assertRaises(ValueError):v.validate_counter_vector({'bad':-1})
            print(json.dumps({'fixture':name,'negative_mutants':'truncation M zero sign conversion order erasure endpoint IDs counters rejected'}))

    def test_empty_interval_and_synthetic_zero_base_Z_metadata(self):
        _,model,P=FIXTURES[0]
        o=v.Oracle(self.seal,model,P)
        arm=v.ARMS['circuit1.a3']
        R=tuple(P);queries=[]
        for i in range(5):
            queries.append({'index':i,'target':list(R),'answer':v.engine_answer(o,R,arm),'counters':{}})
            R=o.group.add(R,R)
        self.assertEqual([q['answer']['bit'] for q in queries],[1,0,1,0,0])
        proc={'L':5,'predicate_evaluations':5,'predicate_trace':queries,
            'candidate_scalar_prime':9,'candidate_scalar':None,'scalar_prime':None,'scalar':None,
            'interval':{'denominator':32,'lower_numerator':260,'upper_numerator':273,'value':20,'nonempty':False},
            'public_checks':{'original':None,'transformed':None},'target_multiplier_inverse':1,
            'status':'EMPTY_INTERVAL','reason':'EMPTY_BINARY_INTERVAL','retained_bit_reads':0,'counts':{}}
        row={'base_multiplier':3,'target_multiplier':1,'target':P,'original':proc,'incremental':None}
        v.check_engine_trace(o,arm,row)
        proc['reason']='wrong reason'
        with self.assertRaises(ValueError):v.check_engine_trace(o,arm,row)
        proc['reason']='EMPTY_BINARY_INTERVAL'
        proc['candidate_scalar']=1
        with self.assertRaises(ValueError):v.check_engine_trace(o,arm,row)
        # Synthetic implementation-branch control only: disclosed real fixture has
        # no nonidentity Z-zero. Inject zero in independent host table, never worker.
        base=o.group.mul(3,o.base)
        o.z[base]=0
        got=v.engine_answer(o,tuple(P),arm)
        self.assertEqual(got,{'status':'UNDEFINED','bit':None,'reason':'ZERO_BASE_Z',
            'anchor':None,'z':None,'g':None,'normalized':None})

    def test_published_data_only_F11_records_and_bundle(self):
        path=Path(os.environ.get('VERIFIER_ENGINE_INTERFACE',str(Path(__file__).resolve().parents[1]/'engine-interface.json')))
        if not path.is_file():self.skipTest('published data-only engine interface unavailable')
        interface=json.loads(path.read_bytes())
        sample=interface['embedded_deterministic_F11_records']
        o=v.Oracle(self.seal,sample['setup']['model'],sample['setup']['base'])
        bits,geom=v.check_engine_trace(o,sample['setup']['arm'],sample['trace'])
        v.check_engine_cell(o,sample['trace'],bits,sample['decoder-cell'])
        self.assertEqual(geom['s'],4)
        for label in ('list','scale','upper','counter','query'):
            trace=copy.deepcopy(sample['trace'])
            cell=copy.deepcopy(sample['decoder-cell'])
            if label=='list':cell['words'].pop()
            if label=='scale':cell['words'][0]['candidate_scalar']=6
            if label=='upper':trace['original']['interval']['upper_numerator']-=1
            if label=='counter':trace['original']['predicate_trace'][0]['counters']['bad']=-1
            if label=='query':trace['original']['predicate_trace'][0]['target']=[2,7]
            with self.assertRaises(ValueError):
                b,_=v.check_engine_trace(o,sample['setup']['arm'],trace)
                v.check_engine_cell(o,trace,b,cell)
        # Complete calibration bundle uses original only, no extra paired arm.
        trace=copy.deepcopy(sample['trace']);trace['incremental']=None;trace['equal']=None
        summary=copy.deepcopy(sample['summary'])
        expected={'cells':0,'intents':1,'setups':1,'singles':1,'traces':1}
        summary['expected']=summary['observed']=expected
        values={'setups.jsonl':[sample['setup']], 'single-points.jsonl':[sample['single-point']],
            'attempt-intents.jsonl':[sample['intent']], 'traces.jsonl':[trace], 'decoder-cells.jsonl':[]}
        for name,rows in values.items():
            (self.root/name).write_bytes(b''.join(v.canonical(row)+b'\n' for row in rows))
        (self.root/'engine-summary.json').write_bytes(v.canonical(summary))
        cohort_raw=v.canonical({'nonce':'0'*64,'curves':[{'curve_id':'fixture-F11','model':sample['setup']['model'],
            'base':sample['setup']['base'],'targets':[{'target_id':'target7','point':[7,2]}]}]})
        summary['provenance']['cohort_sha256']=v.digest(cohort_raw)
        (self.root/'engine-summary.json').write_bytes(v.canonical(summary))
        completion=copy.deepcopy(sample['completion'])
        completion['provenance']['cohort_sha256']=v.digest(cohort_raw)
        for name in set(v.FILES)-{'engine-completion.json'}:
            raw=(self.root/name).read_bytes()
            completion['files'][name]={'sha256':v.digest(raw),'bytes':len(raw),
                'records':len(values[name]) if name in values else 1}
        (self.root/'engine-completion.json').write_bytes(v.canonical(completion))
        evidence=custody(self.root)
        plan={'public_cohort_bytes_hex':cohort_raw.hex(),'engine_interface_canonical_sha256':v.digest(v.canonical(interface)),
            'provenance':completion['provenance'],'setup_ids':['fixture-F11/circuit1.a5'],
            'single_ids':[sample['single-point']['single_id']],
            'trace_ids':[trace['trace_id']],'paired_trace_ids':[],'expected':expected}
        checked=v.verify_bundle(self.root,evidence,plan,interface)
        self.assertEqual(checked['observed'],expected)
        altered=copy.deepcopy(plan);altered['public_cohort_bytes_hex']=v.canonical({'curves':[]}).hex()
        with self.assertRaises(ValueError):v.verify_bundle(self.root,evidence,altered,interface)
        broken=copy.deepcopy(plan);broken['paired_trace_ids']=[trace['trace_id']]
        with self.assertRaises(ValueError):v.verify_bundle(self.root,evidence,broken,interface)
        print(json.dumps({'fixture':'F11','published_data_only_sample':'trace+cell pass; five mutants rejected; complete original-only bundle passes; paired schedule mutant rejected'}))

    def test_references_saturation_null_and_bsgs(self):
        for name,model,P in FIXTURES:
            o=v.Oracle(self.seal,model,P)
            g=o.group
            bsgs=ref.BSGS(self.seal,g,tuple(P))
            first=bsgs.solve(o.points[3]);again=bsgs.solve(o.points[3])
            self.assertEqual(first['online_primitive_vector'],again['online_primitive_vector'])
            for x,Q in enumerate(o.points):self.assertEqual(bsgs.solve(Q)['scalar'],x)
            for M in (0,1,g.r-1,g.r+7):
                ans=ref.uniform_list(self.seal,g,tuple(P),o.points[3],M,b'\0'*32)
                self.assertEqual(len(ans['guesses']),min(M,g.r-1))
                self.assertEqual(len(set(ans['guesses'])),len(ans['guesses']))
                self.assertNotIn(0,ans['guesses'])
                if M>=g.r-1:self.assertTrue(ans['success'])
            mask={R:True for R in o.points}
            mask[o.points[2]]=mask[o.points[-2]]=False
            out=ref.mask_reference(self.seal,o,mask,b'\1'*32)
            self.assertEqual(out['support']['exact_small'],2**((g.r-1)//2-2))
            self.assertEqual(out['draw_count'],1023)
            self.assertEqual(out['unique_draws']+out['duplicate_draws'],1023)
            for index in range(out['draw_count']):
                labels=ref.unpack_labels(out,index)
                self.assertEqual(labels[1],0);self.assertEqual(labels[-1],1)
                self.assertIsNone(labels[2]);self.assertIsNone(labels[-2])
                for k in range(1,g.r):
                    if labels[k] is not None:self.assertEqual(labels[k],1-labels[-k])
                chart=ref.chart_view(o,labels,2)
                self.assertEqual(len(chart),g.r)
            stats=ref.retained_bank_statistics(self.seal,o,out,[1,1,2,3],[1,1,3],{'score_sum':0,'q0_successes':0})
            self.assertEqual(stats['bank_duplicates'],1)
            self.assertEqual(stats['start_duplicates'],1)
            self.assertEqual(len(stats['reference_statistics']),1023)
            self.assertEqual(sum(stats['ties']['q0'][k] for k in ('less','equal','greater')),1023)
            bad=mask.copy();bad[o.points[2]]=True
            self.assertEqual(ref.mask_reference(self.seal,o,bad,b'\1'*32)['status'],'ineligible_asymmetric_mask')
            bad={R:False for R in o.points}
            self.assertEqual(ref.mask_reference(self.seal,o,bad,b'\1'*32)['status'],'ineligible_undefined_anchor')
            bad[o.points[1]]=bad[o.points[-1]]=True
            degenerate=ref.mask_reference(self.seal,o,bad,b'\1'*32)
            self.assertEqual(degenerate['support']['exact_small'],1)
            self.assertEqual(degenerate['duplicate_draws'],1022)
            self.assertEqual(ref.tie_counts(1,[0,1,1,2]),{'less':1,'equal':2,'greater':1,'count':4,'inferential_p_value':None})
            print(json.dumps({'fixture':name,'references':{'null_support':out['support'],
                'null_duplicate_draws':out['duplicate_draws'],'BSGS_all_targets':g.r,
                'uniform_saturation_domain':g.r-1}},sort_keys=True))


if __name__=='__main__':unittest.main(verbosity=2)
