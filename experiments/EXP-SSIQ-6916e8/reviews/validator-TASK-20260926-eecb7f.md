# Validator report: TASK-20260926-eecb7f (EXP-SSIQ-6916e8, H-SSIQ-a9df38)

Reviewer role: Validator (policy requested `review-adversarial`), independent
session. This is the only repository file this reviewer writes (card
`write_scope`). No ledger record, run file, or knowledge entry is modified. No
run is launched and no RUN-* is minted.

## Section A: blind re-derivation (Phase A)

**Section A UTC write time: 2026-09-26T03:23:51Z** (taken with `date -u` immediately
before this section was written to the report path. The scratch session started
at 2026-09-26T03:18:42Z. The last scratch output was produced at 2026-09-26T03:21:59Z.)

**Phase A sources.** (1) `ledger/handoffs/TASK-20260926-eecb7f.yaml`, lines
1-330 only (line 330 is the marker line). One `Grep` for the marker string
returned lines 10, 320 and 330, all at or above the marker. (2) My own knowledge,
with every such input marked `recalled` below. (3) My own scratch code and its
output in the session scratch directory
`/tmp/claude-0/-home-user/5af2d3d8-0ba3-5d96-b05f-205cb058efcf/scratchpad/validator-eecb7f/`.
I read no other repository path, including `AGENTS.md` and `agents/validator.md`.
I used no MCP and no git. Disclosure: the harness auto-injected the
repository's `CLAUDE.md` into my context at session start. It is a generic
runtime file that states nothing about EXP-SSIQ-6916e8 or its quantities, and I
did not open it.

Frozen Gram convention (card): `A_ii = q(e_i)`, `A_ij = (q(e_i+e_j)-q(e_i)-q(e_j))/2`, `det = det(A)`.

### Results (blind)

| quantity | blind value | numeric check |
| --- | --- | --- |
| Q1 `det(O, Nrd)` | **p^2/16**, for every prime p including p = 2 (so 1/4 at p = 2) | exact match for 2 independently built maximal orders at each of p = 2, 3, 5, 13, 17, 1 at p0 = 9223372036854775907, and the 26 further maximal orders `conj(I)I/n(I)` built from the Q2 ideals (19 of them are lattices different from O) |
| Q2 `[O : I]` | **n(I)^2** | exact match for 26 left ideals: 8 at p = 2, 9 at p = 13, 9 at p0. They include composite norms 6, 35, 4, 15, 330, 36 and a 20-digit principal norm, plus the two-sided P |
| Q3 `det(P^0, Nrd/p)` | **p/4**, for every prime p including p = 2 (so 1/2 at p = 2) | exact match at p = 2, 3, 5, 13, 17, p0 (11 orders) |

### Recalled inputs (pointers, not support)

- R1 `recalled`: `B_{p,inf}` is definite, so `Nrd` is positive definite. For
  my presentations `(a,b)` with `a,b<0`, the ramification set `{p, inf}` was
  checked with PARI `hilbert()` over the primes dividing `2ab` (output below).
- R2 `recalled`, and elementary: `Nrd(x) = x*conj(x)`, so
  `Nrd(x+y)-Nrd(x)-Nrd(y) = Trd(x*conj(y))`. It was checked on random elements
  in `sanity()`.
- R3 `recalled`: maximality of a Z-order is local. For l != p, `B_l = M_2(Q_l)`
  and every maximal order there is `GL_2(Q_l)`-conjugate to `M_2(Z_l)`.
- R4 `recalled`: `B_p` is the quaternion division algebra over Q_p, and
  `w = v_p o Nrd` is a valuation on it. Its unique maximal order is
  `O_p = {w >= 0} = Z_{p^2} + Z_{p^2}*pi`, with `pi^2 = p`,
  `pi*a = sigma(a)*pi`, and residue field `F_{p^2}`. This holds also for
  p = 2, with `Z_4 = Z_2[zeta_3]` unramified.
- R5 `recalled`: maximal orders are hereditary, so every left O-lattice `I`
  with `O_L(I) = O` is locally principal.
- R6 `recalled`: for `alpha` in B, the determinant of `x -> x*alpha` on the
  4-dimensional Q-space B is `Nrd(alpha)^2`.
