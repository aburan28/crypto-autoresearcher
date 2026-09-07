#!/usr/bin/env python3
"""Non-measuring implementation adapter for EXP-ECDLP-1b1b99.

This file deliberately contains no fixture discovery, curve enumeration, timing,
or experimental-output persistence.  It records the exact interfaces a future,
separately locked runner must supply, and makes the charged [3 lambda] map
composition explicit so it cannot accidentally become a lambda computation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

TASK_ID = "TASK-20260906-2f2a56"
EXPERIMENT_ID = "EXP-ECDLP-1b1b99"
SPEC_SHA256 = "b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff"
APPROVAL_ID = "DEC-20260906-f73475"
QUERY_LADDER = (1, 16, 256, 4096)
SCALAR_ARMS = ("binary_double_and_add", "wnaf_w2", "wnaf_w3", "wnaf_w4", "wnaf_w5", "pinned_library")
COST_TERMS = (
    "Cshared", "Cdiscovery_all_candidates", "Cpointcount_factor", "Ckernel_search",
    "Cmaps", "Clevel_cert", "Ceigenvalue_sign", "Cnormalization",
    "Cpsi", "Ci", "Cphi", "Cverify", "Calgorithm_selection", "Cscalar_setup", "Cmul",
)
RUN_ARTIFACT_NAMES = ("manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv", "certificates.json", "stdout.log", "stderr.log", "report.md")


class LaunchRefused(RuntimeError):
    """Raised before a future run when its real control-plane lock is absent or invalid."""


class CancellationRequested(RuntimeError):
    """Future runner boundary: cancel only before starting a new frozen stage."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stream_digest(*, purpose: str, parameters: Sequence[int], seed: int, counter: int) -> int:
    """Frozen SHA-256 stream: JSON.stringify([id,purpose,[p,A,B,r,k,u,arm],seed,counter])."""
    if len(parameters) != 7:
        raise ValueError("parameters must be [p,A,B,r,k,u,arm]")
    if purpose not in {"query", "control", "field_x", "target", "shuffle"}:
        raise ValueError("unrecognized frozen RNG purpose")
    if seed < 0 or counter < 0 or any(not isinstance(x, int) for x in parameters):
        raise ValueError("RNG tuple values, seed, and counter must be nonnegative/integer as applicable")
    return int.from_bytes(hashlib.sha256(canonical_json([EXPERIMENT_ID, purpose, list(parameters), seed, counter])).digest(), "big")


def rejection_draw(*, purpose: str, parameters: Sequence[int], seed: int, counter: int, n: int) -> tuple[int, int]:
    """Return a uniform value in [0,n) and the next global counter; n=1 consumes one digest."""
    if n < 1:
        raise ValueError("n must be positive")
    limit = (1 << 256) // n * n
    while True:
        value = stream_digest(purpose=purpose, parameters=parameters, seed=seed, counter=counter)
        counter += 1
        if value < limit:
            return value % n, counter


def fisher_yates(values: Iterable[Any], *, parameters: Sequence[int], seed: int, counter: int) -> tuple[list[Any], int]:
    """Frozen shuffle from canonical caller ordering; uses the actual u and arm tuple."""
    out = list(values)
    for i in range(len(out) - 1, 0, -1):
        j, counter = rejection_draw(purpose="shuffle", parameters=parameters, seed=seed, counter=counter, n=i + 1)
        out[i], out[j] = out[j], out[i]
    return out, counter


def choose_eigenvalue_sign(candidates: Sequence[int], *, r: int, g0: Any, i_map: Callable[[Any], Any], scalar_mul: Callable[[int, Any], Any]) -> int:
    """Select the unique root lambda with [lambda]G0=i(G0); both roots are charged later."""
    if len(candidates) != 2 or len({x % r for x in candidates}) != 2:
        raise ValueError("exactly two supplied square-root candidates are required")
    matches = [lam % r for lam in candidates if scalar_mul(lam % r, g0) == i_map(g0)]
    if len(matches) != 1:
        raise ValueError("eigenvalue sign is ambiguous or does not match i(G0)")
    return matches[0]


def charged_transport(point: Any, *, psi: Callable[[Any], Any], i_map: Callable[[Any], Any], phi: Callable[[Any], Any]) -> Any:
    """The frozen floor evaluation: phi(i(psi(R))) = [3 lambda]R, never [lambda]R."""
    return phi(i_map(psi(point)))


def verify_transport_identity(point: Any, *, m: int, scalar_mul: Callable[[int, Any], Any], psi: Callable[[Any], Any], i_map: Callable[[Any], Any], phi: Callable[[Any], Any]) -> bool:
    return charged_transport(point, psi=psi, i_map=i_map, phi=phi) == scalar_mul(m, point)


