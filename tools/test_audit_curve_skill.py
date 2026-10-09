"""Pin the cross-host audit-curve skill and its fail-closed contract."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CANONICAL = ROOT / ".claude" / "skills" / "audit-curve" / "SKILL.md"
ADAPTER = ROOT / ".agents" / "skills" / "audit-curve" / "SKILL.md"
TRANSFER = ROOT / ".claude" / "skills" / "transfer" / "SKILL.md"
ENDOMORPHISM_RULES = ROOT / "docs" / "endomorphism-rules.md"
KNOWLEDGE = ROOT / "knowledge" / "techniques" / "KN-TECH-6a2ef9.md"
REPORT_TEMPLATE = (
    ROOT / ".claude" / "skills" / "audit-curve" / "references"
    / "report-template.md"
)
RESEARCH_VISUALS = (
    ROOT / ".claude" / "skills" / "research-visuals" / "SKILL.md"
)


def frontmatter_value(path: Path, key: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    if match is None:
        raise AssertionError(f"{path} has no frontmatter {key}")
    return match.group(1)


class AuditCurveSkillTests(unittest.TestCase):
    def test_canonical_skill_and_report_contract_exist(self) -> None:
        self.assertTrue(CANONICAL.is_file(), f"missing {CANONICAL}")
        self.assertTrue(TRANSFER.is_file(), f"missing {TRANSFER}")
        self.assertTrue(
            ENDOMORPHISM_RULES.is_file(), f"missing {ENDOMORPHISM_RULES}"
        )
        self.assertTrue(KNOWLEDGE.is_file(), f"missing {KNOWLEDGE}")
        self.assertTrue(REPORT_TEMPLATE.is_file(), f"missing {REPORT_TEMPLATE}")
        self.assertEqual(frontmatter_value(CANONICAL, "name"), "audit-curve")
        body = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("knowledge/techniques/KN-TECH-6a2ef9.md", body)
        self.assertIn("references/report-template.md", body)
        self.assertIn(".claude/skills/transfer/SKILL.md", body)
        self.assertIn("docs/endomorphism-rules.md", body)

        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/audit-curve/SKILL.md", agents)
        self.assertIn(".claude/skills/transfer/SKILL.md", agents)
        self.assertIn("docs/endomorphism-rules.md", agents)
        self.assertIn("## Weak-curve and isogenous-representative audits", agents)

        report = REPORT_TEMPLATE.read_text(encoding="utf-8")
        for section in (
            "scope:",
            "instance:",
            "exact_checks:",
            "instrument_controls:",
            "attack_ledger:",
            "isogeny_paths:",
            "statistics:",
            "conclusion:",
            "subgroup_order_factorization: null",
            "generator_nonidentity:",
            "extension_orders_checked: []",
            "offline_work: null",
            "online_work: null",
            "indeterminate_samples: null",
            "false_negative_assessment: null",
            "adversarial_input_capability: null",
            "formula_compatible_companions: []",
            "singular_smooth_locus_checks: []",
            "fundamental_discriminant_D_K: null",
            "frobenius_order_conductor_f_pi: null",
            "endomorphism_order_conductor_f_E: null",
            "conductor_gap_index_g_pi_E: null",
            "volcano_levels: []",
            "inseparable_endomorphisms: []",
        ):
            self.assertIn(section, report)

    def test_host_adapter_delegates_to_canonical(self) -> None:
        self.assertTrue(ADAPTER.is_file(), f"missing {ADAPTER}")
        self.assertEqual(frontmatter_value(ADAPTER, "name"), "audit-curve")
        self.assertEqual(
            frontmatter_value(ADAPTER, "description"),
            frontmatter_value(CANONICAL, "description"),
        )
        body = ADAPTER.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/audit-curve/SKILL.md", body)
        self.assertIn("$run", body)

    def test_skill_fails_closed_and_scopes_weakness(self) -> None:
        body = CANONICAL.read_text(encoding="utf-8")
        for required in (
            "INDETERMINATE",
            "INVALID_INSTANCE",
            "CLASS_WEAK",
            "WEAK_REPRESENTATIVE_EXISTS",
            "SOURCE_TRANSFER_WEAK",
            "IMPLEMENTATION_WEAK",
            "NO_WEAKNESS_FOUND_WITHIN_SCOPE",
            "Never emit `SAFE` or `SECURE`",
        ):
            self.assertIn(required, body)
        self.assertIn("gcd(deg(phi), r) = 1", body)
        self.assertIn("gcd(q, ell) = 1", body)
        self.assertIn("pairing transfer `NOT_APPLICABLE`", body)
        self.assertIn("cyclic point of exact order `r`", body)
        self.assertIn("P != O", body)
        self.assertIn("Shor's algorithm", body)
        self.assertIn("1 - alpha^(1/n)", body)
        self.assertIn("validated detector", body)
        self.assertIn("unique-multiple argument", body)
        self.assertIn("planted positive and negative controls", body)
        self.assertIn("advisory secondary structural", body)
        self.assertIn("does not validate the primality of `p`", body)
        self.assertIn("research-visuals/SKILL.md", body)
        self.assertIn("formula-compatible companion", body)
        self.assertIn("companion is not an elliptic curve", body)
        self.assertIn("inherit a square-root DLP cost automatically", body)
        self.assertIn("t_m = t t_(m-1) - q t_(m-2)", body)
        self.assertIn("Frob_q^m", body)

        for required in (
            "Delta_pi = f_pi^2 D_K",
            "f_E | f_pi",
            "g_(pi,E)",
            "never copy `f_pi` into `f_E`",
            "horizontal",
            "ascending",
            "descending",
            "Koblitz `tau`",
            "inseparable",
            "N_vertical",
            "Do not convert `f_pi`",
        ):
            self.assertIn(required, body)

        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("formula-compatible", agents)
        self.assertIn("confirmation-only oracle", agents)

        knowledge = KNOWLEDGE.read_text(encoding="utf-8")
        self.assertIn("Follow the formulas beyond the named twist", knowledge)
        self.assertIn("singular parameter values", knowledge)
        self.assertIn("confirmation-only oracle", knowledge)
        self.assertIn(
            "does not prove that all of `E[ell]` is rational", knowledge
        )
        self.assertIn("`Frob_q^m` to act as the identity", knowledge)

        for required in (
            "Conductor and volcano accounting",
            "Current NIST-family evidence boundary",
            "P-224",
            "B-571",
            "does not generally certify the representative conductor `f_E`",
        ):
            self.assertIn(required, knowledge)

        loop_rules = ENDOMORPHISM_RULES.read_text(encoding="utf-8")
        for required in (
            "explicit endpoint isomorphism",
            "Matching `j`-invariants alone",
            "hat(phi) o phi = [deg(phi)]",
            "deg([n]) = n^2",
            "nonsquare degree",
            "characteristic-polynomial root alone is only a candidate",
            "mixed-degree ideal-class relations",
            "same mathematical map",
            "Variable-base",
            "known `k`",
            "KN-LIT-390",
        ):
            self.assertIn(required, loop_rules)

        visuals = RESEARCH_VISUALS.read_text(encoding="utf-8")
        for required in (
            "(D_K, f_pi, f_E)",
            "horizontal | ascending | descending | unresolved",
            "Koblitz `tau`",
        ):
            self.assertIn(required, visuals)

    def test_skill_does_not_create_a_second_execution_entry_point(self) -> None:
        body = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("public `run` entry point", body)
        self.assertIn("route that launch\nthrough `/run`", body)
        self.assertIn("Coordinator alone", body)

        plugin_skills = (
            ROOT / "plugins" / "crypto-autoresearcher-harness" / "skills"
        )
        extras = [
            path
            for path in plugin_skills.rglob("SKILL.md")
            if path != plugin_skills / "run" / "SKILL.md"
        ]
        self.assertEqual(extras, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
