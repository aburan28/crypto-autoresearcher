import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from native import Sampler,build,seed_for
from verify import multiply,points,scalar_draw
from identity import generator_identity
from metrics import features
from research import immutable,jobs


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.sampler=Sampler(build(Path(cls.temp.name)/'native.so'))
        cls.curve={'p':17,'A':2,'B':2,'N':19}
        cls.generator=[5,1]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_native_iid_matches_independent_affine_arithmetic(self):
        seed=seed_for('unit-test','iid')
        raw,counter=self.sampler.sample(self.curve,self.generator,seed,0,300)
        start=0
        for point in points(raw,17):
            k,start=scalar_draw(seed,19,start)
            self.assertEqual(point,multiply(self.curve,tuple(self.generator),k))
        self.assertEqual(start,counter)

    def test_uniform_affine_sampler_handles_two_torsion(self):
        curve={'p':17,'A':1,'B':0,'N':16}
        raw,_=self.sampler.sample(curve,[0,0],seed_for('unit-test','torsion'),2,100000)
        observed=Counter(points(raw,17))
        expected={(x,y) for x in range(17) for y in range(17) if (y*y-x*x*x-x)%17==0}
        self.assertEqual(set(observed),expected)
        # An incorrect zero-RHS acceptance makes its one-point fibers twice as
        # frequent. A generous fixed tolerance catches that substantive bias.
        target=100000/len(expected)
        for count in observed.values(): self.assertLess(abs(count-target),target*.06)

    def test_invalid_generator_refused(self):
        with self.assertRaises(ArithmeticError):
            self.sampler.sample(self.curve,[1,1],seed_for('invalid'),0,1)

    def test_exact_bits_and_bins(self):
        p=(1<<192)-(1<<64)-1; width=24
        coords=[(0,1),(p//2,1),(p-1,1),(1<<64,1),(1<<96,1)]
        raw=b''.join(x.to_bytes(width,'big')+y.to_bytes(width,'big') for x,y in coords)
        result,_=features(raw,p,32)
        counts=Counter(32*x//p for x,y in coords)
        self.assertEqual(result['x_bin_counts'],[counts[i] for i in range(32)])

    def test_published_ec1_identity_is_preserved(self):
        inputs=json.loads((HERE/'inputs.json').read_text())
        for anchor in inputs['anchors']:
            self.assertEqual(generator_identity(anchor,anchor['G'],'niststandard'),anchor['identity'])

    def test_fixed_cohort_counts_and_seed_pairing(self):
        inputs=json.loads((HERE/'inputs.json').read_text());config=json.loads((HERE/'config.json').read_text())
        queue=jobs(inputs,config);self.assertEqual(len({j['id'] for j in queue}),len(queue))
        for case in config['cases']:
            for cohort in ('published','random'):
                self.assertEqual(sum(j['points'] for j in queue if j['case']==case and j['mode']=='walk' and j['cohort']==cohort),10485760)
        self.assertEqual(sum(j['points'] for j in queue),46399488)

    def test_immutable_write_and_replay(self):
        path=Path(self.temp.name)/'immutable.json'
        immutable(path,b'one');immutable(path,b'one')
        with self.assertRaises(ValueError):immutable(path,b'two')


if __name__=='__main__': unittest.main()
