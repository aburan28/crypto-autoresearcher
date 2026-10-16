#!/usr/bin/env python3
"""Recompute scoped findings from immutable candidate and evaluation records."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluation(name, end):
    path = ROOT / "raw" / "evaluations" / name / f"{1:05d}-{end:05d}.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines()]
    if len(records) - 1 != end or records[0]["candidate_sha256"] != digest(ROOT / "raw" / "candidates.jsonl"):
        raise ArithmeticError(f"incomplete or stale {name} evaluation")
    return path, records[1:]


def main():
    if not json.loads((ROOT / "raw" / "controls.json").read_text())["all_passed"]:
        raise ArithmeticError("controls not passed")
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    screen = json.loads((ROOT / "raw" / "screening_summary.json").read_text())
    if screen["total_target_candidate_pairs"] != 31945 or not all(
        screen["anchors"].get(name) for name in targets
    ):
        raise ArithmeticError("generator anchors incomplete")
    prime_certs = json.loads((ROOT / "raw" / "prime_order_certificates.json").read_text())["certificates"]
    p192_certs = json.loads((ROOT / "raw" / "p192_skipped_x9_certificates.json").read_text())["certificates"]
    binary_certs = json.loads((ROOT / "raw" / "binary_order_certificates.json").read_text())["certificates"]
    if not all(row["order_certified"] for row in prime_certs) or not all(
        row["group_order_certified"] for row in p192_certs + binary_certs
    ):
        raise ArithmeticError("independent certificate incomplete")
    binary = {}
    artifact_hashes = {"candidates": digest(ROOT / "raw" / "candidates.jsonl"),
                       "screening": digest(ROOT / "raw" / "screening_summary.json"),
                       "controls": digest(ROOT / "raw" / "controls.json"),
                       "prime_2torsion": digest(ROOT / "raw" / "prime_2torsion_screen.jsonl"),
                       "prime_3torsion": digest(ROOT / "raw" / "prime_3torsion_screen.jsonl"),
                       "prime_order_certificates": digest(ROOT / "raw" / "prime_order_certificates.json"),
                       "p192_skipped_x9_certificates": digest(ROOT / "raw" / "p192_skipped_x9_certificates.json"),
                       "binary_order_certificates": digest(ROOT / "raw" / "binary_order_certificates.json")}
    for name in ("B-233", "B-283", "B-409", "B-571"):
        path, rows = evaluation(name, targets[name]["candidate_index"])
        artifact_hashes[name] = digest(path)
        if any(row["status"] != "COUNTED" for row in rows) or not rows[-1]["anchor_order_matches"]:
            raise ArithmeticError(f"incomplete binary stream {name}")
        family = [row for row in rows[:-1] if row["checks"]["family_accept"]]
        reference = [row for row in rows[:-1] if row["checks"]["x9_reference_accept"]]
        binary[name] = {
            "tested": len(rows), "earlier": len(rows) - 1,
            "earlier_family_profile_count": len(family),
            "earlier_x9_255_reference_count": len(reference),
            "earlier_x9_255_reference": [{"index": row["index"], "seed": row["seed"], "b_polynomial": row["b"],
                                          "cofactor": row["checks"]["x9_255_smooth_cofactor"],
                                          "prime_subgroup": row["checks"]["x9_remainder"],
                                          "subgroup_bits": int(row["checks"]["x9_remainder"]).bit_length()}
                                         for row in reference],
        }
    path, p192 = evaluation("P-192", 139)
    artifact_hashes["P-192"] = digest(path)
    if not p192[-1]["anchor_order_matches"] or any(row["status"] == "INDETERMINATE" for row in p192):
        raise ArithmeticError("P-192 stream incomplete")
    candidate_by_index = {}
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        row = json.loads(line)
        if row["target"] == "P-192":
            candidate_by_index[row["index"]] = row
    family = []
    order_only = []
    strict = []
    for row in p192[:-1]:
        if row["status"] != "COUNTED":
            continue
        source = candidate_by_index[row["index"]]
        same_c = source["variants"]["nist_fips_186_2"]["c"] == source["variants"]["ansi_x9_62_1998"]["c"]
        for root in ("canonical", "other"):
            checked = row[root]
            if checked["family_accept"]:
                family.append({"index": row["index"], "root": root})
            if checked["x9_reference_accept"]:
                entry = {"index": row["index"], "seed": row["seed"], "root": root,
                         "b": row["canonical_b"] if root == "canonical" else row["other_b"],
                         "cofactor": checked["x9_255_smooth_cofactor"],
                         "prime_subgroup": checked["x9_remainder"],
                         "subgroup_bits": int(checked["x9_remainder"]).bit_length(),
                         "strict_x9_seed_mapping_matches": same_c}
                order_only.append(entry)
                if same_c:
                    strict.append(entry)
    if sorted({row["index"] for row in strict}) != sorted({row["index"] for row in p192_certs}):
        raise ArithmeticError("P-192 strict-X9 certificates do not cover all survivors")
    p256_path = ROOT / "raw" / "evaluations" / "P-256" / "00876-00876.jsonl"
    p256 = json.loads(p256_path.read_text().splitlines()[1])
    artifact_hashes["P-256:876"] = digest(p256_path)
    if p256["status"] != "COUNTED" or not p256["canonical"]["family_accept"] or not any(
        row["name"] == "P-256:876" and row["order_certified"] for row in prime_certs
    ):
        raise ArithmeticError("P-256 candidate 876 missing confirmation")
    two_torsion = json.loads((ROOT / "raw" / "prime_2torsion_screen.jsonl").read_text().splitlines()[-1])["counts"]
    three_torsion = json.loads((ROOT / "raw" / "prime_3torsion_screen.jsonl").read_text().splitlines()[-1])["counts"]
    summary = {
        "status": "partial_exact_prime_screen_complete_binary_and_p192",
        "candidate_pairs_including_anchors": 31945,
        "candidate_pairs_earlier": 31931,
        "prime_anchor_coefficients_strict_x9_matches": sum(bool(screen["anchors"].get(name + ":strict_x9_matches_coefficient"))
                                                            for name, target in targets.items() if target["kind"] == "prime"),
        "prime_anchor_coefficients_total": 10,
        "prime_2torsion_screen": two_torsion,
        "prime_3torsion_branch_screen": three_torsion,
        "binary": binary,
        "P-192": {"tested": 139, "earlier_family_profile": family,
                  "earlier_x9_order_reference_count": len(order_only),
                  "earlier_x9_order_reference": order_only,
                  "earlier_strict_x9_255_reference_count": len(strict),
                  "earlier_strict_x9_255_reference": strict},
        "P-256:876": {"seed": p256["seed"], "b": p256["canonical_b"],
                       "prime_order": p256["canonical"]["order"],
                       "family_accept": True, "strict_x9_seed_mapping_matches": p256["strict_x9_same_c"]},
        "binary_all_earlier_family_profile": sum(item["earlier_family_profile_count"] for item in binary.values()),
        "binary_all_earlier_x9_255_reference": sum(item["earlier_x9_255_reference_count"] for item in binary.values()),
        "artifact_sha256": artifact_hashes,
        "limitation": "Other prime-field streams lack complete exact point counts; X9 lmax and rmin are reference settings, not a recovered private stopping rule.",
    }
    output = ROOT / "raw" / "analysis_summary.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output), "binary_x9_skips": summary["binary_all_earlier_x9_255_reference"],
                      "p192_strict_x9_skips": len(strict)}, sort_keys=True))


if __name__ == "__main__":
    main()
