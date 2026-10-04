"""Phase 7 writers: environment.json, manifest.yaml, run-report.md.
Observations only; no conclusion about H-CERTBIN-be6cbd."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import yaml

import common
from common import ROOT, now, read_jsonl_gz, sha256_file, write_json

SPEC_PATH = "experiments/EXP-CERTBIN-ddfe75/specification.yaml"


def _git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def environment():
    import numpy
    try:
        import mpmath
        mpv = mpmath.__version__
    except Exception:  # pragma: no cover
        mpv = None
    from crypto_autoresearcher.gf2 import _native, kernels
    mem = None
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal"):
                mem = line.split(":")[1].strip()
    except OSError:
        pass
    return {"python": sys.version, "executable": sys.executable, "numpy": numpy.__version__, "mpmath": mpv,
            "pyyaml": yaml.__version__, "platform": platform.platform(), "machine": platform.machine(),
            "cpu_count": os.cpu_count(), "mem_total": mem,
            "gf2_backend": kernels.backend(), "gf2_build_info": dict(_native.build_info),
            "gf2_threads": kernels.default_threads(),
            "env": {k: os.environ.get(k) for k in ["CRYPTO_AR_GF2_BACKEND", "PYTHONDONTWRITEBYTECODE",
                                                   "CRYPTO_AR_GF2_THREADS", "RUN_ID", "OPENBLAS_NUM_THREADS",
                                                   "NCONV_DEV_SLOTS", "NCONV_DEV_SEED_OFFSET",
                                                   "AUTORESEARCH_POLICY", "AUTORESEARCH_BACKEND"]},
            "recorded_at": now()}


def phase_timings(out):
    ev = [json.loads(l) for l in open(out / "phase-log.jsonl")]
    t = {}
    for e in ev:
        k = str(e["phase"])
        t.setdefault(k, []).append({kk: e.get(kk) for kk in ("event", "at", "seconds", "maxrss_mb")})
    return t, max(e.get("maxrss_mb") or 0 for e in ev)


def write_all(R, args, d):
    out = R.out
    env = environment()
    write_json(out / "environment.json", env)
    head = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain")
    invs = [json.loads(l) for l in open(out / "checkpoint" / "invocations.jsonl")]
    spec_head = subprocess.run(["git", "show", f"HEAD:{SPEC_PATH}"], cwd=ROOT, capture_output=True).stdout
    import hashlib
    spec_byte_ident = hashlib.sha256(spec_head).hexdigest() == sha256_file(ROOT / SPEC_PATH)
    pkg_diff = _git("status", "--porcelain", "--", "src/crypto_autoresearcher/gf2")
    impl = {p.name: sha256_file(p) for p in sorted((common.EXP / "impl").glob("*")) if p.is_file()}
    verif = {p.name: sha256_file(p) for p in sorted((common.EXP / "verifier").glob("*")) if p.is_file()}
    timings, peak = phase_timings(out)
    cv, ncv, det = d["cv"], d["ncv"], d["det"]
    vinfo = json.load(open(out / "certificate-verification.json"))["meta"]
    man = {"run": {
        "id": args.run_id, "experiment_id": "EXP-CERTBIN-ddfe75", "task_id": "TASK-20260924-7c1fb2",
        "archived_by": "TASK-20260924-40b2ca", "approval_decision": "DEC-20260924-833c70",
        "status": d["validity"],
        "invalid_reasons": [f"{k} failed ({v['invalidation_rule']})" for k, v in d["ic"].items() if not v["pass"]],
        "claim_tier": "toy",
        "certificate": {"kind": "unsatisfiability_certificate", "formats": ["flat-v1", "wdag-v1"],
                        "verifier": "experiments/EXP-CERTBIN-ddfe75/verifier/verify_nconv.py (separate process)",
                        "submitted": cv["n_submitted"], "verified": cv["n_verified"], "failed": cv["n_failed"],
                        "per_closure_arm_format": d["cert_tab"], "uncertified": d["unc_tab"],
                        "negative_controls": {"n": ncv["n"], "rejected": ncv["n_rejected"]},
                        "independence": ("code-level: the verifier imports nothing from impl/, crypto_autoresearcher, "
                                         "any archived impl/ or any review directory; NOT author-independent of impl/ "
                                         "(same executor session wrote both); the engine was written by the dispatching session")},
        "code": {"commit_at_first_invocation": invs[0]["commit"], "dirty_at_first_invocation": invs[0]["dirty"],
                 "dirty_paths_at_first_invocation": invs[0]["dirty_paths"],
                 "commit_at_report": head, "dirty_at_report": bool(status),
                 "impl_sha256": impl, "verifier_sha256": verif, "invocations": invs,
                 "verifier_invocation": vinfo, "command_file": "command.txt"},
        "trial_plan": {"path": "experiments/EXP-CERTBIN-ddfe75/trial-plan-v1.json",
                       "sha256": d["p0"]["trial_plan_sha256"], "written_at": d["p0"]["trial_plan_written_at"],
                       "predates_phase0": d["p0"]["trial_plan_predates_phase0"]},
        "specification": {"path": SPEC_PATH, "sha256": sha256_file(ROOT / SPEC_PATH),
                          "byte_identical_to_approved": spec_byte_ident,
                          "approved_version_ref": "HEAD (" + head + "), which contains the design snapshot TASK-20260924-f6c337"},
        "engine": {"package": "src/crypto_autoresearcher/gf2", "pinned_commit": "934bee5",
                   "tree_rule": d["eng"]["a_tree_rule"], "kernels_c_sha256": d["eng"]["b_hashes"]["kernels_c_sha256"],
                   "package_files_sha256": d["eng"]["b_hashes"]["package_files_sha256"],
                   "build_info": d["eng"]["e_build_info"]["build_info"],
                   "kernels_backend": d["eng"]["e_build_info"]["kernels_backend"],
                   "package_unchanged_at_report": pkg_diff == "",
                   "import_mode": "sys.path insertion of src/ (no editable install)",
                   "threads": env["gf2_threads"]},
        "inference": {"requested_policy": "executor-implementation", "canonical_policy": "executor-implementation",
                      "backend": "anthropic", "adapter_resolved_model_id": "claude-sonnet-5",
                      "resolved_model_id": "claude-opus-5-5",
                      "model_provenance": "operator-supplied (executor session model as reported by the Claude Code runtime)",
                      "model_verified": False, "requested_reasoning_effort": "medium", "reasoning_effort": None,
                      "fallback_used": True,
                      "fallback_reason": ("Claude Code subagent inherits the session model (claude-opus-5-5); the adapter "
                                          "binds executor-implementation to claude-sonnet-5. fallback_allowed: true in the "
                                          "handoff (DEC-20260923-4d7a19 R-1)."),
                      "independent_session": False,
                      "note": "The model wrote the code. Every number comes from deterministic code; no model in the computational loop."},
        "environment": {"see": "environment.json", "python_version": platform.python_version(),
                        "numpy_version": env["numpy"], "memory_cap": "RLIMIT_AS 3 GiB (ulimit -v in the launch shell and setrlimit in the driver)",
                        "threads": env["gf2_threads"],
                        "dev_overrides_unset": not (common.DEV_SLOTS or common.DEV_SEED_OFFSET)},
        "inputs": json.load(open(out / "inputs.json"))["files"],
        "seeds": {"S_selftest": common.SEED_SELFTEST, **common.ARM_SEEDS},
        "randomness": ("numpy 2.4.6 PCG64, one generator per fresh arm (seeds above) and one for the self-test; "
                       "no other source of randomness; archived arms use no seed"),
        "phase_timings": timings, "peak_rss_mb_driver": peak,
        "validity": {"status": d["validity"], "instrument_checks": {k: v["pass"] for k, v in d["ic"].items()},
                     "raw_vs_summary_agree": d["agree"]},
        "determinism": {"pass": det["pass"], "pid": det.get("pid")},
        "deviations": "see implementation.md in this run directory",
    }}
    with open(out / "manifest.yaml", "w") as f:
        yaml.safe_dump(man, f, sort_keys=False, width=110)
    write_report(out, args, d, man)


def _yn(b):
    return "held" if b else "failed"


def write_report(out, args, d, man):
    dr, ar, ic = d["dr"], d["arm_rows"], d["ic"]
    L = []
    a = L.append
    a(f"# Run report: EXP-CERTBIN-ddfe75 / {args.run_id} (N-CONV)\n")
    a("Observations only. No hypothesis status is changed and no heuristic is declared supported or refuted.\n")
    a(f"Validity status: **{d['validity']}**. Task TASK-20260924-7c1fb2; archived by TASK-20260924-40b2ca.\n")
    a("## Claim tier and scope (verbatim from the specification)\n")
    a("Claim tier: toy. " + ("Closure measurements on synthetic Boolean systems derived from one cell: n = 17, "
      "f = t^17 + t^3 + 1, m = 2, l = 9, V = {deg < 9} (polynomial basis), curve A = 97044, B = 126251 "
      "(#E = 4 * 32603). The targets are the 144 archived x_R of RUN-CERTBIN-c417e0 (sets U62, S62, C20; all "
      "x(2E) subgroup targets). The closures are M_4, W_4 and their ell-substituted counterparts, as defined below.") + "\n")
    a("sota_delta: zero on every ECDLP cost axis (time, memory, data). dominated_by: oracle A (2^9 = 512 quadratic "
      "root-findings over V per attempt at m = 2) and parallel Pollard rho (about 160 group operations at q = 32603). "
      "No cost claim. Nothing here transfers to n = 19, other curves or V, or off-x(2E) targets without measurement.\n")
    a("## Primary verdicts (NC-DR-9)\n")
    r1 = dr["NC-DR-1"]
    a(f"- NC-DR-1: **{r1['verdict']}**. L1 (uncertified counted as not refuted): w = {r1['L1_uncertified_as_not_refuted']['w']}, "
      f"n_C = {r1['L1_uncertified_as_not_refuted']['n_C']}, CP95 {r1['L1_uncertified_as_not_refuted']['cp95']}, label "
      f"{r1['L1_uncertified_as_not_refuted']['label']}. L2 (uncertified excluded): w = {r1['L2_uncertified_excluded']['w']}, "
      f"n_C = {r1['L2_uncertified_excluded']['n_C']}, label {r1['L2_uncertified_excluded']['label']}. Uncertified: {r1['uncertified']}. "
      f"E-TENSOR falsified (w <= floor(n_C/2)): {r1['L1_uncertified_as_not_refuted']['E_TENSOR_falsified']}; "
      f"E-LINEAR falsified (w > floor(n_C/2)): {r1['L1_uncertified_as_not_refuted']['E_LINEAR_falsified']}.")
    r4 = dr["NC-DR-4"]
    a(f"- NC-DR-4: **{r4['verdict']}**" + (f" (sub-label: {r4['sub_label']})" if r4["sub_label"] else "") +
      f". N-CONV ABOVE N-ELL144: {r4['N-CONV_above_N-ELL144']}; N-CONV ABOVE NULL-F262: {r4['N-CONV_above_NULL-F262']}. "
      f"N-CONVL level: {r4['N-CONVL_level']}. Appended N-CONV17 reading: {r4['appended_N-CONV17_reading']}.\n")
    a("## Secondary verdicts\n")
    a(f"- NC-DR-2: {dr['NC-DR-2']['label']} (N-CONV CP95 {dr['NC-DR-2']['N-CONV_cp95']} vs 386/386 CP95 "
      f"{dr['NC-DR-2']['S3_386_cp95']}); against in-run S_3 (82): {dr['NC-DR-2']['in_run_S3_82']['label']}.")
    a("- NC-DR-3 ladder (W_4, verified wdag-v1, CP95):")
    for arm, v in dr["NC-DR-3"]["intervals"].items():
        a(f"  - {arm}{' [one affine draw]' if arm == 'NULL-AFF62' else ''}: {v['x']}/{v['n']}, CP95 {v['cp95']}")
    above = [p for p, lab in dr["NC-DR-3"]["pairs"].items() if "ABOVE" in lab]
    a("  - ABOVE relations: " + ("; ".join(dr["NC-DR-3"]["pairs"][p] for p in above) if above else "none") +
      "; every other ordered pair NOT DISTINGUISHED.")
    a("- NC-DR-5 (descriptive; label on unsatisfiable systems):")
    for arm, v in dr["NC-DR-5"]["per_arm"].items():
        for pop, x in v.items():
            if pop == "unsat" or (arm == "S3-S62" and pop == "all"):
                a(f"  - {arm} ({pop}): {x['reference_profile']}/{x['n']} reference profile -> {x['label']}; "
                  f"T5_applicable {x['T5_applicable']}/{x['n']}")
    r6 = dr["NC-DR-6"]
    a(f"- NC-DR-6: {r6['N-CONV_label']}. M_4 per arm: " + "; ".join(
        f"{k} {v['x']}/{v['n']}" for k, v in r6["per_arm_M4"].items()) +
      f". N-CONV W_4 among M_4-unrefuted: {r6['N-CONV_W4_given_M4_unrefuted']['x']}/{r6['N-CONV_W4_given_M4_unrefuted']['n']}.")
    a(f"- NC-DR-7 (recorded, Coordinator decides after review): {dr['NC-DR-7']['recommendation']}.")
    a(f"- NC-DR-8: all instrument checks pass: {dr['NC-DR-8']['all_pass']}.\n")
    a("## Instrument checks\n")
    for k, v in ic.items():
        a(f"- {k}: {'PASS' if v['pass'] else 'FAIL'} ({v['invalidation_rule']})")
    a("")
    a("## Predictions PN-1..PN-5 (H-CERTBIN-be6cbd), mechanical reading\n")
    w = r1["L1_uncertified_as_not_refuted"]
    pn1 = {"TENSOR": "E-TENSOR threshold met", "LINEAR": "E-LINEAR threshold met", "MIXED": "neither threshold met (MIXED)"}.get(
        r1["verdict"], r1["verdict"])
    a(f"- PN-1: w = {w['w']} of n_C = {w['n_C']}: {pn1}.")
    a(f"- PN-2 (L-TOP, P equal to S_3's at the same x_R; N-CONV17 one P): {_yn(ic['C-TOP']['pass'])} "
      f"({ic['C-TOP']['detail']['checked']} systems checked).")
    a(f"- PN-3 (T4 on every substituted system; T5 where applicable): {_yn(ic['C-T4']['pass'])} "
      f"(T4 {ic['C-T4']['detail']['T4_checked']} systems, T5 {ic['C-T4']['detail']['T5_checked']}).")
    sat_ref = sum(v["M4_refuted_engine"] + v["W4_refuted_engine"] for v in d["sat_rows"].values())
    a(f"- PN-4 (0 refuted satisfiable controls): {_yn(sat_ref == 0 and ic['C-PS']['pass'])} ({sat_ref} refutations).")
    nell = ar["N-ELL144"]
    a(f"- PN-5 (N-ELL144 refuted 0 times where T5 applies with the semi-regular profile): "
      f"N-ELL144 W_4 engine refutations {nell['W4_engine']}/{nell['n']}; see NC-DR-5 for the T5/profile fractions.\n")
    a("## Coordinator prior (a)-(g): observed outcome against the modal expectation\n")
    lvN = r1["verdict"]
    a(f"- (a) N-CONV modal TENSOR: observed {lvN}.")
    a(f"- (b) N-CONV M_4 rate at least S_3's Stage-1 rate (324/386 = 0.839): observed {ar['N-CONV']['M4_verified']}/{ar['N-CONV']['n']}.")
    sr = d["semireg"].get("N-CONV", {}).get("unsat", {})
    a(f"- (c) N-CONV substituted profiles non-semi-regular on >= 90%: observed reference (semi-regular) profile on "
      f"{sr.get('reference_profile')}/{sr.get('n')}.")
    a(f"- (d) N-CONVL TENSOR-level: observed {dr['NC-DR-4']['N-CONVL_level']} ({ar['N-CONVL']['W4_verified']}/{ar['N-CONVL']['n']}).")
    a(f"- (e) N-CONV17 (no confident prior): observed {dr['NC-DR-4']['N-CONV17_level']} ({ar['N-CONV17']['W4_verified']}/{ar['N-CONV17']['n']}).")
    a(f"- (f) N-ELL144 refuted 0 times: observed {nell['W4_engine']} engine refutations.")
    tot_unc = sum(len(v) for k, v in d["unc_tab"].items() if k.startswith("W_4"))
    a(f"- (g) every W_4 refutation gets a verified wdag-v1: uncertified W_4 refutations {tot_unc}; failed certificates "
      f"{d['cv']['n_failed']}.\n")
    a("## E_hex bit layout\n")
    a("A system is 17 rows (f_0..f_16). Row k is a 172-bit integer written as lowercase hex without prefix; bit j "
      "(least significant first) is column j of mu_order(2, 18): column 0 the constant, columns 1..18 v_0..v_17, "
      "columns 19..171 the 153 pairs (a, b), a < b, in ascending tuple order. E_sha256 = sha256(json.dumps(E_hex)). "
      "Assignments and solutions are 18-bit integers with bit i = v_i.\n")
    a("## Independence disclosure\n")
    a("The engine crypto_autoresearcher.gf2 (pinned at 934bee5, _kernels.c sha256 "
      "c8f79d5961fffaf80428cdd29d0a53bfcc1e6d32ab07022931e3aacd926ca745) was written by the dispatching session, "
      "not by this executor and not by any reviewer. impl/ and verifier/ were both written by this executor in one "
      "session. The verifier is code-independent of the engine and of impl/ (it imports neither and re-derives every "
      "system, draw stream, satisfiability count and certificate check with its own code), but it is NOT "
      "author-independent of impl/. Author-independent verification is the review round's (claim_tier_and_review "
      "joints 1-3).\n")
    a("## Artifacts\n")
    a("manifest.yaml, command.txt, environment.json, stdout.log, stderr.log, raw-result.json, cell-summary.json, "
      "decision-rules.json, instrument-checks.json, engine-provenance/, selftest.json, inputs.json, support.json, "
      "draws-*.jsonl.gz, instances.jsonl.gz, predictions-t5.jsonl.gz, closures.jsonl.gz, certificates.jsonl.gz, "
      "certificate-verification.json, construction-verification.json, draw-replay-verification.json, "
      "negative-controls-certificates.jsonl.gz, negative-controls-verification.json, determinism.json, "
      "phase-log.jsonl, implementation.md, checkpoint/.\n")
    (out / "run-report.md").write_text("\n".join(L) + "\n")
