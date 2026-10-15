"""Non-study software checks only: p=5,7,11; no scientific panel execution."""
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/"tools"))

from lattice_ic_core import (Counter, Curve, Field, check_artifacts, encode_point,
                             factorize, poly_eval_mod, rank_mod,
                             select_prime_subgroup, write_artifacts)
from src.crypto_autoresearcher.index_calculus.curve import Curve as OracleCurve


class FieldTests(unittest.TestCase):
    def test_prime_arithmetic_and_encoding(self):
        for p in (5, 7, 11):
            f = Field(p)
            self.assertEqual(f.encode(-1), [p-1])
            self.assertEqual(list(f.elements()), [(i,) for i in range(p)])
            for a in range(p):
                self.assertEqual(f.pow(a, 0), f.one)
                for b in range(p):
                    self.assertEqual(f.add(a, b), ((a+b) % p,))
                    self.assertEqual(f.sub(a, b), ((a-b) % p,))
                    self.assertEqual(f.mul(a, b), ((a*b) % p,))
                if a:
                    self.assertEqual(f.mul(a, f.inv(a)), f.one)
                    self.assertEqual(f.pow(a, -1), f.inv(a))
            with self.assertRaises(ZeroDivisionError):
                f.inv(0)
            with self.assertRaises(TypeError):
                f.coerce((1, 2))

    def test_quadratic_arithmetic_and_all_inverses(self):
        for p, polynomial in ((5, (2, 0)), (7, (1, 0)), (11, (1, 0))):
            f = Field(p, polynomial)
            u = (0, 1)
            self.assertEqual(f.add(f.add(f.mul(u, u), f.mul(polynomial[1], u)), polynomial[0]), f.zero)
            self.assertEqual(f.order, p*p)
            self.assertEqual(f.key((p+1, -1)), (1, p-1))
            self.assertEqual(f.encode((1, 2)), [1, 2])
            for a in f.elements():
                self.assertEqual(f.add(a, f.neg(a)), f.zero)
                self.assertEqual(f.pow(a, p*p), a)
                if a != f.zero:
                    self.assertEqual(f.mul(a, f.inv(a)), f.one)
                    self.assertEqual(f.pow(a, -3), f.inv(f.pow(a, 3)))
            # Product checked against an independent direct convolution/remainder.
            for a in f.elements():
                for b in ((1, 2), (3, 4), u):
                    c0, c1 = polynomial
                    raw = [a[0]*b[0], a[0]*b[1]+a[1]*b[0], a[1]*b[1]]
                    expected = ((raw[0]-c0*raw[2]) % p, (raw[1]-c1*raw[2]) % p)
                    self.assertEqual(f.mul(a, b), expected)

    def test_nonzero_linear_coefficient(self):
        f = Field(5, (1, 1))  # discriminant 2 is nonsquare mod5
        for a in f.elements():
            if a != f.zero:
                self.assertEqual(f.mul(a, f.inv(a)), f.one)

    def test_invalid_fields(self):
        for p in (0, 1, 4, 9, True):
            with self.assertRaises(ValueError):
                Field(p)
        for poly in ((0, 1), (4, 0), (1, 2)):
            with self.assertRaises(ValueError):
                Field(5, poly)
        with self.assertRaises(ValueError):
            Field(5, (1,))


