import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze import primary_comparisons
from measure import (circular_gaps, correlation, decode_coordinates, encode_coordinates,
                     exact_weights, field_arrays, identity, make_probes, naf_weight,
                     probe_stats, scalar_weight, window_stats)
from prepare import toy_inputs
from run import measure_field, sqrt_mod


class MeasurementTests(unittest.TestCase):
    def test_exhaustive_independent_y_oracle(self):
        for p in (17, 101, 251):
            x, roots = field_arrays(p)
            for a, b in ((2, 2), (3, 7), (0, 1)):
                weights = exact_weights(p, a, b, x, roots)
                reference = [sum(y * y % p == (q**3 + a * q + b) % p for y in range(p)) for q in range(p)]
                self.assertEqual(weights.tolist(), reference)
                self.assertEqual(weights.tolist(), [scalar_weight(p, a, b, q) for q in range(p)])
        self.assertEqual(1 + sum(reference), 252)
        weights = exact_weights(17, 2, 2, *field_arrays(17))
        self.assertEqual(1 + int(weights.sum()), 19)

    def test_singular_rejected(self):
        with self.assertRaises(ValueError):
            exact_weights(17, 0, 0, *field_arrays(17))

    def test_full_isomorphism(self):
        p, a, b, u = 101, 3, 7, 13
        x, roots = field_arrays(p)
        old = exact_weights(p, a, b, x, roots)
        new = exact_weights(p, a * pow(u, 4, p) % p, b * pow(u, 6, p) % p, x, roots)
        np.testing.assert_array_equal(new[x * u * u % p], old)
        self.assertEqual(int(old.sum()), int(new.sum()))

    def test_circular_gap_wrap(self):
        stats = circular_gaps(np.array([1, 0, 0, 1, 0, 0, 0, 0], dtype=bool))
        self.assertEqual(stats["max_empty_run"], 4)
        self.assertEqual(stats["histogram_1_to_32_plus_overflow"][2], 1)
        self.assertEqual(stats["histogram_1_to_32_plus_overflow"][4], 1)
        self.assertEqual(circular_gaps(np.zeros(8, dtype=bool))["max_empty_run"], 8)

    def test_statistic_positive_control(self):
        clustered = np.tile(np.repeat([0, 2], 64), 16).astype(np.uint8)
        random_control = clustered.copy()
        np.random.default_rng(123).shuffle(random_control)
        self.assertGreater(window_stats(clustered, [1])["lag_correlations"]["1"], 0.9)
        self.assertLess(abs(window_stats(random_control, [1])["lag_correlations"]["1"]), 0.1)
        self.assertIsNone(correlation(np.ones(8, dtype=bool), 1))

    def test_mass_not_liftability(self):
        xs, weights = [0, 1, 8, 9], np.array([0, 1, 2, 2], dtype=np.uint8)
        stats = probe_stats(17, xs, weights, 2)
        self.assertEqual(stats["proposal_counts"], [3, 1])
        self.assertEqual(stats["point_mass"], [3, 2])
        self.assertEqual(stats["coverage"], 0.75)
        self.assertEqual(stats["point_density"], 1.25)

    def test_deterministic_probes_and_bigint_encoding(self):
        for p in (101, (1 << 224) - (1 << 96) + 1):
            first = make_probes(p, 42, identity(p, 2, 3), 32, 16)
            self.assertEqual(first, make_probes(p, 42, identity(p, 2, 3), 32, 16))
            self.assertEqual(len(set(first[0])), 32)
            self.assertEqual(decode_coordinates(encode_coordinates(first[0], p)), first[0])

    def test_tonelli_shanks(self):
        for p in (17, 101, 103):
            for x in range(p):
                y = sqrt_mod(x, p)
                if y is None:
                    self.assertFalse(any(z * z % p == x for z in range(p)))
                else:
                    self.assertEqual(y * y % p, x)

    def test_naf(self):
        self.assertEqual(naf_weight((1 << 192) - (1 << 64) - 1), 3)
        self.assertEqual(naf_weight((1 << 224) - (1 << 96) + 1), 3)

    def test_small_field_artifact(self):
        config = json.loads((Path(__file__).resolve().parents[1] / "config.json").read_text())
        config.update(uniform_probes=16, window_probes=16, lags=[1, 2, 4], x_bins=4)
        task = {"id": "self-check", "case": "self-check", "arm": "S", "block": 0, "p": 101,
                "bits": 7, "naf_weight": naf_weight(101), "kind": "census",
                "models": [{"index": 0, "p": 101, "A": 3, "B": 7}]}
        with tempfile.TemporaryDirectory() as directory:
            measure_field(task, config, directory)
            row = json.loads((Path(directory) / "self-check.json").read_text())
            with np.load(Path(directory) / "self-check.npz", allow_pickle=False) as raw:
                lift = np.unpackbits(raw["census_liftability_packed"][0], bitorder="little")[:101]
                zeros = row["curves"][0]["census"]["zero_x"]
                weights = 2 * lift
                weights[zeros] = 1
                self.assertEqual(1 + int(weights.sum()), row["curves"][0]["N"])
                self.assertEqual(row["isomorphic_companion"]["N"], row["curves"][0]["N"])

    def test_production_matching_and_independent_field_counts(self):
        config = json.loads((Path(__file__).resolve().parents[1] / "config.json").read_text())
        tasks, populations = toy_inputs(config)
        self.assertEqual([(r["all_primes"], r["sparse_primes"]) for r in populations], [(10749, 2955), (38635, 5108)])
        self.assertEqual(len(tasks), 5120)
        self.assertEqual(sum(len(t["models"]) for t in tasks), 20480)
        for bits in config["toy_bits"]:
            subset = [t for t in tasks if t["bits"] == bits]
            self.assertEqual(len({t["p"] for t in subset}), len(subset))
            for block in range(config["blocks_per_stratum"]):
                rows = [t for t in subset if t["block"] == block]
                s = next(t["p"] for t in rows if t["arm"] == "S")
                for row in rows:
                    self.assertEqual(row["p"].bit_length(), bits)
                    self.assertLessEqual(abs(row["p"] - s), s * .05)
                    if row["arm"] == "C":
                        self.assertEqual(row["p"] % 96, s % 96)
                    if row["arm"] == "S":
                        self.assertLessEqual(naf_weight(s), 6)

    def test_confidence_unit_is_field_block(self):
        config = {"primary_cases": ["toy-check"], "primary_metrics": ["trace_square"],
                  "primary_control_arms": ["R", "C"], "blocks_per_stratum": 3,
                  "random_controls_per_block": 2, "residue_controls_per_block": 2,
                  "familywise_alpha": .001, "primary_comparisons": 2}
        fields = []
        for block in range(3):
            for arm, count in (("S", 1), ("R", 2), ("C", 2)):
                for _ in range(count):
                    value = block / 4 if arm == "S" else .1
                    fields.append({"case": "toy-check", "block": block, "arm": arm,
                                   "curves": [{"trace_square": value}] * 4})
        first = primary_comparisons(fields, config)
        for field in fields:
            field["curves"] *= 20
        second = primary_comparisons(fields, config)
        for left, right in zip(first, second):
            for key in ("difference", "standard_error", "degrees_of_freedom"):
                self.assertAlmostEqual(left[key], right[key], places=14)
            np.testing.assert_allclose(left["simultaneous_interval"], right["simultaneous_interval"], rtol=1e-14)
        self.assertEqual(first[0]["structured_units"], 3)
        self.assertEqual(first[0]["degrees_of_freedom"], 2)


if __name__ == "__main__":
    unittest.main()
