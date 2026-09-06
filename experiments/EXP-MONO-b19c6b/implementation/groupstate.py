"""Per-curve group-state builder: point enumeration, Z/n1 x Z/n2 structure,
coordinate map, and factor-base construction, all keyed off curve.py.
Unchanged from EXP-MONO-c819ba's groupstate.py."""
from fields import ec_scal, ec_neg
from curve import (
    enumerate_points, group_structure, build_coordinate_map,
    factor_base_x_coords, ConstructionFailure,
)


class CurveState:
    def __init__(self, p, A, B):
        self.p = p
        self.A = A
        self.B = B
        self.points, self.sqrt_table = enumerate_points(A, B, p)
        self.N = len(self.points) + 1  # +1 for O
        gs = group_structure(self.points, self.N, A, p)
        self.n1, self.n2 = gs["n1"], gs["n2"]
        self.G1, self.G2 = gs["G1"], gs["G2"]
        self.orders = gs["orders"]
        self.factorization = gs["factorization"]
        self.point_to_coord, self.coord_grid = build_coordinate_map(
            self.points, self.N, A, p, self.n1, self.n2, self.G1, self.G2)
        fb_full, excluded_zero = factor_base_x_coords(A, B, p, self.sqrt_table)
        self.fb_full = fb_full
        self.excluded_zero = excluded_zero
        fbset = set(fb_full)
        self.fb_full_symmetric = all((x, (-y) % p) in fbset for (x, y) in fb_full)

    def coord(self, P):
        return self.point_to_coord[P]

    def coords_of(self, pts):
        return [self.point_to_coord[P] for P in pts]

    def scal_image_subgroup(self, k):
        img = set()
        img.add(None)
        for P in self.points:
            img.add(ec_scal(k, P, self.A, self.p))
        return img

    def negate(self, P):
        return ec_neg(P, self.p)
