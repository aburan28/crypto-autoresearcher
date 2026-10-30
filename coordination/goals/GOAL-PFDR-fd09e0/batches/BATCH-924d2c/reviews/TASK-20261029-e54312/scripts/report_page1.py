"""J2a(7) / gap G-6: extract page 1 of reports/run-20261023T2211Z/report.pdf (pdftotext -f 1 -l 1 -layout) and
check its statements against analysis.json, raw-result.json and the manifests. Read-only.

usage: python3 -I -B report_page1.py <repo-root> <out-txt> <out-json>
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import yaml

repo, out_txt, out_json = sys.argv[1:4]
E = os.path.join(repo, "experiments/EXP-PFDR-bb0d26")
pdf = os.path.join(E, "reports/run-20261023T2211Z/report.pdf")
txt = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
ver = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True).stderr.splitlines()[0]
with open(out_txt, "w") as f:
    f.write(txt)
an = json.load(open(os.path.join(E, "runs/RUN-PFDR-089edc/analysis.json")))
census = json.load(open(os.path.join(E, "runs/RUN-PFDR-4d8c71/raw-result.json")))
rep = json.load(open(os.path.join(E, "runs/RUN-PFDR-cd03e2/raw-result.json")))
journal = [json.loads(ln) for ln in open(os.path.join(E, "runbook-sessions/RBS-PFDR-bb0d26/journal.jsonl"))]
man = yaml.safe_load(open(os.path.join(E, "runs/RUN-PFDR-089edc/manifest.yaml")))["run"]
plan_ids = [("selftest", "RUN-PFDR-e44a19"), ("census-toy-main", "RUN-PFDR-4d8c71"), ("analyze-main", "RUN-PFDR-243425"),
            ("census-toy-rep", "RUN-PFDR-cd03e2"), ("analyze-final", "RUN-PFDR-089edc")]
rows = re.findall(r"^\s*(selftest|census-toy-main|analyze-main|census-toy-rep|analyze-final)\b.*?(RUN-PFDR-[0-9a-f]{6})\s+(\S+)\s+(\S+)\s*$",
                  txt, re.M)


def metric(name):
    m = re.search(rf"^\s*{name}\s+\S+\s+\S+\s+\d+\s+(.*)$", txt, re.M)
    return m.group(1).strip() if m else None


checks = []


def chk(name, ok, page, record):
    checks.append({"check": name, "ok": bool(ok), "page1": page, "record": record})


chk("run ids and trials in plan order", [(r[0], r[1]) for r in rows] == plan_ids, [(r[0], r[1]) for r in rows], plan_ids)
chk("all five units output_validated / valid True", all(r[2] == "output_validated" and r[3] == "True" for r in rows),
    [r[2:] for r in rows], "journal units seq 11-15 valid true")
chk("units line '5 valid of 5; invalid: none'", "5 valid of 5; invalid: none" in txt, "5 valid of 5" in txt,
    journal[-1]["summary"]["units"])
cm, cs, cn = metric("calibration_mean_final"), metric("calibration_sd_final"), metric("calibration_n_final")
chk("calibration mean (5 significant digits)", cm == f"count=1, max={an['calibration']['mean']:.5g}, min={an['calibration']['mean']:.5g}",
    cm, an["calibration"]["mean"])
chk("calibration sd (5 significant digits)", cs == f"count=1, max={an['calibration']['sd']:.5g}, min={an['calibration']['sd']:.5g}",
    cs, an["calibration"]["sd"])
chk("calibration n", cn == f"count=1, max={an['calibration']['n']}, min={an['calibration']['n']}", cn, an["calibration"]["n"])
fv = metric("fraction_valid_final")
chk("fraction_valid (6 significant digits)", fv == f"count=1, max={an['fraction_valid']:.6g}, min={an['fraction_valid']:.6g}",
    fv, an["fraction_valid"])
chk("census_main_jobs", metric("census_main_jobs") == f"count=1, max={census['summary']['jobs']}, sum={census['summary']['jobs']}",
    metric("census_main_jobs"), census["summary"]["jobs"])
chk("census_rep_jobs", metric("census_rep_jobs") == f"count=1, max={rep['summary']['jobs']}, sum={rep['summary']['jobs']}",
    metric("census_rep_jobs"), rep["summary"]["jobs"])
chk("outcome stated on page 1", an["outcome"] in txt, "absent" if an["outcome"] not in txt else "present", an["outcome"])
chk("headline stated on page 1", an["headline"] in txt, "absent" if an["headline"] not in txt else "present", an["headline"])
cmt = re.search(r"Commit: ([0-9a-f]{40})", txt)
chk("page-1 commit equals the run manifests' commit", cmt and cmt.group(1) == man["code"]["commit"],
    cmt.group(1) if cmt else None, {"run manifests": man["code"]["commit"], "journal seq 0 preflight": journal[0]["preflight"]["commit"],
                                    "journal seq 9 preflight": journal[9]["preflight"]["commit"]})
tip = re.search(r"Journal tip: ([0-9a-f]{64}) \((\d+) entries\)", txt)
chk("journal tip and entry count", tip and tip.group(1) == journal[-1]["hash"] and int(tip.group(2)) == len(journal),
    tip.groups() if tip else None, [journal[-1]["hash"], len(journal)])
contradictions = [c for c in checks if not c["ok"] and c["check"] not in ("outcome stated on page 1", "headline stated on page 1",
                                                                          "page-1 commit equals the run manifests' commit")]
blocked = open(os.path.join(E, "reports/run-20261022T1218Z/RENDER-BLOCKED.txt")).read().strip()
out = {"script": "scripts/report_page1.py", "pdftotext": ver,
       "pdf_sha256": hashlib.sha256(open(pdf, "rb").read()).hexdigest(), "page1_text": os.path.basename(out_txt),
       "checks": checks, "contradictions_with_records": contradictions,
       "render_blocked_run_20261022T1218Z": {"text": blocked, "has_pdf": os.path.exists(os.path.join(E, "reports/run-20261022T1218Z/report.pdf"))}}
with open(out_json, "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
for c in checks:
    print(c["ok"], c["check"], "|", c["page1"], "|", c["record"])
print("contradictions", len(contradictions))
