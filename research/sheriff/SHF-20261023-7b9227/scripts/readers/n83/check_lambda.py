"""Closure exactness premise: lambda^2 - lambda + 2 = 0 mod r and Frobenius acts as [lambda] on <G>."""
import importlib.util, sys, json
spec = importlib.util.spec_from_file_location('vs', sys.argv[1]); 
src = open(sys.argv[1]).read().split("d = sys.argv[1]")[0]; ns = {}; exec(src, ns)
r = ns['r']; G = ns['G']; lam = 2998004823950457
phiG = (ns['sq'](G[0]), ns['sq'](G[1]))
print(json.dumps(dict(lambda_char_poly_zero=(lam * lam - lam + 2) % r == 0, frobenius_is_lambda_on_G=ns['smul'](lam, G) == phiG,
                      alpha_3_plus_2tau=ns['add'](ns['smul'](3, G), ns['smul'](2, phiG)) == ns['smul']((3 + 2 * lam) % r, G))))
