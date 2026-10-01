"""Emit the explicit root lists as F_2 coefficient vectors of length 131.

Vector convention: position i of the 131-character string is the coefficient of
z^i in K = F_2[z]/(z^131+z^13+z^2+z+1).  (LSB-first, i.e. index == exponent.)
Each orbit is listed in Frobenius order x, x^2, x^4, ... starting from the
numerically smallest element of the orbit (canonical, seed-independent).
"""
import json, sys

data = json.load(open('../out/rederivation_results.json'))
for ent in data['attaining']:
    lam = ent['lambda_packed']
    path = f'../out/roots_lambda_{lam}.txt'
    with open(path, 'w') as fh:
        fh.write(f"# lambda = {ent['lambda']}  (bit-packed {lam} = 0b{lam:b})\n")
        fh.write(f"# K = F_2[z]/(z^131 + z^13 + z^2 + z + 1),  L = X^(2^33) - lambda(X)\n")
        fh.write(f"# N(lambda) = {ent['N']} distinct roots in K\n")
        fh.write("# each line: 131 characters, position i = coefficient of z^i\n")
        for o in ent['orbits']:
            fh.write(f"# --- Frobenius orbit of size {o['orbit_size']}, "
                     f"minimal polynomial over F_2 = {o['minpoly']}\n")
            for v, h in zip(o['roots_bits_lsb_first'], o['roots_hex']):
                assert len(v) == 131
                fh.write(f"{v}  {h}\n")
    n = sum(o['orbit_size'] for o in ent['orbits'])
    print(f'wrote {path}: {n} root vectors')
