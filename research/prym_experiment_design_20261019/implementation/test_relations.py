"""Software regression fixtures, not admitted experiment observations."""
import copy
import unittest

from arithmetic import Elliptic,Field,interpolate,pdiv,pmul
from independent import add,multiply,vandermonde
from relations import Rank


class ArithmeticTests(unittest.TestCase):
    def test_independent_laws_and_interpolation(self):
        f=Field(101);e=Elliptic(f,0,2,1);P=(1,2)
        for scalar in [0,1,2,3,17,-9]:
            self.assertEqual(e.mul(scalar,P),multiply(101,0,2,scalar,P))
        points=[(0,3),(1,9),(2,5),(3,44)]
        self.assertEqual(interpolate(f,points),vandermonde(101,points))
        a=[7,2,9];b=[2,1];product=pmul(f,a,b)
        self.assertEqual(pdiv(f,product,b),(a,[0]))

    def test_affine_rank_and_inconsistency(self):
        r=Rank(2,101)
        self.assertTrue(r.add([1,1],8))
        self.assertTrue(r.add([2,1],11))
        self.assertEqual(r.solve(),[3,5])
        self.assertFalse(r.add([3,2],19))
        with self.assertRaises(ArithmeticError):r.add([3,2],20)


if __name__=='__main__':unittest.main()
