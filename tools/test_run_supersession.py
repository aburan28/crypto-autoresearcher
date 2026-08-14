#!/usr/bin/env python3
"""Tests for run-manifest supersession (tools/run_supersession_registry.yaml).

An archived run manifest is immutable, so a defect in one is repaired by a NEW
record beside it. The registry tells validate_ledger.py which record to read
without letting either file drift. These tests pin the properties that make
that safe:

  * a run with no registry entry is validated exactly as before;
  * a registered supersession is validated against the SUPERSEDING record;
  * the superseded file must still be present and still hash to its
    registered value, and so must the superseding file;
  * an entry pointing at a missing file errors and falls back rather than
    silently dropping the run;
  * supersession cannot smuggle in a different run id, and cannot weaken the
    duplicate-ID check;
  * tier_of_run() handles a list-valued field_bits instead of crashing.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl


REPO = Path(vl.REPO)
ARTIFACTS = ("command.txt", "environment.json", "stdout.log", "stderr.log",
             "raw-result.json")


def manifest_body(**over) -> dict:
    """A run manifest that validates clean, before any field is removed."""
    body = {
        "id": "RUN-SUP-001",
        "experiment_id": "EXP-SUP-001",
        "status": "completed_valid",
        "code": {"commit": "0" * 40, "command": "python3 driver.py"},
        "environment": {"python": "3.13.0"},
        "inputs": {"parameters": {"field_bits": 16}},
        "timing": {"wall_clock_seconds": 1.0},
        "result": {"certificate": {"kind": "none"}},
    }
    body.update(over)
    return body


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SupersessionFixture(unittest.TestCase):
    """A temporary run directory with a defective manifest beside a repair."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="run-supersession-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = self.tmp / "experiments" / "EXP-SUP-001" / "runs" / "RUN-SUP-001"
        self.run_dir.mkdir(parents=True)
        for artifact in ARTIFACTS:
            (self.run_dir / artifact).write_text("{}\n", encoding="utf-8")
        # The defect this machinery exists for: required fields absent from an
        # already-archived manifest.
        defective = manifest_body()
        defective.pop("environment")
        defective.pop("inputs")
        self.superseded = self.write_manifest("manifest.yaml", defective)
        self.superseding = self.write_manifest("manifest_v2.yaml",
                                               manifest_body())

    def write_manifest(self, name: str, body: dict) -> Path:
        path = self.run_dir / name
        path.write_text(yaml.safe_dump({"run": body}, sort_keys=False),
                        encoding="utf-8")
        return path

    def registry(self, **over) -> dict[str, dict]:
        entry = {
            "run_id": "RUN-SUP-001",
            "superseded_path": str(self.superseded),
            "superseded_sha256": sha256_of(self.superseded),
            "superseding_path": str(self.superseding),
            "superseding_sha256": sha256_of(self.superseding),
        }
        entry.update(over)
        return {os.path.abspath(entry["superseded_path"]): entry}


class NoRegistryEntryTests(SupersessionFixture):
    def test_unregistered_run_is_validated_exactly_as_before(self) -> None:
        """The default path must not change: same errors, same rendering."""
        without = vl.Ctx(set())
        vl.check_run(str(self.superseded), without)
        empty = vl.Ctx(set())
        vl.check_run(str(self.superseded), empty, {})
        unrelated = vl.Ctx(set())
        vl.check_run(str(self.superseded), unrelated,
                     {"/nowhere/manifest.yaml": {"run_id": "RUN-OTHER-001"}})

        self.assertEqual(without.errors, empty.errors)
        self.assertEqual(without.errors, unrelated.errors)
        self.assertEqual(
            [e.split(": ", 1)[1] for e in without.errors],
            ["run missing required field 'environment'",
             "run missing required field 'inputs'"],
        )
        self.assertIn("RUN-SUP-001", without.ids)

    def test_unregistered_clean_run_still_passes(self) -> None:
        clean_dir = self.tmp / "experiments" / "EXP-SUP-002" / "runs" / "RUN-SUP-002"
        clean_dir.mkdir(parents=True)
        for artifact in ARTIFACTS:
            (clean_dir / artifact).write_text("{}\n", encoding="utf-8")
        path = clean_dir / "manifest.yaml"
        path.write_text(
            yaml.safe_dump({"run": manifest_body(id="RUN-SUP-002")},
                           sort_keys=False),
            encoding="utf-8")
        ctx = vl.Ctx(set())
        vl.check_run(str(path), ctx, {})
        self.assertEqual(ctx.errors, [])