- R7 `recalled`: Pizer-style presentations of maximal orders (the "formula
  orders" below). They are **not** trusted: every one was re-verified as an
  order and as maximal by my own test.
- R8 PARI `isprime(p0,2)` returned 1, which is an APRCL primality proof for p0.

### Maximality test used (stated, own)

Let O be an order and O' any overorder. Then `O c O' c O'^# c O^#`, where
`L^# = {x : Trd(x*conj(y)) in Z for all y in L}`. `O' c O'^#` holds because
products of elements of O' are integral. `O'^# c O^#` holds because O is
contained in O'. So every element of O' is an element of O^# with integral
`Nrd`. `Nrd mod Z` is well defined on `O^#/O`, because
`Nrd(x+o) = Nrd(x) + Trd(x conj o) + Nrd(o)`. **If no nonzero class of `O^#/O`
has integral Nrd, then O is maximal.** The test is applied in two ways:

- For small p, every class of `O^#/O` is enumerated (via Smith form of `T`).
- For p0, the elementary divisors of `T` are `[p0,p0,1,1]`. The induced binary
  form `2p0*Nrd(u g1 + v g2) mod p0` is shown anisotropic by a Legendre symbol
  of -1.

The test is a proof of maximality. Every order was also checked to be a ring:
`1` is in O and `e_i e_j` is in O for all basis vectors.

Identification of `P = {x in O : p | Nrd x}` (own): the candidate is
`Pc = {x in O : Trd(x conj y) = 0 mod p for all y in O}`, a lattice.

- For p <= 17, all of `O/pO` was enumerated. The classes with `p | Nrd` are
  exactly the classes of `Pc`, with 0 mismatches, and there are p^2 of them.
- For p0, three checks were made:
  1. Every element of `Pc` has `p | Nrd`: all `A_ii` and `2A_ij` are 0 mod p.
  2. `Nrd mod p` is constant on cosets of `Pc`.
  3. `Nrd mod p` on `O/Pc = F_p^2` is an anisotropic binary form.

  Together these give `P = Pc` without enumeration.

### Q1: derivation

1. With the frozen convention, `A = T/2`, where `T_ij = Trd(e_i conj e_j)` (R2).
   So `det A = det T / 16`.
2. `det T` is basis-independent: a change of Z-basis is unimodular. It is a
   positive integer, because `T` is integral (O is an order) and positive
   definite (R1). Its l-adic valuation can be computed in `O_l = O (x) Z_l`.
3. For l != p: `O_l` is conjugate to `M_2(Z_l)` (R3), and conjugation preserves
   `Nrd = det`. On the basis `e11,e12,e21,e22`,
   `Trd(x conj y) = x11 y22 + x22 y11 - x12 y21 - x21 y12`. That is two
   hyperbolic planes, with determinant 1. So `v_l(det T) = 0`.
4. For l = p: `O_p = Z_{p^2} (+) Z_{p^2} pi` (R4), and
   `Nrd(a + b pi) = N(a) - p N(b)`. This is an orthogonal sum.
   `T = T_1 (+) (-p) T_1`, where `T_1` is the trace form of the unramified
   `Z_{p^2}`, which has unit determinant. For p = 2, `T_1 = [[2,1],[1,2]]`
   with determinant 3. So `v_p(det T) = 2`.
5. Hence `det T = p^2` and **`det(O, Nrd) = p^2/16`**. Nothing in the argument
   uses p odd.

**Where it changes if O is not maximal.** For `O c O_max`,
`det(O,Nrd) = [O_max:O]^2 p^2/16 = discrd(O)^2/16`. For an Eichler order of
level N this is `(pN)^2/16`. Scratch confirms both: `Z+2O` at p = 13 gives
676 = 8^2*169/16, and a level-3 Eichler order at p = 13 gives 1521/16 = 39^2/16.
The value p^2/16 is therefore a maximality fingerprint. It does not hold for
all orders.

### Q2: derivation

1. `I != 0` with `O I c I c O`. Since B is a division algebra, `O*alpha c I`
   for any nonzero `alpha` in I, and `O*alpha` has rank 4. So I is a full
   lattice. `O_L(I)` contains O, so it equals O by maximality.
2. By R5, `I_l = O_l alpha_l` for each l.
3. `[O_l : O_l alpha_l] = |det(x -> x alpha_l)|_l^{-1} = |Nrd(alpha_l)^2|_l^{-1}` (R6).
4. `n(I) Z_l = Nrd(I_l) Z_l = Nrd(alpha_l) Z_l`, because `Nrd(O_l)` contains
   `Nrd(1) = 1`.
5. Multiplying over l: **`[O : I] = n(I)^2`**.

**Where it changes if O is not maximal.** Step 2 fails for non-invertible
ideals, and then the identity fails. Two scratch cases at p = 13:

| order | ideal | `[O':I]` | n(I) | n(I)^2 |
| --- | --- | --- | --- | --- |
| `O' = Z+2O` | `I = 2O` | 2 | 4 | 16 |
| Eichler E of level 3 | `J = E cap 3O` | 27 | 9 | 81 |

The identity still holds for every locally principal ideal of any order.

**Measurement independence.** `[O:I]` was taken as `|det|` of the coordinates
of I's HNF basis on O's basis. `n(I)` was taken as `gcd(A_ii, 2A_ij)` of the
Nrd Gram on I's basis, which generates the value ideal of a quadratic form.

### Q3: derivation

1. For l != p, `P_l = O_l`. At p, `P_p = {w >= 1} = pi O_p` (R4). Since `w` is
   a valuation, P is a lattice and a two-sided ideal, with `[O:P] = p^2` and
   `n(P) = p`.
2. `det(P, Nrd) = det(O,Nrd)[O:P]^2 = p^6/16`. So `det(P, Nrd/p) = p^{-4} p^6/16 = p^2/16`.
3. `Trd(P) = pZ`. For l != p, `Trd(O_l) = Z_l`. At p,
   `pi O_p = pZ_{p^2} (+) Z_{p^2} pi`, and `Trd(a + b pi) = Tr(a)`, which has
   image `pZ_p`: the unramified trace is surjective, also at p = 2.
4. `Q*1` is orthogonal to `B^0`, since `Trd(1*conj x) = Trd(x) = 0`. The
   kernel of `Trd|_P` is `P^0`. So `[P : Zp (+) P^0] = [Trd(P) : Trd(Zp)] = [pZ : 2pZ] = 2`.
5. Therefore `det(Zp (+) P^0, Nrd/p) = 4 * p^2/16 = p^2/4`, and
   `det(Zp, Nrd/p) = Nrd(p)/p = p`.
6. **`det(P^0, Nrd/p) = p/4`**.

**Where it changes if P is replaced by O.** `Trd(O) = Z`, because 1/2 is not in
`O^#`. `[O : Z (+) O^0] = 2` and `det(O^0, Nrd) = p^2/4`, so
`det(O^0, Nrd/p) = 1/(4p)`. Scratch confirms this at every p.

**Where it changes if O is not maximal.** Step 1 fails, and so do the trace
image and the index 2 in step 4. For `(Z+2O) cap P` at p = 13 the trace image
is 26Z and the determinant is 52, not 13/4. For a level-N Eichler order E with
p not dividing N, `det((E cap P)^0) = N^2 p/4` (scratch at N = 3: 117/4).

Intermediate identities confirmed at every p:

- `Trd(P) = pZ`
- `[P : Zp + P^0] = 2`
- `det(P, Nrd/p) = p^2/16`
- `det(O^0, Nrd) = p^2/4`

### Section A scratch code (own, verbatim) and outputs (verbatim)

Commands (each run as one process, `ulimit -v 4000000; timeout 900`):

```
cd /tmp/claude-0/-home-user/5af2d3d8-0ba3-5d96-b05f-205cb058efcf/scratchpad/validator-eecb7f
(ulimit -v 4000000; timeout 900 gp -q --default parisize=200000000 phaseA_q1q3.gp) > phaseA_q1q3.out 2>&1
(ulimit -v 4000000; timeout 900 gp -q --default parisize=200000000 phaseA_q2.gp) > phaseA_q2.out 2>&1
```

Earlier invocations failed with gp syntax errors in my own scripts (missing
braces on multi-line statements, a loop-variable typo, a helper that rejected
matrices, and a ramification list printed as a string). Those were fixed. The
outputs below are from the final code. A re-run of `phaseA_q1q3.gp` after the
last library fix differed from the previous run only in how the ramification
list is printed.

SHA-256 of the final scratch files:

```
f76b1510cdda7974911a3f8858df72c274367980fbe34609b533b86a4db0668a  qlib.gp
912ba0e5fc6612d91b0374c9525be4e3bcabbd9d5e3ef6f645cdd339730a3888  phaseA_q1q3.gp
3718a957866358ad6316a70a817cbfab2615eb133c9b46a2c91a94d003516acb  phaseA_q2.gp
ac00879c5ff5c6052712e4386c5d7a85b16c5a0738a1a5a6f57c9bd005ec91e3  phaseA_q1q3.out
5a9f8cf5a02223bac042a6f51f5e8b4bd6518a0f9d6d89cdea0252632fd59dcc  phaseA_q2.out
```

`qlib.gp`:

```gp
\\ validator-eecb7f -- own quaternion library, written from scratch in Phase A.
\\ B = (a,b)_Q with basis 1,i,j,k; i^2=a, j^2=b, k=ij=-ji.
\\ Elements are column vectors [x0,x1,x2,x3]~ in standard coordinates.
\\ A lattice is a 4 x n matrix whose columns are Z-basis vectors (std coords).

{qmul(a,b,x,y) = [x[1]*y[1] + a*x[2]*y[2] + b*x[3]*y[3] - a*b*x[4]*y[4],
                 x[1]*y[2] + x[2]*y[1] - b*x[3]*y[4] + b*x[4]*y[3],
                 x[1]*y[3] + x[3]*y[1] + a*x[2]*y[4] - a*x[4]*y[2],
                 x[1]*y[4] + x[4]*y[1] + x[2]*y[3] - x[3]*y[2]]~;}
qnrd(a,b,x) = x[1]^2 - a*x[2]^2 - b*x[3]^2 + a*b*x[4]^2;
qtrd(x) = 2*x[1];
qconj(x) = [x[1],-x[2],-x[3],-x[4]]~;

\\ Gram of the form Nrd/s on the columns of M, FROZEN CONVENTION:
\\ A_ii = q(e_i), A_ij = (q(e_i+e_j)-q(e_i)-q(e_j))/2.
gramq(a,b,M,s) = {
  my(n=#M, A=matrix(n,n));
  for(i=1,n, for(j=1,n,
     A[i,j] = (qnrd(a,b,M[,i]+M[,j]) - qnrd(a,b,M[,i]) - qnrd(a,b,M[,j]))/2/s));
  for(i=1,n, A[i,i] = qnrd(a,b,M[,i])/s);
  A;
}
isintv(v) = (denominator(v) == 1);
\\ Z-span of the columns of a rational matrix G (full rank 4 assumed by callers)
latspan(G) = { my(d=denominator(G)); mathnf(G*d)/d; }
\\ coordinates of x w.r.t. lattice basis M (square)
crd(M,x) = matsolve(M,x);
inlat(M,x) = isintv(crd(M,x));

\\ M is an order: 1 in M and closed under multiplication
isorder(a,b,M) = {
  if(!inlat(M,[1,0,0,0]~), return(0));
  for(i=1,4, for(j=1,4, if(!inlat(M, qmul(a,b,M[,i],M[,j])), return(0))));
  1;
}
\\ T = (Trd(e_i conj(e_j)))_{ij} = 2 * Gram(Nrd)
trform(a,b,M) = 2*gramq(a,b,M,1);

\\ Maximality test (stated in Section A): any overorder O' of O satisfies
\\ O c O' c O'^# c O^#, so every x in O' is in O^# with Nrd(x) in Z.
\\ Nrd mod Z is well defined on O^#/O. If no nonzero class of O^#/O has
\\ integral Nrd, O has no proper overorder, i.e. O is maximal.
\\ Returns [verdict, method, witness]; verdict 1 = maximal.
maxtest(a,b,M) = {
  my(T=trform(a,b,M), S=matsnf(T,1), U=S[1], V=S[2], D=S[3], ds, gens, tot, big);
  ds = vector(4,k,D[k,k]); gens = vector(4,k,V[,k]/ds[k]);
  tot = prod(k=1,4,ds[k]);
  if(tot <= 200000,
    forvec(c = vector(4,k,[0,ds[k]-1]),
      my(y = sum(k=1,4,c[k]*gens[k]));
      if(!isintv(y),
        my(x = M*y);
        if(denominator(qnrd(a,b,x))==1, return([0,"enum",y]))));
    return([1,"enum O#/O exhaustive",tot]));
  \\ large case: need elementary divisors [p,p,1,1] with p odd prime
  big = select(t->t>1, ds);
  if(#big!=2 || big[1]!=big[2] || !isprime(big[1]) || big[1]==2, return([-1,"unsupported",ds]));
  my(p=big[1], idx=[k | k<-[1..4], ds[k]>1], g1=M*gens[idx[1]], g2=M*gens[idx[2]],
     N1=qnrd(a,b,g1), N2=qnrd(a,b,g2), B12=qnrd(a,b,g1+g2)-N1-N2,
     al=2*p*N1, be=2*p*B12, ga=2*p*N2, disc);
  if(denominator([al,be,ga])!=1, return([-1,"nonintegral binary",[al,be,ga]]));
  disc = be^2-4*al*ga;
  if(kronecker(disc,p)==-1, return([1,"binary disc form anisotropic mod p",disc%p]),
                            return([0,"binary disc form isotropic",disc%p]));
}

\\ Order generated by lattice M and extra elements (closure under products),
\\ guarded: returns 0 if closure leaves dual bound or fails to stabilise.
closure(a,b,M,xs) = {
  my(L=latspan(concat(M,xs)), L2, it=0);
  while(it<20, it++;
    my(G=L);
    for(i=1,4, for(j=1,4, G=concat(G, qmul(a,b,L[,i],L[,j]))));
    L2 = latspan(G);
    if(abs(matdet(L2))==0, return(0));
    if(L2==L, return(L));
    if(denominator(matdet(trform(a,b,L2)))!=1, return(0));
    L=L2);
  0;
}

\\ Saturate an order to a maximal one using the O^#/O search.
saturate(a,b,M) = {
  my(r, it=0);
  while(it<30, it++;
    r = maxtest(a,b,M);
    if(r[1]==1, return(M));
    if(r[1]==-1, error("maxtest unsupported"));
    my(T=trform(a,b,M), S=matsnf(T,1), V=S[2], D=S[3], ds=vector(4,k,D[k,k]),
       gens=vector(4,k,V[,k]/ds[k]), found=0);
    forvec(c = vector(4,k,[0,ds[k]-1]),
      my(y = sum(k=1,4,c[k]*gens[k]));
      if(!isintv(y),
        my(x = M*y);
        if(denominator(qnrd(a,b,x))==1,
          my(C = closure(a,b,M,x));
          if(C!=0 && isorder(a,b,C) && abs(matdet(C))<abs(matdet(M)), M=C; found=1; break))));
    if(!found, error("no enlargement found but maxtest failed")));
  error("saturate: too many iterations");
}

\\ ramification of (a,b): list of primes l | 2ab with Hilbert symbol -1, plus inf
ramif(a,b) = { my(ps=factor(2*a*b)[,1]~, r=[]);
  for(t=1,#ps, if(hilbert(a,b,ps[t])==-1, r=concat(r,ps[t])));
  if(a<0 && b<0, r=concat(r,["inf"])); r; }

\\ P = {x in O : p | Nrd x}. Candidate: radical of trace form mod p, i.e.
\\ {c in Z^4 : T c = 0 mod p} (coords wrt O basis).
pcand(a,b,M,p) = { my(T=trform(a,b,M), K=lift(matker(T*Mod(1,p))));
  M*mathnf(concat(K, p*matid(4))); }

\\ exhaustive: classes of O/pO with Nrd = 0 mod p (small p only)
pbrute(a,b,M,p) = { my(cnt=0, bad=0, Pc=pcand(a,b,M,p));
  forvec(c=vector(4,k,[0,p-1]),
    my(x=M*c~, z=(qnrd(a,b,x)%p==0), inP=inlat(Pc,x));
    if(z, cnt++); if(z!=inP, bad++));
  [cnt, bad]; }

\\ Check Pc = P for large p without enumeration:
\\ (a) every element of Pc has p | Nrd (Gram entries A_ii, 2A_ij = 0 mod p)
\\ (b) [O:Pc] = p^2 and Nrd mod p is well defined on O/Pc (T(x,c)=0 mod p)
\\ (c) the binary form Nrd mod p on O/Pc is anisotropic => no x in O \ Pc has p|Nrd.
pcheck(a,b,M,p) = {
  my(Pc=pcand(a,b,M,p), A=gramq(a,b,Pc,1), okA=1, idx=abs(matdet(crd(M,Pc))),
     T=trform(a,b,M), okT, C, Q, q1,q2,b12, disc);
  for(i=1,4, if(A[i,i]%p!=0, okA=0); for(j=1,4, if(i!=j && (2*A[i,j])%p!=0, okA=0)));
  \\ well-definedness: T(e_i, c) = 0 mod p for c in Pc
  my(TT = matrix(4,4,i,j, qnrd(a,b,M[,i]+Pc[,j]) - qnrd(a,b,M[,i]) - qnrd(a,b,Pc[,j])));
  okT = 1; for(i=1,4, for(j=1,4, if(TT[i,j]%p!=0, okT=0)));
  \\ complement of Pc in O mod p: pick two O-basis vectors independent mod Pc
  C = matsnf(crd(M,Pc),1);  \\ U*X*V = D ; quotient generators from U^-1
  my(Ui = C[1]^(-1), Dg = C[3], qidx = [k | k<-[1..4], Dg[k,k]>1]);
  if(#qidx!=2, return([okA, okT, idx, "quotient not (Z/p)^2", Dg]));
  my(u1 = M*Ui[,qidx[1]], u2 = M*Ui[,qidx[2]]);
  q1 = qnrd(a,b,u1); q2 = qnrd(a,b,u2); b12 = qnrd(a,b,u1+u2)-q1-q2;
  if(p==2, my(anis = (q1%2!=0) && (q2%2!=0) && ((q1+q2+b12)%2!=0));
           return([okA, okT, idx, anis]));
  disc = b12^2 - 4*q1*q2;
  [okA, okT, idx, kronecker(disc,p)==-1];
}

\\ trace-zero sublattice of lattice L (4 columns)
tr0(L) = { my(t = matrix(1,#L,r,j, qtrd(L[,j])), K = matkerint(t)); L*K; }

\\ left ideal O*alpha + O*N (as lattice)
lideal(a,b,M,al,N) = { my(G=matrix(4,0));
  for(i=1,4, G=concat(G, qmul(a,b,M[,i],al)));
  latspan(concat(G, N*M)); }
\\ n(I): gcd of values of Nrd on I = gcd(A_ii, 2A_ij)
nrdideal(a,b,L) = { my(A=gramq(a,b,L,1), g=0);
  for(i=1,#L, g=gcd(g,A[i,i]); for(j=i+1,#L, g=gcd(g,2*A[i,j]))); g; }
isleft(a,b,M,L) = { for(i=1,4, for(j=1,4, if(!inlat(L, qmul(a,b,M[,i],L[,j])), return(0)))); 1; }
```

`phaseA_q1q3.gp`:

```gp
\\ validator-eecb7f Phase A driver: sanity, Q1, Q3 (own code, own orders)
read("qlib.gp");
setrand(20260926);

\\ ---- sanity of the multiplication table on random elements
{sanity(a,b) = my(ok=1);
  for(t=1,200, my(x=vector(4,k,random(41)-20)~/(1+random(3)), y=vector(4,k,random(41)-20)~, z=vector(4,k,random(41)-20)~);
    if(qmul(a,b,qmul(a,b,x,y),z)!=qmul(a,b,x,qmul(a,b,y,z)), ok=0);
    if(qnrd(a,b,qmul(a,b,x,y))!=qnrd(a,b,x)*qnrd(a,b,y), ok=0);
    if(qmul(a,b,x,qconj(x))!=[qnrd(a,b,x),0,0,0]~, ok=0);
    if(qtrd(x)*x - qmul(a,b,x,x) != [qnrd(a,b,x),0,0,0]~, ok=0));
  ok; }

p0 = 2^63; while(!(isprime(p0) && p0%4==3), p0++);
print("large prime p0 = ", p0, "  p0 mod 8 = ", p0%8, "  isprime (APRCL/ECPP proof) = ", isprime(p0,2) );

\\ [p, a, b, formula order (recalled Pizer-type presentation) or 0]
{cases = [ [2,-1,-1, [1,0,0,1/2; 0,1,0,1/2; 0,0,1,1/2; 0,0,0,1/2]],
          [3,-1,-3, [1,0,1/2,0; 0,1,0,1/2; 0,0,1/2,0; 0,0,0,1/2]],
          [5,-2,-5, [1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1]],
          [13,-2,-13,[1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1]],
          [17,-17,-3,[1/2,0,0,0; 0,1/2,0,0; 1/2,0,1/3,0; 0,1/2,1/3,1]],
          [p0,-1,-p0,[1,0,1/2,0; 0,1,0,1/2; 0,0,1/2,0; 0,0,0,1/2]] ];}

{for(t=1,#cases,
  my(p=cases[t][1], a=cases[t][2], b=cases[t][3], F=cases[t][4], orders=List(), names=List());
  print("\n==================== p = ", p, "   p mod 8 = ", p%8, "   B = (", a, ",", b, ")");
  print("ramified places of (a,b): ", ramif(a,b), "   mult. table sanity: ", sanity(a,b));
  if(p < 100,
    my(Os = saturate(a,b,matid(4)));
    listput(orders, Os); listput(names, "saturated from Z<i,j>"));
  listput(orders, F); listput(names, "formula order (recalled presentation)");
  for(u=1,#orders,
    my(M=orders[u], A, T, mt, Pc, P0, Ap, detP0, O0, trP, pc);
    print("--- order: ", names[u]);
    print("  basis (columns, std coords): ", M);
    print("  is order: ", isorder(a,b,M));
    T = trform(a,b,M); mt = maxtest(a,b,M);
    print("  det Trd(e_i conj e_j) = ", matdet(T), "  elementary divisors ", matsnf(T));
    print("  maximality test: ", mt[1], "  [", mt[2], "]");
    A = gramq(a,b,M,1);
    print("  Q1 det Gram(O,Nrd) = ", matdet(A), "   p^2/16 = ", p^2/16, "   equal: ", matdet(A)==p^2/16);
    \\ Q3
    Pc = pcand(a,b,M,p);
    if(p < 100, pc = pbrute(a,b,M,p);
       print("  P brute force over O/pO: #classes with p|Nrd = ", pc[1], " (p^2 = ", p^2, "), mismatches vs candidate = ", pc[2]));
    print("  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: ", pcheck(a,b,M,p));
    trP = gcd(vector(4,j,qtrd(Pc[,j])));
    P0 = tr0(Pc);
    detP0 = matdet(gramq(a,b,P0,p));
    O0 = tr0(M);
    print("  Trd(P) = ", trP, "Z ;  [P : Zp + P^0] = ", abs(matdet(crd(Pc, concat([p,0,0,0]~, P0)))));
    print("  det Gram(P,Nrd/p) = ", matdet(gramq(a,b,Pc,p)), "   det Gram(O^0,Nrd) = ", matdet(gramq(a,b,O0,1)), " (p^2/4 = ", p^2/4, ")");
    print("  Q3 det Gram(P^0,Nrd/p) = ", detP0, "   p/4 = ", p/4, "   equal: ", detP0==p/4);
    print("  [P replaced by O] det Gram(O^0,Nrd/p) = ", matdet(gramq(a,b,O0,p)), "   1/(4p) = ", 1/(4*p));
    print("  P^0 Gram (Nrd/p): ", gramq(a,b,P0,p))));}
quit;
```

`phaseA_q2.gp`:

```gp
\\ validator-eecb7f Phase A driver: Q2 (index vs n(I)), extra maximal orders
\\ (right orders of the ideals) for Q1, and non-maximal controls.
read("qlib.gp");

p0 = 2^63; while(!(isprime(p0) && p0%4==3), p0++);

\\ primitive alpha in O (coords in [-R,R]^4 wrt O basis) with N | Nrd(alpha)
{findalpha(a,b,M,N,R) =
  my(fl = factor(N)[,1]);
  forvec(c = vector(4,k,[-R,R]),
    my(v=c~, al=M*v, ok=1);
    if(v==0, next);
    for(t=1,#fl, if(v%fl[t]==0, ok=0));
    if(ok && qnrd(a,b,al)%N==0, return(al)));
  0;}

\\ lattice intersection of two full-rank 4x4 lattices
{latint(L1,L2) = my(d=denominator(concat(L1,L2)), K=matkerint(concat(L1*d,-L2*d)));
  latspan(L1*K[1..4,]);}

{doideal(a,b,M,I,label) =
  my(idx = abs(matdet(crd(M,I))), n = nrdideal(a,b,I), OR, mt);
  print("  ", label, ": left O-ideal ", isleft(a,b,M,I), ", contained in O ", isintv(crd(M,I)),
        ";  [O:I] = ", idx, " = ", factor(idx), " ;  n(I) = ", n, " ;  [O:I] == n(I)^2 : ", idx==n^2);
  \\ another maximal order: (1/n) conj(I) I ; verify order + maximal + det
  my(G=matrix(4,0)); for(i=1,4, for(j=1,4, G=concat(G, qmul(a,b,qconj(I[,i]),I[,j]))));
  OR = latspan(G)/n;
  mt = maxtest(a,b,OR);
  print("     O2 = conj(I)I/n(I): is order ", isorder(a,b,OR), ", I*O2 c I ",
        prod(i=1,4,prod(j=1,4,inlat(I,qmul(a,b,I[,i],OR[,j])))),
        ", maximal ", mt[1], " [", mt[2], "], det Gram(O2,Nrd) = ", matdet(gramq(a,b,OR,1)),
        ", equals p^2/16: ", matdet(gramq(a,b,OR,1))==(ramif(a,b)[1])^2/16,
        ", O2 == O as lattice: ", latspan(OR)==latspan(M));
  OR;}

{cases = [ [2,-1,-1, [1,0,0,1/2; 0,1,0,1/2; 0,0,1,1/2; 0,0,0,1/2]],
           [13,-2,-13,[1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1]],
           [p0,-1,-p0,[1,0,1/2,0; 0,1,0,1/2; 0,0,1/2,0; 0,0,0,1/2]] ];}

{for(t=1,#cases,
  my(p=cases[t][1], a=cases[t][2], b=cases[t][3], M=cases[t][4]);
  print("\n==================== Q2 at p = ", p, "  B = (", a, ",", b, ")  O maximal: ", maxtest(a,b,M)[1]);
  foreach([2,3,5,6,4,35], N,
    my(al = findalpha(a,b,M,N,3));
    if(al==0, print("  N=",N,": no alpha found"); next);
    my(I = lideal(a,b,M,al,N));
    print("  alpha = ", al~, "  Nrd(alpha) = ", qnrd(a,b,al), " = ", factor(qnrd(a,b,al)));
    doideal(a,b,M,I,Str("I = O*alpha + O*",N)));
  \\ principal ideal O*beta with composite reduced norm
  my(be = findalpha(a,b,M,15,3));
  doideal(a,b,M, latspan(matconcat(vector(4,i,qmul(a,b,M[,i],be)))), Str("principal O*beta, Nrd(beta) = ", qnrd(a,b,be)));
  \\ two-sided P and 6*O
  doideal(a,b,M, pcand(a,b,M,p), "P = {x in O : p | Nrd x}");
  doideal(a,b,M, 6*M, "6*O"));}

\\ ----- non-maximal controls at p = 13
a=-2; b=-13; p=13; M=[1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1];
print("\n==================== non-maximal controls at p = 13");
Z2 = latspan(concat([1,0,0,0]~, 2*M));
{print("O' = Z + 2O: is order ", isorder(a,b,Z2), ", maximal ", maxtest(a,b,Z2)[1], ", [O:O'] = ", abs(matdet(crd(M,Z2))),
      ", det Gram(O',Nrd) = ", matdet(gramq(a,b,Z2,1)), " (= [O:O']^2 p^2/16 = ", abs(matdet(crd(M,Z2)))^2*p^2/16, ")");}
I2 = 2*M;
{print("I = 2O as left O'-ideal: left ", isleft(a,b,Z2,I2), ", [O':I] = ", abs(matdet(crd(Z2,I2))), ", n(I) = ", nrdideal(a,b,I2),
      "  -> [O':I] == n(I)^2 : ", abs(matdet(crd(Z2,I2)))==nrdideal(a,b,I2)^2);}
\\ Eichler order of level 3: O cap O2 where O2 = right order of a norm-3 ideal
al3 = findalpha(a,b,M,3,3); I3 = lideal(a,b,M,al3,3);
O2 = latspan(matconcat(vector(16,t, qmul(a,b,qconj(I3[,(t-1)\4+1]),I3[,(t-1)%4+1]))))/nrdideal(a,b,I3);
E3 = latint(M,O2);
{print("Eichler O cap O2 (level 3): is order ", isorder(a,b,E3), ", maximal ", maxtest(a,b,E3)[1],
      ", det Trd form ", matdet(trform(a,b,E3)), ", det Gram(E,Nrd) = ", matdet(gramq(a,b,E3,1)), " (=(3p)^2/16 = ", (3*p)^2/16, ")");}
\\ a left E-ideal that is not locally principal: I = E cap (3O)+... use J = 3*O2 + E*? simple: J = O2*3 cap E? report only index/norm
J = latint(E3, 3*M);
{print("J = E cap 3O (left E-ideal? ", isleft(a,b,E3,J), "): [E:J] = ", abs(matdet(crd(E3,J))), ", n(J) = ", nrdideal(a,b,J),
      "  -> [E:J] == n(J)^2 : ", abs(matdet(crd(E3,J)))==nrdideal(a,b,J)^2);}
\\ Q3 with a non-maximal order: P_E = {x in E : p | Nrd x}; E is maximal at p, so expect same p/4
PE = latint(E3, pcand(a,b,M,p));
print("P_E = E cap P: det Gram(P_E^0, Nrd/p) = ", matdet(gramq(a,b,tr0(PE),p)), "  (p/4 * 3^2 = ", p/4*9, ")");
PZ = latint(Z2, pcand(a,b,M,p));
print("P_{Z+2O} = (Z+2O) cap P: det Gram(P^0, Nrd/p) = ", matdet(gramq(a,b,tr0(PZ),p)), "  Trd(P_{Z+2O}) = ", gcd(vector(4,j,qtrd(PZ[,j]))), "Z");
quit;
```

`phaseA_q1q3.out` (ANSI colour codes stripped):

```
large prime p0 = 9223372036854775907  p0 mod 8 = 3  isprime (APRCL/ECPP proof) = 1

==================== p = 2   p mod 8 = 2   B = (-1,-1)
ramified places of (a,b): [2, "inf"]   mult. table sanity: 1
--- order: saturated from Z<i,j>
  basis (columns, std coords): [1, 0, 0, 1/2; 0, 1, 0, 1/2; 0, 0, 1, 1/2; 0, 0, 0, 1/2]
  is order: 1
  det Trd(e_i conj e_j) = 4  elementary divisors [2, 2, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 1/4   p^2/16 = 1/4   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 4 (p^2 = 4), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 4, 1]
  Trd(P) = 2Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 1/4   det Gram(O^0,Nrd) = 1 (p^2/4 = 1)
  Q3 det Gram(P^0,Nrd/p) = 1/2   p/4 = 1/2   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/8   1/(4p) = 1/8
  P^0 Gram (Nrd/p): [1, 1/2, -1/2; 1/2, 1, -3/2; -1/2, -3/2, 3]
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1, 0, 0, 1/2; 0, 1, 0, 1/2; 0, 0, 1, 1/2; 0, 0, 0, 1/2]
  is order: 1
  det Trd(e_i conj e_j) = 4  elementary divisors [2, 2, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 1/4   p^2/16 = 1/4   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 4 (p^2 = 4), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 4, 1]
  Trd(P) = 2Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 1/4   det Gram(O^0,Nrd) = 1 (p^2/4 = 1)
  Q3 det Gram(P^0,Nrd/p) = 1/2   p/4 = 1/2   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/8   1/(4p) = 1/8
  P^0 Gram (Nrd/p): [1, 1/2, -1/2; 1/2, 1, -3/2; -1/2, -3/2, 3]

==================== p = 3   p mod 8 = 3   B = (-1,-3)
ramified places of (a,b): [3, "inf"]   mult. table sanity: 1
--- order: saturated from Z<i,j>
  basis (columns, std coords): [1, 0, 0, 1/2; 0, 1, 1/2, 0; 0, 0, 1/2, 0; 0, 0, 0, 1/2]
  is order: 1
  det Trd(e_i conj e_j) = 9  elementary divisors [3, 3, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 9/16   p^2/16 = 9/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 9 (p^2 = 9), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 9, 1]
  Trd(P) = 3Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 9/16   det Gram(O^0,Nrd) = 9/4 (p^2/4 = 9/4)
  Q3 det Gram(P^0,Nrd/p) = 3/4   p/4 = 3/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/12   1/(4p) = 1/12
  P^0 Gram (Nrd/p): [3, 3/2, 0; 3/2, 1, 0; 0, 0, 1]
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1, 0, 1/2, 0; 0, 1, 0, 1/2; 0, 0, 1/2, 0; 0, 0, 0, 1/2]
  is order: 1
  det Trd(e_i conj e_j) = 9  elementary divisors [3, 3, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 9/16   p^2/16 = 9/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 9 (p^2 = 9), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 9, 1]
  Trd(P) = 3Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 9/16   det Gram(O^0,Nrd) = 9/4 (p^2/4 = 9/4)
  Q3 det Gram(P^0,Nrd/p) = 3/4   p/4 = 3/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/12   1/(4p) = 1/12
  P^0 Gram (Nrd/p): [3, 3/2, 0; 3/2, 1, 0; 0, 0, 1]

==================== p = 5   p mod 8 = 5   B = (-2,-5)
ramified places of (a,b): [5, "inf"]   mult. table sanity: 1
--- order: saturated from Z<i,j>
  basis (columns, std coords): [1, 0, 1/2, 1/2; 0, 1, 1/2, 1/4; 0, 0, 1/2, 0; 0, 0, 0, 1/4]
  is order: 1
  det Trd(e_i conj e_j) = 25  elementary divisors [5, 5, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 25/16   p^2/16 = 25/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 25 (p^2 = 25), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 25, 1]
  Trd(P) = 5Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 25/16   det Gram(O^0,Nrd) = 25/4 (p^2/4 = 25/4)
  Q3 det Gram(P^0,Nrd/p) = 5/4   p/4 = 5/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/20   1/(4p) = 1/20
  P^0 Gram (Nrd/p): [10, -5/2, -15/2; -5/2, 1, 2; -15/2, 2, 6]
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1/2, 0, 0, 0; 0, 1/4, 0, 0; 1/2, 1/2, 1, 0; 1/2, 1/4, 0, 1]
  is order: 1
  det Trd(e_i conj e_j) = 25  elementary divisors [5, 5, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 25/16   p^2/16 = 25/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 25 (p^2 = 25), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 25, 1]
  Trd(P) = 5Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 25/16   det Gram(O^0,Nrd) = 25/4 (p^2/4 = 25/4)
  Q3 det Gram(P^0,Nrd/p) = 5/4   p/4 = 5/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/20   1/(4p) = 1/20
  P^0 Gram (Nrd/p): [10, 5/2, 5/2; 5/2, 1, 0; 5/2, 0, 2]

==================== p = 13   p mod 8 = 5   B = (-2,-13)
ramified places of (a,b): [13, "inf"]   mult. table sanity: 1
--- order: saturated from Z<i,j>
  basis (columns, std coords): [1, 0, 1/2, 1/2; 0, 1, 1/2, 1/4; 0, 0, 1/2, 0; 0, 0, 0, 1/4]
  is order: 1
  det Trd(e_i conj e_j) = 169  elementary divisors [13, 13, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 169/16   p^2/16 = 169/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 169 (p^2 = 169), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 169, 1]
  Trd(P) = 13Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 169/16   det Gram(O^0,Nrd) = 169/4 (p^2/4 = 169/4)
  Q3 det Gram(P^0,Nrd/p) = 13/4   p/4 = 13/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/52   1/(4p) = 1/52
  P^0 Gram (Nrd/p): [26, -13/2, -39/2; -13/2, 2, 5; -39/2, 5, 15]
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1/2, 0, 0, 0; 0, 1/4, 0, 0; 1/2, 1/2, 1, 0; 1/2, 1/4, 0, 1]
  is order: 1
  det Trd(e_i conj e_j) = 169  elementary divisors [13, 13, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 169/16   p^2/16 = 169/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 169 (p^2 = 169), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 169, 1]
  Trd(P) = 13Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 169/16   det Gram(O^0,Nrd) = 169/4 (p^2/4 = 169/4)
  Q3 det Gram(P^0,Nrd/p) = 13/4   p/4 = 13/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/52   1/(4p) = 1/52
  P^0 Gram (Nrd/p): [65, 13/2, 13/2; 13/2, 1, 0; 13/2, 0, 2]

==================== p = 17   p mod 8 = 1   B = (-17,-3)
ramified places of (a,b): [17, "inf"]   mult. table sanity: 1
--- order: saturated from Z<i,j>
  basis (columns, std coords): [1, 0, 0, 1/2; 0, 1, 1/2, 0; 0, 0, 1/2, 1/3; 0, 0, 0, 1/6]
  is order: 1
  det Trd(e_i conj e_j) = 289  elementary divisors [17, 17, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 289/16   p^2/16 = 289/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 289 (p^2 = 289), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 289, 1]
  Trd(P) = 17Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 289/16   det Gram(O^0,Nrd) = 289/4 (p^2/4 = 289/4)
  Q3 det Gram(P^0,Nrd/p) = 17/4   p/4 = 17/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/68   1/(4p) = 1/68
  P^0 Gram (Nrd/p): [1, 17/2, -5; 17/2, 85, -51; -5, -51, 31]
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1/2, 0, 0, 0; 0, 1/2, 0, 0; 1/2, 0, 1/3, 0; 0, 1/2, 1/3, 1]
  is order: 1
  det Trd(e_i conj e_j) = 289  elementary divisors [17, 17, 1, 1]
  maximality test: 1  [enum O#/O exhaustive]
  Q1 det Gram(O,Nrd) = 289/16   p^2/16 = 289/16   equal: 1
  P brute force over O/pO: #classes with p|Nrd = 289 (p^2 = 289), mismatches vs candidate = 0
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 289, 1]
  Trd(P) = 17Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 289/16   det Gram(O^0,Nrd) = 289/4 (p^2/4 = 289/4)
  Q3 det Gram(P^0,Nrd/p) = 17/4   p/4 = 17/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/68   1/(4p) = 1/68
  P^0 Gram (Nrd/p): [1, 17/2, 3/2; 17/2, 102, 17; 3/2, 17, 3]

==================== p = 9223372036854775907   p mod 8 = 3   B = (-1,-9223372036854775907)
ramified places of (a,b): [9223372036854775907, "inf"]   mult. table sanity: 1
--- order: formula order (recalled presentation)
  basis (columns, std coords): [1, 0, 1/2, 0; 0, 1, 0, 1/2; 0, 0, 1/2, 0; 0, 0, 0, 1/2]
  is order: 1
  det Trd(e_i conj e_j) = 85070591730234617692071315155187672649  elementary divisors [9223372036854775907, 9223372036854775907, 1, 1]
  maximality test: 1  [binary disc form anisotropic mod p]
  Q1 det Gram(O,Nrd) = 85070591730234617692071315155187672649/16   p^2/16 = 85070591730234617692071315155187672649/16   equal: 1
  P candidate check [okA(all Nrd = 0 mod p), okT(T(O,P)=0 mod p), [O:P], O/P binary anisotropic]: [1, 1, 85070591730234617692071315155187672649, 1]
  Trd(P) = 9223372036854775907Z ;  [P : Zp + P^0] = 2
  det Gram(P,Nrd/p) = 85070591730234617692071315155187672649/16   det Gram(O^0,Nrd) = 85070591730234617692071315155187672649/4 (p^2/4 = 85070591730234617692071315155187672649/4)
  Q3 det Gram(P^0,Nrd/p) = 9223372036854775907/4   p/4 = 9223372036854775907/4   equal: 1
  [P replaced by O] det Gram(O^0,Nrd/p) = 1/36893488147419103628   1/(4p) = 1/36893488147419103628
  P^0 Gram (Nrd/p): [9223372036854775907, 9223372036854775907/2, 0; 9223372036854775907/2, 2305843009213693977, 0; 0, 0, 1]
```

`phaseA_q2.out` (ANSI colour codes stripped):

```

==================== Q2 at p = 2  B = (-1,-1)  O maximal: 1
  alpha = [-4, -4, -3, -1]  Nrd(alpha) = 42 = [2, 1; 3, 1; 7, 1]
  I = O*alpha + O*2: left O-ideal 1, contained in O 1;  [O:I] = 4 = Mat([2, 2]) ;  n(I) = 2 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 1
  alpha = [-4, -4, -3, -1]  Nrd(alpha) = 42 = [2, 1; 3, 1; 7, 1]
  I = O*alpha + O*3: left O-ideal 1, contained in O 1;  [O:I] = 9 = Mat([3, 2]) ;  n(I) = 3 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-9/2, -9/2, -7/2, -3/2]  Nrd(alpha) = 55 = [5, 1; 11, 1]
  I = O*alpha + O*5: left O-ideal 1, contained in O 1;  [O:I] = 25 = Mat([5, 2]) ;  n(I) = 5 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-4, -4, -3, -1]  Nrd(alpha) = 42 = [2, 1; 3, 1; 7, 1]
  I = O*alpha + O*6: left O-ideal 1, contained in O 1;  [O:I] = 36 = [2, 2; 3, 2] ;  n(I) = 6 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 0
  N=4: no alpha found
  alpha = [-4, -3, -3, -1]  Nrd(alpha) = 35 = [5, 1; 7, 1]
  I = O*alpha + O*35: left O-ideal 1, contained in O 1;  [O:I] = 1225 = [5, 2; 7, 2] ;  n(I) = 35 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 0
  principal O*beta, Nrd(beta) = 15: left O-ideal 1, contained in O 1;  [O:I] = 225 = [3, 2; 5, 2] ;  n(I) = 15 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 0
  P = {x in O : p | Nrd x}: left O-ideal 1, contained in O 1;  [O:I] = 4 = Mat([2, 2]) ;  n(I) = 2 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 1
  6*O: left O-ideal 1, contained in O 1;  [O:I] = 1296 = [2, 4; 3, 4] ;  n(I) = 36 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 1/4, equals p^2/16: 1, O2 == O as lattice: 1

==================== Q2 at p = 13  B = (-2,-13)  O maximal: 1
  alpha = [-3/2, -3/4, -6, -21/4]  Nrd(alpha) = 1188 = [2, 2; 3, 3; 11, 1]
  I = O*alpha + O*2: left O-ideal 1, contained in O 1;  [O:I] = 4 = Mat([2, 2]) ;  n(I) = 2 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-3/2, -3/4, -5, -17/4]  Nrd(alpha) = 798 = [2, 1; 3, 1; 7, 1; 19, 1]
  I = O*alpha + O*3: left O-ideal 1, contained in O 1;  [O:I] = 9 = Mat([3, 2]) ;  n(I) = 3 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-3/2, -3/4, -5, -21/4]  Nrd(alpha) = 1045 = [5, 1; 11, 1; 19, 1]
  I = O*alpha + O*5: left O-ideal 1, contained in O 1;  [O:I] = 25 = Mat([5, 2]) ;  n(I) = 5 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-3/2, -3/4, -5, -17/4]  Nrd(alpha) = 798 = [2, 1; 3, 1; 7, 1; 19, 1]
  I = O*alpha + O*6: left O-ideal 1, contained in O 1;  [O:I] = 36 = [2, 2; 3, 2] ;  n(I) = 6 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-3/2, -3/4, -6, -21/4]  Nrd(alpha) = 1188 = [2, 2; 3, 3; 11, 1]
  I = O*alpha + O*4: left O-ideal 1, contained in O 1;  [O:I] = 16 = Mat([2, 4]) ;  n(I) = 4 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-3/2, -3/4, -2, -17/4]  Nrd(alpha) = 525 = [3, 1; 5, 2; 7, 1]
  I = O*alpha + O*35: left O-ideal 1, contained in O 1;  [O:I] = 1225 = [5, 2; 7, 2] ;  n(I) = 35 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  principal O*beta, Nrd(beta) = 330: left O-ideal 1, contained in O 1;  [O:I] = 108900 = [2, 2; 3, 2; 5, 2; 11, 2] ;  n(I) = 330 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 0
  P = {x in O : p | Nrd x}: left O-ideal 1, contained in O 1;  [O:I] = 169 = Mat([13, 2]) ;  n(I) = 13 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 1
  6*O: left O-ideal 1, contained in O 1;  [O:I] = 1296 = [2, 4; 3, 4] ;  n(I) = 36 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [enum O#/O exhaustive], det Gram(O2,Nrd) = 169/16, equals p^2/16: 1, O2 == O as lattice: 1

==================== Q2 at p = 9223372036854775907  B = (-1,-9223372036854775907)  O maximal: 1
  alpha = [-9/2, -9/2, -3/2, -3/2]  Nrd(alpha) = 41505174165846491622 = [2, 1; 3, 2; 727, 1; 1327, 1; 2390145843251, 1]
  I = O*alpha + O*2: left O-ideal 1, contained in O 1;  [O:I] = 4 = Mat([2, 2]) ;  n(I) = 2 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-9/2, -4, -3/2, -1]  Nrd(alpha) = 29975959119778021734 = [2, 1; 3, 1; 43, 1; 353, 1; 1589377, 1; 207086483, 1]
  I = O*alpha + O*3: left O-ideal 1, contained in O 1;  [O:I] = 9 = Mat([3, 2]) ;  n(I) = 3 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-9/2, -7/2, -3/2, -1/2]  Nrd(alpha) = 23058430092136939800 = [2, 3; 3, 1; 5, 2; 23, 1; 101, 1; 386719, 1; 42779309, 1]
  I = O*alpha + O*5: left O-ideal 1, contained in O 1;  [O:I] = 25 = Mat([5, 2]) ;  n(I) = 5 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-9/2, -4, -3/2, -1]  Nrd(alpha) = 29975959119778021734 = [2, 1; 3, 1; 43, 1; 353, 1; 1589377, 1; 207086483, 1]
  I = O*alpha + O*6: left O-ideal 1, contained in O 1;  [O:I] = 36 = [2, 2; 3, 2] ;  n(I) = 6 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-9/2, -7/2, -3/2, -1/2]  Nrd(alpha) = 23058430092136939800 = [2, 3; 3, 1; 5, 2; 23, 1; 101, 1; 386719, 1; 42779309, 1]
  I = O*alpha + O*4: left O-ideal 1, contained in O 1;  [O:I] = 16 = Mat([2, 4]) ;  n(I) = 4 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  alpha = [-7/2, -1/2, -1/2, 3/2]  Nrd(alpha) = 23058430092136939780 = [2, 2; 5, 1; 7, 1; 29, 1; 5679416278851463, 1]
  I = O*alpha + O*35: left O-ideal 1, contained in O 1;  [O:I] = 1225 = [5, 2; 7, 2] ;  n(I) = 35 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  principal O*beta, Nrd(beta) = 23058430092136939800: left O-ideal 1, contained in O 1;  [O:I] = 531691198313966362074243675708824040000 = [2, 6; 3, 2; 5, 4; 23, 2; 101, 2; 386719, 2; 42779309, 2] ;  n(I) = 23058430092136939800 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 0
  P = {x in O : p | Nrd x}: left O-ideal 1, contained in O 1;  [O:I] = 85070591730234617692071315155187672649 = Mat([9223372036854775907, 2]) ;  n(I) = 9223372036854775907 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 1
  6*O: left O-ideal 1, contained in O 1;  [O:I] = 1296 = [2, 4; 3, 4] ;  n(I) = 36 ;  [O:I] == n(I)^2 : 1
     O2 = conj(I)I/n(I): is order 1, I*O2 c I 1, maximal 1 [binary disc form anisotropic mod p], det Gram(O2,Nrd) = 85070591730234617692071315155187672649/16, equals p^2/16: 1, O2 == O as lattice: 1

==================== non-maximal controls at p = 13
O' = Z + 2O: is order 1, maximal 0, [O:O'] = 8, det Gram(O',Nrd) = 676 (= [O:O']^2 p^2/16 = 676)
I = 2O as left O'-ideal: left 1, [O':I] = 2, n(I) = 4  -> [O':I] == n(I)^2 : 0
Eichler O cap O2 (level 3): is order 1, maximal 0, det Trd form 1521, det Gram(E,Nrd) = 1521/16 (=(3p)^2/16 = 1521/16)
J = E cap 3O (left E-ideal? 1): [E:J] = 27, n(J) = 9  -> [E:J] == n(J)^2 : 0
P_E = E cap P: det Gram(P_E^0, Nrd/p) = 117/4  (p/4 * 3^2 = 117/4)
P_{Z+2O} = (Z+2O) cap P: det Gram(P^0, Nrd/p) = 52  Trd(P_{Z+2O}) = 26Z
```

*End of Section A. Phase B reads begin only after this section was written.*

---

## Phase B: setting

- **Phase B began at 2026-09-26T03:23:58Z.** This was after Section A was
  written to this path at 03:23:51Z. Section A's bytes were copied to scratch
  (`sectionA_as_written.md`, sha256
  `6d694d9ea8074b62e85dc75ba3c03336ab49698a4ddab0666f68e85d3a73260a`), and a
  byte comparison before this Phase B text was appended showed them unchanged.
- **Commits read.**
  - The producer artifacts under review were read at **`b4ae42bfd`** with
    `git show b4ae42bfd:<path>`.
  - The card was read in the working tree, which equals HEAD `6ec32c261` for
    that path: `git status` shows it unmodified.
  - `b4ae42bfd` is an ancestor of HEAD, and `git diff --stat b4ae42bfd HEAD`
    over `experiments/EXP-SSIQ-6916e8` and `H-SSIQ-a9df38` is empty.
  - `derivation-note.md` is **byte-identical** at `3ea7223b9` and `b4ae42bfd`
    (sha256 `9bd98c12841b8d51e67c3794573770d0a1aa4de381f16e1d900ddd93780bda7e`).
    That is the version reviewed.
  - Other revisions read:
    - `3d8faa394` (the specification, to check the v1 run-time commit);
    - `da16c1908` (the amendment blob);
    - `3ea7223b9` (the note).
- **Hashes verified by me.** Every committed run output matches its manifest's
  `output_sha256`:
  - v1 raw `2bbc828b…`, env `67ba8049…`, command `b0d70e85…`,
    stdout `34692a60…`, check.stdout `14a10bd3…`, stderr files empty;
  - v2 raw `a477d37c…`, env `381e4900…`, command `61159c7d…`,
    stdout `a6b2e179…`, check.stdout `c77b40ed…`, comparison `45e085df…`.

  The specification sha256 is `81db1913…350db` at `3d8faa394` and `b4ae42bfd`.
  The amendment sha256 is `678040641377…34e6` at `da16c1908` and `b4ae42bfd`.
- **Not verified, by design.** The sha256 values of the implementation files
  bound in both manifests were not checked against the committed blobs.
  Checking them means reading bytes under `implementation/`, which is
  `blind_from` (RV-2). See "Not done".
- **Scratch code.** All scratch code is my own, under
  `/tmp/claude-0/-home-user/5af2d3d8-0ba3-5d96-b05f-205cb058efcf/scratchpad/validator-eecb7f/`.
  Each process ran alone under `ulimit -v 4000000; timeout 900`. Scripts and
  outputs are reproduced verbatim in the appendix. No producer script was
  read or executed, and no scratch value is a contract cell (RV-6).

**How the verdict labels are assigned.** Labels follow each joint's text and
its `breaking_artifact` literally.

- For **J1** and **J2** the card's own breaking artifact was produced, so the
  label is `breaks`.
- The substance of both matches the Coordinator's modal expectation, which
  labelled the same findings "J1 holds with the geometric-Hom scope repair" and
  "J2 holds as a normalisation and instrument check".
- **J1:** statement-level wording break in H-SSIQ-a9df38 only. No mathematical
  step of the note fails.
- **J2:** the run is valid (J6), but it is not falsification-bearing for the
  lemma.
- Neither label is a finding of mathematical error.

---

## J1. Derivation note and interface: **breaks at statement level only; the note's mathematics holds**

**Verdict (attestation value): `breaks`, scoped as follows.**

- The breaking artifact the card defines was produced: "a computed pair
  (E, E') over F_{p^2} for which the statement as written fails". It breaks
  **H-SSIQ-a9df38's statement wording**.
- **Every mathematical step of the note holds**, for the geometric
  Hom-module, conditional on recalled standard inputs.
- No step of Sections 0-3, 5 or 6 is false.
- The repair is a wording repair, not a withdrawal.

**(a) Interface (D).**

*My statement, from Phase A knowledge (`recalled`).* Let `O ≅ End(E)`. For
every isogeny `φ: E → E'`, the kernel ideal `I_φ = {α ∈ O : α(ker φ) = 0}`
(equivalently, `{ψ∘φ : ψ ∈ Hom(E', E)}`) is a left O-ideal with:

- `n(I_φ) = deg φ`;
- `O_R(I_φ) ≅ End(E')`;
- `ψ ↦ ψ∘φ` an isometry `(Hom(E', E), deg) → (I_φ, Nrd/n(I_φ))`;
- dualisation an isometry `Hom(E, E') ≅ Hom(E', E)`.

Hence `(Hom(E, E'), deg) ≅ (I, Nrd/n(I))` for **the ideal class belonging to
E'** (Kohel 1996; Voight, Ch. 42, both recalled).

*Line 244, internal.* `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 244
at `b4ae42bfd` was opened. It says, verbatim as the note's Section 5 quotes it:
"the lattice of isogenies Hom(E, E^{(p)}) (with the quadratic form deg) is
isometric to the unique two-sided ideal P of reduced norm p in O (with the
quadratic form Nrd/p)." The citation is correct, with correct provenance.

*General pair.* The note is correct that Kohel and Voight are not in the repo;
the De Feo survey PDF exists but could not be read (see Not done). An in-repo
text does state the general-pair interface:

- **`inputs/JMV-0411378-20260907/sources/jmv-math-0411378v3.txt` lines
  1312-1325** (Jao-Miller-Venkatesan, arXiv math/0411378v3, retrieved
  2026-09-07 per `provenance.json`).
- It says: "isomorphism classes of supersingular curves Ei isogenous to E are
  in 1-1 correspondence with the left ideal classes Ii := Hom(Ei, E) of R …
  the set of equivalence classes of isogenies from Ei to Ej is equal to
  Ij−1 Ii modulo the units of Ij. This correspondence is degree preserving, in
  the sense that the degree of an isogeny equals the reduced norm of the
  corresponding element in Ij−1 Ii, normalized by the norm of Ij−1 Ii itself."
- That is (D) in the `Ij^{-1} Ii` convention, with `deg = Nrd/n(·)`.
- **Provenance: internal (opened by this validator).** It is a published
  statement in a retrieved copy, not a proof.
- The general pair can therefore be upgraded from `recalled` to `internal` in
  a *new* record naming `verified_by: validator TASK-20260926-eecb7f`. The
  note is immutable.

My scratch check shows the determinant is unchanged in that convention. At
p = 13, with `Ii` of norm 3 and `Ij` of norm 5,
`J = Ij^{-1} Ii = conj(Ij) Ii / n(Ij)` scaled to be integral gives
`det(cJ, Nrd/n(cJ)) = 169/16 = p^2/16` (`phaseB_scratch.out`, J1(a)).

*Convention independence (note Section 5, lines 218-223).* This holds
algebraically:

- conjugation is an Nrd-isometry;
- `n(Ibar) = n(I)`;
- `I^{-1} = Ibar/n(I)`, and `Nrd·n(I)` on `I^{-1}` is `Nrd/n(I)` on `Ibar`.

Scratch at p = 13 gives all three determinants equal to 169/16.

*Every pair has a connecting ideal.* Any two supersingular curves over
`F_p-bar` are isogenous (`recalled`: connectedness of the supersingular
ℓ-isogeny graph). JMV lines 1300-1320 of the same file treat all supersingular
classes as vertices of one isogeny graph, but I did not trace a proof. So this
stays recalled.

*Wording defect in (D) (minor; does not affect the determinant).* Note line
203 characterises the ideal as "a left O-ideal I connecting O to
O_R(I) ≅ End(E')". An isomorphism type of right order does not determine E'
(`recalled`): E' and its Galois conjugate `E'^{(p)}` have isomorphic
endomorphism rings. So (D) should be stated for **the ideal class
corresponding to E'** (as JMV does), not for any I with `O_R(I) ≅ End(E')`.
The determinant claim is untouched, because `det(I, Nrd/n(I)) = p^2/16` for
every invertible I with maximal left order (Lemma S).

*Cited, not silently computed.* Confirmed. No curve or isogeny appears in
either raw-result.json. The run is pure quaternion arithmetic, and
note §5 (lines 224-227) says so.

**(b) Field-of-definition attack (the breaking artifact).** This is my own
naive point count over `F_{p^2}` of `y^2 = x^3 + g^e x`, e = 0..3, with g a
multiplicative generator. It was cross-checked against PARI `ellcard`
(`phaseB_scratch.out`, J1(b)):

| p | curve | #E(F_{p^2}) | trace t | Frobenius |
| --- | --- | --- | --- | --- |
| 7 | E: y^2 = x^3 + x | 64 = (p+1)^2 | -14 | π = -p |
| 7 | E^t: y^2 = x^3 + g^2 x (quadratic twist) | 36 = (p-1)^2 | +14 | π = +p |
| 7 | E_g: y^2 = x^3 + g x (quartic twist) | 50 = p^2+1 | 0 | π^2 = -p^2 |
| 11 | E | 144 | -22 | π = -p |
| 11 | E^t | 100 | +22 | π = +p |
| 11 | E_g | 122 | 0 | π^2 = -p^2 |

*Argument.*

- An F_q-rational isogeny φ satisfies `φ∘π_E = π_{E'}∘φ`.
- For E, E^t this reads `φ∘[-p] = [p]∘φ`, i.e. `[2p]∘φ = 0`, so φ = 0.
- Equivalently, `#E(F_q) = deg(1-π)` is an F_q-isogeny invariant, and 64 ≠ 36.
- **So `Hom_{F_{p^2}}(E, E^t) = 0`: rank 0.**
- The geometric Hom has rank 4, since `E^t ≅ E` over `F_{p^4}`.
- For the quartic twist, `π = p·ι` with `ι^2 = -1`, so `End_{F_{p^2}}(E_g)` is
  the centraliser of ι, **rank 2**. It contains `Z[ι]` with deg-Gram `I_2`,
  det 1.

*Ruling.*

- **H-SSIQ-a9df38's statement is false as written under the natural reading**
  (curves over `F_{p^2}`, Hom over `F_{p^2}`). Counterexamples at p = 7 and 11:
  the pair (E, E^t) has Hom of rank 0, and the pair (E_g, E_g) has Hom of rank 2.
- **It is true for the geometric Hom** (over `F_p-bar`), equivalently for
  `F_{p^2}`-models of the pair that both have Frobenius -p (or both +p).
- The note's Section 4 (lines 169-170, "full homomorphism module over F_p-bar") uses
  the geometric Hom, so the note is correct.
- Its parenthesis (lines 171-173), "Over a model on which all homomorphisms
  are defined, this is the F_{p^2}-module", **repairs the note but not H**.
  H's statement never says "over F_p-bar". The same wording also appears in the
  source proposal (IDEA-20260926-e1b48e line 39) and in H's `quantifier_order`
  ("FORALL supersingular E, E' / F_{p^2}").
- The evidence record should carry the repair: "Hom over `F_p-bar`" or "for
  `F_{p^2}`-models with equal Frobenius ±p".

**(c) Step walk. Every step checks.**

| step | status | input |
| --- | --- | --- |
| §0 polarisation, T = 2A, det T = 16 det A | derived; checked | none |
| §0 n(I) = gcd(A_ii, 2A_ij); [M:L] = \|det H\| | derived | none |
| §1 Lemma C | derived (Smith form) | none |
| §2 disc(O) = p^2 | **recalled** in the note | I re-derived it in Section A from the recalled local structure (R3, R4); still conditional |
| §2 Step 1 conjugation map | holds | its determinant is exactly **-1** (scratch: -1 on the Hurwitz order and at p = 13). That is harmless: the note takes \|det\| and fixes the sign by definiteness |
| §2 hand checks | reproduced | Hurwitz matrix det = 1/4; my Hurwitz Gram equals the note's matrix; block `[[1,1/2],[1/2,(1+p)/4]]` has det p/4 symbolically |
| §3 local principality; O_R(I) maximal | **recalled** | Voight |
| §3 det(ρ_α) = Nrd(α)^2 | derived in the note (splitting field, rows); correct | none |
| §3 (S1), (S2), (S3) | derived; agree with Section A Q2 | none |
| §3 method note on P | holds with one looseness: "p \| Nrd on a basis" does not by itself give p \| Nrd on the lattice (the 2A_ij terms). The identification still follows from two-sidedness plus [O:P] = p^2 (two-sided ideals containing pO are O, P, pO; recalled) | my anisotropy check (Section A) verifies P directly |
| §6 Fact 1, Trd(O) = Z | p odd: derived. p = 2: **recalled** (class number 1) | avoidable: Section A uses 1/2 ∉ P^{-1} locally |
| §6 Fact 2, Trd(P) = pZ | **recalled** local structure O_p = S + Sπ | — |
| §6 Steps 1-3 | derived; agree with Section A Q3 | none |

*Tier.* "Derivation tier" here means **conditional on recalled standard
facts**:

- disc(O) = p^2;
- hereditary maximal orders (local principality);
- the local structure at p;
- class number 1 at p = 2 (avoidable);
- all supersingular curves being isogenous;
- the general-pair Deuring interface, which is now in-repo via JMV.

Under AGENTS rule 9 and validator item 9, these are recalled references doing
real work. That is **incomplete evidence, not fabrication**, and the evidence
record must list them.

**(d) Comparison with Section A.** Agreement on all three quantities. The
methods differ at two points:

- For Q1 I derived disc(O) = p^2 locally; the note cites it.
- For Trd(O) = Z at p = 2 I used a local argument; the note uses class
  number 1.

No disagreement to localise.

*Paths and lines read for J1.*

- note lines 1-369;
- H lines 1-272;
- Wesolowski lines 236-252 and 81;
- JMV txt lines 1300-1345 and `provenance.json` head;
- git-grep hit lines under `inputs/` and `knowledge/` (listed in the
  attestation);
- IDEA lines 26-70 and 270-280.

---

## J2. Can the computation fail? **breaks as stated: no arm is falsification-bearing for the lemma**

**Verdict: `breaks`.** The joint asserts the arms are falsification-bearing for
the lemma. The card's breaking artifact is "a written demonstration that every
arm reduces to (i)-(v), together with the list of failure modes the run could
and could not detect", and it is produced here.

This does **not** impugn the run's validity (J6 holds). It fixes what the 945
cells can carry. This matches the Coordinator's prior (0.85).

**(a) Classification** (spec lines 116-167 and 173-235; amendment lines
116-196):

| item | exact statement checked | class |
| --- | --- | --- |
| A1 (PARI order), R = 1 | det(T) = p^2 for PARI's stored order | **(i)**: given an order in B_{p,∞}, disc = [O_max:O]^2 p^2, so R = 1 ⇔ the order is maximal (given Lemma B) |
| A2 (hand order), R = 1 | same | (i); the contract already scores R ≠ 1 as D-STD (instrument) |
| A3 (P, Nrd/p), R = 1 | [O:P] = p^2 on a maximal base, plus Lemma C | (ii) + (iii) |
| A4 R = 1 and M-INDEX | [O:I] = n(I)^2 and det(I, Nrd/n) = p^2/16 | (ii): a theorem for every invertible ideal, and every left ideal of a maximal order is invertible |
| A5 (right orders), R = 1 | disc(O_R(I)) = p^2 | (i), with maximality of O_R(I) a theorem (ii) |
| A6 (sublattices) | det(H^T A H) = det(H)^2 det A | (iii) |
| C-TRD | det T / det A = 16 | (iii)/(iv) |
| C-NOSCALE | ratio n^4 | (iii) |
| C-NONMAX | index 8, ratio 64, trace det ≠ p^2 | (iii) + (i) (the maximality test run in reverse) |
| C-NEAR | p^2/4, p/4 | (ii) + (iii) |
| C-ALG, C-CROSS | validity and cross-instrument checks | (v) |
| genuinely about Hom(E, E') | — | **(vi) is empty**: no curve is constructed |

The only way the arms could have "come out otherwise" on correct instruments is
a wrong constant in the note. For example, a convention slip giving p^2/4 would
show R ≠ 1 everywhere. So the run is a real check of the **note's stated
normalisation constant under the frozen Gram convention** (class (iv)). It is
not a check of any mathematical proposition beyond the definitions.

C-NONMAX's trace-form determinant (recomputed below: ≠ p^2 at 22/22, equal to
64 p^2) is exactly the maximality criterion that A1's R = 1 applies in the
other direction. One nuance: G-A2 (amendment lines 163-168) uses "R = 1" as the
maximality certificate for the fallback base. That relies on Lemma B itself.
My scratch `maxtest` confirms that base's maximality independently (J5).

**(b) Failure modes: what the contract would have scored.**

The following were **produced**, not only described (`j2_faults.out`, p = 13):

| fault | passes the C-ALG it would face? | R | contract code |
| --- | --- | --- | --- |
| A1: a non-maximal order returned as "maximal" (Z + 2O) | C-ALG(c) [order, Nrd integral, Trd integral] = [1,1,1] | 64 | **F-NORM** (falsification) though it is an instrument fault |
| A5: a suborder of the true right order (Z + 2 O_R(I)) | C-ALG(c) = [1,1,1]; C-ALG(d) `I·O' ⊆ I` = 1 | 64 (true O_R(I): 1) | **F-NORM**, though an instrument fault |
| A3: pO returned as P | C-ALG(e) [OP⊆P, PO⊆P, p\|Nrd on basis] = all 1 | 28561 = p^4 | **F-NORM**, though an instrument fault |

The A5 mode is not hypothetical. Execution-report.yaml D-8 (lines 243-245)
records that a pre-run bug in the A5 right-order computation "gave non-maximal
lattices". Had it reached the run, the contract would have scored it as a
falsification of the closure.

Further modes:

- A misnormalised polarisation: C-TRD ratio ≠ 16 → INVALID. Correctly an
  instrument code.
- Nrd confused with the absolute norm: C-ALG(b) → STOP/F-INSTR. Correct.
- Wrong algebra: C-ALG(a). Correct.
- A6 index error: F-SUB, "treated first as a suspected instrument defect".
  Acceptable.
- n(I) mis-measured by a conceptual error shared by both instruments:
  **F-NORM**. The invalidation rule at spec lines 394-395 covers only deriving
  one of n and index from the other.

**Contract-design defect (confirming the prior's 0.40).** F-NORM on A1, A3 and
A5 can be triggered by instrument or construction faults that C-ALG does not
catch. No arm carries an independent maximality certificate for PARI's orders.
The headline "a single mismatch surviving the instrument cross-check falsifies
the closure as stated" (spec lines 66-68) overstates what an R ≠ 1 would have
meant. It is moot here: no R ≠ 1 occurred. It bears on how the contract may be
quoted.

**(c) Recomputation from the committed raw data.** This covers **every** cell,
not a sample (`recompute_v2.py` → `recompute_v2.out`). For all 22 primes:

1. The PARI structure constants were verified: unit, associativity of all 64
   triple products, stage-2 table equal to stage 1.
2. The recorded images of i, j, k were verified: i^2 = a, j^2 = b, ij = k = -ji.
3. Every PARI-side basis was then mapped to (1,i,j,k) coordinates.
4. **Every Nrd Gram was rebuilt** with my own formula under the frozen
   convention, and every determinant recomputed by my own exact elimination.

Results:

- 1517 computed records, 0 mismatches against the recorded `gram`,
  `det_python`, `det_pari`, R and R_sub.
- R = 1 at A1 21/21, A2 22/22, A3 22/22, A4 440/440, A5 440/440.
- R_sub = 1 at 484/484, including 44/44 at m = 1024. The index from bases
  equals m at 484/484.
- A3: [O:P] = p^2 and n(P) = p at 22/22.
- A4: [O:I] = n(I)^2, n(I) = target, and form scale = n(I) at 440/440.
- C-NOSCALE: ratio n^4 and R ≠ 1 at 440/440.
- C-TRD: ratio 16 and R(T) = 16 at 22/22.
- C-NONMAX: index 8, R = 64, trace det ≠ p^2 at 22/22.
- C-NEAR: O^0 = p^2/4, P^0 = p/4, trace-zero bases, and p | Nrd on the P^0
  basis at 22/22.
- M-CROSS (ii): the algnorm Gram equals the regular-representation Gram on
  1495/1495 records (`j6_obligations.out`).

**(d) Evidential weight of the 945 cells.**

- **Normalisation inputs:** high. The constant 16, T = 2A, reduced versus
  absolute norm, the n(I)^{-4} rescaling and the index-2 C-NEAR structure are
  all confirmed exactly at 22 primes, including p = 2, 3 and ~2^255. A handful
  of primes would carry nearly the same weight.
- **Deuring interface:** zero. It is not in the run.
- **Universal statement:** none beyond the normalisation. It is a theorem-shaped
  claim resting on the note. The finite sample neither adds logical support nor
  could have refuted it except through an instrument fault.

---

## J3. Hermite certificate and relevance to the admissibility criterion: **holds, with a relevance caveat**

**Verdict: `holds`.** The mathematics is right. The criterion's reading is
identified, and H and the note are correctly scoped. The quotation half of the
breaking artifact exists (below), but **no sentence in H, the note, or the
proposed goal-record consequence overstates**. An overstatement exists only in
the source proposal IDEA (see J4 and PT-6).

**(a) Hermite.**

- `γ_4 = 2^{1/2}` in the convention `min q ≤ γ_4 det(A)^{1/4}` with
  `q = x^T A x` (`recalled`: Korkine-Zolotarev).
- Checked numerically (`phaseB_scratch.out`, J3(a)):
  - Hurwitz order at p = 2: min Nrd = 1, det = 1/4, min/det^{1/4} = 1.41421… = √2 (equality).
  - D4: min 2, det 4, ratio √2.
- Direction: det(L) ≥ m^2 p^2/16 makes the certified bound
  `γ_4 det^{1/4} ≥ (γ_4/2) m^{1/2} p^{1/2}`. That is weaker (larger), and it
  says nothing about the actual minimum.
- The constant `(c_4/2) p^{1/2} = 2^{-1/2} p^{1/2}` is right (note §4 item 4,
  lines 181-187).

**(b) The criterion at its source.**

- The admissibility condition was derived in
  **`coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/reviews/RT-BATCH-001.md`
  lines 137-159**: "For a positive-definite quadratic form the Hermite exponent
  is `log_p(det)/rank`; reaching `1/4` needs `log_p(det)/rank ≤ 1/4`, which
  admits **rank 4 with `det ≲ p`** … `rank > 3` is precisely where N5's own
  third case — *higher-dimensional objects (superspecial abelian surfaces)* —
  lives" (lines 145-148).
- The same text continues: "Raising the ambient dimension changes the
  homogeneity degree of the degree form (it is quadratic on `Hom` of elliptic
  curves; it is not quadratic on `Hom` of higher-dimensional abelian
  varieties)" (lines 152-154).
- It was carried into DEC-20260805-2be965 D-5 (lines 102-104) and into
  goal.yaml `exponent_budget_corrections` (lines 575-581).
- So the reading is **(i), a Hermite/Minkowski upper bound**.
- RT-BATCH-002.md lines 575-581 later glosses the N5 question as "does the
  candidate object's governing lattice fail to be generic of determinant ≍ p",
  which gestures at (ii).

Under each reading, rank 4 inside a single g = 1 Hom-module under deg has
determinant ≥ p^2/16:

- **(i)** The certificate exponent is ≥ 1/2 − log_p 2. **Closed** rigorously.
- **(ii)** Gaussian-heuristic typical minimum: the exponent is 1/2. That is a
  heuristic statement, and "certificate" misdescribes it. Structured lattices
  can have far smaller minima (PT-4).
- **(iii)** Counting: #{x : q(x) ≤ X} ≈ (π^2/2) X^2 / √det ≤ 2π^2 X^2 / (m p),
  so X ≳ p^{1/2} is needed. Same exponent, heuristic for small X.

**(c) Relevance, confirming the prior's 0.60 as a caveat rather than a break.**

- The criterion's authors located the rank-4 option in **g ≥ 2 superspecial
  abelian surfaces**, not in single g = 1 Hom-modules.
- The lemma is therefore correct, but it closes an instance the criterion never
  relied on: the g = 1 single-Hom sub-case, for every target E' and every
  full-rank sublattice.
- That sub-case includes one real N5 sub-branch: prescribed-torsion targets,
  whose compatible isogenies form a full-rank finite-index sublattice. It
  excludes oriented targets (rank 2) and g ≥ 2.
- H's consequence (H lines 24-28) keeps every qualifier: "single Hom(E, E')",
  "under deg", "DIMENSION ONE", "N5 is NOT closed". So it is correctly scoped.
- Any adoption into GOAL-SSIQ-001 must keep all of: **rank 4 (full rank),
  single Hom-module, degree form, g = 1, geometric Hom**. Dropping "single
  Hom-module" is false (PT-6). Dropping "full rank" is false (PT-1, PT-2).

**(d) Asymptotics.**

- The exponent is `1/2 + log_p(m)/2 − log_p 2` against 1/4.
- Note §4 item 5 (lines 188-195) enumerates `p m^2 ≤ 16`:
  p ∈ {2,3,5,7,11,13} at m = 1 and p ∈ {2,3} at m = 2. I verified the
  enumeration.
- It is illustrative of the literal "≤" and is **not load-bearing**: neither H
  nor the proposed consequence cites it, and the criterion's "≲" is asymptotic.

---

## J4. Proves too much: **holds, with two wording hazards**

**Verdict: `holds`.** On every PT object the note's argument stops at a named
step (see "Proves-too-much" below). No object gets det ≥ p^2/16, exponent
≥ 1/2, or a floor on an actual minimum from the argument as written. None of
H, the note, or the proposed consequence asserts a false conclusion on any of
them.

Wording hazards to fix in the evidence record. These are not mathematical
failures:

1. **Floor reading (PT-4).**
   - Note §4 item 3 (line 180) calls `log_p det(L)/4 ≥ 1/2 − log_p 2` "the
     **exponent floor**".
   - H (lines 15-17) says a certificate "can never certify a nonzero isogeny
     E → E' of degree below (c_4/2) p^{1/2}".
   - Both are correct as statements about the determinant and the certificate
     bound. Both are readable as a floor on isogeny degrees, which PT-4
     refutes: min deg 1 on End(E), and 2 on a 2-isogenous pair, at p = 103.
   - The note's own lines 197-199 and H's `assumptions` (lines 55-59) disclaim
     the floor.
   - Suggested evidence wording: "lower bound on the certificate's
     determinant exponent; not a lower bound on any isogeny degree".
2. **Unqualified closure in the source proposal (PT-6).**
   - IDEA-20260926-e1b48e says "Dimension-one N5 via rank 4 is closed" (title,
     line 33) and "Any change of auxiliary target E' within dimension one, for
     a rank-4 certificate, is closed" (lines 276-277).
   - Its "remains open (ii)" (lines 63-65) says "a direct sum over targets has
     rank 8 … exponent 1/2 again". That reads as if multi-module lattices were
     also closed.
   - PT-6 (rank 4, det 1, inside End(E) ⊕ End(E), g = 1) makes the first
     sentence false without "single Hom-module", and shows the second covers
     only the full rank-8 sum.
   - IDEA is outside the three texts J4 polices, but no successor record
     should inherit its wording.

---

## J5. The blocking A1 cell: **holds**

**Verdict: `holds`.** The raise is a PARI 2.15.4 maximal-order-routine defect
that is independent of the claim. The code INCONCLUSIVE-CONSTRUCTION is the one
the contract dictates. The decision rulings are below.

**(a) From the record.** The v2 `prime_status["9223372036854775837"]` gives:

- **route_attempts:**
  - R1 `alginit(nfinit(y), [-2, -9223372036854775837])`, maxord 1,
    `setrand_before_alginit: 1`, error `error(impossible inverse in dvmdii: 0.)`;
  - R2 `alginit(nfinit(y), [-9223372036854775837, -2])`, maxord 1, setrand 1,
    same error;
  - R3 `alginit(nfinit(y), [-2, -9223372036854775837], , 0)`, maxord 0,
    setrand 1, error null.
- **R3 checks:**
  - `calg_a`: ramified_finite [p], ramified_infinite_count 1,
    `algramifiedplaces_ok` true, Hilbert {2: 1, p: -1, inf: -1};
  - `calg_b`: Nrd(1) = 1, Nrd(2) = 4;
  - `structure_constants_reproduce_algmul` true;
  - `ijk_relations_ok` true;
  - stage-2 call identical, stage-2 multiplication table equal to stage 1;
  - `g_a2` pass with R = "1".
- **v1:** `stage1_error` is the same string, base "none".
- **`stderr.log` of both runs is empty** (0 bytes, sha256 `e3b0c442…`). The
  errors live in raw-result.json, not in stderr.

My checks:

- The mapped base Gram equals the Python A2 Gram at that prime (base basis
  `[1, (1+j+k)/2, (i+2j+k)/4, k]`; det `85070591730234616400799229995519050569/16`
  in both).
- My structure-constant and ijk verification passed there, as at every prime
  (J2(c)).

**(b) By hand.**

- p = 9223372036854775837 = 2^63 + 29, and p ≡ 5 mod 8.
- `(-2, -p)_p = (-2/p) = (-1/p)(2/p) = (+1)(−1) = −1`: **ramified at p**.
- At ∞, a, b < 0: ramified.
- At 2, with u = −1 and v = −p ≡ 3 mod 8: `(2u, v)_2 = (−1)^{ε(u)ε(v) + ω(v)} = (−1)^{1+1} = +1`. Split.
- No other prime divides 2ab.
- So B = B_{p,∞}. PARI agrees: `hilbert` gives 1 at 2 and −1 at p;
  `kronecker(-2,p) = −1`.

**(c) Reproduction** (`j5_pari.gp` → `j5_pari.out`, one gp process):

- R1 and R2 with `setrand(1)` both raise `error("impossible inverse in dvmdii: 0.")`.
- R3 with flag 0 initialises: `algramifiedplaces = [1, [p, [p]~, 1, 1, 1]]`,
  algnorm(1) = 1, algnorm(2) = 4.
- Three diagnostics, all of which **raise the same error**:
  - D1: nf variable `t` instead of `y`;
  - D2: the equivalent presentation `[-2, -9p]` (same algebra; 9 is a square);
  - D3: parisize 4·10^8.

The raise is deterministic and insensitive to the variable name, to scaling
the presentation by a square, and to stack size. It is specific to PARI's
default maximal-order computation for this algebra at this p. (An earlier
invocation of my script failed on gp closure syntax before any alginit call
ran. It is disclosed in the appendix and counted as no diagnostic.)

**(d) Independence.** No mechanism links the raise to the determinant claim.

- The algebra is verified to be B_{p,∞}.
- A maximal order demonstrably exists there: my own `maxtest` proves the A2
  order maximal at this p by a Lemma-B-free test (O^#/O ≅ (Z/p)^2 with an
  anisotropic discriminant form; `phaseB_scratch.out`, J5 line). It also has
  det(O, Nrd) = p^2/16, P = the radical (anisotropy check), and
  det(P^0, Nrd/p) = p/4.
- The failing routine's job is only to produce such an order.
- Scratch values are diagnostics, **not an A1 cell** (RV-6).
- The raise is infrastructure/tool behaviour and is evidence about nothing
  (RV-7).

**(e) Code and decisions.**

*Tally re-derived* from the amendment `tally_rule` (lines 201-247) and my
recount of `counts.item_states` (2398 items):

- 945 primary + 484 sub + 462 index + 506 control items are COMPUTED_VALID.
- One primary item, `9223372036854775837:A1`, is NOT_COMPUTED with cause
  CONSTRUCTION.
- No COMPUTED_EXCLUDED item.
- No computed control ratio or index differs from its pre-registered value, so
  not INVALID.
- No computed R ≠ 1 and no index ≠ n^2, so not F-NORM.
- No R_sub ≠ 1, so not F-SUB.
- No instrument disagreement, so not F-INSTR.
- No INFRASTRUCTURE cause, so not F-INFRA.
- A2 is valid with R = 1 at 22/22, so not D-STD.
- C-NEAR is exact at 22/22, so not INCONCLUSIVE-NEAR.
- The only trigger is **INCONCLUSIVE-CONSTRUCTION**, which matches the
  record. S1 is false; S2-S5 are true.

Rulings:

1. **SUCCESS / S1 under any reading: no.**
   - S1 requires all 946 planned lattices valid with R = 1 (spec lines
     409-410).
   - The amendment says in terms that "S1 still requires … A1 at every prime"
     and that an R3 prime "leaves its A1 cell not computed, so S1 and therefore
     SUCCESS cannot hold" (amendment lines 181-189).
   - `success_unchanged` says a NOT_COMPUTED item "is never a pass either"
     (lines 232-236).
2. **Admitting R3/A2 as A1 after the outcome** would change a success
   criterion after the outcome: **yes, forbidden**. The amendment explicitly
   declined it "because A1 is the independent PARI instrument and A2 already
   occupies the hand-written slot" (lines 186-189).
3. **A legitimate clearing route** needs all of the following:
   - a new pre-registered amendment, committed before any run;
   - a new, independent maximal-order instrument. My D1-D3 suggest another
     presentation or the same PARI routine will keep failing, so the candidates
     are another PARI version, another algorithm with its own positive and
     negative controls, or the WISDE/AOV order source named in spec
     `out_of_scope`;
   - a new RUN id, whose outcome is its own. RUN-SSIQ-004595's code stays as
     recorded, and no cell is pooled into it.
4. **Bearing on the universal statement: none.**
   - The statement rests on the note.
   - One more PARI-side A1 cell would add one more instance of a class (i)
     identity already checked on 21 PARI orders, 22 hand-written orders and 440
     right orders.

---

## J6. Run-set validity and amendment obligations: **holds, with summary and schema notes**

**Verdict: `holds`.** No artifact-policy field whose absence makes a run
"not evidence" is missing. There is no seed mismatch and no data/summary
disagreement in any measured count or state. Every amendment obligation is
met. The defects below are summary-text or procedural and are disclosed.

**(a) Run count.**

- `git ls-tree b4ae42bfd experiments/EXP-SSIQ-6916e8/runs/` shows `.gitkeep`,
  `RUN-SSIQ-004595` and `RUN-SSIQ-81bd08`: exactly two runs.
- The v2 outcome derives from v2 records alone. The v2 raw data holds its own
  complete records at all 22 primes.
- The comparison is report-only. No v1 cell is pooled.

**(b) Schema.** Both manifests carry:

- exact command (with `command.txt`);
- commit and dirty state with porcelain;
- environment and versions, including the gp version and the binary sha256
  `c9673623…` (identical in both runs);
- parameters and seeds;
- inference block;
- stdout and stderr;
- raw results;
- validity status and reason;
- timestamps and resources.

Git order: the design was committed at `254729199` (01:52:18) before v1 ran
(02:12:25), with HEAD `3d8faa394` a descendant and the specification
byte-identical. The amendment `da16c1908` (02:31:37) precedes the v2 run
(02:47:34), so pre-registration holds.

Notes:

1. **D-9.** v1 `gp_version_full` is empty (v1 manifest lines 130-134). This is
   **immaterial**. The version string 2.15.4 is present, and the binary sha256
   equals v2's, whose full banner is recorded. It is not "schema-incomplete".
2. **Inference.** Both executor handoffs declared `fallback_allowed: false`,
   yet both runs record `fallback_used: true` (served `claude-opus-5-5` instead
   of `claude-sonnet-5`, forced by `model: inherit`). This is a disclosed
   procedural deviation. It has no bearing on deterministic exact arithmetic.
3. **Arithmetic slip in the summaries.**
   - v2 manifest lines 50-52 and execution-report-v2.yaml line 440 give the
     total as "1946" ("946 + 484 + 462 + 506 = 1946").
   - The sum is **2398**, and `counts.item_states` has 2398 entries (2397
     COMPUTED_VALID + 1 NOT_COMPUTED).
   - Every per-category count is right. Only the stated total is wrong.
4. **v1 count wording.**
   - The v1 report (lines 32-35, 53-55) and the amendment's d3_adjudication
     (lines 255-257) call the blocking set "the 64 PARI-side cells (A1, A3,
     A4_1..20, A5_1..20, A6_0..21, C-TRD, C-NONMAX, C-NEAR, C-NOSCALE_1..20)".
   - The list names 64 lattices plus 23 controls, 87 items in all. My v1 count
     is 64 invalid lattice records, all at that prime.
   - Cosmetic; the ruling is unaffected.

**(c) Seeds.** I recomputed
`seed(arm,p,k) = int(sha256("20260926:<arm>:<p>:<k>").hexdigest()[:16],16)`
for **all 924** (A4 k = 1..20, A6 k = 0..21, at 22 primes). They match
`prime_status` 924/924 and the per-record `seed` fields 924/924. The v1 seeds
are identical to v2's.

**(d) Raw versus summary.** My own script recounts:

- 946 primary items: 945 valid, 1 NOT_COMPUTED;
- 484 A6;
- 462 M-INDEX;
- 506 control values;
- per-arm tallies, control results and M-CROSS = 0.

All equal the execution report and manifest, apart from the stated "1946"
total above.

**(e) Amendment obligations.**

1. The ladder was entered iff R1 raised: true at all 22 primes. `setrand(1)`
   preceded every call. The routes used are {R1, R3}, and no unlisted route
   was used.
2. No R2 prime exists: confirmed, `[]`.
3. At the R3 prime, G-A2 was evaluated (pass, R = 1), and the mapped base Gram
   equals the Python A2 Gram: confirmed.
4. No NOT_COMPUTED item appears as a mismatch: `controls_failed`, `F_NORM`,
   `M_INDEX` mismatches and `INVALID` are all `[]`.
5. **Comparison file identity:** my own comparison covered **all 1449 lattice
   records and 483 control records** at the 21 shared primes. Every compared
   field (basis, gram, dets, R, R_sub, H, seed, alpha, n, index, both Nrd
   Grams, validity) is identical. There are no v2-only ids at shared primes,
   and all 1450 valid v1 determinants recompute exactly. The file's own totals
   (1995 records, 52479 fields, 0 differences) are consistent.
6. **d3_adjudication is correct under v1's text.**
   - "C-NEAR mismatch" requires a computed value, and C-NEAR was exact at all
     21 computed primes.
   - The stopping rule makes a prime with no base order
     INCONCLUSIVE-CONSTRUCTION.
   - INVALID needs a computed ratio that differs, and none does.
   - The v1 raw label INCONCLUSIVE-NEAR is a derived-label defect (D-3).
   - v1's code is therefore INCONCLUSIVE-CONSTRUCTION, as a case of the
     umbrella INCONCLUSIVE with blocking cells named.

**(f) Note version.**

- The note is byte-identical at `3ea7223b9` and `b4ae42bfd`
  (sha256 `9bd98c12…`), and it was first committed at `3ea7223b9` together
  with RUN-SSIQ-81bd08.
- **Neither manifest binds its sha256.** v1 binds only the three
  implementation files. The amendment's C-7 (lines 374-376) says
  "RUN-SSIQ-81bd08's manifest binds their sha256 values" of "the version-1
  implementation files and derivation-note.md". For the note that is
  **inaccurate**.
- v1 `environment.json` `git_status_porcelain` lists
  `?? experiments/EXP-SSIQ-6916e8/derivation-note.md` at run start
  (02:12:25Z). So the note's **existence** before the run is recorded, but its
  **content** at that time is not checkable.
- Section 9 (lines 329-369) was appended after the run (D-10). S6's "existed
  before the run" is therefore attested, and only partly evidenced.
- **J1 reviewed the committed version** (with Section 9).

---

## J7 (Phase B comparison): **holds**

My blind values were Q1 = p^2/16, Q2 = n(I)^2 and Q3 = p/4 for every p,
including 2. They agree with:

- note (B), line 80;
- (S1), line 122;
- the §6 result, line 280;
- RUN-SSIQ-004595: R = 1 on 945/945 A1/A2/A3/A4/A5 cells, [O:I] = n(I)^2 on
  462/462, and C-NEAR p/4 on 22/22 (my recount).

The two derivations differ only in the recalled inputs they lean on (J1(d)).
No disagreement to localise.

---

## Proves-too-much

Values from `phaseB_scratch.out` (own code). The steps cited are the note's.

| object | computed (rank, det, min) | known-false conclusion | where the note's argument stops (section, line) | result |
| --- | --- | --- | --- | --- |
| **PT-1** (P^0, Nrd/p), p = 13, 17, 101 | rank 3; det 13/4, 17/4, 101/4 = p/4 exactly; log_p(det)/3 = 0.153, 0.170, 0.233 (→ 1/3); min 1 at each (these orders contain √-p); γ_3 det^{1/3} = (p/2)^{1/3} = Theorem 1.5's constant (line 81) | exponent ≥ 1/2 | Lemma C needs L and M of the same rank (lines 46-47). Theorem item 2 needs a full-rank L (line 177). §6 says so (lines 285-286) | **stops: full rank** |
| **PT-2** Z[i] ⊂ End(E), E: y^2 = x^3+x, p = 7, 11, 103 | rank 2; Gram I_2, det 1; log_p(det)/2 = 0 ≤ 1/4 (admissible rank-2 certificate) | any rank-2 extension of the closure | full rank (lines 46-47, 177). §7 item 1 leaves rank ≤ 3 open (lines 301-303). H: "every full-rank (rank-4) sublattice" | **stops: full rank** |
| **PT-3** O^#, p = 13, 17 | rank 4; det 1/2704, 1/4624 = det(O)/[O^#:O]^2 = 1/(16p^2); Nrd on the basis includes 10/13, 5/13 (p = 13) and 1/17, 6/17 (p = 17): not integral | "every rank-4 lattice in B under Nrd has det ≥ p^2/16" | L must lie inside an integral Hom(E, E') with deg (line 177; Lemma C needs L ⊆ M). (O^#, Nrd) is not (Hom, deg): the Hom-normalised form on O^# = P^{-1} is p·Nrd, which gives p^2/16 again | **stops: integrality / Hom membership** |
| **PT-4** actual minima, p = 103 | End(E): min deg 1 (the identity) against the certificate bound (√2/2)√103 ≈ 7.18. Hom(E, E') for a 2-isogenous E' (I = Oα + 2O, n = 2, right order maximal): det p^2/16, min deg 2 | floor reading: no isogeny of degree below (c_4/2)p^{1/2} | Upper-bound direction: §4 item 4 bounds the certified value, and lines 197-199 say "never floors" | **stops: direction**. Wording hazards: "exponent floor" (line 180) and H lines 15-17 (see J4) |
| **PT-5** L1 and C-NEAR | C-NEAR in RUN-SSIQ-004595: det(P^0, Nrd/p) = p/4 at 22/22 and det(O^0, Nrd) = p^2/4 at 22/22 (my recount). L1: goal.yaml lines 591-602, CLOSED-IN-SCOPE on pillar D1 (a different argument). γ_3 (p/4)^{1/3} = (p/2)^{1/3} (EV-SSIQ-e43afd line 159; my check at 13, 17, 101) | re-closing, re-opening or contradicting L1; closing N5 | §6 "rank-3 route to p^{1/3} is untouched" (lines 285-288). §7 items 1 and 3 leave rank ≤ 3 and g ≥ 2 open (lines 301-307). H "N5 is NOT closed" | **stops: scope**. Neither re-closes nor contradicts L1; N5 untouched |
| **PT-6** Z[i] ⊕ Z[i] ⊂ End(E) ⊕ End(E), p = 7, 11, 103 | rank 4; Gram I_4, det 1 ≤ p | "rank-4 det ≲ p option empty" without "single Hom-module" | Full rank: rank 4 in a rank-8 sum. §7 item 4 covers only orthogonal sums of FULL modules and excludes non-full-rank multi-target constructions (lines 308-312). H keeps "inside a single Hom(E, E')" | **stops: full rank / single module**. Overstated only in IDEA-20260926-e1b48e (J4 item 2) |

Every object stops at the step the failure signature predicts, and every
computed value matches the known one. **The argument does not prove too
much.** The two wording hazards are reported separately (J4).

---

## What each verdict permits and forbids

This is not a decision. It states what each joint verdict permits and forbids.

**Permitted by these verdicts:**

- recording EXP-SSIQ-6916e8 as **INCONCLUSIVE-CONSTRUCTION** (run of record
  RUN-SSIQ-004595; RUN-SSIQ-81bd08 is INCONCLUSIVE-CONSTRUCTION under v1 per
  d3);
- treating both runs as **admissible receipts of exactly what they measured**,
  subject to the implementation-hash check in "Not done";
- an evidence record with `proof_status: derivation` and
  `proof_refs: derivation-note.md` (sha256 `9bd98c12…`), which lists every
  recalled input (J1(c)), carries the H scope repair ("geometric Hom" or
  "equal-Frobenius F_{p^2}-models"; J1(b)) and the relevance caveat (J3(c)),
  and replaces "exponent floor" and "can never certify" with non-floor wording
  (J4);
- upgrading the general-pair interface to `internal` via JMV lines 1312-1325,
  in a new record with `verified_by`;
- carrying the note to the rule-12 `review-breakthrough` round.

**Forbidden by these verdicts:**

- any SUCCESS or S1 reading;
- admitting R3/A2 as A1;
- treating the PARI raise as evidence;
- reading the 945 cells as evidence for the Deuring interface or for the
  universal statement;
- quoting the contract headline as if the run could have falsified the lemma
  (J2);
- moving H-SSIQ-a9df38 to supported, adopting the closure into GOAL-SSIQ-001,
  or promoting a KN-FIND before the rule-12 round (card `review_tier_note`);
- any adoption wording that drops rank 4 (full rank), single Hom-module, deg,
  g = 1, or geometric Hom.

No verdict here supports `weaken` or `reject_scoped`: no mathematical error was
found.

---

## Validation report (validator.md schema)

```yaml
validation_report:
  id: null   # not minted: this reviewer's only write is this file; the archive task mints if needed
  task_id: TASK-20260926-eecb7f
  run_ids: [RUN-SSIQ-004595, RUN-SSIQ-81bd08]
  artifact_checks:
    - "All run files present at b4ae42bfd; every output_sha256 in both manifests matches the committed bytes."
    - "Specification sha256 81db1913…350db and amendment sha256 678040641377…34e6 match the committed blobs."
    - "Amendment da16c1908 committed before RUN-SSIQ-004595 started (02:31:37 < 02:47:34)."
    - "Implementation sha256 binding NOT verified by this reviewer (blind_from, RV-2)."
    - "derivation-note.md sha256 9bd98c12… is not bound by either manifest; AMD C-7 misstates this."
  metric_recomputations:
    - "Every Nrd Gram (1517 records) was rebuilt from committed bases and verified structure constants, and every determinant recomputed: 0 mismatches."
    - "R=1: A1 21/21, A2 22/22, A3 22/22, A4 440/440, A5 440/440. R_sub=1: 484/484 (m=1024: 44/44)."
    - "M-INDEX: 462/462. Seeds: 924/924."
    - "Item states: 2397 COMPUTED_VALID + 1 NOT_COMPUTED = 2398 (the manifest and report state the sum as 1946, an arithmetic slip)."
  control_checks:
    - "C-TRD 22/22 (ratio 16, R(T)=16); C-NONMAX 22/22 (index 8, R=64, trace det != p^2); C-NOSCALE 440/440 (ratio n^4, R != 1); C-NEAR 22/22 (p^2/4, p/4)."
    - "C-ALG and C-CROSS recomputed: algnorm Gram == regular-representation Gram on 1495/1495 records."
    - "Contract-design defect: F-NORM on A1, A3 and A5 can be triggered by instrument faults that C-ALG does not catch (J2(b), demonstrated)."
  heuristic_validation_checks: ["not applicable: no heuristic under test (spec heuristic_under_test: null)"]
  cost_model_checks: ["not applicable: no cost claimed"]
  proof_architecture_checks:
    - "Baseline fixture: L1's (P, Nrd/p) exponent 1/2 and P^0 = p/4 are reproduced; the Theorem 1.5 constant is reproduced via gamma_3."
    - "Ceiling/nearby control: PT-1..PT-6 all stop at named steps."
    - "Quantifier fidelity: H's 'E, E' / F_{p^2}' is wrong for the rational Hom (J1(b)); the note's geometric Hom is right."
  verdict: passed
  verdict_meaning: >-
    Both runs are admissible receipts of the exact quaternion-lattice values
    they record, subject to a non-blind session confirming the implementation
    sha256 values against the committed blobs. The experiment outcome is
    INCONCLUSIVE-CONSTRUCTION. A passed validation supports no ECDLP claim,
    demonstrates no speedup, does not support the lemma beyond its
    normalisation, and authorises no promotion.
  limitations:
    - "Implementation sha256 not verified (blind_from)."
    - "The rule-12 review-breakthrough round is still owed."
    - "Same model identity as the producers (claude-opus-5-5): concurrence is session-independent, not model-independent (L-4)."
    - "The phase gate is attested, not mechanical (L-1)."
  artifact_paths: [experiments/EXP-SSIQ-6916e8/reviews/validator-TASK-20260926-eecb7f.md]
```

---

## Appendix: Phase B scratch code and outputs (own code, verbatim)

All run from `/tmp/claude-0/-home-user/5af2d3d8-0ba3-5d96-b05f-205cb058efcf/scratchpad/validator-eecb7f/`, one process at a time. `phaseB_scratch.gp` and `j2_faults.gp` `read("qlib.gp")` (`j5_pari.gp` is standalone). That is the Phase A library quoted verbatim in Section A (sha256 `f76b1510…668a`, unchanged).

Committed artifacts were exported read-only to `committed/` with, for each path:

```
git show b4ae42bfd:experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/<f>   > committed/v1/<f>   # f in manifest.yaml raw-result.json command.txt environment.json stdout.log stderr.log check.stdout.log check.stderr.log
git show b4ae42bfd:experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/<f>  > committed/v2/<f>   # same list + comparison-to-RUN-SSIQ-81bd08.json
git show b4ae42bfd:experiments/EXP-SSIQ-6916e8/derivation-note.md > committed/derivation-note.md
git show 3ea7223b9:experiments/EXP-SSIQ-6916e8/derivation-note.md > committed/derivation-note-3ea7223b9.md   # cmp: identical
git show b4ae42bfd:experiments/EXP-SSIQ-6916e8/specification.yaml > committed/specification.yaml
git show b4ae42bfd:experiments/EXP-SSIQ-6916e8/amendments/AMD-20260926-f9acf7.yaml > committed/AMD.yaml
git show b4ae42bfd:inputs/P13-WESOLOWSKI-2026/paper_fulltext.md > committed/weso.md
git show b4ae42bfd:ledger/goals/GOAL-SSIQ-001/goal.yaml > committed/goal.yaml
git show b4ae42bfd:ledger/decisions/DEC-20260805-2be965.yaml > committed/DEC-2be965.yaml
```

sha256 of the exported run files (`sha256sum`):

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  committed/v1/check.stderr.log
14a10bd35b757ea92f75c4809536c67f9f244211e53abe6e0e27126a1dca64a3  committed/v1/check.stdout.log
b0d70e85c23ea6b43d05865d18b58ab4011441d9adb7b35843a4e92cc5aedc1f  committed/v1/command.txt
67ba8049d60e2ef145eedfe5d2b742383af9d6a55f5c250f86fb933d496eeb09  committed/v1/environment.json
1b44663c3477400811886d636bc4cfa2a7e655308a9dc0cdf5d4be32aff6c7b4  committed/v1/manifest.yaml
2bbc828b196fb880cd0e2699a279bb9c2e24eea9eaaaa2cf74d557f69d6304d5  committed/v1/raw-result.json
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  committed/v1/stderr.log
34692a60cdf5ddc4760a28f9870a5fe9ffa3962c8f8d621c983bd4083ebdcd31  committed/v1/stdout.log
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  committed/v2/check.stderr.log
c77b40ed940c301c02b121dc3e87941b83aceca5fcb5e703355dcd6f0e93d918  committed/v2/check.stdout.log
61159c7d4de8a719d21a92f7518f5e9431d0d9f37a870f804be213856a473778  committed/v2/command.txt
45e085df62842a1918e8dafd437f95da7052b5b60869e2667c4519c883859779  committed/v2/comparison-to-RUN-SSIQ-81bd08.json
381e490067d3be1b5073e024f6dc76836eb582cb46fb623fd57c4d83c66f7a79  committed/v2/environment.json
6efb23034374bbb5670da6fbaf68e3368bb4c2aedc63d1ec50d936b4a698e6a2  committed/v2/manifest.yaml
a477d37c041f7b0736f3d9173ea4b4dbff6e3f2e9f00edcdebd52f40379cfd25  committed/v2/raw-result.json
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  committed/v2/stderr.log
a6b2e179f05229a279576e94f0c77b012c142250bb49d3956471a8861e62a138  committed/v2/stdout.log
9bd98c12841b8d51e67c3794573770d0a1aa4de381f16e1d900ddd93780bda7e  committed/derivation-note.md
9bd98c12841b8d51e67c3794573770d0a1aa4de381f16e1d900ddd93780bda7e  committed/derivation-note-3ea7223b9.md
81db19133f23adccb316a1914801ca154d58e49ac76ae38a793b65db89c350db  committed/specification.yaml
678040641377b2bae0998dc04c29e281097319f781306c810498f3c9a37434e6  committed/AMD.yaml
```

**Failed invocations (disclosed).** They are listed here and were not used for any value:

1. The first `j5_pari.gp` used gp closures `()->(setrand(1); alginit(...))`. gp rejected them (`syntax error, unexpected ')', expecting )-> or ','`), so no R1, R2, D1, D2 or D3 `alginit` call executed in that attempt; only the R3 line ran. That attempt counts as no diagnostic, and the script was rewritten with plain `iferr`.
2. The first `phaseB_scratch.gp` had one enumeration bug. `ffgen` gives a field generator, not a multiplicative generator, so the counter was switched to `ffprimroot`. It also had unbraced multi-line prints (`syntax error, unexpected end of file`) and one floating-point `qfminim` flag. These were fixed, and the file was re-run in full.
3. The first `j2_faults.gp` used the name `I`, which gp reserves for sqrt(-1) (`variable name expected`). The variable was renamed `Iq` and the file re-run.

### `recompute_v2.py`

Command:

```
(ulimit -v 4000000; timeout 900 python3 recompute_v2.py committed/v2/raw-result.json) 2>&1 | tee recompute_v2.out
```

Script (sha256 `3034145294f3663a023149315ff7352b566dd11bf884affba73db4556a4809ad`):

```python
#!/usr/bin/env python3
"""validator-eecb7f Phase B: own recomputation from COMMITTED raw-result.json
(RUN-SSIQ-004595, read at b4ae42bfd via git show). No producer code is used or read.

For every lattice record:
  * PARI-side records (coord_system O0_basis_form): the structure constants
    (prime_status.multable_stage1) and the recorded images of i, j, k are
    first VERIFIED (associativity, unit, i^2=a, j^2=b, ij=k=-ji). The basis is
    then mapped to (1,i,j,k) coordinates and the Nrd Gram is rebuilt with my
    own formula Nrd = x0^2 - a x1^2 - b x2^2 + ab x3^2 (frozen Gram convention),
    divided by form_scale.
  * A2 records (coord_system ijk) are evaluated directly.
Then: my own exact Fraction determinant; R = det*16/p^2; compare with the
recorded gram, det_python, det_pari, R. Index [O:I] and n(I) are measured
independently; seeds recomputed; item states and outcome tally recounted.
"""
import json, sys, hashlib, collections
from fractions import Fraction as F
from math import gcd

RAW = sys.argv[1]
d = json.load(open(RAW))

def fr(s): return F(s)

def det(M):
    M = [[F(x) for x in row] for row in M]
    n = len(M); s = F(1)
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] != 0), None)
        if piv is None: return F(0)
        if piv != c: M[c], M[piv] = M[piv], M[c]; s = -s
        s *= M[c][c]
        for r in range(c+1, n):
            f = M[r][c] / M[c][c]
            if f: M[r] = [M[r][k] - f*M[c][k] for k in range(n)]
    return s

