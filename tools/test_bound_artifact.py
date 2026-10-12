"""tools/bound_artifact.py: a bound record becomes a cairn artifact without
losing a bit, and the committed fixtures are exactly that rendering."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bound_artifact  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "cairn" / "checkers" / "fixtures"


class RenderTests(unittest.TestCase):
    def test_floats_become_decimal_strings_and_nothing_else_moves(self) -> None:
        record = {"a": 1.5, "b": 7, "c": True, "d": None, "e": "x", "f": [0.1, 2, [3.25]],
                  "g": {"h": 596.4583333333334, "i": 1e-05}}
        artifact = bound_artifact.render(record)
        self.assertEqual(artifact, {"a": "1.5", "b": 7, "c": True, "d": None, "e": "x",
                                    "f": ["0.1", 2, ["3.25"]],
                                    "g": {"h": "596.4583333333334", "i": "1e-05"}})
        self.assertEqual(bound_artifact.check(record, artifact), [])
        # Nothing in the artifact is a float, which is the whole point.
        self.assertNotIn("float", json.dumps(artifact).replace("1.5", ""))

    def test_a_non_finite_number_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            bound_artifact.render({"x": float("nan")})

    def test_check_catches_a_lossy_or_edited_rendering(self) -> None:
        record = {"x": 596.4583333333334}
        self.assertTrue(bound_artifact.check(record, {"x": "596.458"}))
        self.assertTrue(bound_artifact.check(record, {"x": 596.4583333333334}))

    def test_the_committed_fixtures_are_the_rendering_of_the_committed_records(self) -> None:
        for name in ("prime-rho-neg", "prime-bsgs-neg"):
            record = json.loads((FIXTURES / f"{name}.bound.json").read_text(encoding="utf-8"))
            artifact = json.loads((FIXTURES / f"{name}.artifact.json").read_text(encoding="utf-8"))
            self.assertEqual(bound_artifact.check(record, artifact), [], name)
            self.assertEqual((FIXTURES / f"{name}.artifact.json").read_text(encoding="utf-8"),
                             bound_artifact.dumps(bound_artifact.render(record)), name)

    def test_the_cli_renders_and_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "artifact.json"
            record = FIXTURES / "prime-rho-neg.bound.json"
            self.assertEqual(bound_artifact.main(["render", str(record), "--out", str(out)]), 0)
            self.assertEqual(bound_artifact.main(["check", str(record), str(out)]), 0)
            edited = json.loads(out.read_text(encoding="utf-8"))
            edited["sizes"][0]["mean_gae"] = "500.0"
            out.write_text(json.dumps(edited), encoding="utf-8")
            self.assertEqual(bound_artifact.main(["check", str(record), str(out)]), 1)


if __name__ == "__main__":
    unittest.main()
