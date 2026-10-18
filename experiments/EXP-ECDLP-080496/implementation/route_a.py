"""Route a: z=1; then z=0,x=1; then (0:1:0). No sibling imports."""
def compute(inputs):
    p, d = inputs["p"], inputs["d"]
    def normalize(v):
        leading = next(t for t in v if t % p)
        inverse = pow(leading, p-2, p)
        return tuple(t*inverse % p for t in v)
    found, candidates = [], 0
    for z in (1, 0):
        if z:
            chart = ((x,y,1) for x in range(p) for y in range(p))
        else:
            chart = ((1,y,0) for y in range(p))
        for x,y,z0 in chart:
            candidates += 1
            if (x**3+y**3+z0**3-3*d*x*y*z0) % p == 0:
                found.append((x,y,z0))
    candidates += 1
    if 1 % p == 0:
        found.append((0,1,0))
    points = sorted(set(normalize(v) for v in found))
    return record(inputs, points, candidates, len(found), normalize)

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

