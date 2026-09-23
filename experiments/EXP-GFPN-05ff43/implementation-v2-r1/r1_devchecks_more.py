#!/usr/bin/env python3
"""EXP-GFPN-05ff43 stage R1 -- development checks DV-1 (static part and the child-side probe), DV-5, DV-6, DV-8,
DV-9 and DV-10. Called through r1_devchecks.py; development only; outputs under --out (session scratchpad).
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_common as R                                    # noqa: E402

TOK = re.compile(r"RUN-GFPN-[0-9a-f]{6}")


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ============================================================================ DV-1 static inventory + child probe
def dv1_static(out, rest):
    """Static search of implementation-v2/, implementation-v2-a1/ and the layer for PARI uses, the call graph from
    each driver command to them, and a NO-COMPUTATION start-up probe of the Sage child's PARI stack."""
    os.makedirs(out, exist_ok=True)
    pat = re.compile(r"cypari2|\bpari\b|ellcard|allocatemem|parisize|/usr/bin/gp|\bgp\b|sage", re.I)
    hits = []
    for d in (R.V2_DIR, R.A1_DIR, HERE):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py"):
                continue
            for i, line in enumerate(open(os.path.join(d, f)), 1):
                if pat.search(line):
                    hits.append({"file": os.path.relpath(os.path.join(d, f), R.REPO), "line": i, "text": line.rstrip()[:200]})
    comparator = os.path.join(R.REPO, "coordination", "goals", "GOAL-GFPN-380702", "reviews", "TASK-20260923-58953e", "scratch", "k4a_anchor_system.py")
    comp_hits = [{"line": i, "text": line.rstrip()[:200]} for i, line in enumerate(open(comparator), 1)
                 if re.search(r"pari|GF\(|allocatemem|parisize|import", line)]
    # call graph (by reading the code; line numbers of the frozen files)
    graph = {
        "v2 fixture": "v2_driver.main -> cmd_fixture (275) -> fixture_core (284) -> C.curve_order_pari (308) [IN-PROCESS cypari2]",
        "v2 controls": "v2_driver.main -> cmd_controls (752) -> C.fixture_n3(4111) (764) -> C.curve_order_pari (771) [IN-PROCESS cypari2]",
        "v2 fixture4": "v2_driver.main -> cmd_fixture4 (526) -> C.fixture_n4 -> C.curve_order_pari (542) [IN-PROCESS cypari2]",
        "v2 anchor-identity": "v2_driver.main -> cmd_anchor_identity (628) -> V.run_child(SAGE_PYTHON, COMPARATOR) (650) [CHILD: Sage, PARI-backed GF(p^5)]",
        "v2 build": "v2_driver.main -> cmd_build (935): builders in capped v2_child.py children (flint/numpy); ladder orders from ladder.json; no PARI",
        "v2 cells": "v2_driver.main -> cmd_cells (1016): orders from ladder.json; msolve children; no PARI",
        "v2 aggregate": "v2_driver.main -> cmd_aggregate (1248): reads raw-result.json files; no PARI",
        "a1 controls-a1": "a1_driver.main -> cmd_controls_a1 (56) -> P.curve_facts (89) -> V.run_child(/usr/bin/gp) [CHILD: gp, parisize 256000000 / parisizemax 4000000000 set in the script, a1_pari.py line 38]",
        "a1 build": "a1_driver.cmd_build (219) -> v2_driver.cmd_build; no PARI",
        "a1 cells": "a1_driver.cmd_cells (228) -> v2_driver.cmd_cells; no PARI",
        "a1 aggregate-a1": "a1_driver.cmd_aggregate_a1 (276): reads raw-result.json files; no PARI",
    }
    # no-computation start-up probe of the Sage child's PARI stack (capped child)
    sys.path.insert(0, R.V2_DIR)
    import v2_solver as V
    probe = os.path.join(out, "sage_pari_probe.py")
    with open(probe, "w") as fh:
        fh.write("from sage.all import *\nfrom sage.libs.pari import pari\n"
                 "print('R1PROBE parisize', int(pari.default('parisize')))\nprint('R1PROBE parisizemax', int(pari.default('parisizemax')))\n"
                 "print('R1PROBE stacksize', int(pari.stacksize()))\nprint('R1PROBE stacksizemax', int(pari.stacksizemax()))\n"
                 "import sage.version; print('R1PROBE sage_version', sage.version.version)\n")
    so, se = os.path.join(out, "sage_pari_probe.stdout"), os.path.join(out, "sage_pari_probe.stderr")
    rec = V.run_child(["/opt/conda-sage/envs/sage/bin/python", probe], so, se, cap_bytes=R.CAP_BYTES, timeout_s=3600, count_instructions=False)
    vals = {}
    for line in open(so, errors="replace"):
        if line.startswith("R1PROBE "):
            k, v = line.split()[1], line.split()[2]
            vals[k] = v
    # which Sage finite-field class GF(p^5) with p = 16777291 uses: read from Sage's source, not computed
    ffsrc = "/opt/conda-sage/envs/sage/lib/python3*/site-packages/sage/rings/finite_rings/finite_field_constructor.py"
    import glob
    ffc = glob.glob(ffsrc)
    impl = []
    if ffc:
        for i, line in enumerate(open(ffc[0]), 1):
            if re.search(r"impl = |order < zech_log_bound|pari_ffelt|givaro", line):
                impl.append({"line": i, "text": line.rstrip()[:160]})
    rep = {"static_hits": hits, "comparator_hits": comp_hits, "call_graph": graph,
           "sage_child_probe": {"child": {k: rec.get(k) for k in ("outcome", "returncode", "rlimit_as_child_getrlimit", "rlimit_as_proc_limits_after_exec", "wall_seconds")},
                                "values": vals, "stderr_tail": open(se, errors="replace").read().splitlines()[-10:]},
           "sage_finite_field_constructor": {"file": ffc[0] if ffc else None, "lines": impl[:40]}}
    dump(os.path.join(out, "dv1_static.json"), rep)
    print("DV-1 static: %d PARI-related lines in v2/v2-a1/layer; Sage probe %s %s" % (len(hits), rec.get("outcome"), vals))
    return 0


