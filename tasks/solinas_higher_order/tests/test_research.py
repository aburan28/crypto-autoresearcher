import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from metrics import features, encode, decode, gf2_hankel_rank, mutual_information, longest_run, transport
from native import Sampler, build, seed_for
from oracle import add, multiply, sqrt_mod
from research import immutable, initialize, check_source, jobs, one_job, run, canonical
from verify import x_triple_relation, verify_job
from analyze import paired, binomial_interval


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(); cls.root = Path(cls.scratch.name)
        cls.inputs = json.loads((HERE/'inputs.json').read_text())
        cls.targets = json.loads((HERE/'targets.json').read_text())
        cls.config = json.loads((HERE/'config.json').read_text())
        cls.library = build(cls.root/'sampler.so'); cls.sampler = Sampler(cls.library)

    @classmethod
    def tearDownClass(cls): cls.scratch.cleanup()

    def test_native_prefix_and_walk_against_affine_oracle(self):
        for curve in self.inputs['anchors']:
            raw, used = self.sampler.sample(curve, curve['G'], seed_for('engineering', curve['case']), 3, 80)
            self.assertEqual(used, 0); coords = decode(raw, curve['p'])
            q = None
            for actual in coords:
                q = add(curve, q, tuple(curve['G'])); self.assertEqual(q, actual)
            raw, used = self.sampler.sample(curve, curve['G'], seed_for('engineering-walk', curve['case']), 1, 64)
            coords = decode(raw, curve['p'])
            for i in range(63): self.assertEqual(add(curve, coords[i], tuple(curve['G'])), coords[i+1])
            with self.assertRaises(ArithmeticError): self.sampler.sample(curve, curve['G'], seed_for('bad'), 5, 64)

    def test_mi_formulas_and_positive_controls(self):
        values = np.arange(64, dtype=int)
        self.assertAlmostEqual(mutual_information(values//8, values % 8), 0)
        self.assertAlmostEqual(mutual_information(values//8, values//8), 3)
        p = self.inputs['anchors'][0]['p']; raw = encode([(i, i) for i in range(256)], p)
        f = features(raw, p)
        self.assertEqual(f['longrun64'], 256)
        self.assertEqual(f['hankel64_deficit'], 32)
        self.assertEqual(f['triple64'], 1)
        self.assertAlmostEqual(f['perm_gap'], np.log2(6))
        self.assertGreater(f['motif64'], 100)

    def test_binary_rank_against_separate_matrix_elimination(self):
        for seed in range(8):
            bits = np.random.default_rng(seed).integers(0, 2, 63, dtype=np.int8)
            matrix = np.array([bits[i:i+32] for i in range(32)]); rank = 0
            for column in range(32):
                candidates = np.flatnonzero(matrix[rank:, column])
                if not len(candidates): continue
                row = rank+int(candidates[0]); matrix[[rank, row]] = matrix[[row, rank]]
                for i in range(rank+1, 32):
                    if matrix[i, column]: matrix[i] ^= matrix[rank]
                rank += 1
            self.assertEqual(gf2_hankel_rank(bits), rank)
        self.assertEqual(gf2_hankel_rank(np.zeros(63, dtype=np.int8)), 0)
        self.assertLessEqual(gf2_hankel_rank(np.arange(63) % 2), 2)

    def test_exact_tail_binning_and_bit_motif_formula(self):
        p = self.inputs['anchors'][1]['p']
        xs = [0, p//64, p//64+1, p-1]*32
        f = features(encode([(x, x) for x in xs], p), p)
        self.assertEqual(f['x_tail64'], sum(64*x < p for x in xs)/len(xs))
        self.assertEqual(f['xy_tail64'], f['x_tail64'])
        bits = [(x >> 64) & 1 for x in xs]
        products = [(2*bits[i]-1)*(2*bits[i+1]-1)*(2*bits[i+2]-1) for i in range(len(bits)-2)]
        self.assertEqual(f['triple64'], abs(sum(products)/len(products)))
        self.assertEqual(longest_run(np.array([0, 0, 1, 1, 1, 0])), 3)
        with self.assertRaises(ValueError): features(encode([(p, 0)]*64, p), p)

    def test_sqrt_targets_and_sign_deduplication(self):
        self.assertEqual(len(self.targets['targets']), 320)
        anchors = {a['case']: a for a in self.inputs['anchors']}
        for item in self.targets['targets']:
            curve = anchors[item['case']]; x, y = item['G']; p = curve['p']
            self.assertEqual((y*y-x*x*x-curve['A']*x-curve['B']) % p, 0)
            self.assertLessEqual(y, p-y)
        for p in (101, 127, 257):
            for v in range(p):
                result = sqrt_mod(v, p)
                roots = [x for x in range(p) if x*x % p == v]
                self.assertEqual(result, min(roots) if roots else None)

    def test_universal_triples_and_isomorphic_transport(self):
        curve = self.inputs['anchors'][0]; p = curve['p']
        raw, used = self.sampler.sample(curve, curve['G'], seed_for('identity'), 3, 80)
        coords = decode(raw, p); wrong = multiply(curve, tuple(curve['G']), 2)[0]
        for i in range(16, 77):
            triple = [coords[i+j][0] for j in range(3)]
            self.assertTrue(x_triple_relation(curve, triple, curve['G'][0]))
            self.assertFalse(x_triple_relation(curve, triple, wrong))
        for x, y in decode(transport(raw, p), p):
            self.assertEqual((y*y-x*x*x-16*curve['A']*x-64*curve['B']) % p, 0)
        # A small non-Solinas control model checks that the relation is generic.
        toy = {'p': 101, 'A': 2, 'B': 3}; h = (1, sqrt_mod(6, 101))
        checked = 0
        for k in range(2, 40):
            three = [multiply(toy, h, k+j) for j in range(3)]
            if None in three: continue
            self.assertTrue(x_triple_relation(toy, [q[0] for q in three], h[0])); checked += 1
        self.assertGreater(checked, 10)

    def test_jobs_and_raw_units_replay_for_every_cohort(self):
        config = copy.deepcopy(self.config); config.update(walk_blocks=2, walk_points=64, field_points=64,
            bank_generators=4, bank_chunk=2, prefix_points=64, target_points=64, target_starts=2, diagnostic_blocks=1)
        queue = jobs(self.inputs, self.targets, config)
        for kind in ('walk', 'bank', 'prefix', 'target', 'field'):
            job = next(j for j in queue if j['kind'] == kind)
            out = self.root/('unit-'+kind)
            one_job(job, config, str(out), str(self.library), 'engineering-design')
            result = verify_job(job, str(out), config, 'engineering-design')
            self.assertEqual(result['points'], job['points'])
            self.assertEqual(result['wrong_step_hits'], 0)
            self.assertEqual(result['shuffled_triple_hits'], 0)

    def test_immutability_and_corrupt_resume(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch); path = root/'immutable.json'; immutable(path, b'one'); immutable(path, b'one')
            with self.assertRaises(ValueError): immutable(path, b'two')
            config = copy.deepcopy(self.config); config.update(walk_blocks=2, walk_points=64, field_points=64,
                bank_generators=4, bank_chunk=2, prefix_points=64, target_points=64, target_starts=2, diagnostic_blocks=1)
            cp = root/'config.json'; cp.write_bytes(canonical(config)); out = root/'run'
            _, _, sha = initialize(out, cp)
            with self.assertRaises(ValueError): initialize(out, cp, 'different-seed')
            job = jobs(self.inputs, self.targets, config)[0]
            one_job(job, config, str(out), str(self.library), sha)
            raw = out/'points'/(job['id']+'.raw'); raw.write_bytes(raw.read_bytes()+b'x')
            with self.assertRaisesRegex(ValueError, 'checksum'): run(out, 1)

    def test_inference_unit_and_zero_hit_interval(self):
        result = paired([1, 2, 3, 4], [0, 1, 2, 3], .001)
        self.assertEqual(result['difference'], 1)
        self.assertEqual(result['left_units'], 4)
        lo, hi = binomial_interval(0, 100000, .001)
        self.assertEqual(lo, 0)
        self.assertAlmostEqual(hi, 1-(.001/2)**(1/100000))


if __name__ == '__main__': unittest.main()
