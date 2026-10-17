"""Small-field and mocked engineering controls; never launches wide ideals."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sage.all import EllipticCurve, GF, PolynomialRing

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import execute
import verify_run


class LauncherControls(unittest.TestCase):
    def test_schedule_and_caps(self):
        rows = execute.schedule()
        self.assertEqual(len(rows), 27)
        self.assertEqual([r["kind"] for r in rows], ["positive"] * 6 + ["natural"] * 21)
        self.assertEqual({(r["arm"], r["m"]) for r in rows[6:]},
                         {(a, m) for a in ("coset", "random", "small_x") for m in range(2, 9)})
        self.assertEqual((execute.CALL_SECONDS, execute.RSS_CAP, execute.MODEL_CAP,
                          execute.PANEL_SECONDS, execute.START_FREE, execute.CONTINUE_FREE,
                          execute.SCRATCH_CAP),
                         (300, 8*1024**3, 64, 4*3600, 16*1024**3,
                          8*1024**3, 8*1024**3))
        with tempfile.TemporaryDirectory(prefix="icperf-prime63-admission-", dir=execute.SCRATCH) as temp:
            request = Path(temp) / "wide-request.json"
            request.write_text('{"p":"4503599627370497","variables":["x"],"equations":[]}')
            argv = ["execute.py", "--worker-request", str(request),
                    "--worker-output", str(Path(temp) / "out.json")]
            with patch.object(sys, "argv", argv), self.assertRaisesRegex(ValueError, "approved experiment packet"):
                execute.main()

    def test_pre_variety_distinct_and_repeated(self):
        R = PolynomialRing(GF(101), names=("x",), order="degrevlex")
        x = R.gen()
        distinct = R.one()
        for k in range(65):
            distinct *= x-k
        for polynomial, label in [(distinct, "65_distinct"), (x**65, "65_multiplicity")]:
            I = R.ideal([polynomial])
            count, capped = execute.standard_monomial_count(I.groebner_basis(), R)
            self.assertEqual((count, capped), (65, True), label)
            # The production worker returns here; neither control calls variety.
        I64 = R.ideal([distinct.quo_rem(x-64)[0]])
        self.assertEqual(execute.standard_monomial_count(I64.groebner_basis(), R), (64, False))
        for poly in (distinct, x**65):
            terms = [{"coefficient": int(poly[e]) % 101,
                      "powers": [[0, e]] if e else []}
                     for e in range(poly.degree() + 1) if poly[e]]
            request = {"p": "101", "variables": ["x", "y"],
                       "equations": [terms, [{"coefficient": 1, "powers": [[1, 1]]}]]}
            result = execute.worker(request)
            self.assertEqual(result["status"], "model_cap_censored")
            self.assertFalse(result["variety_called"])

    def test_small_field_certificate_and_false_objects(self):
        p = 101
        E = EllipticCurve(GF(p), [2, 3])
        pts = [q for q in E.points() if not q.is_zero() and int(q[1]) != 0]
        pair = next((a, b) for a in pts for b in pts
                    if int(a[0]) != int(b[0]) and not (a+b).is_zero()
                    and a-b != a+b)
        a, b = pair
        target = a+b
        xa, xb = int(a[0]), int(b[0])
        system = {"curve": {"p": p, "a": 2, "b": 3}, "p": str(p),
                  "arm": "random", "m": 2, "base_points": [[xa, int(a[1])], [xb, int(b[1])]],
                  "base_parameters": {}, "target_point": [int(target[0]), int(target[1])],
                  "variables": ["x1", "x2"],
                  "equations": [[{"coefficient": 1, "powers": [[0, 1]]},
                                  {"coefficient": (-xa) % p, "powers": []}],
                                 [{"coefficient": 1, "powers": [[1, 1]]},
                                  {"coefficient": (-xb) % p, "powers": []}]]}
        root = {"variables": {"x1": str(xa), "x2": str(xb)}}
        valid = verify_run.verify_explicit(system, root, [int(a[1]), int(b[1])])
        self.assertTrue(valid["accepted"])
        self.assertTrue(verify_run.verify_root(system, root)["accepted"])
        self.assertFalse(verify_run.verify_root(system, {"point": [xa, xb]})["accepted"])
        self.assertFalse(verify_run.verify_root(system, {"variables": {"x1": str((xa+1)%p), "x2": str(xb)}})["accepted"])
        self.assertFalse(verify_run.verify_explicit(system, root, [(-int(a[1])) % p, int(b[1])])["accepted"])
        # These signs sum to -target and therefore match target x only.
        self.assertEqual(verify_run.verify_explicit(system, root,
                         [(-int(a[1])) % p, (-int(b[1])) % p])["reason"],
                         "full_target_mismatch")
        changed = dict(system, target_point=[int(a[0]), int(a[1])])
        self.assertFalse(verify_run.verify_root(changed, root)["accepted"])
        nonmember = dict(system, base_points=[[xb, int(b[1])]])
        self.assertFalse(verify_run.verify_root(nonmember, root)["accepted"])
        # Construct a nonlifting x in the allowed x set with a matching
        # polynomial root; the checker must reject at Sage x-lifting.
        bad_x = next(x for x in range(1, p) if not E.lift_x(GF(p)(x), all=True))
        coset = dict(system, arm="coset", base_parameters={"d": p-1, "coset": 1},
                     base_points=[[bad_x, 0], [xb, int(b[1])]],
                     equations=[[{"coefficient": 1, "powers": [[0, 1]]},
                                 {"coefficient": (-bad_x) % p, "powers": []}],
                                system["equations"][1]])
        bad_root = {"variables": {"x1": str(bad_x), "x2": str(xb)}}
        self.assertEqual(verify_run.verify_root(coset, bad_root)["reason"], "nonlifting_x")

    def test_mock_panel_raw_coverage_and_stops(self):
        scratch = execute.SCRATCH
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="icperf-prime63-mock-", dir=scratch) as temp:
            root = Path(temp)
            panel = root / "panel"
            def fake_supervise(command, env, stdout, stderr, deadline, **kwargs):
                stdout.write_text("mocked worker\n")
                stderr.write_text("")
                response = stdout.parent / "response.json"
                if stdout.parent.name.startswith("natural-"):
                    response.write_text('{"status":"ok","root_count":0,"roots":[]}\n')
                else:
                    response.write_text('{"status":"model_cap_censored","roots":[],"variety_called":false}\n')
                return {"stop": "exited", "exit_code": 0, "command": command,
                        "started_utc": "mock", "ended_utc": "mock", "wall_seconds": 0,
                        "cpu_user_seconds": 0, "cpu_system_seconds": 0,
                        "peak_tree_rss_bytes_sampled": 0, "peak_scratch_bytes_sampled": 0,
                        "minimum_free_bytes_sampled": shutil.disk_usage(scratch).free,
                        "poll_seconds": execute.POLL_SECONDS,
                        "stdout_sha256": execute.sha(stdout), "stderr_sha256": execute.sha(stderr)}
            with patch.object(execute, "supervise", side_effect=fake_supervise):
                receipt = execute.create_panel({"task_id": "TASK-20261017-4d8c00",
                                                "_approval_packet_path": "/mock/approved-packet.json"}, panel)
            self.assertEqual((receipt["attempted"], receipt["unattempted"]), (27, 0))
            print(json.dumps({"control": "mock_27_schedule", "attempted": receipt["attempted"],
                              "unattempted": receipt["unattempted"]}, sort_keys=True))
            self.assertEqual(verify_run.verify_raw_archive(panel)["status"], "pass")
            self.assertEqual(verify_run.verify_panel(panel, execute.schedule())["cells"], 27)
            stdout = panel / "coset-m2" / "stdout.log"
            raw = stdout.read_bytes()
            stdout.unlink()
            with self.assertRaisesRegex(ValueError, "missing or extra raw file"):
                verify_run.verify_raw_archive(panel)
            stdout.write_bytes(raw)
            receipt_path = panel / "receipt.json"
            old_receipt = receipt_path.read_text()
            altered = json.loads(old_receipt)
            altered["raw_files"][0]["sha256"] = "0" * 64
            receipt_path.write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "raw digest mismatch"):
                verify_run.verify_raw_archive(panel)
            receipt_path.write_text(old_receipt)
            response = panel / "natural-coset-m2" / "response.json"
            old_response = response.read_text()
            response.write_text('{"status":"ok","root_count":1,"roots":[]}\n')
            # Raw manifest must first be amended in a mock-only test to reach
            # the semantic root-count check.
            altered = json.loads(old_receipt)
            blob = response.read_bytes()
            entry = next(r for r in altered["raw_files"] if r["path"] == "natural-coset-m2/response.json")
            entry.update(sha256=hashlib.sha256(blob).hexdigest(), bytes=len(blob))
            next(r for r in altered["cells"] if r["cell"] == "natural-coset-m2")["response_sha256"] = entry["sha256"]
            with tarfile.open(panel / "raw.tar.gz", "w:gz") as tar:
                for row in altered["raw_files"]:
                    tar.add(panel / row["path"], arcname=row["path"])
            altered["raw_tar_sha256"] = execute.sha(panel / "raw.tar.gz")
            receipt_path.write_text(json.dumps(altered))
            with self.assertRaisesRegex(ValueError, "root_count"):
                verify_run.verify_panel(panel, execute.schedule())
            response.write_text(old_response)
            stopped = root / "stopped"
            def invalid_supervise(command, env, stdout, stderr, deadline, **kwargs):
                stdout.write_text("invalid control\n")
                stderr.write_text("")
                return {"stop": "exited", "exit_code": 1, "command": command,
                        "started_utc": "mock", "ended_utc": "mock", "wall_seconds": 0,
                        "cpu_user_seconds": 0, "cpu_system_seconds": 0,
                        "peak_tree_rss_bytes_sampled": 0, "peak_scratch_bytes_sampled": 0,
                        "minimum_free_bytes_sampled": shutil.disk_usage(scratch).free,
                        "poll_seconds": execute.POLL_SECONDS,
                        "stdout_sha256": execute.sha(stdout), "stderr_sha256": execute.sha(stderr)}
            with patch.object(execute, "supervise", side_effect=invalid_supervise):
                receipt = execute.create_panel({"task_id": "TASK-20261017-4d8c00",
                                                "_approval_packet_path": "/mock/approved-packet.json"}, stopped)
            self.assertEqual((receipt["attempted"], receipt["unattempted"]), (1, 26))
            print(json.dumps({"control": "mock_fail_closed", "attempted": receipt["attempted"],
                              "unattempted": receipt["unattempted"]}, sort_keys=True))
            self.assertTrue(all(not r["attempted"] for r in receipt["cells"][1:]))

    def test_actual_small_worker_and_supervisor_timeout(self):
        scratch = execute.SCRATCH
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="icperf-prime63-small-", dir=scratch) as temp:
            d = Path(temp)
            req = {"p": "101", "variables": ["x", "y"],
                   "equations": [[{"coefficient": 1, "powers": [[0, 2]]},
                                  {"coefficient": 100, "powers": []}],
                                 [{"coefficient": 1, "powers": [[1, 1]]}]]}
            request, response, stdout, stderr = [d / n for n in ("request.json", "response.json", "stdout.log", "stderr.log")]
            request.write_text(json.dumps(req))
            env = dict(__import__("os").environ, DOT_SAGE=str(scratch / "sage"), TMPDIR=str(scratch / "tmp"))
            for name in ("sage", "tmp"):
                (scratch / name).mkdir(exist_ok=True)
            command = [str(execute.SAGE), "-python", str(HERE / "execute.py"),
                       "--worker-request", str(request), "--worker-output", str(response)]
            outcome = execute.supervise(command, env, stdout, stderr, __import__("time").monotonic()+120)
            self.assertEqual(outcome["stop"], "exited")
            self.assertEqual(outcome["exit_code"], 0)
            self.assertEqual(read_json(response)["root_count"], 2)
            print(json.dumps({"control": "small_field_worker", "supervisor": outcome}, sort_keys=True))
            sleepout, sleeperr = d / "sleep.out", d / "sleep.err"
            outcome = execute.supervise([sys.executable, "-c", "import time;time.sleep(10)"],
                                         env, sleepout, sleeperr, __import__("time").monotonic()+0.6)
            self.assertEqual(outcome["stop"], "timeout_censored")
            print(json.dumps({"control": "timeout_guard", "supervisor": outcome}, sort_keys=True))


def read_json(path):
    return json.loads(path.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
