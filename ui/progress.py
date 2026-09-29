"""Allowlisted research telemetry snapshots. Never run a worker from the UI."""
from __future__ import annotations

import argparse
import json
import math
import re
import time
from datetime import datetime, timezone
from pathlib import Path

NUMBERS = (
    "actions_last_24h", "design_actions_last_24h", "run_actions_last_24h",
    "runner_output_validated_trial_delta_24h", "runner_coverage_unknown_24h",
    "next_action_latency_seconds_median_24h", "measured_cost_usd_last_24h",
)
COVERAGE = ("runner_coverage_24h", "cost_coverage_last_24h")
STALE_SECONDS = 3600


def _instant(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.timestamp() if dt.tzinfo is not None else None
    except ValueError:
        return None


def _iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).isoformat(timespec="seconds")


def unavailable(reason):
    return {"schema": 1, "available": False, "reason": reason,
            "generated_at": None, "source_updated_at": None, "stale": True,
            "metrics": {key: None for key in (*NUMBERS, *COVERAGE,
                         "verified_discoveries", "independent_relations")}}


def sanitize(snapshot, *, now=None):
    now = time.time() if now is None else now
    if not isinstance(snapshot, dict) or snapshot.get("schema") != 1:
        return unavailable("Progress snapshot has an unsupported format.")
    if snapshot.get("available") is not True:
        return unavailable("No observed research telemetry is available.")
    generated = _instant(snapshot.get("generated_at"))
    updated = _instant(snapshot.get("source_updated_at"))
    if (generated is None or updated is None or updated > generated + 5
            or generated > now + 300):
        return unavailable("Progress snapshot has invalid observation timestamps.")
    raw = snapshot.get("metrics")
    if not isinstance(raw, dict):
        return unavailable("Progress snapshot has no metric object.")
    metrics = {}
    for key in NUMBERS:
        value = raw.get(key)
        valid = type(value) in (int, float) and math.isfinite(value)
        if key != "runner_output_validated_trial_delta_24h":
            valid = valid and value >= 0
        if key not in ("next_action_latency_seconds_median_24h", "measured_cost_usd_last_24h"):
            valid = valid and type(value) is int
        metrics[key] = value if valid else None
    for key in COVERAGE:
        value = raw.get(key)
        match = re.fullmatch(r"(\d{1,12})/(\d{1,12})", value) if isinstance(value, str) else None
        metrics[key] = value if match and int(match[1]) <= int(match[2]) else None
    for value_key, coverage_key in (
        ("measured_cost_usd_last_24h", "cost_coverage_last_24h"),
        ("runner_output_validated_trial_delta_24h", "runner_coverage_24h"),
    ):
        coverage = metrics[coverage_key]
        if coverage is None or int(coverage.split("/")[0]) == 0:
            metrics[value_key] = None
    # No receipt joiner exists yet. Never promote numbers injected by a caller.
    metrics.update(verified_discoveries=None, independent_relations=None)
    return {"schema": 1, "available": True, "generated_at": _iso(generated),
            "source_updated_at": _iso(updated),
            "stale": now - min(generated, updated) > STALE_SECONDS,
            "window_seconds": 86400, "metrics": metrics}


def payload(path: Path, *, now=None):
    try:
        if path.stat().st_size > 65536:
            return unavailable("Progress snapshot exceeds the size limit.")
        return sanitize(json.loads(path.read_text(encoding="utf-8")), now=now)
    except (OSError, ValueError, UnicodeError, OverflowError, RecursionError):
        return unavailable("No readable progress snapshot has been supplied.")


def export(state_dir: Path, *, now=None):
    """Read the existing report; emit only public aggregate fields to stdout.

    This is an explicit operator command, never called by build/server. The
    producer must publish the snapshot separately. No paths, prompts, model
    replies, credentials or worker errors leave this boundary.
    """
    now = time.time() if now is None else now
    latest = None
    try:
        with (state_dir / "events.jsonl").open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(row, dict):
                    continue
                stamp = row.get("time")
                if (row.get("event") in {"started", "finished", "no_progress", "interrupted_action"}
                        and type(stamp) in (int, float) and math.isfinite(stamp)
                        and 0 <= stamp <= now):
                    latest = max(latest or 0, stamp)
        if latest is None:
            return unavailable("No observed research telemetry is available.")
        from orchestration.campaign.autopilot import report
        metrics = report(state_dir, now=now)
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        return unavailable("Research telemetry could not be summarized.")
    return sanitize({"schema": 1, "available": True, "generated_at": _iso(now),
                     "source_updated_at": _iso(latest), "metrics": metrics}, now=now)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(export(args.state_dir), allow_nan=False))


if __name__ == "__main__":
    main()
