"""Worker-budget declaration (runner) and deterministic fan-out (parallel).

The two halves of the same guarantee: a run may use more than one core only by
declaring how many, and a parallel result must equal the serial one.
"""

from __future__ import annotations

import os
import unittest

from crypto_autoresearcher import parallel, runner as runner_module
from crypto_autoresearcher.records import RecordValidationError


# Module-level so the pool can pickle them by reference under spawn and fork.
def _square(index: int, item: int) -> int:
    return index * 1000 + item * item


def _seeded(index: int, item: int) -> int:
    """Seed derived from the index, which is what makes shards immaterial."""
    import random

    return random.Random(index).randrange(10**9) + item


def _impure(index: int, item: int) -> int:
    """Depends on the process it lands in, so parallel != serial."""
    return item + (os.getpid() % 2)


def _explodes(index: int, item: int) -> int:
    if item == 3:
        raise ValueError("worker failure")
    return item


class WorkerSlotTests(unittest.TestCase):
    def _experiment(self, **budget: object) -> dict:
        base = {
            "wall_clock_seconds_per_run": 600,
            "total_cpu_hours": 1,
            "maximum_memory_gb": 8,
            "maximum_runs": 1,
        }
        base.update(budget)
        return {"budget": base}

    def test_absent_field_is_one_worker_and_zero_slots(self) -> None:
        self.assertEqual(runner_module._worker_slots(self._experiment()), 0)

    def test_declared_workers_become_slots(self) -> None:
        self.assertEqual(
            runner_module._worker_slots(self._experiment(maximum_workers=8)), 7
        )

    def test_zero_and_negative_and_bool_are_rejected(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.subTest(value=value):
                with self.assertRaises(RecordValidationError):
                    runner_module._worker_slots(
                        self._experiment(maximum_workers=value)
                    )

    def test_policy_string_is_unchanged_for_the_default(self) -> None:
        # Every approval lock written before maximum_workers existed must still
        # match, so slot 0 has to reproduce the historical string exactly.
        self.assertEqual(
            runner_module._descendant_policy(0),
            "forbidden-via-rlimit-nproc-zero",
        )
        self.assertEqual(
            runner_module._descendant_policy(0),
            runner_module.LOCKED_DESCENDANT_POLICY,
        )

    def test_policy_string_records_the_bound(self) -> None:
        self.assertEqual(
            runner_module._descendant_policy(7), "bounded-via-rlimit-nproc-7"
        )
        self.assertNotEqual(
            runner_module._descendant_policy(7),
            runner_module.LOCKED_DESCENDANT_POLICY,
        )

    def test_unlocked_runs_leave_nproc_untouched(self) -> None:
        # Unplanned (unlocked) runs never touched RLIMIT_NPROC and still must not.
        self.assertIsNone(runner_module._nproc_limit(None))
        self.assertTrue(callable(runner_module._resource_limiter(1 << 30, 60.0, None)))

    def test_zero_slots_still_forbid_fork_outright(self) -> None:
        self.assertEqual(runner_module._nproc_limit(0), 0)

    def test_bounded_slots_clear_the_current_process_count(self) -> None:
        # A limit at or below the uid's live count makes fork() fail for the
        # pool as surely as zero does, so the bound must sit above it.
        observed = runner_module._uid_process_count()
        self.assertGreater(observed, 0)
        limit = runner_module._nproc_limit(4)
        self.assertIsNotNone(limit)
        assert limit is not None
        self.assertGreater(limit, observed)
        self.assertGreaterEqual(limit - observed, 4)


class ResolveWorkersTests(unittest.TestCase):
    def test_none_is_one(self) -> None:
        self.assertEqual(parallel.resolve_workers(None), 1)

    def test_clamped_to_available_cores(self) -> None:
        self.assertEqual(parallel.resolve_workers(64, available=4), 4)

    def test_under_subscription_is_honoured(self) -> None:
        self.assertEqual(parallel.resolve_workers(2, available=16), 2)

    def test_invalid_declarations_raise(self) -> None:
        with self.assertRaises(ValueError):
            parallel.resolve_workers(0)
        with self.assertRaises(TypeError):
            parallel.resolve_workers(True)


class ShardedMapTests(unittest.TestCase):
    def test_empty_input(self) -> None:
        self.assertEqual(parallel.sharded_map(_square, [], workers=4), [])

    def test_serial_matches_reference(self) -> None:
        items = list(range(20))
        self.assertEqual(
            parallel.sharded_map(_square, items, workers=1),
            [_square(i, x) for i, x in enumerate(items)],
        )

    def test_result_is_identical_across_worker_counts(self) -> None:
        items = list(range(50))
        reference = parallel.sharded_map(_square, items, workers=1)
        for workers in (2, 3, 4):
            with self.subTest(workers=workers):
                self.assertEqual(
                    parallel.sharded_map(_square, items, workers=workers), reference
                )

    def test_index_derived_seeds_survive_sharding(self) -> None:
        items = list(range(40))
        reference = parallel.sharded_map(_seeded, items, workers=1)
        self.assertEqual(
            parallel.sharded_map(_seeded, items, workers=4), reference
        )

    def test_order_follows_input_not_completion(self) -> None:
        items = list(range(30))
        result = parallel.sharded_map(_square, items, workers=4)
        self.assertEqual(result, sorted(result))

    def test_worker_failure_propagates(self) -> None:
        # A short result list would be a silently truncated sweep.
        with self.assertRaises(ValueError):
            parallel.sharded_map(_explodes, list(range(10)), workers=2)


class VerifyDeterminismTests(unittest.TestCase):
    def test_pure_function_passes_and_returns_the_result(self) -> None:
        items = list(range(30))
        self.assertEqual(
            parallel.verify_determinism(_square, items, workers=4),
            [_square(i, x) for i, x in enumerate(items)],
        )

    def test_impure_function_is_caught(self) -> None:
        # Only meaningful when the pool really lands work in other processes.
        if (os.cpu_count() or 1) < 2:
            self.skipTest("needs more than one core")
        with self.assertRaises(RuntimeError):
            parallel.verify_determinism(_impure, list(range(200)), workers=4)


if __name__ == "__main__":
    unittest.main()
