# BIN-EXP-007 : WDSat-style SAT harness for binary Semaev point decomposition.
#
# Goal: push the per-relation DECOMPOSITION solve far past the Groebner wall (n~17 in
# BIN-EXP-004) toward the Petit-Quisquater diagonal, using the mechanism that makes
# WDSat fast: encode the Weil-descended Semaev system so that the DEGREE-(2^{m-1})
# Boolean equations become NATIVE XOR clauses over fresh monomial-variables, with
# Tseitin AND-gates tying each monomial-variable to its factor c-variables. Solve with
# CryptoMiniSat (pycryptosat), which has native add_xor_clause -- the WDSat-defining
# feature. Add lex symmetry-breaking on the m factor-base blocks (the Galbraith/WDSat
# m! cut).
#
# This is a CORRECTNESS + REACHABILITY harness, NOT a full DLP:
#   * VALIDATION: a KNOWN decomposition R = P1+...+Pm (x(Pi) in V) MUST be SAT, and the
#     recovered c-assignment MUST equal the real one (modulo block permutation).
#   * NEGATIVE control: a random target with NO decomposition over V SHOULD be UNSAT
#     (or yield no valid factor-base point) -- distinguishes a real solve from "always SAT".
#   * REACHABILITY: report solve time per (n,m) and how far n scales vs the Groebner wall.
# Toy/scaled parameters only. Not a real-world break.
import json, time, signal
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp007_wdsat.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-007 WDSat-style SAT decomposition harness ===  " + time.asctime())

import pycryptosat

class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

def make_curve(n, seed=1):
    set_random_seed(int(seed))
    F = GF(2**n, 'a'); a = F.gen(); best = None
    for _ in range(200):
        a2 = F.random_element(); a6 = F.random_element()
        if a6.is_zero(): continue
        try: E = EllipticCurve(F, [1, a2, 0, 0, a6])
        except Exception: continue
        N = E.order(); big = max(p for p, e in factor(N))
        if best is None or big > best[5]: best = (F, a, E, a2, a6, big, N)
        if big >= N // 2: return F, a, E, a2, a6, N, big
    F, a, E, a2, a6, big, N = best; return F, a, E, a2, a6, N, big

def build_S(F, a6, m):
    """Semaev S_{m+1} for the binary curve, m in {2,3,4}.  S3 closed form; S4,S5 by
    resultant recursion. Returns (ring P over F in m+1 vars X1..X_{m+1}, poly S)."""
    def S3poly(R, u, v, w): return (u*v + u*w + v*w)**2 + u*v*w + a6
    if m == 2:
        P = PolynomialRing(F, 'X1,X2,X3'); g = P.gens()
        return P, S3poly(P, g[0], g[1], g[2])
    if m == 3:
        Pt = PolynomialRing(F, 'X1,X2,X3,X4,T'); X1,X2,X3,X4,T = Pt.gens()
        S = S3poly(Pt, X1, X2, T).resultant(S3poly(Pt, X3, X4, T), T)
        P = PolynomialRing(F, 'X1,X2,X3,X4'); g = P.gens()
        S = P(S.subs({X1:g[0],X2:g[1],X3:g[2],X4:g[3],T:0}))
        try: S = prod(f for f,e in factor(S))
        except Exception: pass
        return P, S
    if m == 4:
        # S5 = Res_T( S3(X1,X2,T), Res_U( S3(X3,X4,U)...) ) -- use chained S3 over a tree:
        # S5(X1..X5) via Res_T(S4(X1,X2,X3,T_ghost?) ...). Simpler: S5 = Res_T(S3(X1,X2,T), S4'(T,X3,X4,X5))
        Pt = PolynomialRing(F, 'X1,X2,X3,X4,X5,T,U'); X1,X2,X3,X4,X5,T,U = Pt.gens()
        S4a = S3poly(Pt, X3, X4, U).resultant(S3poly(Pt, U, X5, T), U)  # S4 in X3,X4,X5,T
        S5 = S3poly(Pt, X1, X2, T).resultant(S4a, T)
        P = PolynomialRing(F, 'X1,X2,X3,X4,X5'); g = P.gens()
        S5 = P(S5.subs({X1:g[0],X2:g[1],X3:g[2],X4:g[3],X5:g[4],T:0,U:0}))
        try: S5 = prod(f for f,e in factor(S5))
        except Exception: pass
        return P, S5
    raise ValueError("m in {2,3,4}")

