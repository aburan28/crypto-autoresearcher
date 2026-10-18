"""Arithmetic route a: exact Fraction ordering and exponentiation."""
from fractions import Fraction
def compute(inputs):
    left,witness,right = [Fraction(inputs[k]) for k in ("left","witness","right")]
    products = [[left.numerator*witness.denominator,left.denominator*witness.numerator],
                [witness.numerator*right.denominator,witness.denominator*right.numerator],
                [right.numerator*left.denominator,right.denominator*left.numerator]]
    return {"measurement": {"left_below_witness": left<witness, "witness_below_right": witness<right,
        "n_squared": inputs["n"]**2, "n_cubed": inputs["n"]**3, "reversed_below": right<left,
        "cross_products": products, "tail_products": [5*6,6*5]}, "witness": {"rational_cross_products": products}}

def assess(inputs, m):
    return {"reversed_comparison_false": not m["reversed_below"],
            "both_tail_products_computed": m["tail_products"] == [5*6,6*5]}, {
        "witness_inside": (m["left_below_witness"] and m["witness_below_right"]) == inputs["predicted"]["witness_inside"],
        "n_squared": m["n_squared"] == inputs["predicted"]["n_squared"],
        "n_cubed": m["n_cubed"] == inputs["predicted"]["n_cubed"],
        "reversed_below": m["reversed_below"] == inputs["predicted"]["reversed_below"]}

