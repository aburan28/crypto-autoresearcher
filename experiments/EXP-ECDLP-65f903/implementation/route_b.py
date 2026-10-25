"""Arithmetic route b: unreduced cross products and repeated multiplication."""
def compute(inputs):
    pairs = [tuple(map(int,inputs[k].split("/"))) for k in ("left","witness","right")]
    a,b,c = pairs
    products = [[a[0]*b[1],a[1]*b[0]],[b[0]*c[1],b[1]*c[0]],[c[0]*a[1],c[1]*a[0]]]
    power = 1
    powers = []
    for index in range(3):
        power *= inputs["n"]
        powers.append(power)
    return {"measurement": {"left_below_witness": products[0][0]<products[0][1],
        "witness_below_right": products[1][0]<products[1][1], "n_squared": powers[1], "n_cubed": powers[2],
        "reversed_below": products[2][0]<products[2][1], "cross_products": products, "tail_products": [5*6,6*5]},
        "witness": {"rational_cross_products": products}}

def assess(inputs, m):
    return {"reversed_comparison_false": not m["reversed_below"],
            "both_tail_products_computed": m["tail_products"] == [5*6,6*5]}, {
        "witness_inside": (m["left_below_witness"] and m["witness_below_right"]) == inputs["predicted"]["witness_inside"],
        "n_squared": m["n_squared"] == inputs["predicted"]["n_squared"],
        "n_cubed": m["n_cubed"] == inputs["predicted"]["n_cubed"],
        "reversed_below": m["reversed_below"] == inputs["predicted"]["reversed_below"]}

