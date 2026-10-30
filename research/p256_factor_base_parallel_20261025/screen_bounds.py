"""Exact necessary representation counts, not an attack-cost forecast.

For a fixed signed base F=-F of 2M nonzero points, every unordered d-multiset
has exactly one sum. Thus the number of represented nonzero targets is at
most binomial(2M+d-1,d). Collisions and zero sums only reduce coverage.
The bound requires the base to be fixed before a uniform nonzero target.
It does not cover a target-dependent coefficient-labelled base.
"""
from decimal import Decimal, localcontext
from math import comb
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "baseline"))
from parameters import CURVES


def minimum_half_coverage_base(r, arity):
    def enough(m):
        return 2 * comb(2*m + arity - 1, arity) >= r - 1
    low, high = 0, 1
    while not enough(high):
        high *= 2
    while low + 1 < high:
        mid = (low + high) // 2
        if enough(mid):
            high = mid
        else:
            low = mid
    assert enough(high) and not enough(high-1)
    return high


def generate():
    curve = next(c for c in CURVES if c["name"] == "P-256")
    r = curve["r"]
    rows = []
    with localcontext() as context:
        context.prec = 70
        for d in range(3, 9):
            m = minimum_half_coverage_base(r, d)
            rows.append({
                "arity": d,
                "minimum_canonical_base_size_necessary": str(m),
                "log2_M_approx": str(Decimal(m).ln()/Decimal(2).ln()),
                "multisets_at_M": str(comb(2*m+d-1, d)),
                "multisets_at_M_minus_1": str(comb(2*(m-1)+d-1, d)),
                "logical_status": "necessary only; no density, independence or solving-cost assertion",
            })
    return {
        "schema": "p256-fixed-base-counting-screen/v1",
        "date": "2026-10-25",
        "parameters": {"name": "P-256", "p": str(curve["p"]), "r": str(r),
                       "a": str(curve["a"]), "b": str(curve["b"]), "cofactor": 1},
        "statement": "Pr(nonempty) <= min(1, binomial(2M+d-1,d)/(r-1)); 2*binomial(2M+d-1,d)>=r-1 is necessary for probability at least one half.",
        "assumptions": ["fixed base before target selection", "uniform nonzero target in the prime-order group", "unordered multisets with repetitions allowed"],
        "rows": rows,
        "limitations": ["Not a success lower bound.", "Does not apply directly to target-dependent F3 bases.", "No algorithmic time or memory bound is inferred from this count."],
    }


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "counting-screen.json"
    if output.exists():
        raise SystemExit("Refusing to overwrite an earlier counting-screen receipt")
    output.write_text(json.dumps(generate(), indent=2)+"\n")
    print(f"6 exact integer boundary checks passed; receipt: {output}")
