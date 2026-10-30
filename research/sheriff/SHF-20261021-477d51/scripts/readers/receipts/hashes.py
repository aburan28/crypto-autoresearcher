#!/usr/bin/env python3
"""Independent B7 seal check and plan.json reconstruction (SHF-20261021-477d51, receipts reader).

Own reimplementation of the ecbench seal definitions read from the target's source
(read only, never executed):
  plan_sha256    = sha256(plan.json bytes)        runner.rs:162-166, 490
  host_sha256    = sha256(host.json bytes)        runner.rs:479
  records_sha256 = sha256(records.jsonl bytes)    runner.rs:655-659
  spec_sha256    = sha256(canonical({schema, workloads, arms, measurement}))  spec.rs:202-209, 328
  session_id     = "ECBS1h" + sha256(canonical({spec_sha256, host_sha256, plan_sha256,
                    started_unix_ms: str}))[:12]                              runner.rs:493-501
  plan.json      = serde_json::to_string_pretty(PlanDoc{schema, spec_id, arms, workloads,
                    executions}) + "\n"                                        runner.rs:483-490
Plan reconstruction:
  (A) spec.json + sealed records.jsonl: arms' resolved methods and workloads copied from
      records, executions from my own expansion of the spec (spec.rs:283-321);
  (B) spec.json + method declarations read in methods.rs only (campaign sessions): every
      field computed here; for prime_search curves (a, b) come from certs.py (solved from
      recorded points) because the RNG-based curve search is not reimplemented; the
      registry fields (registered, ec1, curve_uid) are copied from records.
"""
import hashlib
import json
import sys
from collections import OrderedDict

sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
from certs import Curve, canon, digest, derive_u64, planted_law, icv1_model_hash  # own code  # noqa: E402

CAMPAIGN = "/home/user/crypto/research/ic_planner_validation_20261020/sessions"
F4 = "/home/user/crypto/research/f4_pricing_jump_20261018"
F4_SESSIONS = [
    "records/000-2245b7596", "records/039-cd226d0ce", "records/095-e15e29dbd", "records/096-f2c9202ca",
    "records/303-abee07ee7",
    "leaderboard_rerun/f4_f5_f6_cross_family_20261011-K13", "leaderboard_rerun/f4_f5_f6_cross_family_20261011-K19",
    "leaderboard_rerun/f4_f5_f6_cross_family_20261011-R13", "leaderboard_rerun/f4_f5_f6_cross_family_20261011-R19",
    "leaderboard_rerun/f6_ic_ecbench_ladder_20261005-n13", "leaderboard_rerun/f6_ic_ecbench_ladder_20261005-n19",
    "leaderboard_rerun/f6_ic_ecbench_ladder_20261005-n23",
]

# methods.rs:133-196, 255-262, 452-459 (read, not executed)
DECLS = {
    "rho.negation": {"family": "rho", "entry": "ic_boundary::rho_walk_with(NegationClasses, RhoWalk::negation())",
                     "defaults": {"cap_multiple": "64"}, "required": []},
    "ic.pipeline": {"family": "ic", "entry": "ic_framework::run_pipeline",
                    "defaults": {"solver": "", "linalg": "incremental-gauss", "targets": "walk",
                                 "max_trials": "100000000", "solver_budget_seconds": "0"},
                    "required": ["factor_base", "oracle"]},
}


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def spec_identity(spec):
    wl = dict(spec["workloads"])
    if wl.get("target_kind", "planted") == "planted":
        wl.pop("target_kind", None)
    arms = []
    for a in spec["arms"]:
        arms.append({"name": a["name"], "role": a["role"],
                     "method": {"id": a["method"]["id"], "params": a["method"].get("params", {})}})
    m = spec["measurement"]
    meas = {"rounds": m["rounds"], "warmup": m.get("warmup", 1), "order": m.get("order", "alternate"),
            "seed": m["seed"], "isolation_required": m.get("isolation_required", "L2"),
            "timeout_seconds": m.get("timeout_seconds", 600)}
    return {"schema": spec["schema"], "workloads": wl, "arms": arms, "measurement": meas}


