from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ROOT = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-NORM-RANK-001"
VERIFIER_PATH = EXPERIMENT_ROOT / "src" / "verify_tt_norm_rank.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("tt_norm_rank_verifier_tests", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load TT norm-rank verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VERIFY = load_verifier()


class TTNormRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_record = json.loads(
            (EXPERIMENT_ROOT / "instance-manifest-v1.json").read_text(encoding="utf-8")
        )
        cls.matrix_record = json.loads(
            (EXPERIMENT_ROOT / "execution-matrix-v3.json").read_text(encoding="utf-8")
        )
        cls.mutation_record = json.loads(
            (EXPERIMENT_ROOT / "mutation-manifest-v2.json").read_text(encoding="utf-8")
        )

    def test_manifest_and_v3_traffic_records_replay(self) -> None:
        audited = VERIFY.audit_manifest(self.manifest_record)
        self.assertEqual([row["curve_id"] for row in audited], ["C08", "C10", "C12", "C14", "C15", "C17"])
        matrix = VERIFY.audit_execution_matrix(self.matrix_record)
        self.assertEqual(
            matrix["aggregate_counts"]["rank_logical_traffic_upper_bound_base_field_word_equivalents"],
            587_622_372,
        )
        mutations = VERIFY.audit_mutation_manifest(self.mutation_record)
        self.assertEqual((mutations["control_count"], mutations["mutation_count"]), (6, 15))

    def test_independent_rcb_handles_identity_inverse_and_doubling(self) -> None:
        instance = self.manifest_record["manifest"]["instances"][0]
        p = instance["field"]["p"]
        a = instance["curve"]["a"]
        b = instance["curve"]["b"]
        affine = [tuple(row["affine"]) for row in instance["registries"]["random_unique"]]
        affine += [None, VERIFY.affine_neg(affine[0], p)]
        projective = [VERIFY.affine_to_projective(point) for point in affine]
        for left_index, left in enumerate(projective):
            for right_index, right in enumerate(projective):
                output = VERIFY.rcb_combine(left, right, p, a, b)
                self.assertTrue(VERIFY.projective_on_curve(output, p, a, b))
                self.assertEqual(
                    VERIFY.projective_to_affine(output, p),
                    VERIFY.affine_add(affine[left_index], affine[right_index], p, a),
                )

    def test_controls_have_frozen_asymmetric_profiles_and_traffic(self) -> None:
        controls = VERIFY.control_tensors()
        profiles = {row["id"]: row["cut_ranks"] for row in controls}
        self.assertEqual(profiles["CTRL-ASYMMETRIC"], [1, 2, 3, 4])
        self.assertEqual(profiles["CTRL-DENSE"], [4, 16, 16, 4])
        self.assertEqual(profiles["CTRL-NORM"], [2, 1, 1, 1])
        for control in controls:
            for rank in control["ranks"]:
                traffic = rank["accounting"]["traffic"]
                self.assertLessEqual(
                    traffic["total_field_words"], rank["accounting"]["upper"]["traffic"]
                )

    def test_c08_semantics_source_span_and_rescaling(self) -> None:
        replay = VERIFY.recompute_baseline(
            self.manifest_record,
            self.matrix_record,
            self.mutation_record,
            development_curve_ids={"C08"},
        )
        self.assertEqual(replay["summary"]["semantic_cell_count"], 10)
        self.assertEqual(replay["summary"]["rank_job_count"], 68)
        for registry in replay["instances"][0]["registries"]:
            for cell in registry["cells"]:
                semantic = cell["semantic"]
                self.assertEqual(semantic["norm_mismatches"], 0)
                self.assertEqual(semantic["source_span_mismatches"], 0)
                self.assertEqual(semantic["zero_set_mismatches"], 0)
                self.assertEqual(semantic["rescaling_mismatches"], 0)

    def test_fp_rank_is_unchanged_after_scalar_extension(self) -> None:
        values = [
            (index * index + 7 * index + 3) % 239
            for index in range(3**5)
        ]
        embedded = [(value, 0) for value in values]
        for cut in range(1, 5):
            base_rank, _, _ = VERIFY.rank_fp_right_pivots(values, 3, cut, 239)
            extension_rank, _, _ = VERIFY.rank_fp2_right_pivots(
                embedded, 3, cut, 239, 7
            )
            self.assertEqual(base_rank, extension_rank)

    def test_frozen_mutation_detectors_reject_every_payload(self) -> None:
        replay = VERIFY.recompute_baseline(
            self.manifest_record,
            self.matrix_record,
            self.mutation_record,
            development_curve_ids={"C08"},
        )
        changed = "0" * 64
        payloads = {
            "M01-WRONG-B3": {"source": {"output_digest": changed}, "semantic": {"g_digest": changed, "h_digest": changed}},
            "M02-FLIP-GATE37": {"source": {"output_digest": changed}, "semantic": {"g_digest": changed, "h_digest": changed}},
            "M03-AFFINE-PRODUCER": {"source": {"output_digest": changed}, "semantic": {"g_digest": changed, "h_digest": changed}},
            "M04-ZERO-PROJECTIVE": {"source": {"invalid_projective_count": 1, "first_output": [0, 0, 0]}},
            "M05-WRONG-FROBENIUS": {"semantic": {"norm_mismatches": 1, "h_digest": changed}},
            "M06-G-SQUARED": {"semantic": {"norm_mismatches": 1, "h_digest": changed}},
            "M07-RANK-FIELD-PROVENANCE": {"rank_record": {"tensor": "h", "field": "F_p2"}},
            "M08-RAW-BOND-AS-RANK": {"rank_record": {"rank_kind": "raw_hadamard_product"}},
            "M09-REVERSE-CUTS": {"control_id": "CTRL-ASYMMETRIC", "reported_cut_ranks": [4, 3, 2, 1]},
            "M10-POSTSELECT-TARGET": {
                "selection": "post_observation_minimum_rank",
                "frozen_q00_target_id": "C08-Q-00",
                "candidate": {
                    "target_id": "postselected",
                    "label": "after",
                    "scalar": 1,
                },
            },
            "M11-DUPLICATE-PRIMARY": {
                "curve_id": "C08",
                "registry": "random_unique",
                "point_ids": ["a", "a"],
                "affine": [[1, 2], [1, 2]],
            },
            "M12-SHARED-VERIFIER-CODE": {"imports": ["generate_tt_norm_rank"]},
            "M13-OMIT-ENUMERATION-COST": {"accounting": {}},
            "M14-OMIT-MEMORY": {"accounting": {"canonical_storage": {}}},
            "M15-ASYMPTOTIC-LABEL": {"interpretation": "ASYMPTOTIC", "breakthrough_claim": True},
        }
        for mutation in self.mutation_record["mutation_manifest"]["mutations"]:
            detected, _ = VERIFY.detect_mutation(
                mutation["id"], payloads[mutation["id"]], replay, self.manifest_record
            )
            self.assertTrue(detected, mutation["id"])

    def test_verifier_does_not_import_the_producer(self) -> None:
        self.assertTrue(VERIFY.verifier_independence_audit()["valid"])


if __name__ == "__main__":
    unittest.main()
