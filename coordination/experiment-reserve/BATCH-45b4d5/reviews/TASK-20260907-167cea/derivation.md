# TASK-20260907-167cea blind mathematical derivation

This note covers only the assigned joint: the transported CM identity, the
conductor-three level rule and exceptional multiplicities, and the exact
finite-panel cost/decision quantifiers. It does not review producer code or any
scientific run, and it does not give a whole-package, launch, status, or ECDLP
verdict. The report remains pending Coordinator archive task
`TASK-20260907-e71ece` and adjudication.

## 1. Exact transport identity and endpoint normalization

Let

\[
  \phi:E_0\longrightarrow E_k,
  \qquad
  \psi=\widehat\phi:E_k\longrightarrow E_0
\]

be a separable degree-three isogeny and its exact dual on the models actually
used by the evaluator. Then

\[
  \psi\phi=[3]_{E_0},\qquad \phi\psi=[3]_{E_k}.
\]

Let \(\iota\in\operatorname{End}(E_0)\) be the selected \(i\)-endomorphism and
define

\[
  \beta=\phi\circ\iota\circ\psi\in\operatorname{End}(E_k).
\]

The whole-curve identity is

\[
\begin{aligned}
  \beta^2
   &=\phi\iota\psi\phi\iota\psi \\
   &=\phi\iota[3]\iota\psi \\
   &=\phi[-3]\psi \\
   &=[-3]\phi\psi=[-9]_{E_k}.
\end{aligned}
\]

Now let \(G_0=\langle P\rangle\) have prime order \(r\ne 3,p\), and assume
\(\iota(P)=[\lambda]P\). Since \(\gcd(r,3)=1\), \(\phi\) restricts to an
isomorphism from \(G_0\) onto \(G_k=\phi(G_0)\). For \(R=\phi(P)\),

\[
\begin{aligned}
  \psi(R)&=\psi\phi(P)=[3]P,\\
  \beta(R)&=\phi\iota([3]P)=\phi([3\lambda]P)=[3\lambda]R.
\end{aligned}
\]

Thus the scalar is exactly

\[
  m=3\lambda\pmod r.
\]

It is not \(\lambda\), and the sign is fixed by the check
\([\lambda]G_0=\iota(G_0)\). Because \(r\ge127\) is prime and \(r\ne3\),
\((3-1)\lambda\ne0\) and \(6\lambda\ne0\pmod r\); both the missing factor and
the wrong sign differ from the required scalar on every nonzero point.

Model normalization is load-bearing. If \(v:E_0\to E_{\rm raw}\) is the raw
isogeny and \(\alpha:E_{\rm raw}\to E_k\) is a selected codomain isomorphism,
then

\[
  \phi=\alpha v,
  \qquad
  \psi=\widehat v\,\alpha^{-1}.
\]

For a coordinate isomorphism \(\rho_u:E_k\to E_k^{(u)}\), the conjugated maps
must be

\[
  \phi_u=\rho_u\phi,
  \qquad
  \psi_u=\psi\rho_u^{-1},
  \qquad
  \beta_u=\rho_u\beta\rho_u^{-1}.
\]

Checking a raw dual on a post-composed codomain is insufficient. Both dual
compositions must be checked on the actual source and target models before a
scalar comparison is meaningful. The dual identities and the codomain
normalization issue are supported by the retrieved primary technical source:
Daniel Shumow, *Isogenies of Elliptic Curves: A Computational Approach*,
Theorem 2.23, Remark 2.24, and Section 3
(<https://eprint.iacr.org/2009/522.pdf>; provenance: `retrieved`, verified by
`TASK-20260907-167cea`).

## 2. Conductor-three certificate and exceptional multiplicity

For \(E_0:y^2=x^3-x\) in characteristic \(p\equiv1\pmod4\), the selected
square root \(\iota_0^2=-1\) defines

\[
  \iota(x,y)=(-x,\iota_0 y),\qquad \iota^2=[-1].
\]

Under the frozen assumption \(\operatorname{End}(E_0)=\mathbb Z[i]\), write
Frobenius as \(\pi=a+bi\). Then \(t=2a\), \(p=a^2+b^2\), and

