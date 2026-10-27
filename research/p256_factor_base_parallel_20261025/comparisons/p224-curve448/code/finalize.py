"""Derive the Hasse order certificates and render observations, without new trials."""
import hashlib,json,math,platform,sys
from pathlib import Path
from flint import fmpz

ROOT=Path(__file__).resolve().parent.parent
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
producer=load(ROOT/'producer-result.json');independent=load(ROOT/'independent-result.json')
assert independent['status']=='PASS' and len(independent['checks'])==4
groups=[]
for filename in ('p224-s16-domain.json','curve448-s16-domain.json'):
    path=ROOT/'certificates'/filename;cert=load(path);c=cert['parameters'];p,r,h=c['p'],c['r'],c['h']
    assert fmpz(p).is_prime() and fmpz(r).is_prime()
    disc=(-16*(4*c['a']**3+27*c['b']**2))%p;assert disc!=0
    radius=math.isqrt(4*p);lower=p+1-radius;upper=p+1+radius
    kmin=(lower+r-1)//r;kmax=upper//r;assert kmin==kmax==h
    groups.append(dict(curve=c['name'],p=p,r=r,h=h,cardinality=h*r,discriminant=disc,
      primality=dict(p=True,r=True,implementation='python-flint fmpz.is_prime (FLINT proven primality API)'),
      hasse=dict(radius_floor_2sqrtp=radius,lower=lower,upper=upper,first_multiple_index=kmin,last_multiple_index=kmax),
      proof='Independent affine checker verifies a nonidentity G with [r]G=O. Prime r gives ord(G)=r, so r divides #E. Hasse interval contains exactly the multiple h*r.',
      generator=cert['public_generator'],domain_certificate_sha256=sha(path),independent_result_sha256=sha(ROOT/'independent-result.json')))
save(ROOT/'certificates'/'group-orders.json',groups)
result=dict(schema='p224-curve448-local-comparison/v1',task='TASK-20261025-8c305c',
 status='all finite-domain implementation checks passed',validation_status='unvalidated',
 independent_implementation=True,independent_session_review=False,claim_tier='crypto',
 results=producer['results'],group_order_certificate='certificates/group-orders.json',
 producer_result_sha256=sha(ROOT/'producer-result.json'),independent_result_sha256=sha(ROOT/'independent-result.json'),
 custody=producer['custody'],no_uploads_or_git_mutations=True,
 limitations=['Only S=16,32 deterministic generic cosets were checked; no S=64 extension was needed.',
 'No uniform target yield, field-size scaling, asymptotic, end-to-end, or attack-cost inference.',
 'Independent arithmetic implementation in the same executor session; no scientific review gate discharged.',
 'Normal committed-and-pushed handoff condition is unmet; sealed local input exception retained.'],
 command_environment=dict(python=sys.version,platform=platform.platform(),python_flint='0.8.0',
 requested_policy='executor-implementation',requested_reasoning='high',actual_model='inherited parent model; not probed',
 model_verified=False,fallback_used=False,degraded_requirements=[]),
 sources=[dict(provenance='internal',path='../../baseline/parameters.py',use='Published parameter input, copied constants'),
 dict(provenance='internal',path='../../baseline/s4-symmetric.json',use='Producer symmetric S4 coefficient input'),
 dict(provenance='internal',path='/workspace/dickson-inspection/curve_arithmetic.py',use='Read-only arithmetic reference; implementation rewritten as Jacobian and affine checks'),
 dict(provenance='internal',path='/workspace/dickson-inspection/bigfield.py',use='Read-only finite-domain comparison reference'),
 dict(provenance='internal',path='../../../../tools/curve_identity.py',use='Canonical JSON identity algorithm reproduced; identities include exact model and generator')])
save(ROOT/'result.json',result)

rows=[];controls=[]
for r in result['results']:
    counts=r['lift_counts']
    rows.append(f"| {r['name']} | {r['S']} | {r['M']} | {r['signed_base']} | {counts['non-lift']} | {counts['cofactor rejection']} |")
    cc=r['cases']
    controls.append(f"| {r['name']} | {r['S']} | "+' | '.join(str(q['solutions']) for q in cc)+' | '+str(sum(q['repeated_coordinate_solutions'] for q in cc))+' |')