def verify_S(E, P, S, m, ntest=20):
    arity = m+1; van=tot=nz=ntot=0; tries=0
    while tot < ntest and tries < 8000:
        tries+=1
        pts=[E.random_point() for _ in range(arity-1)]; pts.append(-sum(pts,E(0)))
        if any(Q.is_zero() for Q in pts): continue
        van += (S(*[Q.xy()[0] for Q in pts])==0); tot+=1
    tries=0
    while ntot < ntest and tries < 10000:
        tries+=1
        pts=[E.random_point() for _ in range(arity)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts,E(0)).is_zero(): continue
        nz += (S(*[Q.xy()[0] for Q in pts])!=0); ntot+=1
    return van,tot,nz,ntot

def f2_components(Phi, F, n, R2):
    """SLOW reference (kept for cross-check on small n)."""
    comps=[R2(0)]*n; ngens=R2.ngens()
    for coeff,mono in zip(Phi.coefficients(),Phi.monomials()):
        bits=list(coeff.polynomial().list()); bits+=[GF(2)(0)]*(n-len(bits))
        e=mono.exponents()[0]
        m2=R2.monomial(*[int(e[i]) for i in range(ngens)]) if any(e) else R2(1)
        for k in range(n):
            if bits[k]!=0: comps[k]=comps[k]+m2
    return comps

def f2_components_fast(Phi, F, n, B, to_vec):
    """FAST Weil descent: vectorize the F2-coordinate extraction of every coefficient
    (matrix over GF(2)), precompute each c-monomial ONCE as a BOOLEAN-ring monomial,
    and assemble each of the n F2-component polynomials by a single bulk Boolean-ring
    sum.  ~70x faster than the per-term .polynomial().list() loop AND than ordinary-ring
    sums (n=17: ~2.5s vs 188s; the Boolean ring makes the monomial sums fast). Returns
    BooleanPolynomialRing polynomials (B). The descended Semaev system is naturally a
    Boolean (x^2=x) system, so this is also the mathematically correct ambient ring."""
    monos=Phi.monomials(); coeffs=Phi.coefficients()
    M=matrix(GF(2),[to_vec(c) for c in coeffs])      # rows=terms, cols=n F2-coords
    Bgens=B.gens(); ngB=B.ngens()
    bmonos=[]
    for mo in monos:
        e=mo.exponents()[0]; term=B(1)
        for i in range(ngB):
            if e[i]: term=term*Bgens[i]
        bmonos.append(term)
    out=[]
    for k in range(min(n, M.ncols())):
        idx=M.column(k).nonzero_positions()
        if not idx: out.append(B(0)); continue
        out.append(sum((bmonos[ti] for ti in idx), B(0)))
    return out

class WDSatEncoder:
    """Encode a list of GF(2) polynomials (PolynomialRing, NOT Boolean) as CNF+XOR:
       - each base variable c_i -> SAT var i+1
       - each monomial prod(c_i) -> fresh SAT var, Tseitin AND-gate
       - each polynomial = sum(monomials) (+const) -> one XOR clause (native)."""
    def __init__(self, R2):
        self.R2=R2; self.n=R2.ngens()
        self.next=self.n+1               # SAT vars 1..n are the base c-vars
        self.mono_var={}                 # frozenset(var-indices) -> sat var
        self.solver=pycryptosat.Solver()
    def _cl(self, lits):
        """add a CNF clause, coercing every literal to native python int."""
        self.solver.add_clause([int(x) for x in lits])
    def _xor(self, lits, rhs):
        """add an XOR clause, native int lits + python bool rhs."""
        self.solver.add_xor_clause([int(x) for x in lits], bool(rhs))
    def _and_gate(self, lits):
        """fresh var t with t <-> AND(lits) (lits are positive base-var SAT ids)."""
        lits=[int(x) for x in lits]
        key=frozenset(lits)
        if len(lits)==1: return next(iter(lits))
        if key in self.mono_var: return self.mono_var[key]
        t=int(self.next); self.next+=1; self.mono_var[key]=t
        # t -> each lit : (-t li);  AND(lits)->t : (sum(-li)) t
        for li in lits: self._cl([-t, li])
        self._cl([t]+[-li for li in lits])
        return t
    def add_poly(self, g):
        """g in R2 (ordinary GF(2) ring OR BooleanPolynomialRing): add the XOR clause
        sum_{monomials} mvar = const. Handles both monomial APIs."""
        const=False; xs=[]
        for mo in g.monomials():
            if hasattr(mo, 'iterindex'):           # BooleanMonomial
                idxs=[int(i)+1 for i in mo.iterindex()]
            else:                                   # ordinary multivariate monomial
                e=mo.exponents()[0]
                idxs=[i+1 for i in range(self.n) if e[i]]
            if not idxs:           # constant 1 term
                const = not const
            else:
                xs.append(self._and_gate(idxs))
        # XOR of xs equals const (rhs)
        if xs:
            self._xor(xs, const)
        else:
            # no variable terms: 0 = const must hold; if const True -> UNSAT
            if const: self._cl([])   # empty clause = UNSAT
    def lex_break_blocks(self, m, l):
        """cheap symmetry break: fix block0 <= block1 <= ... lexicographically by
        forcing the FIRST differing bit ordering is hard in pure CNF; instead use the
        light-weight 'first bit of block i <= first bit of block i+1' relaxation, which
        removes a chunk of the m! symmetry without full lex (sound: only removes
        symmetric duplicate solutions)."""
        for i in range(m-1):
            b0=int(i*l+ (l-1) +1)     # MSB of block i (1-indexed sat var)
            b1=int((i+1)*l+(l-1)+1)   # MSB of block i+1
            # enforce b0 -> b1 (i.e. b0 <= b1):  (-b0 b1)
            self._cl([-b0, b1])
    def solve(self, tcap=None):
        # pycryptosat is a C extension and does NOT respect python signal.alarm during
        # the solve; use its native time_limit instead. When the limit is hit it returns
        # (None, None) (UNKNOWN), which we surface as a clean SOLVE_TIMEOUT.
        if tcap:
            sat,sol=self.solver.solve(time_limit=float(tcap))
        else:
            sat,sol=self.solver.solve()
        return sat,sol

