"""Derived report artifacts only; reads sealed fixed-check certificates."""
from pathlib import Path
from html import escape
import hashlib
import json
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
R=HERE/'receipts'
producer=json.loads((R/'check-04'/'receipt.json').read_text())
independent=json.loads((R/'independent-04.json').read_text())
adversarial=json.loads((R/'adversarial-03.json').read_text())
assert producer['status']==independent['status']==adversarial['status']=='passed'
def put(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
for name,kind,command,reason in [
    ('check-01','software_failure',
     'SYMPY_GROUND_TYPES=flint /workspace/dickson-solver/.venv/bin/python research/p256_factor_base_parallel_20261025/tracks/f4/validate.py --out research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-01',
     'SymPy 1.14.0 factor_list FLINT conversion TypeError at 256-bit field; fixed by direct FLINT factor API'),
    ('independent-01','environment_path_failure',
     'SYMPY_GROUND_TYPES=python /usr/local/bin/python3 research/p256_factor_base_parallel_20261025/tracks/f4/independent_check.py research/p256_factor_base_parallel_20261025/tracks/f4/receipts/check-02 --receipt research/p256_factor_base_parallel_20261025/tracks/f4/receipts/independent-01.json',
     '/usr/local/bin/python3 does not exist; used resolved non-Ubuntu python3 path')]:
    put(R/(name+'.failure.json'),{'status':kind,'command':command,'exit_code':1 if name=='check-01' else 127,
        'reason':reason,'scientific_inference':'none; no mathematical negative evidence',
        'stdout_sha256':hashlib.sha256((R/(name+'.stdout')).read_bytes()).hexdigest(),
        'stderr_sha256':hashlib.sha256((R/(name+'.stderr')).read_bytes()).hexdigest(),
        'full_redirection_command':'commands.md'})

pieces=['''<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="900" viewBox="0 0 1320 900">
<title>F4 exact P-256 divisor and signed cancellation checks</title>
<desc>Fixed correctness fixtures, with independent modular ranks; no yield trial.</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#546e7a"/></marker></defs>
<rect width="1320" height="900" fill="#f8fafc"/>
<style>text{font-family:Arial,sans-serif;fill:#183247} .title{font-size:28px;font-weight:bold}.head{font-size:20px;font-weight:bold}.body{font-size:17px}.small{font-size:15px}.line{stroke:#546e7a;stroke-width:2;fill:none}.card{fill:#fff;stroke:#c7d4df;stroke-width:1.5}</style>
''']
def text(X,Y,value,kind='body'):
    pieces.append(f'<text x="{X}" y="{Y}" class="{kind}">{escape(str(value))}</text>')
def rect(X,Y,W,H):pieces.append(f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="12" class="card"/>')
def line(x1,y1,x2,y2,arrow=False):pieces.append(f'<path d="M{x1} {y1} L{x2} {y2}" class="line"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
def dot(X,Y,label):
    pieces.append(f'<circle cx="{X}" cy="{Y}" r="7" fill="#146c94"/>');text(X+12,Y+6,label,'small')
text(35,45,'F4 · actual P-256 · exact divisor / signed graph prototype','title')
text(35,75,'TASK-20261025-ce1163 · fixed correctness inputs · no performance or yield claim','small')
for X,title,lines in [(35,'Sample / construct functions',['L(mO), m = 3…8','f = A(x) + y B(x)','anchors and inverse pairs retained']),
                      (470,'Certify principal divisor',['N = A² − (x³ − 3x + b) B²','factor + local multiplicity jets','29 cases; 5 nonrational unresolved']),
                      (905,'Cancel signed outside columns',['A c = 0 modulo subgroup r','24 stitched group sums checked','separate Jacobian + rank consumer'])]:
    rect(X,105,380,150);text(X+16,135,title,'head')
    for i,item in enumerate(lines):text(X+16,169+29*i,item)
line(420,180,460,180,True);line(855,180,895,180,True)
rect(35,280,1250,255);text(55,310,'Measured fixed-fixture rank accounting (mod r)','head')
headers=[('family',55),('raw rows',420),('all-column rank',550),('outside rank',740),('kernel dim.',900),('after rank',1060),('zero rows',1170)]
for h,X in headers:text(X,345,h,'small')
for i,(key,label) in enumerate([('one_outside','one outside / hub'),('two_outside','two outside / balanced cycle'),('combined','combined pole fixtures'),('unbalanced_triangle','same-sign triangle')]):
    v=producer['graph_ranks'][key];Y=383+39*i
    vals=[label,v['input_rows'],v['rank_before_all_columns'],v['outside_incidence_rank'],v['kernel_dimension'],v['rank_after_cancellation'],v['zero_cancelled_rows']]
    for (_,X),val in zip(headers,vals):text(X,Y,val,'small')
rect(35,560,605,230);text(55,590,'Balanced square: one independent base relation','head')
coords=[(110,635),(390,635),(390,735),(110,735)]
for i,(X,Y) in enumerate(coords):
    U,V=coords[(i+1)%4];line(X,Y,U,V,True)
for (X,Y),label in zip(coords,['100G','101G','103G','106G']):dot(X,Y,label)
text(435,650,'oriented endpoints','small');text(435,680,'iG and −jG','small')
text(55,775,'G + 2G + 3G − 6G = O; duplicate edge adds zero rank','small')
rect(665,560,620,230);text(685,590,'Same-sign triangle: no cancellation','head')
tri=[(745,735),(845,635),(945,735)]
for i,(X,Y) in enumerate(tri):U,V=tri[(i+1)%3];line(X,Y,U,V)
for (X,Y),label in zip(tri,['100G','101G','103G']):dot(X,Y,label)
text(1015,650,'outside rank = 3','small');text(1015,680,'kernel = {0}','small')
text(685,775,'Unsigned graph cycles alone do not imply signed relations','small')
text(35,827,'Exact uniform-section control: P(all zeros rational affine) = binom(r+m−2,m) / (r p^(m−1))','body')
text(35,853,'This counts multiplicities across the whole curve; factor-base yield / natural rank per total cost remains unrun.','small')
text(35,879,'Evidence: receipts/check-04, independent-04.json, adversarial-03.json, exact-counts.json · editable SVG source','small')
pieces.append('</svg>')
svg='\n'.join(pieces)+'\n'
ET.fromstring(svg)
(HERE/'diagram.svg').write_text(svg)

result={'schema':'f4-implementation-result/v1','task_id':'TASK-20261025-ce1163','track':'F4',
 'status':'implementation_checks_passed','scientific_trial_run':False,'official_state_transition':False,
 'performance_advantage_claim':False,'input_commit_requested':'2c8c71cfff6f7f63297fbe4de4608cd94d857184',
 'actual_head':producer['head'],'curve':{k:producer[k] for k in ['p','a','b','r','generator']},
 'checks':{'divisor_cases':producer['divisor_cases'],'fully_rational':producer['fully_rational_cases'],
           'unresolved_nonrational':producer['unresolved_cases'],'pole_orders':producer['pole_orders_checked'],
           'expected_api_refusals':producer['expected_rejections'],'irreducible_factors':independent['irreducible_factor_checks'],
           'local_branch_multiplicity_checks':independent['local_branch_multiplicity_checks'],
           'stitched_group_sums':independent['stitched_group_sums'],
           'corrupt_certificates_detected':len(adversarial['controls']),
           'abstract_counting_checks':18,'ranks':producer['graph_ranks']},
 'sampling_parameters':json.loads((R/'check-04'/'sampling_controls.json').read_text()),
 'algebra':{'function':'A(x)+yB(x)','norm':'A^2-(x^3-3x+b)B^2',
            'exact_pole':'max(2deg(A),3+2deg(B))',
            'cancellation':'kernel of signed outside incidence modulo r',
            'exact_unanchored_all_rational_probability':'binom(r+m-2,m)/(r*p^(m-1)), 2<=m<r',
            'uniform_anchor_control':'projective exact-top slice of evaluation kernel, cardinality p^(d-1)',
            'graph_eligibility':'complete rational divisor; at most two nonzero outside inverse-orbit columns'},
 'limitations':['Constructed split positives and repeated outside points certify correctness only.',
                'No natural yield, collision-frequency, rank-growth or comparative cost trial.',
                'Nonrational norm factors retained as unresolved; extension-prime-divisor recovery absent.',
                'Rational 2-torsion jets unsupported; P-256 cubic irreducibility excludes this branch.',
                'Dense signed-kernel oracle retains witnesses; sparse scalable cycle engine absent.',
                'No unknown target attachment, logarithm recovery, full solve or amortized comparison.',
                'Separate arithmetic implementations share author/session; no independent scientific review.',
                'Published order/cofactor assumed, not independently point-counted or primality-certified.'],
 'failures_retained':['receipts/check-01.failure.json','receipts/independent-01.failure.json'],
 'resources_for_fixed_validation_only':{k:producer[k] for k in ['wall_seconds','cpu_seconds','max_rss_kib']},
 'environment':{'python':producer['python'],'sympy':producer['sympy'],'python_flint':'0.8.0',
                'platform':producer['platform'],'inference_binding':'native Codex inherited; unprobed'},
 'artifacts':{'report':'report.md','diagram':'diagram.svg','methods_commands':'commands.md',
              'producer':'receipts/check-04/receipt.json','separate_checker':'receipts/independent-04.json',
              'corruptions':'receipts/adversarial-03.json','exact_counting':'receipts/exact-counts.json',
              'obstruction':'obstruction.md'},
 'next_decisive_step':'Coordinator freezes a matched conditional-law paired trial with natural structured/base controls and all-draw full resource/rank accounting, then independent replay.',
 'pdf':'Root renders per-track and aggregate PDF under the handoff; no PDF generated by this executor.'}
put(HERE/'result.json',result)
files={str(f.relative_to(HERE)):{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
       for f in sorted(HERE.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.name!='manifest.sha256.json'}
put(HERE/'manifest.sha256.json',{'scope':'F4 artifacts present at packaging; excludes manifest itself and Python cache',
                              'files':files,'maximum_file_bytes':max(v['bytes'] for v in files.values())})
print(json.dumps({'status':result['status'],'artifact_count':len(files),'maximum_file_bytes':max(v['bytes'] for v in files.values()),
                  'sources':[n for n in files if n.endswith('.py') and '/' not in n]}))
