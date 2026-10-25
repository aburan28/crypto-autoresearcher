"""Route b: y-outer census; partition by cubic fibres and sign representative."""
def field(p,B):
    points=[]
    for y in range(p):
        for x in range(p):
            if (x*x*x+B)%p==y*y%p:
                points.append((x,y))
    points.sort()
    roots=[v for v in range(2,p) if (v*v+v+1)%p==0]
    if not roots:
        raise ValueError("no order-three root")
    cubic={}
    for x,y in points:
        cubic.setdefault((y,pow(x,3,p)),[]).append((x,y))
    orbits=sorted(sorted(group) for group in cubic.values())
    signs={}
    for x,y in points:
        key=(x,min(y,(-y)%p))
        signs.setdefault(key,[]).append((x,y))
    sign_groups=sorted(sorted(group) for group in signs.values())
    n=1+len(points)
    x,y=p,n
    while y:
        x,y=y,x%y
    if x>1:
        degree=None; residues=[p%n]; reason="noncoprime_base_and_order_no_positive_embedding_degree"
    else:
        residue=1; residues=[]; degree=None; seen=set()
        while residue not in seen:
            seen.add(residue); residue=residue*p%n; residues.append(residue)
            if residue==1:
                degree=len(residues); break
        if degree is None:
            raise ValueError("unit order did not return to one")
        reason="least_positive_exponent_verified"
    x,y=n,p-1
    while y:
        x,y=y,x%y
    row={"p":p,"B":B,"order":n,"trace":p+1-n,"nonidentity_points":len(points),
        "beta_orbits":len(orbits),"beta_factor":len(points)//len(orbits),"sign_pairs":len(sign_groups),
        "sign_factor":len(points)//len(sign_groups),"difference":len(points)-len(orbits),
        "embedding_degree":degree,"embedding_reason":reason,"embedding_residues":residues,
        "p_power_minus_one_residue_if_noncoprime":(p-1)%n if degree is None and p%n==0 else None,
        "gcd_order_pm1":x}
    return row,{"nonidentity_points":[list(v) for v in points],"beta_roots":roots,
        "beta_orbits":[[list(v) for v in group] for group in orbits],
        "sign_pairs":[[list(v) for v in group] for group in sign_groups]}
def compute(inputs):
    fields={}; witness={}
    for name in ("field7","field13"):
        fields[name],witness[name]=field(inputs[name]["p"],inputs[name]["B"])
    numerator=3*inputs["alpha_numerators"][2]-2*inputs["alpha_denominators"][2]
    denominator=3*inputs["alpha_denominators"][2]
    u,v=abs(numerator),denominator
    while v:
        u,v=v,u%v
    depths=inputs["depth_values"]
    product=1
    for value in depths:
        product=product*value
    first=fields["field7"]
    measurement=dict(fields)
    measurement.update(beta_factor=first["beta_factor"],sign_factor=first["sign_factor"],
        factor_product=first["beta_factor"]*first["sign_factor"],trace7=first["trace"],
        embed_degree13=fields["field13"]["embedding_degree"],third_gap=f"{numerator//u}/{denominator//u}",
        grid_cells=sum(len(depths) for _ in inputs["alpha_numerators"]),depth_product=product)
    return {"measurement":measurement,"witness":witness}

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

