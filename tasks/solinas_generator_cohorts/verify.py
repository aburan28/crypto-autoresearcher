"""Independent integer arithmetic checks and full raw-file integrity validation."""
import hashlib
import json
from pathlib import Path

from metrics import features
from native import seed_for
from research import canonical, check_source, digest, immutable, jobs


def add(curve, left, right):
    if left is None: return right
    if right is None: return left
    p,a=curve['p'],curve['A']
    x,y=left; u,v=right
    if x==u and (y+v)%p==0: return None
    slope=((3*x*x+a)*pow(2*y,-1,p) if left==right else (v-y)*pow(u-x,-1,p))%p
    rx=(slope*slope-x-u)%p
    return (rx,(slope*(x-rx)-y)%p)


def multiply(curve, point, scalar):
    result=None
    while scalar:
        if scalar&1: result=add(curve,result,point)
        point=add(curve,point,point); scalar>>=1
    return result


def scalar_draw(seed, limit, counter=0):
    bits=limit.bit_length(); width=(bits+7)//8
    while True:
        block=bytearray(hashlib.sha256(seed+counter.to_bytes(8,'big')).digest()[:width]); counter+=1
        block[0]&=0xff>>(8*width-bits)
        scalar=int.from_bytes(block,'big')
        if 0<scalar<limit: return scalar,counter


def points(raw,p):
    width=(p.bit_length()+7)//8
    return [(int.from_bytes(raw[i:i+width],'big'),int.from_bytes(raw[i+width:i+2*width],'big'))
            for i in range(0,len(raw),2*width)]


def verify(output):
    output=Path(output).resolve()
    design=check_source(output);config=design['config']
    inputs=json.loads((output/'inputs.json').read_text())
    queue=jobs(inputs,config)
    expected={j['id']+'.json' for j in queue}
    if {p.name for p in (output/'records').glob('*.json')}!=expected:
        raise ValueError('Missing or extra records')
    model_checks=0;walk_checks=0;scalar_checks=0;transport_checks=0;raw_bytes=0
    for index,job in enumerate(queue):
        record=json.loads((output/'records'/(job['id']+'.json')).read_text())
        if record['job']!=job or record['design_sha256']!=hashlib.sha256(canonical(design)).hexdigest():
            raise ValueError('Record provenance differs from frozen plan')
        path=output/record['raw']['path'];raw=path.read_bytes();raw_bytes+=len(raw)
        p,a,b=job['curve']['p'],job['curve']['A'],job['curve']['B']
        width=(p.bit_length()+7)//8
        if len(raw)!=job['points']*2*width or len(raw)!=record['raw']['bytes'] or digest(path)!=record['raw']['sha256']:
            raise ValueError('Raw identity, dimensions, or checksum differs')
        coords=points(raw,p)
        for x,y in coords:
            if not (0<=x<p and 0<=y<p) or (y*y-x*x*x-a*x-b)%p:
                raise ValueError('Invalid raw point')
        model_checks+=len(coords)
        measured,_=features(raw,p,config['bins'])
        if measured!=record['features']:
            raise ValueError('Summary differs from independent full raw replay')
        if job['mode']=='walk':
            h=tuple(record['generator'])
            # Spread checks include beginning/end and 14 interior transitions.
            positions=sorted({i*(len(coords)-2)//15 for i in range(16)})
            for position in positions:
                if add(job['curve'],coords[position],h)!=coords[position+1]:
                    raise ValueError('Consecutive point recurrence differs')
                walk_checks+=1
        if job['mode'] in ('walk','iid') and job['block']<config['diagnostic_blocks']:
            seed=bytes.fromhex(record['point_seed_hex'])
            k,counter=scalar_draw(seed,job['curve']['N'])
            if multiply(job['curve'],tuple(record['generator']),k)!=coords[0]:
                raise ValueError('Independent start/scalar multiplication differs')
            scalar_checks+=1
            if record['generator_seed_hex']:
                r,_=scalar_draw(bytes.fromhex(record['generator_seed_hex']),job['curve']['N'])
                if multiply(job['curve'],tuple(job['published_G']),r)!=tuple(record['generator']):
                    raise ValueError('Independent random generator derivation differs')
                scalar_checks+=1
            if job['mode']=='iid':
                for position in range(1,4):
                    k,counter=scalar_draw(seed,job['curve']['N'],counter)
                    if multiply(job['curve'],tuple(record['generator']),k)!=coords[position]:
                        raise ValueError('Independent iid scalar multiplication differs')
                    scalar_checks+=1
        if record['diagnostics']:
            transformed=record['diagnostics']['isomorphic_u2_curve']
            for x,y in coords:
                tx,ty=4*x%p,8*y%p
                if (ty*ty-tx*tx*tx-transformed['A']*tx-transformed['B'])%p:
                    raise ValueError('Isomorphic point transport failed')
                transport_checks+=1
            if record['diagnostics']['sorted_positive_x_lag1']<.99:
                raise ValueError('Deliberately correlated positive control was missed')
        if (index+1)%512==0:
            print(json.dumps({'verified_records':index+1,'total':len(queue),'valid_points':model_checks}),flush=True)
    receipt=json.loads((output/'receipt.json').read_text())
    if receipt['jobs']!=len(queue) or receipt['points']!=model_checks or receipt['raw_bytes']!=raw_bytes:
        raise ValueError('Receipt does not match raw dataset')
    result={'status':'passed','records':len(queue),'all_points_on_curve':model_checks,
            'independent_walk_transition_checks':walk_checks,'independent_scalar_multiplications':scalar_checks,
            'isomorphic_point_checks':transport_checks,'all_raw_sha256_verified':True,
            'all_features_recomputed':True,'raw_bytes':raw_bytes,
            'independence_note':'OpenSSL arithmetic checked by separate Python affine arithmetic. Same-session verification, not an independent reviewer.'}
    immutable(output/'verification.json',canonical(result));print(json.dumps(result),flush=True)


if __name__=='__main__':
    import sys
    verify(sys.argv[1])
