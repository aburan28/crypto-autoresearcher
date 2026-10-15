#!/usr/bin/env python3
"""EXP-ECDLP-8c41d7 launcher: m = 4 under the block elimination order.

Thin wrapper over EXP-ECDLP-20a588/block_order_grid.py (same arms, same
instruments, same controls); the only addition is the 5-point summation
polynomial
    S_5(x1..x4, xT) = Res_X( S_3(x1, x2, X), Res_Y( S_3(X, x3, Y), S_3(x4, xT, Y) ) ),
expanded once per instance by Singular in field arithmetic (untimed
preprocessing, identical input for every arm). A planted decomposition must
make S_5 vanish (checked before any solver runs; `s5_planted_zero`).
"""
import importlib.util, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "block_order_grid", os.path.join(HERE, "..", "EXP-ECDLP-20a588", "block_order_grid.py"))
bog = importlib.util.module_from_spec(_spec)
sys.modules["block_order_grid"] = bog          # workers are forked; pickle resolves run_instance through this name
_spec.loader.exec_module(bog)
pkm, msg = bog.pkm, bog.msg
_orig = msg.summation_poly


def summation_poly(p, m, a, b, xT):
    if m != 4:
        return _orig(p, m, a, b, xT)
    n = pkm.num
    S3 = pkm.S3
    s4 = ("resultant(" + S3.format(x1="X", x2="x3", x3="Y", a=n(a), b=n(b)) + ","
          + S3.format(x1="x4", x2=n(xT), x3="Y", a=n(a), b=n(b)) + ",Y)")
    s5 = "resultant(" + S3.format(x1="x1", x2="x2", x3="X", a=n(a), b=n(b)) + "," + s4 + ",X)"
    script = f"ring r0 = {p},(x1,x2,x3,x4,X,Y),dp;\npoly S = {s5};\nprint(string(S));\nquit;\n"
    out = subprocess.run(["Singular", "-q", "--no-rc"], input=script, capture_output=True, text=True, timeout=900)
    s = "".join(out.stdout.split())
    assert s and "X" not in s and "Y" not in s, out.stdout[:200] + out.stderr[:200]
    return s


msg.summation_poly = summation_poly

if __name__ == "__main__":
    bog.main()
