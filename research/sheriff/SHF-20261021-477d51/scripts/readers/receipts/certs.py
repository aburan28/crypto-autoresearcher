#!/usr/bin/env python3
"""Independent B4 certificate check for research/ic_planner_validation_20261020.

Written by the sheriff receipts reader (SHF-20261021-477d51); shares no code with
the producer. Plain Python integer arithmetic; sympy.isprime only as a second
primality opinion. Reads files given by path; executes nothing from the target repo.

For every record in sessions/<s>/records.jsonl:
  * curve: prime_explicit -> (p,a,b,r,G) from curve_spec (and compared with the
    frozen specs/<s>.json); prime_search -> p from the ICV1 field, (a,b) solved
    from two recorded points (G and a target), checked against every other point
    and against the ICV1 model hash (sha256 of the model JSON).
  * [planted]G == target, [recovered]G == target, recovered == planted,
    status == verified, matches_* flags.
  * planted recomputed from the target law uniform_scalar_sha256_v1.
  * workload_id / workload_sha256 recomputed from the identity view.
  * algorithm_seed recomputed from the measurement seed (plan expansion).
  * execution order (seq, round, warmup, arm, workload) recomputed.
Per curve: p, r prime (trial division to isqrt, i.e. a proof for these sizes),
G on curve, [r]G == O, Hasse, r > 4 sqrt(p) (so #E == r, cofactor 1),
a, b != 0, disc != 0, j != 0, 1728.
"""
import hashlib
import json
import math
import sys
from collections import Counter, OrderedDict

try:
    import sympy  # second opinion only
except Exception:  # pragma: no cover
    sympy = None

O = None  # point at infinity


