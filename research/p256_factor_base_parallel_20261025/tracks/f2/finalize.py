#!/usr/bin/env python3
"""Build derived identity, summary and SVG views from sealed exact-check receipts."""
import hashlib,importlib.util,json,math,platform,subprocess,sys
from pathlib import Path
from xml.sax.saxutils import escape
import flint
from arithmetic import *

def read(path): return json.loads(path.read_text())
def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def main():
    root=Path(__file__).resolve().parent;src=root/'receipts/validation-001'
    result=read(src/'result.json');replay=read(root/'receipts/replay-pass.json');relations=read(root/'receipts/relation-positive.json')
    assert replay['status']==relations['status']=='PASS'
    control_record=root/'receipts/direct-execution-control.json'
    if not control_record.exists():
        command=[sys.executable,str(root/'check_impl.py')]
        proc=subprocess.run(command,capture_output=True,text=True)
        write(control_record,dict(command=command,exit_code=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,
            expected='nonzero exit and no success sentinel',status='PASS' if proc.returncode and 'F2_EXACT_CHECKS_COMPLETE' not in proc.stdout else 'FAIL'))
    assert read(control_record)['status']=='PASS'
    chain=read(src/'chain.json');edges=chain['edges'];compact=read(src/'compact-full-chain.json')
    kg=tuple(compact['kernel_generator']);offset=tuple(compact['generic_offset']);endpoint=tuple(compact['generic_endpoint'])
    assert map_chain(kg,edges) is None and map_chain(offset,edges)==endpoint
    assert exact_two_power(kg,16,AUX) and endpoint[1]!=0
    compact_record=dict(status='PASS',checks=4,degree=65536,kernel_maps_to_O=True,
                        generic_point_maps_to_endpoint=True,kernel_generator_exact_order=65536,
                        endpoint_not_two_torsion=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    write(root/'compact-check.json',compact_record)
    spec=importlib.util.spec_from_file_location('repository_curve_identity',root.parents[3]/'tools/curve_identity.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    field=dict(characteristic=P,degree=1,representation='prime field Fp',element_encoding='canonical integers 0<=x<p')
    identities=[]
    for i,curve in enumerate(chain['curves']):
        a,b,c=curve
        generator=read(src/'generator.json')['generator'] if i==0 else edges[i-1]['image_generator']
        record=dict(model='general Weierstrass',a1=0,a2=a,a3=0,a4=b,a6=c,
            subgroup_order=2**(96-i),cofactor=(P+1)//2**(96-i),generator=generator,
            target_group='certified cyclic auxiliary image subgroup')
        identity=module.curve_identity(field,record,'f2a'+str(i));record['curve_id']=identity['curve_id']
        identities.append(dict(index=i,field=field,curve=record,identity=identity))
    gx=int('6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296',16)
    gy=int('4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5',16)
    assert on_curve((gx,gy),TARGET) and mul(TARGET_R,(gx,gy),TARGET) is None
    targetrecord=dict(model='short Weierstrass',a=-3%P,b=TARGET_B,subgroup_order=TARGET_R,
        cofactor=1,generator=[gx,gy],target_group='published P-256 prime-order target group')
    targetid=module.curve_identity(field,targetrecord,'p256');targetrecord['curve_id']=targetid['curve_id']
    write(root/'identities.json',dict(auxiliary=identities,target=dict(field=field,curve=targetrecord,identity=targetid),
          identity_implementation=str(root.parents[3]/'tools/curve_identity.py'),
          identity_implementation_sha256=hashlib.sha256((root.parents[3]/'tools/curve_identity.py').read_bytes()).hexdigest(),
          note='EC1 identities include chosen subgroup/generator/model metadata; metadata equality is not an arithmetic proof.'))
    result['independent_arithmetic_replay']=dict(status='PASS',checks=replay['checks'],accepted_lifts=replay['accepted_lifts'],independent_session=False,
        receipt='receipts/replay-pass.json')
    result['constructed_relation_controls']=dict(status='PASS',checks=relations['checks'],cases=relations['cases'],d=3,
        receipt='receipts/relation-positive.json',scope=relations['scope'])
    result['compact_certificate_checks']=compact_record
    result['input_bindings']=read(root/'input-bindings.json')
    result['total_assertions']=result['checks']+replay['checks']+relations['checks']+4+1+result['input_bindings']['checks']
    result['expected_failure_controls']=[dict(name='unexpected exception',receipt='receipts/control-exception/receipt.json',expected_exit=1),
        dict(name='missing completion sentinel',receipt='receipts/control-early-return/receipt.json',expected_exit=1),
        dict(name='mutated target y',receipt='receipts/replay-corrupt-target.json',expected_exit=1),
        dict(name='direct body execution',receipt='receipts/direct-execution-control.json',expected_exit=1)]
    result['gcd_target_order_auxiliary_order']=math.gcd(P+1,TARGET_R)
    result['target_trace']=P+1-TARGET_R
    result['backend_versions']=dict(python_flint=flint.__version__,FLINT=flint.__FLINT_VERSION__)
    result['claim_tier']='implementation_validation_and_derived_mathematics'
    result['existing_obstruction']='../../../../problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md'
    result['artifact_index']=dict(report='report.md',derivation='derivation.md',diagram='diagram.svg',quantitative_graph='incidence.svg',
        chain='receipts/validation-001/chain.json',comparison='receipts/validation-001/comparison.json',identities='identities.json')
    write(root/'result.json',result)
    # Editable SVG includes full EC1 UID text, plus exact records in identities.json.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="820" viewBox="0 0 1200 820">',
       '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#38556b"/></marker></defs>',
       '<rect width="1200" height="820" fill="#fff"/>',
       '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#173042} .title{font-size:25px;font-weight:700}.body{font-size:17px}.uid{font-family:monospace;font-size:11px}.small{font-size:14px}</style>',
       '<text x="40" y="40" class="title">F2: certified auxiliary chain and fixed-target coordinate lifts</text>',
       '<text x="40" y="70" class="small">TASK-20261025-929e0f · exact implementation checks · no performance trial</text>']
    for idx,i in enumerate([0,6,12,16]):
        xx=35+idx*295;uid=identities[i]['identity']['curve_uid'];hexdigest=uid.rsplit(':',1)[1]
        svg.extend([f'<rect x="{xx}" y="110" width="275" height="170" rx="10" fill="#edf6fa" stroke="#38556b"/>',
            f'<text x="{xx+10}" y="140" class="body">A{i}: y²=x³+a₂x²+a₄x</text>',
            f'<text x="{xx+10}" y="166" class="small">Fp · |H{i}|=2^{96-i} · #A{i}=p+1</text>',
            f'<text x="{xx+10}" y="191" class="uid">urn:ec-record:1:sha256:</text>',
            f'<text x="{xx+10}" y="207" class="uid">{hexdigest[:32]}</text>',
            f'<text x="{xx+10}" y="223" class="uid">{hexdigest[32:]}</text>',
            f'<text x="{xx+10}" y="250" class="small">Exact a₂,a₄: identities.json[{i}]</text>'])
        if idx<3:
            svg.append(f'<path d="M{xx+275},190 L{xx+293},190" stroke="#38556b" stroke-width="2" marker-end="url(#arrow)"/>')
    svg.extend(['<text x="40" y="314" class="small">Edges: 16 × degree 2, separable over Fp; direction unresolved; no ordinary-volcano label.</text>',
       '<text x="40" y="342" class="body">Kernel base: x(K \\ {O})  ·  Generic base: x(P+K)  ·  Complete finite-fibre certificates</text>',
       '<path d="M600,360 L600,408" stroke="#38556b" stroke-width="2" marker-end="url(#arrow)"/>',
       '<rect x="170" y="420" width="860" height="124" rx="10" fill="#fff7e9" stroke="#b77b2a"/>',
       '<text x="190" y="450" class="body">Reinterpret x on fixed P-256: v²=x³−3x+b₂₅₆</text>',
       '<text x="190" y="480" class="body">Reject nonsquares; verify [r](x,v)=O; retain canonical sign.</text>',
       '<text x="190" y="510" class="body">This arrow is a coordinate selection rule, with no group-homomorphism claim.</text>',
       f'<text x="190" y="532" class="uid">{targetid["curve_uid"]}</text>',
       '<text x="40" y="585" class="body">12 complete enumerated domains · 16,320 x rows · 8,279 accepted lifts</text>',
       '<text x="40" y="617" class="body">Matched final M=26,121,515,2066 at d=3; kernel/generic/Dickson controls.</text>',
       '<text x="40" y="650" class="body">16-edge fibre: compact certificate of 65,536 distinct rational x values.</text>',
       '<text x="40" y="683" class="body">Target subgroup and auxiliary order are coprime; traces differ.</text>',
       '<text x="40" y="726" class="small">Evidence: receipts/validation-001/, receipts/replay-pass.json; exact identities: identities.json.</text>',
       '<text x="40" y="751" class="small">Remaining obligation: complete relation solver with denominators, root solving and rejection charged.</text>',
       '<text x="40" y="785" class="small">Degree/pole/branch checks through 4096; full-degree target lift enumeration not run.</text>','</svg>'])
    (root/'diagram.svg').write_text('\n'.join(svg)+'\n')
    # Quantitative plot of full enumerated populations, not fitted probabilities.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560">',
       '<rect width="1000" height="560" fill="white"/>',
       '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#173042;font-size:16px}</style>',
       '<text x="40" y="35" font-size="22">Exact target incidence in complete structured x domains</text>',
       '<text x="40" y="64">Bar height: accepted fraction; labels: exact accepted counts. All accepted points satisfy [r]P=O.</text>']
    families=[('elliptic_generic','#267caa'),('elliptic_kernel','#68a96b'),('Dickson_generic','#d29340')]
    for tick in [0,0.25,0.5,0.6]:
        yy=370-400*tick
        svg.extend([f'<line x1="70" y1="{yy}" x2="970" y2="{yy}" stroke="#dde5ea"/>',f'<text x="58" y="{yy+5}" text-anchor="end" font-size="13">{tick:.0%}</text>'])
    for i,s in enumerate(result['summaries']):
        xx=90+i*230
        for j,(family,color) in enumerate(families):
            count=s['counts'][family];ratio=count/s['raw_M'];yy=370-400*ratio
            svg.extend([f'<rect x="{xx+j*48}" y="{yy:.2f}" width="35" height="{400*ratio:.2f}" fill="{color}"/>',
                f'<text x="{xx+j*48+17}" y="{yy-10:.2f}" text-anchor="middle" font-size="13">{count}</text>'])
        svg.append(f'<text x="{xx+60}" y="400" text-anchor="middle">raw M={s["raw_M"]}</text>')
        svg.append(f'<text x="{xx+60}" y="426" text-anchor="middle">matched M={s["matched_final_M"]}</text>')
    for j,(family,color) in enumerate(families):
        xx=50+j*310
        svg.extend([f'<rect x="{xx}" y="458" width="18" height="18" fill="{color}"/>',f'<text x="{xx+27}" y="474">{family}</text>'])
    svg.extend(['<text x="40" y="515">Source: validation-001; 12 complete cases, 16,320 rows. No sampling uncertainty for these exact sets.</text>',
                '<text x="40" y="540">No general acceptance probability, relation yield or performance inference is made.</text>','</svg>'])
    (root/'incidence.svg').write_text('\n'.join(svg)+'\n')
    print(json.dumps(dict(status='PASS',total_assertions=result['total_assertions'],accepted_lifts=replay['accepted_lifts'])))
if __name__=='__main__':main()
