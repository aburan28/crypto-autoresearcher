"""Software regression fixtures, not admitted experiment observations."""
import copy
import unittest

from arithmetic import Elliptic,Field,interpolate,pdiv,pmul
from independent import add,multiply,vandermonde,verify_fixture,verify_row
from relations import Context,Rank,uid


def planted_fixture():
    # x6+3-2²=(x²-1)(x²-7)(x²-11) in F19. All logs are
    # intentionally public in this SOFTWARE control, never the science panel.
    fixture={'p':19,'a':0,'b':3,'r':13,'P':[1,17],
             'factor_base':[{'point':[1,2],'lift':[1,2]},
                            {'point':[7,2],'lift':[8,2]},
                            {'point':[11,2],'lift':[7,2]}]}
    fixture['uid']=uid(fixture)
    return fixture


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

    def test_principal_witness_and_false_labels(self):
        fixture=planted_fixture()
        self.assertEqual(verify_fixture(fixture)['generator_order'],13)
        ctx=Context(fixture)
        descriptor,reason=ctx.descriptor(1,(0,1,2),(2,0,0))
        self.assertIsNone(reason)
        row,reason=ctx.construct(descriptor)
        self.assertIsNone(reason)
        self.assertTrue(verify_row(fixture,row))
        for field,value in [('source_scalar',2),('pole_orders_at_infinity',[2,3]),
                            ('coefficients',[0,0,0]),('source_locator','post-hoc K')]:
            invalid=copy.deepcopy(row);invalid[field]=value
            with self.assertRaises(ValueError):verify_row(fixture,invalid)

    def test_geometric_aliases_share_bucket_and_split(self):
        ctx=Context(planted_fixture())
        original,_=ctx.descriptor(1,(0,1,2),(2,0,0))
        deck=copy.deepcopy(original)
        deck['points']=[(-x%19,y) for x,y in deck['points']]
        self.assertEqual(ctx.canonical_identity(original),ctx.canonical_identity(deck))
        self.assertEqual(ctx.bucket(original),ctx.bucket(deck))


if __name__=='__main__':unittest.main()
