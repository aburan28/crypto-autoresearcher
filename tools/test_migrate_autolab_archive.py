import json
import tempfile
import unittest
from pathlib import Path

from tools.migrate_autolab_archive import (
    build_task_catalog,
    copy_and_hash,
    enumerate_bindings,
    tree_hash,
)


class AutolabMigrationTest(unittest.TestCase):
    def test_copy_catalog_and_exclusions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            task = source / "tasks" / "crypto_task"
            task.mkdir(parents=True)
            (task / "task.toml").write_text(
                '[metadata]\ndomain="puzzle_and_challenge"\ntags=["cryptography"]\n',
                encoding="utf-8",
            )
            (task / "instruction.md").write_text("task\n", encoding="utf-8")
            (task / "trial_result.json").write_text('{"ok": true}\n', encoding="utf-8")
            (task / "dangling").symlink_to("missing-target")
            external = root / "external-directory"
            external.mkdir()
            (task / "directory-alias").symlink_to(external, target_is_directory=True)
            cache = task / "__pycache__"
            cache.mkdir()
            (cache / "skip.pyc").write_bytes(b"skip")
            (task / "._instruction.md").write_bytes(b"skip")

            bindings, excluded = enumerate_bindings(source, destination, ("tasks",))
            rows = [copy_and_hash(binding, verify_only=False) for binding in bindings]
            catalog = build_task_catalog(source, rows)

            self.assertEqual(len(rows), 5)
            self.assertEqual(len(catalog), 1)
            self.assertEqual(catalog[0]["result_like_file_count"], 1)
            self.assertEqual(excluded["excluded_file"], 1)
            self.assertEqual(len(tree_hash(rows)), 64)
            self.assertTrue((destination / "tasks" / "crypto_task" / "instruction.md").is_file())
            self.assertEqual(
                (destination / "tasks" / "crypto_task" / "dangling").readlink(),
                Path("missing-target"),
            )
            self.assertEqual(
                (destination / "tasks" / "crypto_task" / "directory-alias").readlink(),
                external,
            )

    def test_verify_only_reports_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "destination"
            (source / "output").mkdir(parents=True)
            (source / "output" / "result.json").write_text("{}\n", encoding="utf-8")
            bindings, _ = enumerate_bindings(source, destination, ("output",))
            row = copy_and_hash(bindings[0], verify_only=True)
            self.assertEqual(row["status"], "missing")
            self.assertFalse((destination / "output" / "result.json").exists())


if __name__ == "__main__":
    unittest.main()
