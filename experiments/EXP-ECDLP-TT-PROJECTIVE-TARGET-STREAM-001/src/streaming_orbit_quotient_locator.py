#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
BASE_SOURCE = REPO_ROOT / "experiments" / "EXP-ECDLP-TT-SOURCE-ORBIT-QUOTIENT-001" / "src" / "orbit_quotient_locator.py"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load("streaming_target_orbit_base", BASE_SOURCE)


class ActiveMapping:
    """Mapping facade that exposes only the current target's cache."""

    def __init__(self, owner: "StreamingOrbitPredicates", attribute: str) -> None:
        self.owner = owner
        self.attribute = attribute

    def _mapping(self) -> dict[Any, Any]:
        return getattr(self.owner, self.attribute)

    def __contains__(self, key: object) -> bool:
        return key in self._mapping()

    def __getitem__(self, key: Any) -> Any:
        if self.attribute == "active_value_cache":
            self.owner.activate(int(key))
            return self._mapping()
        return self._mapping()[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._mapping()[key] = value

    def __iter__(self):
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())

    def clear(self) -> None:
        self._mapping().clear()


class StreamingOrbitPredicates(BASE.OrbitPredicates):
    """Keep source-state advice while discarding target-local values per target."""

    def __init__(self, advice: Any, classes: list[dict[str, Any]], targets: list[tuple[int, int]], p: int) -> None:
        super().__init__(advice, classes, targets, p)
        self.active_target = -1
        self.active_value_cache: dict[Any, int] = {}
        self.active_original_cache: dict[Any, tuple[int, int] | None] = {}
        self.cache = ActiveMapping(self, "active_value_cache")
        self.original_cache = ActiveMapping(self, "active_original_cache")

    def activate(self, target_index: int) -> None:
        if self.active_target == target_index:
            return
        self.active_target = target_index
        self.active_value_cache.clear()
        self.active_original_cache.clear()


BASE.OrbitPredicates = StreamingOrbitPredicates
OrbitPredicates = StreamingOrbitPredicates


def run(relation_inputs: list[Path], fixture_path: Path, families: list[str], budget_labels: list[str]) -> dict[str, Any]:
    result = BASE.run(relation_inputs, fixture_path, families, budget_labels)
    result["protocol"] = "EXP-ECDLP-TT-PROJECTIVE-TARGET-STREAM-001-orbit-v1"
    result["config"]["target_cache_mode"] = "streaming-one-target-at-a-time"
    result["summary"]["boundary"] = "Streaming target-local cache over shared projective source states; exact support, rank, and rho are required; no generic ECDLP claim."
    return result


for name in dir(BASE):
    if not name.startswith("_") and name not in {"OrbitPredicates", "run"}:
        globals()[name] = getattr(BASE, name)