\[
  D_\pi=t^2-4p=-4b^2=-4f_\pi^2,
  \qquad f_\pi=[\mathbb Z[i]:\mathbb Z[\pi]]=|b|.
\]

The certificate must check this equality, the integrality of \(f_\pi\), and
\(v_3(f_\pi)=1\). Full rational \(E_0[3]\) gives four Frobenius-stable cyclic
order-three kernels. Since 3 is inert in \(\mathbb Q(i)\),

\[
  \left(\frac{-4}{3}\right)=-1,
\]

so the maximal order has no horizontal degree-three edge. The maximal source
cannot ascend. Each of its four rational kernels therefore descends by index
three, and because the 3-adic depth of \(\mathbb Z[\pi]\) is exactly one, the
target order is

\[
  \mathcal O_3=\mathbb Z+3\mathbb Z[i]
\]

and is already at the floor of rationality. Its rational degree-three edge
count must be exactly one, the ascending dual edge. This is a useful
fixture-level certificate rather than an assumption to fill when a check is
missing.

The four kernels do **not** give four target isomorphism classes. The source has
\(|\mathcal O_K^*|=4\), while the conductor-three order has only the units
\(\{\pm1\}\). Kohel's unit-corrected descending-target count is

\[
  \frac{3-\left(\frac{-4}{3}\right)}
       {[\mathcal O_K^*:\mathcal O_3^*]}
  =\frac{3-(-1)}{4/2}=2.
\]

The same fact is visible directly on the four lines of \(E_0[3]\cong\mathbb
F_3^2\). Projectively, multiplication by \(i\) can be represented by

\[
  J=\begin{pmatrix}0&-1\\1&0\end{pmatrix},
\]

whose characteristic polynomial \(X^2+1\) has no root over \(\mathbb F_3\).
It has no fixed projective line and its two orbits are

\[
  \{(1:0),(0:1)\},\qquad
  \{(1:1),(1:2)\}.
\]

Kernels in the same orbit yield explicitly isomorphic quotient targets over
\(\mathbb F_p\), because the source automorphism is defined over
\(\mathbb F_p\). A conforming artifact therefore needs four `kernel_id`/map
endpoints, two `isomorphism_class_id` values, multiplicity two for each class,
and the within-pair isomorphisms. Four equation labels may be retained, but
they cannot be called four independent arithmetic classes.

The level and multiplicity count are supported by the retrieved primary
source David Kohel, *Endomorphism rings of elliptic curves over finite fields*,
Section 4.2, especially Propositions 21 and 23
(<https://www.i2m.univ-amu.fr/perso/david.kohel/pub/thesis.pdf>; provenance:
`retrieved`, verified by `TASK-20260907-167cea`). Proposition 23 explicitly
identifies the unit-index factor with the automorphism-orbit size.

## 3. Fully charged cost formula

The specification names the correct categories of cost, but it does not index
them finely enough to determine one number. Let

- \(c\) be one of the six deterministic source classes;
- \(k\in\{1,2,3,4\}\) be a labeled cyclic-kernel endpoint;
- \(u\in\{1,2,3\}\) be a coordinate presentation;
- \(s\in\{606101,606103\}\) be a measurement seed;
- \(q\in\{1,16,256,4096\}\); and
- \(a\) be a scalar-baseline arm.

One coherent whole-class-batch definition would be

\[
\begin{aligned}
T_T(c,u,s,q)={}&C_{\rm shared}(c)+C_{\rm discovery}(c)
 +C_{\rm pointcount/factor}(c)+C_{\rm kernel}(c)+C_{\rm eigensign}(c)\\
&+\sum_{k=1}^{4}\left(
 C_{\rm map}(c,k)+C_{\rm level}(c,k)+C_{\rm norm}(c,k,u)
 +\sum_{j=1}^{q}
  (C_\psi+C_\iota+C_\phi+C_{\rm verify})_{c,k,u,s,j}
\right),\\[3pt]
T_S(c,u,s,q)={}&C_{\rm shared}(c)+C_{\rm select}(c,u)
 +\sum_{k=1}^{4}\left(
 C_{\rm scalar\ setup}(a^*,c,k,u)
 +\sum_{j=1}^{q}(C_{\rm mul}+C_{\rm verify})_{a^*,c,k,u,s,j}
\right),\\[3pt]
R(c,u,s,q)={}&\frac{T_S(c,u,s,q)}{T_T(c,u,s,q)}.
\end{aligned}
\]