class CurveTests(unittest.TestCase):
    @staticmethod
    def scalar_point(point):
        return None if point is None else (point[0][0], point[1][0])

    def test_independent_prime_oracle_all_point_pairs(self):
        for p, a, b in ((5, 2, 1), (7, 1, 1), (11, 1, 1)):
            curve, oracle = Curve(Field(p), a, b), OracleCurve(p, a, b)
            expected = [None]+[(x, y) for x in range(p) for y in range(p)
                               if oracle.is_on_curve((x, y))]
            points = curve.points()
            self.assertEqual([self.scalar_point(t) for t in points], expected)
            for left in points:
                self.assertTrue(curve.is_on_curve(left))
                self.assertEqual(curve.add(left, curve.neg(left)), None)
                for right in points:
                    actual = curve.add(left, right)
                    self.assertTrue(curve.is_on_curve(actual))
                    self.assertEqual(self.scalar_point(actual),
                                     oracle.add(self.scalar_point(left), self.scalar_point(right)))
                for scalar in range(-3, 8):
                    self.assertEqual(self.scalar_point(curve.mul(scalar, left)),
                                     oracle.mul(scalar, self.scalar_point(left)))

    def test_exceptional_branches_and_validation(self):
        curve = Curve(Field(5), 1, 0)
        two_torsion = ((0,), (0,))
        self.assertEqual(curve.add(None, two_torsion), two_torsion)
        self.assertEqual(curve.add(two_torsion, None), two_torsion)
        self.assertIsNone(curve.add(two_torsion, two_torsion))
        self.assertIsNone(curve.mul(0, two_torsion))
        self.assertIsNone(curve.neg(None))
        self.assertFalse(curve.is_on_curve(((1,), (0,))))
        with self.assertRaises(ValueError):
            curve.add(((1,), (0,)), None)
        with self.assertRaises(ValueError):
            Curve(Field(5), 0, 0)

    def test_quadratic_enumeration_group_and_encoding(self):
        f, curve = Field(5, (2, 0)), None
        curve = Curve(f, 1, 1)
        points = curve.points()
        self.assertEqual(points[1:], sorted(points[1:]))
        # Independent enumeration predicate in the same tiny field checks that
        # the square-root table retains every y branch, not just one root.
        brute = [None]+[(x, y) for x in f.elements() for y in f.elements()
                       if f.mul(y, y) == f.add(f.add(f.mul(f.mul(x, x), x), f.mul(1, x)), 1)]
        self.assertEqual(points, brute)
        self.assertEqual(curve.points(), points)
        returned = curve.points()
        returned.pop()
        self.assertEqual(curve.points(), points)
        for point in points:
            self.assertEqual(curve.mul(len(points), point), None)
            self.assertTrue(curve.is_on_curve(curve.add(point, point)))
            self.assertEqual(encode_point(f, point), encode_point(point, curve))
        self.assertIsNone(encode_point(curve, None))
        self.assertEqual(encode_point(f, ((1, 2), (3, 4))), [[1, 2], [3, 4]])

    def test_subgroup_admission_rejections_and_certificate(self):
        curve = Curve(Field(5), 2, 1)
        admitted = select_prime_subgroup(curve)
        self.assertTrue(admitted["admitted"])
        self.assertEqual(admitted["order"], 7)
        self.assertEqual(admitted["r"], 7)
        self.assertEqual(admitted["factorization"], {"7": 1})
        self.assertEqual(admitted["P"], curve.points()[1])
        self.assertEqual(admitted["G"], [curve.mul(i, admitted["P"]) for i in range(7)])
        self.assertTrue(admitted["certificate"]["unique_r_subgroup"])
        self.assertFalse(select_prime_subgroup(curve, r=5)["admitted"])
        self.assertFalse(select_prime_subgroup(curve, r=4)["admitted"])
        square = Curve(Field(5), 1, 1)  # nine rational points
        self.assertFalse(select_prime_subgroup(square, r=3, min_prime=3)["admitted"])
        weak = select_prime_subgroup(square, r=3, min_prime=3, require_valuation_one=False)
        self.assertTrue(weak["admitted"])
        self.assertFalse(weak["certificate"]["unique_r_subgroup"])


class LinearAndCounterTests(unittest.TestCase):
    def test_rank_rectangular_zero_and_nonprime(self):
        for r in (5, 7, 11):
            self.assertEqual(rank_mod([], r), 0)
            self.assertEqual(rank_mod([[], []], r), 0)
            self.assertEqual(rank_mod([[1, 2, 3], [2, 4, 6], [0, 1, 1]], r), 2)
            self.assertEqual(rank_mod([[r, 0], [0, r]], r), 0)
            self.assertEqual(rank_mod([[0, 1], [1, 0], [2, 2]], r), 2)
        with self.assertRaises(ValueError):
            rank_mod([[1], [1, 2]], 5)
        with self.assertRaises(ValueError):
            rank_mod([[1]], 9)
        with self.assertRaises(TypeError):
            rank_mod([[1.5]], 5)
        self.assertEqual(poly_eval_mod([2, 3, 1], 4, 5), 0)
        self.assertEqual(factorize(99), {3: 2, 11: 1})

    def test_counter_nested_exception_and_snapshot_copy(self):
        counter = Counter()
        with counter.phase("outer"):
            counter.inc("operation")
            with self.assertRaises(RuntimeError):
                with counter.phase("inner"):
                    counter.inc("operation", 2)
                    raise RuntimeError("softwarecheck")
            counter.inc("operation")
        snapshot = counter.snapshot()
        self.assertEqual(snapshot["operations"]["operation"], 4)
        self.assertEqual(snapshot["phases"]["outer"]["operations"]["operation"], 2)
        self.assertEqual(snapshot["phases"]["inner"]["operations"]["operation"], 2)
        self.assertGreaterEqual(snapshot["phases"]["outer"]["wall_seconds"], 0)
        snapshot["operations"]["operation"] = 900
        self.assertEqual(counter.snapshot()["operations"]["operation"], 4)
        json.dumps(counter.snapshot(), allow_nan=False)


