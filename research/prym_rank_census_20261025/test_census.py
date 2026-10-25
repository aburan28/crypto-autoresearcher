"""Planted software controls only; never samples the prospective science panel."""
from copy import deepcopy
import unittest

from check_census import check
from rank_census import collect, nullspace, schedule
from relations import Rank
from witness import controls

FIXTURE = {'p': 19, 'a': 0, 'b': 3, 'r': 13, 'P': [1, 17], 'uid': 'planted-software-control',
           'factor_base': [{'point': [1, 2], 'lift': [1, 2]},
                           {'point': [7, 2], 'lift': [8, 2]},
                           {'point': [11, 2], 'lift': [7, 2]}]}
CONFIG = dict(domain='prym-rank-census-planted-software', public_source_max=1,
              sample_branches_per_source=8, seeds=[0], arms=['sample64', 'full3584'])


def planted():
    blocks = []
    cells = [collect(FIXTURE, 0, CONFIG, arm, blocks.append) for arm in CONFIG['arms']]
    return dict(complete=True, secret_labels_present=False, cells=cells, controls=controls()), blocks


class Tests(unittest.TestCase):
    def test_complete_replay_and_nested_rank(self):
        result, blocks = planted()
        checked = check(CONFIG, {'fixtures': [FIXTURE]}, result, iter(blocks))
        self.assertEqual(len(checked), 2)
        self.assertEqual([c['attempts_replayed'] for c in checked], [8, 64])
        self.assertGreater(checked[1]['rows_verified'], 0)

    def test_tampered_reject_and_missing_branch_fail(self):
        result, blocks = planted()
        changed = deepcopy(blocks)
        changed[0]['statuses'] = '?' + changed[0]['statuses'][1:]
        with self.assertRaises(ValueError):
            check(CONFIG, {'fixtures': [FIXTURE]}, result, iter(changed))
        with self.assertRaises((ValueError, StopIteration)):
            check(CONFIG, {'fixtures': [FIXTURE]}, result, iter(blocks[:-1]))

    def test_known_columns_cannot_be_restored(self):
        result, blocks = planted()
        result['cells'][0]['projection']['public_derivations'] = []
        with self.assertRaises(ValueError):
            check(CONFIG, {'fixtures': [FIXTURE]}, result, iter(blocks))

    def test_false_witness_and_kernel_are_rejected(self):
        result, blocks = planted()
        bad = deepcopy(result)
        bad['cells'][1]['rows'][0]['source_scalar'] = 2
        with self.assertRaises(ValueError):
            check(CONFIG, {'fixtures': [FIXTURE]}, bad, iter(blocks))
        bad = deepcopy(result)
        bad['cells'][1]['nullspace'] = [[0]*bad['cells'][1]['projection']['U']]
        with self.assertRaises(ValueError):
            check(CONFIG, {'fixtures': [FIXTURE]}, bad, iter(blocks))

    def test_nullspace_spans_finite_kernel(self):
        rank = Rank(3, 13)
        rank.add([1, 2, 3], 7)
        vectors = nullspace(rank)
        self.assertEqual(len(vectors), 2)
        self.assertTrue(all(sum(a*b for a, b in zip([1, 2, 3], v)) % 13 == 0 for v in vectors))
        rank.add([0, 1, 2], 3)
        self.assertEqual(len(nullspace(rank)), 1)

    def test_finite_schedule_is_nested_without_replenishment(self):
        sources, pool, sampled = schedule(FIXTURE, 0, CONFIG)
        self.assertEqual(sources, [1])
        self.assertEqual(len(pool), 64)
        self.assertEqual(len(set(sampled[1])), 8)
        self.assertTrue(set(sampled[1]) <= set(range(len(pool))))


if __name__ == '__main__':
    unittest.main()