# ============================================================================ DV-5 plan derivation (own code path)
def md_declared_keys():
    """Read the declared key paths back from implementation-v2-r1.md (the RC-4 (b) record), independently."""
    txt = open(os.path.join(R.EXP_DIR, "implementation-v2-r1.md")).read()
    sec = txt.split("## RC-4 (a)")[0]
    v2part, a1part = sec.split("`trial-plan-v2-a1-r1.json` (12 paths):")
    grab = lambda s: re.findall(r"^\| `(/[^`]+)` \|", s, re.M)   # noqa: E731
    return grab(v2part), grab(a1part)


def dv5_equal(r1plan, frozen, declared, inverse):
    """RC-4 (c) with DV-5's OWN implementation: pointer deletion by path walking, inverse mapping by a character
    scanner (no regex substitution, no writer function)."""
    def walk_delete(o, parts):
        if len(parts) == 1:
            if isinstance(o, dict):
                o.pop(parts[0], None)
            return
        if isinstance(o, dict) and parts[0] in o:
            walk_delete(o[parts[0]], parts[1:])

    def unmap(s):
        out, i, L = [], 0, len("RUN-GFPN-") + 6
        while i < len(s):
            j = s.find("RUN-GFPN-", i)
            if j < 0:
                out.append(s[i:])
                break
            out.append(s[i:j])
            tok = s[j:j + L]
            ok_tok = len(tok) == L and all(c in "0123456789abcdef" for c in tok[9:])
            out.append(inverse.get(tok, tok) if ok_tok else tok)
            i = j + L
        return "".join(out)

    def rec(o):
        if isinstance(o, dict):
            return {k: rec(v) for k, v in o.items()}
        if isinstance(o, list):
            return [rec(v) for v in o]
        return unmap(o) if isinstance(o, str) else o
    r, f = json.loads(json.dumps(r1plan)), json.loads(json.dumps(frozen))
    for ptr in declared:
        parts = ptr.strip("/").split("/")
        walk_delete(r, parts)
        walk_delete(f, parts)
    a = json.dumps(rec(r), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    b = json.dumps(f, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return a == b, hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest()


def strings_with_paths(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from strings_with_paths(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from strings_with_paths(v, path + "/%d" % i)
    elif isinstance(o, str):
        yield path, o


def dv5(out, rest):
    os.makedirs(out, exist_ok=True)
    rep, ok = {"plans": {}}, True
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    v2r1, a1r1 = R.load_json(R.PLAN_V2_R1), R.load_json(R.PLAN_A1_R1)
    rep["frozen_sha256"] = {"trial-plan-v2.json": sha(R.PLAN_V2), "trial-plan-v2-a1.json": sha(R.PLAN_A1)}
    ok &= rep["frozen_sha256"] == {"trial-plan-v2.json": R.PLAN_V2_SHA256, "trial-plan-v2-a1.json": R.PLAN_A1_SHA256}
    M = dict(v2r1["id_map"], **a1r1["id_map"])
    inverse = {v: k for k, v in M.items()}
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    fv2, fa1 = [p["run_id"] for p in v2["packages"]], [p["run_id"] for p in a1["packages"]]
    rep["M"] = {"entries": len(M), "bijection": len(set(M.values())) == 42 and len(M) == 42,
                "preimages_are_the_42_frozen_ids": set(M) == set(fv2) | set(fa1),
                "images_disjoint_from_v1_v2_a1": not (set(M.values()) & (v1 | set(fv2) | set(fa1))),
                "a1r1_id_map_v2_equals_v2r1_id_map": a1r1.get("id_map_v2") == v2r1["id_map"]}
    ok &= rep["M"]["entries"] == 42 and all(v for k, v in rep["M"].items() if k != "entries")
    mdv2, mda1 = md_declared_keys()
    # "trial-plan-v2.json lines 95-177": line 95 opens the object, line 177 holds its last member and line 178 is
    # its closing brace " }," (the cited range stops one line short of the brace; recorded as an observation).
    all_lines = open(R.PLAN_V2).read().splitlines()
    rep["watchdogs_line_range"] = {"line_95": all_lines[94], "line_177": all_lines[176], "line_178": all_lines[177]}
    wd_txt = "\n".join(all_lines[94:178]).strip()
    assert wd_txt.startswith('"watchdogs":') and all_lines[177] == " },"
    wd_obj = json.loads(wd_txt[len('"watchdogs":'):].rstrip().rstrip(","))
    for name, plan, frozen, md_keys, n_expected, fz_ids in (("trial-plan-v2-r1.json", v2r1, v2, mdv2, 31, fv2),
                                                              ("trial-plan-v2-a1-r1.json", a1r1, a1, mda1, 11, fa1)):
        declared = plan["repair"]["declared_key_paths"]
        eq, h_r, h_f = dv5_equal(plan, frozen, declared, inverse)
        allowed_old_prefixes = ["/id_map", "/v2_ids_never_reused", "/a1_ids_never_reused", "/retired_ids", "/frozen_v2_ids_never_reused",
                                "/id_map_v2"] if name == "trial-plan-v2-r1.json" else ["/id_map", "/id_map_v2", "/frozen_v2_ids_never_reused",
                                                                                      "/a1_ids_never_reused", "/retired_ids"]
        old = set(fv2) | set(fa1)
        stray = []
        for pth, s in strings_with_paths(plan):
            for t in TOK.findall(s):
                if t in old and not any(pth == a or pth.startswith(a + "/") for a in allowed_old_prefixes):
                    stray.append({"path": pth, "id": t})
        disclosed = [x for x in stray if x["path"] == "/gate/regression/reference_run"]
        undisclosed = [x for x in stray if x["path"] != "/gate/regression/reference_run"]
        pk_ids = [p["run_id"] for p in sorted(plan["packages"], key=lambda p: p["order"])]
        c = {"rc4c_equality_dv5_own_code": eq, "canonical_sha256_r1_side": h_r, "canonical_sha256_frozen_side": h_f,
             "declared_keys_equal_md_record": declared == md_keys,
             "watchdogs_identical_to_trial_plan_v2_lines_95_177": plan["watchdogs"] == wd_obj == v2["watchdogs"],
             "package_count": len(pk_ids) == n_expected,
             "every_package_id_is_the_image_of_the_frozen_id_in_order": pk_ids == [M[i] for i in [p["run_id"] for p in sorted(frozen["packages"], key=lambda p: p["order"])]],
             "no_old_id_outside_maps_lists_retired_ids_except_disclosed": not undisclosed,
             "no_forbidden_task_id": all(f not in json.dumps(plan) for f in R.FORBIDDEN_TASK_IDS),
             "protocol_label": plan["protocol_version"] == (R.PROTOCOL_V2_R1 if n_expected == 31 else R.PROTOCOL_A1_R1)}
        rep["plans"][name] = {"checks": c, "old_id_occurrences_disclosed": disclosed, "old_id_occurrences_undisclosed": undisclosed,
                              "md_declared_keys": md_keys}
        ok &= all(c[k] for k in c if not k.startswith("canonical"))
    if a1r1["v2_ids_never_reused"] != [M[i] for i in a1["v2_ids_never_reused"]]:
        ok = False
        rep["a1r1_v2_ids_never_reused_mapped"] = False
    else:
        rep["a1r1_v2_ids_never_reused_mapped"] = True
    pr = subprocess.run([sys.executable, "-B", os.path.join(HERE, "r1_make_plans.py"), "--check"], capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    rep["writer_regenerates_byte_identically"] = {"returncode": pr.returncode, "stdout": pr.stdout.splitlines(), "stderr": pr.stderr.splitlines()}
    ok &= pr.returncode == 0
    rep["pass"] = bool(ok)
    dump(os.path.join(out, "dv5.json"), rep)
    print(json.dumps({k: v["checks"] for k, v in rep["plans"].items()}, indent=1))
    print("writer --check:", pr.stdout.strip())
    print("DV-5:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-8 exclusion list + comparator
def dv8(out, rest):
    import r1_reg1 as REG
    os.makedirs(out, exist_ok=True)
    rep, ok = {}, True
    ex, ex_sha = REG.load_exclusions()
    never = set(ex["never_excludable"])
    rep["exclusion_list_sha256"] = ex_sha
    rep["entries_confined_to_permitted_categories"] = all(e["category"] in ex["permitted_categories"] for e in ex["entries"])
    rep["no_entry_names_a_never_excludable_field"] = all(not (set(e["path"]) & never) for e in ex["entries"])
    ok &= rep["entries_confined_to_permitted_categories"] and rep["no_entry_names_a_never_excludable_field"]
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)
    self_rep = REG.compare(ref, ref)
    rep["self"] = {"verdict": self_rep["verdict"], "output": REG.render(self_rep)}
    ok &= self_rep["verdict"] == "PASS"
    # perturbations on scratch copies, one per item (a)-(d)
    cases = {}

    def copy_ref(tag):
        d = os.path.join(out, "perturb", tag, R.REG1_REFERENCE_RUN)
        if os.path.exists(os.path.dirname(d)):
            shutil.rmtree(os.path.dirname(d))
        shutil.copytree(ref, d)
        return d

    d = copy_ref("a_ms_byte")
    p = os.path.join(d, "solver", "fx_reg0_S3.ms")
    b = bytearray(open(p, "rb").read()); i = b.rfind(b"1"); b[i:i + 1] = b"2"; open(p, "wb").write(bytes(b))
    cases["a: one byte of solver/fx_reg0_S3.ms"] = d
    d = copy_ref("b_raw_D")
    p = os.path.join(d, "raw-result.json")
    r = json.load(open(p)); r["targets"][2]["arms"]["S3"]["D"] += 1; json.dump(r, open(p, "w"), indent=1)
    cases["b: raw-result targets[2].arms.S3.D + 1"] = d
    d = copy_ref("c_cert_u")
    p = os.path.join(d, "certificates", "decomposition_S3_rescaled_tfresh1_r0.json")
    c = json.load(open(p)); c["factor_base"]["u_values"][0] = (c["factor_base"]["u_values"][0] + 1) % 4111; json.dump(c, open(p, "w"), indent=1)
    cases["c: certificates/decomposition_S3_rescaled_tfresh1_r0.json factor_base.u_values[0] + 1"] = d
    d = copy_ref("d_msout_byte")
    p = os.path.join(d, "solver", "fx_fresh2_raw_u.ms.out")
    b = bytearray(open(p, "rb").read()); i = b.find(b"4111") ; b[i:i + 1] = b"5"; open(p, "wb").write(bytes(b))
    cases["d: one byte of solver/fx_fresh2_raw_u.ms.out"] = d
    d = copy_ref("excluded_only")
    p = os.path.join(d, "raw-result.json")
    r = json.load(open(p)); r["metrics"]["wall_seconds"] = 1.0; r["targets"][0]["arms"]["S3"]["solver"]["wall_seconds"] = 99.0; json.dump(r, open(p, "w"), indent=1)
    p = os.path.join(d, "certificates", "decomposition_S3_tfresh1_r0.json")
    c = json.load(open(p)); c["run_id"] = "RUN-GFPN-a61a10"; json.dump(c, open(p, "w"), indent=1)
    cases["control: excluded fields only (metrics.wall_seconds, one solver.wall_seconds, one certificate run_id)"] = d
    rep["perturbations"] = {}
    for name, cd in cases.items():
        rr = REG.compare(ref, cd)
        must = "PASS" if name.startswith("control") else "FAIL"
        rep["perturbations"][name] = {"verdict": rr["verdict"], "expected": must, "failures": rr["failures"]}
        ok &= rr["verdict"] == must
        print("  %-100s %s (expected %s)" % (name, rr["verdict"], must))
    # the reference-integrity check itself: a comparator run whose REFERENCE bytes were altered must fail
    alt_receipt = os.path.join(out, "perturb", "receipt_altered.json")
    rc = R.load_json(R.RECEIPT_V2_PHASE_B)
    key = "experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-ac4487/raw-result.json"
    rc["path_sha256"][key] = "0" * 64
    dump(alt_receipt, rc)
    rr = REG.compare(ref, ref, receipt=alt_receipt)
    rep["reference_integrity_negative"] = {"verdict": rr["verdict"], "failures": rr["failures"][:3]}
    ok &= rr["verdict"] == "FAIL"
    rep["pass"] = bool(ok)
    dump(os.path.join(out, "dv8.json"), rep)
    with open(os.path.join(out, "dv8_self_output.txt"), "w") as fh:
        fh.write(rep["self"]["output"] + "\n")
    print("DV-8 self:", self_rep["verdict"], "; integrity negative:", rr["verdict"])
    print("DV-8:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-9 no edit
FROZEN_REL = ["implementation", "implementation-v2", "implementation-v2-a1", "implementation.md", "implementation-v2.md", "implementation-v2-a1.md",
              "trial-plan.json", "trial-plan-v2.json", "trial-plan-v2-a1.json", "specification.yaml", "amendments", "runs/RUN-GFPN-ac4487",
              "runs/RUN-GFPN-3377f1", "execution-report-v2.yaml"]


def tree_hashes():
    out = {}
    for rel in FROZEN_REL:
        p = os.path.join(R.EXP_DIR, rel)
        if os.path.isfile(p):
            out[rel] = sha(p)
        else:
            for dp, _dn, fn in os.walk(p):
                for f in fn:
                    fp = os.path.join(dp, f)
                    out[os.path.relpath(fp, R.EXP_DIR)] = sha(fp)
    return out


def dv9(out, rest):
    os.makedirs(out, exist_ok=True)
    base = {}
    for line in open(rest[0]):
        h, p = line.split(None, 1)
        base[p.strip()] = h
    now = tree_hashes()
    rep = {"baseline_file": rest[0], "n_baseline": len(base), "n_now": len(now),
           "changed": sorted(p for p in base if now.get(p) != base[p]), "added": sorted(set(now) - set(base)),
           "removed": sorted(set(base) - set(now))}
    rc_v2 = R.receipt_paths(R.load_json(R.RECEIPT_V2_PHASE_A))
    rc_a1 = R.receipt_paths(R.load_json(R.RECEIPT_A1_PHASE_A))
    rc_b = R.receipt_paths(R.load_json(R.RECEIPT_V2_PHASE_B))
    rep["equal_to_0fa03f_phase_A_receipt"] = all(sha(os.path.join(R.REPO, p)) == h for p, h in rc_v2.items())
    rep["equal_to_4ff597_phase_A_receipt"] = all(sha(os.path.join(R.REPO, p)) == h for p, h in rc_a1.items())
    rep["run_packages_equal_to_0fa03f_phase_B_receipt"] = all(sha(os.path.join(R.REPO, p)) == h for p, h in rc_b.items())
    rep["amendments"] = {os.path.basename(p): (sha(p), w, sha(p) == w) for p, w in R.BOUND_HASHES}
    pyc = []
    for dp, dn, fn in os.walk(R.EXP_DIR):
        for n in dn + fn:
            if n == "__pycache__" or n.endswith(".pyc"):
                pyc.append(os.path.relpath(os.path.join(dp, n), R.EXP_DIR))
    rep["bytecode_now"] = sorted(pyc)
    before = [l.strip()[2:] for l in open(rest[1]) if l.strip()]
    rep["bytecode_before"] = before
    rep["new_bytecode"] = sorted(set(pyc) - set(before))
    ok = (not rep["changed"] and not rep["added"] and not rep["removed"] and rep["equal_to_0fa03f_phase_A_receipt"]
          and rep["equal_to_4ff597_phase_A_receipt"] and rep["run_packages_equal_to_0fa03f_phase_B_receipt"]
          and all(v[2] for v in rep["amendments"].values()) and not rep["new_bytecode"])
    rep["pass"] = ok
    dump(os.path.join(out, "dv9.json"), rep)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("bytecode_now", "bytecode_before")}, indent=1)[:3000])
    print("DV-9:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


# ============================================================================ DV-10 ids
def dv10(out, rest):
    """rest[0]: the mint-time --check log (every bare id checked BEFORE any stage-R1 file named it). The current
    re-check is recorded as information only: by now the ids occur in the stage-R1 files themselves."""
    os.makedirs(out, exist_ok=True)
    ids = [x.strip() for x in open(os.path.join(HERE, "minted-run-ids.txt")) if x.strip()]
    mint_log = open(rest[0]).read()
    blocks, mint_rc = {}, {}
    for chunk in mint_log.split("### python3 -B tools/allocate_id.py --check ")[1:]:
        cid, body = chunk.split("\n", 1)
        blocks[cid.strip()] = body
        mrc = re.search(r"^rc=(\d+)$", body, re.M)
        mint_rc[cid.strip()] = int(mrc.group(1)) if mrc else None
    v2, a1 = R.load_json(R.PLAN_V2), R.load_json(R.PLAN_A1)
    v1 = set(v2["v1_ids_never_reused"]) | set(a1["v1_ids_never_reused"])
    fv2, fa1 = {p["run_id"] for p in v2["packages"]}, {p["run_id"] for p in a1["packages"]}
    checks = []
    for i in ids:
        pr = subprocess.run([sys.executable, "-B", os.path.join(R.REPO, "tools", "allocate_id.py"), "--check", i], capture_output=True, text=True, cwd=R.REPO)
        occ = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", pr.stdout)
        mocc = re.search(r"occurrences across the union \((\d+) identifier-bearing paths scanned\): (\d+)", blocks.get(i, ""))
        checks.append({"id": i, "mint_time_check_rc": mint_rc.get(i), "mint_time_occurrences": int(mocc.group(2)) if mocc else None,
                       "mint_time_ok": "OK: well-formed and free across the union." in blocks.get(i, ""),
                       "recheck_now_rc": pr.returncode, "recheck_now_occurrences": int(occ.group(2)) if occ else None,
                       "recheck_now_stdout": pr.stdout.strip().splitlines(),
                       "in_v1": i in v1, "in_v2": i in fv2, "in_a1": i in fa1,
                       "run_dir_exists": os.path.exists(os.path.join(R.RUNS_DIR, i))})
    rep = {"n": len(ids), "distinct": len(set(ids)), "checks": checks,
           "none_in_v1_v2_a1": not any(c["in_v1"] or c["in_v2"] or c["in_a1"] for c in checks),
           "no_run_dir": not any(c["run_dir_exists"] for c in checks),
           "retired_run_dirs": sorted(i for i in (fv2 | fa1) - {"RUN-GFPN-ac4487", "RUN-GFPN-3377f1"} if os.path.exists(os.path.join(R.RUNS_DIR, i)))}
    rep["all_mint_time_checks_ok_zero_occurrences"] = all(c["mint_time_check_rc"] == 0 and c["mint_time_occurrences"] == 0 and c["mint_time_ok"] for c in checks)
    rep["pass"] = (rep["n"] == 42 and rep["distinct"] == 42 and rep["none_in_v1_v2_a1"] and rep["no_run_dir"] and not rep["retired_run_dirs"]
                   and rep["all_mint_time_checks_ok_zero_occurrences"])
    dump(os.path.join(out, "dv10.json"), rep)
    print("DV-10: 42 ids; mint-time --check rc %s occurrences %s; re-check now rc %s occurrences %s (stage-R1 files)" % (
        sorted({c["mint_time_check_rc"] for c in checks}), sorted({c["mint_time_occurrences"] for c in checks}),
        sorted({c["recheck_now_rc"] for c in checks}), sorted({c["recheck_now_occurrences"] for c in checks})))
    print("DV-10:", "PASS" if rep["pass"] else "FAIL")
    return 0 if rep["pass"] else 1


def dispatch(check, out, rest):
    if check == "dv6":
        import r1_dv6
        return r1_dv6.dv6(out, rest)
    if check == "dv7":
        import r1_toy
        return r1_toy.dv7(out, rest)
    fn = {"dv1": dv1_static, "dv5": dv5, "dv8": dv8, "dv9": dv9, "dv10": dv10}[check]
    return fn(out, rest)
