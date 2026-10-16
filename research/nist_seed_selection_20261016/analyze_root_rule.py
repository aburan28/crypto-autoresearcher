#!/usr/bin/env python3
"""Record the observed coefficient-root convention without assuming intent."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "root_choice_pattern.json"
    if output.exists():
        raise FileExistsError(output)
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    anchors = {}
    source = ROOT / "raw" / "candidates.jsonl"
    for line in source.open():
        row = json.loads(line)
        target = targets[row["target"]]
        if row["kind"] != "prime" or row["index"] != target["candidate_index"]:
            continue
        p = int(target["p"])
        c = int(row["variants"]["nist_fips_186_2"]["c"], 16)
        roots = [int(b, 16) for b in row["variants"]["nist_fips_186_2"]["b_roots"]]
        if len(roots) != 2:
            raise ArithmeticError(f"anchor root count: {row['target']}")
        canonical = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p) if p % 4 == 3 else min(roots)
        published = int(target["published_b"])
        if published not in roots:
            raise ArithmeticError(f"published root missing: {row['target']}")
        anchors[row["target"]] = {"p_mod_4": p % 4,
                                  "canonical_rule": "power_(p_plus_1)_over_4" if p % 4 == 3 else "smaller_numeric_root",
                                  "published_matches_canonical": published == canonical,
                                  "published_b": hex(published), "other_b": hex(p - published)}
    if len(anchors) != 10:
        raise ArithmeticError("missing published prime anchors")
    result = {"candidate_sha256": digest(source), "anchors": anchors,
              "p_3_mod_4_match_count": sum(item["p_mod_4"] == 3 and item["published_matches_canonical"]
                                           for item in anchors.values()),
              "p_3_mod_4_total": sum(item["p_mod_4"] == 3 for item in anchors.values()),
              "interpretation": "Observed output convention only; the historical square-root implementation is unknown."}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "matches": result["p_3_mod_4_match_count"],
                      "total": result["p_3_mod_4_total"], "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
