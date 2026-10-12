"""Verify immutable artifacts and exact point identities independently of analysis."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from measure import decode_coordinates, identity, scalar_weight


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify(run):
    inputs = json.loads((run / "inputs.json").read_text())
    receipt = json.loads((run / "receipt.json").read_text())
    assert receipt["status"] == "complete" and not receipt["failures"]
    assert receipt["input_sha256"] == sha(run / "inputs.json")
    assert receipt["environment_sha256"] == sha(run / "environment.json")
    task_by_id = {row["id"]: row for row in inputs["tasks"]}
    assert set(task_by_id) == {row["field_id"] for row in receipt["fields"]}
    curves = checked = raw_bytes = 0
    for entry in receipt["fields"]:
        path = run / "fields" / (entry["field_id"] + ".json")
        assert sha(path) == entry["json_sha256"]
        field = json.loads(path.read_text())
        task = task_by_id[entry["field_id"]]
        assert (field["p"], field["arm"], field["case"]) == (task["p"], task["arm"], task["case"])
        raw_path = path.parent / field["raw_file"]
        assert sha(raw_path) == entry["raw_sha256"] == field["raw_sha256"]
        raw_bytes += raw_path.stat().st_size
        with np.load(raw_path, allow_pickle=False) as raw:
            for i, row in enumerate(field["curves"]):
                p, a, b, n = row["p"], row["A"], row["B"], row["N"]
                assert row["curve_id"] == identity(p, a, b)
                assert (a, b, p) == (task["models"][i]["A"], task["models"][i]["B"], task["p"])
                assert (4 * a**3 + 27 * b**2) % p
                assert (p + 1 - n) ** 2 <= 4 * p
                xs = decode_coordinates(raw["uniform_x_bytes"][i])
                weights = raw["uniform_weights"][i]
                assert len(xs) == len(set(xs)) == inputs["config"]["uniform_probes"]
                assert all(0 <= x < p for x in xs)
                assert np.isin(weights, [0, 1, 2]).all()
                for x, weight in zip(xs[:16], weights[:16]):
                    assert scalar_weight(p, a, b, x) == weight
                    checked += 1
                assert abs(float((weights > 0).mean()) - row["uniform"]["coverage"]) < 1e-15
                assert int(weights.sum()) == sum(row["uniform"]["point_mass"])
                for x, y in row["public_point_examples"]:
                    assert y * y % p == (x**3 + a * x + b) % p
                if field["kind"] == "census":
                    packed = raw["census_liftability_packed"][i]
                    lift = np.unpackbits(packed, bitorder="little")[:p]
                    zeros = row["census"]["zero_x"]
                    assert 1 + 2 * int(lift.sum()) - len(zeros) == n
                    assert int(lift.sum()) == row["census"]["coverage_count"]
                    assert lift[xs].tolist() == (weights > 0).astype(np.uint8).tolist()
                    assert sum(row["census"]["x_bin_point_mass"]) == n - 1
                    assert sum(row["census"]["histogram_1_to_32_plus_overflow"]) == int(lift.sum())
                    for x in zeros:
                        assert (x**3 + a * x + b) % p == 0
                else:
                    assert n == task["models"][i]["N"]
                curves += 1
            companion = field["isomorphic_companion"]
            u = companion["isomorphism"]["u"]
            first = field["curves"][0]
            assert companion["A"] == first["A"] * pow(u, 4, p) % p
            assert companion["B"] == first["B"] * pow(u, 6, p) % p
            assert companion["N"] == first["N"]
    assert curves == inputs["curves"]
    result = {"status": "passed", "fields": len(task_by_id), "curves": curves,
              "independent_scalar_character_spot_checks": checked, "raw_bytes_verified": raw_bytes,
              "receipt_sha256": sha(run / "receipt.json"),
              "limitations": "Same-session software verification and independent formulas, not an independent research review."}
    with (run / "verification.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.run), indent=2))
