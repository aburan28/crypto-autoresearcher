#!/usr/bin/env python3
"""Tests for the source index.

The index exists to answer "can a later session get back to what we read?", so
the tests that matter are the ones pinning the distinctions that make an answer
honest rather than merely present:

  - a declared `artifact_frozen_in_repo: false` is never upgraded by inference
    (SRC-OAI-TEN-PROOFS-2026 says its PDF is absent, and that statement is the
    whole point of the record);
  - a package whose artifact is present but undeclared is still found
    (SRC-P13-WESOLOWSKI-2026 has no `frozen_path` and is the corpus's one
    fully-frozen paper);
  - a source that was sought and never obtained keeps a row rather than
    vanishing into an unexplained absence;
  - a file present without a `.sha256` is reported as unvouched-for, not as
    verified.

Each of those is a way the index could quietly overstate reachability, which is
the failure this tool is meant to prevent.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_source_index as bsi


class IdentifierNormalisationTests(unittest.TestCase):
    def test_eprint_prefixes_collapse_to_one_key(self) -> None:
        for raw in ("iacr:2004/031", "eprint:2004/031", "2004/031"):
            with self.subTest(raw):
                self.assertEqual(bsi.canonical_identifier("eprint", raw), "eprint:2004/031")

    def test_arxiv_and_doi_prefixes_are_stripped(self) -> None:
        self.assertEqual(bsi.canonical_identifier("arxiv", "arXiv:2607.14624"), "arxiv:2607.14624")
        self.assertEqual(
            bsi.canonical_identifier("doi", "https://doi.org/10.1016/j.jsc.2008.08.005"),
            "doi:10.1016/j.jsc.2008.08.005",
        )

    def test_url_scheme_and_trailing_slash_do_not_split_one_source(self) -> None:
        a = bsi.canonical_identifier("url", "https://eprint.iacr.org/2004/031/")
        b = bsi.canonical_identifier("url", "http://eprint.iacr.org/2004/031")
        self.assertEqual(a, b)

    def test_absent_identifiers_stay_absent(self) -> None:
        """Rule 5: a missing identifier is reported missing, never invented."""
        for empty in (None, "", "null", "None"):
            with self.subTest(empty):
                self.assertIsNone(bsi.canonical_identifier("doi", empty))


class SourcePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packages = {p["record_id"]: p for p in bsi.collect_source_packages()}

    def test_a_declared_absent_artifact_is_not_upgraded_by_inference(self) -> None:
        oai = self.packages["SRC-OAI-TEN-PROOFS-2026"]
        self.assertFalse(oai["artifact_frozen_in_repo"])
        self.assertEqual(oai["artifact_frozen_basis"], "declared")

    def test_an_undeclared_but_present_artifact_is_found(self) -> None:
        wes = self.packages["SRC-P13-WESOLOWSKI-2026"]
        self.assertTrue(wes["artifact_frozen_in_repo"])
        self.assertEqual(wes["artifact_frozen_basis"], "package_contents")
        self.assertIn(
            "inputs/P13-WESOLOWSKI-2026/paper_fulltext.md", wes["package_contents"]
        )

    def test_frozen_path_packages_resolve_through_that_field(self) -> None:
        panny = self.packages["SRC-P13-PANNY-POC"]
        self.assertTrue(panny["frozen_path_present"])
        self.assertEqual(panny["artifact_frozen_basis"], "frozen_path")


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = {a["path"]: a for a in bsi.collect_frozen_artifacts()}

    def test_every_declared_hash_in_the_repository_matches(self) -> None:
        mismatched = [a["path"] for a in self.artifacts.values() if a["verdict"] == "MISMATCH"]
        self.assertEqual(mismatched, [], f"vendored artifact hash mismatch: {mismatched}")

    def test_a_sought_but_never_retrieved_source_keeps_a_row(self) -> None:
        row = self.artifacts["inputs/ECTD-TESKE-20260731/sources/dent-galbraith-hidden.pdf"]
        self.assertEqual(row["verdict"], "never_retrieved")
        self.assertFalse(row["present"])
        self.assertTrue(row["fetch_failure_marker"])

    def test_a_file_without_a_sidecar_is_not_reported_as_verified(self) -> None:
        row = self.artifacts["inputs/ECTD-TESKE-20260731/sources/fght-2016-961.pdf"]
        self.assertEqual(row["verdict"], "present_unhashed")
        self.assertTrue(row["present"])
        self.assertIsNone(row["declared_sha256"])


class IndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = bsi.build()

    def test_literature_partitions_exactly_into_resolvable_and_not(self) -> None:
        c = self.index["counts"]
        self.assertEqual(
            c["literature_with_identifier"] + c["literature_without_identifier"],
            c["literature_entries"],
        )

    def test_no_literature_entry_fails_to_parse(self) -> None:
        broken = [r["id"] for r in self.index["literature"] if r["parse_error"]]
        self.assertEqual(broken, [], f"unparseable literature frontmatter: {broken}")

    def test_failed_retrievals_are_retained_not_filtered(self) -> None:
        """A blocked fetch is provenance: it records that we looked."""
        self.assertGreater(self.index["counts"]["retrieval_attempts_failed"], 0)

    def test_render_is_deterministic(self) -> None:
        """--check compares rendered text, so an unstable render would flap CI."""
        self.assertEqual(bsi.render(self.index), bsi.render(bsi.build()))


if __name__ == "__main__":
    unittest.main()