def inv(M):
    n = len(M); A = [[F(x) for x in row] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]; A[c] = [x/pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]; A[r] = [A[r][k] - f*A[c][k] for k in range(2*n)]
    return [row[n:] for row in A]

def matvec(M, v): return [sum(M[i][j]*v[j] for j in range(len(v))) for i in range(len(M))]

def nrd_ijk(a, b, x): return x[0]**2 - a*x[1]**2 - b*x[2]**2 + a*b*x[3]**2

def gram(q, vecs, s):
    n = len(vecs); A = [[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j: A[i][i] = q(vecs[i]) / s
            else:
                A[i][j] = (q([x+y for x, y in zip(vecs[i], vecs[j])]) - q(vecs[i]) - q(vecs[j])) / 2 / s
    return A

def mul_factory(mt):
    # mt[i] is stored as rows; column c of mt[i] = e_i * e_c (determined below)
    T = [[[fr(x) for x in row] for row in m] for m in mt]
    def mul(x, y):
        r = [F(0)]*4
        for i in range(4):
            if x[i] == 0: continue
            for c in range(4):
                if y[c] == 0: continue
                for k in range(4):
                    r[k] += x[i]*y[c]*T[i][k][c]
        return r
    return mul

prim = {str(e['p']): e for e in d['primes']}
PS = d['prime_status']
report = collections.defaultdict(int)
problems = []
conv = {}   # p -> (a, b, O0->ijk matrix, O0-basis check info)

for p, st in PS.items():
    pres = prim[p]['presentation']; a, b = F(pres['a']), F(pres['b'])
    # at the R3 prime the algebra presentation is presentation_used (same (a,b))
    if st.get('presentation_used'):
        pu = st['presentation_used']
        assert F(pu[0]) == a and F(pu[1]) == b, (p, pu, pres)
    mt = st.get('multable_stage1')
    if mt is None:
        problems.append(f"{p}: no multable"); continue
    mul = mul_factory(mt)
    E = [[F(int(i == j)) for j in range(4)] for i in range(4)]
    one = [fr(x) for x in st['one_stage1']]
    ok_unit = all(mul(one, E[i]) == E[i] and mul(E[i], one) == E[i] for i in range(4))
    ok_assoc = all(mul(mul(E[i], E[j]), E[k]) == mul(E[i], mul(E[j], E[k]))
                   for i in range(4) for j in range(4) for k in range(4))
    I, J, K = [[fr(x) for x in v] for v in st['ijk_images']]
    sc = lambda c: [c*x for x in one]
    neg = lambda v: [-x for x in v]
    ok_rel = (mul(I, I) == sc(a) and mul(J, J) == sc(b) and mul(I, J) == K and mul(J, I) == neg(K))
    ok_mt2 = (st.get('multable_stage2') == mt)
    # columns: images of 1,i,j,k in O0 coords -> matrix Img (4x4, columns); O0 coords -> ijk: Img^-1
    Img = [[one[r], I[r], J[r], K[r]] for r in range(4)]
    C = inv(Img)
    conv[p] = (a, b, C, mul)
    report['primes_structure_checked'] += 1
    if not (ok_unit and ok_assoc and ok_rel and ok_mt2):
        problems.append(f"{p}: structure check unit={ok_unit} assoc={ok_assoc} rel={ok_rel} mt2={ok_mt2}")

def to_ijk(p, v):
    a, b, C, _ = conv[p]
    return matvec(C, [fr(x) for x in v])

recs = {x['id']: x for x in d['lattices']}
mism = collections.Counter()
rows = []
base_det_unscaled = {}
for x in d['lattices']:
    if x.get('state') != 'COMPUTED_VALID':
        report['not_computed_records'] += 1
        rows.append((x['id'], x['arm'], x.get('state'), None)); continue
    p = x['p']; P = F(int(p))
    a, b = (F(x['presentation']['a']), F(x['presentation']['b'])) if x['coord_system'] == 'ijk' else conv[p][:2]
    q = lambda v: nrd_ijk(a, b, v)
    vecs = [[fr(t) for t in row] for row in x['basis']] if x['coord_system'] == 'ijk' else [to_ijk(p, row) for row in x['basis']]
    s = fr(x['form_scale'])
    A = gram(q, vecs, s)
    Arec = [[fr(t) for t in row] for row in x['gram']]
    if A != Arec: mism['gram'] += 1; problems.append(f"gram mismatch {x['id']}")
    D = det(A)
    if D != fr(x['det_python']): mism['det_python'] += 1; problems.append(f"det_python mismatch {x['id']}")
    if D != fr(x['det_pari']): mism['det_pari'] += 1; problems.append(f"det_pari mismatch {x['id']}")
    arm = x['arm']
    R = D*16/P**2
    if arm in ('A1', 'A2', 'A3', 'A4', 'A5'):
        if x['R'] is None or fr(x['R']) != R: mism['R'] += 1; problems.append(f"R mismatch {x['id']}")
        report[f'R==1:{arm}'] += (R == 1); report[f'R!=1:{arm}'] += (R != 1)
    if arm == 'A6':
        Hm = [[fr(t) for t in row] for row in x['H']]
        m = abs(det(Hm))
        # independent index: basis coordinates of L relative to its parent's basis
        par = recs[f"{p}:{x['parent']}"] if f"{p}:{x['parent']}" in recs else None
        Rsub = D*16/(m**2*P**2)
        report['A6_Rsub==1'] += (Rsub == 1)
        if fr(x['R_sub']) != Rsub: mism['R_sub'] += 1; problems.append(f"R_sub mismatch {x['id']}")
        if m != x['m_planned']: mism['m'] += 1; problems.append(f"m mismatch {x['id']}")
        if par is not None:
            Lc = [[fr(t) for t in row] for row in x['basis']]; Pc = [[fr(t) for t in row] for row in par['basis']]
            idx = abs(det(Lc)) / abs(det(Pc))
            report['A6_index_from_bases==m'] += (idx == m)
        if m == 1024: report['A6_m1024_Rsub==1'] += (Rsub == 1)
    if arm in ('A3', 'A4'):
        # index [O:I] from coordinates relative to the base order; n(I) from unscaled Nrd gram
        base = recs[f"{p}:base"]
        Bc = [[fr(t) for t in row] for row in base['basis']]
        Lc = [[fr(t) for t in row] for row in x['basis']]
        idx = abs(det(Lc)) / abs(det(Bc))
        A1 = gram(q, vecs, F(1))
        g = 0
        for i in range(4):
            g = gcd(g, int(A1[i][i]))
            for j in range(i+1, 4): g = gcd(g, int(2*A1[i][j]))
        report[f'{arm}_index==n^2'] += (idx == g*g)
        if arm == 'A4':
            report['A4_n==target'] += (g == int(x['target_norm']))
            report['A4_scale==n'] += (s == g)
            # C-NOSCALE: det(I,Nrd)/det(I,Nrd/n) = n^4, R_unscaled != 1
            Du = det(A1)
            report['CNOSCALE_ratio==n^4'] += (Du / D == g**4)
            report['CNOSCALE_R!=1'] += (Du*16/P**2 != 1)
        if arm == 'A3':
            report['A3_index==p^2'] += (idx == P**2); report['A3_n==p'] += (g == P)
    if arm == 'base':
        base_det_unscaled[p] = D
        T = [[2*t for t in row] for row in A]
        report['CTRD_ratio==16'] += (det(T) / D == 16); report['CTRD_R(T)==16'] += (det(T)*16/P**2 == 16)
    if arm == 'C-NONMAX':
        base = recs[f"{p}:base"]
        Bc = [[fr(t) for t in row] for row in base['basis']]; Lc = [[fr(t) for t in row] for row in x['basis']]
        idx = abs(det(Lc)) / abs(det(Bc))
        report['CNONMAX_index==8'] += (idx == 8); report['CNONMAX_R==64'] += (R == 64)
        report['CNONMAX_trdet!=p^2'] += (16*D != P**2)
    if arm == 'C-NEAR-O0':
        report['CNEAR_O0==p^2/4'] += (D == P**2/4)
        report['CNEAR_O0_tracezero'] += all(v[0] == 0 for v in vecs)
    if arm == 'C-NEAR-P0':
        report['CNEAR_P0==p/4'] += (D == P/4)
        report['CNEAR_P0_tracezero'] += all(v[0] == 0 for v in vecs)
        report['CNEAR_P0_p|Nrd_all'] += all(q(v) % P == 0 for v in vecs)
    report[f'computed:{arm}'] += 1

# ---- seeds
def seed(arm, p, k): return int(hashlib.sha256(f"20260926:{arm}:{p}:{k}".encode()).hexdigest()[:16], 16)
sd_ok = sd_n = 0
for p, st in PS.items():
    for k, s in enumerate(st['a4_seeds'], start=1):
        sd_n += 1; sd_ok += (int(s) == seed('A4', p, k))
    for k, s in enumerate(st['a6_seeds'], start=0):
        sd_n += 1; sd_ok += (int(s) == seed('A6', p, k))
rec_seed_ok = sum(1 for x in d['lattices'] if x['arm'] in ('A4', 'A6') and x.get('seed') is not None
                  and int(x['seed']) == seed(x['arm'], x['p'], x['idx']))
rec_seed_n = sum(1 for x in d['lattices'] if x['arm'] in ('A4', 'A6') and x.get('seed') is not None)

# ---- item states / tally recount
ist = d['counts']['item_states']
st_ctr = collections.Counter((i['kind'], i['state']) for i in ist)
codes = collections.Counter(c for i in ist for c in i.get('codes', []))
verdicts = collections.Counter(i.get('verdict') for i in ist)

print("== structure/presentation checks:", dict(report)['primes_structure_checked'], "primes")
print("== mismatches vs record:", dict(mism) if mism else "none")
for k in sorted(report): print(f"   {k}: {report[k]}")
print("== seeds prime_status: %d/%d match; lattice-record seeds: %d/%d match" % (sd_ok, sd_n, rec_seed_ok, rec_seed_n))
print("== item_states: total", len(ist), dict(st_ctr))
print("   verdicts:", dict(verdicts), " codes:", dict(codes))
nc = [i for i in ist if i['state'] != 'COMPUTED_VALID']
print("   non-COMPUTED_VALID items:", nc)
print("== problems (%d):" % len(problems), problems[:20])
```

Output (sha256 `6c8101552e9135c15fe52f583e7d4f6efdcf89936626e4178a6f2b784ee510e2`, ANSI codes stripped):

```
== structure/presentation checks: 22 primes
== mismatches vs record: none
   A3_index==n^2: 22
   A3_index==p^2: 22
   A3_n==p: 22
   A4_index==n^2: 440
   A4_n==target: 440
   A4_scale==n: 440
   A6_Rsub==1: 484
   A6_index_from_bases==m: 484
   A6_m1024_Rsub==1: 44
   CNEAR_O0==p^2/4: 22
   CNEAR_O0_tracezero: 22
   CNEAR_P0==p/4: 22
   CNEAR_P0_p|Nrd_all: 22
   CNEAR_P0_tracezero: 22
   CNONMAX_R==64: 22
   CNONMAX_index==8: 22
   CNONMAX_trdet!=p^2: 22
   CNOSCALE_R!=1: 440
   CNOSCALE_ratio==n^4: 440
   CTRD_R(T)==16: 22
   CTRD_ratio==16: 22
   R!=1:A1: 0
   R!=1:A2: 0
   R!=1:A3: 0
   R!=1:A4: 0
   R!=1:A5: 0
   R==1:A1: 21
   R==1:A2: 22
   R==1:A3: 22
   R==1:A4: 440
   R==1:A5: 440
   computed:A1: 21
   computed:A2: 22
   computed:A3: 22
   computed:A4: 440
   computed:A5: 440
   computed:A6: 484
   computed:C-NEAR-O0: 22
   computed:C-NEAR-P0: 22
   computed:C-NONMAX: 22
   computed:base: 22
   not_computed_records: 1
   primes_structure_checked: 22
== seeds prime_status: 924/924 match; lattice-record seeds: 924/924 match
== item_states: total 2398 {('primary', 'COMPUTED_VALID'): 945, ('sub', 'COMPUTED_VALID'): 484, ('index', 'COMPUTED_VALID'): 462, ('control', 'COMPUTED_VALID'): 506, ('primary', 'NOT_COMPUTED'): 1}
   verdicts: {'pass': 2397, None: 1}  codes: {'INCONCLUSIVE-CONSTRUCTION': 1}
   non-COMPUTED_VALID items: [{'id': '9223372036854775837:A1', 'kind': 'primary', 'state': 'NOT_COMPUTED', 'cause': 'CONSTRUCTION', 'codes': ['INCONCLUSIVE-CONSTRUCTION']}]
== problems (0): []
```

### `compare_v1_v2.py`

Command:

```
(ulimit -v 4000000; timeout 900 python3 compare_v1_v2.py) 2>&1 | tee compare_v1_v2.out
```

Script (sha256 `f208b0b8c90f72d67ac6b49f275c3da2310aa94b46f5309cee69743fabf7c252`):

```python
#!/usr/bin/env python3
"""validator-eecb7f Phase B: own comparison of RUN-SSIQ-81bd08 vs RUN-SSIQ-004595
committed raw-result.json files (both read at b4ae42bfd). Own code; the producer's
compare_runs.py is not read or used. Also recomputes every v1 determinant."""
import json, sys, collections
from fractions import Fraction as F
sys.argv = sys.argv[:1] + ['committed/v1/raw-result.json']
v1 = json.load(open('committed/v1/raw-result.json'))
v2 = json.load(open('committed/v2/raw-result.json'))
BAD = '9223372036854775837'

def det(M):
    M = [[F(x) for x in row] for row in M]; n = len(M); s = F(1)
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] != 0), None)
        if piv is None: return F(0)
        if piv != c: M[c], M[piv] = M[piv], M[c]; s = -s
        s *= M[c][c]
        for r in range(c+1, n):
            f = M[r][c]/M[c][c]
            if f: M[r] = [M[r][k]-f*M[c][k] for k in range(n)]
    return s

