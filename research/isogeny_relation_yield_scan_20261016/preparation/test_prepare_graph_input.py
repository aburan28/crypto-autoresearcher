"""Small fixed implementation controls; never part of a scientific target stream."""
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_graph_input import SCHEDULE, base_points, draw, load_vertex, prepare, target_coefficients
from verify_collector import add, multiply, parse_input, on_curve


STUDY = Path(__file__).resolve().parents[1]
WALKS = {"P29": STUDY / "walk-p29-2048-attempt2.jsonl",
         "P37": STUDY / "walk-p37-256.jsonl"}
BASE_ROOT = b"B" * 32
TARGET_ROOT = b"T" * 32


def parse_payload(payload):
    lines = payload.decode().splitlines()
    header = lines[0].split()
    nbase = int(header[5])
    base = [tuple(map(int, line.split()[2:])) for line in lines[1:1 + nbase]]
    targets = [tuple(map(int, line.split()[2:])) for line in lines[1 + nbase:]]
    return base, targets


def main():
    cases = 0
    for stratum, walk in WALKS.items():
        header0, model0, curve0, generator0 = load_vertex(walk, 0)
        header1, model1, curve1, generator1 = load_vertex(walk, 1)
        assert header0 == header1 and model0["j"] != model1["j"]
        k, coeffs, _ = target_coefficients(TARGET_ROOT, stratum, "discovery", curve0.r, 8)
        assert len(coeffs) == 8 and len({scalar for _, _, scalar in coeffs}) == 8
        assert all(scalar for _, _, scalar in coeffs)
        assert draw(BASE_ROOT, ["domain-a"], 1000) == draw(BASE_ROOT, ["domain-a"], 1000)
        assert draw(BASE_ROOT, ["domain-a"], 1000) != draw(BASE_ROOT, ["domain-b"], 1000)
        arms = ("low_x", "mid_x", "random_x", "power_x", "u2_native", "u2_transport")
        for index in (0, 1):
            expected_coeffs = None
            for arm in arms:
                if arm == "power_x" and index != 0:
                    continue
                payload, meta = prepare(walk, index, arm, "discovery", BASE_ROOT, TARGET_ROOT, 8)
                again, same_meta = prepare(walk, index, arm, "discovery", BASE_ROOT, TARGET_ROOT, 8)
                assert payload == again and meta == same_meta
                assert meta["input_sha256"] == hashlib.sha256(payload).hexdigest()
                base, targets = parse_payload(payload)
                assert len(base) == 2 * SCHEDULE[stratum]["B"] and len(targets) == 8
                assert len({base[j][0] for j in range(0, len(base), 2)}) == SCHEDULE[stratum]["B"]
                target_coeffs = [(a, b) for a, b, _, _ in targets]
                assert target_coeffs == [(a, b) for a, b, _ in coeffs]
                if expected_coeffs is None:
                    expected_coeffs = target_coeffs
                assert expected_coeffs == target_coeffs
                q = tuple(meta["Q"])
                g = tuple(meta["generator"])
                result_curve = curve0 if index == 0 else curve1
                if arm.startswith("u2"):
                    from verify_collector import Curve
                    result_curve = Curve(result_curve.p, 16 * result_curve.a % result_curve.p,
                                         64 * result_curve.b % result_curve.p, result_curve.r)
                assert all(on_curve(point, result_curve) for point in base)
                assert all(add(multiply(a, g, result_curve), multiply(b, q, result_curve), result_curve) == (x, y)
                           for a, b, x, y in targets)
                cases += 1
            low, _ = prepare(walk, index, "low_x", "discovery", BASE_ROOT, TARGET_ROOT, 8)
            transported, _ = prepare(walk, index, "u2_transport", "discovery", BASE_ROOT, TARGET_ROOT, 8)
            low_base, low_targets = parse_payload(low)
            trans_base, trans_targets = parse_payload(transported)
            assert trans_base == [(x * 4 % curve0.p, y * 8 % curve0.p) for x, y in low_base]
            assert [(a, b) for a, b, _, _ in low_targets] == [(a, b) for a, b, _, _ in trans_targets]
        try:
            prepare(walk, 1, "power_x", "discovery", BASE_ROOT, TARGET_ROOT, 8)
        except ValueError:
            pass
        else:
            raise AssertionError("power_x index restriction missing")
    print({"status": "pass", "small_fixture_cases": cases,
           "scope": "base/target preparation correctness only; no relation collection"})


if __name__ == "__main__":
    main()
