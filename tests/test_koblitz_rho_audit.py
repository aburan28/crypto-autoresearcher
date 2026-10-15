from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.koblitz_rho_audit import AuditError, audit_document, main


ROOT = Path(__file__).resolve().parents[1]
NIST_AUDIT = ROOT / "research/endosweep_nist_20261006/nist.json"


class KoblitzRhoAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(NIST_AUDIT.read_text())

    def test_all_five_nist_k_curves_certify_exact_signed_tau_orbits(self) -> None:
        result = audit_document(self.document)
        self.assertTrue(result["all_consistency_checks_pass"])
        self.assertEqual([row["field_degree_m"] for row in result["curves"]], [163, 233, 283, 409, 571])
        for row in result["curves"]:
            m = row["field_degree_m"]
            self.assertEqual(row["tau"]["action_order"], m)
            self.assertEqual(row["tau"]["signed_action_order"], 2 * m)
            self.assertIn("archived prime-subgroup", row["tau"]["free_on_nonzero_prime_order_subgroup"])

        model = {row["curve"]: row["random_map_model"] for row in result["curves"]}
        self.assertAlmostEqual(model["K-163"]["signed_tau_gain_vs_negation_bits"], 3.674364, places=6)
        self.assertAlmostEqual(model["K-571"]["signed_tau_gain_vs_negation_bits"], 4.578673, places=6)
        self.assertAlmostEqual(
            model["K-163"]["conditional_negation_only_endpoint_max_step_cost_ratio_vs_source_signed_tau"],
            0.078326,
            places=6,
        )
        for row in model.values():
            self.assertAlmostEqual(
                row["signed_tau_gain_vs_plain_bits"] - row["signed_tau_gain_vs_negation_bits"],
                0.5,
                places=12,
            )
            self.assertNotIn("negation_only_endpoint_max_step_cost_ratio", row)

    def test_cli_binds_source_digest_and_labels_scope(self) -> None:
        expected_sha = hashlib.sha256(NIST_AUDIT.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "audit.json"
            markdown_out = Path(tmp) / "audit.md"
            self.assertEqual(
                main(
                    [
                        "--input",
                        str(NIST_AUDIT),
                        "--json-out",
                        str(json_out),
                        "--markdown-out",
                        str(markdown_out),
                    ]
                ),
                0,
            )
            result = json.loads(json_out.read_text())
            self.assertEqual(result["source"]["sha256"], expected_sha)
            self.assertIn("archived booleans", result["source"]["limitations"])
            self.assertIn("derived consistency audit", markdown_out.read_text())

    def test_tampered_tau_eigenvalue_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.document)
        tampered["curves"]["nist/K-163"]["tau"]["eigenvalue"] = "0x1"
        with self.assertRaisesRegex(AuditError, "eigenvalue does not satisfy"):
            audit_document(tampered)

    def test_failed_archived_point_check_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.document)
        tau = tampered["curves"]["nist/K-283"]["tau"]
        tau["checks"]["tau(G)=[lambda]G"] = False
        with self.assertRaisesRegex(AuditError, r"tau\(G\)"):
            audit_document(tampered)


if __name__ == "__main__":
    unittest.main()
