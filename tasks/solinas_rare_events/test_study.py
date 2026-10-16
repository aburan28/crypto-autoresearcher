"""Engineering checks use seeds distinct from the frozen scientific seed."""
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from analyze import cp, mcnemar
from metrics import fair_coin_run_probability, scores_from_packed
from native import Engine, build, seed_for
from oracle import add, affine_draw, multiply, scalar_draw
from research import HERE, check_record, run_study
from verify import verify


class StudyTests(unittest.TestCase):
    def test_planted_and_negative_bits(self):
        sequences=np.array([[0]*256,[i%2 for i in range(256)]],dtype=np.uint8)
        scores=scores_from_packed(np.packbits(sequences,axis=1,bitorder='little'))
        self.assertEqual(scores[0,0],256);self.assertEqual(scores[1,0],1)
        self.assertEqual(scores[0,1],254);self.assertEqual(scores[0,2],15*253**2)
        for length in range(2,11):
            for threshold in range(2,length+2):
                hit=0
                for seq in itertools.product((0,1),repeat=length):
                    longest=max(len(list(g)) for _,g in itertools.groupby(seq));hit+=longest>=threshold
                self.assertAlmostEqual(fair_coin_run_probability(length,threshold),hit/2**length)

    def test_exact_statistics_controls(self):
        self.assertEqual(mcnemar(np.ones((100,2),dtype=bool),0,1)['p_two_sided_exact'],1)
        flags=np.zeros((32,2),dtype=bool);flags[:,0]=True
        self.assertLess(mcnemar(flags,0,1)['p_two_sided_exact'],1e-8)
        lower,upper=cp(0,4096,.0001)
        self.assertEqual(lower,0);self.assertGreater(upper,0)

    def test_native_full_stream_and_oracle(self):
        inputs=json.loads((HERE/'inputs.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);engine=Engine(build(root/'engine.so'))
            for index,model in enumerate(inputs['candidates']+[inputs['ordinary_controls'][0]]):
                named=(1 if model.get('case')=='P-192' else 2) if index<3 else 0
                curve=model['curve'] if named else {k:model[k] for k in ('p','A','B','N')}
                width=(curve['p'].bit_length()+7)//8;cohorts=3 if named else 1;count=8
                starts=seed_for('engineering-full-stream-v1',index,'start');gens=seed_for('engineering-full-stream-v1',index,'gen')
                directory=root/str(index)
                data=engine.sample(curve,model['G'],named,count,0,1,starts,gens,directory,True)
                self.assertTrue(np.array_equal(scores_from_packed(data['bits']),data['scores']))
                raw=(directory/'coordinates.raw').read_bytes();stride=256*2*width
                streams=[b''.join(raw[(w*cohorts+c)*stride:(w*cohorts+c+1)*stride] for w in range(count)) for c in range(cohorts)]
                self.assertEqual([hashlib.sha256(s).hexdigest() for s in streams],data['coordinate_sha256'])
                sc=gc=0
                for w in range(count):
                    if named:
                        k,sc=scalar_draw(starts,curve['N'],sc);r,gc=scalar_draw(gens,curve['N'],gc)
                        expected=multiply(curve,tuple(model['published_G']),k)
                        steps=[tuple(model['G']),tuple(model['published_G']),multiply(curve,tuple(model['published_G']),r)]
                    else:expected,sc=affine_draw(curve,starts,sc);steps=[tuple(model['G'])]
                    for c in range(cohorts):
                        offset=(w*cohorts+c)*stride;points=[tuple(int.from_bytes(raw[i+j*width:i+(j+1)*width],'big') for j in (0,1)) for i in range(offset,offset+stride,2*width)]
                        self.assertEqual(points[0],expected)
                        for j in range(1,256):self.assertEqual(points[j],add(curve,points[j-1],steps[c]))
                        packed=np.packbits(np.array([(x>>64)&1 for x,y in points],dtype=np.uint8),bitorder='little')
                        self.assertTrue(np.array_equal(packed,data['bits'][w,c]))
                self.assertEqual([sc,gc],data['counter_consumed'])

    def test_resumable_pipeline_and_corrupt_refusal(self):
        inputs=json.loads((HERE/'inputs.json').read_text());config=json.loads((HERE/'config.json').read_text())
        inputs['ordinary_controls']=[inputs['ordinary_controls'][0]]
        for model in inputs['candidates']+inputs['ordinary_controls']:model['windows']=4
        config.update(seed='engineering-resume-v1',chunk_windows=2)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'run';first=run_study(root,inputs,config,1);second=run_study(root,inputs,config,1)
            self.assertEqual(first['point_observations'],second['point_observations'])
            result=verify(root);self.assertEqual(result['totals']['windows_with_all_scores_replayed'],40)
            record=json.loads(next((root/'records').glob('*.json')).read_text())
            path=root/'artifacts'/record['id']/'bits.bin';data=bytearray(path.read_bytes());data[0]^=1;path.write_bytes(data)
            with self.assertRaises(ValueError):check_record(root,record)
            changed=dict(config,seed='engineering-changed-v1')
            with self.assertRaises(ValueError):run_study(root,inputs,changed,1)


if __name__=='__main__':unittest.main()
