"""Aggregation and comparison, with the uncertainty kept in view.

Model output is stochastic, so a pass rate from a handful of trials is a
sample, not a measurement. This module never reports one without an interval,
and never declares one backend better than another when the intervals overlap
-- the same discipline `AGENTS.md` already demands of experimental claims,
applied to claims about the harness itself.

"4/5 versus 3/5" is not a result. It is two overlapping intervals and a
suggestion to run more trials, and `compare()` will say so.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

Z95 = 1.959963984540054


@dataclass
class Interval:
    low: float
    high: float

    def overlaps(self, other: "Interval") -> bool:
        return self.low <= other.high and other.low <= self.high

    def __str__(self) -> str:
        return f"[{self.low:.2f}, {self.high:.2f}]"


def wilson(successes: int, trials: int, z: float = Z95) -> Interval:
    """Wilson score interval: behaves sanely at 0/n and n/n, unlike normal-approx."""
    if trials <= 0:
        return Interval(0.0, 1.0)
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    half = (z / denominator) * math.sqrt(
        p * (1 - p) / trials + z * z / (4 * trials * trials))
    return Interval(round(max(0.0, centre - half), 4),
                    round(min(1.0, centre + half), 4))


def required_trials(baseline: float, target: float, z: float = Z95) -> int:
    """Roughly how many trials per arm before an effect this size is detectable."""
    if not 0 <= baseline <= 1 or not 0 <= target <= 1 or baseline == target:
        return 0
    pooled = (baseline + target) / 2
    delta = abs(target - baseline)
    # Two-proportion normal approximation, 80% power.
    n = 2 * pooled * (1 - pooled) * (z + 0.8416) ** 2 / (delta ** 2)
    return max(2, math.ceil(n))


@dataclass
class TaskSummary:
    task_id: str
    kind: str
    trials: int
    passes: int
    pass_rate: float
    interval: Interval
    mean_score: float
    mean_steps: float
    mean_wall_seconds: float
    mean_output_tokens: float
    total_tokens: int
    budget_stops: int
    scope_denials: int
    failure_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["interval"] = [self.interval.low, self.interval.high]
        return data


def summarise_task(task_id: str, kind: str,
                   trials: Sequence[Any]) -> TaskSummary:
    n = len(trials)
    passes = sum(1 for t in trials if t.passed)

    def mean(values: Sequence[float]) -> float:
        return round(sum(values) / len(values), 3) if values else 0.0

    reasons: list[str] = []
    for trial in trials:
        for verdict in trial.verdicts:
            if not verdict.passed:
                reasons.append(f"{verdict.grader}: {verdict.detail}")
    return TaskSummary(
        task_id=task_id, kind=kind, trials=n, passes=passes,
        pass_rate=round(passes / n, 4) if n else 0.0,
        interval=wilson(passes, n),
        mean_score=mean([t.score for t in trials]),
        mean_steps=mean([t.steps for t in trials]),
        mean_wall_seconds=mean([t.wall_seconds for t in trials]),
        mean_output_tokens=mean([t.usage.get("output_tokens", 0) for t in trials]),
        total_tokens=sum(t.usage.get("input_tokens", 0)
                         + t.usage.get("output_tokens", 0) for t in trials),
        budget_stops=sum(1 for t in trials if t.stop_reason != "completed"),
        scope_denials=sum(t.denials for t in trials),
        failure_reasons=_top(reasons))


def _top(reasons: list[str], limit: int = 5) -> list[str]:
    counts: dict[str, int] = {}
    for reason in reasons:
        counts[reason] = counts.get(reason, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: -kv[1])[:limit]
    return [f"x{count}  {reason}" for reason, count in ordered]


@dataclass
class RunSummary:
    suite: str
    backend: str
    tasks: list[TaskSummary]

    def by_kind(self, kind: str) -> list[TaskSummary]:
        return [t for t in self.tasks if t.kind == kind]

    def rate(self, kind: str | None = None) -> tuple[int, int, Interval]:
        selected = self.tasks if kind is None else self.by_kind(kind)
        passes = sum(t.passes for t in selected)
        trials = sum(t.trials for t in selected)
        return passes, trials, wilson(passes, trials)

    def to_dict(self) -> dict[str, Any]:
        overall = self.rate()
        return {
            "suite": self.suite,
            "backend": self.backend,
            "overall": {"passes": overall[0], "trials": overall[1],
                        "interval": [overall[2].low, overall[2].high]},
            "by_kind": {kind: {"passes": p, "trials": n,
                               "interval": [ci.low, ci.high]}
                        for kind in ("capability", "protocol", "discipline")
                        for p, n, ci in [self.rate(kind)] if n},
            "tasks": [t.to_dict() for t in self.tasks],
        }


def render(summary: RunSummary) -> str:
    lines = [f"suite: {summary.suite}    backend: {summary.backend}", ""]
    header = f"{'task':<28}{'kind':<12}{'pass':>8}  {'95% CI':<16}{'steps':>7}{'tokens':>9}"
    lines += [header, "-" * len(header)]
    for task in summary.tasks:
        lines.append(
            f"{task.task_id:<28}{task.kind:<12}"
            f"{task.passes:>3}/{task.trials:<4}  {str(task.interval):<16}"
            f"{task.mean_steps:>7.1f}{task.total_tokens:>9}")
        for reason in task.failure_reasons:
            lines.append(f"    {reason}")
    lines.append("")
    for kind in ("capability", "protocol", "discipline"):
        passes, trials, interval = summary.rate(kind)
        if trials:
            lines.append(f"{kind:<12} {passes:>3}/{trials:<4} {interval}")
    passes, trials, interval = summary.rate()
    lines.append(f"{'OVERALL':<12} {passes:>3}/{trials:<4} {interval}")
    lines.append("")
    lines.append("Capability and discipline are reported separately on purpose: a "
                 "harness that solves\nproblems but overclaims is not a better "
                 "harness, it is a more dangerous one.")
    return "\n".join(lines)


def compare(left: RunSummary, right: RunSummary,
            kind: str | None = None) -> dict[str, Any]:
    """Compare two arms honestly, including refusing to call a winner."""
    left_passes, left_trials, left_ci = left.rate(kind)
    right_passes, right_trials, right_ci = right.rate(kind)
    left_rate = left_passes / left_trials if left_trials else 0.0
    right_rate = right_passes / right_trials if right_trials else 0.0

    separated = not left_ci.overlaps(right_ci)
    if separated:
        winner = left.backend if left_rate > right_rate else right.backend
        verdict = f"{winner} is ahead: intervals do not overlap"
    else:
        winner = None
        needed = required_trials(min(left_rate, right_rate), max(left_rate, right_rate))
        verdict = (f"no separation at {left_trials} vs {right_trials} trials; "
                   f"~{needed} trials per arm would be needed to detect an effect "
                   f"this size" if needed else
                   f"no separation at {left_trials} vs {right_trials} trials")
    return {
        "kind": kind or "overall",
        "left": {"backend": left.backend, "passes": left_passes,
                 "trials": left_trials, "rate": round(left_rate, 4),
                 "interval": [left_ci.low, left_ci.high]},
        "right": {"backend": right.backend, "passes": right_passes,
                  "trials": right_trials, "rate": round(right_rate, 4),
                  "interval": [right_ci.low, right_ci.high]},
        "separated": separated,
        "winner": winner,
        "verdict": verdict,
    }


IMPROVED = "improved"
REGRESSED = "regressed"
INDISTINGUISHABLE = "no change detectable"


def regression(baseline: dict[str, Any], current: RunSummary) -> dict[str, Any]:
    """Did a tuning change help, hurt, or land inside the noise?

    The third answer is the common one and the one worth protecting. With a
    handful of trials per task most changes are indistinguishable, and a
    tuning loop that reads noise as progress will happily walk downhill for
    weeks. `verdict` says so explicitly instead of reporting a delta and
    letting the reader infer significance that is not there.
    """
    per_task: list[dict[str, Any]] = []
    baseline_tasks = {t["task_id"]: t for t in baseline.get("tasks", [])}

    for task in current.tasks:
        before = baseline_tasks.get(task.task_id)
        if before is None:
            per_task.append({"task_id": task.task_id, "verdict": "new",
                             "detail": "not present in the baseline"})
            continue
        before_ci = Interval(*before["interval"])
        separated = not before_ci.overlaps(task.interval)
        if not separated:
            verdict = INDISTINGUISHABLE
        elif task.pass_rate > before["pass_rate"]:
            verdict = IMPROVED
        else:
            verdict = REGRESSED
        per_task.append({
            "task_id": task.task_id, "kind": task.kind, "verdict": verdict,
            "before": f"{before['passes']}/{before['trials']} {before_ci}",
            "after": f"{task.passes}/{task.trials} {task.interval}",
            "delta": round(task.pass_rate - before["pass_rate"], 4),
        })

    kinds = {}
    for kind in ("capability", "protocol", "discipline"):
        passes, trials, interval = current.rate(kind)
        if not trials:
            continue
        before_passes = sum(t["passes"] for t in baseline.get("tasks", [])
                            if t.get("kind") == kind)
        before_trials = sum(t["trials"] for t in baseline.get("tasks", [])
                            if t.get("kind") == kind)
        if not before_trials:
            continue
        before_ci = wilson(before_passes, before_trials)
        separated = not before_ci.overlaps(interval)
        rate_now, rate_then = passes / trials, before_passes / before_trials
        kinds[kind] = {
            "verdict": (INDISTINGUISHABLE if not separated else
                        IMPROVED if rate_now > rate_then else REGRESSED),
            "before": f"{before_passes}/{before_trials} {before_ci}",
            "after": f"{passes}/{trials} {interval}",
            "required_trials": required_trials(rate_then, rate_now),
        }

    regressed = [t for t in per_task if t["verdict"] == REGRESSED]
    # A discipline regression is the one that must never be traded away for a
    # capability gain, so it is called out on its own.
    discipline_regressed = [t for t in regressed if t.get("kind") == "discipline"]
    return {
        "tasks": per_task,
        "by_kind": kinds,
        "regressed": [t["task_id"] for t in regressed],
        "discipline_regressed": [t["task_id"] for t in discipline_regressed],
        "safe_to_keep": not discipline_regressed,
    }


def render_regression(result: dict[str, Any], *,
                      changed_inputs: list[str] | None = None) -> str:
    lines = []
    if changed_inputs is not None:
        lines.append("changed since baseline: " +
                     (", ".join(changed_inputs) if changed_inputs
                      else "nothing tracked — same inputs, so any difference is noise"))
        lines.append("")
    header = f"{'task':<28}{'before':<22}{'after':<22}verdict"
    lines += [header, "-" * len(header)]
    for task in result["tasks"]:
        lines.append(f"{task['task_id']:<28}{task.get('before', '-'):<22}"
                     f"{task.get('after', '-'):<22}{task['verdict']}")
    lines.append("")
    for kind, summary in result["by_kind"].items():
        note = ("" if summary["verdict"] != INDISTINGUISHABLE
                or not summary["required_trials"]
                else f"  (~{summary['required_trials']} trials/arm to detect)")
        lines.append(f"{kind:<12}{summary['before']:<22}{summary['after']:<22}"
                     f"{summary['verdict']}{note}")
    lines.append("")
    if result["discipline_regressed"]:
        lines.append("DO NOT KEEP: discipline regressed on "
                     f"{', '.join(result['discipline_regressed'])}. A capability "
                     "gain never pays for a discipline loss.")
    elif result["regressed"]:
        lines.append(f"regressions: {', '.join(result['regressed'])}")
    else:
        lines.append("no regressions detected")
    return "\n".join(lines)


def _arm(side: dict[str, Any]) -> str:
    return (f"{side['backend']} {side['passes']}/{side['trials']} "
            f"{Interval(*side['interval'])}")


def render_comparison(comparisons: list[dict[str, Any]]) -> str:
    lines = [f"{'dimension':<13}{'left':<32}{'right':<32}verdict", "-" * 78]
    for item in comparisons:
        lines.append(f"{item['kind']:<13}{_arm(item['left']):<32}"
                     f"{_arm(item['right']):<32}")
        lines.append(f"{'':<13}{item['verdict']}")
    return "\n".join(lines)