Using each \(k\) exactly once gives equal kernel-endpoint weight. Dividing both
whole totals by four gives the same ratio. It is not generally equivalent to
averaging four ratios: for scalar totals \([1,1,9,9]\) and transport totals
\([1,1,3,3]\), the ratio of totals is \(20/8=2.5\), while the mean of floor
ratios is \((1+1+3+3)/4=2.0\).

This displayed formula is a proposed disambiguation, not an amendment. The
Coordinator must freeze the intended allocation. In particular, discovery,
point counting/factorization, kernel enumeration, all rejected candidates,
maps, level certificates, eigenvalue-sign selection, normalization and
conversion remain on the transport side. Scalar selection must charge every
candidate arm, table and repeated selection block. Verification is charged on
both sides. Shared query generation may be reported and canceled only under
the specification's separately labeled scaffolding rule. The direct \([3]i\)
top computation is a separate mandatory known-resource control and does not
silently enter or leave the four-floor ratio.

The specification also must choose the domain of the baseline argmin. For
example, a valid rule could be

\[
 a^*_{c,u}=\operatorname*{argmin}_{a\in\mathcal A}
   \sum_{k=1}^4 T^{\rm selection}_{S}(a,c,k,u,606101,256),
\]

with a deterministic tie-break, followed by freezing \(a^*_{c,u}\) for every
\(q\) and both seeds. A global or per-class-only rule could also be frozen, but
the current prose does not choose among them. The cost of the selection event
is shared across cells, so its allocation also must be explicit. On the
confirmatory seed, the selected arm remains fixed even if the descriptive
oracle minimum is lower. In the fixed mock, development times \([10,11,9]\)
select arm 3; confirmatory times \([8,20,12]\) must use 12 for the frozen arm
and may report 8 only as the oracle descriptor.

Charging a q=256 selection exercise inside the q=1 scalar total is permitted by
the frozen protocol, but then the q=1 result is a protocol-defined cold-total
scenario. It is not ordinary one-query evaluation latency. The eventual report
must retain that interpretation boundary.

The omitted-discovery known-false control used the fixed illustrative costs

\[
 S(q)=30+2q,\quad T_{\rm full}(q)=5000+q,\quad
 T_{\rm omit}(q)=5+q.
\]

At \(q=4096\), the fully charged ratio is \(8222/9096=0.9039138083\), while
the omitted-cost ratio is \(8222/4101=2.0048768593\). The frozen-ladder
crossover changes from \(>4096\) to 1. This is a synthetic decision-branch
counterexample only; it is not a measured cost, a prediction, or an estimate
of the prospective implementation.

## 4. Complete finite-panel quantifiers

Let `Complete` mean all of the following:

1. exactly two eligible source classes were selected in each of the three
   frozen intervals before timing, giving six source classes;
2. every class has all four labeled kernel/map endpoints, exactly two
   multiplicity-two target isomorphism classes, valid dual/level/subgroup/model
   certificates and every mandatory control;
3. every floor, coordinate, seed, query-ladder and required algorithm cell is
   present; and
4. every primary timing block reaches the declared resolution, with no invalid
   control or unexplained coordinate-instrument warning.

With a uniquely frozen equal-floor aggregate, the 36 primary q=4096 ratios are

\[
 \{R(c,u,s,4096):c=1,\ldots,6;\ u=1,2,3;\
   s\in\{606101,606103\}\}.
\]

The exact branches are

\[
\begin{aligned}
\textsf{positive}
 &\iff \textsf{Complete}\ \land\
   \forall c,u,s:\ R(c,u,s,4096)\ge1.20,\\
\textsf{negative-scoped}
 &\iff \textsf{Complete}\ \land\
   \forall c,u,s:\ R(c,u,s,4096)\le1,\\
\textsf{inconclusive}
 &\text{ otherwise.}
\end{aligned}
\]

