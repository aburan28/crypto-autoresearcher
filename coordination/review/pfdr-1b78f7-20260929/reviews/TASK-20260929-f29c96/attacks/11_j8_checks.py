"""J8: DEV-B, DEV-C, DEV-D checks and the DEV-A timeline facts (no randomness).

DEV-B  At each of the four merge-written locations, (1) every entry of the archived
       checksums.sha256 matches its file; (2) the pre-regeneration checksums.sha256 is
       RECONSTRUCTED: the archived stdout.log minus its final line is hashed, that hash replaces
       the stdout.log entry of the archived (post-regeneration) checksums.sha256, and the
       result's sha256 is compared with the "before" hash recorded in
       implementation-notes-amd430f44.yaml.  Equality proves the regeneration changed exactly
       one entry (stdout.log) and that stdout.log changed by exactly its final line.
       (3) view-map.json / view-map-stage-r.json entries against the archived files.
DEV-C  every file in job and attempt directories outside the M-1 layout, and whether any
       run-root or merged/ directory (the view targets analyze_census.py reads) holds a name
       that would shadow a canonical input (e.g. an uncompressed rows.jsonl beside rows.jsonl.gz).
DEV-D  interpreter, Python and numpy versions of every environment.json of the experiment's runs,
       attempts and jobs, and the interpreter named in every command.txt.
Output: attacks/out/11_j8_checks.json
"""
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import EXP, OUT, P, RUNS  # noqa: E402

BEFORE = {"RUN-PFDR-1b78f7-census-m4/merged": "aafaa717f912b0b243989acbd46c9f959812d5dc044f66a8efc0d6dde31df7c7",
          "RUN-PFDR-1b78f7-census-m5": "7f97b083dfb7189783940c0564126ce0161db68aaae46ff271eb0396f664310d",
          "RUN-PFDR-1b78f7-j0": "bc91aca1704b0a22ed1e7d02f6fff1ffca5dfc108bad9a0ce0383111238809a5",
          "RUN-PFDR-1b78f7-stage-r": "61a474c6a3dc6bb2631dca64ad642cc90dac7bf5e99672ebb0056bbf38ed1333"}
AFTER = {"RUN-PFDR-1b78f7-census-m4/merged": "ac2fd60354ab3ba19f0ce47b5a59cabece65cca63b9465774e69f85aa185f3f0",
         "RUN-PFDR-1b78f7-census-m5": "0740bab03861f5abd8ff830b9fb21e82dd76097cd0e8a7eab2b4fac9b46179f1",
         "RUN-PFDR-1b78f7-j0": "c1cc45c411e179e4b69ea49fcb53b6bf88bc1dccacd49a5594fab9062f154ee8",
         "RUN-PFDR-1b78f7-stage-r": "36616a7876d5fff88d4a160b3d3a3f577cbfa3e911330f4b94ad271bcc67d797"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fsha(p):
    with open(p, "rb") as fh:
        return sha(fh.read())


def dev_b():
    out = {}
    for loc, before in BEFORE.items():
        d = os.path.join(RUNS, loc)
        cs_path = os.path.join(d, "checksums.sha256")
        raw = open(cs_path, "rb").read()
        rec = {"archived_checksums_sha256": sha(raw), "recorded_after": AFTER[loc],
               "archived_equals_recorded_after": sha(raw) == AFTER[loc]}
        bad = []
        lines = raw.decode().splitlines()
        for ln in lines:
            h, rel = ln.split("  ", 1)
            p = os.path.join(d, rel)
            if not os.path.exists(p) or fsha(p) != h:
                bad.append(rel)
        rec["entries"] = len(lines)
        rec["entries_not_matching_file"] = bad
        so = open(os.path.join(d, "stdout.log"), "rb").read()
        body = so.rstrip(b"\n").split(b"\n")
        last = body[-1].decode()
        trunc = b"\n".join(body[:-1]) + b"\n"
        new_lines = []
        for ln in lines:
            h, rel = ln.split("  ", 1)
            new_lines.append(f"{sha(trunc)}  {rel}" if rel == "stdout.log" else ln)
        rebuilt = ("\n".join(new_lines) + "\n").encode()
        rec["stdout_final_line"] = last
        rec["reconstructed_before_sha256"] = sha(rebuilt)
        rec["recorded_before"] = before
        rec["reconstruction_equals_recorded_before"] = sha(rebuilt) == before
        rec["entries_differing_before_vs_after"] = ["stdout.log"] if sha(rebuilt) == before else "not established"
        out[loc] = rec
    # view maps
    vm = {}
    for vpath in (os.path.join(RUNS, P + "analysis", "view-map.json"),
                  os.path.join(RUNS, P + "stage-r", "view-map-stage-r.json")):
        v = json.load(open(vpath))
        diffs = []
        for e in v["entries"]:
            tgt = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(RUNS))), e["target"])
            for rel, h in e["files_sha256"].items():
                p = os.path.join(tgt, rel)
                cur = fsha(p) if os.path.exists(p) else None
                if cur != h:
                    diffs.append({"target": e["target"], "file": rel, "view_hash": h[:16], "archived_hash": (cur or "MISSING")[:16],
                                  "view_hash_is_recorded_before": h in BEFORE.values()})
        vm[os.path.relpath(vpath, RUNS)] = {"entries": len(v["entries"]), "differences": diffs}
    out["view_maps"] = vm
    return out


