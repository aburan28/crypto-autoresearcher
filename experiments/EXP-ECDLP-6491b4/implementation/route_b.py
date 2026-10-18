"""Arithmetic route b: integer products and Euclidean normalization; no imports."""
def reduce_pair(a,b):
    if b <= 0:
        raise ValueError("positive denominator required")
    x,y = abs(a),b
    while y:
        x,y = y,x%y
    return str(a//x)+"/"+str(b//x)
def compute(inputs):
    denominator = inputs["n"]
    out,totals,parts = [],[],[]
    for cell in inputs["cells"]:
        cross = cell["P"] * cell["T"]
        square = cell["T"] * cell["T"]
        total = 1 + square + cross
        totals.append(total)
        out.append(reduce_pair(total,denominator))
        parts.append({"P_T": cross, "T_T": square, "constant": 1})
    leak = inputs["leak_claim"]
    a,b = map(int,leak["claimed_success"].split("/"))
    numerator = 1+leak["T"]*(leak["T"]+leak["P"])
    label = "above_floor" if a*denominator > b*numerator else "inside_bound"
    return {"measurement": {"bound_by_cell": out, "numerator_by_cell": totals, "leak_label": label},
            "witness": {"cell_terms": parts, "leak_floor": reduce_pair(numerator,denominator)}}

def assess(inputs, m):
    return {"leak_claim_above_floor": m["leak_label"] == "above_floor"}, {
        "bounds": m["bound_by_cell"] == [cell["predicted"] for cell in inputs["cells"]]}

