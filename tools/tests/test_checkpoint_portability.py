"""Offline checkpoint regressions: actual gate tests still use real S3."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class CheckpointPortability(unittest.TestCase):
    def test_clean_and_untracked_worktrees(self):
        source=Path(__file__).resolve().parents[2]/"scripts/checkpoint.sh"
        for untracked in (False,True):
            with self.subTest(untracked=untracked), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                (root/"scripts").mkdir()
                shutil.copy(source,root/"scripts/checkpoint.sh")
                (root/".gitignore").write_text(".resume/\nmock-bin/\nmock-copies/\n")
                subprocess.run(["git","init","-q",str(root)],check=True)
                subprocess.run(["git","add","scripts/checkpoint.sh",".gitignore"],cwd=root,check=True)
                subprocess.run(["git","-c","user.name=Checkpoint Test","-c","user.email=test@example.invalid",
                                "commit","-qm","fixture"],cwd=root,check=True)
                (root/".resume").mkdir()
                (root/".resume/RESUME.md").write_text("offline checkpoint fixture\n")
                if untracked:
                    (root/"scientific-input.json").write_text('{"retained":true}\n')
                mock=root/"mock-bin"
                mock.mkdir()
                copies=root/"mock-copies"
                copies.mkdir()
                aws=mock/"aws"
                aws.write_text("#!/usr/bin/env python3\nimport os,sys,shutil\nfrom pathlib import Path\n"
                    "a=sys.argv[1:]\n"
                    "if a==['configure','list-profiles']: print('checkpoint-test')\n"
                    "elif 'cp' in a: shutil.copy(a[-2],Path(os.environ['CHECKPOINT_TEST_COPIES'])/Path(a[-1]).name)\n"
                    "else: raise SystemExit(2)\n")
                aws.chmod(0o755)
                env=dict(os.environ,PATH=str(mock)+os.pathsep+os.environ["PATH"],
                         CHECKPOINT_AWS_PROFILE="checkpoint-test",CHECKPOINT_TEST_COPIES=str(copies),
                         CHECKPOINT_TOKEN_FILE=str(root/"missing-token"),CHECKPOINT_UPLOAD_TOKEN="")
                result=subprocess.run(["bash","scripts/checkpoint.sh","push"],cwd=root,env=env,
                                      capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertTrue((copies/"checkpoint.tar.gz").is_file())
                self.assertTrue((copies/"meta.json").is_file())
                replay=subprocess.run(["bash","scripts/checkpoint.sh","push"],cwd=root,env=env,
                                      capture_output=True,text=True)
                self.assertEqual(replay.returncode,0,replay.stdout+replay.stderr)
                self.assertIn("unchanged since",replay.stdout)


if __name__=="__main__":
    unittest.main()
