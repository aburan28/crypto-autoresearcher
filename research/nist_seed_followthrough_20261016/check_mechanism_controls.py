#!/usr/bin/env python3
"""Independent positive/negative controls for the bounded CM predicate."""

import hashlib
import json
import sys
from pathlib import Path

from compare_mechanisms import square_cm_fields


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "raw/mechanism_controls.json"
SOURCE_URL = "https://www.secg.org/sec2-v2.pdf"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    # SEC 2 v2.0 section 2.4.1 supplies these independent domain parameters.
    p = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
    n = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
    delta = (p + 1 - n) ** 2 - 4 * p
    positive = square_cm_fields(delta)
    negative = square_cm_fields(delta - 1)
    if not any(x["fundamental_discriminant"] == -3 for x in positive):
        raise AssertionError("secp256k1 CM-field control missed")
    if negative:
        raise AssertionError("perturbed-discriminant negative control matched")
    rows = json.loads((HERE / "raw/mechanism_comparison.json").read_text())["rows"]
    if not rows or any(square_cm_fields(int(r["frobenius_discriminant"]))
                       != r["small_cm_field_matches"] for r in rows):
        raise AssertionError("recorded CM predicates disagree")
    result = {"status": "controls_passed", "command": sys.argv,
              "script_sha256": digest(Path(__file__)),
              "comparison_sha256": digest(HERE / "raw/mechanism_comparison.json"),
              "sec2_source_url": SOURCE_URL, "sec2_section": "2.4.1",
              "secp256k1_p": str(p), "secp256k1_n": str(n),
              "secp256k1_delta": str(delta), "positive_matches": positive,
              "perturbed_delta": str(delta - 1), "negative_matches": negative,
              "comparison_branches_rechecked": len(rows)}
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(OUTPUT), "sha256": digest(OUTPUT),
                      "positive": len(positive), "negative": len(negative)}))


if __name__ == "__main__":
    main()
