"""Independent recheck of protocol.json 'gates' from raw producer records (stdout only).
argv: panel_dir protocol.json"""
import base64, json, sys
from pathlib import Path
panel = Path(sys.argv[1]); proto = json.load(open(sys.argv[2]))
rows = [json.loads(l) for l in (panel / "runs.jsonl").read_text().splitlines() if l.strip()]
def raw(r):
    t = (panel / r["stdout_file"]).read_text()
    return json.loads(base64.b64decode([l for l in t.splitlines() if l.startswith("raw_b64=")][0][8:]))
idx = proto["online"]["index_digest"]
units = {}
fails = []
for r in rows:
    o = raw(r)
    if o.get("issues"): fails.append(("issues", r["serial"], o["issues"]))
    units.setdefault(r["point_id"], {})[r["arm"]] = (r, o)
    if r["arm"] == "rT": continue
    tg = [x for x in o["records"] if x.get("kind") == "compact_orbit_dlp_target"][0]
    sm = [x for x in o["records"] if x.get("kind") == "compact_orbit_dlp_summary"][0]
    arm = proto["arms"][r["arm"]]
    exp_slots = proto["online"]["root_table_slots"]["folded" if arm["fold"] else "unfolded"]
    if arm["table"] == "base" or arm["table"] == "compact" or arm["table"] == "filter":
        pass
    checks = {
        "scan_order": sm["scan_order"] == "feistel", "pipeline": sm["probe_pipeline"] == "prefetch",
        "target_canon_lift": tg["target_canonicalizer"] == "lift",
        "slots": sm["root_table_slots"] == exp_slots, "fold": sm["state_fold"] == arm["fold"],
        "stored": sm["stored_states"] == (proto["online"]["stored_states_folded"] if arm["fold"] else proto["online"]["regular_states"]),
        "logical": sm["index_digest"]["logical_states"] == idx["logical_states"],
        "blake3": sm["index_digest"]["logical_states_blake3"] == idx["logical_states_blake3"],
        "entries": sm["index_digest"]["table_entries"] == idx["table_entries"],
        "sum64": sm["index_digest"]["table_map_sum64"] == idx["table_map_sum64"],
        "xor64": sm["index_digest"]["table_map_xor64"] == idx["table_map_xor64"],
        "no_bloom": sm["root_bloom_enabled"] is False,
        "no_filter_rejected": tg.get("planted_rejected_found", 0) == 0,
        "root_table": sm["root_table"] == arm["table"],
        "solved": sm["targets_solved"] == 1 and sm["targets_failed"] == 0,
    }
    if arm["kind"] == "ic_rank":
        checks["rank600"] = sm["rank"] == 600 and sm["rank_failures"] == 0
        checks["logs_equal_archived"] = o["fields"]["logs_equal_archived"] is True
    bad = [k for k, v in checks.items() if not v]
    if bad: fails.append((r["serial"], r["arm"], bad))
# per-point identities
UNF = ("cP", "cSmF", "kP", "kSmF"); FOLD = ("cS", "cSaa", "cSX", "cSmS", "cSF", "cSI", "kS", "kSaa", "kSmS")
for u, arms in sorted(units.items()):
    sc = {str(o["fields"]["recovered_scalar"]) for _, o in arms.values()}
    rel = {json.dumps(o["fields"]["relation"]) for a, (_, o) in arms.items() if a != "rT"}
    pu = {o["fields"]["ops"] for a, (_, o) in arms.items() if a in UNF}
    pf = {o["fields"]["ops"] for a, (_, o) in arms.items() if a in FOLD}
    ok = len(sc) == 1 and len(rel) == 1 and len(pu) == 1 and len(pf) == 1 and min(pf) <= min(pu)
    if "cSX" in arms:
        sx = arms["cSX"][1]["fields"]
        ok = ok and sx["ops"] + sx["audit_probes"] == min(pu)
    print(u, "arms", len(arms), "scalar", sc, "rel_ok", len(rel) == 1, "probes unfolded", pu, "folded", pf,
          "cSX+audit", (arms["cSX"][1]["fields"]["ops"] + arms["cSX"][1]["fields"]["audit_probes"]) if "cSX" in arms else None, "OK" if ok else "FAIL")
    if not ok: fails.append(("unit", u))
# rank block identities
for u in ("s000", "s001"):
    a = units[u]
    sm = {k: [x for x in a[k][1]["records"] if x.get("kind") == "compact_orbit_dlp_summary"][0] for k in ("kP", "kS", "kSaa", "kSmF", "kSmS")}
    dig = {k: sm[k]["rank_relations_blake3"] for k in ("kS", "kSaa", "kSmF", "kSmS")}
    probes_same = sm["kS"]["rank_attempt_probes"] == sm["kSaa"]["rank_attempt_probes"] == sm["kSmS"]["rank_attempt_probes"]
    mf_ge = all(x >= y for x, y in zip(sm["kSmF"]["rank_attempt_probes"], sm["kS"]["rank_attempt_probes"]))
    print(u, "rank digests equal (lift arms):", len(set(dig.values())) == 1, "kP digest differs:", sm["kP"]["rank_relations_blake3"] != dig["kS"],
          "probes kS=kSaa=kSmS:", probes_same, "kSmF>=kS per attempt:", mf_ge,
          "attempts", {k: sm[k]["rank_attempts"] for k in sm}, "probes_total", {k: sm[k]["rank_probes_total"] for k in sm})
    if not (len(set(dig.values())) == 1 and probes_same and mf_ge): fails.append(("rank", u))
q0 = proto["online"]["q0_identity"]
for a in ("cP", "cS"):
    f = units["q0"][a][1]["fields"]
    want = q0["probes_unfolded"] if a == "cP" else q0["probes_folded"]
    print("q0", a, f["relation"] == q0["relation"], str(f["recovered_scalar"]) == q0["scalar"], f["ops"] == want)
print("gate failures:", fails)
