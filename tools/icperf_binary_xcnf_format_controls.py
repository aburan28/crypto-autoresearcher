"""Record two tiny local CryptoMiniSat XCNF parity-format controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    binary_name = shutil.which("cryptominisat5")
    if binary_name is None:
        raise SystemExit("cryptominisat5 is not installed; format control unavailable")
    binary = Path(binary_name).resolve()
    rows = []
    cases = [("xor_one", "x1 2 0", "v 1 -2 0"),
             ("xor_zero", "x-1 2 0", "v 1 2 0")]
    with tempfile.TemporaryDirectory(prefix="icperf-xcnf-format-") as folder:
        for name, parity, expected in cases:
            formula = f"p cnf 2 2\n{parity}\n1 0\n".encode("ascii")
            path = Path(folder) / f"{name}.xcnf"
            path.write_bytes(formula)
            command = [str(binary), "--verb", "0", str(path)]
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=10, check=False)
            assert result.returncode == 10
            assert "s SATISFIABLE" in result.stdout and expected in result.stdout
            rows.append({"case": name, "input_ascii": formula.decode("ascii"),
                         "input_sha256": digest(formula), "command": command,
                         "exit_code": result.returncode, "stdout": result.stdout,
                         "stderr": result.stderr, "expected_model_line": expected,
                         "matched_expected": True})
    record = {"schema": "icperf-binary-xcnf-format-controls-v1",
              "scope": "two-variable syntax controls only; no selected IC formula solved",
              "source_sha256": digest(Path(__file__).read_bytes()),
              "binary_path": str(binary), "binary_sha256": digest(binary.read_bytes()),
              "controls": rows}
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"path": str(args.out), "passed": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
