"""Fixed development-only conformance/mutation tests; no research cohort run."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from verify_public import (
    ARMS, MASK64, SCHEMA, SCOPE, Checker, Curve, Fixture, Invalid, Setting, Target,
    fingerprint, load_fixtures, load_targets, prime, table_hash, verify,
)


def point(value):
    return {"x": 0 if value is None else value[0], "y": 0 if value is None else value[1], "infinity": value is None}


F = Fixture("fixed-F17", Curve(17, 2, 2), (5, 1), 19, 19)


def common(kind, arm="harvest"):
    return {"schema": SCHEMA, "scope": SCOPE, "row_kind": kind, "cell_id": "fixed-cell", "fixture": F.identifier, "replicate": 0, "arm": arm}


def fixture_targets(identifiers=("Q2",)):
    return {(F.identifier, 0, identifier): Target(F.identifier, 0, identifier, ordinal, F.curve.multiply(F.base, int(identifier[1:]))) for ordinal, identifier in enumerate(identifiers)}


def rows_success(arm="harvest", duplicate=False):
    initial = [(fingerprint(F.base), 1)]
    if arm == "static_filled":
        initial = sorted((fingerprint(F.curve.multiply(F.base, e)), e) for e in [1, 3, 6])
    setup = common("setup", arm) | {"status": "ready", "parameters": {"dp_bits": 0, "initial_chains": 1, "requested_build_chains": 1, "endpoint_cap": 3, "max_precomp_ops": 10000, "max_online_ops": 10000, "seed": 1, "threads": 1, "walks": 1, "early_abort": False}, "known_count": len(initial), "endpoint_cap": 3, "table_state_hash64": table_hash(initial)}
    target = fixture_targets()[(F.identifier, 0, "Q2")]
    trace = [setup] + [common("initial_endpoint", arm) | {"index": i, "fp": fp, "exponent": e} for i, (fp, e) in enumerate(initial)]
    if arm == "harvest":
        for index, a in enumerate([1, 1] if duplicate else [1, 4]):
            terminal = F.curve.add(target.point, F.curve.multiply(F.base, a))
            trace.append(common("lookup") | {"target_id": target.identifier, "target_ordinal": 0, "attempt": index + 1, "fp": fingerprint(terminal), "offset_a": a, "lookup_begin": 0, "lookup_end_exclusive": 1, "known_count": 1, "pending_count": index, "endpoint_cap": 3})
            trace.append(common("terminal") | {"target_id": target.identifier, "target_ordinal": 0, "attempt": index + 1, "reason": "unmatched_dp", "point": point(terminal), "offset_a": a, "fp": fingerprint(terminal), "pending_slot": index + 1, "known_count": 1, "pending_count": index + 1, "endpoint_cap": 3})
        trace.append(common("lookup") | {"target_id": target.identifier, "target_ordinal": 0, "attempt": 3, "fp": initial[0][0], "offset_a": 18, "lookup_begin": 0, "lookup_end_exclusive": 1, "known_count": 1, "pending_count": 2, "endpoint_cap": 3})
        trace.append(common("lookup_witness") | {"target_id": target.identifier, "target_ordinal": 0, "attempt": 3, "entry_index": 0, "fp": initial[0][0], "exponent": 1, "offset_a": 18, "candidate_scalar": 2, "public_equation_checked": True, "verified": True, "known_count": 1, "pending_count": 2, "endpoint_cap": 3})
        trace.append(common("verified_solution") | {"target_id": target.identifier, "target_ordinal": 0, "point": point(target.point), "verified_scalar": 2, "public_equation_checked": True, "known_count": 1, "pending_count": 2, "endpoint_cap": 3})
        accepted = []
        for index, a in enumerate([1, 1] if duplicate else [1, 4]):
            e = (2 + a) % F.order
            fp = fingerprint(F.curve.multiply(F.base, e))
            take = e not in {v for _, v in initial + accepted}
            trace.append(common("harvest_proposal") | {"target_id": target.identifier, "target_ordinal": 0, "pending_slot": index + 1, "fp": fp, "exponent": e, "accepted": take, "known_count": 1, "pending_count": 2, "endpoint_cap": 3})
            if take:
                accepted.append((fp, e))
        trace.append(common("harvest_commit_ready") | {"target_id": target.identifier, "target_ordinal": 0, "accepted_count": len(accepted), "known_count": 1, "pending_count": 2, "endpoint_cap": 3})
        final = sorted(initial + accepted)
        reuse = {"known_before": 1, "known_after": len(final), "capacity": 3, "pending_peak": 2, "unmatched_dp": 2, "chain_limit_restarts": 0, "staged": 2, "capacity_rejections": 0, "bucket_candidates_verified": 1, "rejected_bucket_witnesses": 0, "proposed": 2, "inserted": len(accepted), "duplicates": 2 - len(accepted), "rolled_back": 0}
    else:
        final, reuse = initial, {}
    trace.append(common("target", arm) | {"target_id": target.identifier, "target_ordinal": 0, "point": point(target.point), "status": "solved", "upstream_status": 0, "verified_scalar": 2, "public_equation_checked": True, "known_count": len(final), "pending_count": 0, "endpoint_cap": 3, "table_state_hash64": table_hash(final), "harvest_committed": arm == "harvest", "reuse": reuse})
    return trace


def check(rows, arm="harvest", targets=None):
    checker = Checker({F.identifier: F}, fixture_targets() if targets is None else targets, {arm})
    for row in rows:
        checker.ingest(row)
    return checker.finish()


class ArithmeticTests(unittest.TestCase):
    def test_fixed_group_sequence(self):
        expected = [None, (5, 1), (6, 3), (10, 6), (3, 1), (9, 16), (16, 13), (0, 6), (13, 7), (7, 6), (7, 11), (13, 10), (0, 11), (16, 4), (9, 1), (3, 16), (10, 11), (6, 14), (5, 16), None]
        self.assertEqual([F.curve.multiply(F.base, n) for n in range(20)], expected)
        for n in range(19):
            self.assertEqual(F.curve.add(expected[n], F.base), expected[n + 1])

    def test_domain(self):
        F.validate()
        self.assertTrue(prime(1048573))
        self.assertFalse(prime(1048575))
        with self.assertRaises(Invalid):
            Fixture("composite", Curve(15, 2, 2), (5, 1), 19, 19).validate()
        with self.assertRaises(Invalid):
            Fixture("bad-r", F.curve, F.base, 18, 18).validate()
        with self.assertRaises(Invalid):
            Fixture("singular", Curve(17, 0, 0), (0, 0), 19, 19).validate()
        with self.assertRaises(Invalid):
            Fixture("wrong-order", F.curve, F.base, 17, 17).validate()
        with self.assertRaises(Invalid):
            F.curve.point({"x": 1, "y": 0, "infinity": True})
        with self.assertRaises(Invalid):
            F.curve.point({"x": 5, "y": 2, "infinity": False})
        with self.assertRaises(Invalid):
            F.curve.point({"x": 5, "y": 1, "infinity": 0})


class TraceTests(unittest.TestCase):
    def mutate_rejected(self, kind, field, value):
        rows = rows_success()
        next(row for row in rows if row["row_kind"] == kind)[field] = value
        with self.assertRaises(Invalid):
            check(rows)

    def test_complete_success(self):
        summary = check(rows_success())
        self.assertEqual(summary["target_arm_cases"], 1)
        self.assertEqual(summary["promotions_checked"], 2)
        self.assertFalse(summary["native_cost_counters_verified"])

    def test_duplicate_pending_endpoint(self):
        self.assertEqual(check(rows_success(duplicate=True))["status"], "public_equations_and_trace_pass")

    def test_static_small(self):
        check(rows_success("static_small"), "static_small")

    def test_disabled_retention(self):
        check(rows_success("harvest_disabled"), "harvest_disabled")

    def test_static_full(self):
        check(rows_success("static_full"), "static_full")

    def test_static_filled(self):
        check(rows_success("static_filled"), "static_filled")

    def test_underfilled_ready_reference_rejected(self):
        rows = rows_success("static_small")
        for row in rows:
            row["arm"] = "static_filled"
        with self.assertRaises(Invalid):
            check(rows, "static_filled")

    def test_underfilled_censored_setup_preserved(self):
        rows = rows_success("static_small")
        for row in rows:
            row["arm"] = "static_filled"
        rows[0]["status"] = "censored"
        rows[-1].update({"status": "censored", "upstream_status": 4, "verified_scalar": None, "public_equation_checked": False})
        self.assertEqual(check(rows, "static_filled")["producer_status_counts"]["censored"], 1)

    def test_rho_reference(self):
        rows = rows_success("rho_reference")
        rows = [row for row in rows if row["row_kind"] != "initial_endpoint"]
        for row in rows:
            row["known_count"] = 0
            row["table_state_hash64"] = 0
        check(rows, "rho_reference")

    def test_settings_seed_bound(self):
        setting = Setting("fixed-cell", F.identifier, 0, 0, 1, 3, 10000, 10000, 1)
        checker = Checker({F.identifier: F}, fixture_targets(), {"harvest"}, {setting.cell_id: setting})
        rows = rows_success()
        rows[0]["parameters"]["seed"] = 2
        with self.assertRaises(Invalid):
            for row in rows:
                checker.ingest(row)

    def test_multiple_stateful_cells_rejected(self):
        checker = Checker({F.identifier: F}, fixture_targets(), {"harvest"})
        setup = rows_success()[0]
        checker.ingest(setup)
        setup = copy.deepcopy(setup)
        setup["cell_id"] = "second-cell"
        with self.assertRaises(Invalid):
            checker.ingest(setup)

    def test_false_equation_claim_without_scalar(self):
        self.mutate_rejected("target", "verified_scalar", None)

    def test_status_code_preserved(self):
        self.mutate_rejected("target", "upstream_status", 4)

    def test_wrong_final_scalar(self):
        self.mutate_rejected("target", "verified_scalar", 3)

    def test_congruent_but_noncanonical_scalar(self):
        self.mutate_rejected("target", "verified_scalar", 21)

    def test_wrong_terminal_offset(self):
        self.mutate_rejected("terminal", "offset_a", 2)

    def test_wrong_terminal_point(self):
        self.mutate_rejected("terminal", "point", point((3, 1)))

    def test_wrong_initial_log(self):
        self.mutate_rejected("initial_endpoint", "exponent", 2)

    def test_wrong_promoted_log(self):
        self.mutate_rejected("harvest_proposal", "exponent", 4)

    def test_before_public_verification(self):
        rows = rows_success()
        i = next(i for i, row in enumerate(rows) if row["row_kind"] == "verified_solution")
        j = next(i for i, row in enumerate(rows) if row["row_kind"] == "harvest_proposal")
        rows[i], rows[j] = rows[j], rows[i]
        with self.assertRaises(Invalid):
            check(rows)

    def test_pending_search_range(self):
        self.mutate_rejected("lookup", "lookup_end_exclusive", 2)

    def test_boolean_lookup_boundary_rejected(self):
        self.mutate_rejected("lookup", "lookup_end_exclusive", True)

    def test_pending_lookup_index(self):
        self.mutate_rejected("lookup_witness", "entry_index", 1)

    def test_lookup_missing(self):
        rows = rows_success()
        del rows[2]
        with self.assertRaises(Invalid):
            check(rows)

    def test_wrong_lookup_candidate(self):
        self.mutate_rejected("lookup_witness", "candidate_scalar", 3)

    def test_wrong_verification_flag(self):
        self.mutate_rejected("lookup_witness", "verified", False)

    def test_capacity_violation(self):
        self.mutate_rejected("terminal", "endpoint_cap", 1)

    def test_bad_pending_slot(self):
        self.mutate_rejected("terminal", "pending_slot", 3)

    def test_drop_before_full(self):
        self.mutate_rejected("terminal", "pending_slot", None)

    def test_bad_pending_metadata(self):
        self.mutate_rejected("terminal", "pending_count", 0)

    def test_duplicate_marked_accepted(self):
        rows = rows_success(duplicate=True)
        proposals = [row for row in rows if row["row_kind"] == "harvest_proposal"]
        proposals[1]["accepted"] = True
        with self.assertRaises(Invalid):
            check(rows)

    def test_partial_commit(self):
        self.mutate_rejected("harvest_commit_ready", "accepted_count", 1)

    def test_final_hash_mutation(self):
        self.mutate_rejected("target", "table_state_hash64", 0)

    def test_missing_target(self):
        with self.assertRaises(Invalid):
            check(rows_success()[:-1])

    def test_missing_coverage(self):
        with self.assertRaises(Invalid):
            check(rows_success(), targets=fixture_targets(("Q2", "Q3")))

    def test_duplicate_target(self):
        rows = rows_success()
        rows.append(copy.deepcopy(rows[-1]))
        with self.assertRaises(Invalid):
            check(rows)

    def test_unknown_kind(self):
        self.mutate_rejected("target", "row_kind", "silent-extra")

    def test_censoring_retained(self):
        rows = rows_success()
        rows = rows[:6]
        final = common("target") | {"target_id": "Q2", "target_ordinal": 0, "point": point((6, 3)), "status": "censored", "upstream_status": 4, "verified_scalar": None, "public_equation_checked": False, "known_count": 1, "pending_count": 0, "endpoint_cap": 3, "table_state_hash64": table_hash([(fingerprint(F.base), 1)]), "harvest_committed": False, "reuse": {"known_before": 1, "known_after": 1, "capacity": 3, "pending_peak": 2, "unmatched_dp": 2, "chain_limit_restarts": 0, "staged": 2, "capacity_rejections": 0, "bucket_candidates_verified": 0, "rejected_bucket_witnesses": 0, "proposed": 0, "inserted": 0, "duplicates": 0, "rolled_back": 2}}
        result = check(rows + [final])
        self.assertEqual(result["producer_status_counts"]["censored"], 1)
        self.assertEqual(result["verified_case_witnesses"], 0)

    def test_unsuccessful_harvest_setup_retained(self):
        setup = rows_success()[0]
        setup.update({"status": "censored", "known_count": 0, "table_state_hash64": 0})
        final = rows_success()[-1]
        final.update({"status": "censored", "upstream_status": 3, "verified_scalar": None, "public_equation_checked": False, "known_count": 0, "table_state_hash64": 0, "harvest_committed": False, "reuse": {}})
        result = check([setup, final])
        self.assertEqual(result["producer_status_counts"]["censored"], 1)
        self.assertEqual(result["verified_case_witnesses"], 0)

    def test_chain_limit_not_admitted(self):
        # A fixed known DP/non-DP pair under a one-bit rule; no empirical sampling.
        entries = [(fingerprint(F.curve.multiply(F.base, e)), e) for e in range(19)]
        seed = next((fp, e) for fp, e in entries if not fp & 1)
        nons = next((fp, e) for fp, e in entries if fp & 1)
        rows = [common("setup") | {"status": "ready", "parameters": {"dp_bits": 1}, "known_count": 1, "endpoint_cap": 3, "table_state_hash64": table_hash([seed])}, common("initial_endpoint") | {"index": 0, "fp": seed[0], "exponent": seed[1]}]
        rows.append(common("terminal") | {"target_id": "Q2", "target_ordinal": 0, "attempt": 1, "reason": "chain_limit", "point": point(F.curve.multiply(F.base, nons[1])), "offset_a": (nons[1] - 2) % 19, "fp": nons[0], "pending_slot": 1, "known_count": 1, "pending_count": 1, "endpoint_cap": 3})
        with self.assertRaises(Invalid):
            check(rows)


class CliTests(unittest.TestCase):
    def test_public_tsv_cli_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixtures, targets, settings, records = root / "fixtures.tsv", root / "targets.tsv", root / "settings.tsv", root / "records.jsonl"
            fixtures.write_text("fixture_id\tstratum\tp\ta\tb\tgx\tgy\tr\tN\tseed\nfixed-F17\tdevelopment\t17\t2\t2\t5\t1\t19\t19\t1\n")
            targets.write_text("fixture_id\treplicate\ttarget_id\ttarget_ordinal\tqx\tqy\tinfinity\nfixed-F17\t0\tQ2\t0\t6\t3\t0\n")
            settings.write_text("cell_id\tfixture_id\treplicate\tdp_bits\tinitial_chains\tendpoint_cap\tmax_precomp_ops\tmax_online_ops\tseed\nfixed-cell\tfixed-F17\t0\t0\t1\t3\t10000\t10000\t1\n")
            records.write_text("".join(json.dumps(row) + "\n" for row in rows_success()))
            self.assertEqual(verify(fixtures, targets, settings, [records], {"harvest"}, root / "valid"), 0)
            records.write_text("{bad json}\n")
            self.assertEqual(verify(fixtures, targets, settings, [records], {"harvest"}, root / "invalid"), 1)
            self.assertEqual(json.loads((root / "invalid" / "summary.json").read_text())["status"], "invalid_public_record")
            with self.assertRaises(Invalid):
                verify(fixtures, targets, settings, [records], {"harvest"}, root / "valid")

    def test_private_column_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private.tsv"
            path.write_text("fixture_id\tk\nfixed-F17\t2\n")
            with self.assertRaises(Invalid):
                load_targets(path, {F.identifier: F})

    def test_noncanonical_target_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "target.tsv"
            path.write_text("fixture_id\treplicate\ttarget_id\ttarget_ordinal\tqx\tqy\tinfinity\nfixed-F17\t0\tQ2\t0\t1\t0\t1\n")
            with self.assertRaises(Invalid):
                load_targets(path, {F.identifier: F})

    def test_on_curve_target_outside_subgroup_rejected(self):
        outside_fixture = Fixture("fixed-F383", Curve(383, 261, 146), (196, 297), 181, 362)
        outside_fixture.validate()
        self.assertTrue(outside_fixture.curve.on_curve((66, 0)))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "outside.tsv"
            path.write_text("fixture_id\treplicate\ttarget_id\ttarget_ordinal\tqx\tqy\tinfinity\nfixed-F383\t0\toutside-P-subgroup\t0\t66\t0\t0\n")
            with self.assertRaises(Invalid):
                load_targets(path, {outside_fixture.identifier: outside_fixture})


if __name__ == "__main__":
    unittest.main(verbosity=2)