r1 = {x['id']: x for x in v1['lattices']}; r2 = {x['id']: x for x in v2['lattices']}
print("v1 lattice records:", len(r1), " v2:", len(r2))
v1_missing = [i for i, x in r1.items() if not x.get('valid')]
print("v1 records not valid:", len(v1_missing), " all at the R3 prime:", all(i.startswith(BAD+':') for i in v1_missing),
      " arms:", dict(collections.Counter(r1[i]['arm'] for i in v1_missing)))
print("v1 records at BAD prime:", sum(1 for i in r1 if i.startswith(BAD+':')), " with non-null gram:",
      sum(1 for i in r1 if i.startswith(BAD+':') and r1[i].get('gram')))
# v1 determinant recomputation from recorded Gram
bad_det = 0; n_det = 0
for i, x in r1.items():
    if x.get('valid') and x.get('gram'):
        n_det += 1
        D = det(x['gram'])
        if D != F(x['det_python']) or D != F(x['det_pari']): bad_det += 1
print("v1 valid records with gram: %d; own det == det_python == det_pari: %d" % (n_det, n_det - bad_det))
# field-by-field comparison at shared primes
fields = ['basis', 'gram', 'form_scale', 'det_python', 'det_pari', 'R', 'R_sub', 'H', 'seed', 'alpha_base_coords',
          'n_python', 'n_pari', 'index_python', 'index_pari', 'gram_nrd_unscaled', 'gram_regrep_unscaled', 'valid']
