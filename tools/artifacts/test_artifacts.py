"""End-to-end tests for tools/artifacts against a file:// remote in a scratch repository.

    python3 -m unittest tools/artifacts/test_artifacts.py
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "artifacts.py"
sys.path.insert(0, str(TOOL.parent))
import artifacts  # noqa: E402
import wire_workflows  # noqa: E402
from wire_workflows import explicitly_pulled_and_verified, metadata_only, wire  # noqa: E402


def sh(cwd, *argv, check=True, env=None):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=check, env=env)


class PlaceCopy(unittest.TestCase):
    def test_creates_missing_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            src = base / "src.bin"
            src.write_bytes(b"abc")
            dest = base / "docs" / "reports" / "x" / "report.pdf"
            artifacts.place_copy(src, dest)
            self.assertEqual(dest.read_bytes(), b"abc")


class RoundTrip(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.repo, self.remote, self.cache = base / "repo", base / "remote", base / "cache"
        self.repo.mkdir()
        self.env = {**os.environ, "ARTIFACTS_REMOTE": f"file://{self.remote}", "ARTIFACTS_CACHE": str(self.cache),
                    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                    "GIT_COMMITTER_EMAIL": "t@t"}
        sh(self.repo, "git", "init", "-q", "-b", "main")
        runs = self.repo / "research" / "r1" / "runs"
        runs.mkdir(parents=True)
        self.big = os.urandom(300_000)
        (runs / "a.jsonl").write_bytes(self.big)
        (runs / "weird [1]*.log").write_bytes(os.urandom(70_000))
        (runs / "small.jsonl").write_bytes(b"{}\n")        # under data_min_bytes: stays
        (self.repo / "research" / "r1" / "README.md").write_text("x" * 2_000_000)  # code ext: stays
        (self.repo / "research" / "r1" / "blob.unknown").write_bytes(os.urandom(1_100_000))  # > max_bytes
        self.git("add", "-A")
        self.git("commit", "-qm", "seed")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *a):
        return sh(self.repo, "git", *a, env=self.env).stdout

    def art(self, *a, check=True, cwd=None):
        return sh(cwd or self.repo, sys.executable, str(TOOL), *a, check=check, env=self.env)

    def test_push_commit_clone_pull_verify(self):
        plan = self.art("plan").stdout
        self.assertIn("research/r1/runs/a.jsonl", plan)
        self.assertIn("research/r1/blob.unknown", plan)
        self.assertNotIn("small.jsonl", plan)
        self.assertNotIn("README.md", plan)

        self.art("push", "research")
        self.git("commit", "-qm", "move data to the store")
        tracked = self.git("ls-files").split("\n")
        self.assertNotIn("research/r1/runs/a.jsonl", tracked)
        self.assertIn("research/r1/runs/.artifacts.json", tracked)
        self.assertIn("research/r1/runs/small.jsonl", tracked)
        self.assertEqual(self.git("status", "--porcelain"), "")  # hydrated files are ignored

        digest = hashlib.sha256(self.big).hexdigest()
        self.assertTrue((self.remote / "sha256" / digest[:2] / digest).exists())
        m = json.loads((self.repo / "research/r1/runs/.artifacts.json").read_text())
        self.assertEqual(m["files"]["a.jsonl"], {"sha256": digest, "bytes": len(self.big)})

        # A fresh clone has pointers only; pull a subtree, then everything.
        clone = Path(self.tmp.name) / "clone"
        sh(self.tmp.name, "git", "clone", "-q", str(self.repo), str(clone))
        self.assertFalse((clone / "research/r1/runs/a.jsonl").exists())
        self.art("pull", "research/r1/runs/a.jsonl", cwd=clone)
        self.assertEqual((clone / "research/r1/runs/a.jsonl").read_bytes(), self.big)
        self.assertFalse((clone / "research/r1/blob.unknown").exists())
        self.art("pull", cwd=clone)
        self.assertTrue((clone / "research/r1/runs/weird [1]*.log").exists())
        self.assertEqual(self.art("verify", "--remote", cwd=clone).returncode, 0)
        self.assertEqual(sh(clone, "git", "status", "--porcelain").stdout, "")

        # Editing a hydrated file in place is caught, and never corrupts the cache.
        (clone / "research/r1/runs/a.jsonl").write_bytes(b"tampered")
        self.assertEqual(self.art("verify", cwd=clone, check=False).returncode, 1)
        self.art("pull", cwd=clone)
        self.assertEqual((clone / "research/r1/runs/a.jsonl").read_bytes(), self.big)

    def test_sparse_private_manifest_keeps_metadata_checks_credential_free(self):
        manifest = self.repo / "docs/reports/private/.artifacts.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({
            "schema": "artifacts.manifest/v1",
            "files": {"report.pdf": {
                "sha256": hashlib.sha256(self.big).hexdigest(), "bytes": len(self.big),
            }},
        }) + "\n")
        workflows = self.repo / ".github/workflows"
        workflows.mkdir(parents=True)
        metadata = workflows / "metadata.yml"
        original = ("# artifact-store: no-pull (checks descriptors, not report bytes)\n"
                    "jobs:\n  metadata:\n    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - run: python tools/check_metadata.py docs/reports/private\n")
        metadata.write_text(original)
        consumer = workflows / "consumer.yml"
        consumer.write_text("jobs:\n  content:\n    steps:\n"
                            "      - uses: actions/checkout@v4\n"
                            "      - run: cat docs/reports/private/report.pdf\n")
        self.git("add", ".github", "docs")
        self.git("commit", "-qm", "private pointer and separate metadata/content consumers")
        self.git("sparse-checkout", "set", "--no-cone", "/.github/")
        self.assertFalse(manifest.exists())
        self.assertFalse((manifest.parent / "report.pdf").exists())
        fork_env = {k: v for k, v in self.env.items()
                    if not k.startswith(("AWS_", "ARTIFACTS_"))}
        fork_env["GITHUB_EVENT_NAME"] = "pull_request"
        script = str(TOOL.parent / "wire_workflows.py")
        result = sh(self.repo, sys.executable, script, "--check",
                    ".github/workflows/metadata.yml", env=fork_env)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(metadata.read_text(), original)
        # The same excluded private pointer still requires hydration when read.
        required = sh(self.repo, sys.executable, script, "--check",
                      ".github/workflows/consumer.yml", env=fork_env, check=False)
        self.assertEqual(required.returncode, 1)
        sh(self.repo, sys.executable, script, ".github/workflows/consumer.yml",
           env=fork_env)
        self.assertIn("artifacts.py pull --jobs 16 docs/reports/private/report.pdf",
                      consumer.read_text())
        self.assertEqual(metadata.read_text(), original)

    def test_corrupt_remote_object_is_refused(self):
        self.art("push", "research/r1/runs/a.jsonl")
        digest = hashlib.sha256(self.big).hexdigest()
        obj = self.remote / "sha256" / digest[:2] / digest
        obj.write_bytes(b"x" * len(self.big))
        os.remove(self.repo / "research/r1/runs/a.jsonl")
        for p in (self.cache / "sha256").rglob("*"):
            if p.is_file():
                p.chmod(0o644)
                p.unlink()
        r = self.art("pull", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("refused", r.stderr)
        self.assertFalse((self.repo / "research/r1/runs/a.jsonl").exists())

    def test_push_merges_existing_manifest_and_gitignore(self):
        (self.repo / "research/r1/runs/.gitignore").write_text("/tmp/\n")
        self.art("push", "research/r1/runs/a.jsonl")
        self.art("push", "research/r1/runs")
        gi = (self.repo / "research/r1/runs/.gitignore").read_text()
        self.assertTrue(gi.startswith("/tmp/\n"))
        self.assertEqual(gi.count(artifacts.BEGIN), 1)
        self.assertIn("/weird \\[1\\]\\*.log", gi)
        m = json.loads((self.repo / "research/r1/runs/.artifacts.json").read_text())
        self.assertEqual(sorted(m["files"]), ["a.jsonl", "weird [1]*.log"])

    def test_push_from_sparse_checkout_reads_blobs(self):
        (self.repo / "research/r1/runs/.gitignore").write_text("/keep-me/\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "gitignore")
        self.git("sparse-checkout", "set", "--no-cone", "/*", "!/research/")
        self.assertFalse((self.repo / "research").exists())
        self.art("push", "research")
        self.git("commit", "-qm", "move from sparse")
        self.git("sparse-checkout", "disable")
        gi = (self.repo / "research/r1/runs/.gitignore").read_text()
        self.assertTrue(gi.startswith("/keep-me/\n"))
        self.assertNotIn("research/r1/runs/a.jsonl", self.git("ls-files"))
        self.art("pull")
        self.assertEqual((self.repo / "research/r1/runs/a.jsonl").read_bytes(), self.big)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_pull_into_absent_sparse_directory_preserves_bytes_and_clean_tree(self):
        self.art("push", "research/r1/runs/a.jsonl")
        self.git("commit", "-qm", "archive fixture")
        (self.repo / "research/r1/runs/a.jsonl").unlink()
        self.git("sparse-checkout", "set", "--no-cone", "/*", "!/research/")
        self.assertFalse((self.repo / "research").exists())
        self.art("pull", "research/r1/runs/a.jsonl")
        self.assertEqual((self.repo / "research/r1/runs/a.jsonl").read_bytes(), self.big)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_check_gate(self):
        base = self.git("rev-parse", "HEAD").strip()
        (self.repo / "new.jsonl").write_bytes(os.urandom(100_000))
        (self.repo / "tool.py").write_text("x = 1\n" * 300_000)
        self.git("add", "-A")
        self.git("commit", "-qm", "add data")
        r = self.art("check", base, check=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("new.jsonl", r.stdout)
        self.assertNotIn("tool.py", r.stdout)

        base = self.git("rev-parse", "HEAD").strip()
        self.art("push", "new.jsonl")
        self.git("commit", "-qm", "move it")
        self.assertEqual(self.art("check", base).returncode, 0)

    def test_migrate_from_subdirectory_resolves_root_level_candidates(self):
        base = self.git("rev-parse", "HEAD").strip()
        payload = os.urandom(100_000)
        (self.repo / "new.jsonl").write_bytes(payload)
        self.git("add", "new.jsonl")
        self.git("commit", "-qm", "add root-level data")
        caller = self.repo / "research"

        dry = self.art("migrate", base, "--dry-run", cwd=caller)
        self.assertIn("new.jsonl", dry.stdout)
        self.assertEqual(self.art("migrate", base, cwd=caller).returncode, 0)

        tracked = self.git("ls-files").splitlines()
        self.assertNotIn("new.jsonl", tracked)
        manifest = self.repo / ".artifacts.json"
        self.assertTrue(manifest.is_file())
        entry = json.loads(manifest.read_text())["files"]["new.jsonl"]
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(entry, {"sha256": digest, "bytes": len(payload)})
        self.assertEqual((self.remote / "sha256" / digest[:2] / digest).read_bytes(), payload)


class Policy(unittest.TestCase):
    P = artifacts.DEFAULT_POLICY

    def test_rules(self):
        f = artifacts.belongs_in_store
        self.assertTrue(f("a/b.jsonl", 70_000, self.P))
        self.assertFalse(f("a/b.jsonl", 60_000, self.P))
        self.assertTrue(f("a/b.json", 2 << 20, self.P))
        self.assertFalse(f("a/b.json", 500_000, self.P))
        self.assertFalse(f("src/big.rs", 5 << 20, self.P))
        self.assertTrue(f("x/fb.tar.part-0001", 100_000, self.P))
        self.assertFalse(f("x/.artifacts.json", 5 << 20, self.P))
        self.assertFalse(f("docs/browser/data.json", 30 << 20, {**self.P, "keep": ["docs/browser/data.json"]}))


class NeededPaths(unittest.TestCase):
    def test_sibling_doc_does_not_pull_whole_docs_tree(self):
        sys.path.insert(0, str(TOOL.parent))
        import wire_workflows as w
        moved = {"docs/reports/ecdlp-lead-discovery-20261024/report.pdf",
                 "knowledge/leads/ecdlp/coverage.tsv"}
        dirs = {"docs", "docs/reports", "docs/reports/ecdlp-lead-discovery-20261024",
                "knowledge", "knowledge/leads", "knowledge/leads/ecdlp"}
        self.assertEqual(w.needed("see docs/ci-tiers.md and .github/scripts/x.py", moved, dirs), [])
        self.assertEqual(
            w.needed("python3 tools/lead_atlas.py  # knowledge/leads/ecdlp/coverage.tsv", moved, dirs),
            ["knowledge/leads/ecdlp/coverage.tsv"],
        )


class S3Argv(unittest.TestCase):
    def setUp(self):
        cfg = artifacts.Config(root=Path("."), remote="s3://bucket/store", endpoint=None, read_url=None,
                               cache=Path("/c"), aws="aws")
        self.r = artifacts.Remote(cfg)
        self.d = hashlib.sha256(b"x").hexdigest()

    def test_layout_matches_crypto_store(self):
        self.assertEqual(self.r.key(self.d), f"store/sha256/{self.d[:2]}/{self.d}")

    def test_put_is_write_once_and_checksummed(self):
        a = self.r.put_args(self.d, Path("f"))
        self.assertEqual(a[a.index("--if-none-match") + 1], "*")
        self.assertEqual(a[a.index("--checksum-sha256") + 1], base64.b64encode(bytes.fromhex(self.d)).decode())
        self.assertEqual(a[a.index("--bucket") + 1], "bucket")

    def test_rejects_non_digest(self):
        with self.assertRaises(SystemExit):
            artifacts.object_key("../../etc/passwd")


class WorkflowWiring(unittest.TestCase):
    PATH = "examples/experiment-protocol/ecbench-l2-smoke-subset/session"

    def test_comment_only_data_path_does_not_require_pull(self):
        from wire_workflows import needed
        text = "# See docs/ci-tiers.md for the policy.\nrun: echo checked\n"
        moved = {"docs/reports/one/figure.png"}
        dirs = {"docs", "docs/reports", "docs/reports/one"}
        self.assertEqual(needed(text, moved, dirs), [])
        self.assertEqual(needed("run: echo docs/reports-s3.md\n", moved, dirs), [])
        self.assertEqual(needed("run: cat docs/reports/one/figure.png\n", moved, dirs),
                         ["docs/reports/one/figure.png"])

    def test_scope_only_checkout_stays_unwired(self):
        workflow = ("jobs:\n  changes:\n    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "        with:\n          sparse-checkout: .github/scripts\n"
                    "      - run: python3 .github/scripts/ci_scope.py\n")
        wired, _ = wire(workflow, ["coordination", "docs"])
        self.assertEqual(wired, workflow)

    def test_data_reading_checkout_still_gets_pull(self):
        workflow = ("jobs:\n  ledger:\n    steps:\n"
                    "      - uses: actions/checkout@v4\n"
                    "      - run: python3 tools/check_merge_hygiene.py\n")
        wired, _ = wire(workflow, ["coordination", "docs"])
        self.assertIn("artifacts.py pull --jobs 16 coordination docs", wired)

    def workflow(self):
        return ("jobs:\n"
                "  changes:\n"
                "    steps:\n"
                "      - run: echo checked\n"
                "  harness:\n"
                "    steps:\n"
                "      - run: |\n"
                f"          python3 tools/artifacts/artifacts.py pull {self.PATH}\n"
                f"          python3 tools/artifacts/artifacts.py verify {self.PATH}\n")

    def test_explicit_pull_and_verify_in_consumer(self):
        self.assertTrue(explicitly_pulled_and_verified(self.workflow(), [self.PATH]))

    def test_missing_verify_is_not_accepted(self):
        self.assertFalse(explicitly_pulled_and_verified(
            self.workflow().replace("artifacts.py verify", "artifacts.py list"), [self.PATH]))

    def test_missing_pull_is_not_accepted(self):
        self.assertFalse(explicitly_pulled_and_verified(
            self.workflow().replace("artifacts.py pull", "artifacts.py list"), [self.PATH]))

    def test_pull_in_one_job_does_not_cover_another_consumer(self):
        other = f"  second-consumer:\n    steps:\n      - run: cat {self.PATH}/records.jsonl\n"
        self.assertFalse(explicitly_pulled_and_verified(self.workflow() + other, [self.PATH]))

    def test_only_documented_metadata_workflows_skip_private_hydration(self):
        self.assertTrue(metadata_only("# artifact-store: no-pull (metadata-only checks)\n"))
        self.assertFalse(metadata_only(self.workflow()))



class WorkflowBootstrap(unittest.TestCase):
    def test_sparse_clone_can_load_tool_and_remote_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sh(root, "git", "init", "-q", "-b", "main")
            for name, content in {".github/scripts/scope.py": "", "tools/artifacts/artifacts.py": TOOL.read_text(), ".artifacts/config.json": '{"remote":"file:///test-store"}'}.items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            sh(root, "git", "add", ".")
            sh(root, "git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")
            block = ["      - uses: actions/checkout@v4", "        with:", "          sparse-checkout: .github/scripts"]
            wired = wire_workflows.add_sparse_pattern(block, "      ")
            patterns = [line.strip() for line in wired[3:]]
            sh(root, "git", "sparse-checkout", "set", "--cone", *patterns)
            self.assertTrue((root / "tools/artifacts/artifacts.py").is_file())
            self.assertEqual(artifacts.Config.load(root).remote, "file:///test-store")

    def test_conditional_full_checkout_is_preserved(self):
        block = ["      - uses: actions/checkout@v4", "        with:", "          sparse-checkout: ${{ needs.changes.outputs.full_checkout != 'true' && env.SPARSE_RULES || '' }}", "          sparse-checkout-cone-mode: false"]
        self.assertEqual(wire_workflows.add_sparse_pattern(block, "      "), block)

    def test_rewiring_refreshes_paths_and_keeps_checkout_condition(self):
        source = "jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n        if: needs.changes.outputs.run == 'true'\n      - run: make check\n"
        once, _ = wire_workflows.wire(source, ["data/new"])
        self.assertEqual(once, wire_workflows.wire(once, ["data/new"])[0])
        stale = once.replace("pull --jobs 16 data/new", "pull data/old")
        self.assertEqual(once, wire_workflows.wire(stale, ["data/new"])[0])
        self.assertEqual(once.count("if: needs.changes.outputs.run == 'true'"), 2)
        self.assertIn("shell: bash", once)
        self.assertIn("working-directory: ${{ github.workspace }}", once)
        self.assertIn('export ARTIFACTS_AWS="$artifacts_cli_aws"', once)

if __name__ == "__main__":
    unittest.main()
