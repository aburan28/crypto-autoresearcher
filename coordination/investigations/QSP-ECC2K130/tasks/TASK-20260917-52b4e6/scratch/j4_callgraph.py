"""J4 (a): the ACTUAL call graph of I1, I2, I3 and verify_roots_f2, by static
analysis of the committed qspcore.py (ast, no execution)."""
import ast, sys
SRC="/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation/qspcore.py"
tree=ast.parse(open(SRC).read())
funcs={}
class V(ast.NodeVisitor):
    def visit_FunctionDef(self,node):
        calls=set()
        for x in ast.walk(node):
            if isinstance(x,ast.Call):
                f=x.func
                if isinstance(f,ast.Name): calls.add(f.id)
                elif isinstance(f,ast.Attribute): calls.add("K."+f.attr if isinstance(f.value,ast.Name) and f.value.id in("K","self") else f.attr)
        funcs[node.name]=calls
        self.generic_visit(node)
V().visit(tree)
LEAVES={"deg","clmul","square","polymod","polymod_sparse_tail","gcd","polydivmod",
        "compose","iterate","frob_power_mod","frob_power_mod_sparse","ddf_factor","_edf",
        "K.mul","K.sq","K.pow2k","K.eval_f2poly","kp_gcd","kp_sqmod","kp_mod","kp_mul"}
def closure(name, seen=None):
    if seen is None: seen=set()
    if name in seen or name not in funcs: return set()
    seen.add(name)
    out=set()
    for c in funcs[name]:
        if c in LEAVES: out.add(c)
        out |= closure(c, seen)
    return out
targets=["i1_brute_f2","_frob_table","_xpow_tables","_lam_table_f2","i2_gcd_f2",
         "i3_injection_f2","verify_roots_f2","c6_linearized_N","difference_poly_f2",
         "deg_D_and_degenerate","ddf_factor","kp_roots","f2_roots_in_K"]
res={t:sorted(closure(t)) for t in targets}
for t in targets: print("%-22s -> %s"%(t, ", ".join(res[t])))
print()
I1=set(res["i1_brute_f2"])|set(res["_frob_table"])|set(res["_xpow_tables"])|set(res["_lam_table_f2"])
I2=set(res["i2_gcd_f2"]); I3=set(res["i3_injection_f2"]); VR=set(res["verify_roots_f2"])
print("I1 primitive set:", sorted(I1))
print("I2 primitive set:", sorted(I2))
print("I3 primitive set:", sorted(I3))
print("verify_roots_f2 :", sorted(VR))
print()
print("SHARED by I1 & I2 & I3 :", sorted(I1&I2&I3))
print("SHARED by I2 & I3 only :", sorted((I2&I3)-I1))
print("I1-only                :", sorted(I1-I2-I3))
print("I3-only                :", sorted(I3-I1-I2))
print("verify_roots_f2 shares with I3:", sorted(VR&I3), " with I1:", sorted(VR&I1))
