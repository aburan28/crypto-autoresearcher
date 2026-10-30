"""Execute checkpoint argument parsing and deferred cleanup without network access."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/checkpoint.sh"


class CheckpointQuoting(unittest.TestCase):
    def test_clean_and_only_excluded_untracked_files_have_a_state_hash(self):
        source = SCRIPT.read_text()
        functions = '\n'.join(re.search(r'(?ms)^'+name+r'\(\) \{.*?^\}', source).group()
                              for name in ('file_stat', 'state_hash'))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git','init','-q'],cwd=root,check=True)
            (root/'tracked.txt').write_text('fixed input\n')
            subprocess.run(['git','add','tracked.txt'],cwd=root,check=True)
            subprocess.run(['git','-c','user.name=Checkpoint test','-c','user.email=test@example.invalid',
                            'commit','-qm','fixture'],cwd=root,check=True)
            code = ('set -euo pipefail\nEXCLUDE_RE="(^|/)(target|node_modules|\\.git)/"\n'
                    +functions+'\nstate_hash\n')
            values = []
            for relative in (None, '.resume/untracked-note', 'node_modules/untracked-build'):
                if relative:
                    path=root/relative
                    path.parent.mkdir(parents=True,exist_ok=True)
                    path.write_text('excluded from checkpoint state\n')
                result=subprocess.run(['bash','-c',code],cwd=root,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertRegex(result.stdout,r'^[0-9a-f]{64}\n$')
                values.append(result.stdout)
            self.assertEqual(len(set(values)),1)

    def test_metadata_size_is_one_integer_with_quoted_path(self):
        function = re.search(r"(?ms)^file_stat\(\) \{.*?^\}", SCRIPT.read_text()).group()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a ' quoted file.txt"
            path.write_bytes(b"three")
            result = subprocess.run(
                ["bash", "-c", function+'\nfile_stat "$1" size', "checkpoint-test", str(path)],
                text=True, capture_output=True, check=True)
            self.assertEqual(result.stdout, "5\n")
            self.assertEqual(result.stderr, "")
            fingerprint = subprocess.run(
                ["bash", "-c", function+'\nfile_stat "$1"', "checkpoint-test", str(path)],
                text=True, capture_output=True, check=True)
            self.assertEqual(fingerprint.stdout.strip(), f"{path} 5 {path.stat().st_mtime_ns}")

    def test_share_preserves_literal_reference_components(self):
        source = SCRIPT.read_text()
        function = re.search(r"(?ms)^cmd_share\(\) \{.*?^\}", source).group()
        stub = '''index_lookup() {
python3 -c 'import json,os,sys; open(os.environ["LOOKUP_ARGS"],"w").write(json.dumps(sys.argv[1:])); print("stamp https://example.invalid/checkpoint")' "$@"
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "branch-one").touch()
            (root / "branch-two").touch()
            args = root / "args.json"
            for ref, expected in [
                ("crypto/feature__ci/stamp", ["crypto", "feature__ci", "stamp"]),
                ("crypto/branch*/stamp", ["crypto", "branch*", "stamp"]),
                ("crypto/branch with spaces/stamp", ["crypto", "branch with spaces", "stamp"]),
            ]:
                result = subprocess.run(
                    ["bash", "-c", "set -euo pipefail\n" + function + "\n" + stub + '\ncmd_share "$1"', "checkpoint-test", ref],
                    cwd=root, env={**os.environ, "LOOKUP_ARGS": str(args)},
                    text=True, capture_output=True, check=True,
                )
                self.assertEqual(json.loads(args.read_text()), expected)
                self.assertEqual(result.stdout.strip(), "https://example.invalid/checkpoint")

    def test_return_cleanup_handles_quotes_and_spaces_in_stage_path(self):
        trap = next(line.strip() for line in SCRIPT.read_text().splitlines()
                    if line.strip().startswith("trap ") and "stage" in line and "RETURN" in line)
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / "checkpoint ' with spaces"
            stage.mkdir()
            code = 'set -euo pipefail\ncleanup_test() {\nlocal stage="$1"\n' + trap + '\nreturn 0\n}\ncleanup_test "$1"'
            subprocess.run(["bash", "-c", code, "checkpoint-test", str(stage)],
                           check=True, text=True, capture_output=True)
            self.assertFalse(stage.exists())


if __name__ == "__main__":
    unittest.main()
