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
