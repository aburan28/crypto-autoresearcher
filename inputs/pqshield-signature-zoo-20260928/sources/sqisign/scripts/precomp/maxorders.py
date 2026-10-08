from sage.all import *

from sage.misc.banner import require_version
if not require_version(10, 5, print_message=True):
    exit('')

from parameters import p

################################################################

# Underlying theory:
# - Ibukiyama, On maximal orders of division quaternion algebras with certain optimal embeddings
# - https://ia.cr/2023/106 Lemma 10

from sage.algebras.quatalg.quaternion_algebra import basis_for_quaternion_lattice
bfql = lambda els: basis_for_quaternion_lattice(els, reverse=True)

Quat1, (i,j,k) = QuaternionAlgebra(-1, -p).objgens()
assert Quat1.discriminant() == p         # ramifies correctly

O0mat = matrix([list(g) for g in [Quat1(1), i, (i+j)/2, (1+k)/2]])
O0 = Quat1.quaternion_order(list(O0mat))

orders = [ (1, identity_matrix(QQ,4), O0mat, i, O0mat, vector((1,0,0,0))) ]