cmp_n = 0; diff = collections.Counter(); diff_ids = []
for i, x in r1.items():
    if i.startswith(BAD+':'): continue
    y = r2.get(i)
    if y is None: diff['missing_in_v2'] += 1; diff_ids.append(i); continue
    cmp_n += 1
    for f in fields:
        if (f in x) or (f in y):
            if x.get(f) != y.get(f): diff[f] += 1; diff_ids.append((i, f))
extra_v2 = [i for i in r2 if not i.startswith(BAD+':') and i not in r1]
print("records compared (21 shared primes):", cmp_n, " differing fields:", dict(diff) or "none", " v2-only ids at shared primes:", extra_v2)
# controls
c1 = {c['p']: c for c in v1['controls']}; c2 = {c['p']: c for c in v2['controls']}
cd = 0; cn = 0
for p in c1:
    if p == BAD: continue
    for k in ['C-TRD', 'C-NONMAX', 'C-NEAR']:
        cn += 1
        a = {kk: vv for kk, vv in (c1[p][k] or {}).items() if kk in ('trace_form', 'det_pari', 'det_python', 'ratio_detT_over_detA', 'R_T', 'index_pari', 'ratio', 'R', 'trace_form_det_pari', 'det_O0', 'det_P0')}
        b = {kk: c2[p][k].get(kk) for kk in a}
        cd += (a != b)
    for u, w in zip(c1[p]['C-NOSCALE'], c2[p]['C-NOSCALE']):
        cn += 1; cd += any(u.get(k) != w.get(k) for k in ('idx', 'n', 'det_unscaled', 'det_scaled', 'ratio', 'R_unscaled'))
