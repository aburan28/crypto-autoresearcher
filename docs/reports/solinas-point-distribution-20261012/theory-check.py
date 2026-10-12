"""Independent complete scalar checks of the derived uniform-model moments."""
import json
from pathlib import Path

rows = []
for p in (5, 7, 11, 17, 29):
    squares = {y * y % p for y in range(p)}
    total_square = non_square = non_count = non_coverage = non_trace = 0
    for a in range(p):
        for b in range(p):
            weights = []
            for x in range(p):
                rhs = (x**3 + a * x + b) % p
                weights.append(1 if rhs == 0 else (2 if rhs in squares else 0))
            trace = p - sum(weights)
            total_square += trace * trace
            if (4 * a**3 + 27 * b**2) % p:
                non_square += trace * trace
                non_count += 1
                non_coverage += sum(w > 0 for w in weights)
                non_trace += trace
    assert non_count == p * (p - 1)
    assert total_square == p * p * (p - 1)
    assert non_square == (p - 1) * (p * p - 1)
    assert 2 * non_coverage == (p - 1) * (p * p + p - 1)
    assert non_trace == 0
    rows.append({"p": p, "nonsingular_models": non_count, "sum_trace_squared": non_square,
                 "sum_trace": non_trace, "sum_liftable_x": non_coverage})
result = {"status": "passed", "checks": rows,
          "scope": "Independent exhaustive software checks at five primes. General formulas are algebraically derived in THEORY.md, not established merely by finite tests."}
with (Path(__file__).parent / "theory-check.json").open("x") as stream:
    json.dump(result, stream, sort_keys=True, indent=2)
    stream.write("\n")
print(json.dumps(result))