def expand_executions(spec, workload_ids):
    m = spec["measurement"]
    warm_n = m.get("warmup", 1)
    n_arms = len(spec["arms"])
    out, seq = [], 0
    for rnd in range(warm_n + m["rounds"]):
        warm = rnd < warm_n
        for wi, wid_s in enumerate(workload_ids):
            wid = int(wid_s[1:], 16)
            seed = derive_u64("ecbench.warmup_seed" if warm else "ecbench.algorithm_seed", [m["seed"], wid, rnd])
            order = list(range(n_arms))
            if m.get("order", "alternate") == "alternate":
                if rnd % 2 == 1:
                    order.reverse()
            else:
                s = derive_u64("ecbench.order", [m["seed"], wid, rnd])
                raise SystemExit("shuffle order not needed here")
            for arm in order:
                out.append(OrderedDict([("seq", seq), ("round", rnd), ("warmup", warm), ("arm", arm),
                                        ("workload", wi), ("algorithm_seed", seed)]))
                seq += 1
    return out


def pretty(doc):
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def plan_from_records(sdir, spec, spec_id):
    recs = [json.loads(l, object_pairs_hook=OrderedDict) for l in open(f"{sdir}/records.jsonl")]
    arms = []
    for a in spec["arms"]:
        r = next(x for x in recs if x["arm"] == a["name"])
        arms.append(OrderedDict([("name", a["name"]), ("role", a["role"]), ("method", r["method"])]))
    curves = spec["workloads"]["curves"]
    wl = {}
    for r in recs:
        w = r["workload"]
        ci = curves.index(json.loads(json.dumps(w["curve_spec"])))
        wl.setdefault((ci, w["target_index"]), w)
    keys = sorted(wl)
    workloads = [wl[k] for k in keys]
    execs = expand_executions(spec, [w["workload_id"] for w in workloads])
    # cross-check the expansion against the records' own (seq, round, warmup, arm, workload, seed)
    mism = 0
    idx = {w["workload_id"]: i for i, w in enumerate(workloads)}
    names = [a["name"] for a in spec["arms"]]
    for e, r in zip(execs, recs):
        got = (r["seq"], r["round"], r["warmup"], names.index(r["arm"]), idx[r["workload"]["workload_id"]], int(r["algorithm_seed"]))
        if got != tuple(e.values()):
            mism += 1
    if len(execs) != len(recs):
        mism += abs(len(execs) - len(recs))
    doc = OrderedDict([("schema", "ecbench.plan/v1"), ("spec_id", spec_id), ("arms", arms),
                       ("workloads", workloads), ("executions", execs)])
    return pretty(doc), mism, recs


def resolve_method(ms):
    d = DECLS[ms["id"]]
    params = dict(d["defaults"])
    for k in d["required"]:
        assert k in ms.get("params", {}), (ms, k)
    for k, v in ms.get("params", {}).items():
        assert k in d["defaults"] or k in d["required"], (ms, k)
        params[k] = v
    params = OrderedDict(sorted(params.items()))
    sha = digest({"schema": "ecbench.method/v1", "id": ms["id"], "params": params})
    return OrderedDict([("id", ms["id"]), ("family", d["family"]), ("params", params),
                        ("method_id", "ECM1h" + sha[:12]), ("method_sha256", sha), ("entry", d["entry"])])


def plan_from_spec_only(spec, spec_id, curve_params, registry_fields):
    """curve_params: (p, a, b, r, gx, gy); registry_fields: (registered, ec1, curve_uid)."""
    p, a, b, r, gx, gy = curve_params
    E = Curve(p, a, b)
    cs = spec["workloads"]["curves"][0]
    t = p + 1 - r
    mh = icv1_model_hash(p, a, b)
    icv1 = "ICV1:fp-%d:%d:%d:%d:unk:unk:r:%s" % (p, t, r, E.j(), mh[:12])
    slug = "icv1-fp%d-%s-%s" % (p.bit_length(), ("tm%d" % -t) if t < 0 else ("t%d" % t), mh[:8])
    if cs["kind"] == "prime_explicit":
        construction = "PrimeCurve { p: %d, a: %d, b: %d } (explicit)" % (cs["p"], cs["a"], cs["b"])
    else:
        construction = "find_prime_order_curve(%d, %d)" % (cs["bits"], cs["seed"])
    facts = OrderedDict([("slug", slug), ("icv1", icv1), ("family", "prime"), ("construction", construction),
                         ("field_degree", None), ("field_bits", p.bit_length()), ("group_order", r), ("r", r),
                         ("cofactor", 1), ("generator", ["0x%x" % gx, "0x%x" % gy]), ("automorphisms_available", 2),
                         ("registered", registry_fields[0]), ("ec1", registry_fields[1]), ("curve_uid", registry_fields[2])])
    tseed = spec["workloads"]["target_seed"]
    workloads = []
    for i in range(spec["workloads"]["targets_per_curve"]):
        k = planted_law(icv1, r, tseed, i)
        Q = E.mul(k, (gx, gy))
        target = ["0x%x" % Q[0], "0x%x" % Q[1]]
        ident = {"schema": "ecbench.workload/v1", "icv1": icv1, "subgroup_order": str(r), "cofactor": "1",
                 "generator": facts["generator"], "target": target, "target_law": "uniform_scalar_sha256_v1",
                 "target_seed": str(tseed), "target_index": str(i), "target_count": 1, "cache_policy": "cold"}
        wsha = digest(ident)
        workloads.append(OrderedDict([("workload_id", "W" + wsha[:12]), ("workload_sha256", wsha),
                                      ("curve_spec", cs), ("curve", facts), ("target_law", "uniform_scalar_sha256_v1"),
                                      ("target_seed", tseed), ("target_index", i), ("target", target), ("planted", k)]))
    arms = [OrderedDict([("name", a["name"]), ("role", a["role"]), ("method", resolve_method(a["method"]))])
            for a in spec["arms"]]
    execs = expand_executions(spec, [w["workload_id"] for w in workloads])
    doc = OrderedDict([("schema", "ecbench.plan/v1"), ("spec_id", spec_id), ("arms", arms),
                       ("workloads", workloads), ("executions", execs)])
    return pretty(doc)


