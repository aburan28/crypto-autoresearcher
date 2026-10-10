import unittest
from tools.progress_dashboard import bootstrap_paired, frontiers, render_html
from tests.test_progress_fidelity import sample

class DashboardTests(unittest.TestCase):
    def test_few_pairs_not_confident(self):
        self.assertEqual(bootstrap_paired(sample())["status"], "insufficient_pairs")

    def test_bootstrap_reproducible(self):
        r = sample()
        r["baseline"]["observations"] = [10, 12, 14, 16, 18, 20]
        r["candidate"]["observations"] = [5, 6, 7, 8, 9, 10]
        r["baseline"]["pairs"] = list("abcdef")
        r["candidate"]["pairs"] = list("abcdef")
        self.assertEqual(bootstrap_paired(r), bootstrap_paired(r))
        self.assertAlmostEqual(bootstrap_paired(r)["lower"], 2)

    def test_frontier_does_not_multiply_speedups(self):
        base = dict(claim_id="a", qualified_schema=True, curve_id="x",
                    scale="toy-scale", metric="cost", unit="seconds",
                    level="local", evidence="measured", speedup=2)
        other = dict(base, claim_id="b", speedup=3)
        self.assertEqual(frontiers([base, other])[0]["speedup"], 3)

    def test_html_escapes(self):
        rendered = render_html([dict(path="<script>alert(1)</script>", qualified_schema=False, error="bad")])
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

if __name__ == "__main__":
    unittest.main()