class RegisteredSupersessionTests(SupersessionFixture):
    def test_flat_archived_manifest_id_is_bound_to_replacement(self) -> None:
        self.superseded.write_text(yaml.safe_dump({
            "run_id": "RUN-SUP-001",
            "experiment_id": "EXP-SUP-001",
        }, sort_keys=False), encoding="utf-8")
        supersessions = self.registry()
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertEqual(ctx.errors, [])

    def test_registered_supersession_validates_the_superseding_record(self) -> None:
        supersessions = self.registry()
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        vl.check_run(str(self.superseded), ctx, supersessions)
        self.assertEqual(ctx.errors, [])
        # The run id is registered once, from the record that was read.
        self.assertEqual(ctx.ids["RUN-SUP-001"], str(self.superseding))
        self.assertEqual(ctx.run_params["RUN-SUP-001"], {"field_bits": 16})

    def test_a_defect_in_the_superseding_record_is_still_reported(self) -> None:
        """Supersession redirects the check; it does not suppress it."""
        incomplete = manifest_body()
        incomplete.pop("timing")
        self.write_manifest("manifest_v2.yaml", incomplete)
        ctx = vl.Ctx(set())
        vl.check_run(str(self.superseded), ctx, self.registry())
        self.assertEqual(len(ctx.errors), 1, ctx.errors)
        # Reported against the record that was actually read.
        self.assertIn("missing required field 'timing'", ctx.errors[0])
        self.assertIn("manifest_v2.yaml", ctx.errors[0])

    def test_companion_artifacts_are_checked_in_the_run_directory(self) -> None:
        (self.run_dir / "stdout.log").unlink()
        ctx = vl.Ctx(set())
        vl.check_run(str(self.superseded), ctx, self.registry())
        self.assertTrue(any("missing artifact 'stdout.log'" in e
                            for e in ctx.errors), ctx.errors)

    def test_supersession_does_not_weaken_the_duplicate_id_check(self) -> None:
        """A second record with the same run id still collides."""
        other_dir = self.tmp / "experiments" / "EXP-SUP-003" / "runs" / "RUN-SUP-001b"
        other_dir.mkdir(parents=True)
        for artifact in ARTIFACTS:
            (other_dir / artifact).write_text("{}\n", encoding="utf-8")
        other = other_dir / "manifest.yaml"
        other.write_text(yaml.safe_dump({"run": manifest_body()},
                                        sort_keys=False), encoding="utf-8")
        ctx = vl.Ctx(set())
        supersessions = self.registry()
        vl.check_run(str(self.superseded), ctx, supersessions)
        vl.check_run(str(other), ctx, supersessions)
        self.assertTrue(any("duplicate ID RUN-SUP-001" in e
                            for e in ctx.errors), ctx.errors)


class SupersessionIntegrityTests(SupersessionFixture):
    def test_superseded_hash_mismatch_is_an_error(self) -> None:
        """A silent edit of the frozen original must not hide behind a repair."""
        supersessions = self.registry(superseded_sha256="a" * 64)
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertTrue(any("registered superseded run manifest hash changed"
                            in e for e in ctx.errors), ctx.errors)

    def test_superseding_hash_mismatch_is_an_error(self) -> None:
        supersessions = self.registry(superseding_sha256="b" * 64)
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertTrue(any("registered superseding run manifest hash changed"
                            in e for e in ctx.errors), ctx.errors)

    def test_hash_errors_are_not_downgraded_to_legacy_warnings(self) -> None:
        """force=True: a path that is grandfathered elsewhere still errors."""
        ctx = vl.Ctx({os.path.abspath(str(self.superseded)),
                      os.path.abspath(str(self.superseding))})
        vl.check_run_supersessions(ctx, self.registry(superseded_sha256="a" * 64))
        self.assertTrue(ctx.errors)
        self.assertEqual(ctx.legacy_warnings, [])

    def test_missing_superseded_file_is_an_error(self) -> None:
        supersessions = self.registry()
        self.superseded.unlink()
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertTrue(any("registered superseded run manifest is missing" in e
                            for e in ctx.errors), ctx.errors)

    def test_missing_superseding_file_errors_and_falls_back(self) -> None:
        supersessions = self.registry()
        self.superseding.unlink()
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertTrue(any("registered superseding run manifest is missing"
                            in e for e in ctx.errors), ctx.errors)
        vl.check_run(str(self.superseded), ctx, supersessions)
        # Falls back to the superseded record: its defects reappear and the run
        # is still registered rather than vanishing from the ledger.
        self.assertTrue(any("missing required field 'environment'" in e
                            for e in ctx.errors), ctx.errors)
        self.assertIn("RUN-SUP-001", ctx.ids)

    def test_run_id_mismatch_is_an_error(self) -> None:
        """An entry may not point at a record for a different run."""
        self.write_manifest("manifest_v2.yaml", manifest_body(id="RUN-OTHER-001"))
        supersessions = self.registry(
            superseding_sha256=sha256_of(self.superseding))
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, supersessions)
        self.assertTrue(any("declares run id 'RUN-OTHER-001'" in e
                            for e in ctx.errors), ctx.errors)


