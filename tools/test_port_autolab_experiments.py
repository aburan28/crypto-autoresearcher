#!/usr/bin/env python3
"""Tests for the Autolab port tool.

Every test replays a defect that reached the PR that introduced this tool. If
one regresses, the 84 EXP-AL* packages stop meaning what their records say:

  - `test_gitignored_candidate_is_never_recorded` — the tool recorded what it
    copied on the porting machine, but `.gitignore` drops `*.sage.py`. Fifty
    packages shipped an artifact count and file list citing files that are not
    in the repository.
  - `test_appledouble_never_displaces_the_real_file` — three packages listed a
    macOS `._`-prefixed resource fork as their contract artifact while the real
    contract file they do ship went unlisted.
  - `test_item_with_no_archivable_source_is_skipped` — `catalog_binary` emitted
    all eleven binary-field packages whether or not the source existed, so a
    run over an empty `source/` dir was still written `completed_valid` with
    `import_complete: 1`. A receipt for work that did not happen.
  - `test_docs_mirror_is_not_mistaken_for_a_source_checkout` — `inputs/refs`
    satisfied the old root probe while holding no result artifacts, so a rerun
    silently resolved a different `source_repo` than the one written into all
    84 specifications.
  - the `finding` tests — `extract_finding` returned bare status flags and
    serialized dicts, which were copied verbatim into hypothesis statements.
    Twenty-seven read "Source finding: failed"; five embedded a Python dict.
  - `test_verify_*` / `test_reconcile_*` — `--verify` is the check a reviewer
    can run from a fresh clone with no Autolab checkout, so it has to actually
    fail on a misreported archive and pass after `--reconcile`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import port_autolab_experiments as port


class _Repo:
    """A throwaway git repo with the real .gitignore rules, `port.REPO` at it."""

    GITIGNORE = "*.sage.py\n._*\n.DS_Store\n"

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.path, check=True)
        (self.path / ".gitignore").write_text(self.GITIGNORE)
        self.src = self.path / "autolab"
        self.src.mkdir()
        self._saved = port.REPO
        port.REPO = self.path
        return self

    def __exit__(self, *exc):
        port.REPO = self._saved
        self.tmp.cleanup()

    def source(self, name: str, text: str = "x") -> Path:
        p = self.src / name
        p.write_text(text)
        return p

    def package(self, exp_id: str) -> Path:
        """A minimal ported package whose records match its archive."""
        exp_dir = self.path / "experiments" / exp_id
        (exp_dir / "source").mkdir(parents=True)
        (exp_dir / "source" / "probe_result.json").write_text(
            json.dumps({"finding": "d_ff stayed flat across three sizes"}))
        (exp_dir / "source" / "probe.sage").write_text("# probe\n")
        port.dump_yaml(exp_dir / "specification.yaml", {"experiment": {
            "id": exp_id, "hypothesis_id": "H-ALPF-900", "version": 1,
            "objective": "Archive `probe`. Source finding: failed",
            "inputs": {"source_id": "probe"}}})
        truth = port.archived_artifacts(exp_dir)
        (exp_dir / "implementation.md").write_text(
            "# Implementation\n\n## Copied artifacts\n"
            + "".join(f"- `{rel}`\n" for rel in sorted(truth))
            + "\n## Deviations\n- none\n")
        run_dir = exp_dir / "runs" / f"RUN-{exp_id.split('-', 1)[1]}-import"
        run_dir.mkdir(parents=True)
        port.dump_yaml(run_dir / "manifest.yaml", {"run": {
            "id": run_dir.name, "experiment_id": exp_id,
            "inputs": {"parameters": {"topic": "prime-field ECDLP"}},
            "result": {"metrics": port.archive_metrics(truth)}}})
        (run_dir / "raw-result.json").write_text(
            json.dumps({"copied_artifact_sha256": truth}, indent=2))
        return exp_dir


class ArchiveSelectionTests(unittest.TestCase):
    def test_gitignored_candidate_is_never_recorded(self):
        with _Repo() as repo:
            kept = port.archivable(repo.path / "experiments/E/source", [
                repo.source("round001.sage"),
                repo.source("round001.sage.py"),
                repo.source("round001_result.json"),
            ])
            self.assertEqual(
                [p.name for p in kept],
                ["round001.sage", "round001_result.json"],
                "a file .gitignore drops cannot be archived, so no record may cite it",
            )

    def test_appledouble_never_displaces_the_real_file(self):
        with _Repo() as repo:
            kept = port.archivable(repo.path / "experiments/E/source", [
                repo.source("._contract.md"),
                repo.source("contract.md"),
            ])
            self.assertEqual([p.name for p in kept], ["contract.md"])

    def test_fallback_ignore_patterns_hold_without_git(self):
        # If `git check-ignore` cannot answer, silence must not be read as
        # "nothing is ignored" -- that is how the bad manifests were written.
        with tempfile.TemporaryDirectory() as tmp:
            saved, port.REPO = port.REPO, Path(tmp)  # not a git repo
            try:
                src = Path(tmp) / "src"
                src.mkdir()
                for name in ("a.sage", "a.sage.py"):
                    (src / name).write_text("x")
                kept = port.archivable(Path(tmp) / "dest", list(src.iterdir()))
            finally:
                port.REPO = saved
            self.assertEqual([p.name for p in kept], ["a.sage"])

    def test_archive_metrics_follow_the_archive(self):
        self.assertEqual(
            port.archive_metrics({"source/x_result.json": "d"}),
            {"import_complete": 1, "source_result_present": 1,
             "source_script_present": 0, "copied_artifact_count": 1},
            "source_script_present must reflect the archive, not the candidate list",
        )
        self.assertEqual(port.archive_metrics({})["import_complete"], 0)


class FailClosedTests(unittest.TestCase):
    def test_item_with_no_archivable_source_is_skipped(self):
        with _Repo() as repo:
            item = {"area": "ALBIN", "topic": "binary-field ECDLP",
                    "source_id": "bin_exp001", "title": "t",
                    "result_json": None, "result_md": None, "contract": None,
                    "code": [], "logs": [], "extras": []}
            self.assertIsNone(port.port_item(item, 1))
            self.assertFalse((repo.path / "experiments" / "EXP-ALBIN-001").exists(),
                             "nothing may be written for a package with no archive")

    def test_binary_catalog_is_empty_without_a_source_tree(self):
        saved, port.AUTOLAB = port.AUTOLAB, Path("/nonexistent-autolab")
        try:
            self.assertEqual(port.catalog_binary(), [])
        finally:
            port.AUTOLAB = saved

    def test_docs_mirror_is_not_mistaken_for_a_source_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prime = root / "experiments" / "ecdlp_prime_field"
            prime.mkdir(parents=True)
            (prime / "round001_results.md").write_text("# notes\n")
            self.assertFalse(port.has_portable_content(root),
                             "a docs mirror holds no result artifacts to port")
            (prime / "round001_result.json").write_text("{}")
            self.assertTrue(port.has_portable_content(root))


class FindingTests(unittest.TestCase):
    def test_status_flag_is_not_reported_as_a_finding(self):
        finding = port.extract_finding({"status": "failed"}, "")
        self.assertNotEqual(finding.strip().lower(), "failed")
        self.assertIn("failed", finding, "the flag is still reported, just not as a result")
        self.assertTrue(port.finding_is_degenerate("failed"))

    def test_serialized_dict_is_not_reported_as_a_finding(self):
        finding = port.extract_finding(
            {"gate_discriminating": False, "posc_passes_gate": True}, "")
        self.assertFalse(finding.lstrip().startswith("{"))
        self.assertIn("gate_discriminating", finding)
        self.assertTrue(port.finding_is_degenerate("{'a': True, 'b': False}"))

    def test_metadata_header_is_not_reported_as_a_finding(self):
        header = "**Date:** 2026-05-31. **Script:** `bin_exp001.sage`. **Log:** `x.log`."
        self.assertTrue(port.finding_is_degenerate(header))
        finding = port.extract_finding(None, f"# Result\n{header}\nWeil descent gate held.")
        self.assertEqual(finding, "Weil descent gate held.")

    def test_a_written_verdict_is_preferred_over_a_flag(self):
        self.assertEqual(
            port.extract_finding(
                {"status": "failed", "claim_status": "TOY EVIDENCE / MODEL-BOUND"}, ""),
            "TOY EVIDENCE / MODEL-BOUND")

    def test_absent_finding_is_reported_as_absent(self):
        self.assertIn("No narrative finding", port.extract_finding(None, ""))


class VerifyTests(unittest.TestCase):
    def test_a_faithful_package_passes(self):
        with _Repo() as repo:
            self.assertEqual(port.package_discrepancies(repo.package("EXP-ALPF-901")), [])

    def test_verify_catches_an_overstated_artifact_count(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-902")
            manifest = next((exp_dir / "runs").glob("*/manifest.yaml"))
            doc = port.yaml.safe_load(manifest.read_text())
            doc["run"]["result"]["metrics"]["copied_artifact_count"] = 99
            port.dump_yaml(manifest, doc)
            problems = port.package_discrepancies(exp_dir)
            self.assertTrue(any("copied_artifact_count=99" in p for p in problems), problems)

    def test_verify_catches_a_listed_but_unarchived_artifact(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-903")
            impl = exp_dir / "implementation.md"
            impl.write_text(impl.read_text().replace(
                "## Deviations", "- `source/probe.sage.py`\n\n## Deviations"))
            problems = port.package_discrepancies(exp_dir)
            self.assertTrue(any("probe.sage.py" in p and "not archived" in p
                                for p in problems), problems)

    def test_verify_catches_an_archived_but_unlisted_artifact(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-904")
            impl = exp_dir / "implementation.md"
            impl.write_text(impl.read_text().replace("- `source/probe.sage`\n", ""))
            problems = port.package_discrepancies(exp_dir)
            self.assertTrue(any("omits archived" in p for p in problems), problems)

    def test_verify_catches_a_stale_hash(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-905")
            raw_path = next((exp_dir / "runs").glob("*/raw-result.json"))
            raw = json.loads(raw_path.read_text())
            raw["copied_artifact_sha256"]["source/probe.sage"] = "0" * 64
            raw_path.write_text(json.dumps(raw))
            problems = port.package_discrepancies(exp_dir)
            self.assertTrue(any("sha256 mismatch" in p for p in problems), problems)


class ReconcileTests(unittest.TestCase):
    def test_reconcile_repairs_the_record_and_leaves_the_archive_alone(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-906")
            before = {p.name: p.read_bytes() for p in (exp_dir / "source").iterdir()}
            manifest = next((exp_dir / "runs").glob("*/manifest.yaml"))
            doc = port.yaml.safe_load(manifest.read_text())
            doc["run"]["result"]["metrics"]["copied_artifact_count"] = 99
            port.dump_yaml(manifest, doc)

            self.assertTrue(port.reconcile_package(exp_dir))
            self.assertEqual(port.package_discrepancies(exp_dir), [])
            self.assertEqual({p.name: p.read_bytes()
                              for p in (exp_dir / "source").iterdir()}, before,
                             "reconcile rewrites records, never archived artifacts")

    def test_reconcile_is_idempotent(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-907")
            port.reconcile_package(exp_dir)
            self.assertFalse(port.reconcile_package(exp_dir))

    def test_reconcile_refreshes_a_degenerate_finding_from_the_archive(self):
        with _Repo() as repo:
            exp_dir = repo.package("EXP-ALPF-908")
            new = port.reconcile_findings(exp_dir)
            self.assertEqual(new, "d_ff stayed flat across three sizes")
            spec = port.yaml.safe_load(
                (exp_dir / "specification.yaml").read_text())["experiment"]
            self.assertNotIn("Source finding: failed", spec["objective"])
            self.assertIn(new, spec["objective"])
            self.assertIsNone(port.reconcile_findings(exp_dir),
                              "a healthy finding is left alone")


if __name__ == "__main__":
    unittest.main()
