"""Check that the three Lean factor definitions are the frozen bitmask polynomials."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def mask(expression: str) -> int:
    terms = expression.split(" + ")
    result = 0
    for term in terms:
        if term == "1":
            exponent = 0
        elif term == "X":
            exponent = 1
        else:
            match = re.fullmatch(r"X\^(\d+)", term)
            assert match, f"unrecognized polynomial term {term!r}"
            exponent = int(match.group(1))
        bit = 1 << exponent
        assert not result & bit, f"duplicate term {term!r}"
        result |= bit
    return result


def check(repo: Path) -> dict:
    source_paths = [
        repo / "experiments/EXP-BINSTD-8bdf86/stage1-ell89/admissible-phi-dims.json",
        repo / "experiments/EXP-BINSTD-8bdf86/stage1-ell89r1/admissible-phi-dims.json",
    ]
    sources = [path.read_bytes() for path in source_paths]
    assert sources[0] == sources[1]
    frozen = json.loads(sources[0])
    assert frozen["n"] == 17
    assert [item["poly"] for item in frozen["factors"]] == [3, 313, 471]
    lean_path = repo / "formal/CryptoResearch/Binstd/Factorization.lean"
    lean_bytes = lean_path.read_bytes()
    definitions = dict(re.findall(
        r"^noncomputable def (factor\w+) : F2\[X\] := (.+)$",
        lean_bytes.decode(), flags=re.MULTILINE,
    ))
    assert set(definitions) == {"factor1", "factor8a", "factor8b"}
    observed = [mask(definitions[name]) for name in ("factor1", "factor8a", "factor8b")]
    assert observed == [item["poly"] for item in frozen["factors"]]
    return {
        "schema": "binstd-factor17-source-binding-v1",
        "frozen_source_sha256": hashlib.sha256(sources[0]).hexdigest(),
        "lean_source_sha256": hashlib.sha256(lean_bytes).hexdigest(),
        "bitmask_factors": observed,
        "source_files_equal": True,
        "scope": "binds constants to frozen factor bitmasks; does not check irreducibility or module classification",
    }


if __name__ == "__main__":
    print(json.dumps(check(Path(sys.argv[1]).resolve()), indent=2, sort_keys=True))