def registry_document(**over) -> dict:
    record = {
        "run_id": "RUN-SUP-001",
        "superseded_path": "experiments/EXP-SUP-001/runs/RUN-SUP-001/manifest.yaml",
        "superseded_sha256": "c" * 64,
        "superseding_path": "experiments/EXP-SUP-001/runs/RUN-SUP-001/manifest_v2.yaml",
        "superseding_sha256": "d" * 64,
        "defect": "missing environment and inputs",
        "registered": "2026-08-01",
    }
    record.update(over)
    return {"schema": vl.RUN_SUPERSESSION_SCHEMA, "records": [record]}


class RegistryLoaderTests(unittest.TestCase):
    def load(self, document) -> dict[str, dict]:
        tmp = Path(tempfile.mkdtemp(prefix="run-supersession-registry-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        path = tmp / "registry.yaml"
        path.write_text(yaml.safe_dump(document, sort_keys=False),
                        encoding="utf-8")
        return vl.load_run_supersessions(str(path))

    def test_wellformed_registry_is_keyed_by_absolute_superseded_path(self) -> None:
        entries = self.load(registry_document())
        key = os.path.abspath(os.path.join(
            vl.REPO,
            "experiments/EXP-SUP-001/runs/RUN-SUP-001/manifest.yaml"))
        self.assertEqual(list(entries), [key])
        self.assertTrue(os.path.isabs(entries[key]["superseding_path"]))

    def test_absent_registry_is_empty_not_fatal(self) -> None:
        self.assertEqual(vl.load_run_supersessions("/nonexistent/registry.yaml"),
                         {})

    def test_wrong_schema_is_refused(self) -> None:
        document = registry_document()
        document["schema"] = "something-else-v1"
        with self.assertRaises(ValueError):
            self.load(document)

    def test_missing_required_field_is_refused(self) -> None:
        for field in vl.RUN_SUPERSESSION_REQUIRED:
            document = registry_document()
            document["records"][0].pop(field)
            with self.assertRaises(ValueError, msg=field):
                self.load(document)

    def test_non_hex_digest_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(superseded_sha256="not-a-digest"))

    def test_superseded_path_must_be_a_discovered_run_manifest(self) -> None:
        """Otherwise the entry would never be consulted and would mislead."""
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseded_path="experiments/EXP-SUP-001/notes.yaml"))

    def test_superseding_path_must_not_be_discovered_by_the_run_glob(self) -> None:
        """Two globbed records with one run id would collide on registration."""
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="experiments/EXP-SUP-009/runs/RUN-X/manifest.yaml"))

    def test_escaping_paths_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.load(registry_document(
                superseding_path="experiments/../../etc/manifest_v2.yaml"))

    def test_duplicate_superseded_path_is_refused(self) -> None:
        document = registry_document()
        document["records"].append(dict(document["records"][0]))
        with self.assertRaises(ValueError):
            self.load(document)


class TierOfRunTests(unittest.TestCase):
    """field_bits may be a list of cells; the largest cell governs the tier."""

    def test_scalar_field_bits_is_unchanged(self) -> None:
        self.assertEqual(vl.tier_of_run({"field_bits": 16}), vl.TIER_ORDER["toy"])
        self.assertEqual(vl.tier_of_run({"field_bits": 64}),
                         vl.TIER_ORDER["medium"])
        self.assertEqual(vl.tier_of_run({"field_bits": 256}),
                         vl.TIER_ORDER["crypto"])
        self.assertEqual(vl.tier_of_run({"field_bit_size": 16}),
                         vl.TIER_ORDER["toy"])
        self.assertIsNone(vl.tier_of_run({}))

    def test_list_field_bits_does_not_crash(self) -> None:
        """int([16, 20]) raises TypeError, which would abort validation."""
        self.assertEqual(vl.tier_of_run({"field_bits": [16, 20]}),
                         vl.TIER_ORDER["toy"])

    def test_largest_cell_governs(self) -> None:
        self.assertEqual(vl.tier_of_run({"field_bits": [16, 64]}),
                         vl.TIER_ORDER["medium"])
        self.assertEqual(vl.tier_of_run({"field_bits": [16, 256]}),
                         vl.TIER_ORDER["crypto"])
        self.assertEqual(vl.tier_of_run({"field_bits": (20, 16)}),
                         vl.TIER_ORDER["toy"])

    def test_unusable_values_are_unknown_rather_than_fatal(self) -> None:
        for value in ([], {"a": 1}, ["wide"], [None], [[16]], "wide"):
            with self.subTest(value=value):
                self.assertIsNone(vl.tier_of_run({"field_bits": value}))

    def test_claim_tier_is_not_an_automatic_scale_ceiling(self) -> None:
        ctx = vl.Ctx(set())
        ctx.run_params["RUN-T-001"] = {"field_bits": [16, 20]}
        ctx.ids["RUN-T-001"] = "x"
        ctx.ids["EV-T-001"] = "ledger/evidence/EV-T-001.yaml"
        ctx.record_types["EV-T-001"] = "evidence"
        ctx.records["EV-T-001"] = {
            "id": "EV-T-001", "hypothesis_id": None, "run_ids": ["RUN-T-001"],
            "claim_tier": "crypto",
        }
        vl.check_cross_refs(ctx)
        self.assertFalse(any("exceeds what its runs' parameters allow" in e
                             for e in ctx.errors), ctx.errors)


