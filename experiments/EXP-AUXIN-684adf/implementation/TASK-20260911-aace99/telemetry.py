"""Small explicit telemetry records for producer and reference paths."""
from __future__ import annotations
import time
def start(): return time.perf_counter_ns()
def finish(begin, counters): return {"elapsed_ns":time.perf_counter_ns()-begin,"counters":dict(counters),"resource_basis":"process-local sampled implementation telemetry"}
