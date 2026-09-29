#!/usr/bin/env python3
"""J2 -- clause-by-clause probes of v2's signal handler and payload mechanism.

NO LATTICE COMPUTE AT ALL.  These probes exercise the producer's OWN functions
(imported from the committed instrument, not re-implemented) with synthetic
inputs, to test clauses of the safety argument that a d=64 kill cannot reach.
"""
import json
import os
import sys
import time

INSTR_DIR = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
             "batches/BATCH-762807/tasks/TASK-20260826-602395")
sys.path.insert(0, INSTR_DIR)
import rt_ctrl_1_matched_pair_v2 as v2  # noqa: E402  the instrument under test

MODE = sys.argv[1]

if MODE == "handler_write_fails":
    # CLAUSE UNDER TEST: "the handler does exactly one os.write(fd, payload),
    # one os.fsync, one short os.write to fd 1, then os._exit(128+signum)".
    # What happens when the journal write FAILS (the ENOSPC / bad-fd case)?
    # The handler swallows the exception and STILL writes the fd-1 message.
    r, w = os.pipe()
    os.close(w)                       # writing to r-end of a closed pipe: EBADF
    v2._H_FD = 10001                  # a file descriptor that is not open
    v2._H_PAYLOAD = {15: b'{"status": "KILLED_PARTIAL"}\n'}
    sys.stderr.write("about to invoke the producer's handler with a dead fd\n")
    sys.stderr.flush()
    v2._signal_flush_and_die(15, None)   # never returns
    sys.stderr.write("UNREACHABLE\n")

elif MODE == "payload_missing_signum":
    # CLAUSE UNDER TEST: one pre-serialised payload PER SIGNAL. What if the
    # handler fires before any refresh has bound a payload for that signal?
    v2._H_FD = 1
    v2._H_PAYLOAD = {}                # the module-level default
    v2._signal_flush_and_die(15, None)

elif MODE == "refresh_cost":
    # CLAUSE UNDER TEST (bearing on the pre-tour refresh): the payload is
    # rebuilt and RE-SERIALISED, once PER SIGNAL, on every refresh, and it
    # embeds the whole uncapped tours_table.  Measure the serialisation cost as
    # a function of the table size, using a REAL row taken from a real v2 run.
    src = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
           "batches/BATCH-762807/reviews/TASK-20260826-9605ae/probes/"
           "j2/T10_late/p_results.jsonl")
    row = None
    for line in open(src, errors="replace"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("record_kind") == "tour_progress":
            row = {k: v for k, v in rec.items()
                   if k not in ("record_kind",)}
            break
    out = {"row_source": src, "row_keys": len(row), "measurements": []}
    for n in (1, 10, 100, 500, 1000, 2000):
        table = [dict(row) for _ in range(n)]
        rec = {"status": "KILLED_PARTIAL", "tours": n, "tours_table": table,
               "stdout_tail": ["x" * 80] * 24}
        t0 = time.perf_counter()
        reps = 5
        for _ in range(reps):
            for _signum in (2, 14, 15):        # THREE payloads per refresh
                (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8")
        dt = (time.perf_counter() - t0) / reps
        nbytes = len((json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
        out["measurements"].append(
            {"tours_table_rows": n,
             "seconds_per_refresh_all_three_payloads": dt,
             "payload_bytes_each": nbytes,
             "bytes_written_per_flush": nbytes})
    out["what_this_is"] = (
        "A MEASUREMENT of the producer's serialisation shape at larger table "
        "sizes, with NO lattice compute. It is not a projection of d=512 "
        "behaviour and does not stand in for one.")
    print(json.dumps(out, indent=2))

elif MODE == "os_write_return_ignored":
    # CLAUSE UNDER TEST: "O_APPEND plus a single write() syscall means the
    # record is appended whole". Demonstrate that BOTH Journal.write and the
    # handler DISCARD the os.write return value, so a short write would
    # silently truncate a line rather than be retried or reported.
    import inspect
    jw = inspect.getsource(v2.Journal.write)
    hw = inspect.getsource(v2._signal_flush_and_die)
    out = {
        "journal_write_source": jw,
        "handler_source": hw,
        "journal_write_uses_return_value_of_os_write":
            "= os.write" in jw or "n = os.write" in jw,
        "handler_uses_return_value_of_os_write":
            "= os.write" in hw,
        "finding": (
            "Both call os.write(...) as a bare statement. A short write -- "
            "possible in principle on ENOSPC or a very large payload -- would "
            "append a TRUNCATED JSON line and neither site would notice. The "
            "reader side (rebuild_results / read_jsonl) RETAINS unparseable "
            "lines verbatim rather than dropping them, so the failure would be "
            "visible rather than silent, but the writer does not retry."),
    }
    print(json.dumps(out, indent=2))
