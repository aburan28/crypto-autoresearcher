"""Algebraic software controls; no retained-curve shift search or collector."""
import pytest

from crypto_autoresearcher.index_calculus.cover_frames import ShiftedCover
from crypto_autoresearcher.index_calculus.curve import Curve


@pytest.mark.parametrize('h',[0,1,2,3])
def test_both_quotients_and_complete_affine_lifts_on_marked_small_curve(h):
    p,a,b = 101,2,3
    frame,curve = ShiftedCover(p,a,b,h),Curve(p,a,b)
    for x in range(p):
        assert sum(c*pow(x,j,p) for j,c in enumerate(frame.polynomial)) % p == frame.rhs(x)
    for u in range(p):
        point = curve.lift_x(u)
        if point is None:continue
        lifts = frame.lifts(point)
        assert lifts == tuple((x,point[1]) for x in range(p) if x*x % p == (u-h) % p)
        for lift in lifts:
            assert frame.image(lift) == point
            X,Y = lift
            for deck in (1,-1):
                for sign in (1,-1):
                    transformed = (deck*X % p,sign*Y % p)
                    assert frame.is_on_cover(transformed)
                    assert frame.image(transformed) == (u,sign*point[1] % p)
            auxiliary = frame.auxiliary_image(lift)
            if X == 0:
                assert auxiliary is None and len(lifts) == 1
            else:
                U,V = auxiliary
                c2,c1,c0 = frame.auxiliary_coefficients
                assert V*V % p == (U**3+c2*U*U+c1*U+c0) % p
    assert frame.lifts(None) == ()


def test_historical_frame_and_refusals():
    frame = ShiftedCover(101,2,21,0)
    assert frame.polynomial == (21,0,2,0,0,0,1)
    assert frame.auxiliary_coefficients == (2,0,21**2 % 101)
    with pytest.raises(ValueError,match='singular even sextic'):
        ShiftedCover(101,2,0,0)
    with pytest.raises(ValueError,match='singular curve'):
        ShiftedCover(101,0,0,1)
    with pytest.raises(ValueError,match='prime characteristic'):
        ShiftedCover(25,2,3,0)
    with pytest.raises(ValueError,match='not on'):
        frame.image((0,0))
    with pytest.raises(ValueError,match='not on'):
        frame.lifts((0,0))
