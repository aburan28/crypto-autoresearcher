"""Independent checker: residue-indexed square roots and cubic image."""
def compute(inputs):
    q = inputs["p"]
    roots = {}
    for residue in range(q):
        roots.setdefault(pow(residue,2,q),[]).append(residue)
    points = []
    for coordinate in range(q):
        rhs = (pow(coordinate,3,q)+inputs["A"]*coordinate+inputs["B"]) % q
        points.extend((coordinate,root) for root in roots.get(rhs,[]))
    return record(inputs, sorted(points))

def record(inputs, points):
    modulus=inputs["p"]; rows=[]; mismatch=[0,0,0]; zeros=0
    for coordinate, ordinate in points:
        opposite = (modulus-ordinate) % modulus
        before=(coordinate,(coordinate+1)%modulus,ordinate)
        after=(coordinate,(coordinate+1)%modulus,opposite)
        for i in range(3):
            mismatch[i] += before[i] != after[i]
        zeros += ordinate == 0
        rows.append(dict(point=[coordinate,ordinate],negative=[coordinate,opposite],
            x=[before[0],after[0]],x_plus_1=[before[1],after[1]],y=[before[2],after[2]]))
    return {"measurement":dict(affine_point_count=len(rows),x_mismatches=mismatch[0],
        x_plus_1_mismatches=mismatch[1],y_mismatches=mismatch[2],points_with_y_zero=zeros,
        all_y_zero_points_included=(zeros==len([a for a in range(modulus) if (pow(a,3,modulus)+inputs["A"]*a+inputs["B"])%modulus==0]))),
        "witness":dict(affine_points=[list(v) for v in points],pointwise_map_values=rows)}
def assess(inputs, m):
    controls=dict(y_is_noninvariant_control=bool(m["y_mismatches"]),zero_y_point_included=m["all_y_zero_points_included"])
    compared={key: expected==m[key] for key,expected in inputs["predicted"].items()}
    return controls,compared

