"""Route a: exhaustive affine census and repeated beta-map orbit walks."""
from math import gcd
def field(p,B):
    points=sorted((x,y) for x in range(p) for y in range(p) if (y*y-x*x*x-B)%p==0)
    roots=[v for v in range(2,p) if pow(v,3,p)==1]
    if not roots:
        raise ValueError("field has no nontrivial cube root of unity")
    beta=roots[0]
    remaining=set(points); orbits=[]
    while remaining:
        start=min(remaining); orbit=[]; v=start
        while v not in orbit:
            orbit.append(v); v=(beta*v[0]%p,v[1])
        if v!=start or not set(orbit)<=set(points):
            raise ValueError("map walk failed to close on curve")
        remaining-=set(orbit); orbits.append(sorted(orbit))
    signs=set()
    for x,y in points:
        signs.add(tuple(sorted(((x,y),(x,-y%p)))))
    n=len(points)+1
    if gcd(p,n)>1:
        degree=None; residues=[p%n]; reason="noncoprime_base_and_order_no_positive_embedding_degree"
    else:
        residues=[]
        for k in range(1,n+1):
            residues.append(pow(p,k,n))
            if residues[-1]==1:
                degree=k; break
        else:
            raise ValueError("unit-group order search unexpectedly exhausted")
        reason="least_positive_exponent_verified"
    row={"p":p,"B":B,"order":n,"trace":p+1-n,"nonidentity_points":len(points),
        "beta_orbits":len(orbits),"beta_factor":len(points)//len(orbits),"sign_pairs":len(signs),
        "sign_factor":len(points)//len(signs),"difference":len(points)-len(orbits),
        "embedding_degree":degree,"embedding_reason":reason,"embedding_residues":residues,
        "p_power_minus_one_residue_if_noncoprime":(p-1)%n if degree is None and p%n==0 else None,
        "gcd_order_pm1":gcd(n,p-1)}
    proof={"nonidentity_points":[list(v) for v in points],"beta_roots":roots,"beta_orbits":[[list(v) for v in group] for group in sorted(orbits)],
           "sign_pairs":[[list(v) for v in group] for group in sorted(signs)]}
    return row,proof

def compute(inputs):
    from fractions import Fraction
    fields,proof = {},{}
    for key in ("field7","field13"):
        row,certificate = field(inputs[key]["p"],inputs[key]["B"])
        fields[key],proof[key] = row,certificate
    a=Fraction(inputs["alpha_numerators"][2],inputs["alpha_denominators"][2])-Fraction(2,3)
    product=1
    for depth in inputs["depth_values"]:
        product*=depth
    f=fields["field7"]
    return {"measurement": {**fields,"beta_factor":f["beta_factor"],"sign_factor":f["sign_factor"],
        "factor_product":f["beta_factor"]*f["sign_factor"],"trace7":f["trace"],
        "embed_degree13":fields["field13"]["embedding_degree"],"third_gap":f"{a.numerator}/{a.denominator}",
        "grid_cells":len(inputs["alpha_numerators"])*len(inputs["depth_values"]),"depth_product":product},
        "witness":proof}

def assess(inputs,m):
    return {"orbit_factor_not_difference_or_sign": m["beta_factor"] not in (4,2),
            "trace_not_zero": m["trace7"] != 0, "embedding_degree_not_one": m["embed_degree13"] != 1,
            "third_alpha_not_two_thirds": m["third_gap"] != "0/1", "grid_not_sum_of_counts": m["grid_cells"] != 10,
            "second_field_included": m["field13"]["p"] == inputs["field13"]["p"]}, {
        "beta_factor": m["beta_factor"] == inputs["field7"]["beta_factor"],
        "sign_factor": m["sign_factor"] == inputs["field7"]["sign_factor"],
        "factor_product": m["factor_product"] == inputs["field7"]["factor_product"],
        "trace7": m["trace7"] == inputs["field7"]["trace"], "embed_degree13": m["embed_degree13"] == inputs["field13"]["embed_degree"],
        "third_gap": m["third_gap"] == f"{inputs['third_gap_num']}/{inputs['third_gap_den']}",
        "grid_cells": m["grid_cells"] == inputs["grid_cells"], "depth_product": m["depth_product"] == inputs["depth_product"],
        "field13_beta_factor": m["field13"]["beta_factor"] == inputs["field13"]["beta_factor"],
        "field13_sign_factor": m["field13"]["sign_factor"] == inputs["field13"]["sign_factor"]}

