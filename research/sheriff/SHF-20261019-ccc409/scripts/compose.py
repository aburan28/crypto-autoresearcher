#!/usr/bin/env python3
"""Compose verdicts.jsonl from the harness rows, replay rows and manual overrides.

Rules are mechanical and stated in REPORT.md. A field that no check reached is
null, never true. Verdicts are recommendations to the Coordinator, never edits.
"""
from __future__ import annotations
import json, re, glob, collections
from pathlib import Path
import yaml

CASE = Path(__file__).resolve().parents[1]
REPO = CASE.parents[2]

rows = {}
for l in open(CASE / "shards/all.jsonl"):
    d = json.loads(l)
    rows[d["evidence_id"]] = d
replay = {}
for f in sorted(glob.glob(str(CASE / "shards/replay_out[0-3].jsonl"))):
    for l in open(f):
        d = json.loads(l)
        replay[d["evidence_id"]] = d
mut = json.load(open(CASE / "mutation_detail.json"))

# ---- manual overrides: each one was re-checked by the Sonnet reader (see REPORT.md)
DIGEST_OVERRIDE = {
    "EV-BINSTD-9ac9c5": (True, "harness mismatch was a false positive: the dict also carries specification_sha256, which is not environment.json's digest; every file digest matches"),
    "EV-BINSTD-f9c882": (True, "same instrument false positive as EV-BINSTD-9ac9c5; file digests match"),
    "EV-ECQ-8ee697": (True, "harness took sha256_of_snapshot_field instead of sha256_read_at_run_time; the declared run-time digest 5eea69cf... equals the file's current sha256"),
    "EV-CERTBIN-091c56": (False, "26/28 declared digests match; tools/gf2_replay_rc1.py and tests/test_gf2_kernels.py changed after the run (code inputs drifted; a replay at HEAD runs different code)"),
    "EV-ICPERF-433fa5": (False, "convert.py matches its declared sha256 (harness took frozen_sha256); experiments/EXP-ICPERF-e21835/code/bench.py differs from both its declared and frozen digests (modified by e1728d8a88, 'Fix runner polling latency', after the manifest)"),
}
REPLAY_MANUAL_PASS = {  # harness said fail; the Sonnet reader re-ran and diffed: only time/platform/commit fields differ
    "EV-FALSIFY-440677": "diff after dropping platform/python/timestamp/git fields is empty",
    "EV-SEMBIN-07960c": "diff after dropping elapsed/platform/python/start fields is empty",
    "EV-MONO-d90e9c": "raw-result.json equal after dropping timings/rss; preregistration.json differs only in preregistered_at, which the replay rewrites to the replay's own clock",
}
RECOMPUTED = {
    "EV-ECDLP-284817": (True, "from raw-results.json: cost_ratio 0.0557+-0.0223 [0.0321,0.0926] and oracle_marginal_ratio 3.754+-3.187 [1.36,11.237] both reproduce over the 8 (p,b) groups; but 3.754 is the mean over groups of per-cell B/C ratios, whereas the record defines it as candidates_verified_B/candidates_verified_C, which gives 3.108+-2.088 per group (2.53 pooled)"),
}
FIDELITY = {
    "EV-ECDLP-284817": (False, "stated metric definition (ratio of totals) does not give the stated value (mean of per-cell ratios); minor, the direction (oracle raises candidates verified) holds under both"),
}
MANUAL_NOTES = {
    "EV-ECDLP-284817": ["run record RUN-SEMAEV-f48dd1-grid was rewritten in place by three commits on 2026-08-07 (metric correction, manifest CI, pseudo-replication correction): raw-results.json and analysis.yaml were modified, not superseded",
                        "the run's own analysis shows 40 cells are 8 independent (prime,b) groups: n_eff=8, one instrument, no independent review"],
    "EV-ECDLP-fd61e4": ["cites the same rewritten run RUN-SEMAEV-f48dd1-grid"],
    "EV-ICPERF-433fa5": ["label 'moderate' is not in schemas/evidence.schema.json; the record itself scopes it to the instrument only, with a BROKEN joint (O-6), an unfit wall-clock channel (O-7) and broken custody"],
}
NO_RUN_TYPES = {"theoretical", "analytical", "literature", "structural_exact", "paper_body_analysis",
                "paper_body_analysis_corrective", "design", "synthesis"}
