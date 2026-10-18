"""Independent checker: integer factor accumulation and math.gcd."""
from math import gcd
def compute(inputs):
    n = inputs["n"]
    fractions,totals,proof = [],[],[]
    for row in inputs["cells"]:
        t,p = row["T"],row["P"]
        total = sum((t*p,t*t,1))
        divisor = gcd(total,n)
        fractions.append(f"{total//divisor}/{n//divisor}")
        totals.append(total)
        proof.append(dict(P_T=t*p,T_T=t*t,constant=1))
    leak = inputs["leak_claim"]
    num = sum((leak["P"]*leak["T"],pow(leak["T"],2),1))
    a,b = (int(x) for x in leak["claimed_success"].split("/"))
    divisor = gcd(num,n)
    return {"measurement": {"bound_by_cell": fractions, "numerator_by_cell": totals,
            "leak_label": ("above_floor" if a*n-num*b > 0 else "inside_bound")},
            "witness": {"cell_terms": proof, "leak_floor": f"{num//divisor}/{n//divisor}"}}
def assess(inputs, m):
    control = dict(leak_claim_above_floor=(m["leak_label"]=="above_floor"))
    predicted = [row["predicted"] for row in inputs["cells"]]
    return control, dict(bounds=(predicted==m["bound_by_cell"]))

