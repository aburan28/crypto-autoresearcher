"""Mechanical tests use the already-known F11/order13 fixture, never new panels."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from collections import Counter

import cohort


def doc():
    return {"schema": cohort.EXCLUSION_SCHEMA, "curve_keys": []}


def fixture_plan(status="draft"):
    return {"experiment_id": "software-fixture", "status": status,
            "cohort": {"seed_hex": "00" * 32, "max_point_sampling_attempts": 8,
             "strata": [{"id": "unit", "curve_count": 1, "p_min": 11, "p_max": 11,
                         "target_order": 13, "target_mode": "all_nonidentity", "max_proposals": 2}]}}


class Feed:
    def __init__(self, values): self.values = iter(values)
    def randbelow(self, bound):
        value = next(self.values)
        if not 0 <= value < bound: raise AssertionError((value, bound))
        return value


class CohortTests(unittest.TestCase):
    def test_describe_is_draw_and_census_free_and_counts_fixed_schedule(self):
        plan = fixture_plan()
        with patch.object(cohort.secrets, "token_hex", side_effect=AssertionError("entropy forbidden")), \
             patch.object(cohort, "Stream", side_effect=AssertionError("draw forbidden")), \
             patch.object(cohort, "point_count", side_effect=AssertionError("census forbidden")):
            result = cohort.describe_plan(plan)
        self.assertEqual(result["fixture_count_planned"], 1)
        self.assertEqual(result["target_cases_planned"], 12)
        self.assertEqual(result["cohort_draws"], 0)
        self.assertFalse(result["measurement_started"])

    def test_config_refuses_ambiguous_exact_count_and_composite_order(self):
        plan = fixture_plan()
        plan["cohort"]["strata"][0]["target_count"] = 13
        with self.assertRaisesRegex(ValueError, "r-1"): cohort.describe_plan(plan)
        plan = fixture_plan()
        plan["cohort"]["strata"][0]["target_order"] = 25
        with self.assertRaisesRegex(ValueError, "odd prime"): cohort.describe_plan(plan)

    def test_config_refuses_duplicate_strata_and_invalid_interval(self):
        plan = fixture_plan()
        plan["cohort"]["strata"].append(dict(plan["cohort"]["strata"][0]))
        with self.assertRaisesRegex(ValueError, "unique"): cohort.describe_plan(plan)
        plan = fixture_plan()
        plan["cohort"]["strata"][0].update(p_min=13, p_max=14)
        with self.assertRaisesRegex(ValueError, "no p=3"): cohort.describe_plan(plan)

    def test_trial_division_and_known_character_census(self):
        counts = Counter()
        self.assertTrue(cohort.prime(13, counts))
        self.assertFalse(cohort.prime(1, counts))
        self.assertFalse(cohort.prime(9, counts))
        cache = cohort.ResidueCache(counts)
        self.assertEqual(cohort.point_count(11, 1, 6, cache, counts), 13)
        self.assertEqual(counts["cohort_point_count_x"], 11)
        self.assertEqual(counts["cohort_residue_table_square"], 5)
        cohort.point_count(11, 1, 6, cache, counts)
        self.assertEqual(counts["cohort_residue_cache_hit"], 1)
        self.assertEqual(counts["cohort_residue_table_square"], 5)

    def test_j_key_scaling_and_twist_collision_are_explicit(self):
        j = cohort.j_invariant(11, 1, 6)
        self.assertEqual(j, 6)
        self.assertEqual(j, cohort.j_invariant(11, 2**4 % 11, 6 * 2**6 % 11))
        self.assertEqual(j, cohort.j_invariant(11, 4, 4))
        with self.assertRaisesRegex(ValueError, "singular"): cohort.j_invariant(11, 0, 0)
        self.assertEqual(cohort.exclusion_keys({"schema": cohort.EXCLUSION_SCHEMA,
                                              "curve_keys": [{"p": 11, "j": 6}, {"p": 11, "j": 6}]}), {(11, 6)})

    def test_exact_target_census_is_coordinates_not_scalar_order(self):
        costs = Counter()
        points = cohort._all_points(11, 1, 6, cohort.ResidueCache(costs), costs)
        self.assertEqual(len(points), 12)
        self.assertEqual(points, sorted(points))
        self.assertEqual(points[0], (2, 4))
        self.assertNotIn(None, points)
        self.assertTrue(all((y*y-x*x*x-x-6) % 11 == 0 for x,y in points))
        self.assertEqual(costs["cohort_target_census_x"], 11)

    def test_point_sampler_rejects_nonresidues_and_obeys_sign(self):
        costs = Counter()
        self.assertEqual(cohort._sample_point(11, 1, 6, Feed([0, 2, 1]), costs, 3), (2, 7))
        self.assertEqual(costs["cohort_point_proposal"], 2)
        self.assertEqual(costs["cohort_point_nonresidue_rejection"], 1)
        with self.assertRaisesRegex(RuntimeError, "cap"):
            cohort._sample_point(11, 1, 6, Feed([0]), Counter(), 1)

    def test_stream_is_domain_separated_and_bounded(self):
        first = cohort.Stream(b"unit-only", "one", Counter())
        replay = cohort.Stream(b"unit-only", "one", Counter())
        other = cohort.Stream(b"unit-only", "two", Counter())
        a = [first.randbelow(101) for _ in range(20)]
        self.assertEqual(a, [replay.randbelow(101) for _ in range(20)])
        self.assertNotEqual(a, [other.randbelow(101) for _ in range(20)])
        self.assertTrue(all(0 <= x < 101 for x in a))
        with self.assertRaises(ValueError): first.randbelow(0)

    def test_generate_draft_and_existing_directory_refuse_before_nonce(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", side_effect=AssertionError("entropy forbidden")):
            path = Path(td) / "new"
            with self.assertRaisesRegex(ValueError, "frozen"):
                cohort.generate(fixture_plan(), path, exclusions_data=doc())
            self.assertFalse(path.exists())
            with self.assertRaises(FileExistsError):
                cohort.generate(fixture_plan("frozen"), td, exclusions_data=doc())

    def test_invalid_exclusion_schema_refuses_before_nonce(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", side_effect=AssertionError("entropy forbidden")):
            with self.assertRaisesRegex(ValueError, "exclusion schema"):
                cohort.generate(fixture_plan("frozen"), Path(td)/"new", exclusions_data={})

    def test_mocked_validity_shortfall_preserves_intents_and_zero_fixtures(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", return_value="ab"*32), \
             patch.object(cohort, "prime", side_effect=lambda n, costs: n == 13), \
             patch.object(cohort, "point_count", side_effect=AssertionError("future census forbidden")):
            # Mocked invalid-field branch; no new curve or scientific census.
            plan = fixture_plan("frozen")
            path = Path(td)/"cohort"
            result = cohort.generate(plan, path, exclusions_data=doc())
            self.assertEqual(result["generation_status"], "incomplete")
            self.assertEqual(result["fixtures"], [])
            rows = [json.loads(x) for x in (path/"cohort-history.jsonl").read_text().splitlines()]
            self.assertEqual([x["event"] for x in rows], ["proposal_intent", "proposal_result"] * 2)
            self.assertEqual([x["status"] for x in rows if x["event"]=="proposal_result"], ["nonprime_field"]*2)
            self.assertEqual(result["shortfalls"][0]["actual_fixtures"], 0)
            nonce = json.loads((path/"cohort-nonce.json").read_bytes())
            self.assertTrue(nonce["recorded_before_first_curve_draw"])
            completion = json.loads((path/"cohort-completion.json").read_bytes())
            self.assertEqual(completion["scientific_candidate_attempts"], 0)
            self.assertEqual(completion["history_sha256"], hashlib.sha256((path/"cohort-history.jsonl").read_bytes()).hexdigest())

    def test_accepted_known_fixture_software_branch_charges_and_retains_public_ids(self):
        # Existing published F11/order13 curve only. This is a mocked unit
        # fixture, not any prospective field/seed/cohort proposal.
        def fixed_stream(seed, domain, costs):
            return Feed([0,1,6])
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", return_value="cd"*32), \
             patch.object(cohort, "Stream", side_effect=fixed_stream), \
             patch.object(cohort, "point_count", return_value=13), \
             patch.object(cohort, "_sample_point", return_value=(2,7)):
            path = Path(td)/"cohort"
            result = cohort.generate(fixture_plan("frozen"), path, exclusions_data=doc())
            self.assertEqual(result["generation_status"], "complete")
            self.assertEqual(result["target_cases"], 12)
            self.assertEqual(result["fixtures"][0]["panel"], "exact")
            self.assertEqual(result["fixtures"][0]["base"], [2,7])
            targets = result["fixtures"][0]["targets"]
            self.assertEqual(len({t["target_id"] for t in targets}), 12)
            self.assertTrue(result["fixtures"][0]["generation_certificate"]["base_r_multiple_is_identity"])
            self.assertFalse(result["scalar_truth_generated"])
            self.assertEqual(result["plan_canonical_sha256"], hashlib.sha256(cohort.canonical(fixture_plan("frozen"))).hexdigest())
            costs = json.loads((path/"cohort-costs.json").read_bytes())
            self.assertGreater(costs["base_order_check_counts"]["group_add_call"], 0)

    def test_partial_known_fixture_prefix_is_retained_without_extension(self):
        def fixed_stream(seed, domain, costs):
            return Feed([0,1,6,0,1,6])
        plan = fixture_plan("frozen")
        plan["cohort"]["strata"][0]["curve_count"] = 2
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", return_value="ef"*32), \
             patch.object(cohort, "Stream", side_effect=fixed_stream), \
             patch.object(cohort, "point_count", return_value=13), \
             patch.object(cohort, "_sample_point", return_value=(2,7)):
            path = Path(td)/"cohort"
            result = cohort.generate(plan, path, exclusions_data=doc())
            self.assertEqual(result["generation_status"], "incomplete")
            self.assertEqual(result["fixture_count"], 1)
            self.assertEqual(result["target_cases"], 12)
            self.assertEqual(result["shortfalls"][0]["actual_fixtures"], 1)
            rows = [json.loads(x) for x in (path/"cohort-history.jsonl").read_text().splitlines()]
            self.assertEqual([x["status"] for x in rows if x["event"]=="proposal_result"], ["accepted", "prior_or_current_field_j_key"])
            self.assertEqual(result["generation_failures"][0]["proposal_cap"], 2)

    def test_excluded_field_never_reaches_point_census(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cohort.secrets, "token_hex", return_value="99"*32), \
             patch.object(cohort, "point_count", side_effect=AssertionError("excluded census forbidden")):
            exclusion = doc()
            exclusion["excluded_fields"] = [11]
            result = cohort.generate(fixture_plan("frozen"), Path(td)/"cohort", exclusions_data=exclusion)
            self.assertEqual(result["generation_status"], "incomplete")
            self.assertEqual(result["fixtures"], [])
            rows = [json.loads(x) for x in (Path(td)/"cohort/cohort-history.jsonl").read_text().splitlines()]
            self.assertTrue(all(x["status"]=="excluded_prior_field" for x in rows if x["event"]=="proposal_result"))

    def test_cache_capacity_records_eviction(self):
        counts = Counter()
        cache = cohort.ResidueCache(counts, capacity=1)
        cache.get(7)
        cache.get(11)
        self.assertEqual(cache.peak_bytes, 11)
        self.assertEqual(counts["cohort_residue_cache_eviction"], 1)


if __name__ == "__main__": unittest.main()
