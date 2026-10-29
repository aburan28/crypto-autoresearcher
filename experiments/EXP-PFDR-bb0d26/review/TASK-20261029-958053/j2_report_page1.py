#!/usr/bin/env python3
"""J2: page 1 of reports/run-20261023T2211Z/report.pdf against the run records (TASK-20261029-958053).

usage: j2_report_page1.py <repo_root> <out.json> <out_page1.txt>
Extracts page 1 with `pdftotext -f 1 -l 1 -layout`, then checks every run id and every quoted metric value
against the recorded raw-result.json / receipts (values compared after rounding the record the way the page
prints it: 5 significant digits for z-scores, 6 for fractions, integers exact).
"""
import json
import os
import re
import subprocess
import sys

EXP = "experiments/EXP-PFDR-bb0d26"


def main(root, out_json, out_txt):
    pdf = os.path.join(root, EXP, "reports/run-20261023T2211Z/report.pdf")
    txt = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    with open(out_txt, "w") as f:
        f.write(txt)
    R = os.path.join(root, EXP, "runs")
    raw = {r: json.load(open(os.path.join(R, r, "raw-result.json")))["summary"] for r in os.listdir(R) if r.startswith("RUN-")}
    rcpt = {r: json.load(open(os.path.join(R, r, "execution-receipt.json"))) for r in raw}
    checks = []

    def chk(name, ok, detail=None):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    for tid, rid in (("selftest", "RUN-PFDR-e44a19"), ("census-toy-main", "RUN-PFDR-4d8c71"),
                     ("analyze-main", "RUN-PFDR-243425"), ("census-toy-rep", "RUN-PFDR-cd03e2"),
                     ("analyze-final", "RUN-PFDR-089edc")):
        m = re.search(rf"^\s*{re.escape(tid)}(?: \(control\))?\s+(RUN-PFDR-[0-9a-f]{{6}})\s+(\S+)\s+(\S+)\s*$", txt, re.M)
        chk(f"page 1 unit row {tid}", m is not None and m.group(1) == rid and m.group(2) == rcpt[rid]["status"]
            and m.group(3) == "True", m.groups() if m else None)
    chk("page 1 names RUN-PFDR-243425 and RUN-PFDR-089edc", "RUN-PFDR-243425" in txt and "RUN-PFDR-089edc" in txt)
    chk("page 1 says 5 valid of 5", "5 valid of 5" in txt)

    def metric(name):
        m = re.search(rf"^\s*{name}\s+\S+\s+\S+\s+(\d+)\s+(.*)$", txt, re.M)
        return dict(kv.split("=") for kv in m.group(2).replace(",", " ").split()) if m else None

    fin, mainc, rep, st = raw["RUN-PFDR-089edc"], raw["RUN-PFDR-4d8c71"], raw["RUN-PFDR-cd03e2"], raw["RUN-PFDR-e44a19"]
    want = {
        "calibration_mean_final": {"max": f"{fin['calibration']['mean']:.5g}", "min": f"{fin['calibration']['mean']:.5g}"},
        "calibration_n_final": {"max": str(fin["calibration"]["n"]), "min": str(fin["calibration"]["n"])},
        "calibration_sd_final": {"max": f"{fin['calibration']['sd']:.5g}", "min": f"{fin['calibration']['sd']:.5g}"},
        "census_main_failed_infrastructure": {"max": str(mainc["failed_infrastructure"]), "sum": str(mainc["failed_infrastructure"])},
        "census_main_jobs": {"max": str(mainc["jobs"]), "sum": str(mainc["jobs"])},
        "census_rep_failed_infrastructure": {"max": str(rep["failed_infrastructure"]), "sum": str(rep["failed_infrastructure"])},
        "census_rep_jobs": {"max": str(rep["jobs"]), "sum": str(rep["jobs"])},
        "fraction_valid_final": {"max": f"{fin['fraction_valid']:.6g}", "min": f"{fin['fraction_valid']:.6g}"},
        "selftest_cells": {"max": str(st["cells"]), "min": str(st["cells"])},
    }
    for name, w in want.items():
        got = metric(name)
        ok = got is not None and all(got.get(k) == v for k, v in w.items()) and got.get("count") == "1"
        chk(f"page 1 metric {name}", ok, {"page": got, "record_rounded": w})
    chk("analyze-main and analyze-final summaries are identical (page quotes the final run)", raw["RUN-PFDR-243425"] == fin)
    out = {"page1_chars": len(txt), "checks": checks, "ok": all(c["ok"] for c in checks)}
    with open(out_json, "w") as f:
        json.dump(out, f, indent=1)
    for c in checks:
        print(("OK   " if c["ok"] else "FAIL ") + c["check"], "" if c["ok"] else c["detail"])
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
