"""Software checks on selector arithmetic and data separation; no science run."""
import unittest

from companion_selector import (accepts, add_companion, candidate_digest,
                                companion_point, fit, public_bucket, split)


class SelectorTests(unittest.TestCase):
    def test_two_cover_lifts_have_opposite_companion_points(self):
        # Integer point (1,2) on y²=x6+3, reduced at p=101.
        left = companion_point(101, 0, 3, 1, 2)
        right = companion_point(101, 0, 3, -1, 2)
        self.assertEqual(left, (3, 6))
        self.assertIsNone(add_companion(101, 0, 3, left, right))
        doubled = add_companion(101, 0, 3, left, left)
        u, v = doubled
        self.assertEqual((v*v-u**3-9) % 101, 0)
        self.assertEqual(public_bucket(101, None), 'infinity')

    def test_training_cannot_consume_holdout_or_duplicate(self):
        ids = []
        for a in range(100):
            ident = candidate_digest({'curve_uid': 'software-fixture',
                                      'source_scalar': a, 'lambda': 1,
                                      'signed_fb_lift_ids': ['1+', '2-', '3+']})
            ids.append(ident)
        train = [x for x in ids if split(x) == 'train']
        holdout = next(x for x in ids if split(x) == 'holdout')
        records = [{'candidate_id': ident, 'bucket': f'bin{i%4}',
                    'accepted': i % 4 == 0} for i, ident in enumerate(train)]
        model = fit(records)
        self.assertTrue(accepts(model, 'bin0'))
        self.assertFalse(accepts(model, 'unseen'))
        with self.assertRaises(ValueError):
            fit(records+[records[0]])
        with self.assertRaises(ValueError):
            fit([{'candidate_id': holdout, 'bucket': 'bin0', 'accepted': True}])


if __name__ == '__main__':
    unittest.main()
