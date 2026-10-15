"""Independent exhaustive group-law control for collector.rs.

This is a bounded implementation test, not a scientific endpoint trial.
"""
from __future__ import annotations

import itertools
import subprocess
import sys
import tempfile
from pathlib import Path
from verify_collector import Curve, column_layout, row_for, verify

P = 17
A = 2
B = 2
R = 19
G = (5, 1)
IDENTITY = None


def neg(point):
    return None if point is None else (point[0], (-point[1]) % P)


def add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + A) * pow(2 * y1, -1, P)) % P
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, P)) % P
    x3 = (slope * slope - x1 - x2) % P
    return x3, (slope * (x1 - x3) - y1) % P


def mul(scalar, point):
    result = None
    while scalar:
        if scalar & 1:
            result = add(result, point)
        point = add(point, point)
        scalar >>= 1
    return result


def first_signed_base(count):
    base = []
    for x in range(P):
        roots = [y for y in range(P) if y * y % P == (x**3 + A * x + B) % P]
        if len(roots) == 2:
            y = min(roots)
            base.extend(((x, y), (x, (-y) % P)))
            if len(base) == 2 * count:
                return base
    raise AssertionError("insufficient base")


def encode_input(base, targets, curve=(P, A, B, R)):
    rows = [f"curve {curve[0]} {curve[1]} {curve[2]} {curve[3]} {len(base)} {len(targets)}"]
    rows.extend(f"base {i} {x} {y}" for i, (x, y) in enumerate(base))
    rows.extend(
        f"target {i} {alpha} {beta} {point[0]} {point[1]}"
        for i, alpha, beta, point in targets
    )
    return "\n".join(rows) + "\n"