Therefore any mixed outcome, ratio strictly between 1 and 1.20, missing class,
missing coordinate, missing floor contribution, failed certificate, or
below-resolution primary block is inconclusive. Thirty-five favorable cells
and one unavailable cell cannot become a complete-panel positive. Floors,
coordinates and seeds are paired/repeated views of the six deterministic
classes and do not increase the independent-instance count.

For each \((c,u,s)\),

\[
 q^*=\min\{q\in[1,16,256,4096]:R(c,u,s,q)\ge1\}
\]

is exact only if every earlier ladder cell is resolved below one. `>4096` is
valid only if all four ladder cells are resolved below one. If, for example,
\(R_1=0.8\), \(R_{16}\) is unresolved, \(R_{256}=1.2\), and
\(R_{4096}=1.4\), the first resolved crossing is 256 but exact \(q^*\) is
unknown because it may be 16. No interpolation is allowed.

Seed 606101 is the development/selection seed at q=256. Seed 606103 is the
clean confirmatory seed for the frozen scalar arm. Both are required finite
cells, but they are not two independent source-class samples, and the oracle
minimum on 606103 cannot replace the selected arm.

## 5. Fixed checker and cumulative budget

The following one-worker command executed 24 fixed arithmetic/mock cases. It
performed no curve search, frozen-fixture search, scientific control, timing
panel, or implementation inspection. It completed 24/24 cases in 0.07 wall
seconds, 0.02 user CPU seconds and 0.01 system CPU seconds. Peak RSS was not
recorded. No case was rerun after the provider interruption.

