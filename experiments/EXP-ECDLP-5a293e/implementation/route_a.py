"""Route a: x-outer exhaustive affine listing. No sibling imports."""
def compute(inputs):
    p,A,B = inputs["p"],inputs["A"],inputs["B"]
    points = [(x,y) for x in range(p) for y in range(p) if (y*y-x*x*x-A*x-B) % p == 0]
    return record(inputs, points)

def record(inputs, points):
    p = inputs["p"]
    rows = []
    for x,y in points:
        negative = (x, (-y) % p)
        rows.append({"point": [x,y], "negative": list(negative),
                     "x": [x,negative[0]], "x_plus_1": [(x+1)%p,(negative[0]+1)%p], "y": [y,negative[1]]})
    measurement = {"affine_point_count": len(points),
        "x_mismatches": sum(r["x"][0] != r["x"][1] for r in rows),
        "x_plus_1_mismatches": sum(r["x_plus_1"][0] != r["x_plus_1"][1] for r in rows),
        "y_mismatches": sum(r["y"][0] != r["y"][1] for r in rows),
        "points_with_y_zero": sum(y == 0 for x,y in points),
        "all_y_zero_points_included": {x for x,y in points if y == 0} == {x for x in range(p) if (x*x*x+inputs["A"]*x+inputs["B"]) % p == 0}}
    return {"measurement": measurement, "witness": {"affine_points": [list(v) for v in points], "pointwise_map_values": rows}}
def assess(inputs, m):
    return {"y_is_noninvariant_control": m["y_mismatches"] != 0,
            "zero_y_point_included": m["all_y_zero_points_included"]}, {
            key: m[key] == value for key,value in inputs["predicted"].items()}

