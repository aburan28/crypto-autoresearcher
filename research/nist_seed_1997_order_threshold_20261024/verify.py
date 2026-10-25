#!/usr/bin/env python3
"""Independent source-row and pairwise-order replay of analysis.json."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
record = json.loads((here / "analysis.json").read_text())
skip_path = root / "research/nist_seed_skipped_curves_20261016/assessed.json"
target_path = root / "research/nist_seed_selection_20261016/targets.json"
for key, path in (("skipped", skip_path), ("targets", target_path)):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["source_sha256"][key]
skipped = json.loads(skip_path.read_text())["candidate_rows"]
targets = json.loads(target_path.read_text())
sources = {}
for s in skipped:
    sources[(s["timestamp"], s["seed_hex"].lower())] = (int(s["p_hex"], 16), int(s["n_hex"], 16), "omitted")
for t in targets:
    if t["kind"] == "prime" and t["name"] not in ("P-384", "P-521"):
        sources[(t["unix_time"], t["published_seed"].lower())] = (int(t["p"]), int(t["published_subgroup_order"]), "published")
assert len(sources) == 19
assert len(record["rows"]) == 19
by_field = defaultdict(lambda: {"published": [], "omitted": []})
for row in record["rows"]:
    p, n, label = sources.pop((row["run"], row["seed"]))
    assert (row["p"], row["n"], row["label"], row["n_minus_p"]) == (p, n, label, n-p)
    by_field[p][label].append((n, row["ordinal"]))
assert not sources
total = 0
for field in record["fields"]:
    matching = [items for p, items in by_field.items() if p.bit_length() == field["field_bits"]]
    assert len(matching) == 1
    items = matching[0]
    pub = items["published"]
    omit = items["omitted"]
    assert len(pub) == field["published_count"] and len(omit) == field["omitted_count"]
    # An omitted n survives every accepting lower threshold iff at least one
    # published order is at most that n (equivalently: min published n <= n).
    forced = sorted(ordinal for n, ordinal in omit if any(pn <= n for pn, _ in pub))
    assert forced == field["unavoidable_omission_ordinals"]
    assert str(min(n for n, _ in pub)) == field["published_min_n"]
    assert str(max(n for n, _ in omit)) == field["omitted_max_n"]
    assert field["separator_exists"] == (len(forced) == 0)
    total += len(forced)
assert total == record["total_unavoidable_omissions"] == 7
assert record["complete_separator_all_four_fields"] is False
print("independent pairwise replay: 19 rows, four fields, seven unavoidable omissions")