def check(sdir, label, certs=None, frozen_spec=None):
    sess = json.load(open(f"{sdir}/session.json"))
    spec = json.load(open(f"{sdir}/spec.json"), object_pairs_hook=OrderedDict)
    out = OrderedDict(session=label, path=sdir, session_id=sess["session_id"])
    files = OrderedDict()
    for f in ("spec.json", "plan.json", "host.json", "records.jsonl", "session.json"):
        files[f] = sha_file(f"{sdir}/{f}")
    out["file_sha256"] = files
    out["records_sha256_ok"] = files["records.jsonl"] == sess["records_sha256"]
    out["plan_sha256_ok"] = files["plan.json"] == sess["plan_sha256"]
    out["host_sha256_ok"] = files["host.json"] == sess["host_sha256"]
    ssha = digest(spec_identity(spec))
    out["spec_sha256_recomputed"] = ssha
    out["spec_sha256_ok"] = ssha == sess["spec_sha256"]
    out["spec_id_ok"] = "ECS1h" + ssha[:12] == sess["spec_id"]
    sid = "ECBS1h" + digest({"spec_sha256": sess["spec_sha256"], "host_sha256": sess["host_sha256"],
                             "plan_sha256": sess["plan_sha256"],
                             "started_unix_ms": str(sess["started_unix_ms"])})[:12]
    out["session_id_recomputed"] = sid
    out["session_id_ok"] = sid == sess["session_id"]
    if frozen_spec is not None:
        out["spec_json_equals_frozen_spec_bytes"] = open(f"{sdir}/spec.json", "rb").read() == open(frozen_spec, "rb").read()
    text, mism, recs = plan_from_records(sdir, spec, sess["spec_id"])
    out["records"] = len(recs)
    out["records_written_ok"] = len(recs) == sess["records_written"] == sess["executions_planned"]
    sc = {}
    for r in recs:
        sc[r["outcome"]["status"]] = sc.get(r["outcome"]["status"], 0) + 1
    out["status_counts_ok"] = sc == sess["status_counts"]
    out["records_session_id_ok"] = all(r["session_id"] == sess["session_id"] for r in recs)
    out["records_binary_sha256_ok"] = all(r["binary_sha256"] == sess["binary_sha256"] for r in recs)
    out["records_env_class_ok"] = all(r["env_class_id"] == sess["env_class_id"] for r in recs)
    plan_bytes = open(f"{sdir}/plan.json", "rb").read()
    out["planA_expansion_vs_records_mismatches"] = mism
    out["planA_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    out["planA_bytes_equal_plan_json"] = text.encode() == plan_bytes
    out["planA_sha_equals_session_plan_sha256"] = out["planA_sha256"] == sess["plan_sha256"]
    # plan.json arms/spec vs the spec (task 7)
    pj = json.loads(plan_bytes)
    out["plan_spec_id_ok"] = pj["spec_id"] == sess["spec_id"]
    out["plan_arms_match_spec"] = [(a["name"], a["role"], a["method"]["id"]) for a in pj["arms"]] == [
        (a["name"], a["role"], a["method"]["id"]) for a in spec["arms"]] and all(
        all(pa["method"]["params"].get(k) == v for k, v in sa["method"].get("params", {}).items())
        for pa, sa in zip(pj["arms"], spec["arms"]))
    if certs is not None:
        c = certs["curve"]
        r0 = recs[0]["workload"]["curve"]
        textB = plan_from_spec_only(spec, sess["spec_id"], (c["p"], c["a"], c["b"], c["r"], c["G"][0], c["G"][1]),
                                    (r0["registered"], r0["ec1"], r0["curve_uid"]))
        out["planB_sha256"] = hashlib.sha256(textB.encode()).hexdigest()
        out["planB_bytes_equal_plan_json"] = textB.encode() == plan_bytes
        out["planB_sha_equals_session_plan_sha256"] = out["planB_sha256"] == sess["plan_sha256"]
    oks = [v for k, v in out.items() if k.endswith("_ok") or k.endswith("_equal_plan_json") or k.endswith("plan_sha256") and isinstance(v, bool)]
    out["all_ok"] = all(oks) and mism == 0
    return out


def main():
    outp = sys.argv[1]
    certs = json.load(open(sys.argv[2]))
    cmap = {s["session"]: s for s in certs["sessions"]}
    results = []
    for s in ["c24", "c28", "c30", "r24", "r26", "r28"]:
        results.append(check(f"{CAMPAIGN}/{s}", s, certs=cmap[s],
                             frozen_spec=f"/home/user/crypto/research/ic_planner_validation_20261020/specs/{s}.json"))
    for s in F4_SESSIONS:
        results.append(check(f"{F4}/{s}", "f4:" + s))
    # proves-too-much controls on the seal checks
    controls = OrderedDict()
    pj = open(f"{F4}/records/000-2245b7596/plan.json", "rb").read()
    sess = json.load(open(f"{F4}/records/000-2245b7596/session.json"))
    i = pj.index(b'"algorithm_seed": ') + len(b'"algorithm_seed": ')
    mutated = pj[:i] + bytes([pj[i] ^ 1]) + pj[i + 1:]
    controls["one_byte_flip_in_f4_000_plan_json"] = {
        "sha256": hashlib.sha256(mutated).hexdigest(), "equals_seal": hashlib.sha256(mutated).hexdigest() == sess["plan_sha256"]}
    reordered = json.dumps(json.loads(pj), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    controls["key_sorted_reserialisation_of_f4_000_plan_json"] = {
        "equals_seal": hashlib.sha256(reordered.encode()).hexdigest() == sess["plan_sha256"]}
    spec = json.load(open(f"{CAMPAIGN}/r24/spec.json"), object_pairs_hook=OrderedDict)
    sess24 = json.load(open(f"{CAMPAIGN}/r24/session.json"))
    spec["measurement"]["seed"] += 1
    controls["r24_spec_measurement_seed_plus_one"] = {"equals_seal": digest(spec_identity(spec)) == sess24["spec_sha256"]}
    textB = plan_from_spec_only(spec, sess24["spec_id"], (16777199, 16777196, 31, 16782299, 2, 5412647),
                                (True, "EC1P24Cfph095cb65c0da0", "urn:ec-record:1:sha256:095cb65c0da0a37ab991f2bfd8c0fb3634459c36cd06f3e2dac5baf467b6293c"))
    controls["r24_planB_with_measurement_seed_plus_one"] = {"equals_seal": hashlib.sha256(textB.encode()).hexdigest() == sess24["plan_sha256"]}
    spec = json.load(open(f"{CAMPAIGN}/r24/spec.json"), object_pairs_hook=OrderedDict)
    spec["arms"][1]["method"]["params"]["factor_base"] = "prime-abscissa:size=129"
    textB = plan_from_spec_only(spec, sess24["spec_id"], (16777199, 16777196, 31, 16782299, 2, 5412647),
                                (True, "EC1P24Cfph095cb65c0da0", "urn:ec-record:1:sha256:095cb65c0da0a37ab991f2bfd8c0fb3634459c36cd06f3e2dac5baf467b6293c"))
    controls["r24_planB_with_plan_arm_size_129"] = {"equals_seal": hashlib.sha256(textB.encode()).hexdigest() == sess24["plan_sha256"]}
    for v in controls.values():
        v["rejected"] = not v["equals_seal"]
    json.dump(OrderedDict(sessions=results, controls=controls), open(outp, "w"), indent=1)
    for r in results:
        flags = {k: v for k, v in r.items() if isinstance(v, bool) and not v}
        print(r["session"], "all_ok=%s" % r["all_ok"], "failing=%s" % flags,
              "A=%s" % r["planA_bytes_equal_plan_json"], "B=%s" % r.get("planB_bytes_equal_plan_json", "-"),
              "mism=%d" % r["planA_expansion_vs_records_mismatches"])
    for k, v in controls.items():
        print("control", k, "rejected=%s" % v["rejected"])


if __name__ == "__main__":
    main()