class ArtifactTests(unittest.TestCase):
    @staticmethod
    def result():
        return {"softwarecheck": True, "parameters": {"p": 5, "quadratic": (2, 0)},
                "checks": {"software_arithmetic": True}, "exact": Fraction(1, 3)}

    def write(self, directory, result=None):
        return write_artifacts(self.result() if result is None else result, directory, 7,
                               datetime.now(timezone.utc).isoformat(),
                               time.monotonic(), time.process_time())

    def test_standalone_unknown_provenance_and_exclusive_files(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            manifest = self.write(directory)
            run = manifest["run"]
            self.assertEqual(run["status"], "development_only")
            self.assertIsNone(run["id"])
            self.assertIsNone(run["code"]["commit"])
            self.assertIsNone(run["code"]["dirty_tree"])
            self.assertIn("commit", run["missing_provenance"])
            self.assertNotIn("planted ambient orders", run["inputs"]["instance_policy"])
            self.assertEqual(json.loads((directory/"raw-result.json").read_text())["exact"],
                             {"numerator": 1, "denominator": 3})
            self.assertFalse(check_artifacts(directory)["scientific_validation"])
            digest = hashlib.sha256((directory/"raw-result.json").read_bytes()).hexdigest()
            with self.assertRaises(FileExistsError):
                self.write(directory)
            self.assertEqual(digest, hashlib.sha256((directory/"raw-result.json").read_bytes()).hexdigest())
            self.assertFalse((directory/"launch.json").exists())

    def test_fake_supervisor_metadata_stays_softwarecheck(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            launch = {"softwarecheck": True, "run_id": "RUN-SOFTWARECHECK-000000",
                      "experiment_id": "EXP-SOFTWARECHECK-000000", "argv": ["python", "softwarecheck.py"],
                      "authority": {"commit": "softwarecheck_fixture_commit"}}
            environment = {"softwarecheck": True, "commit": "softwarecheck_fixture_commit",
                           "source_sha256": {"softwarecheck.py": "not_a_real_source_hash"}}
            (directory/"launch.json").write_text(json.dumps(launch))
            (directory/"environment.json").write_text(json.dumps(environment))
            before = (directory/"environment.json").read_bytes()
            run = self.write(directory)["run"]
            self.assertEqual(run["status"], "development_only")
            self.assertTrue(run["softwarecheck"])
            self.assertEqual(run["code"]["commit"], "softwarecheck_fixture_commit")
            self.assertEqual(run["code"]["argv"], launch["argv"])
            self.assertEqual(run["code"]["source_binding"], environment["source_sha256"])
            self.assertIsNone(run["code"]["dirty_tree"])
            self.assertEqual((directory/"environment.json").read_bytes(), before)
            dependencies = run["environment"]["installed_dependencies"]
            self.assertIn("installed_version", dependencies["sympy"])
            self.assertIn("installed_version", dependencies["fpylll"])
            process = subprocess.run([sys.executable, str(ROOT/"tools/lattice_ic_core.py"),
                                      "--check", str(directory)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertTrue(json.loads(process.stdout)["development_only"])

    def test_partial_metadata_bad_commit_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            (directory/"launch.json").write_text(json.dumps({"softwarecheck": True}))
            with self.assertRaisesRegex(ValueError, "partial"):
                self.write(directory)
            self.assertFalse((directory/"raw-result.json").exists())
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            (directory/"launch.json").write_text(json.dumps({"softwarecheck": True,
                "argv": ["python", "softwarecheck"], "authority": {"commit": "fixture_A"}}))
            (directory/"environment.json").write_text(json.dumps({"softwarecheck": True, "commit": "fixture_B"}))
            with self.assertRaisesRegex(ValueError, "commit mismatch"):
                self.write(directory)
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            self.write(directory)
            (directory/"raw-result.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                check_artifacts(directory)

    def test_non_json_values_rejected_before_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            result = self.result()
            result["bad"] = float("nan")
            with self.assertRaises(ValueError):
                self.write(directory, result)
            self.assertFalse((directory/"raw-result.json").exists())

    def test_canonical_path_crosscheck_remains_softwarecheck(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)/"EXP-SOFTWARECHECK-000000"/"runs"/"RUN-SOFTWARECHECK-000000"
            directory.mkdir(parents=True)
            launch = {"softwarecheck": True, "run_id": directory.name,
                      "argv": ["python", "softwarecheck.py"]}
            environment = {"softwarecheck": True, "commit": "softwarecheck_fixture_commit",
                           "source_sha256": {"softwarecheck.py": "not_a_real_source_hash"}}
            (directory/"launch.json").write_text(json.dumps(launch))
            (directory/"environment.json").write_text(json.dumps(environment))
            run = self.write(directory)["run"]
            self.assertEqual(run["experiment_id"], directory.parent.parent.name)
            self.assertEqual(run["status"], "development_only")
            launch["run_id"] = "RUN-SOFTWARECHECK-wrong_path"
            other = Path(temporary)/"EXP-SOFTWARECHECK-000000"/"runs"/"RUN-SOFTWARECHECK-000001"
            other.mkdir()
            (other/"launch.json").write_text(json.dumps(launch))
            (other/"environment.json").write_text(json.dumps(environment))
            with self.assertRaisesRegex(ValueError, "run mismatch"):
                self.write(other)

    def test_invalid_start_timestamp_rejected(self):
        with tempfile.TemporaryDirectory(prefix="lattice-core-softwarecheck-") as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(ValueError, "timezone"):
                write_artifacts(self.result(), directory, 7, "2026-10-15T12:00:00",
                                time.monotonic(), time.process_time())
            self.assertFalse((directory/"manifest.yaml").exists())


if __name__ == "__main__":
    unittest.main()