ANALYTIC_PROOF = {"derivation", "certificate", "theoretical derivation", "verified_from_paper_body", "structural_exact"}

TASKS = {}
for d in glob.glob(str(REPO / "coordination/goals/*/batches/*/tasks/TASK-*")) + glob.glob(str(REPO / "coordination/**/TASK-*"), recursive=True):
    TASKS.setdefault(Path(d).name, d)
PATHRE = re.compile(r"(?:coordination|experiments|ledger|knowledge|research|tools|papers|formal|analysis|outputs|claims|docs|notes|inputs)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,6}")

out = []
for eid, r in sorted(rows.items()):
    cls = r["class"]
    if r.get("strength_raw") in ("anecdotal", "contradictory"):
        cls = "enum_other"  # valid schema value the harness bucketed as malformed; audited beyond the brief's scope
    p = REPO / "ledger/evidence" / f"{eid}.yaml"
    text = p.read_text()
    v = {"evidence_id": eid, "strength_claimed": r.get("strength_raw") if r.get("strength_raw") else None, "class": cls}
    notes, flags = [], []
    if cls == "malformed_parse_error":
        v.update(runs_found=None, digests_ok=None, recomputed_ok=None, replay_ok=None, independence_ok=None,
                 statement_fidelity_ok=None, verdict="unvalidated", recommended_strength=None,
                 notes=[f"record does not parse as YAML ({r.get('parse_error')}); nothing in it can be audited; the file cannot be read by any tool in this repo that loads ledger/evidence"],
                 flags=["unparsable"])
        out.append(v)
        continue
    ev = yaml.safe_load(text)
    toks = set(PATHRE.findall(text))
    tp_found = sorted(x for x in toks if (REPO / x).exists())
    review_paths = [x for x in tp_found if re.search(r"validation_report|red_team|review|validator", x)]
    task_ids = set(re.findall(r"TASK-\d{8}-[0-9a-f]{4,8}", text))
    tasks_found = sorted(t for t in task_ids if t in TASKS)
    v["text_paths_found"] = len(tp_found)
    v["task_ids_resolved"] = len(tasks_found)
    ev = ev.get("evidence", ev) if isinstance(ev, dict) else {}
    typ = ev.get("type")
    proof = ev.get("proof_status")
    nruns, nfound = r["run_ids_declared"], r["runs_found"]
    v["runs_declared"] = nruns
    v["runs_found"] = nfound
    # ---- digests
    d_ok = r["digests_ok"]
    if eid in DIGEST_OVERRIDE:
        d_ok, why = DIGEST_OVERRIDE[eid]
        notes.append("digest: " + why)
    v["digests_ok"] = d_ok
    v["digests_declared"] = r["digests"]["declared"]
    # ---- immutability
    cm = []
    for run in (r.get("runs_mutated_after_add") or {}):
        det = mut.get(run, {})
        if det.get("content_touched"):
            cm.append(run)
    if cm:
        authorised = all("declared" in " ".join(r["runs_mutated_after_add"][x]) for x in cm) and False
        flags.append("run_content_modified_after_add")
        kind = "FCP" if any("FCP" in x for x in cm) else ""
        notes.append(f"{len(cm)} cited run(s) had result/log content modified after first commit (git history): {', '.join(cm[:3])}{'...' if len(cm) > 3 else ''}"
                     + ("; FCP edits were the declared duplicate-id repair (CORR-20260802-004), content change is identifier substitution" if kind else ""))
    elif r.get("runs_mutated_after_add"):
        flags.append("run_metadata_modified_after_add")
        notes.append(f"{len(r['runs_mutated_after_add'])} cited run(s) had only manifest/metadata files modified after first commit")
    # ---- replay
    rp = replay.get(eid)
    rok = None
    if rp:
        st = rp["status"]
        if eid in REPLAY_MANUAL_PASS:
            rok, st = True, "pass (manual re-diff)"
            notes.append("replay: " + REPLAY_MANUAL_PASS[eid])
        elif st == "pass":
            rok = True
            notes.append("replay: command re-run in scratch worktree at the audited commit; regenerated result file(s) equal the committed ones after dropping time-like keys")
        elif st == "fail":
            rok = False
        else:
            notes.append(f"replay sampled but {st}: {(rp.get('reason') or '')[-90:]}")
        v["replay_status"] = st
    v["replay_ok"] = rok
    # ---- recompute / fidelity
    rc = RECOMPUTED.get(eid)
    v["recomputed_ok"] = rc[0] if rc else None
    if rc:
        notes.append("recompute: " + rc[1])
    fd = FIDELITY.get(eid)
    v["statement_fidelity_ok"] = fd[0] if fd else None
    if fd:
        notes.append("fidelity: " + fd[1])
    notes += MANUAL_NOTES.get(eid, [])
    # ---- independence (cited-artifact signals; record text only for 'asserted')
    sig = r["independence_signals"]
    rb = ev.get("reviewed_by")
    rb_s = json.dumps(rb) if rb else ""
    non_coord = bool(rb) and not re.fullmatch(r'"?(coordinator|Coordinator)[^"]{0,80}"?', rb_s) and not re.search(r"^\"?coordinator", rb_s, re.I) \
        or sig["validator"] or sig["red_team"]
    asserted = bool(re.search(r"blind re-?deriv|independent(ly)? (re-?deriv|reproduc|implementation|session|validator|reviewer|re-?analy)|second engine|red[- ]team", text, re.I))
    is_analytic = (typ in NO_RUN_TYPES) or (nruns == 0 and proof in ANALYTIC_PROOF)
    if non_coord and (sig["validator"] or sig["red_team"] or isinstance(rb, list)) and (review_paths or tasks_found):
        ind = True
        notes.append(f"independence: reviewer artifacts resolve on disk ({(review_paths or tasks_found)[:2]}); roles/authors not individually read")
    elif non_coord and (sig["validator"] or sig["red_team"] or isinstance(rb, list)):
        ind = None
        notes.append("independent reviewer named but no reviewer artifact resolves on disk")
    elif is_analytic and cls in ("replicated", "strong", "moderate") and not asserted:
        ind = False
    elif asserted:
        ind = None
        notes.append("independence asserted in the record's own text but no independent reviewer artifact is cited in reviewed_by/review_refs")
    else:
        ind = False if cls in ("replicated", "strong", "moderate") else None
    v["independence_ok"] = ind
    # ---- resolution
    resolvable = nfound > 0 or r["refs_found"] > 0 or r["experiments_found"] > 0 or bool(tp_found) or bool(tasks_found)
    if nruns and nfound < nruns:
        flags.append("runs_missing")
        notes.append(f"{nruns - nfound}/{nruns} declared run ids do not resolve to experiments/*/runs/: {r['runs_missing'][:3]}")
    if r["refs_missing"]:
        flags.append("refs_missing")
        notes.append(f"cited refs missing on disk: {r['refs_missing'][:3]}")
    if r["text_run_tokens_unresolved"]:
        notes.append(f"run ids named in prose but absent from disk: {r['text_run_tokens_unresolved'][:3]}")
    if r["numbers_claimed"] and nruns:
        notes.append(f"number trace (not a recompute): {r['numbers_traced_to_run_artifacts']}/{r['numbers_claimed']} 4+-digit decimals in the claim appear verbatim in the cited run files")
    if d_ok is None and nruns:
        notes.append("no sha256 declared in the cited run records (digests not_covered)")
    # ---- verdict
    empirical = (typ in (None, "empirical", "measurement", "instrument_fitness") or proof == "empirical_only") and not is_analytic
    if empirical and nruns == 0 and not resolvable:
        verdict = "unvalidated"
        notes.append("empirical-type record with no run, experiment or artifact reference that resolves on disk")
    elif nruns and nfound == 0:
        verdict = "unvalidated"
    elif rok is False or v["recomputed_ok"] is False:
        verdict = "contradicted" if (v["recomputed_ok"] is False) else "unvalidated"
    elif (d_ok is True and ind is True and (rok or v["recomputed_ok"]) and "run_content_modified_after_add" not in flags and nfound):
        verdict = "validated"
    elif resolvable:
        verdict = "validated_with_caveats"
    else:
        verdict = "unvalidated"
        notes.append("nothing the record cites resolves on disk")
    if cls.startswith("malformed") and verdict == "validated":
        verdict = "validated_with_caveats"
    # ---- recommended strength
    nexp = r["experiment_ids"]
    reproduction = (nruns >= 2) or (nexp >= 2) or ind is True or (rok is True)
    basis = None
    rec = None
    if cls == "enum_other":
        rec, basis = r.get("strength_raw"), "valid schema value; outside the brief's scope (audited because the harness bucketed it with the malformed records)"
    elif cls.startswith("malformed"):
        rec = "coordinator_to_assign"
        basis = f"strength value {r.get('strength_raw')!r} is outside the schema enum {{anecdotal,preliminary,replicated,strong,inconclusive,contradictory}}"
        if r.get("strength_raw") and re.search(r"strong|decisive|replicat", str(r.get("strength_raw")), re.I):
            basis += "; the prose value reads as a strong/decisive claim, which the audit does not support above the ceiling shown"
        ceiling = "preliminary" if reproduction and nfound else ("anecdotal" if nfound else "not_assessable")
        v["strength_ceiling_supported"] = ceiling
    elif is_analytic:
        rec = cls if cls != "moderate" else "preliminary"
        basis = "derivation/analysis record: cited artifacts resolve, derivation not re-derived by this audit (not_covered), so the label is unconfirmed rather than disproved"
        if cls == "moderate":
            basis = "'moderate' is not a schema value; map to preliminary unless a coordinator rule says otherwise"
        if ind is False and cls == "strong":
            basis += "; reviewed by Coordinator only"
    elif cls == "moderate":
        rec = "replicated" if reproduction else "preliminary"
        basis = "'moderate' is not a schema value; mapped by reproduction evidence on disk"
    elif cls == "replicated":
        rec = "replicated" if reproduction else "preliminary"
        basis = None if reproduction else "empirical record with <=1 run, 1 experiment and no cited independent reproduction: nothing on disk shows a second reproduction"
    elif cls == "strong":
        if not reproduction:
            rec, basis = "preliminary", "single run/experiment and no cited independent reproduction: multiple instances not shown on disk"
        elif ind is False:
            rec, basis = "replicated", "reproduced (>=2 runs/experiments, or this audit's replay passed) but Coordinator self-review only: no cited independent validator or red team"
        else:
            rec = "strong"
    if eid == "EV-ECDLP-284817":
        rec, basis = "preliminary", "one run, n_eff=8 groups after its own pseudo-replication correction, one instrument, no independent review, and the run record was rewritten in place"
    v["recommended_strength"] = rec
    v["downgrade_basis"] = basis
    v["verdict"] = verdict
    v["notes"] = notes
    v["flags"] = flags
    out.append(v)

with open(CASE / "verdicts.jsonl", "w") as f:
    for v in out:
        f.write(json.dumps(v) + "\n")
c = collections.Counter((v["class"] if v["class"] in ("replicated", "strong", "moderate", "enum_other") else "malformed", v["verdict"]) for v in out)
for k, n in sorted(c.items()):
    print(k, n)
d = collections.Counter()
for v in out:
    cl = v["class"] if v["class"] in ("replicated", "strong", "moderate") else "malformed"
    if v.get("recommended_strength") and v["recommended_strength"] != v["strength_claimed"]:
        d[(cl, v["strength_claimed"] if cl != "malformed" else "n/a|other", v["recommended_strength"])] += 1
print(d)
