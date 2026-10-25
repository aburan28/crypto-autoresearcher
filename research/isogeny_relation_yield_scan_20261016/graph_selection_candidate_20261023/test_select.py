"""Small synthetic controls for frozen-selection plumbing."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import discovery_select as candidate


def write(path: Path, value: dict | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((json.dumps(value, sort_keys=True) if isinstance(value, dict) else value) + "\n")


class SelectionTests(unittest.TestCase):
    def test_full_schedule_shape_with_synthetic_equal_yields(self) -> None:
        path = Path(__file__).resolve().parents[1] / "graph_schedule_20261023/discovery-arms.jsonl"
        schedule = [json.loads(line) for line in path.read_text().splitlines()]
        results = [{"arm_key": row["arm_key"], "stratum": row["stratum"],
                    "index": row["path_index"], "arm": row["base_rule"],
                    "j": row["model"]["j"], "target_count": row["discovery_targets"],
                    "useful_targets": 0, "coefficient_sha256": "c" * 64,
                    "base_root_sha256": "b" * 64, "target_root_sha256": "a" * 64,
                    "verifier_root_sha256": "e" * 64,
                    "commitment_sha256": ("d" if row["stratum"] == "P29" else "f") * 64}
                   for row in schedule]
        selected = candidate.nominate(schedule, results, b"C" * 32)
        self.assertEqual(len(schedule), 8206)
        self.assertEqual(len(selected["P29"]["control_indices_draw_order"]), 16)
        self.assertEqual(len(selected["P37"]["control_indices_draw_order"]), 8)
        self.assertNotEqual(selected["P29"]["commitment_sha256"],
                            selected["P37"]["commitment_sha256"])
        self.assertLessEqual(len(selected["P29"]["selected_vertices"]), 65)
        self.assertLessEqual(len(selected["P37"]["selected_vertices"]), 33)
        self.assertEqual(len(selected["P29"]["confirmation_arm_keys"]),
                         3 * len(selected["P29"]["selected_vertices"]))
        self.assertEqual(len(selected["P37"]["confirmation_arm_keys"]),
                         3 * len(selected["P37"]["selected_vertices"]))

    def test_tie_break_and_complete_coverage(self) -> None:
        original = candidate.EXPECTED
        candidate.EXPECTED = {"P29": {"vertices": 3, "quota": 8, "extreme_count": 1,
                                       "control_count": 1},
                              "P37": {"vertices": 2, "quota": 4, "extreme_count": 1,
                                       "control_count": 1}}
        try:
            schedule, results = [], []
            for stratum, count in (("P29", 3), ("P37", 2)):
                for index in range(count):
                    for arm in candidate.MAIN:
                        key = f"{stratum}-v{index:04d}-{arm}"
                        schedule.append({"arm_key": key, "stratum": stratum,
                                         "base_rule": arm, "path_index": index,
                                         "model": {"j": (7, 3, 5)[index]},
                                         "discovery_targets": 8 if stratum == "P29" else 4})
                        results.append({"arm_key": key, "stratum": stratum,
                                        "index": index, "arm": arm,
                                        "j": (7, 3, 5)[index],
                                        "target_count": 8 if stratum == "P29" else 4,
                                        "useful_targets": 2 if index != 2 else 0,
                                        "coefficient_sha256": "c" * 64,
                                        "base_root_sha256": "b" * 64,
                                        "target_root_sha256": "a" * 64,
                                        "verifier_root_sha256": "c" * 64,
                                        "commitment_sha256": ("d" if stratum == "P29" else "f") * 64})
            selected = candidate.nominate(schedule, results, b"C" * 32)
            self.assertEqual(selected["P29"]["extremes"]["low_x"]["top"], [1])
            self.assertEqual(selected["P29"]["extremes"]["low_x"]["bottom"], [2])
            self.assertEqual(len(selected["P29"]["confirmation_arm_keys"]) % 3, 0)
            results[-1]["coefficient_sha256"] = "e" * 64
            with self.assertRaisesRegex(ValueError, "paired target coefficient stream"):
                candidate.nominate(schedule, results, b"C" * 32)
            results[-1]["coefficient_sha256"] = "c" * 64
            results[-1]["commitment_sha256"] = "e" * 64
            with self.assertRaisesRegex(ValueError, "graph commitment differs within"):
                candidate.nominate(schedule, results, b"C" * 32)
            results[-1]["commitment_sha256"] = "f" * 64
            for result in results:
                if result["stratum"] == "P37":
                    result["commitment_sha256"] = "d" * 64
            with self.assertRaisesRegex(ValueError, "distinct graph strata reuse"):
                candidate.nominate(schedule, results, b"C" * 32)
            for result in results:
                if result["stratum"] == "P37":
                    result["commitment_sha256"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "coverage incomplete"):
                candidate.nominate(schedule, results[:-1], b"C" * 32)
            with self.assertRaisesRegex(ValueError, "identities differ"):
                candidate.nominate(schedule, results[:-1] + results[:1], b"C" * 32)
        finally:
            candidate.EXPECTED = original

    def test_supervisor_receipt_must_validate_and_bind_raw_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = {"specification": "experiments/EXP-ECTD-a1b2c3/specification.yaml"}
            trial = {"id": "P29-v0000-low_x", "run_id": "RUN-ECTD-d4e5f6"}
            row = {"arm_key": trial["id"], "stratum": "P29", "path_index": 0,
                   "base_rule": "low_x", "discovery_targets": 8,
                   "base_x_orbits": 1, "p": 19, "r": 19,
                   "generator": [0, 1], "model": {"a": 1, "b": 1, "j": 7}}
            directory = root / "experiments/EXP-ECTD-a1b2c3/runs/RUN-ECTD-d4e5f6"
            input_path = root / "prepared.txt"
            input_path.write_text("curve 19 1 1 19 2 8\nbase 0 0 1\nbase 1 0 18\n" +
                                  "".join(f"target {i} {i} 1 0 1\n" for i in range(8)))
            prepared_path = root / "prepared-manifest.json"
            write(prepared_path, {"input_sha256": candidate.sha(input_path),
                                  "seed_mode": "independent_verifier_root",
                                  "schedule_conformant": True, "j": 7,
                                  "stratum": "P29", "index": 0, "arm": "low_x",
                                  "target_count": 8, "generator": [0, 1],
                                  "base_root_sha256": "b" * 64,
                                  "target_root_sha256": "a" * 64,
                                  "verifier_root_sha256": "c" * 64,
                                  "commitment_sha256": "d" * 64})
            attempt = {"schema": "ectd.graph-arm-execution-attempt.v1",
                       "status": "completed_unreviewed", "mode": "scientific_trial",
                       "admission_sha256": "a" * 64,
                       "bindings": {"stratum": "P29", "index": 0, "arm": "low_x",
                                    "target_count": 8}}
            write(directory / "attempt/receipt.json", attempt)
            rank = {"status": "valid", "targets": 8, "useful_targets": 7,
                    "rank_increments": 3, "independent_ordered_count_match": True,
                    "rank_prefix": {"8": 3}}
            result = {"schema": "ectd.graph-trial-result.v1", "status": "completed_unreviewed",
                      "mode": "scientific_trial", "digests": {
                          "admission_sha256": "a" * 64,
                          "input_sha256": candidate.sha(input_path),
                          "prepared-manifest_sha256": candidate.sha(prepared_path)},
                      "attempt_receipt_sha256": candidate.sha(directory / "attempt/receipt.json"),
                      "prepared": {"stratum": "P29", "index": 0, "arm": "low_x",
                                   "stage": "discovery", "target_count": 8},
                      "rank_check": rank}
            write(directory / "raw-result.json", result)
            write(directory / "manifest.yaml", {
                "schema": "ectd.graph-trial-manifest.v1", "status": "completed_unreviewed",
                "subprocess_return_code": 0,
                "paths": {"input": str(input_path), "prepared-manifest": str(prepared_path)},
                "attempt_receipt_sha256": candidate.sha(directory / "attempt/receipt.json"),
                "raw_result_sha256": candidate.sha(directory / "raw-result.json")})
            write(directory / "check.stdout.log", {"status": "valid", "targets": 8,
                                                    "useful_targets": 7, "rank_increments": 3})
            write(directory / "check.stderr.log", "")
            artifacts = {name: candidate.sha(directory / name) for name in
                         ("raw-result.json", "manifest.yaml", "check.stdout.log", "check.stderr.log")}
            receipt = {"status": "output_validated", "returncode": 0, "check_returncode": 0,
                       "plan_sha256": "p" * 64, "trial_id": trial["id"],
                       "run_id": trial["run_id"], "artifact_sha256": artifacts}
            write(directory / "execution-receipt.json", receipt)
            observed = candidate.discover_one(root, plan, "p" * 64, row, trial)
            self.assertEqual((observed["useful_targets"], observed["rank_increments"]), (7, 3))
            result["rank_check"]["useful_targets"] = 8
            write(directory / "raw-result.json", result)
            with self.assertRaisesRegex(ValueError, "artifact digest differs"):
                candidate.discover_one(root, plan, "p" * 64, row, trial)


if __name__ == "__main__":
    unittest.main()