class CommittedRegistryTests(unittest.TestCase):
    """The registry as committed must be true of the repository right now."""

    def test_committed_registry_loads_and_both_files_hash_as_recorded(self) -> None:
        entries = vl.load_run_supersessions()
        self.assertTrue(entries)
        for entry in entries.values():
            for role in ("superseded", "superseding"):
                path = Path(entry[f"{role}_path"])
                self.assertTrue(path.is_file(), path)
                self.assertEqual(sha256_of(path), entry[f"{role}_sha256"],
                                 str(path))

    def test_committed_supersessions_are_clean(self) -> None:
        entries = vl.load_run_supersessions()
        ctx = vl.Ctx(set())
        vl.check_run_supersessions(ctx, entries)
        for key in entries:
            vl.check_run(key, ctx, entries)
        self.assertEqual(ctx.errors, [])

    def test_lpf_plantz_manifest_is_routed_to_its_superseding_record(self) -> None:
        superseded = REPO / ("experiments/EXP-LPF-001/runs/RUN-LPF-001-plantz/"
                             "manifest.yaml")
        entries = vl.load_run_supersessions()
        self.assertIn(os.path.abspath(str(superseded)), entries)
        # Unrouted, the frozen record still shows exactly the defect the
        # supersession repairs. It is never edited.
        ctx = vl.Ctx(set())
        vl.check_run(str(superseded), ctx)
        self.assertEqual(
            sorted(e.split(": ", 1)[1] for e in ctx.errors),
            ["run missing required field 'environment'",
             "run missing required field 'inputs'"],
        )

    def test_superseding_record_declares_the_supersession_from_its_own_side(self) -> None:
        entries = vl.load_run_supersessions()
        for entry in entries.values():
            repo_root = REPO.resolve()
            registry_original = Path(entry["superseded_path"]).resolve()
            run_dir = registry_original.parent
            current = Path(entry["superseding_path"]).resolve()
            self.assertEqual(current.parent, run_dir, str(current))
            seen: set[str] = set()
            while True:
                self.assertNotIn(str(current), seen, entry["superseding_path"])
                seen.add(str(current))
                body = yaml.safe_load(
                    current.read_text(encoding="utf-8"))["run"]
                self.assertEqual(body.get("id"), entry["run_id"], str(current))
                declared = body.get("supersedes") or {}
                # Three immutable superseding-record vocabularies coexist.
                # Most records use prior_manifest_*, four early ECDLP
                # records use prior_manifest/prior_sha256, and SSIQ uses
                # path/sha256.  One final v3 record honestly names its v2
                # predecessor, which then names the registry's original.
                # Follow and hash-check that immutable chain rather than
                # rewriting history to make every replacement look direct.
                prior_path = (declared.get("prior_manifest_path")
                              or declared.get("prior_manifest")
                              or declared.get("path"))
                prior_sha256 = (declared.get("prior_manifest_sha256")
                                or declared.get("prior_sha256")
                                or declared.get("sha256"))
                self.assertIsNotNone(prior_path, str(current))
                self.assertIsNotNone(prior_sha256, str(current))
                prior = (repo_root / str(prior_path)).resolve()
                self.assertTrue(prior.is_relative_to(repo_root), str(prior))
                self.assertEqual(prior.parent, run_dir, str(prior))
                self.assertTrue(prior.is_file(), str(prior))
                self.assertEqual(sha256_of(prior), prior_sha256, str(prior))
                self.assertEqual(vl._run_id_of(str(prior)), entry["run_id"],
                                 str(prior))
                if prior == registry_original:
                    self.assertEqual(prior_sha256,
                                     entry["superseded_sha256"])
                    break
                current = prior


if __name__ == "__main__":
    unittest.main()