def is_prime_td(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    lim = math.isqrt(n)
    f = 3
    while f <= lim:
        if n % f == 0:
            return False
        f += 2
    return True


class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a % p, b % p

    def on(self, P):
        if P is O:
            return True
        x, y = P
        p = self.p
        return 0 <= x < p and 0 <= y < p and (y * y - (x * x * x + self.a * x + self.b)) % p == 0

    def add(self, P, Q):
        p = self.p
        if P is O:
            return Q
        if Q is O:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return O
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p
        return (x3, y3)

    def mul(self, k, P):
        R = O
        A = P
        while k > 0:
            if k & 1:
                R = self.add(R, A)
            A = self.add(A, A)
            k >>= 1
        return R

    def disc(self):
        p = self.p
        return (4 * pow(self.a, 3, p) + 27 * self.b * self.b) % p

    def j(self):
        p = self.p
        a3 = 4 * pow(self.a, 3, p) % p
        return 1728 * a3 * pow((a3 + 27 * self.b * self.b) % p, -1, p) % p


def canon(v):
    # sorted keys, compact, ASCII-escaped: the documented identity codec
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(v):
    return hashlib.sha256(canon(v).encode()).hexdigest()


def derive_u64(domain, parts):
    d = hashlib.sha256(canon({"domain": domain, "parts": list(parts)}).encode()).digest()
    return int.from_bytes(d[:8], "big")


def planted_law(icv1, r, seed, index):
    model = int(icv1.rsplit(":", 1)[1], 16)
    return 1 + derive_u64("uniform_scalar_sha256_v1", [model, r, seed, index]) % (r - 1)


def icv1_model_hash(p, a, b):
    model_json = '{"a":"%d","b":"%d","field":"fp-%d","form":"y^2=x^3+a*x+b","p":"%d","v":"1"}' % (a, b, p, p)
    return hashlib.sha256(model_json.encode()).hexdigest()


def workload_identity(w):
    c = w["curve"]
    return {
        "schema": "ecbench.workload/v1",
        "icv1": c["icv1"],
        "subgroup_order": str(c["r"]),
        "cofactor": str(c["cofactor"]),
        "generator": c["generator"],
        "target": w["target"],
        "target_law": w["target_law"],
        "target_seed": str(w["target_seed"]),
        "target_index": str(w["target_index"]),
        "target_count": 1,
        "cache_policy": "cold",
    }


def hx(s):
    return int(s, 16)


def solve_ab(p, P1, P2):
    (x1, y1), (x2, y2) = P1, P2
    u1 = (y1 * y1 - x1 ** 3) % p
    u2 = (y2 * y2 - x2 ** 3) % p
    a = (u1 - u2) * pow(x1 - x2, -1, p) % p
    b = (u1 - a * x1) % p
    return a, b


def expected_executions(spec, n_workloads):
    m = spec["measurement"]
    n_arms = len(spec["arms"])
    out = []
    seq = 0
    for rnd in range(m["warmup"] + m["rounds"]):
        warm = rnd < m["warmup"]
        for wi in range(n_workloads):
            order = list(range(n_arms))
            if m.get("order", "alternate") == "alternate":
                if rnd % 2 == 1:
                    order.reverse()
            else:
                raise SystemExit("only alternate order implemented")
            for arm in order:
                out.append((seq, rnd, warm, arm, wi))
                seq += 1
    return out


def check_session(base, s, flip=None):
    spec_frozen_path = f"{base}/specs/{s}.json"
    sdir = f"{base}/sessions/{s}"
    spec = json.load(open(spec_frozen_path))
    spec_sess_bytes = open(f"{sdir}/spec.json", "rb").read()
    spec_frozen_bytes = open(spec_frozen_path, "rb").read()
    sess = json.load(open(f"{sdir}/session.json"))
    res = OrderedDict(session=s)
    res["spec_json_bytes_equal_frozen_spec"] = spec_sess_bytes == spec_frozen_bytes
    curve_spec = spec["workloads"]["curves"][0]
    assert len(spec["workloads"]["curves"]) == 1
    tseed = spec["workloads"]["target_seed"]
    tpc = spec["workloads"]["targets_per_curve"]
    mseed = spec["measurement"]["seed"]
    arm_names = [a["name"] for a in spec["arms"]]
    arm_roles = [a["role"] for a in spec["arms"]]
    exp_exec = expected_executions(spec, tpc)

    recs = [json.loads(l) for l in open(f"{sdir}/records.jsonl")]
    if flip is not None:
        flip(recs)
    res["records"] = len(recs)
    fails = Counter()
    status = Counter()
    per_arm = Counter()
    fail_examples = []

    def bad(key, rec):
        fails[key] += 1
        if len(fail_examples) < 10:
            fail_examples.append({"check": key, "seq": rec.get("seq"), "record_id": rec.get("record_id")})

    # ---- curve identity, from the first record + all points ----
    c0 = recs[0]["workload"]["curve"]
    icv1 = c0["icv1"]
    fields = icv1.split(":")
    p_icv1 = int(fields[1].split("-")[1])
    G = (hx(c0["generator"][0]), hx(c0["generator"][1]))
    r = int(c0["r"])
    if curve_spec["kind"] == "prime_explicit":
        p, a, b = curve_spec["p"], curve_spec["a"], curve_spec["b"]
        res["curve_source"] = "frozen spec prime_explicit"
        if (curve_spec["gx"], curve_spec["gy"]) != G or curve_spec["r"] != r or curve_spec["group_order"] != r:
            fails["spec_vs_record_curve_facts"] += 1
        if p != p_icv1:
            fails["icv1_field_vs_spec_p"] += 1
    else:
        p = p_icv1
        # solve a,b from G and the first target whose x differs
        Q0 = None
        for rec in recs:
            T = tuple(hx(t) for t in rec["workload"]["target"])
            if T[0] != G[0]:
                Q0 = T
                break
        a, b = solve_ab(p, G, Q0)
        res["curve_source"] = "prime_search: p from ICV1 field; (a,b) solved from G and a recorded target"
    E = Curve(p, a, b)
    curve = OrderedDict()
    curve["p"] = p
    curve["a"] = a
    curve["b"] = b
    curve["r"] = r
    curve["G"] = list(G)
    curve["p_bits"] = p.bit_length()
    curve["p_prime_trial_division"] = is_prime_td(p)
    curve["r_prime_trial_division"] = is_prime_td(r)
    if sympy is not None:
        curve["p_prime_sympy"] = bool(sympy.isprime(p))
        curve["r_prime_sympy"] = bool(sympy.isprime(r))
    curve["G_on_curve"] = E.on(G)
    curve["rG_is_O"] = E.mul(r, G) is O
    t = p + 1 - r
    curve["trace"] = t
    curve["hasse_t2_le_4p"] = t * t <= 4 * p
    curve["r_sq_gt_16p_so_unique_multiple"] = r * r > 16 * p
    curve["cofactor_1_proved"] = bool(
        curve["r_prime_trial_division"] and curve["rG_is_O"] and G is not O and curve["hasse_t2_le_4p"] and curve["r_sq_gt_16p_so_unique_multiple"]
    )
    curve["a_nonzero"] = a % p != 0
    curve["b_nonzero"] = b % p != 0
    curve["disc_nonzero"] = E.disc() != 0
    j = E.j()
    curve["j"] = j
    curve["j_not_0_or_1728"] = j not in (0, 1728 % p)
    mh = icv1_model_hash(p, a, b)
    curve["icv1"] = icv1
    curve["icv1_model_hash_matches_own_(p,a,b)"] = fields[-1] == mh[:12]
    curve["icv1_trace_matches"] = int(fields[2]) == t
    curve["icv1_order_matches"] = int(fields[3]) == r
    curve["icv1_j_matches"] = int(fields[4]) == j
    curve["slug_matches"] = c0["slug"] == "icv1-fp%d-%s-%s" % (p.bit_length(), ("tm%d" % -t) if t < 0 else ("t%d" % t), mh[:8])
    curve["record_cofactor"] = c0["cofactor"]
    curve["record_automorphisms_available"] = c0["automorphisms_available"]
    curve["construction"] = c0["construction"]
    curve["registered"] = c0["registered"]
    curve["ec1"] = c0["ec1"]
    res["curve"] = curve

    # ---- per-record checks ----
    wl_seen = {}
    for i, rec in enumerate(recs):
        w = rec["workload"]
        oc = rec["outcome"]
        status[oc["status"]] += 1
        per_arm[rec["arm"]] += 1
        if rec["session_id"] != sess["session_id"]:
            bad("session_id", rec)
        if rec["env_class_id"] != sess["env_class_id"]:
            bad("env_class_id", rec)
        if rec["binary_sha256"] != sess["binary_sha256"]:
            bad("binary_sha256", rec)
        if w["curve_spec"] != curve_spec:
            bad("curve_spec_vs_frozen_spec", rec)
        if w["curve"] != c0:
            bad("curve_facts_differ_between_records", rec)
        if w["target_law"] != "uniform_scalar_sha256_v1" or w["target_seed"] != tseed:
            bad("target_law_or_seed", rec)
        Q = (hx(w["target"][0]), hx(w["target"][1]))
        if not E.on(Q):
            bad("target_not_on_curve", rec)
        k = w["planted"]
        if not (1 <= k <= r - 1):
            bad("planted_out_of_range", rec)
        if E.mul(k, G) != Q:
            bad("planted_G_ne_target", rec)
        if planted_law(icv1, r, tseed, w["target_index"]) != k:
            bad("planted_ne_target_law", rec)
        rid, rsha = None, digest(workload_identity(w))
        if w["workload_sha256"] != rsha or w["workload_id"] != "W" + rsha[:12]:
            bad("workload_id_recompute", rec)
        if oc["status"] != "verified":
            bad("status_not_verified", rec)
        rec_k = oc.get("recovered")
        if rec_k is None or int(rec_k) != k:
            bad("recovered_ne_planted", rec)
        if rec_k is not None and E.mul(int(rec_k) % r, G) != Q:
            bad("recovered_G_ne_target", rec)
        if not (oc.get("matches_target") is True and oc.get("matches_planted") is True):
            bad("matches_flags", rec)
        # plan expansion
        es, er, ew, ea, ewi = exp_exec[i]
        if (rec["seq"], rec["round"], rec["warmup"]) != (es, er, ew):
            bad("seq_round_warmup", rec)
        if rec["arm"] != arm_names[ea] or rec["role"] != arm_roles[ea]:
            bad("arm_order", rec)
        if w["target_index"] != ewi:
            bad("workload_order", rec)
        wid = int(w["workload_id"][1:], 16)
        dom = "ecbench.warmup_seed" if rec["warmup"] else "ecbench.algorithm_seed"
        if str(derive_u64(dom, [mseed, wid, rec["round"]])) != str(rec["algorithm_seed"]):
            bad("algorithm_seed", rec)
        # method identity
        m = rec["method"]
        msha = digest({"schema": "ecbench.method/v1", "id": m["id"], "params": m["params"]})
        if m["method_sha256"] != msha or m["method_id"] != "ECM1h" + msha[:12]:
            bad("method_id_recompute", rec)
        sp_arm = spec["arms"][ea]
        if sp_arm["method"]["id"] != m["id"] or any(m["params"].get(kk) != vv for kk, vv in sp_arm["method"].get("params", {}).items()):
            bad("method_vs_spec_arm", rec)
        wl_seen.setdefault(w["target_index"], (k, w["workload_id"]))
    res["records_checked"] = len(recs)
    res["status_counts"] = dict(status)
    res["per_arm"] = dict(per_arm)
    res["distinct_workloads"] = len(wl_seen)
    res["planted_by_target_index"] = {str(i): wl_seen[i][0] for i in sorted(wl_seen)}
    res["verified_and_kG_eq_Q"] = sum(1 for rec in recs if rec["outcome"]["status"] == "verified") - fails["planted_G_ne_target"]
    res["fails"] = dict(fails)
    res["fail_examples"] = fail_examples
    res["session_expected"] = {"executions_planned": sess["executions_planned"], "records_written": sess["records_written"], "status_counts": sess["status_counts"]}
    res["ok"] = (not fails) and len(recs) == len(exp_exec) == sess["records_written"] and all(
        curve[k] for k in ("p_prime_trial_division", "r_prime_trial_division", "G_on_curve", "rG_is_O", "cofactor_1_proved", "a_nonzero", "b_nonzero", "disc_nonzero", "j_not_0_or_1728", "icv1_model_hash_matches_own_(p,a,b)", "icv1_trace_matches", "icv1_order_matches", "icv1_j_matches", "slug_matches")
    ) and res["spec_json_bytes_equal_frozen_spec"]
    return res


def main():
    base = sys.argv[1]
    out = sys.argv[2]
    sessions = ["c24", "c28", "c30", "r24", "r26", "r28"]
    results = [check_session(base, s) for s in sessions]
    total = sum(r["records_checked"] for r in results)
    summary = OrderedDict(
        total_records=total,
        total_fail_counts=sum(sum(r["fails"].values()) for r in results),
        all_ok=all(r["ok"] for r in results),
        kG_eq_Q_and_verified=sum(r["verified_and_kG_eq_Q"] for r in results),
    )

    # proves-too-much controls: corrupt copies in memory; the checker must reject
    controls = OrderedDict()

    def flip_planted(recs):
        recs[17]["workload"]["planted"] ^= 1

    def flip_target(recs):
        x = int(recs[40]["workload"]["target"][1], 16)
        recs[40]["workload"]["target"][1] = hex(x ^ 1)

    def swap_recovered(recs):
        k = int(recs[5]["outcome"]["recovered"])
        recs[5]["outcome"]["recovered"] = str(k + 1)

    def seed_change(recs):
        recs[100]["algorithm_seed"] = str(int(recs[100]["algorithm_seed"]) ^ 1)

    for name, fn in [("flip_lsb_of_planted_r24_rec17", flip_planted), ("flip_lsb_of_target_y_r24_rec40", flip_target),
                     ("recovered_plus_one_r24_rec5", swap_recovered), ("algorithm_seed_lsb_r24_rec100", seed_change)]:
        r_ = check_session(base, "r24", flip=fn)
        controls[name] = {"ok": r_["ok"], "fails": r_["fails"], "rejected": not r_["ok"]}
    # wrong curve: verify c24 records on c28's curve coefficients
    r_c24 = results[0]
    r_c28 = results[1]
    E28 = Curve(r_c28["curve"]["p"], r_c28["curve"]["a"], r_c28["curve"]["b"])
    G24 = tuple(r_c24["curve"]["G"])
    controls["c24_G_on_c28_curve"] = {"on_curve": E28.on(G24), "rejected": not E28.on(G24)}
    # composite-r control: r+2 (even) and a known composite
    controls["trial_division_rejects_composites"] = {
        "r24_r_plus_2": is_prime_td(16782299 + 2),
        "561": is_prime_td(561),
        "rejected": not is_prime_td(16782299 + 2) and not is_prime_td(561),
    }
    json.dump(OrderedDict(summary=summary, sessions=results, controls=controls), open(out, "w"), indent=1)
    print(json.dumps(summary))
    for r_ in results:
        print(r_["session"], "ok=%s" % r_["ok"], "records=%d" % r_["records_checked"], "fails=%s" % r_["fails"],
              "status=%s" % r_["status_counts"], "p=%d a=%d b=%d r=%d j=%d" % (r_["curve"]["p"], r_["curve"]["a"], r_["curve"]["b"], r_["curve"]["r"], r_["curve"]["j"]))
    for k, v in controls.items():
        print("control", k, "rejected=%s" % v["rejected"])


if __name__ == "__main__":
    main()
