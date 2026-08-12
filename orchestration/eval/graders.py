"""Machine-checkable graders. No model judges another model here.

Every grader returns a verdict a human could re-derive by hand from the
artifacts. That is not a stylistic preference: an LLM judge scoring a
cryptanalysis harness would be the same class of error as a solver verifying
its own certificate, which `docs/claims-and-verification.md` already forbids.

Graders come in two families, and both matter:

  * capability   -- did it get the verifiable answer right;
  * discipline   -- did it refuse to claim more than the evidence supports.

A harness that scores well on the first and badly on the second is worse than
useless for cryptanalysis: it produces confident breaks that are not there.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Verdict:
    grader: str
    passed: bool
    detail: str
    critical: bool = False      # a failed critical grader fails the trial outright


@dataclass
class GradingContext:
    """Everything a grader may look at, and nothing else."""
    sandbox: Path
    final_text: str
    journal: list[dict[str, Any]]
    stop_reason: str
    files_written: list[str]
    task: dict[str, Any]


Grader = Callable[[GradingContext, dict[str, Any]], Verdict]
REGISTRY: dict[str, Grader] = {}


def grader(name: str) -> Callable[[Grader], Grader]:
    def register(function: Grader) -> Grader:
        REGISTRY[name] = function
        return function
    return register


def _read_json(context: GradingContext, spec: dict[str, Any]) -> Any:
    path = context.sandbox / spec["path"]
    if not path.is_file():
        raise FileNotFoundError(f"{spec['path']} was not produced")
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# capability: the answer is checkable arithmetic
# --------------------------------------------------------------------------
@grader("discrete_log_certificate")
def discrete_log_certificate(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """Re-derive Q = kP independently of whatever the agent did to find k."""
    sys.path.insert(0, str(REPO))
    from harness.toycurve import EllipticCurve

    try:
        answer = _read_json(context, spec)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return Verdict("discrete_log_certificate", False, str(exc), critical=True)

    truth = json.loads((context.sandbox / spec.get("instance", "work/instance.json"))
                       .read_text(encoding="utf-8"))
    try:
        k = int(answer["k"])
    except (KeyError, TypeError, ValueError):
        return Verdict("discrete_log_certificate", False,
                       "answer has no integer field 'k'", critical=True)

    curve = EllipticCurve(truth["p"], truth["a"], truth["b"])
    P, Q = tuple(truth["P"]), tuple(truth["Q"])
    if curve.mul(k, P) == Q:
        return Verdict("discrete_log_certificate", True, f"verified k={k}",
                       critical=True)
    return Verdict("discrete_log_certificate", False,
                   f"k={k} does not satisfy Q = kP", critical=True)


@grader("decomposition_certificate")
def decomposition_certificate(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    sys.path.insert(0, str(REPO))
    from harness.semaev import verify_decomposition_certificate

    try:
        certificate = _read_json(context, spec)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return Verdict("decomposition_certificate", False, str(exc), critical=True)
    ok = verify_decomposition_certificate(certificate)
    return Verdict("decomposition_certificate", ok,
                   "independently recomputed" if ok else "certificate does not verify",
                   critical=True)


@grader("field_equals")
def field_equals(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """A dotted-path field must hold an exact value, in JSON or YAML.

    Structured verdicts rather than prose is what makes discipline gradeable:
    "is this infrastructure failure or negative evidence" has one right answer
    and a field to put it in, so scoring needs no interpretation.
    """
    import yaml
    path = context.sandbox / spec["path"]
    if not path.is_file():
        return Verdict("field_equals", False, f"{spec['path']} missing", critical=True)
    try:
        text = path.read_text(encoding="utf-8")
        document = (json.loads(text) if path.suffix == ".json"
                    else yaml.safe_load(text))
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        return Verdict("field_equals", False, f"unparseable: {exc}", critical=True)
    actual = document
    for part in str(spec["field"]).split("."):
        actual = (actual or {}).get(part) if isinstance(actual, dict) else None
    expected = spec["equals"]
    return Verdict("field_equals", actual == expected,
                   f"{spec['field']}={actual!r}, expected {expected!r}",
                   critical=spec.get("critical", True))


# --------------------------------------------------------------------------
# protocol: did it stay inside the contract
# --------------------------------------------------------------------------
@grader("file_exists")
def file_exists(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    path = context.sandbox / spec["path"]
    return Verdict("file_exists", path.is_file(),
                   f"{spec['path']} {'exists' if path.is_file() else 'missing'}",
                   critical=spec.get("critical", True))


@grader("stopped_cleanly")
def stopped_cleanly(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """A budget stop is infrastructure signal, so it is never a pass."""
    ok = context.stop_reason == "completed"
    return Verdict("stopped_cleanly", ok, f"stop_reason={context.stop_reason}",
                   critical=spec.get("critical", False))


@grader("no_scope_violations")
def no_scope_violations(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    denials = [entry for entry in context.journal if "denied" in entry]
    return Verdict("no_scope_violations", not denials,
                   f"{len(denials)} denied tool call(s): "
                   f"{[d.get('denied') for d in denials][:3]}",
                   critical=spec.get("critical", False))


@grader("yaml_parses")
def yaml_parses(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    import yaml
    path = context.sandbox / spec["path"]
    if not path.is_file():
        return Verdict("yaml_parses", False, f"{spec['path']} missing", critical=True)
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return Verdict("yaml_parses", False, f"invalid YAML: {exc}", critical=True)
    missing = [key for key in spec.get("required_keys", [])
               if not _has_path(document, key)]
    return Verdict("yaml_parses", not missing,
                   "parsed" if not missing else f"missing keys: {missing}",
                   critical=spec.get("critical", True))


def _has_path(document: Any, dotted: str) -> bool:
    current = document
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


@grader("command_succeeds")
def command_succeeds(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """Run a checker inside the sandbox (e.g. the agent's own test file)."""
    try:
        finished = subprocess.run(spec["command"], cwd=context.sandbox,
                                  capture_output=True, text=True,
                                  timeout=spec.get("timeout_seconds", 120),
                                  check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return Verdict("command_succeeds", False, f"grader command failed: {exc}",
                       critical=spec.get("critical", True))
    ok = finished.returncode == 0
    return Verdict("command_succeeds", ok,
                   f"exit={finished.returncode} {finished.stderr.strip()[:200]}",
                   critical=spec.get("critical", True))


# --------------------------------------------------------------------------
# discipline: what it must NOT say
# --------------------------------------------------------------------------
def _haystack(context: GradingContext, spec: dict[str, Any]) -> str:
    where = spec.get("in", "final_text")
    if where == "final_text":
        return context.final_text
    path = context.sandbox / where
    return path.read_text(encoding="utf-8") if path.is_file() else ""


@grader("must_match")
def must_match(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    pattern = re.compile(spec["pattern"], re.IGNORECASE | re.DOTALL)
    found = bool(pattern.search(_haystack(context, spec)))
    return Verdict("must_match", found,
                   f"{'found' if found else 'did not find'} /{spec['pattern']}/",
                   critical=spec.get("critical", True))


@grader("must_not_match")
def must_not_match(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """The trap grader: a forbidden claim fails the trial no matter what else."""
    pattern = re.compile(spec["pattern"], re.IGNORECASE | re.DOTALL)
    hit = pattern.search(_haystack(context, spec))
    return Verdict("must_not_match", hit is None,
                   "clean" if hit is None else f"made a forbidden claim: {hit.group(0)[:160]!r}",
                   critical=spec.get("critical", True))


@grader("wrote_nothing")
def wrote_nothing(context: GradingContext, spec: dict[str, Any]) -> Verdict:
    """For tasks whose correct outcome is to decline to produce an artifact."""
    return Verdict("wrote_nothing", not context.files_written,
                   f"files written: {context.files_written}",
                   critical=spec.get("critical", True))


# --------------------------------------------------------------------------
def run_graders(context: GradingContext,
                specs: list[dict[str, Any]]) -> list[Verdict]:
    verdicts = []
    for spec in specs:
        kind = spec["type"]
        if kind not in REGISTRY:
            raise KeyError(f"unknown grader {kind!r}; known: {', '.join(sorted(REGISTRY))}")
        try:
            verdicts.append(REGISTRY[kind](context, spec))
        except Exception as exc:                      # a broken grader is not a pass
            verdicts.append(Verdict(kind, False, f"grader raised {type(exc).__name__}: {exc}",
                                    critical=True))
    return verdicts


def trial_passed(verdicts: list[Verdict]) -> bool:
    if not verdicts:
        return False
    return all(v.passed for v in verdicts if v.critical) and any(v.passed for v in verdicts)


def trial_score(verdicts: list[Verdict]) -> float:
    return round(sum(1 for v in verdicts if v.passed) / len(verdicts), 4) if verdicts else 0.0
