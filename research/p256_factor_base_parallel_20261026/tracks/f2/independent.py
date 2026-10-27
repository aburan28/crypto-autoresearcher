"""Separate Jacobian point-sum/coset checker; no producer arithmetic imports."""
P = 2**256 - 2**224 + 2**192 + 2**96 - 1
B = int("5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b", 16)
R = int("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 16)
INF = (1, 1, 0)


def tick(counts, name, n=1):
    if counts is not None:
        counts[name] = counts.get(name, 0)+n


def on_curve(point, a=-3, b=B):
    return point is None or (point[1]**2-point[0]**3-a*point[0]-b) % P == 0


def lift(point):
    return INF if point is None else (point[0], point[1], 1)


def negative(point):
    return None if point is None else (point[0], (-point[1]) % P)


def double(point, a, counts=None):
    tick(counts, "jacobian_double_calls")
    x, y, z = point
    if not z or not y:
        return INF
    xx, yy = x*x % P, y*y % P
    yyyy = yy*yy % P
    zz = z*z % P
    s = 2*((x+yy)**2-xx-yyyy) % P
    m = (3*xx+a*zz*zz) % P
    nx = (m*m-2*s) % P
    return nx, (m*(s-nx)-8*yyyy) % P, ((y+z)**2-yy-zz) % P


def plus(left, right, a=-3, counts=None):
    tick(counts, "jacobian_add_calls")
    x1, y1, z1 = left
    x2, y2, z2 = right
    if not z1:
        return right
    if not z2:
        return left
    z11, z22 = z1*z1 % P, z2*z2 % P
    u1, u2 = x1*z22 % P, x2*z11 % P
    s1, s2 = y1*z2*z22 % P, y2*z1*z11 % P
    if u1 == u2:
        return double(left, a, counts) if s1 == s2 else INF
    h, rr = (u2-u1) % P, (s2-s1) % P
    hh = h*h % P
    hhh = h*hh % P
    v = u1*hh % P
    nx = (rr*rr-hhh-2*v) % P
    return nx, (rr*(v-nx)-s1*hhh) % P, h*z1*z2 % P


def affine(point, counts=None):
    x, y, z = point
    if not z:
        return None
    tick(counts, "jacobian_normalization_inversions")
    inv = pow(z, -1, P)
    inv2 = inv*inv % P
    return x*inv2 % P, y*inv2*inv % P


def scalar(n, point, a=-3, counts=None):
    if n < 0:
        return scalar(-n, negative(point), a, counts)
    value = INF
    for bit in bin(n)[2:]:
        value = double(value, a, counts)
        if bit == "1":
            value = plus(value, lift(point), a, counts)
    return value


def solve_three(target, points, counts=None):
    """Independent complement traversal, not the producer's pair-sum table."""
    if target is None or not on_curve(target):
        raise ValueError("oracle target is not a nonzero target-curve point")
    lookup = {point: index for index, point in enumerate(points)}
    if len(lookup) != len(points) or not all(on_curve(point) for point in points):
        raise ValueError("oracle base is invalid")
    answers = set()
    for i, point in enumerate(points):
        residual = plus(lift(target), lift(negative(point)), counts=counts)
        for j in range(i, len(points)):
            tick(counts, "oracle_pair_states")
            third = affine(plus(residual, lift(negative(points[j])), counts=counts), counts)
            k = lookup.get(third)
            if k is not None and k >= j:
                answers.add((i, j, k))
    return sorted(answers)


def verify_solution(target, points, triple, counts=None):
    total = INF
    for index in triple:
        total = plus(total, lift(points[index]), counts=counts)
    return affine(total, counts) == target


def replay_coset(rows, compact, counts=None):
    """Reconstruct every coset point and every lift/rejection independently."""
    offset = tuple(compact["generic_offset"])
    kernel = tuple(compact["kernel_generator"])
    size = compact["degree"]
    if not (on_curve(offset, 1, 0) and on_curve(kernel, 1, 0)):
        raise ValueError("auxiliary input point not on the auxiliary curve")
    if scalar(size, kernel, 1, counts)[2] or not scalar(size//2, kernel, 1, counts)[2]:
        raise ValueError("kernel generator order is not the specified power of two")
    current = lift(offset)
    unique = set()
    accepted = rejected = seen = 0
    for row in rows:
        actual = affine(current, counts)
        if row["index"] != seen or actual is None or [*actual] != row["auxiliary_point"]:
            raise ValueError("coset recurrence/index certificate differs")
        x = row["x"]
        if actual[0] != x or x in unique or not on_curve(actual, 1, 0):
            raise ValueError("duplicate x or invalid auxiliary coordinate")
        unique.add(x)
        value = (x*x*x-3*x+B) % P
        target = row["target_point"]
        if target is None:
            tick(counts, "oracle_euler_exponentiations")
            if pow(value, (P-1)//2, P) != P-1:
                raise ValueError("rejected target coordinate is not a nonsquare")
            rejected += 1
        else:
            target = tuple(target)
            if target[0] != x or not on_curve(target) or not (0 < target[1] <= P//2):
                raise ValueError("accepted target lift/normalization invalid")
            accepted += 1
        seen += 1
        tick(counts, "coset_rows_replayed")
        current = plus(current, lift(kernel), 1, counts)
    if seen != size or len(unique) != size or affine(current, counts) != offset:
        raise ValueError("coset incomplete or not closed")
    return {"rows": seen, "accepted": accepted, "rejected": rejected,
            "closed": True, "distinct_x": len(unique),
            "subgroup_basis": "certified target total order r; individual [r] tests not performed"}