```sh
/usr/bin/time -p python3 -c '
cases=[]
def ok(name, cond, detail):
    if not cond:
        raise AssertionError(name + ": " + str(detail))
    cases.append((name, detail))
r=149
lam=44
m=(3*lam)%r
ok("lambda_square", (lam*lam)%r==r-1, {"r":r,"lambda":lam})
ok("beta_square", (m*m)%r==(-9)%r, {"m":m,"m2":(m*m)%r})
ok("wrong_factor_rejected", m!=lam%r, {"correct":m,"wrong":lam%r})
ok("wrong_sign_rejected", m!=(-3*lam)%r, {"correct":m,"wrong":(-3*lam)%r})
a=7
ainv=pow(a,-1,r)
correct=(a*m*ainv)%r
wrong=(a*m)%r
ok("model_conjugation_correct", correct==m, {"a":a,"correct":correct})
ok("unadjusted_dual_wrong", wrong!=m, {"a":a,"wrong":wrong,"expected":m})
legendre_minus4_mod3=-1
ok("three_inert", legendre_minus4_mod3==-1, {"kronecker":legendre_minus4_mod3})
distinct_targets=(3-legendre_minus4_mod3)//(4//2)
ok("exceptional_target_count", distinct_targets==2, {"kernels":4,"unit_index":2,"targets":distinct_targets})
floor_legendre=0
ok("floor_rational_edge_count", floor_legendre+1==1, {"D":-36,"rational_edges":1})
lines=[(1,0),(0,1),(1,1),(1,2)]
def norm(v):
    x,y=v[0]%3,v[1]%3
    if x:
        z=pow(x,-1,3); return ((x*z)%3,(y*z)%3)
    z=pow(y,-1,3); return (0,(y*z)%3)
def J(v): return norm((-v[1],v[0]))
expected=[(0,1),(1,0),(1,2),(1,1)]
for idx,(v,e) in enumerate(zip(lines,expected),1):
    ok("orbit_line_"+str(idx),J(v)==e,{"line":v,"image":J(v)})
seen=set(); orbits=[]
for v in lines:
    if v in seen: continue
    orb={v,J(v)}; seen|=orb; orbits.append(sorted(orb))
ok("orbit_count",len(orbits)==2 and all(len(o)==2 for o in orbits),{"orbits":orbits})
Q=[1,16,256,4096]
S={q:30+2*q for q in Q}
Tf={q:5000+q for q in Q}
To={q:5+q for q in Q}
Rf={q:S[q]/Tf[q] for q in Q}
Ro={q:S[q]/To[q] for q in Q}
qf=next((q for q in Q if Rf[q]>=1),">4096")
qo=next((q for q in Q if Ro[q]>=1),">4096")
ok("omitted_discovery_false_gain",Ro[4096]>=1.2 and Rf[4096]<1 and qo==1 and qf==">4096",{"full_R4096":Rf[4096],"omitted_R4096":Ro[4096],"full_qstar":qf,"omitted_qstar":qo})
def branch(vals,complete=True,resolved=True):
    if not complete or not resolved: return "inconclusive"
    if all(x>=1.2 for x in vals): return "positive"
    if all(x<=1.0 for x in vals): return "negative"
    return "inconclusive"
ok("missing_cell_inconclusive",branch([1.3]*35,complete=False)=="inconclusive",{"resolved_cells":35,"required_cells":36})
ok("below_resolution_inconclusive",branch([1.3]*36,resolved=False)=="inconclusive",{"below_resolution_cells":1})
dev=[10,11,9]; conf=[8,20,12]; chosen=min(range(3),key=lambda i:dev[i])
ok("baseline_selection_freeze",chosen==2 and conf[chosen]==12 and min(conf)==8,{"chosen_arm":chosen,"confirm_fixed":conf[chosen],"confirm_oracle":min(conf)})
ratios={1:0.8,16:None,256:1.2,4096:1.4}
first_resolved=next(q for q in Q if ratios[q] is not None and ratios[q]>=1)
exact=all(ratios[q] is not None for q in Q if q<=first_resolved)
ok("crossover_missing_earlier_unresolved",first_resolved==256 and not exact,{"first_resolved_crossing":first_resolved,"exact_qstar":None})
scalar=[1,1,9,9]; transport=[1,1,3,3]
ratio_of_totals=sum(scalar)/sum(transport)
mean_of_ratios=sum(s/t for s,t in zip(scalar,transport))/4
ok("aggregate_definition_matters",ratio_of_totals!=mean_of_ratios,{"ratio_of_totals":ratio_of_totals,"mean_of_floor_ratios":mean_of_ratios})
kernel_weights=[0.25]*4
iso_weights=[kernel_weights[0]+kernel_weights[1],kernel_weights[2]+kernel_weights[3]]
ok("exceptional_multiplicity_weights",iso_weights==[0.5,0.5],{"kernel_weights":kernel_weights,"isomorphism_class_weights":iso_weights})
ok("complete_success_branch",branch([1.2]*36)=="positive",{"cells":36,"minimum":1.2})
ok("complete_falsification_branch",branch([1.0]*36)=="negative",{"cells":36,"maximum":1.0})
ok("threshold_gap_inconclusive",branch([1.1]*36)=="inconclusive",{"cells":36,"ratio":1.1})
print("STATIC_CHECKS",len(cases))
for name,detail in cases:
    print(name,"PASS",detail)
'
```

Artifact validation used cases 25 through 27: the initial YAML parse, exact
two-file custody/nonempty check, and the final post-accounting YAML reparse. The
initial two-case command completed in 0.12 wall seconds, 0.05 user CPU seconds
and 0.01 system CPU seconds with one worker. The cumulative fixed-case count is
27, leaving three unused cases. Operational preflight and source-hash reads are
repository-integrity operations and did not execute candidate arithmetic or
mock cases.

## 6. Blindness and interruption disclosure

No path in the plan's `blind_from` list was read. No producer code, producer
test, producer execution plan, producer mathematical note/report, producer
snapshot narrative, or sibling review was read. The only non-task historical
material read was `/Users/adamburan/.codex/memories/MEMORY.md` lines 37-78,
because the session-level memory instructions required a quick pass. It is a
high-level 2026-09-05 CM intake registry entry; no linked rollout was opened and
no technical conclusion in this derivation relies on it. This is disclosed as
a procedure deviation rather than silently omitted.

The parent coordinator reported that the earlier invocation ended with a
terminal usage-limit error and resumed this same claim after a live usage
check. At resume, both assigned output paths were absent. The same
`review-adversarial` / `gpt-5.6-sol` / `xhigh` configuration was retained, no
reset credit or purchase was used, and no mathematical case was duplicated.
The interruption says nothing about this joint.
