"""Small correctness controls for the five candidate paths."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from .certificate import certify
from .experiments import BooleanF4, elimlin, hybrid, xor_sat
from .research_worker import solve
from .runner import run


class SolverTrials(unittest.TestCase):
    def test_block_f4_and_elimlin_prove_real_consequence(self):
        original = [[3, 4], [3, 8], [1, 2]]
        affine, stats = elimlin(original, 4, degree=3)
        self.assertGreater(stats["elimlin_affine"], 0)
        self.assertIn([4, 8], [sorted(row) for row in affine])
        for blocks in (None, [2, 2]):
            with self.subTest(blocks=blocks):
                solver = BooleanF4(4, blocks)
                basis = solver.solve(original + affine)
                self.assertTrue(certify(4, original, basis, blocks=blocks)["verified"])
                self.assertGreater(solver.stats["largest_matrix_rows"], 0)

    def test_xor_and_hybrid_return_replayed_witnesses(self):
        original = [[3, 4], [3, 8], [1, 2]]
        a, stats = xor_sat(original, 4)
        self.assertGreater(stats["xor_sat_nodes"], 0)
        self.assertIn(a, certify(4, original, BooleanF4(4).solve(original))["solutions"])
        b, branches = hybrid(original, 4, guess=1, blocks=[2, 2])
        self.assertIn(b, certify(4, original, BooleanF4(4).solve(original))["solutions"])
        self.assertEqual(branches[-1]["status"], "verified_witness")

    def test_native_xor_sat(self):
        try:
            import pycryptosat
        except ImportError:
            self.skipTest("native CryptoMiniSat not installed")
        original = [[3, 4], [3, 8], [1, 2]]
        response = solve("cryptominisat", {"operation": "solve", "ring": {"nvars": 4},
                                           "instance": {"equations": original}})
        self.assertEqual(response["status"], "ok")
        self.assertIn(response["solutions"][0],
                      certify(4, original, BooleanF4(4).solve(original))["solutions"])
        specialized = solve("hybrid-cryptominisat", {
            "operation": "solve", "ring": {"nvars": 4},
            "instance": {"equations": original, "blocks": [2, 2], "hybrid_guess": 1}})
        self.assertEqual(specialized["status"], "ok")
        self.assertIn(specialized["solutions"][0],
                      certify(4, original, BooleanF4(4).solve(original))["solutions"])
        self.assertGreater(specialized["metrics"]["branches_attempted"], 0)

    @unittest.skipUnless(os.environ.get("M5GB_BINARY"), "pinned M5GB bridge not built")
    def test_upstream_m5gb_basis(self):
        original = [[1, 2], [3, 4]]
        response = solve("m5gb", {"operation": "solve", "ring": {"nvars": 3},
                                   "instance": {"equations": original}})
        self.assertEqual(response["status"], "ok")
        self.assertTrue(certify(3, original, response["basis_terms"])["verified"])
        self.assertIn("binary-sha256", response["solver_version"])

    @unittest.skipUnless(Path("groebner_compare/ecc2k17_five_way.json").is_file(),
                         "frozen ECC fixture belongs to cryptanalysis")
    def test_frozen_ecc_curve_verifier(self):
        from .pdp_verifier import check
        manifest = json.loads(Path("groebner_compare/ecc2k17_five_way.json").read_text())
        inst = manifest["instances"][0]
        reply = check({"operation": "verify_witnesses", "ring": manifest["ring"],
                       "instance": inst, "solutions": [inst["pdp"]["planted"], 0]})
        self.assertEqual(reply["verified_solutions"], [inst["pdp"]["planted"]])
        tampered = json.loads(json.dumps(inst))
        tampered["equations"][0].append(0)
        with self.assertRaises(ValueError):
            check({"operation": "verify_witnesses", "ring": manifest["ring"],
                   "instance": tampered, "solutions": [inst["pdp"]["planted"]]})

    def test_runner_distinguishes_basis_and_witness(self):
        program = "import json,sys\nfor l in sys.stdin:\n q=json.loads(l);print(json.dumps({'request_id':q['request_id'],'status':'ok','solutions':[0]}),flush=True)"
        manifest = {"schema": 1, "encoding": "witness-control", "watchdog_seconds": 2,
                    "ring": {"nvars": 2, "field": "GF(2)", "quotient": "x_i^2+x_i",
                             "order": "degrevlex", "variables": ["x0", "x1"]},
                    "instances": [{"id": "root", "equations": [[1, 2]]},
                                  {"id": "rejected", "equations": [[0]]}],
                    "backends": [{"id": "double", "mode": "warm",
                                  "command": [sys.executable, "-c", program],
                                  "provenance": "test-only witness double"}]}
        with tempfile.TemporaryDirectory() as folder:
            result = run(manifest, Path(folder) / "receipts")[0]
        self.assertEqual(result["verified_witness_instances"], 1)
        self.assertEqual(result["verified_instances"], 0)
        self.assertEqual([row["status"] for row in result["results"]],
                         ["verified_witness", "unknown"])


if __name__ == "__main__":
    unittest.main()