print("control records compared:", cn, " differing:", cd)
print("v1 seeds == v2 seeds at every prime:", all(v1['prime_status'][p]['a4_seeds'] == v2['prime_status'][p]['a4_seeds'] and
      v1['prime_status'][p]['a6_seeds'] == v2['prime_status'][p]['a6_seeds'] for p in v1['prime_status']))
print("v1 primes list == v2 primes list:", [e['p'] for e in v1['primes']] == [e['p'] for e in v2['primes']],
      " presentations equal:", [e['presentation'] for e in v1['primes']] == [e['presentation'] for e in v2['primes']],
      " target norms equal:", [e['target_norms'] for e in v1['primes']] == [e['target_norms'] for e in v2['primes']])
print("v1 outcome:", v1['outcome']['primary_code'], v1['outcome']['triggered_codes'])
print("v1 success_conditions:", v1['outcome']['success_conditions'])
print("v1 S4_other_failures:", json.dumps(v1['outcome'].get('S4_other_failures'))[:600])
print("v1 counts.summary keys:", list(v1['counts']['summary'].keys()))
print("v1 M_R:", v1['counts']['summary'].get('M_R'), " M_SUB:", v1['counts']['summary'].get('M_SUB'), " M_INDEX:", v1['counts']['summary'].get('M_INDEX'))
comp = json.load(open('committed/v2/comparison-to-RUN-SSIQ-81bd08.json'))
print("comparison file top keys:", list(comp.keys()))
print("comparison summary:", json.dumps({k: v for k, v in comp.items() if not isinstance(v, (list, dict)) or k in ('summary', 'totals')})[:1500])
```

Output (sha256 `0a82050327be8fe7ae5a539e375aa3c5c9cf02746c256cffc0aaefbf7767fc85`, ANSI codes stripped):

```
v1 lattice records: 1514  v2: 1518
v1 records not valid: 64  all at the R3 prime: True  arms: {'A1': 1, 'A3': 1, 'A4': 20, 'A5': 20, 'A6': 22}
v1 records at BAD prime: 65  with non-null gram: 1
v1 valid records with gram: 1450; own det == det_python == det_pari: 1450
records compared (21 shared primes): 1449  differing fields: none  v2-only ids at shared primes: []
control records compared: 483  differing: 0
v1 seeds == v2 seeds at every prime: True
v1 primes list == v2 primes list: True  presentations equal: True  target norms equal: True
v1 outcome: INCONCLUSIVE-NEAR ['INCONCLUSIVE-NEAR', 'INCONCLUSIVE-CONSTRUCTION', 'INCONCLUSIVE']
v1 success_conditions: {'S1': False, 'S2': False, 'S3': False, 'S4': False, 'S5': True, 'S6_file_present': True, 'S7': 'pending: evaluated by check.py after the driver'}
v1 S4_other_failures: []
v1 counts.summary keys: ['primes_planned', 'primes_listed', 'M_R_planned', 'M_R_listed', 'M_R_valid', 'M_R_R_eq_1', 'M_R_R_ne_1', 'M_R_excluded', 'M_R_missing', 'M_R_by_arm', 'M_SUB_planned', 'M_SUB_listed', 'M_SUB_valid', 'M_SUB_R_eq_1', 'M_SUB_R_ne_1', 'M_SUB_excluded_or_missing', 'M_INDEX_planned', 'M_INDEX_listed', 'M_INDEX_evaluated', 'M_INDEX_mismatches', 'M_NORMHIT_hits', 'M_NORMHIT_misses', 'M_CROSS_disagreements', 'M_CROSS_list', 'controls_failed', 'controls_pass_counts', 'controls_planned', 'fallback_primes', 'calg_a_fail_primes', 'calg_b_fail_primes']
v1 M_R: None  M_SUB: None  M_INDEX: None
comparison file top keys: ['basis', 'comparison', 'note', 'per_prime', 'primes_not_compared', 'schema_fields_only_in_RUN-SSIQ-004595', 'schema_fields_only_in_RUN-SSIQ-81bd08', 'schema_note', 'shared_R1_prime_count', 'shared_R1_primes', 'totals', 'v1_raw_result', 'v2_raw_result', 'value_differences', 'value_differences_count']
comparison summary: {"basis": "AMD-20260926-f9acf7 change C-6; TASK-20260926-fba7e0 C-9; REPORT ONLY, feeds no criterion", "comparison": "RUN-SSIQ-004595 (protocol v2) vs RUN-SSIQ-81bd08 (protocol v1)", "note": "Deterministic re-computation with the same seeds, not independent replication; the reproduced primes must not be counted as a second sample (C-6). A value difference is an anomaly for review.", "schema_note": "Fields present in only one run are not compared; RUN-SSIQ-004595 adds the tally_rule state fields, the route record and control state inputs (v2 changes C-1..C-4).", "shared_R1_prime_count": 21, "totals": {"fields_compared": 52479, "fields_different": 0, "fields_identical": 52479, "records_compared": 1995, "records_different": 0, "records_identical": 1995, "records_missing_in_one_run": 0}, "v1_raw_result": "experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/raw-result.json", "v2_raw_result": "experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/raw-result.json", "value_differences_count": 0}
```

### `j6_obligations.py`

Command:

```
(ulimit -v 4000000; timeout 900 python3 j6_obligations.py) 2>&1 | tee j6_obligations.out
```

Script (sha256 `5c1e31dba36dabb52767456f23f17feeef778d693a425ef99d188b4233224381`):

```python
#!/usr/bin/env python3
"""validator-eecb7f J6(e) obligations (1)-(4) from the committed v2 raw-result.json (own code)."""
import json
from fractions import Fraction as F
d = json.load(open('committed/v2/raw-result.json'))
BAD = '9223372036854775837'
ok1 = True
for p, st in d['prime_status'].items():
    ra = st['route_attempts']; routes = [r['route'] for r in ra]
    r1_raised = ra[0]['route'] == 'R1' and ra[0]['error'] is not None
    ladder_entered = len(ra) > 1
    if ladder_entered != r1_raised: ok1 = False; print("ladder/R1 mismatch at", p)
    if any(r['setrand_before_alginit'] != 1 for r in ra): ok1 = False; print("setrand missing at", p)
    if p == BAD: print("BAD prime attempts:", [(r['route'], r['call'], r['maxord_flag'], r['error']) for r in ra])
