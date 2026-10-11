import unittest
from tools.progress_fidelity import InvalidClaim, evaluate

def sample():
    b = dict(observations=[10, 12, 14], pairs=["a:1", "b:2", "c:3"],
             attempted=3, verified=3, failed=0, timed_out=0, invalid=0)
    return dict(claim_id="TEST", family="index_calculus", level="local",
                scale="toy-scale", metric="cost per verified relation", unit="seconds",
                scope=dict(curve_id="toy", field="GF(2^31)", bits=31,
                           instance_generator="v1", parameter_digest="abc"),
                baseline=b, candidate=dict(b, observations=[5, 6, 7]),
                provenance=dict(protocol="frozen", baseline_commit="abc", candidate_commit="def",
                                hardware="cpu", environment_digest="sha256:xyz",
                                verification_artifact="runs/verified.json", run_ids=["r1", "r2"]),
                cost_model=dict(type="none"))

class TestProgressFidelity(unittest.TestCase):
    def test_local(self):
        self.assertEqual(evaluate(sample())["speedup"], 2)
    def test_unmatched_pairs(self):
        r = sample()
        r["candidate"]["pairs"] = ["z:1", "b:2", "c:3"]
        with self.assertRaises(InvalidClaim): evaluate(r)
    def test_censored(self):
        r = sample()
        r["candidate"]["verified"] = 2
        r["candidate"]["timed_out"] = 1
        with self.assertRaises(InvalidClaim): evaluate(r)
    def test_missing_certificate(self):
        r = sample()
        del r["provenance"]["verification_artifact"]
        with self.assertRaises(InvalidClaim): evaluate(r)
    def test_end_to_end_amdahl(self):
        r = sample()
        r["level"] = "end_to_end"
        r["cost_model"] = dict(type="measured", components=[
            dict(name="other", unit="seconds", baseline=90, candidate=90),
            dict(name="optimized", unit="seconds", baseline=10, candidate=5)])
        self.assertAlmostEqual(evaluate(r)["speedup"], 100/95)
    def test_projection_needs_uncertainty(self):
        r = sample()
        r["level"] = "attack_projection"
        r["cost_model"] = dict(type="projection", components=[
            dict(name="solve", unit="seconds", baseline=100, candidate=50)])
        with self.assertRaises(InvalidClaim): evaluate(r)
    def test_throughput(self):
        r = sample()
        r["unit"] = "iterations_per_second"
        r["candidate"]["observations"] = [20, 24, 28]
        self.assertEqual(evaluate(r)["speedup"], 2)
    def test_nonfinite(self):
        r = sample()
        r["baseline"]["observations"][0] = float("nan")
        with self.assertRaises(InvalidClaim): evaluate(r)

if __name__ == "__main__":
    unittest.main()
