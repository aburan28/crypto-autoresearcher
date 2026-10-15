"""Bounded algebraic checks for deterministic prepared-input generation."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from prepare_input import HERE, prepare, transform
from verify_collector import add, multiply, on_curve, parse_input


def main():
    plan = json.loads((HERE / "plan.json").read_text())
    seed = bytes(range(32))
    k_seed = bytes(reversed(range(32)))
    with tempfile.TemporaryDirectory() as temporary:
        for endpoint in ("P29-crater", "P29-floor", "P29-E2", "P29-E3", "P37-crater", "P37-floor"):
            prepared = {}
            for arm in ("native", "random", "u2-transport", "u2-native"):
                payload, manifest = prepare(plan, endpoint, arm, seed, k_seed, 8)
                path = Path(temporary) / f"{endpoint}-{arm}.txt"
                path.write_bytes(payload)
                curve, base, targets = parse_input(path)
                assert len(base) == 2 * manifest["base_abscissae"]
                assert len(targets) == 8
                assert manifest["protocol_conformant_target_count"] is False
                assert len(manifest["base_sha256"]) == len(manifest["target_vector_sha256"]) == 64
                assert curve.p in (320092037, 81640512137)
                generator = tuple(manifest["generator"])
                q = tuple(manifest["Q"])
                assert on_curve(generator, curve) and on_curve(q, curve)
                assert all(on_curve(point, curve) for point in base)
                for alpha, beta, point in targets:
                    assert point == add(multiply(alpha, generator, curve), multiply(beta, q, curve), curve)
                prepared[arm] = (curve, base, targets, manifest)
            native_curve, native_base, native_targets, native_manifest = prepared["native"]
            random_curve, random_base, random_targets, random_manifest = prepared["random"]
            assert random_curve == native_curve
            assert random_targets == native_targets
            assert len({point[0] for point in random_base}) == len(native_base) // 2
            transport_curve, transport_base, transport_targets, transport_manifest = prepared["u2-transport"]
            rebuilt_curve, rebuilt_base, rebuilt_targets, rebuilt_manifest = prepared["u2-native"]
            assert transport_curve == rebuilt_curve
            assert transport_targets == rebuilt_targets
            assert transport_base == [transform(native_curve, point) for point in native_base]
            assert transport_targets == [
                (alpha, beta, transform(native_curve, point))
                for alpha, beta, point in native_targets
            ]
            assert transport_manifest["Q"] == transform(native_curve, tuple(native_manifest["Q"]))
            assert rebuilt_manifest["Q"] == transport_manifest["Q"]
            assert all(0 <= point[0] < native_curve.p for point in rebuilt_base)
    print("prepared-input algebraic control: 6 endpoints, 4 arms, 8 distinct targets each PASS")


if __name__ == "__main__":
    main()