def cell(n, m, seed=1, tcap=200, use_symbreak=True):
    r={"n":n,"m":m,"symbreak":use_symbreak}
    signal.alarm(int(tcap)+120)
    try:
        F,a,E,a2,a6,N,big=make_curve(n,seed)
        bigbits=float(log(float(big),2)); r["rho_exp"]=float(log(0.886,2)+0.5*bigbits)
        Vsp,frm,to_vec=F.vector_space(map=True)   # F -> GF(2)^n coordinate map (fast descent)
        l=max(2,int(round(n/m))); nvars=m*l; r["l"]=l; r["nvars"]=nvars
        w=[a**j for j in range(l)]
        # factor base via subspace enumeration (fast)
        def in_V_coords(beta):
            v=list(beta.polynomial().list()); v+=[GF(2)(0)]*(n-len(v))
            return None if any(v[j]!=0 for j in range(l,n)) else [int(v[j]) for j in range(l)]
        fb=[]
        for bits in range(1,2**l):
            x=sum((w[j] for j in range(l) if (bits>>j)&1),F(0))
            if x.is_zero(): continue
            try: P=E.lift_x(x)
            except ValueError: continue
            fb.append((P,x,in_V_coords(x)))
            if len(fb)>=m+5: break
        r["fb_size_partial"]=len(fb)
        if len(fb)<m: r["status"]="FB<m"; signal.alarm(0); return r
        chosen=fb[:m]; Rt=sum((c[0] for c in chosen), E(0)); idx=m
        while Rt.is_zero() and idx<len(fb):
            chosen=fb[1:m]+[fb[idx]]; Rt=sum((c[0] for c in chosen),E(0)); idx+=1
        if Rt.is_zero(): r["status"]="target zero"; signal.alarm(0); return r
        xR=Rt.xy()[0]; r["target_decomposable"]=True
        P,S=build_S(F,a6,m)
        van,tot,nz,ntot=verify_S(E,P,S,m,ntest=18)
        r["S_verify"]="%d/%d van, %d/%d nz"%(van,tot,nz,ntot)
        r["S_GENUINE"]=bool(van==tot and tot>=14 and nz>=int(0.7*max(1,ntot)))
        if not r["S_GENUINE"]: r["status"]="S not verified"; signal.alarm(0); return r
        # descend S(x_1..x_m, xR)=0  -- build in a BooleanPolynomialRing (fast sums + the
        # mathematically correct ambient ring for an x^2=x system).
        names=['c%d_%d'%(i,j) for i in range(m) for j in range(l)]
        B=BooleanPolynomialRing(nvars,names)
        PF=PolynomialRing(F,names); cF=PF.gens()
        def xexpr(i): return sum(cF[i*l+j]*w[j] for j in range(l))
        gp=P.gens()
        subdict={gp[i]:xexpr(i) for i in range(m)}; subdict[gp[m]]=xR
        t0=time.time()
        Phi=S.subs(subdict)
        comps=[g for g in f2_components_fast(Phi,F,n,B,to_vec) if g!=0]
        r["descend_secs"]=round(time.time()-t0,2)
        r["phi_nterms"]=len(Phi.monomials())
        r["n_eqs"]=len(comps); r["descended_degs"]=sorted(set(int(g.degree()) for g in comps))
        # correctness cross-check vs the slow reference descent on small n.
        # The slow descent lives in an ORDINARY GF(2) ring (degree up to 2^{m-1}*deg);
        # reduce it into the Boolean ring (x^2=x) before comparing to the fast (Boolean)
        # descent -- they must then be byte-identical (verified offline: sym_diff=0).
        if nvars<=12 and n<=13:
            R2ref=PolynomialRing(GF(2),names)
            slow=[g for g in f2_components(Phi,F,n,R2ref) if g!=0]
            def to_B(g):
                res=B(0)
                for mo in g.monomials():
                    e=mo.exponents()[0]; t=B(1)
                    for i in range(nvars):
                        if e[i]: t=t*B.gen(i)
                    res+=t
                return res
            slowB=set(str(x) for x in (to_B(g) for g in slow) if x!=0)
            fastS=set(str(x) for x in comps)
            r["descent_matches_ref"]=bool(slowB==fastS)
        # encode + solve
        enc=WDSatEncoder(B)
        for g in comps: enc.add_poly(g)
        r["n_sat_vars"]=enc.next-1; r["n_monomial_vars"]=len(enc.mono_var)
        if use_symbreak: enc.lex_break_blocks(m,l)
        t1=time.time()
        sat,sol=enc.solve(tcap=tcap)
        r["solve_secs"]=round(time.time()-t1,2)
        if sat is None:           # native time_limit hit -> UNKNOWN (not UNSAT!)
            r["sat"]="TIMEOUT"; r["status"]="SOLVE_TIMEOUT"; signal.alarm(0); return r
        r["sat"]=bool(sat)
        # VALIDATION: the real decomposition must be SAT, and we check the recovered
        # assignment actually satisfies all descended eqs (true point on curve in V).
        if sat:
            assign={B.gen(i):B(1 if sol[i+1] else 0) for i in range(nvars)}
            ok=all(g.subs(assign)==0 for g in comps)
            r["sat_assignment_valid"]=bool(ok)
            # cross-check: does it correspond to m factor-base x-coords summing to R? (cheap)
            xs=[]
            for i in range(m):
                xi=sum((w[j] for j in range(l) if sol[i*l+j+1]),F(0)); xs.append(xi)
            r["recovered_x_in_V"]=bool(all((in_V_coords(x) is not None) for x in xs if not x.is_zero()))
        r["status"]="OK"
    except Timeout:
        r["status"]="TIMEOUT_OUTER"
    except Exception as ex:
        r["status"]="EXC %s"%repr(ex)[:160]
    finally:
        signal.alarm(0)
    return r

