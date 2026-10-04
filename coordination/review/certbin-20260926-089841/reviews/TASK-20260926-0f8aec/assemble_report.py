#!/usr/bin/env python3
"""Assemble validation-report.yaml for TASK-20260926-0f8aec from the joint
sections written (and sealed) earlier in the order recorded in ORDER.log.
The review_attestation block lives ONLY in attestation.yaml (one attestation
per task: tools/check_review_independence.py rejects duplicates)."""
import yaml
from pathlib import Path

D = Path(__file__).resolve().parent
sections = {}
for j, p in [("J2", "j2-construction/j2-section.yaml"), ("J3", "j3-closures/j3-section.yaml"),
             ("J4", "j4-checks/j4-section.yaml"), ("J5", "j5-j6-recompute/j5-section.yaml"),
             ("J6", "j5-j6-recompute/j6-section.yaml")]:
    sections[j] = yaml.safe_load(open(D / p))[j]
    sections[j]["section_file"] = f"coordination/review/certbin-20260926-089841/reviews/TASK-20260926-0f8aec/{p}"
head = yaml.safe_load(open(D / "report-head.yaml"))
vr = head["validation_report"]
vr["joints"] = sections
vr["order_of_work_RV-4"]["ORDER_log_verbatim"] = [l.rstrip("\n") for l in open(D / "ORDER.log")]
out = D / "validation-report.yaml"
with open(out, "w") as f:
    f.write("# TASK-20260926-0f8aec -- validation report, joints J2-J6 of REVIEW-CERTBIN-20260926-089841.\n"
            "# Assembled by assemble_report.py from the joint sections sealed in the order of ORDER.log.\n"
            "# It reports on J2-J6 only and gives no whole-claim verdict (RV-5). The review_attestation is attestation.yaml.\n")
    yaml.safe_dump(head, f, sort_keys=False, width=100, allow_unicode=False, default_flow_style=False)
print("wrote", out)
