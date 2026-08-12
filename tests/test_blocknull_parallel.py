"""CTRL-POWER / CTRL-NULLOBJ replicates must not notice how many cores ran them.

These exercise the real `blocked_permutation_null_both` through the same
callables `s5_controls` uses. Equality here is `==` on float64, not
`assertAlmostEqual`: the module already carries a superseded run
(RUN-INSTR-85b102-poolB) whose p_lower landed on the resolution floor instead
of exactly 1.0 because a reduction changed by one ulp, so "close enough" is
precisely the standard that failed before.
"""

from __future__ import annotations

import unittest

import numpy as np

from harness.run_blocknull import (
    _Layout,
    _NullObjReplicate,
    _PowerReplicate,
    _map_replicates,
    blocked_permutation_null_both,
    derive_seed,
)

WORKERS = 4
REPLICATES = 12
B = 64
DELTAS = (0.0, 0.4, 1.6)


def _geometry(n_blocks: int = 4, per_class: int = 3, classes: int = 3):
    """Labels and blocks with classes nested inside blocks, as the rungs are."""
    labels, blocks = [], []
    for b in range(n_blocks):
        for c in range(classes):
            for _ in range(per_class):
                labels.append(c)
                blocks.append(b)
    return (
        np.array(labels, dtype=np.int64),
        np.array(blocks, dtype=np.int64),
    )


class PowerReplicateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.labels, self.blocks = _geometry()
        self.n = len(self.labels)
        self.layout = _Layout(self.labels, self.blocks)
        self.u_curve = np.linspace(-1.0, 1.0, self.n)
        self.fn = _PowerReplicate(
            "POOL_T", self.n, self.labels, self.blocks, self.u_curve,
            "R2_NBAND_w2", B, self.layout,
        )
        self.grid = [
            (d_idx, delta, r)
            for d_idx, delta in enumerate(DELTAS)
            for r in range(REPLICATES)
        ]

    def test_replicate_reproduces_the_inline_computation(self) -> None:
        """The callable must be the original loop body, not a rewrite of it."""
        for d_idx, delta, r in self.grid[:6]:
            with self.subTest(d_idx=d_idx, r=r):
                rng = np.random.default_rng(
                    derive_seed("CTRLPOWER", "POOL_T", "R2_NBAND_w2",
                                "synthetic", d_idx, r))
                eps = rng.standard_normal(self.n)
                Y = eps + delta * self.u_curve
                seed = derive_seed("CTRLPOWERPERM", "POOL_T", "R2_NBAND_w2",
                                   "synthetic", d_idx, r)
                expected = blocked_permutation_null_both(
                    Y, self.labels, self.blocks, B, seed, layout=self.layout
                )["weighted"]["p_lower"]
                self.assertEqual(self.fn(0, (d_idx, delta, r)), expected)

    def test_parallel_grid_is_bit_identical(self) -> None:
        serial = _map_replicates(self.fn, self.grid, 1)
        for workers in (2, WORKERS):
            with self.subTest(workers=workers):
                self.assertEqual(_map_replicates(self.fn, self.grid, workers),
                                 serial)

    def test_regrouping_by_delta_survives_the_fan_out(self) -> None:
        # s5_controls slices the flat result back into per-delta rows; the
        # slice boundaries must still line up with the delta they name.
        serial = _map_replicates(self.fn, self.grid, 1)
        parallel = _map_replicates(self.fn, self.grid, WORKERS)
        for d_idx, _delta in enumerate(DELTAS):
            lo, hi = d_idx * REPLICATES, (d_idx + 1) * REPLICATES
            self.assertEqual(parallel[lo:hi], serial[lo:hi])

    def test_float_reductions_over_the_result_are_identical(self) -> None:
        # sum() is order-dependent in float64, which is why sharded_map places
        # by index instead of appending on completion.
        serial = _map_replicates(self.fn, self.grid, 1)
        parallel = _map_replicates(self.fn, self.grid, WORKERS)
        self.assertEqual(sum(parallel) / len(parallel),
                         sum(serial) / len(serial))
        self.assertEqual(min(parallel), min(serial))
        self.assertEqual(max(parallel), max(serial))
        self.assertEqual(sum(1 for x in parallel if x <= 0.05),
                         sum(1 for x in serial if x <= 0.05))


class NullObjReplicateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.labels, self.blocks = _geometry()
        n = len(self.labels)
        self.vals = np.linspace(0.5, 2.5, n)
        rng = np.random.default_rng(4242)
        self.items = [
            (r, np.asarray(rng.permutation(self.labels), dtype=np.int64))
            for r in range(REPLICATES)
        ]
        self.fn = _NullObjReplicate(
            "POOL_T", self.vals, self.blocks, "R3_NBAND_w3",
            "full_liftable", B,
        )

    def test_replicate_reproduces_the_inline_computation(self) -> None:
        for r, lab in self.items[:4]:
            with self.subTest(r=r):
                seed = derive_seed("NULLOBJ", "POOL_T", "R3_NBAND_w3",
                                   "full_liftable", 0, r)
                d = blocked_permutation_null_both(
                    self.vals, lab, self.blocks, B, seed)["weighted"]
                self.assertEqual(self.fn(0, (r, lab)),
                                 (d["p_lower"], d["T_obs"]))

    def test_parallel_is_bit_identical(self) -> None:
        serial = _map_replicates(self.fn, self.items, 1)
        parallel = _map_replicates(self.fn, self.items, WORKERS)
        self.assertEqual(parallel, serial)

    def test_unzipping_preserves_pairing(self) -> None:
        pairs = _map_replicates(self.fn, self.items, WORKERS)
        reference = _map_replicates(self.fn, self.items, 1)
        self.assertEqual([p for p, _ in pairs], [p for p, _ in reference])
        self.assertEqual([t for _, t in pairs], [t for _, t in reference])


class S5ControlsIntegrationTests(unittest.TestCase):
    """The whole control stage, serial vs parallel, compared as bytes.

    The replicate callables are verified above; what this adds is the WIRING --
    that s5_controls hands them the right arrays in the right order and slices
    the flat result back onto the delta it names. A transposed labels/blocks
    pair would still produce a self-consistent parallel run and would only show
    up against the serial one.
    """

    @staticmethod
    def _pool():
        from dataclasses import dataclass

        from harness.run_blocknull import MINIMUM_CLASS_SIZE, build_pool

        @dataclass
        class _Rec:
            p: int
            a: int
            b: int
            order: int
            trace: int

        p = 100003
        traces = [40, 120, 200, 280]
        size = MINIMUM_CLASS_SIZE + 4
        classes = {
            t: [_Rec(p, 1, 1, p + 1 - t, t) for _ in range(size)]
            for t in traces
        }
        return build_pool("POOL_T", p, traces, classes, "test-stub")

    def _inputs(self, pool, control_b: int):
        from harness.run_blocknull import RUNGS, blocks_array, functional_keys

        geo = {r: blocks_array(pool, r)[1] for r in RUNGS}
        rng = np.random.default_rng(7)
        keys = list(functional_keys(pool.p))
        values = {k: rng.normal(size=pool.n) for k in keys}
        values.setdefault("full_liftable", rng.normal(size=pool.n))
        ladder = {
            "rung_geometry": geo,
            "B": control_b,
            "nuisance_budget_by_rung": {
                r: {"weighted": 0.01, "unweighted": 0.01} for r in RUNGS
            },
            "cells": {
                f"{pool.name}|{k}|{r}|weighted|B{control_b}": {
                    "variance_ratio_R_empirical": 1.25
                }
                for k in keys + ["full_liftable"]
                for r in RUNGS
            },
        }
        return values, ladder

    def test_control_stage_output_is_byte_identical(self) -> None:
        import json

        from harness.run_blocknull import s5_controls

        pool = self._pool()
        control_b = 48
        values, ladder = self._inputs(pool, control_b)

        def run(workers: int) -> str:
            out = s5_controls(pool, values, ladder, replicates=8,
                              B=control_b, workers=workers)
            return json.dumps(out, sort_keys=True, default=str)

        serial = run(1)
        self.assertEqual(run(WORKERS), serial)
        # Guard against the comparison silently passing on an empty result.
        self.assertIn("CTRL_POWER", serial)
        self.assertIn("CTRL_NULLOBJ", serial)
        self.assertGreater(len(serial), 10_000)


class SerialPathTests(unittest.TestCase):
    def test_workers_one_does_not_import_the_runner_package(self) -> None:
        # The default path must stay usable in a standalone invocation that has
        # no crypto_autoresearcher installed, so the import is deferred.
        import sys

        saved = {
            name: sys.modules.pop(name)
            for name in list(sys.modules)
            if name.startswith("crypto_autoresearcher.parallel")
        }
        try:
            labels, blocks = _geometry()
            fn = _NullObjReplicate("POOL_T", np.linspace(1.0, 2.0, len(labels)),
                                   blocks, "R0_FREE", "full_liftable", B)
            _map_replicates(fn, [(0, labels)], 1)
            self.assertNotIn("crypto_autoresearcher.parallel", sys.modules)
        finally:
            sys.modules.update(saved)


if __name__ == "__main__":
    unittest.main()
