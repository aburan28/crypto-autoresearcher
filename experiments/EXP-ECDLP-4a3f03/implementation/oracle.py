"""Independent checker: square-root table, equivalence closures and modular units."""
import math
def field(q,constant):
    squares={}
    for root in range(q):
        squares.setdefault(root*root%q,[]).append(root)
    points=sorted((a,b) for a in range(q) for b in squares.get((a**3+constant)%q,[]))
    roots=sorted({r for r in range(q) if r!=1 and r*r*r%q==1})
    pointset=set(points)
    beta_groups=set()
    sign_groups=set()
    for a,b in points:
        orbit=tuple(sorted({(a,b)}|{(a*r%q,b) for r in roots}))
        if not set(orbit)<=pointset:
            raise ValueError("beta equivalence leaves curve")
        beta_groups.add(orbit)
        sign_groups.add(tuple(sorted({(a,b),(a,(-b)%q)})))
    order=1+len(pointset)
    if math.gcd(order,q)!=1:
        degree=None; values=[q%order]
        why="noncoprime_base_and_order_no_positive_embedding_degree"
    else:
        values=[]; k=1
        while True:
            value=pow(q,k,order); values.append(value)
            if value==1:
                degree=k; break
            k+=1
            if k>order:
                raise ValueError("order bound violated")
        why="least_positive_exponent_verified"
    m=dict(p=q,B=constant,order=order,trace=q+1-order,nonidentity_points=len(points),
        beta_orbits=len(beta_groups),beta_factor=len(points)//len(beta_groups),
        sign_pairs=len(sign_groups),sign_factor=len(points)//len(sign_groups),difference=len(points)-len(beta_groups),
        embedding_degree=degree,embedding_reason=why,embedding_residues=values,
        p_power_minus_one_residue_if_noncoprime=((q-1)%order if degree is None and q%order==0 else None),
        gcd_order_pm1=math.gcd(order,q-1))
    w=dict(nonidentity_points=[list(v) for v in points],beta_roots=roots,
        beta_orbits=[[list(v) for v in group] for group in sorted(beta_groups)],
        sign_pairs=[[list(v) for v in group] for group in sorted(sign_groups)])
    return m,w
def compute(inputs):
    first,w1=field(inputs["field7"]["p"],inputs["field7"]["B"])
    second,w2=field(inputs["field13"]["p"],inputs["field13"]["B"])
    gap=inputs["alpha_numerators"][2]*3-inputs["alpha_denominators"][2]*2
    den=3*inputs["alpha_denominators"][2]; g=math.gcd(gap,den)
    return {"measurement":{"field7":first,"field13":second,"beta_factor":first["beta_factor"],
        "sign_factor":first["sign_factor"],"factor_product":first["beta_factor"]*first["sign_factor"],
        "trace7":first["trace"],"embed_degree13":second["embedding_degree"],"third_gap":f"{gap//g}/{den//g}",
        "grid_cells":len([(a,d) for a in inputs["alpha_numerators"] for d in inputs["depth_values"]]),
        "depth_product":math.prod(inputs["depth_values"])},"witness":{"field7":w1,"field13":w2}}
def assess(inputs,m):
    controls={"orbit_factor_not_difference_or_sign":m["beta_factor"]!=4 and m["beta_factor"]!=2,
        "trace_not_zero":m["trace7"]!=0,"embedding_degree_not_one":m["embed_degree13"]!=1,
        "third_alpha_not_two_thirds":m["third_gap"]!="0/1","grid_not_sum_of_counts":m["grid_cells"]!=10,
        "second_field_included":m["field13"]["p"]==inputs["field13"]["p"]}
    anticipated={"beta_factor":inputs["field7"]["beta_factor"],"sign_factor":inputs["field7"]["sign_factor"],
        "factor_product":inputs["field7"]["factor_product"],"trace7":inputs["field7"]["trace"],
        "embed_degree13":inputs["field13"]["embed_degree"],"third_gap":f"{inputs['third_gap_num']}/{inputs['third_gap_den']}",
        "grid_cells":inputs["grid_cells"],"depth_product":inputs["depth_product"]}
    compared={key: value==m[key] for key,value in anticipated.items()}
    compared["field13_beta_factor"]=m["field13"]["beta_factor"]==inputs["field13"]["beta_factor"]
    compared["field13_sign_factor"]=m["field13"]["sign_factor"]==inputs["field13"]["sign_factor"]
    return controls,compared