M1_JOB = {"rows.jsonl.gz", "harvest-rows.jsonl.gz", "staircase.jsonl.gz", "command.txt", "stdout.log",
          "stderr.log", "execution.json"}
M1_ATTEMPT = {"jobs-index.json", "manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log",
              "checksums.sha256", "raw-result.json", "jobs"}


def dev_c():
    extra_job = Counter()
    extra_attempt = defaultdict(list)
    for jd in glob.glob(os.path.join(RUNS, P + "*", "attempt-*", "jobs", "*")) + \
            glob.glob(os.path.join(RUNS, P + "census-m4", "attempt-2", "invocation-check", "b26-c0")):
        for f in os.listdir(jd):
            if f not in M1_JOB:
                extra_job[f] += 1
    for ad in glob.glob(os.path.join(RUNS, P + "*", "attempt-*")):
        for f in os.listdir(ad):
            if f not in M1_ATTEMPT:
                extra_attempt[os.path.relpath(ad, RUNS)].append(f)
    shadows = []
    for run in sorted(glob.glob(os.path.join(RUNS, P + "*"))):
        tgt = os.path.join(run, "merged") if os.path.isdir(os.path.join(run, "merged")) else run
        names = set(os.listdir(tgt))
        for base in ("rows.jsonl", "staircase.jsonl"):
            if base in names:
                shadows.append(os.path.relpath(os.path.join(tgt, base), RUNS))
    reads = ("analyze_census.py reads, per view target: rows.jsonl(.gz) [uncompressed preferred if present], "
             "staircase.jsonl(.gz), execution.json, regression-report.json, raw-result.json; --stage-r: <out>/rows.jsonl(.gz) "
             "and <view>/RUN-PFDR-1b78f7-analysis/analysis.json. merge_census.py reads jobs-index.json, the job rows/"
             "staircase/harvest-rows .gz files named in it, the root attempt-1 files and receipts.")
    return {"extra_files_in_job_dirs": dict(extra_job), "extra_files_in_attempt_dirs": dict(extra_attempt),
            "uncompressed_shadow_files_in_view_targets": shadows, "names_read": reads}


def dev_d():
    envs = []
    for p in sorted(glob.glob(os.path.join(RUNS, P + "*", "**", "environment.json"), recursive=True)):
        e = json.load(open(p))
        envs.append({"path": os.path.relpath(p, RUNS), "python": e.get("python_version") or e.get("python"),
                     "numpy": e.get("numpy_version"), "executable": e.get("python_executable") or e.get("executable")})
    interp = Counter()
    for p in glob.glob(os.path.join(RUNS, P + "*", "**", "command.txt"), recursive=True):
        first = open(p).read().split()
        if first:
            interp[first[0]] += 1
    vals = Counter((x["python"], x["numpy"], x["executable"]) for x in envs)
    return {"environment_json_files": len(envs), "distinct_(python, numpy, executable)": [list(k) + [v] for k, v in vals.items()],
            "command_txt_first_token": dict(interp)}


def main():
    out = {"DEV-B": dev_b(), "DEV-C": dev_c(), "DEV-D": dev_d()}
    with open(os.path.join(OUT, "out", "11_j8_checks.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps(out, indent=1, default=str)[:8000])


if __name__ == "__main__":
    main()