print("(1) ladder entered iff R1 raised, setrand(1) before every call, no unlisted route:", ok1,
      "; routes used:", sorted({st['construction_route'] for st in d['prime_status'].values()}))
print("(2) primes resolved by R2:", [p for p, st in d['prime_status'].items() if st['construction_route'] == 'R2'])
L = {x['id']: x for x in d['lattices']}
b, a2 = L[BAD + ':base'], L[BAD + ':A2']
print("(3) g_a2 at R3 prime:", d['prime_status'][BAD]['g_a2']['pass'], "; base gram == A2 gram (same basis order):",
      [[F(t) for t in r] for r in b['gram']] == [[F(t) for t in r] for r in a2['gram']],
      "; base det:", b['det_python'], "; A2 det:", a2['det_python'], "; A2 basis:", a2['basis'])
o = d['outcome']
print("(4) NOT_COMPUTED items:", o['cells_not_computed'], o['controls_not_computed'], "; controls_failed:", o['controls_failed'],
      "; F_NORM:", o['F_NORM_cells'], "; M_INDEX mismatches:", o['M_INDEX_mismatch_cells'], "; INVALID:", o['INVALID_cells'])
nr = sum(1 for x in d['lattices'] if x.get('state') == 'COMPUTED_VALID' and 'gram_regrep_unscaled' in x)
eq = sum(1 for x in d['lattices'] if x.get('state') == 'COMPUTED_VALID' and 'gram_regrep_unscaled' in x
         and x['gram_regrep_unscaled'] == x['gram_nrd_unscaled'])
print("M-CROSS (ii): PARI-side records with both Nrd Grams:", nr, "; algnorm Gram == regular-rep Gram:", eq)
```

Output (sha256 `5c831cf735d1d21df77c4411ed1e8a7cf28e80409414e7598a2068a7795ef1fe`, ANSI codes stripped):

```
BAD prime attempts: [('R1', 'alginit(nfinit(y), [-2, -9223372036854775837])', 1, 'error(impossible inverse in dvmdii: 0.)'), ('R2', 'alginit(nfinit(y), [-9223372036854775837, -2])', 1, 'error(impossible inverse in dvmdii: 0.)'), ('R3', 'alginit(nfinit(y), [-2, -9223372036854775837], , 0)', 0, None)]
(1) ladder entered iff R1 raised, setrand(1) before every call, no unlisted route: True ; routes used: ['R1', 'R3']
(2) primes resolved by R2: []
(3) g_a2 at R3 prime: True ; base gram == A2 gram (same basis order): True ; base det: 85070591730234616400799229995519050569/16 ; A2 det: 85070591730234616400799229995519050569/16 ; A2 basis: [['1', '0', '0', '0'], ['1/2', '0', '1/2', '1/2'], ['0', '1/4', '1/2', '1/4'], ['0', '0', '0', '1']]
(4) NOT_COMPUTED items: ['9223372036854775837:A1'] [] ; controls_failed: [] ; F_NORM: [] ; M_INDEX mismatches: [] ; INVALID: []
M-CROSS (ii): PARI-side records with both Nrd Grams: 1495 ; algnorm Gram == regular-rep Gram: 1495
```

### `j5_pari.gp`

Command:

```
(ulimit -v 4000000; timeout 900 gp -q --default parisize=200000000 j5_pari.gp) > j5_pari.out 2>&1
```

Script (sha256 `ec1825bbbf1c7a7f5485f957ddb085b7aeb66965740aab79da71c6682dbd653f`):

```gp
\\ validator-eecb7f Phase B, J5: reproduce the PARI 2.15.4 alginit raise at the
\\ blocking prime (own script; diagnostics only, RV-6: nothing here is an A1 cell).
p = 9223372036854775837;
print("version: ", version());
print("isprime(p,2) = ", isprime(p,2), "   p mod 8 = ", p % 8);
print("Hilbert (-2,-p): at 2 -> ", hilbert(-2,-p,2), ", at p -> ", hilbert(-2,-p,p), ";  kronecker(-2,p) = ", kronecker(-2,p), ", kronecker(-1,p) = ", kronecker(-1,p), ", kronecker(2,p) = ", kronecker(2,p));
show(label, r) = print(label, " -> ", if(type(r) == "t_STR", r, "initialised (no error)"));
\\ the three recorded routes, each preceded by setrand(1)
setrand(1); r = iferr(alginit(nfinit(y), [-2,-p]), E, Str(E)); show("R1 setrand(1); alginit(nfinit(y), [-2,-p])", r);
setrand(1); r = iferr(alginit(nfinit(y), [-p,-2]), E, Str(E)); show("R2 setrand(1); alginit(nfinit(y), [-p,-2])", r);
setrand(1); A3 = alginit(nfinit(y), [-2,-p], , 0);
print("R3 setrand(1); alginit(nfinit(y), [-2,-p], , 0) -> initialised; algramifiedplaces = ", algramifiedplaces(A3), "; algnorm(1) = ", algnorm(A3, [1,0,0,0]~), "; algnorm(2) = ", algnorm(A3, [2,0,0,0]~));
\\ three further diagnostics (card J5(c) allows up to three)
setrand(1); r = iferr(alginit(nfinit(t), [-2,-p]), E, Str(E)); show("D1 setrand(1); alginit(nfinit(t), [-2,-p])   [other nf variable]", r);
setrand(1); r = iferr(alginit(nfinit(y), [-2,-9*p]), E, Str(E)); show("D2 setrand(1); alginit(nfinit(y), [-2,-9*p]) [same algebra: 9 is a square]", r);
default(parisize, 400000000);
setrand(1); r = iferr(alginit(nfinit(y), [-2,-p]), E, Str(E)); show("D3 parisize=4e8; setrand(1); alginit(nfinit(y), [-2,-p])", r);
quit;
```

Output (sha256 `12fc4efce348ea7cbaafd264f0103b66f1b7c8725363c8f62fc16a3a09eca1d7`, ANSI codes stripped):

```
version: [2, 15, 4]
isprime(p,2) = 1   p mod 8 = 5
Hilbert (-2,-p): at 2 -> 1, at p -> -1;  kronecker(-2,p) = -1, kronecker(-1,p) = 1, kronecker(2,p) = -1
R1 setrand(1); alginit(nfinit(y), [-2,-p]) -> error("impossible inverse in dvmdii: 0.")
R2 setrand(1); alginit(nfinit(y), [-p,-2]) -> error("impossible inverse in dvmdii: 0.")
R3 setrand(1); alginit(nfinit(y), [-2,-p], , 0) -> initialised; algramifiedplaces = [1, [9223372036854775837, [9223372036854775837]~, 1, 1, 1]]; algnorm(1) = 1; algnorm(2) = 4
D1 setrand(1); alginit(nfinit(t), [-2,-p])   [other nf variable] -> error("impossible inverse in dvmdii: 0.")
D2 setrand(1); alginit(nfinit(y), [-2,-9*p]) [same algebra: 9 is a square] -> error("impossible inverse in dvmdii: 0.")
  ***   Warning: new stack size = 400000000 (381.470 Mbytes).
D3 parisize=4e8; setrand(1); alginit(nfinit(y), [-2,-p]) -> error("impossible inverse in dvmdii: 0.")
```

### `phaseB_scratch.gp`

Command:

```
(ulimit -v 4000000; timeout 900 gp -q --default parisize=200000000 phaseB_scratch.gp) > phaseB_scratch.out 2>&1
```

Script (sha256 `93784546c072c5931ad8314d8812c12c52a91f043d59d52ce7c951feb96cef17`):

```gp
\\ validator-eecb7f Phase B scratch (own code; reuses the Phase A library qlib.gp).
\\ Diagnostics only: nothing here is a contract cell (RV-6).
read("qlib.gp");

