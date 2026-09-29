#!/usr/bin/env python3
"""RED TEAM PROBE, TASK-20260826-5ee48b, joint J4.

QUESTION: after a cell COMPLETES, what does the module-level signal payload
`_H_PAYLOAD` still contain, and would a SIGTERM delivered in the inter-cell
window flush a record describing a cell that did not fail?

SCALE: d=64, beta=20, mpfr_bits=53 -- the batch's own acceptance scale. NO
d=512 reduction. NO mpfr_bits=100 cell. Two toy cells, in-process, with
arm_signals=False so this probe installs NO handler and kills nothing.

It does not call the handler (the handler ends in os._exit). It decodes the
bytes the handler WOULD write, which is the same object by construction:
`_signal_flush_and_die` does `os.write(_H_FD, _H_PAYLOAD[signum])`.
"""
import json
import os
import sys

TASKDIR = (
    "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
    "batches/BATCH-762807/tasks/TASK-20260826-602395"
)
sys.path.insert(0, TASKDIR)
import rt_ctrl_1_matched_pair_v2 as v2  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
workdir = os.path.join(OUT, "_probe_workdir")
os.makedirs(workdir, exist_ok=True)

journal = v2.Journal(os.path.join(workdir, "probe_results.jsonl"))
tee = v2.StdoutTee(os.path.join(workdir, "probe_stdout.log"))

findings = {}

# --- cell 1: run it to normal completion, exactly as the suite does ---------
rec1 = v2.run_cell(
    d=64, beta=20, mpfr_bits=53, role="probe_cell_1",
    journal=journal, tee=tee, strategies=v2.DEFAULT_STRATEGIES,
    heartbeat_seconds=0.05, arm_signals=False,
)
findings["cell_1_status"] = rec1["status"]
findings["cell_1_tours"] = rec1["tours"]

# --- what does the signal payload hold NOW, after the cell COMPLETED? ------
import signal as _sig  # noqa: E402

payload_bytes = v2._H_PAYLOAD.get(_sig.SIGTERM)
findings["payload_present_after_completed_cell"] = payload_bytes is not None
if payload_bytes is not None:
    p = json.loads(payload_bytes.decode("utf-8"))
    findings["payload_after_completed_cell"] = {
        "status": p.get("status"),
        "role": p.get("role"),
        "mpfr_bits": p.get("mpfr_bits"),
        "failed_infrastructure": p.get("failed_infrastructure"),
        "tours": p.get("tours"),
        "tour_in_flight_index": p.get("tour_in_flight_index"),
        "elapsed_seconds_at_refresh": p.get("elapsed_seconds_at_refresh"),
        "tours_table_rows": len(p.get("tours_table", [])),
    }
findings["cell_1_true_elapsed_seconds"] = rec1["elapsed_seconds"]

# --- cell 2 begins. What does the payload hold BEFORE cell 2's first
#     refresh, i.e. during the D1 stub write of cell 2? ---------------------
# Reproduce the ordering of run_cell: the STARTED stub for cell 2 is written
# (journal.write(started)) BEFORE _H_PAYLOAD is refreshed for cell 2.
# We show the payload is still cell 1's at that point by reading it again
# immediately before invoking cell 2.
pre_cell2 = json.loads(v2._H_PAYLOAD[_sig.SIGTERM].decode("utf-8"))
findings["payload_identity_at_start_of_cell_2"] = {
    "role": pre_cell2.get("role"),
    "status": pre_cell2.get("status"),
}

rec2 = v2.run_cell(
    d=64, beta=20, mpfr_bits=53, role="probe_cell_2",
    journal=journal, tee=tee, strategies=v2.DEFAULT_STRATEGIES,
    heartbeat_seconds=0.05, arm_signals=False,
)
findings["cell_2_status"] = rec2["status"]

# --- is there any code path that resets or disarms? ------------------------
src = open(os.path.join(TASKDIR, "rt_ctrl_1_matched_pair_v2.py")).read()
findings["source_contains_payload_reset"] = ("_H_PAYLOAD = {}" in src.split("\n", 250)[-1])
findings["source_contains_SIG_DFL_restore"] = "SIG_DFL" in src
findings["source_H_ARMED_ever_set_false"] = "_H_ARMED = False" in src.split("_H_ARMED = True")[-1]

# --- the prologue question: is anything journalled between the STARTED stub
#     and the first tour_start? ------------------------------------------
kinds = []
with open(journal.path) as fh:
    for line in fh:
        line = line.strip()
        if line:
            kinds.append(json.loads(line).get("record_kind"))
findings["journal_record_kinds_in_order_first_6"] = kinds[:6]
findings["journal_has_any_prologue_record_kind"] = any(
    k not in ("cell_started_stub", "tour_start", "tour_progress", "cell_final",
              "run_header")
    for k in kinds
)
findings["prologue_timings_only_in_cell_final"] = {
    "outer_lll_reduction_elapsed_seconds_in_final": (
        "outer_lll_reduction_elapsed_seconds" in rec1),
    "pre_loop_lll_elapsed_seconds_in_final": (
        "pre_loop_lll_elapsed_seconds" in rec1),
    "outer_lll_in_signal_payload": (
        "outer_lll_reduction_elapsed_seconds" in pre_cell2),
    "pre_loop_lll_in_signal_payload": (
        "pre_loop_lll_elapsed_seconds" in pre_cell2),
}

# --- per-tour row: which RSS quantity does it carry? -----------------------
row = rec1["tours_table"][0]
findings["tour_row_keys_rss_related"] = sorted(
    k for k in row if "rss" in k.lower() or "maxrss" in k.lower())
findings["tour_row_has_ru_maxrss"] = any("maxrss" in k for k in row)
findings["sampler_shortfall"] = {
    "observed": rec1["sampler_samples_observed"],
    "expected_if_never_starved": rec1["sampler_samples_expected_if_never_starved"],
}

print(json.dumps(findings, indent=2, sort_keys=True))
with open(os.path.join(OUT, "probe_payload_lifetime_output.json"), "w") as fh:
    json.dump(findings, fh, indent=2, sort_keys=True)
