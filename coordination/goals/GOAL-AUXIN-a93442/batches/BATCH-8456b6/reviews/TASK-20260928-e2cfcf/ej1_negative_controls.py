#!/usr/bin/env python3
"""EJ1 negative controls for TASK-20260928-e2cfcf. Builds scratch copies of the
draft in scratch/ beside this file by single raw-byte edits, runs ej1_verify on
each, records the scratch sha256 and the verifier's findings, then removes the
scratch copies (each is reproducible from the draft and the edit recorded here).

Usage (repository root): python3 ej1_negative_controls.py <draft.yaml> <out.json>
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ej1_verify  # noqa: E402

EDITS = [
    ("NC-EJ1-a flip one byte in entry T-0001 text",
     b"text: isqrt(n) is the largest integer", b"text: isqrU(n) is the largest integer"),
    ("NC-EJ1-b change one character of T-0010 char_range end (229 -> 228)",
     b"kind: loaded_value\n        char_range:\n        - 0\n        - 229\n",
     b"kind: loaded_value\n        char_range:\n        - 0\n        - 228\n"),
    ("NC-EJ1-c change one character of T-0337 line_col_range end column (22 -> 21)",
     b"line_col_range:\n        - 1469\n        - 20\n        - 1469\n        - 22\n",
     b"line_col_range:\n        - 1469\n        - 20\n        - 1469\n        - 21\n"),
]


def main(draft, out):
    raw = Path(draft).read_bytes()
    scratch = HERE / "scratch"
    scratch.mkdir(exist_ok=True)
    results = []
    for i, (label, old, new) in enumerate(EDITS):
        n = raw.count(old)
        if n != 1:
            results.append({"control": label, "error": f"edit anchor occurs {n} times"})
            continue
        mod = raw.replace(old, new)
        diff_bytes = sum(1 for a, b in zip(raw, mod) if a != b)
        p = scratch / f"nc{i}.yaml"
        p.write_bytes(mod)
        s, _ = ej1_verify.verify(str(p))
        results.append({"control": label, "old": old.decode(), "new": new.decode(),
                        "bytes_changed": diff_bytes,
                        "scratch_sha256": hashlib.sha256(mod).hexdigest(),
                        "verifier_findings": s["findings"],
                        "detected": bool(s["findings"])})
        p.unlink()
    scratch.rmdir()
    json.dump(results, open(out, "w"), indent=1)
    print(json.dumps(results, indent=1))
    return 0 if all(r.get("detected") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
