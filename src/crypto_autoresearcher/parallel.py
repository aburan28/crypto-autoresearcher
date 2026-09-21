"""Deterministic multi-process fan-out for the Python experiment lanes.

The program's evidence rules make one demand of any parallelism: a result may
not depend on how many cores computed it. A pool that returns whatever finished
first, or that lets workers share an RNG, converts a reproducible measurement
into an unreproducible one and every record downstream of it inherits the
defect. So the contract here is narrower than a general executor:

    sharded_map(fn, items, workers=N) == [fn(i, x) for i, x in enumerate(items)]

for every N, including N = 1. Three properties buy that:

1.  **Index-carried work.** ``fn`` receives ``(index, item)`` and must be a pure
    function of them. Seeds are derived from the index, never from a counter
    that advances as tasks are dispatched, so shard boundaries cannot move a
    seed. A closure over a mutable default, a module-level RNG, or a wall-clock
    read breaks this and no amount of pool discipline can repair it.
2.  **Order-independent assembly.** Results are placed by index, never appended
    on completion. Scheduling jitter is therefore unobservable in the output.
3.  **A fork-free default.** ``workers=1`` runs inline in the calling process.
    Under the locked runner that path creates no descendant, so a run that does
    not declare workers behaves exactly as it did before this module existed.

Failures propagate. A worker that dies takes the whole call with it rather than
yielding a short result list — a silently truncated sweep is precisely the kind
of missing data AGENTS.md rule 5 forbids reporting as a measurement.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")

# Mirrors budget.maximum_workers when a specification omits it.
DEFAULT_MAXIMUM_WORKERS = 1


def resolve_workers(declared: int | None, *, available: int | None = None) -> int:
    """Clamp a declared worker budget to what the machine actually offers.

    Over-subscription is not a neutral mistake here: the locked runner charges a
    run for the CPU seconds of its whole process group, so spawning more workers
    than cores inflates the run's own accounting against
    ``budget.total_cpu_hours`` while making it slower.
    """
    if declared is None:
        return DEFAULT_MAXIMUM_WORKERS
    if isinstance(declared, bool) or not isinstance(declared, int):
        raise TypeError("declared worker budget must be an integer")
    if declared < 1:
        raise ValueError("declared worker budget must be at least 1")
    usable = available if available is not None else (os.cpu_count() or 1)
    return max(1, min(declared, usable))


def sharded_map(
    fn: Callable[[int, T], R],
    items: Iterable[T],
    *,
    workers: int = DEFAULT_MAXIMUM_WORKERS,
    chunk_size: int | None = None,
) -> list[R]:
    """Map ``fn`` over ``items``, returning results in input order.

    ``fn`` is called as ``fn(index, item)`` and must be picklable and pure in
    its arguments. The return value is identical for every ``workers`` value.
    """
    work: Sequence[T] = list(items)
    if not work:
        return []

    effective_workers = resolve_workers(workers)
    if effective_workers == 1 or len(work) == 1:
        # No fork: the default path, and the reference implementation that the
        # parallel path is required to agree with.
        return [fn(index, item) for index, item in enumerate(work)]

    if chunk_size is None:
        # Enough chunks to keep every worker fed even when item costs are
        # uneven, without paying pickling overhead per item.
        chunk_size = max(1, len(work) // (effective_workers * 4))

    results: list[Any] = [_MISSING] * len(work)
    with ProcessPoolExecutor(max_workers=effective_workers) as pool:
        indexed = list(enumerate(work))
        for index, value in pool.map(
            _apply, ((fn, i, item) for i, item in indexed), chunksize=chunk_size
        ):
            results[index] = value

    missing = [i for i, value in enumerate(results) if value is _MISSING]
    if missing:
        raise RuntimeError(
            f"sharded_map lost {len(missing)} of {len(work)} results "
            f"(first missing index {missing[0]}); refusing to return a partial sweep"
        )
    return results


def verify_determinism(
    fn: Callable[[int, T], R],
    items: Iterable[T],
    *,
    workers: int,
) -> list[R]:
    """Run serially and in parallel, and return the result only if they agree.

    The control to run once per lane before trusting a parallel sweep. It costs
    one extra serial pass and is the only thing that actually demonstrates
    ``fn`` is pure in ``(index, item)`` rather than merely believed to be.
    """
    work = list(items)
    serial = sharded_map(fn, work, workers=1)
    parallel = sharded_map(fn, work, workers=workers)
    if serial != parallel:
        divergent = next(
            (i for i, (a, b) in enumerate(zip(serial, parallel)) if a != b),
            min(len(serial), len(parallel)),
        )
        raise RuntimeError(
            "parallel result differs from serial at index "
            f"{divergent}: fn is not a pure function of (index, item), so this "
            "sweep is not reproducible and must not be recorded"
        )
    return serial


class _Missing:
    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "<missing>"


_MISSING = _Missing()


def _apply(payload: tuple[Callable[[int, Any], Any], int, Any]) -> tuple[int, Any]:
    fn, index, item = payload
    return index, fn(index, item)