report='''# P-224 and Curve448: exact finite-domain observations

TASK-20261025-8c305c; 25 October 2026. These are local implementation observations on the actual published prime fields. They do not change a scientific status. Independent implementations agree on every complete domain and point decomposition set below.

## Measured observations

M denotes the number of accepted canonical points (x,min(y,p-y)); the signed base contains both signs. Every domain has S distinct roots. Zero-y exclusions were zero in all four cases.

| Curve | S | Canonical M | Signed points | Non-lifts | Cofactor rejections |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

All 12 control sets were completely enumerated. Entries below count unordered signed-point multisets of size three, allowing repetition. The last column counts solutions with repeated x coordinates across the controls.

| Curve | S | Constructed repeated positive | Base cancellation | Unrelated public generator | Repeated-x solutions |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(controls)+'''

Each constructed target is 2P0+P1. Each cancellation target is the last canonical base point Q; all M solutions P+(-P)+Q are retained, including equal-coordinate cases. The unrelated controls use a public standard generator x coordinate, lifted to its canonical sign. Those zero counts concern these four targets and bases only. No secret scalar is supplied to the search.

## Exact domains, curve identities and subgroup checks

P-224 has p=2^224-2^96+1, a=-3, the input b and prime order r, cofactor 1. Its split multiplicative ambient order p-1 has 2-adicity 96. Curve448 has p=2^448-2^224-1 and Montgomery equation v^2=u^3+156326u^2+u. The invertible translation x=u+156326/3, y=v gives the exact short Weierstrass coefficients in each domain certificate. Its norm-one torus has order p+1 with 2-adicity 224; the elliptic curve has cofactor 4. The torus implementation uses F_(p^2)=F_p[i], i^2=-1; p=3 mod4 makes this extension irreducible.

