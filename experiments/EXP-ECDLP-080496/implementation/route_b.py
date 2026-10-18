"""Route b: x=1; then x=0,y=1; then (0:0:1). No sibling imports."""
def compute(inputs):
    q = inputs["p"]
    def normalize(triple):
        value = next(v % q for v in triple if v % q != 0)
        inverse = next(i for i in range(1,q) if i*value % q == 1)
        return tuple((a*inverse) % q for a in triple)
    accepted = []
    tested = 0
    for y in range(q):
        for z in range(q):
            tested += 1
            if (1+y*y*y+z*z*z) % q == (3*inputs["d"]*y*z) % q:
                accepted.append((1,y,z))
    for z in range(q):
        tested += 1
        if (1+z*z*z) % q == 0:
            accepted.append((0,1,z))
    tested += 1
    if 1 % q == 0:
        accepted.append((0,0,1))
    normalized = sorted({normalize(triple) for triple in accepted})
    return record(inputs, normalized, tested, len(accepted), normalize)

def record(inputs, points, candidates, accepted, normalize):
    p = inputs["p"]
    equation = lambda v: (sum(t*t*t for t in v) - 3*inputs["d"]*v[0]*v[1]*v[2]) % p == 0
    cycle = lambda v: normalize((v[1], v[2], v[0]))
    point_set = set(points)
    origin = normalize(inputs["O"])
    sigma_o = cycle(origin)
    tail = (0, 1, 0)
    measurement = {"point_count": len(points), "sigma_preserves_all": all(cycle(v) in point_set and equation(cycle(v)) for v in points),
        "sigma_cube_is_id": all(cycle(cycle(cycle(v))) == v for v in points),
        "fixed_points_of_sigma": sum(cycle(v) == v for v in points), "sigma_O": list(sigma_o),
        "identity_fixes_all": all(normalize(v) == v for v in points),
        "identity_fixed_points": sum(normalize(v) == v for v in points),
        "chart_size_before_normalize": accepted, "chart_candidates_tested": candidates,
        "tail_point_tested": True, "tail_point_on_curve": equation(tail)}
    return {"measurement": measurement, "witness": {"normalized_projective_points": [list(v) for v in points],
        "origin": list(origin), "tail_test_point": list(tail), "tail_residual": (sum(t*t*t for t in tail)-3*inputs["d"]*tail[0]*tail[1]*tail[2]) % p}}

def assess(inputs, m):
    predicted = inputs["predicted"]
    controls = {"identity_fixes_every_point": m["identity_fixes_all"],
                "tail_point_explicitly_tested": m["tail_point_tested"],
                "complete_projective_charts": m["chart_candidates_tested"] == inputs["p"] ** 2 + inputs["p"] + 1}
    prediction = {"point_count": m["point_count"] == predicted["point_count"],
                  "sigma_preserves_all": m["sigma_preserves_all"],
                  "sigma_cube_is_id": m["sigma_cube_is_id"],
                  "fixed_points": m["fixed_points_of_sigma"] == predicted["fixed_points"],
                  "sigma_O": m["sigma_O"] == predicted["sigma_O"]}
    return controls, prediction

