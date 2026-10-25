"""Arithmetic route a: fractions.Fraction; no sibling imports."""
from fractions import Fraction
def compute(inputs):
    values,numerators,terms = [],[],[]
    for cell in inputs["cells"]:
        P,T = cell["P"],cell["T"]
        numerator = P*T + T*T + 1
        fraction = Fraction(numerator,inputs["n"])
        values.append(str(fraction.numerator)+"/"+str(fraction.denominator))
        numerators.append(numerator)
        terms.append({"P_T": P*T, "T_T": T*T, "constant": 1})
    leak = inputs["leak_claim"]
    floor = Fraction(leak["P"]*leak["T"]+leak["T"]**2+1,inputs["n"])
    claim = Fraction(leak["claimed_success"])
    return {"measurement": {"bound_by_cell": values, "numerator_by_cell": numerators,
                "leak_label": "above_floor" if claim > floor else "inside_bound"},
            "witness": {"cell_terms": terms, "leak_floor": str(floor.numerator)+"/"+str(floor.denominator)}}

def assess(inputs, m):
    return {"leak_claim_above_floor": m["leak_label"] == "above_floor"}, {
        "bounds": m["bound_by_cell"] == [cell["predicted"] for cell in inputs["cells"]]}