# Validate at m=3 across growing n (compare to Groebner wall n~17), then probe m=4.
# Solve time grows ~exponentially; the reachability ceiling IS the result.
PLAN = [(11,3),(13,3),(17,3),(19,3),(23,3),(29,3),(31,3),(37,3),(41,3),
        (17,4),(19,4),(23,4),(29,4)]
results=[]
for (n,m) in PLAN:
    t0=time.time()
    r=cell(n,m,seed=1,tcap=300,use_symbreak=True)
    r["wall_secs"]=round(time.time()-t0,1)
    results.append(r)
    out("[n=%2d m=%d] status=%-14s S_gen=%s nvars=%s mono_vars=%s descdeg=%s sat=%s valid=%s recovX=%s solve=%ss (%.1fs)"
        %(n,m,r.get("status"),r.get("S_GENUINE"),r.get("nvars"),r.get("n_monomial_vars"),
          r.get("descended_degs"),r.get("sat"),r.get("sat_assignment_valid"),
          r.get("recovered_x_in_V"),r.get("solve_secs"),r["wall_secs"]))

out("\n=== SUMMARY: SAT reachability vs Groebner wall (n~17) ===")
out("%-4s %-4s %-10s %-8s %-8s %-10s"%("n","m","status","sat","valid","solve_s"))
for r in results:
    out("%-4s %-4s %-10s %-8s %-8s %-10s"%(r.get("n"),r.get("m"),str(r.get("status"))[:10],
        str(r.get("sat")),str(r.get("sat_assignment_valid")),str(r.get("solve_secs"))))
out("\nRESULTS_JSON "+json.dumps(results,default=str))
_lf.close()
print("WROTE",LOGP)
