#!/usr/bin/env python3
"""J3 binding and package checks, TASK-20260924-c83b05 (read-only on the
archived package; writes only j3-checks/bindings_results.json).

B1  every TASK-20260924-e27f93 receipt path: sha256 at HEAD == receipt; the
    path is tracked and clean (git diff --quiet HEAD); the receipt covers every
    committed file under impl/, verifier/ and the run directory (besides
    manifest_v2.yaml, bound separately).
B2  manifest.yaml impl_sha256 / verifier_sha256 == e27f93 receipt == HEAD;
    manifest artifacts[] sha256 == HEAD for every listed file; which run files
    are NOT in the manifest (E-2: implementation.md).
B3  closure_module_sha256 recorded in every closure checkpoint == committed
    closure.py; certificate-verification.json verifier_sha256 == committed
    verify_cert.py; certs_sha256 == certificates.jsonl.gz.
B4  invocations.jsonl: argv, pid, time, commit, dirty; porcelain entries at
    the first invocation classified (untracked '??' vs modified tracked); the
    commit's reachability; the specification unchanged since that commit.
B5  trial-plan-v1.json: written_at before the first invocation and before
    the first closure checkpoint; spec sha256 == committed spec; contains no
    computed value and no instance index (scan for 'idx', keys).
B6  manifest_v2.yaml vs manifest.yaml: YAML-level flattened key diff (added,
    removed, changed); manifest_v2 sha256 == registry superseding_sha256 ==
    a4f217 prior_commit_bindings; manifest.yaml == registry superseded_sha256.
B7  inputs.json / c-src-driver.json vs the c2e57b receipt and vs HEAD.
B8  the a4f217 review-opening receipt: its path_sha256 at HEAD.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
EXP = "experiments/EXP-CERTBIN-e94b27"
RUN = EXP + "/runs/RUN-CERTBIN-c417e0"
import yaml  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(REPO, p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)


def flat(d, p=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{p}.{k}" if p else str(k)))
    elif isinstance(d, list):
        out[p] = json.dumps(d, sort_keys=True, default=str)
    else:
        out[p] = d
    return out


def main():
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J3", "head": git("rev-parse", "HEAD").stdout.strip()}
    rec = json.load(open(os.path.join(REPO, "coordination/design/certbin-followups-20260924/archives/TASK-20260924-e27f93/snapshot-receipt.json")))
    # B1
    b1 = {"paths": len(rec["path_sha256"]), "mismatch": [], "untracked_or_dirty": []}
    for p, h in rec["path_sha256"].items():
        if sha(p) != h:
            b1["mismatch"].append(p)
        if git("ls-files", "--error-unmatch", p).returncode != 0 or git("diff", "--quiet", "HEAD", "--", p).returncode != 0:
            b1["untracked_or_dirty"].append(p)
    tracked = [x for x in git("ls-files", EXP + "/impl", EXP + "/verifier", RUN, EXP + "/trial-plan-v1.json").stdout.split()]
    b1["tracked_files_not_in_receipt"] = sorted(set(tracked) - set(rec["path_sha256"]))
    b1["receipt_paths_not_tracked"] = sorted(set(rec["path_sha256"]) - set(tracked))
    b1["pass"] = not b1["mismatch"] and not b1["untracked_or_dirty"]
    res["B1_e27f93_receipt_rehash"] = b1
    # B2
    man = yaml.safe_load(open(os.path.join(REPO, RUN, "manifest.yaml")))["run"]
    b2 = {"impl_sha256_mismatch_vs_receipt": [], "impl_sha256_mismatch_vs_head": [], "verifier_mismatch": []}
    for f, h in man["code"]["impl_sha256"].items():
        p = f"{EXP}/impl/{f}"
        if rec["path_sha256"].get(p) != h:
            b2["impl_sha256_mismatch_vs_receipt"].append(f)
        if sha(p) != h:
            b2["impl_sha256_mismatch_vs_head"].append(f)
    for f, h in man["code"]["verifier_sha256"].items():
        p = f"{EXP}/verifier/{f}"
        if rec["path_sha256"].get(p) != h or sha(p) != h:
            b2["verifier_mismatch"].append(f)
    b2["impl_files_in_manifest"] = sorted(man["code"]["impl_sha256"])
    b2["impl_files_at_head"] = sorted(os.path.basename(x) for x in tracked if x.startswith(EXP + "/impl/"))
    arts = man["artifacts"]
    b2["manifest_artifacts"] = len(arts)
    b2["artifact_mismatch_vs_head"] = [f for f, v in arts.items() if sha(f"{RUN}/{f}") != v["sha256"]]
    run_files = sorted(os.path.relpath(x, RUN) for x in tracked if x.startswith(RUN + "/"))
    b2["run_files_not_in_manifest_artifacts"] = [f for f in run_files if f not in arts]
    b2["implementation_md_sha256_head"] = sha(f"{RUN}/implementation.md")
    b2["implementation_md_sha256_e27f93"] = rec["path_sha256"][f"{RUN}/implementation.md"]
    b2["pass"] = not (b2["impl_sha256_mismatch_vs_receipt"] or b2["impl_sha256_mismatch_vs_head"] or b2["verifier_mismatch"]
                      or b2["artifact_mismatch_vs_head"])
    res["B2_manifest_code_and_artifact_hashes"] = b2
    # B3
    csha = sha(f"{EXP}/impl/closure.py")
    per = {}
    for f in sorted(os.listdir(os.path.join(REPO, RUN, "checkpoint"))):
        if f.startswith("p-") and f.endswith(".json.gz"):
            d = json.load(gzip.open(os.path.join(REPO, RUN, "checkpoint", f), "rt"))
            per[f] = d.get("closure_module_sha256")
    ver = json.load(open(os.path.join(REPO, RUN, "certificate-verification.json")))
    neg = json.load(open(os.path.join(REPO, RUN, "negative-controls-verification.json")))
    res["B3_closure_and_verifier_hashes_at_use"] = {
        "committed_closure_py": csha, "checkpoint_closure_module_sha256": per,
        "all_checkpoints_equal_committed": all(v == csha for v in per.values()),
        "verifier_sha256_in_certificate_verification": ver["verifier_sha256"],
        "verifier_sha256_in_negative_controls_verification": neg["verifier_sha256"],
        "committed_verify_cert_py": sha(f"{EXP}/verifier/verify_cert.py"),
        "certs_sha256_recorded": ver["certs_sha256"], "certificates_jsonl_gz_sha256": sha(f"{RUN}/certificates.jsonl.gz"),
        "neg_certs_sha256_recorded": neg["certs_sha256"],
        "negative_controls_certificates_sha256": sha(f"{RUN}/negative-controls-certificates.jsonl.gz"),
        "verifier_imports_recorded": {"main": ver["imports"], "negative": neg["imports"]},
        "verifier_pid": {"main": ver["pid"], "negative": neg["pid"]},
    }
    b3 = res["B3_closure_and_verifier_hashes_at_use"]
    b3["pass"] = (b3["all_checkpoints_equal_committed"] and b3["verifier_sha256_in_certificate_verification"] == b3["committed_verify_cert_py"]
                  and b3["verifier_sha256_in_negative_controls_verification"] == b3["committed_verify_cert_py"]
                  and b3["certs_sha256_recorded"] == b3["certificates_jsonl_gz_sha256"]
                  and b3["neg_certs_sha256_recorded"] == b3["negative_controls_certificates_sha256"]
                  and not ver["imports"] and not neg["imports"])
    # B4
    invs = [json.loads(line) for line in open(os.path.join(REPO, RUN, "checkpoint", "invocations.jsonl"))]
    first = invs[0]["git"]
    st = first["status_porcelain"]
    commit = first["commit"]
    b4 = {"invocations": [{"at": i["at"], "pid": i["pid"], "argv_tail": i["argv"][1:], "commit": i["git"]["commit"],
                           "dirty": i["git"]["dirty"], "porcelain_entries": len(i["git"]["status_porcelain"])} for i in invs],
          "first_invocation_porcelain_untracked": sum(1 for s in st if s.startswith("??")),
          "first_invocation_porcelain_modified_tracked": [s for s in st if not s.startswith("??")],
          "first_invocation_untracked_of_this_experiment": [s[3:] for s in st if s[3:].startswith(EXP)],
          "first_invocation_untracked_of_other_experiments": sorted(set(s[3:].split("/")[1] for s in st if not s[3:].startswith(EXP))),
          "commit_is_ancestor_of_head": git("merge-base", "--is-ancestor", commit, "HEAD").returncode == 0,
          "spec_unchanged_between_commit_and_head": git("diff", "--quiet", commit, "HEAD", "--", f"{EXP}/specification.yaml").returncode == 0,
          "any_dev_limit_invocation_recorded": any("--dev-limit" in i["argv"] for i in invs)}
    res["B4_invocations_and_dirty_tree"] = b4
    # B5
    tp = json.load(open(os.path.join(REPO, EXP, "trial-plan-v1.json")))
    p1 = json.load(gzip.open(os.path.join(REPO, RUN, "checkpoint", "p1-sets-oracles-base.json.gz"), "rt"))
    w4u = json.load(gzip.open(os.path.join(REPO, RUN, "checkpoint", "p-W_4-U62.json.gz"), "rt"))
    selft = json.load(open(os.path.join(REPO, RUN, "selftest.json")))
    txt = json.dumps(tp)
    res["B5_trial_plan"] = {
        "written_at": tp["written_at"], "selftest_finished_at": selft["finished_at"],
        "first_driver_invocation_at": invs[0]["at"], "phase1_finished_at": p1["finished_at"],
        "first_closure_checkpoint_finished_at": w4u["finished_at"],
        "written_before_first_invocation": tp["written_at"] < invs[0]["at"],
        "written_before_first_closure": tp["written_at"] < w4u["finished_at"],
        "spec_sha256_in_plan": tp["specification"]["sha256"], "spec_sha256_head": sha(f"{EXP}/specification.yaml"),
        "contains_computed_values_flag": tp["contains_computed_values"],
        "top_level_keys": sorted(tp),
        "mentions_idx_key": '"idx"' in txt,
        "sha256_head": sha(f"{EXP}/trial-plan-v1.json"), "sha256_manifest": man["trial_plan"]["sha256"],
        "note": "written_at is self-recorded by make_trial_plan.py; git cannot date an untracked file, so the ordering rests on the plan's own timestamp and on the plan sha256 recorded in the manifest and the e27f93 receipt.",
    }
    # B6
    a = yaml.safe_load(open(os.path.join(REPO, RUN, "manifest.yaml")))
    b = yaml.safe_load(open(os.path.join(REPO, RUN, "manifest_v2.yaml")))
    fa, fb = flat(a), flat(b)
    reg = yaml.safe_load(open(os.path.join(REPO, "tools/run_supersession_registry.yaml")))
    entries = reg if isinstance(reg, list) else (reg.get("records") or reg.get("supersessions") or reg.get("entries") or [])
    ent = [e for e in entries if isinstance(e, dict) and e.get("run_id") == "RUN-CERTBIN-c417e0"]
    a4 = json.load(open(os.path.join(REPO, "coordination/review/certbin-20260924-3d7e1a/archives/TASK-20260924-a4f217/snapshot-receipt.json")))
    pcb = a4["SC-6"]["prior_commit_bindings"]
    res["B6_manifest_v2_key_diff"] = {
        "keys_removed": sorted(set(fa) - set(fb)),
        "keys_added": {k: fb[k] for k in sorted(set(fb) - set(fa))},
        "keys_changed": {k: [fa[k], fb[k]] for k in sorted(set(fa) & set(fb)) if fa[k] != fb[k]},
        "manifest_v2_sha256_head": sha(f"{RUN}/manifest_v2.yaml"),
        "registry_entries_for_run": len(ent),
        "registry_superseding_sha256": ent[0]["superseding_sha256"] if ent else None,
        "registry_superseded_sha256": ent[0]["superseded_sha256"] if ent else None,
        "registry_kind": ent[0].get("supersession_kind") if ent else None,
        "a4f217_binding_sha256": pcb["experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/manifest_v2.yaml"]["sha256"],
        "manifest_sha256_head": sha(f"{RUN}/manifest.yaml"),
        "manifest_v2_introduced_by": git("log", "--format=%h %s", "--", f"{RUN}/manifest_v2.yaml").stdout.strip(),
        "registry_sha256_head": sha("tools/run_supersession_registry.yaml"),
        "a4f217_registry_sha256_at_head": pcb["tools/run_supersession_registry.yaml"]["sha256_at_head"],
    }
    b6 = res["B6_manifest_v2_key_diff"]
    b6["bindings_consistent"] = (b6["manifest_v2_sha256_head"] == b6["registry_superseding_sha256"] == b6["a4f217_binding_sha256"]
                                 and b6["manifest_sha256_head"] == b6["registry_superseded_sha256"])
    # B7
    inp = json.load(open(os.path.join(REPO, RUN, "inputs.json")))
    cs = json.load(open(os.path.join(REPO, RUN, "checkpoint", "c-src-driver.json")))
    c2 = json.load(open(os.path.join(REPO, "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json")))["path_sha256"]
    d3 = json.load(open(os.path.join(REPO, "coordination/design/certbin-followups-20260924/archives/TASK-20260924-d3a90c/snapshot-receipt.json")))["path_sha256"]
    rows = []
    for r in inp["inputs"]:
        rows.append({"path": r["path"], "recorded": r["sha256"] == c2.get(r["path"]), "head": sha(r["path"]) == c2.get(r["path"]),
                     "driver_c_src_same": any(x["path"] == r["path"] and x["sha256"] == r["sha256"] for x in cs["inputs"])})
    res["B7_c_src"] = {"inputs": rows, "all_match": all(x["recorded"] and x["head"] and x["driver_c_src_same"] for x in rows),
                       "specification_recorded": inp["specification"]["sha256"], "specification_d3a90c": d3.get(f"{EXP}/specification.yaml"),
                       "specification_head": sha(f"{EXP}/specification.yaml"),
                       "c_src_files_list_equals_spec_inputs_plus_copied_sources": [r["path"] for r in inp["inputs"]]}
    # B8
    res["B8_a4f217_rehash"] = {"mismatch": [p for p, h in a4["path_sha256"].items() if sha(p) != h], "paths": len(a4["path_sha256"])}
    json.dump(res, open(os.path.join(HERE, "bindings_results.json"), "w"), indent=1, default=str)
    print(json.dumps({"B1": b1["pass"], "B1_notin": b1["tracked_files_not_in_receipt"], "B2": b2["pass"],
                      "B2_not_in_manifest": b2["run_files_not_in_manifest_artifacts"], "B3": b3["pass"],
                      "B4_modified_tracked": b4["first_invocation_porcelain_modified_tracked"],
                      "B4_ancestor": b4["commit_is_ancestor_of_head"], "B4_spec_same": b4["spec_unchanged_between_commit_and_head"],
                      "B5": [res["B5_trial_plan"]["written_before_first_invocation"], res["B5_trial_plan"]["written_before_first_closure"],
                             res["B5_trial_plan"]["mentions_idx_key"]],
                      "B6_removed": b6["keys_removed"], "B6_changed": b6["keys_changed"], "B6_added": list(b6["keys_added"]),
                      "B6_bind": b6["bindings_consistent"], "B7": res["B7_c_src"]["all_match"], "B8": res["B8_a4f217_rehash"]["mismatch"]},
                     indent=0))


if __name__ == "__main__":
    main()