For each S, zeta has exact order S. The deterministically chosen alpha satisfies c=alpha^S+alpha^(-S) != +/-2. Domain roots are x_k=alpha*zeta^k+(alpha*zeta^k)^(-1). In the torus this is the field trace. D_1(X)=X and D_(2n)=D_n(X)^2-2 give H(X)=D_S(X)-c. Every certificate retains alpha, zeta, c, all S roots, every linear factor with multiplicity, and all H coefficients. Explicit polynomial multiplication equals H, all FLINT roots equal the constructed roots, and gcd(H,H')=1. This proves the complete factorization over the actual field for each specified domain.

Both p and r pass FLINT's proven primality API. Nonsingularity and the nonidentity public generator relation [r]G=O are checked. The Hasse interval contains precisely the multiple h*r, proving the full elliptic curve order from that subgroup witness. The explicit integer bounds are in [group-orders.json](certificates/group-orders.json). Every candidate y is checked; non-lifts are retained. Every nonzero lift undergoes the exact [r]P=O test. Curve448's rejected residual points are retained, and cofactor multiplication is never substituted for membership. No y=0 occurred.

Each domain certificate contains the full metadata identity preimage, EC1 alias and full curve UID. These identify the exact short Weierstrass representation and chosen canonical generator sign. They are metadata identities, not claims of registry registration or a hash proof of isomorphism. Curve448's displayed Montgomery-to-short translation supplies its mathematical relationship.

## Complete decomposition controls and independence

The producer evaluates the supplied symmetric S4 polynomial on every unordered x triple in the entire domain, including non-lifts and cofactor exclusions. This checks 816 x multisets at S=16 and 5984 at S=32 per target. It retains every S4-zero candidate, the exclusion reasons, all accepted sign assignments and the full signed solution set. No division by differences of x coordinates is used. Repeated coordinates are included throughout.

The producer separately enumerates all signed-point triples with Jacobian sums. The independent checker imports no producer arithmetic: it uses affine secant/tangent sums and a left-to-right scalar ladder, computes S4 zeros from the resultant of the two original quadratic f3 polynomials, and independently multiplies polynomial coefficients and factors the full H. It scans every x multiset and every signed-point multiset. Both complete signed sets and complete S4-zero candidate sets agree for all twelve controls. The signed multiset counts per target are 816/8436 for P-224 and 20/120 for Curve448 at S=16/32 respectively.

This is implementation independence within the same executor session. It is not an independent scientific review. Producer certificates preserve their original pending-check field; [independent-result.json](independent-result.json) records the later successful replay without rewriting them.

## Artifacts, custody and scope

The complete canonical M values, exact full domain factorizations, rejected lifts and cofactor residuals are in the four *-domain.json files under [certificates](certificates). Every target's complete S4 and signed solutions has its own certificate. [result.json](result.json) indexes counts and scope; [producer-result.json](producer-result.json) records the original observation, source/input hashes, environment, base commit and dirty-tree state. [code/producer.py](code/producer.py), [code/independent.py](code/independent.py), [code/finalize.py](code/finalize.py), [commands.txt](commands.txt), stdout/stderr logs and [manifest.json](manifest.json) support replay. Each retained file is below 64 KiB before the coordinator's PDF rendering.

The baseline parameter and S4 inputs are internal supplied artifacts. Their use and code inspection provenance are listed in result.json. No source file from /workspace/dickson-inspection is imported; the local reference was read and the arithmetic paths were written self-contained here. Standard references are NIST SP 800-186 section3.2.1 and RFC7748 section4 (bibliographic pointers recalled from the internal source list; not independently fetched in this task).

Normal committed-and-pushed handoff compliance is **unmet**. Execution uses the explicitly recorded [local-custody exception](../../reviews/local-custody-exception.json); the new task card is local. This does not discharge an archive, review, promotion or publication gate. No upload, Git mutation or PR operation was performed. Explicit public-disclosure approval remains pending. The coordinator handles local snapshots and PDF rendering.

S=16 and32 were the fixed domain sizes. Both curves had nonempty accepted bases, so the conditional S=64 extension did not run. There were four completed cases, twelve completed controls, zero failed executions and zero timed-out executions. Runtime fields in the raw records describe these executions only and are not a performance comparison. No statistical uncertainty is attached to exact complete enumeration. No uniform-target yield, field-size scaling, asymptotic or attack-cost conclusion follows from these finite cases.

The quantitative [diagram.svg](diagram.svg) shows recorded coordinate counts for these four domains. Its editable source is code/finalize.py. Existing canonical scientific graphs were inspected only by scope: this local finite-domain record changes no canonical relationship, and no shared graph was edited. The next reviewable step is a separate reviewer replaying these certificates, followed by any specifically authorized expansion of domain sizes; the present observations already cover their full declared finite scope.
'''
(ROOT/'report.md').write_text(report)

# Editable deterministic SVG bar chart, using only recorded counts.
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="400" viewBox="0 0 900 400">',
 '<rect width="900" height="400" fill="#f8fafc"/>',
 '<g font-family="sans-serif" fill="#0f172a"><text x="30" y="32" font-size="21">Exact coordinate disposition on published fields</text>',
 '<text x="30" y="56" font-size="13">TASK-20261025-8c305c · four complete deterministic domains · counts of x coordinates</text>']
colors=['#0f766e','#94a3b8','#c2410c'];labels=['Canonical accepted M','Non-lift','Cofactor rejection']
for i,r in enumerate(result['results']):
    y=85+i*55;parts.append(f'<text x="30" y="{y+21}" font-size="15">{r["name"]} S={r["S"]}</text>');x=225
    for value,color in zip([r['M'],r['lift_counts']['non-lift'],r['lift_counts']['cofactor rejection']],colors):
        if value:
            width=value*15;parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="30" fill="{color}"/><text x="{x+width/2}" y="{y+21}" fill="white" text-anchor="middle" font-size="14">{value}</text>');x+=width
for i,(label,color) in enumerate(zip(labels,colors)):
    x=30+i*280;parts.append(f'<rect x="{x}" y="325" width="18" height="18" fill="{color}"/><text x="{x+25}" y="339" font-size="14">{label}</text>')
parts.extend(['<text x="30" y="380" font-size="13">All factorization, subgroup and 3-point solution-set checks passed; no yield or scaling inference.</text></g></svg>'])
(ROOT/'diagram.svg').write_text('\n'.join(parts)+'\n')
save(ROOT/'manifest.json',dict(schema='local-content-sha256/v1',files={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='manifest.json'}))
print(json.dumps(dict(status='PASS',case_count=4,control_count=12,group_orders_proved=2,largest_file_bytes=max(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()))))
