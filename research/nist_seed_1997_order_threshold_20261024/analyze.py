#!/usr/bin/env python3
"""Exact, source-pinned lower-order-threshold audit for four NIST/ANSI fields."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCES = {
    "skipped": ("research/nist_seed_skipped_curves_20261016/assessed.json", "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841"),
    "targets": ("research/nist_seed_selection_20261016/targets.json", "cff434d44e48b457b481c45e7cb6dcb137e8b34e7656281cb25c9d51721008a3"),
    "certificates": ("research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl", "7902083817b988f00d562dc55f5c9bf5e0fa822fc0400618e6738acfb4990fb2"),
    "labels": ("research/nist_seed_selection_deep_20261016/selection_matrix.json", "d93eabf58eecdb48cb74657d28e985c965bc6ca8a74ec02e468846e8c77329b6"),
}


def source(name):
    relative, digest = SOURCES[name]
    path = ROOT / relative
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, relative
    return raw


def main():
    skipped = json.loads(source("skipped"))["candidate_rows"]
    targets = json.loads(source("targets"))
    certificates = [json.loads(line) for line in source("certificates").splitlines()]
    labels = json.loads(source("labels"))["rows"]
    assert len(skipped) == 11
    index = defaultdict(list)
    for cert in certificates:
        if cert.get("record") == "certificate" and cert.get("order_certified"):
            assert cert["n_prime_pari"] and cert["n_times_point_identity"]
            index[(cert["run"], cert["seed"].lower())].append(cert)
    rows = []
    omitted_fields = {int(s["p_hex"], 16) for s in skipped}
    assert len(omitted_fields) == 4
    for s in skipped:
        rows.append({"label": "omitted", "name": s["identity"]["alias"] if isinstance(s["identity"], dict) and "alias" in s["identity"] else f"{int(s['p_hex'],16).bit_length()} / {s['seed_ordinal_one_based']}", "ordinal": s["seed_ordinal_one_based"], "seed": s["seed_hex"].lower(), "run": s["timestamp"], "p": int(s["p_hex"], 16), "n": int(s["n_hex"], 16)})
    for t in targets:
        if t["kind"] != "prime" or int(t["p"]) not in omitted_fields:
            continue
        rows.append({"label": "published", "name": t["name"], "ordinal": t["candidate_index"], "seed": t["published_seed"].lower(), "run": t["unix_time"], "p": int(t["p"]), "n": int(t["published_subgroup_order"])})
    assert len(rows) == 19 and sum(r["label"] == "published" for r in rows) == 8
    label_keys = {(r["timestamp"], r["seed_hex"].lower()) for r in labels}
    assert len(label_keys) == 21
    for row in rows:
        assert (row["run"], row["seed"]) in label_keys
        certs = index[(row["run"], row["seed"])]
        assert any(int(c["p"]) == row["p"] and int(c["n"]) == row["n"] for c in certs), row["name"]
        row["field_bits"] = row["p"].bit_length()
        row["n_minus_p"] = row["n"] - row["p"]
    groups = defaultdict(lambda: {"published": [], "omitted": []})
    for row in rows:
        groups[row["field_bits"]][row["label"]].append(row)
    summary = []
    for bits, group in sorted(groups.items()):
        pub = group["published"]
        omit = group["omitted"]
        floor = min(r["n"] for r in pub)
        forced = [r["ordinal"] for r in omit if r["n"] >= floor]
        boundary_passes = [r["ordinal"] for r in omit if r["n"] >= floor]
        assert forced == boundary_passes
        summary.append({"field_bits": bits, "published_count": len(pub), "omitted_count": len(omit), "published_min_n": str(floor), "omitted_max_n": str(max(r["n"] for r in omit)), "unavoidable_omission_ordinals": sorted(forced), "unavoidable_omission_count": len(forced), "separator_exists": max(r["n"] for r in omit) < floor})
    assert [(s["field_bits"], s["unavoidable_omission_count"]) for s in summary] == [(192, 1), (224, 3), (239, 3), (256, 0)]
    result = {"scope": "post-observation field-fixed r_min theorem audit, conditional on candidate visitation", "source_sha256": {k: v[1] for k, v in SOURCES.items()}, "rows": sorted(rows, key=lambda r: (r["field_bits"], r["ordinal"], r["label"])), "fields": summary, "total_unavoidable_omissions": sum(s["unavoidable_omission_count"] for s in summary), "complete_separator_all_four_fields": all(s["separator_exists"] for s in summary)}
    (HERE / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{len(rows)} exact rows; {result['total_unavoidable_omissions']} of 11 omissions pass every field-fixed r_min admitting all 8 published controls")


if __name__ == "__main__":
    main()