\\ ---------------- J1(b): field of definition, own point counts over F_{p^2}
{countE(q, gen, a) = my(n = 1, z);
  \\ own naive count of y^2 = x^3 + a x over F_q: point at infinity, then every x in
  \\ {0} u {gen^e : 0 <= e <= q-2}, gen a multiplicative generator of F_q^*
  for(e = -1, q-2,
    my(x = if(e < 0, 0*gen, gen^e));
    z = x^3 + a*x;
    if(z == 0, n += 1, if(z^((q-1)/2) == 1, n += 2)));
  n;}
{forp = [7, 11];
for(t = 1, #forp,
  my(p = forp[t], g = ffgen(p^2, 'w), q = p^2, gen = ffprimroot(g), res = []);
  print("p = ", p, " (p mod 4 = ", p%4, "), q = p^2 = ", q, ", generator order ", fforder(gen));
  for(e = 0, 3,
    my(a = gen^e, N = countE(q, gen, a), tr = q + 1 - N);
    print("   y^2 = x^3 + g^", e, " x :  #E(F_{p^2}) = ", N, "   trace t = ", tr,
          "   frob char poly x^2 - (", tr, ")x + ", q, " = ", factor(x^2 - tr*x + q),
          "   [check vs ellcard: ", ellcard(ellinit([0,0,0,a,0], g)), "]")));}

\\ ---------------- J1(a): JMV-convention form Hom(Ei,Ej) ~ (Ij^-1 Ii, Nrd/n) at p = 13
a=-2; b=-13; p=13; M=[1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1];
{findalpha(a,b,M,N,R) = my(fl = factor(N)[,1]);
  forvec(c = vector(4,k,[-R,R]), my(v=c~, al=M*v, ok=1); if(v==0, next);
    for(t=1,#fl, if(v%fl[t]==0, ok=0)); if(ok && qnrd(a,b,al)%N==0, return(al))); 0;}
Ii = lideal(a,b,M,findalpha(a,b,M,3,3),3); Ij = lideal(a,b,M,findalpha(a,b,M,5,3),5);
nj = nrdideal(a,b,Ij);
{G = matrix(4,0); for(r=1,4, for(s=1,4, G = concat(G, qmul(a,b,qconj(Ij[,r]),Ii[,s])/nj)));}
Jl = latspan(G);
c = denominator(Jl); Jint = c*Jl; nJ = nrdideal(a,b,Jint);
{print("\nJ1(a) JMV form at p=13: n(Ii)=", nrdideal(a,b,Ii), ", n(Ij)=", nj, ", J = Ij^-1 Ii scaled by ", c, ": n(cJ) = ", nJ,
      ", det(cJ, Nrd/n(cJ)) = ", matdet(gramq(a,b,Jint,nJ)), "  (p^2/16 = ", p^2/16, ")");}
\\ convention independence: conj(I) and I^-1 = conj(I)/n(I) with Nrd*n(I)
Ib = matconcat(vector(4,r,qconj(Ii[,r]))); ni = nrdideal(a,b,Ii);
{print("   det(conj I, Nrd/n) = ", matdet(gramq(a,b,Ib,ni)), ";  det(I^-1 = conjI/n(I), Nrd*n(I)) = ", matdet(gramq(a,b,Ib/ni,1/ni)),
      ";  det(I, Nrd/n) = ", matdet(gramq(a,b,Ii,ni)));}

\\ ---------------- J1(c): the note's hand checks and the conjugation determinant
Ahur = [1,0,0,1/2; 0,1,0,1/2; 0,0,1,1/2; 1/2,1/2,1/2,1];
print("\nJ1(c) note Hurwitz matrix det = ", matdet(Ahur), "; my Hurwitz Gram = ", gramq(-1,-1,[1,0,0,1/2;0,1,0,1/2;0,0,1,1/2;0,0,0,1/2],1));
print("   block [[1,1/2],[1/2,(1+p)/4]] det = ", matdet([1,1/2;1/2,(1+'p)/4]));
{foreach([[2,-1,-1,[1,0,0,1/2;0,1,0,1/2;0,0,1,1/2;0,0,0,1/2]],[13,-2,-13,M]], cs,
  my(Mb = cs[4], Cj = matsolve(Mb, matconcat(vector(4,r,qconj(Mb[,r])))));
  print("   det of x -> conj(x) on O (p=", cs[1], ") = ", matdet(Cj), ", integral: ", denominator(Cj)==1));}

\\ ---------------- J3(a): Hermite constant check (gamma_4 = sqrt 2 recalled)
H = [1,0,0,1/2;0,1,0,1/2;0,0,1,1/2;0,0,0,1/2]; AH = gramq(-1,-1,H,1);
mH = qfminim(2*AH)[2]/2;
print("\nJ3(a) Hurwitz (p=2): min Nrd = ", mH, ", det = ", matdet(AH), ", min/det^(1/4) = ", mH/matdet(AH)^(1/4), "  (sqrt2 = ", sqrt(2), ")");
D4 = [2,-1,0,0;-1,2,-1,-1;0,-1,2,0;0,-1,0,2];
print("   D4: min = ", qfminim(D4)[2], ", det = ", matdet(D4), ", min/det^(1/4) = ", qfminim(D4)[2]/matdet(D4)^(1/4));

\\ ---------------- PT objects
print("\n==== PT-1: (P^0, Nrd/p)");
{PT1 = [[13,-2,-13,[1/2,0,0,0;0,1/4,0,0;1/2,1/2,1,0;1/2,1/4,0,1]], [17,-17,-3,[1/2,0,0,0;0,1/2,0,0;1/2,0,1/3,0;0,1/2,1/3,1]],
        [101,-2,-101,[1/2,0,0,0;0,1/4,0,0;1/2,1/2,1,0;1/2,1/4,0,1]]];
 foreach(PT1, cs, my(p=cs[1], a=cs[2], b=cs[3], Mb=cs[4], Pc=pcand(a,b,Mb,p), P0=tr0(Pc), D=matdet(gramq(a,b,P0,p)), mn);
   mn = qfminim(2*p*gramq(a,b,P0,p))[2]/(2*p);
   print("   p=", p, ": maximal ", maxtest(a,b,Mb)[1], ", rank ", #P0, ", det(P^0,Nrd/p) = ", D, " (p/4: ", D==p/4, "), log_p(det)/3 = ", log(D)/log(p)/3,
         ", min(Nrd/p on P^0) = ", mn, ", Hermite gamma_3 det^(1/3) = 2^(1/3)(p/4)^(1/3) = ", 2^(1/3)*(p/4.)^(1/3), " = (p/2)^(1/3) = ", (p/2.)^(1/3)));}

print("\n==== PT-2 and PT-6: Z[i] in End(E), E: y^2=x^3+x, p = 3 mod 4 (End(E) ~ Z<1,i,(1+j)/2,(i+k)/2> in (-1,-p), i=[i]: recalled)");
{foreach([7,11,103], p, my(Mb=[1,0,1/2,0;0,1,0,1/2;0,0,1/2,0;0,0,0,1/2], Zi=[1,0;0,1;0,0;0,0], A2=gramq(-1,-p,Zi,1),
     A4=matconcat([A2,matrix(2,2);matrix(2,2),A2]));
   print("   p=", p, ": O maximal ", maxtest(-1,-p,Mb)[1], ", Z[i] c O: ", isintv(matsolve(Mb,Zi)), ", Gram(Z[i],deg) = ", A2, ", det = ", matdet(A2),
         ", log_p(det)/2 = 0;  PT-6 Z[i]+Z[i] Gram det = ", matdet(A4), " (rank 4, <= p)"));}

print("\n==== PT-3: O^# (dual under the trace pairing) with Nrd");
{foreach([[13,-2,-13,[1/2,0,0,0;0,1/4,0,0;1/2,1/2,1,0;1/2,1/4,0,1]], [17,-17,-3,[1/2,0,0,0;0,1/2,0,0;1/2,0,1/3,0;0,1/2,1/3,1]]], cs,
   my(p=cs[1], a=cs[2], b=cs[3], Mb=cs[4], T=trform(a,b,Mb), Od=Mb*T^(-1), Ad=gramq(a,b,Od,1), idx=abs(matdet(T)));
   print("   p=", p, ": [O^#:O] = ", idx, ", det(O^#,Nrd) = ", matdet(Ad), " = det(O)/[O^#:O]^2 = ", (p^2/16)/idx^2, ", Nrd on O^# basis = ", vector(4,r,Ad[r,r]),
         ", Nrd integral on O^#: ", denominator(vector(4,r,Ad[r,r]))==1, ", log_p(det)/4 = ", log(matdet(Ad))/log(p)/4));}

print("\n==== PT-4: actual minima vs the certificate bound (c_4/2) p^(1/2), p = 103");
{my(p=103, a=-1, b=-p, Mb=[1,0,1/2,0;0,1,0,1/2;0,0,1/2,0;0,0,0,1/2], A=gramq(a,b,Mb,1), al, I, n, AI, mI);
  print("   End(E): min deg = ", qfminim(2*A)[2]/2, " (the identity), det = ", matdet(A), ", certificate bound (sqrt2/2) p^(1/2) = ", sqrt(2)/2*sqrt(p));
  al = findalpha(a,b,Mb,2,3); I = lideal(a,b,Mb,al,2); n = nrdideal(a,b,I); AI = gramq(a,b,I,n);
  mI = qfminim(2*AI)[2]/2;
  print("   Hom(E,E') for the 2-isogenous E' (I = O alpha + 2O, n(I) = ", n, "): det(I,Nrd/n) = ", matdet(AI), ", min deg = ", mI,
        ", right order maximal: ", maxtest(a,b,latspan(matconcat(vector(16,t,qmul(a,b,qconj(I[,(t-1)\4+1]),I[,(t-1)%4+1]))))/n)[1]);}

print("\n==== J5 scratch check of the A2 base order at the blocking prime (NOT an A1 cell; RV-6)");
{my(p=9223372036854775837, a=-2, b=-p, Mb=[1/2,0,0,0;0,1/4,0,0;1/2,1/2,1,0;1/2,1/4,0,1], mt=maxtest(a,b,Mb), Pc=pcand(a,b,Mb,p));
  print("   p=", p, ": ramified ", ramif(a,b), ", is order ", isorder(a,b,Mb), ", maximality test ", mt[1], " [", mt[2], "], det(O,Nrd) = p^2/16: ",
        matdet(gramq(a,b,Mb,1)) == p^2/16, ", P check ", pcheck(a,b,Mb,p), ", det(P^0,Nrd/p) = p/4: ", matdet(gramq(a,b,tr0(Pc),p)) == p/4);}
quit;
```

Output (sha256 `3ddebb9ce9b4a5f37d9270bf0ca20903ca9e6ff0d016725211cb3ef6713b4006`, ANSI codes stripped):

```
p = 7 (p mod 4 = 3), q = p^2 = 49, generator order 48
   y^2 = x^3 + g^0 x :  #E(F_{p^2}) = 64   trace t = -14   frob char poly x^2 - (-14)x + 49 = Mat([x + 7, 2])   [check vs ellcard: 64]
   y^2 = x^3 + g^1 x :  #E(F_{p^2}) = 50   trace t = 0   frob char poly x^2 - (0)x + 49 = Mat([x^2 + 49, 1])   [check vs ellcard: 50]
   y^2 = x^3 + g^2 x :  #E(F_{p^2}) = 36   trace t = 14   frob char poly x^2 - (14)x + 49 = Mat([x - 7, 2])   [check vs ellcard: 36]
   y^2 = x^3 + g^3 x :  #E(F_{p^2}) = 50   trace t = 0   frob char poly x^2 - (0)x + 49 = Mat([x^2 + 49, 1])   [check vs ellcard: 50]
p = 11 (p mod 4 = 3), q = p^2 = 121, generator order 120
   y^2 = x^3 + g^0 x :  #E(F_{p^2}) = 144   trace t = -22   frob char poly x^2 - (-22)x + 121 = Mat([x + 11, 2])   [check vs ellcard: 144]
   y^2 = x^3 + g^1 x :  #E(F_{p^2}) = 122   trace t = 0   frob char poly x^2 - (0)x + 121 = Mat([x^2 + 121, 1])   [check vs ellcard: 122]
   y^2 = x^3 + g^2 x :  #E(F_{p^2}) = 100   trace t = 22   frob char poly x^2 - (22)x + 121 = Mat([x - 11, 2])   [check vs ellcard: 100]
   y^2 = x^3 + g^3 x :  #E(F_{p^2}) = 122   trace t = 0   frob char poly x^2 - (0)x + 121 = Mat([x^2 + 121, 1])   [check vs ellcard: 122]

J1(a) JMV form at p=13: n(Ii)=3, n(Ij)=5, J = Ij^-1 Ii scaled by 20: n(cJ) = 240, det(cJ, Nrd/n(cJ)) = 169/16  (p^2/16 = 169/16)
   det(conj I, Nrd/n) = 169/16;  det(I^-1 = conjI/n(I), Nrd*n(I)) = 169/16;  det(I, Nrd/n) = 169/16

J1(c) note Hurwitz matrix det = 1/4; my Hurwitz Gram = [1, 0, 0, 1/2; 0, 1, 0, 1/2; 0, 0, 1, 1/2; 1/2, 1/2, 1/2, 1]
   block [[1,1/2],[1/2,(1+p)/4]] det = 1/4*p
   det of x -> conj(x) on O (p=2) = -1, integral: 1
   det of x -> conj(x) on O (p=13) = -1, integral: 1

J3(a) Hurwitz (p=2): min Nrd = 1, det = 1/4, min/det^(1/4) = 1.4142135623730950488016887242096980786  (sqrt2 = 1.4142135623730950488016887242096980786)
   D4: min = 2, det = 4, min/det^(1/4) = 1.4142135623730950488016887242096980786

==== PT-1: (P^0, Nrd/p)
   p=13: maximal 1, rank 3, det(P^0,Nrd/p) = 13/4 (p/4: 1), log_p(det)/3 = 0.15317456371512017247059466436623847040, min(Nrd/p on P^0) = 1, Hermite gamma_3 det^(1/3) = 2^(1/3)(p/4)^(1/3) = 1.8662555784086241214825753036782705394 = (p/2)^(1/3) = 1.8662555784086241214825753036782705394
   p=17: maximal 1, rank 3, det(P^0,Nrd/p) = 17/4 (p/4: 1), log_p(det)/3 = 0.17023297192118264640682567251201479507, min(Nrd/p on P^0) = 1, Hermite gamma_3 det^(1/3) = 2^(1/3)(p/4)^(1/3) = 2.0408275509586740352828908066130214826 = (p/2)^(1/3) = 2.0408275509586740352828908066130214826
   p=101: maximal 1, rank 3, det(P^0,Nrd/p) = 101/4 (p/4: 1), log_p(det)/3 = 0.23320634451754135644729355076273469574, min(Nrd/p on P^0) = 1, Hermite gamma_3 det^(1/3) = 2^(1/3)(p/4)^(1/3) = 3.6962708958568577704718159066249100594 = (p/2)^(1/3) = 3.6962708958568577704718159066249100594

==== PT-2 and PT-6: Z[i] in End(E), E: y^2=x^3+x, p = 3 mod 4 (End(E) ~ Z<1,i,(1+j)/2,(i+k)/2> in (-1,-p), i=[i]: recalled)
   p=7: O maximal 1, Z[i] c O: 1, Gram(Z[i],deg) = [1, 0; 0, 1], det = 1, log_p(det)/2 = 0;  PT-6 Z[i]+Z[i] Gram det = 1 (rank 4, <= p)
   p=11: O maximal 1, Z[i] c O: 1, Gram(Z[i],deg) = [1, 0; 0, 1], det = 1, log_p(det)/2 = 0;  PT-6 Z[i]+Z[i] Gram det = 1 (rank 4, <= p)
   p=103: O maximal 1, Z[i] c O: 1, Gram(Z[i],deg) = [1, 0; 0, 1], det = 1, log_p(det)/2 = 0;  PT-6 Z[i]+Z[i] Gram det = 1 (rank 4, <= p)

==== PT-3: O^# (dual under the trace pairing) with Nrd
   p=13: [O^#:O] = 169, det(O^#,Nrd) = 1/2704 = det(O)/[O^#:O]^2 = 1/2704, Nrd on O^# basis = [1, 2, 10/13, 5/13], Nrd integral on O^#: 0, log_p(det)/4 = -0.77023815442731974129410800345064229440
   p=17: [O^#:O] = 289, det(O^#,Nrd) = 1/4624 = det(O)/[O^#:O]^2 = 1/4624, Nrd on O^# basis = [1, 1/17, 3, 6/17], Nrd integral on O^#: 0, log_p(det)/4 = -0.74465054211822603038976149123197780740

==== PT-4: actual minima vs the certificate bound (c_4/2) p^(1/2), p = 103
   End(E): min deg = 1 (the identity), det = 10609/16, certificate bound (sqrt2/2) p^(1/2) = 7.1763500472036618735021498207361340497
   Hom(E,E') for the 2-isogenous E' (I = O alpha + 2O, n(I) = 2): det(I,Nrd/n) = 10609/16, min deg = 2, right order maximal: 1

==== J5 scratch check of the A2 base order at the blocking prime (NOT an A1 cell; RV-6)
   p=9223372036854775837: ramified [9223372036854775837, "inf"], is order 1, maximality test 1 [binary disc form anisotropic mod p], det(O,Nrd) = p^2/16: 1, P check [1, 1, 85070591730234616400799229995519050569, 1], det(P^0,Nrd/p) = p/4: 1
```

### `j2_faults.gp`

Command:

```
(ulimit -v 4000000; timeout 900 gp -q --default parisize=200000000 j2_faults.gp) > j2_faults.out 2>&1
```

Script (sha256 `97a369b0b3d22cfb3c5fbd3fa7cc1d65c337873e034aeb7a6302fd58b61d6dd7`):

```gp
\\ validator-eecb7f J2(b): instrument faults that the frozen contract's C-ALG checks
\\ would NOT catch, and the R value the contract would then score as F-NORM.
read("qlib.gp");
a=-2; b=-13; p=13; M=[1/2,0,0,0; 0,1/4,0,0; 1/2,1/2,1,0; 1/2,1/4,0,1];
{findalpha(a,b,M,N,R) = my(fl = factor(N)[,1]);
  forvec(c = vector(4,k,[-R,R]), my(v=c~, al=M*v, ok=1); if(v==0, next);
    for(t=1,#fl, if(v%fl[t]==0, ok=0)); if(ok && qnrd(a,b,al)%N==0, return(al))); 0;}
Rv(L, s) = matdet(gramq(a,b,L,s))*16/p^2;
calgc(L) = [isorder(a,b,L), denominator(vector(4,r,qnrd(a,b,L[,r])))==1, denominator(vector(4,r,qtrd(L[,r])))==1];
\\ (1) A1 fault: a non-maximal order returned as "the maximal order" (here Z + 2O)
Z2 = latspan(concat([1,0,0,0]~, 2*M));
print("A1 fault  Z+2O : C-ALG(c) [order, Nrd integral, Trd integral] = ", calgc(Z2), "  R = ", Rv(Z2,1), "  -> contract code F-NORM");
\\ (2) A5 fault: a suborder O' of the true right order (the v1 dev bug D-8 produced non-maximal right orders)
Iq = lideal(a,b,M,findalpha(a,b,M,3,3),3); n = nrdideal(a,b,Iq);
OR = latspan(matconcat(vector(16,t,qmul(a,b,qconj(Iq[,(t-1)\4+1]),Iq[,(t-1)%4+1]))))/n;
Osub = latspan(concat([1,0,0,0]~, 2*OR));
cd = prod(i=1,4,prod(j=1,4,inlat(Iq,qmul(a,b,Iq[,i],Osub[,j]))));
print("A5 fault  Z+2O_R(I) : C-ALG(c) = ", calgc(Osub), ", C-ALG(d) I*O' c I = ", cd, "  R = ", Rv(Osub,1), "  (true O_R(I): R = ", Rv(OR,1), ")  -> F-NORM");
\\ (3) A3 fault: pO returned as P (two-sided, p | Nrd on basis) under the fixed form Nrd/p
pO = p*M;
e = [prod(i=1,4,prod(j=1,4,inlat(pO,qmul(a,b,M[,i],pO[,j])))), prod(i=1,4,prod(j=1,4,inlat(pO,qmul(a,b,pO[,j],M[,i])))), vector(4,r,qnrd(a,b,pO[,r])%p==0)];
print("A3 fault  pO : C-ALG(e) [OP c P, PO c P, p|Nrd on basis] = ", e, "  R(Nrd/p) = ", Rv(pO,p), ", [O:P] = ", abs(matdet(matsolve(M,pO))), "  -> F-NORM");
\\ (4) A4 fault: n(I) mis-measured as gcd of the diagonal only (misses the 2A_ij terms)
A = gramq(a,b,Iq,1); nd = gcd(vector(4,r,A[r,r]));
print("A4 check  n(I) true = ", n, ", gcd(diagonal) = ", nd, "  (equal here; a mis-measured n would give R = (n/n')^4 != 1 -> F-NORM)");
quit;
```

Output (sha256 `7326189a2e31f190226c7d927f1896d6bd6a67aee533b4cdbe9eeb063b726c47`, ANSI codes stripped):

```
A1 fault  Z+2O : C-ALG(c) [order, Nrd integral, Trd integral] = [1, 1, 1]  R = 64  -> contract code F-NORM
A5 fault  Z+2O_R(I) : C-ALG(c) = [1, 1, 1], C-ALG(d) I*O' c I = 1  R = 64  (true O_R(I): R = 1)  -> F-NORM
A3 fault  pO : C-ALG(e) [OP c P, PO c P, p|Nrd on basis] = [1, 1, [1, 1, 1, 1]]  R(Nrd/p) = 28561, [O:P] = 28561  -> F-NORM
A4 check  n(I) true = 3, gcd(diagonal) = 3  (equal here; a mis-measured n would give R = (n/n')^4 != 1 -> F-NORM)
```

---

## Not done

- **Implementation-hash binding.** I did not compare the manifests'
  `implementation_sha256` values with the committed blobs, because doing so
  reads `implementation/` (blind_from). A non-blind session can close this
  with `git show b4ae42bfd:<impl path> | sha256sum` for the three v1 and four
  v2 files.
- **Running `check.py` or `compare_runs.py`.** Not run (RV-2). I replaced them
  with my own recomputation and comparison.
- **The `gp_calls[].script` fields of both raw-result.json files.** Not read.
  They embed producer gp code. Only their labels, return codes, stderr and
  record counts were printed.
- **The in-repo De Feo survey PDF**
  (`inputs/ECTD-TESKE-20260731/sources/defeo-1711.04062.pdf`). I tried to read
  it, but the Read tool failed ("pdftoppm is not installed") and no PDF text
  tool is available, so it was not read. The general-pair interface was
  instead traced to the JMV text file.
- **Proofs of the recalled inputs** (disc(O) = p^2 in full, hereditary maximal
  orders, the local structure at p, connectedness of the isogeny graph). Not
  opened, because no in-repo source was located for them. They stay `recalled`.
- **Hom(E, E^t) = 0.** Not established by enumerating isogenies. It rests on
  the Frobenius and point-count argument (J1(b)), which is a proof.
- **ECDLP and cost.** Not applicable. Nothing here bears on any ECDLP claim or
  cost.

---

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260926-eecb7f
  role: validator
  joints_owned: [J1, J2, J3, J4, J5, J6, J7]
  proves_too_much_owned: [PT-1, PT-2, PT-3, PT-4, PT-5, PT-6]
  requested_policy: review-adversarial
  policy_resolution: "python3 -m orchestration.adapter resolve --role validator --independent-session -> anthropic:claude-opus-5 (effort=xhigh)"
  resolved_model_id: claude-opus-5-5
  model_provenance: runtime-reported (session system context); not probe-verified (model_verified false)
  reasoning_effort: >-
    The agent file .claude/agents/validator.md declares effort xhigh (line 17).
    The effective effort is not observable from inside the session.
  fallback_used: true
  fallback_reason: >-
    Subagents run with model: inherit, so the session model claude-opus-5-5
    served instead of the policy-resolved claude-opus-5. The card declares
    fallback_allowed: true for a backend/model substitution only. The tier
    requested was review-adversarial at xhigh, and no requirement is known to
    be degraded. This is the same model identity as the producer runs (L-4), so
    concurrence is session-independent, not model-independent.
  independent_session: true
  independence_note: >-
    This session did not produce the note, the implementation or either run,
    and did not author the card.
  commit_read: b4ae42bfd
  commits_read_other:
    - "6ec32c261 (HEAD; the card, working tree identical)"
    - "3ea7223b9 (derivation-note.md, byte-compared: identical)"
    - "3d8faa394 (specification.yaml, sha256 only)"
    - "da16c1908 (AMD-20260926-f9acf7.yaml, sha256 only)"
  phase_a_sources:
    - "ledger/handoffs/TASK-20260926-eecb7f.yaml lines 1-330 only (Grep for the marker returned lines 10, 320, 330)"
    - "own knowledge, every input marked recalled (R1-R8 in Section A)"
    - "own scratch code: qlib.gp, phaseA_q1q3.gp, phaseA_q2.gp and their outputs"
    - "DISCLOSED, not opened by me: the harness-injected CLAUDE.md (generic runtime text, nothing about EXP-SSIQ-6916e8)"
    - >-
      DISCLOSED: the dispatch message (my task prompt), received before Phase
      A. Beyond the card pointer it named J1-J7 and PT-1..PT-6, mentioned an
      "F_{p^2} twist issue anticipated in J1", and named PARI/GP. It stated no
      determinant, index or exponent value and no derivation method for
      Q1-Q3.
  sources_read:
    - ledger/handoffs/TASK-20260926-eecb7f.yaml (lines 1-330 Phase A; lines 330-972 Phase B)
    - AGENTS.md
    - agents/validator.md
    - templates/research-records.md (lines 560-702)
    - docs/claims-and-verification.md (lines 133-170)
    - tools/check_review_independence.py (lines 137-180, 480-520, grep hits)
    - .claude/agents/validator.md (grep hits for model/effort lines only)
    - experiments/EXP-SSIQ-6916e8/derivation-note.md (git show b4ae42bfd, full; git show 3ea7223b9, byte compare)
    - experiments/EXP-SSIQ-6916e8/specification.yaml (git show b4ae42bfd, full; git show 3d8faa394, sha256)
    - experiments/EXP-SSIQ-6916e8/amendments/AMD-20260926-f9acf7.yaml (git show b4ae42bfd, full; git show da16c1908, sha256)
    - experiments/EXP-SSIQ-6916e8/execution-report.yaml (git show b4ae42bfd, full)
    - experiments/EXP-SSIQ-6916e8/execution-report-v2.yaml (git show b4ae42bfd, full)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/manifest.yaml (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/raw-result.json (b4ae42bfd; parsed by own scripts; gp_calls[].script fields not read)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/command.txt (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/environment.json (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/stdout.log (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/stderr.log (b4ae42bfd; empty)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/check.stdout.log (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-81bd08/check.stderr.log (b4ae42bfd; empty)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/manifest.yaml (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/raw-result.json (b4ae42bfd; parsed by own scripts; gp_calls[].script fields not read)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/command.txt (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/environment.json (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/stdout.log (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/stderr.log (b4ae42bfd; empty)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/check.stdout.log (b4ae42bfd)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/check.stderr.log (b4ae42bfd; empty)
    - experiments/EXP-SSIQ-6916e8/runs/RUN-SSIQ-004595/comparison-to-RUN-SSIQ-81bd08.json (b4ae42bfd; top-level keys and totals)
    - ledger/hypotheses/H-SSIQ-a9df38.yaml (b4ae42bfd, full)
    - ledger/proposals/IDEA-20260926-e1b48e.yaml (b4ae42bfd; grep hits; lines 26-70 and 270-280)
    - ledger/decisions/DEC-20260926-e05697.yaml (b4ae42bfd; grep hits only)
    - ledger/decisions/DEC-20260926-f9acf7.yaml (b4ae42bfd; lines 170-268)
    - ledger/decisions/DEC-20260805-2be965.yaml (b4ae42bfd; lines 1-140 and grep hits)
    - ledger/evidence/EV-SSIQ-e43afd.yaml (b4ae42bfd; grep hits)
    - ledger/goals/GOAL-SSIQ-001/goal.yaml (b4ae42bfd; lines 430-700 and grep hits)
    - inputs/P13-WESOLOWSKI-2026/paper_fulltext.md (b4ae42bfd; lines 236-252; grep hits at lines 19, 77, 81, 177)
    - inputs/JMV-0411378-20260907/sources/jmv-math-0411378v3.txt (b4ae42bfd; lines 1-12, 1300-1345, grep hits)
    - inputs/JMV-0411378-20260907/sources/jmv-math-0411378v3-layout.txt (b4ae42bfd; grep hit lines 420, 982, 1151 only)
    - inputs/JMV-0411378-20260907/provenance.json (b4ae42bfd; first 40 lines)
    - inputs/ECTD-TESKE-20260731/sources/defeo-1711.04062.pdf.sha256 (and a failed attempt to read the PDF; its content was not read)
    - "inputs/ (directory listings; git grep hit lines: idea_generation_20260717.md:765, idea_generation_20260718.md:1203, refs/experiments/ecdlp_prime_field/round018_results.md:12, refs/research/ISO_GOAL_isogenous_weak_curve.md:45, refs/research/p256_isogeny_class_invariance.md:110; file-name-only hits for kohel|voight)"
    - "knowledge/ (git grep at b4ae42bfd: file-name list for kohel|voight; hit lines knowledge/techniques/KN-TECH-028.md:17,19 and knowledge/literature/KN-LIT-7563.md:74)"
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/reviews/RT-BATCH-001.md (b4ae42bfd; lines 120-175 and grep hits)
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-002/reviews/RT-BATCH-002.md (b4ae42bfd; lines 570-590)
    - "coordination/goals/GOAL-SSIQ-001/batches/ (git grep hit lines for admissib|log_p(det)/rank under BATCH-001..007 reviews and BATCH-001 tasks)"
    - "git log / git show --stat for 254729199, 3ea7223b9, da16c1908, b4ae42bfd, 3d8faa394 (implementation/ lines filtered out before display); git ls-tree b4ae42bfd for experiments/EXP-SSIQ-6916e8 (implementation/ paths filtered out before display) and runs/"
    - "orchestration adapter CLI output (python3 -m orchestration.adapter resolve --role validator [--independent-session])"
  sources_not_read_by_design:
    - experiments/EXP-SSIQ-6916e8/implementation/ (blind_from; never read, hashed or executed)
    - experiments/EXP-SSIQ-6916e8/implementation/v2/ (blind_from; never read, hashed or executed)
    - executor return reports of TASK-20260926-7d20e4 and TASK-20260926-fba7e0 (not available to this session)
    - gp_calls[].script fields inside both raw-result.json files (they embed producer gp code)
  reading_order: >-
    Phase A read only card lines 1-330, plus the disclosed dispatch message
    and the harness-injected CLAUDE.md. Section A was written to the report
    path at 2026-09-26T03:23:51Z, and a scratch copy was taken. The first
    Phase B read, the card from line 330, happened at or after 03:23:58Z.
    Before Section A was written, no repository path other than the card's
    Phase A part was opened, no MCP server was queried and no git command was
    run. No slip occurred. Section A was not edited afterwards: a byte
    comparison against the scratch copy was taken before appending Phase B.
  read_sibling_reports: false
  blind_from_respected: true
  runs_launched: 0
  run_ids_minted: []
  repository_writes: [experiments/EXP-SSIQ-6916e8/reviews/validator-TASK-20260926-eecb7f.md]
  verdict:
    J1: breaks
    J2: breaks
    J3: holds
    J4: holds
    J5: holds
    J6: holds
    J7: holds
  verdict_notes:
    J1: >-
      Statement-level break of H-SSIQ-a9df38's wording. Over F_{p^2},
      Hom(E, E^t) = 0 at p = 7, 11 (#E = 64/144 vs 36/100), and
      End_{F_{p^2}} of the quartic twist has rank 2. The claim is true for the
      geometric Hom. The note's mathematics holds, conditional on the listed
      recalled inputs. Line 244 is cited correctly. The general-pair interface
      is now traceable in-repo to JMV lines 1312-1325. (D) should quantify
      over the ideal class of E', not over O_R(I) ≅ End(E').
    J2: >-
      Breaks as stated. Every arm and control reduces to classes (i)-(v), and
      (vi) is empty. The run checks the note's normalisation constant and the
      instruments only. The contract would have scored F-NORM for instrument
      faults on A1, A3 and A5, which was demonstrated. This matches the
      Coordinator's prior; run validity is unaffected.
    J3: >-
      The Hermite direction, gamma_4 = sqrt2 and (c4/2)p^{1/2} are all
      correct. The criterion is a Hermite exponent (RT-BATCH-001 lines
      145-148), and its rank-4 option was located in g >= 2. The lemma closes
      only the g = 1 single-Hom sub-case. H is correctly scoped.
    J4: >-
      All of PT-1..PT-6 stop at their named steps. Wording hazards: "exponent
      floor" (note line 180) and "can never certify" (H lines 15-17). The
      unqualified "Dimension-one N5 via rank 4 is closed" appears only in
      IDEA-20260926-e1b48e.
    J5: >-
      R1/R2 raise and R3 initialises, reproduced deterministically. D1 (other
      variable), D2 ([-2,-9p]) and D3 (parisize) raise too. This is a PARI
      maximal-order-routine defect independent of the claim. The A2 base is
      maximal by my Lemma-B-free test. The tally dictates
      INCONCLUSIVE-CONSTRUCTION. There is no SUCCESS reading, and A1 may not
      be admitted from R3.
    J6: >-
      Two runs; schema complete; seeds 924/924. Every measured count and state
      recomputes exactly. Defects: the stated total "1946" should be 2398; the
      d3/v1 "64 cells" lists 87 items; the note's sha256 is bound by neither
      manifest (AMD C-7 misstates this); and fallback_used ran against
      fallback_allowed false.
    J7: >-
      Blind values p^2/16, n(I)^2 and p/4 agree with the note and with
      RUN-SSIQ-004595.
  recorded_at: '2026-09-26T03:48:35Z'
```