def exhaustive(base, target):
    found = set()
    for triple in itertools.product(range(len(base)), repeat=3):
        if add(add(base[triple[0]], base[triple[1]]), base[triple[2]]) == target:
            found.add(tuple(sorted(triple)))
    ordered = sum(
        1 if i == k else 3 if i == j or j == k else 6 for i, j, k in found
    )
    useful = sum(
        i != j and j != k and len({i // 2, j // 2, k // 2}) == 3
        for i, j, k in found
    )
    return found, ordered, useful


def main(binary, count_binary=None):
    assert mul(R, G) is None
    base = first_signed_base(3)
    q = mul(7, G)
    targets = [((scalar - 7) % R, 1, mul(scalar, G)) for scalar in range(1, R)]
    assert len({point for _, _, point in targets}) == R - 1
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "input.txt"
        path.write_text(
            encode_input(base, [(i, alpha, beta, point) for i, (alpha, beta, point) in enumerate(targets)]),
            encoding="utf-8",
        )
        process = subprocess.run([binary, str(path)], capture_output=True, text=True, check=True)
        output_path = Path(directory) / "output.txt"
        output_path.write_text(process.stdout, encoding="utf-8")
        receipt = verify(path, output_path, G, q, {1, 2, 18})
        assert receipt["status"] == "valid"
        assert receipt["unknown_columns"] == 2  # G and Q both occupy base orbits.
        assert receipt["rank_prefix"][18] <= receipt["unknown_columns"]
        outside_q = mul(2, G)
        assert outside_q[0] not in {point[0] for point in base}
        outside_targets = [((scalar - 2) % R, 1, mul(scalar, G)) for scalar in range(1, R)]
        outside_path = Path(directory) / "outside_input.txt"
        outside_path.write_text(
            encode_input(base, [(i, alpha, beta, point) for i, (alpha, beta, point) in enumerate(outside_targets)]),
            encoding="utf-8",
        )
        outside_output = Path(directory) / "outside_output.txt"
        outside_output.write_text(
            subprocess.run([binary, str(outside_path)], capture_output=True, text=True, check=True).stdout,
            encoding="utf-8",
        )
        outside_receipt = verify(outside_path, outside_output, G, outside_q, {1, 2, 18})
        assert outside_receipt["status"] == "valid"
        assert outside_receipt["unknown_columns"] == 3  # Q has its own column.
        assert outside_receipt["rank_prefix"][18] <= outside_receipt["unknown_columns"]
        count_lines = None
        if count_binary is not None:
            count_text = subprocess.run(
                [count_binary, str(path)], capture_output=True, text=True, check=True
            ).stdout
            count_lines = count_text.splitlines()
            count_path = Path(directory) / "count_output.txt"
            count_path.write_text(count_text, encoding="utf-8")
            complete_receipt = verify(path, output_path, G, q, {1, 2, 18}, count_path)
            assert complete_receipt["independent_ordered_count_match"] is True
        transformed_curve = (P, (16 * A) % P, (64 * B) % P, R)
        transformed = lambda point: ((4 * point[0]) % P, (8 * point[1]) % P)
        mapped_base = [transformed(point) for point in base]
        mapped_targets = [
            (index, alpha, beta, transformed(point))
            for index, (alpha, beta, point) in enumerate(targets)
        ]
        mapped_path = Path(directory) / "mapped_input.txt"
        mapped_path.write_text(encode_input(mapped_base, mapped_targets, transformed_curve))
        mapped_output = Path(directory) / "mapped_output.txt"
        mapped_output.write_text(
            subprocess.run([binary, str(mapped_path)], capture_output=True, text=True, check=True).stdout
        )
        mapped_receipt = verify(mapped_path, mapped_output, transformed(G), transformed(q), {18})
        assert mapped_receipt["status"] == "valid"
        native_counts = [line.split("\t")[4:] for line in process.stdout.splitlines() if line.startswith("target\t")]
        mapped_counts = [line.split("\t")[4:] for line in mapped_output.read_text().splitlines() if line.startswith("target\t")]
        assert native_counts == mapped_counts
    lines = process.stdout.splitlines()
    assert lines[0] == f"collector-v1\t{P}\t{R}\t{len(base)}\t{len(targets)}"
    observed = {}
    for line in lines[1:]:
        fields = line.split("\t")
        if fields[0] == "target":
            index, alpha, beta, unordered, ordered, useful = map(int, fields[1:])
            assert (alpha, beta) == targets[index][:2]
            observed[index] = {"counts": (unordered, ordered, useful), "triples": set()}
        elif fields[0] == "triple":
            index, i, j, k = map(int, fields[1:])
            assert i <= j <= k
            observed[index]["triples"].add((i, j, k))
        else:
            raise AssertionError(fields)
    assert len(observed) == R - 1
    if count_lines is not None:
        assert count_lines[0] == f"count-v1\t{P}\t{R}\t{len(base)}\t{len(targets)}"
        assert len(count_lines) == R
        for index, line in enumerate(count_lines[1:]):
            assert line == f"target\t{index}\t{observed[index]['counts'][1]}"
    for index, (_, _, point) in enumerate(targets):
        triples, ordered, useful = exhaustive(base, point)
        assert observed[index]["triples"] == triples, index
        assert observed[index]["counts"] == (len(triples), ordered, useful), index
    curve = Curve(P, A, B, R)
    logs = {mul(scalar, G): scalar for scalar in range(1, R)}
    for k, target_rows in ((7, targets), (2, outside_targets)):
        q_for_layout = mul(k, G)
        layout = column_layout(base, G, q_for_layout, curve)
        unknown_logs = [0] * (len(layout[4]) + (layout[5] is not None))
        for orbit, column in layout[4].items():
            unknown_logs[column] = logs[base[2 * orbit]]
        if layout[5] is not None:
            unknown_logs[layout[5]] = k
        for index, (alpha, beta, _point) in enumerate(target_rows):
            for triple in observed[index]["triples"]:
                i, j, h = triple
                if i == j or j == h or len({i // 2, j // 2, h // 2}) != 3:
                    continue
                row, rhs = row_for(triple, alpha, beta, base, curve, layout)
                assert sum(value * log for value, log in zip(row, unknown_logs)) % R == rhs
    all_targets = [None] + [mul(scalar, G) for scalar in range(1, R)]
    assert sum(exhaustive(base, point)[1] for point in all_targets) == len(base) ** 3
    print("small-group exhaustive control: 18 targets, all triple sets/counts, both Q-column cases with scalar row replay, independent ordered counts, u2 transported equality, |F|^3 identity PASS")


if __name__ == "__main__":
    main(
        sys.argv[1] if len(sys.argv) > 1 else "/private/tmp/conductor_arity3_collector",
        sys.argv[2] if len(sys.argv) > 2 else None,
    )
