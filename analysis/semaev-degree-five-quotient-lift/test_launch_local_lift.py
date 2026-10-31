"""Reject retained-seed dimension mistakes before host admission."""

import copy
import json
from pathlib import Path
import unittest

from launch_local_lift import validate_request_dimensions


class RetainedRequestDimensions(unittest.TestCase):
    def test_published_n49_seed_uses_fifty_boolean_variables(self):
        request_path = Path(__file__).parent / 'runtime/n49-poly00-d5-local-request-001.json'
        request = json.loads(request_path.read_text())
        with self.assertRaisesRegex(ValueError, 'Boolean variable count 2k'):
            validate_request_dimensions(request)

        corrected = copy.deepcopy(request)
        corrected['disk_policy']['N'] = 50
        validate_request_dimensions(corrected)

        corrected['seed_bytes'] += 1
        with self.assertRaisesRegex(ValueError, 'seed size disagrees'):
            validate_request_dimensions(corrected)


if __name__ == '__main__':
    unittest.main()
