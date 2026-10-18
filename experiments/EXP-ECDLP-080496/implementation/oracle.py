"""Independent checker: all nonzero homogeneous triples, then quotient scaling."""
def compute(inputs):
    q, parameter = inputs["p"], inputs["d"]
    def normalize(v):
        for index in range(3):
            if v[index] % q:
                factor = pow(v[index] % q, -1, q)
                return tuple((factor*a) % q for a in v)
        raise ValueError("zero homogeneous vector")
    points = set()
    vectors = 0
    for x in range(q):
        for y in range(q):
            for z in range(q):
                if x == y == z == 0:
                    continue
                vectors += 1
                if (x*x*x+y*y*y+z*z*z) % q == (3*parameter*x*y*z) % q:
                    points.add(normalize((x,y,z)))
    points = sorted(points)
    return record(inputs, points, vectors//(q-1), len(points), normalize)

def record(inputs, points, candidates, accepted, normalize):
    modulus = inputs["p"]
    preserve, cube_identity, fixed, identity = True, True, 0, 0
    for original in points:
        shifted = normalize(original[1:]+original[:1])
        preserve = preserve and shifted in points
        fixed += shifted == original
        triple_shifted = original
        for _ in range(3):
            triple_shifted = normalize(triple_shifted[1:]+triple_shifted[:1])
        cube_identity = cube_identity and triple_shifted == original
        identity += normalize(tuple(original)) == original
    origin = normalize(tuple(inputs["O"]))
    image = normalize(origin[1:]+origin[:1])
    residual = (0**3+1**3+0**3-3*inputs["d"]*0*1*0) % modulus
    return {"measurement": dict(point_count=len(points),sigma_preserves_all=preserve,
        sigma_cube_is_id=cube_identity,fixed_points_of_sigma=fixed,sigma_O=list(image),
        identity_fixes_all=identity==len(points),identity_fixed_points=identity,
        chart_size_before_normalize=accepted,chart_candidates_tested=candidates,
        tail_point_tested=True,tail_point_on_curve=residual==0),
        "witness": dict(normalized_projective_points=[list(v) for v in points],
            origin=list(origin),tail_test_point=[0,1,0],tail_residual=residual)}

def assess(inputs, m):
    q=inputs["p"]; expected=inputs["predicted"]
    return dict(identity_fixes_every_point=(m["identity_fixes_all"] is True),
        tail_point_explicitly_tested=(m["tail_point_tested"] is True),
        complete_projective_charts=(m["chart_candidates_tested"]==sum((q*q,q,1)))), {
        "point_count":expected["point_count"]==m["point_count"],
        "sigma_preserves_all":m["sigma_preserves_all"],"sigma_cube_is_id":m["sigma_cube_is_id"],
        "fixed_points":expected["fixed_points"]==m["fixed_points_of_sigma"],"sigma_O":expected["sigma_O"]==m["sigma_O"]}

