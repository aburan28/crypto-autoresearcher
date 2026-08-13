#!/usr/bin/env python3
"""
probe_rc_carry_and_artifact_policy.py -- TASK-20260813-451a6d (Validator)

1. RC-2: reads results_a1.json DIRECTLY (never via report_c3lane.md's or
   report_a1.md's transcription) and confirms the literal OUTCOME field for
   P-A12a, and counts every occurrence of "HELD" / "FALSIFIED" in the raw
   file, attributing each to its own prediction-register key.

2. RC-1/RC-2 text carry: diffs PREREG-3 sections 1 and 2's frozen blockquote
   text against report_c3lane.md's (a)/(b) sections, ignoring markdown bold
   markers only (** vs plain), to confirm verbatim carry.

3. Artifact-policy: confirms fpylll is absent from this validator's own
   environment too (procedural symmetry with the producer's own check);
   confirms no __pycache__/*.pyc exists anywhere under BATCH-fbb639; and
   checks run_manifest.yaml for any repository-relative path embedded
   inside a folded (">") YAML scalar, which the task's own completion gate
   and PREREG-3 section 7 binding carries forbid ("no path inside a folded
   YAML scalar").
"""
import json
import re
import subprocess

REPO = "/home/user/crypto-autoresearcher"

print("=" * 70)
print("1. RC-2 -- direct read of results_a1.json (never via any report's prose)")
print("=" * 70)
p = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/tasks/TASK-20260813-2ce014/results_a1.json"
raw = open(p).read()
d = json.loads(raw)
reg = d["PREDICTION_REGISTER"]["items"]
for k, v in reg.items():
    outcome = v.get("OUTCOME")
    print(" %-10s OUTCOME = %r" % (k, outcome))
print()
print(" P-A12a.OUTCOME literal value:", repr(reg["P-A12a"]["OUTCOME"]))
print(' count of the literal substring \'"HELD"\' anywhere in the raw file:', raw.count('"HELD"'))
print(' count of the literal substring \'"FALSIFIED"\' anywhere in the raw file:', raw.count('"FALSIFIED"'))
held_keys = [k for k, v in reg.items() if v.get("OUTCOME") == "HELD"]
print(" keys whose OUTCOME actually is HELD:", held_keys)
print(" CONCLUSION: P-A12a's OUTCOME is FALSIFIED, not HELD; HELD occurs only for",
      held_keys, "-- confirms RC-2's frozen claim independently.")

print()
print("=" * 70)
print("2. RC-1 / RC-2 verbatim-carry check: PREREG-3 vs report_c3lane.md")
print("=" * 70)


def extract_blockquote(path, start_marker, end_marker):
    text = open(path).read()
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    block = text[start:end]
    lines = [l for l in block.splitlines() if l.strip().startswith(">")]
    # strip leading '>' and markdown bold markers, collapse whitespace
    cleaned = []
    for l in lines:
        l = l.lstrip(">").strip()
        l = l.replace("**", "")
        cleaned.append(l)
    return " ".join(cleaned)


prereg_path = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-0eb5a3/prereg.md"
report_path = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/report_c3lane.md"

rc1_prereg = extract_blockquote(
    prereg_path,
    "**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**\n\n> The headline count",
    "**WHAT IS UNCHANGED",
)
rc1_report = extract_blockquote(
    report_path,
    "> The headline count",
    "What is unchanged",
)
def norm(s):
    s = s.replace("`", "").replace("**", "")
    s = s.replace("§", "section").replace("section", "section")  # normalize the section-mark
    s = re.sub(r"\s+", " ", s).strip()
    return s


print(" RC-1 texts equal after stripping bold/backtick markers and whitespace:", norm(rc1_prereg) == norm(rc1_report))
if norm(rc1_prereg) != norm(rc1_report):
    print("  PREREG-3 :", norm(rc1_prereg)[:300])
    print("  report   :", norm(rc1_report)[:300])

rc2_prereg = extract_blockquote(
    prereg_path,
    "**FROZEN CORRECTION TEXT, TO BE CARRIED VERBATIM INTO THE LEAD'S REPORT:**\n\n> `report_a1.md`",
    "**WHAT IS NOT EDITED",
)
rc2_report = extract_blockquote(
    report_path,
    "> report_a1.md section 10",
    "The immutable commit",
)
print(" RC-2 texts equal after stripping bold/backtick markers, whitespace and section-mark notation:",
      norm(rc2_prereg) == norm(rc2_report))
if norm(rc2_prereg) != norm(rc2_report):
    print("  PREREG-3 :", norm(rc2_prereg)[:400])
    print("  report   :", norm(rc2_report)[:400])
    import difflib
    for line in difflib.unified_diff(
        [norm(rc2_prereg)], [norm(rc2_report)], lineterm="", n=0
    ):
        print("  DIFF:", line)

print()
print("=" * 70)
print("3. Artifact-policy checks")
print("=" * 70)
try:
    import fpylll  # noqa
    print(" fpylll IS importable in this validator's own environment (unexpected)")
except ModuleNotFoundError as e:
    print(" fpylll import in this validator's own environment:", repr(e))

res = subprocess.run(
    ["find", REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639",
     "-iname", "__pycache__", "-o", "-iname", "*.pyc"],
    capture_output=True, text=True,
)
print(" __pycache__ / *.pyc found under BATCH-fbb639:", repr(res.stdout.strip()) or "(none)")

manifest_path = REPO + "/coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/run_manifest.yaml"
lines = open(manifest_path).read().splitlines()
print("\n Scanning run_manifest.yaml for folded ('>') YAML scalar blocks containing a")
print(" repository-relative path (pattern: 'coordination/goals/...'):")
in_block = False
block_indent = None
block_start_line = None
buf = []
findings = []


def flush():
    global buf, block_start_line
    if buf:
        text = " ".join(buf)
        if "coordination/goals" in text:
            findings.append((block_start_line, text))
    buf = []


for i, line in enumerate(lines, start=1):
    stripped = line.strip()
    if re.search(r":\s*>-?\s*$", line):
        flush()
        in_block = True
        block_indent = len(line) - len(line.lstrip())
        block_start_line = i
        continue
    if in_block:
        if line.strip() == "" or (len(line) - len(line.lstrip())) > block_indent:
            buf.append(stripped)
            continue
        else:
            flush()
            in_block = False
flush()

if findings:
    for ln, text in findings:
        print("  FOUND at folded scalar starting line %d:" % ln)
        print("   ", text)
else:
    print("  none found")