@dataclass(frozen=True)
class CostLedger:
    """All frozen primary cost terms remain present; no unique transport charge cancels."""
    values: dict[str, float]

    def __post_init__(self) -> None:
        unknown = set(self.values) - set(COST_TERMS)
        missing = set(COST_TERMS) - set(self.values)
        if unknown or missing:
            raise ValueError(f"cost ledger must contain exactly frozen terms; missing={sorted(missing)} unknown={sorted(unknown)}")
        if any(value < 0 for value in self.values.values()):
            raise ValueError("costs must be nonnegative")

    def transport_total(self, evaluations: int) -> float:
        fixed = sum(self.values[k] for k in COST_TERMS[:9])
        per_query = sum(self.values[k] for k in ("Cpsi", "Ci", "Cphi", "Cverify"))
        return fixed + evaluations * per_query

    def scalar_total(self, evaluations: int) -> float:
        fixed = self.values["Cshared"] + self.values["Calgorithm_selection"] + self.values["Cscalar_setup"]
        return fixed + evaluations * (self.values["Cmul"] + self.values["Cverify"])


def select_baseline(scores: dict[str, float], *, selection_seed: int, q: int) -> str:
    if selection_seed != 606101 or q != 256:
        raise ValueError("frozen scalar-arm selection is only seed 606101 at q=256")
    if set(scores) != set(SCALAR_ARMS):
        raise ValueError("all frozen scalar arms must be supplied for selection")
    return min(SCALAR_ARMS, key=lambda arm: (scores[arm], arm))


def protocol_coverage() -> dict[str, Any]:
    return {
        "map": "charged_transport calls psi, i_map, phi in order; output is compared with [m] where m=3*lambda mod r",
        "sign": "choose_eigenvalue_sign tests both supplied roots against i(G0) and rejects ambiguity",
        "controls": ["composition", "coordinate", "level_all_four_floors", "identity_transport", "label_permutation"],
        "rng": "stream_digest, rejection_draw, fisher_yates implement the frozen SHA256 JSON stream and rejection rule",
        "scalar_arms": list(SCALAR_ARMS),
        "cost_terms": list(COST_TERMS),
        "future_runner_requirements": ["certified level rule", "all four normalized Velu maps and exact duals", "real locked backend", "canonical run artifact directory"],
    }


def canonical_artifact_layout(run_id: str) -> tuple[str, ...]:
    """Return, but do not create, the frozen future run layout after a control-plane ID allocation."""
    if not run_id or "/" in run_id or "\\" in run_id or run_id in {".", ".."}:
        raise ValueError("run_id must be a nonempty control-plane allocated basename")
    prefix = f"runs/{run_id}"
    return tuple(f"{prefix}/{name}" for name in RUN_ARTIFACT_NAMES)


def check_cancellation(cancel_requested: bool, stage: str) -> None:
    """A future runner calls this before each frozen stage and persists partial artifacts itself."""
    if cancel_requested:
        raise CancellationRequested(f"future run cancelled before stage {stage}; preserve completed artifacts and mark run incomplete")


def require_launch_lock(path: Path) -> None:
    """Validate only a future control-plane lock; this adapter never starts a measurement."""
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise LaunchRefused(f"genuine future launch lock unavailable: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LaunchRefused(f"genuine future launch lock is not JSON: {exc}") from exc
    required = {"kind", "approved", "experiment_id", "approval_decision_id", "spec_sha256", "execution_plan_sha256", "driver_sha256", "runtime", "resource_limits", "signature"}
    missing = required - set(lock)
    if missing or lock.get("kind") != "genuine_runtime_code_execution_lock" or lock.get("approved") is not True:
        raise LaunchRefused(f"genuine future launch lock does not bind required fields: missing={sorted(missing)}")
    if lock["experiment_id"] != EXPERIMENT_ID or lock["approval_decision_id"] != APPROVAL_ID or lock["spec_sha256"] != SPEC_SHA256:
        raise LaunchRefused("genuine future launch lock binds a different frozen protocol")
    if not all(lock.get(field) for field in ("execution_plan_sha256", "driver_sha256", "runtime", "signature")):
        raise LaunchRefused("genuine future launch lock contains unresolved bindings")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run implementation adapter for EXP-ECDLP-1b1b99; performs no measurement.")
    parser.add_argument("--dry-run", action="store_true", help="print protocol coverage (default)")
    parser.add_argument("--launch-lock", type=Path, help="future genuine control-plane lock; validation only")
    args = parser.parse_args(argv)
    if args.launch_lock is not None:
        require_launch_lock(args.launch_lock)
        raise LaunchRefused("lock parsed, but no certified backend/fixture implementation is bundled; no experiment was launched")
    print(json.dumps({"status": "dry_run_not_launched", "task_id": TASK_ID, "experiment_id": EXPERIMENT_ID, "coverage": protocol_coverage()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
