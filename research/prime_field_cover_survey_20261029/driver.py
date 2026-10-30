"""Admitted complete common-atom shifted-cover survey; never collects relations."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter,process_time

from crypto_autoresearcher.index_calculus.cover_frames import ShiftedCover
from crypto_autoresearcher.index_calculus.curve import Curve
from crypto_autoresearcher.index_calculus.execution_gate import admit

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT/'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0,str(OLD))
from independent import multiply,verify_fixture

PARAMETERS = {'shift_order':'all_field_elements_ascending','base_atoms':16,'source_count':64}
_NATIVE_CAPABILITY = object()


def survey(fixtures, *, capability=None):
    if capability is not _NATIVE_CAPABILITY and not all(f.get('software_control') is True and f['p']<=211 for f in fixtures):
        raise ValueError('scientific survey requires committed protocol/release and checkpoint admission')
    cells = []
    for fixture in fixtures:
        p,a,b = (fixture[k] for k in ('p','a','b'))
        curve = Curve(p,a,b)
        sources = fixture['width_binding']['source_order']
        if len(set(sources)) != len(sources) or any(type(s) is not int or not 0<s<fixture['r'] for s in sources):
            raise ValueError('invalid fixed public source order')
        base = [tuple(v['point']) for v in fixture['factor_base']]
        if any(not curve.is_on_curve(point) for point in base):
            raise ValueError('base point is not on the fixed curve')
        source_points = [curve.mul(s,tuple(fixture['P'])) for s in sources]
        if any(point is None for point in source_points):
            raise ValueError('source infinity needs a new protocol')
        rows = []
        counters = dict(modular_pow_calls=0,base_membership_tests=0,source_membership_tests=0,
                        setup_group_ops=curve.ops.group_ops,eligible_helper_constructions=0)
        for h in range(p):
            masks = []
            for name,points in (('base',base),('source',source_points)):
                square,zero = [],[]
                for point in points:
                    delta = (point[0]-h) % p
                    symbol = pow(delta,(p-1)//2,p)
                    counters['modular_pow_calls'] += 1
                    counters[name+'_membership_tests'] += 1
                    square.append('1' if symbol in (0,1) else '0')
                    zero.append('1' if delta==0 else '0')
                masks.extend((''.join(square),''.join(zero)))
            c4,c2,c0 = 3*h % p,(3*h*h+a) % p,(h**3+a*h+b) % p
            eligible = c0 != 0 and all(bit=='1' for bit in masks[0])
            if eligible:
                frame = ShiftedCover(p,a,b,h)
                counters['eligible_helper_constructions'] += 1
                if (frame.c4,frame.c2,frame.c0) != (c4,c2,c0):
                    raise ValueError('frame helper coefficient mismatch')
            rows.append(dict(h=h,c4=c4,c2=c2,c0=c0,singular=c0==0,eligible=eligible,
                             base_square_mask=masks[0],base_zero_mask=masks[1],
                             source_square_mask=masks[2],source_zero_mask=masks[3]))
        cells.append(dict(fixture_uid=fixture['uid'],curve_uid=fixture['ec1']['curve_uid'],
                          p=p,a=a,b=b,r=fixture['r'],source_order=sources,
                          source_points=[list(point) for point in source_points],rows=rows,
                          eligible_h=[row['h'] for row in rows if row['eligible']],counters=counters))
    return dict(schema='prime-field-shifted-cover-survey/v1',complete=True,cells=cells,
                new_curve_draws=0,new_base_draws=0,new_target_draws=0,relation_collection_attempts=0,
                counter_scope='Explicit membership pow calls and setup Curve group calls only; not total field work or complete S.',
                scientific_promotion=False)


def check(fixtures,result):
    """Full roots-set reference with separate public-source arithmetic.

    The reference does not use the producer's Legendre masks, Curve.mul, or
    ShiftedCover identities. Coefficients come from polynomial composition.
    """
    if (result.get('schema')!='prime-field-shifted-cover-survey/v1' or result.get('complete') is not True or
            len(result['cells'])!=len(fixtures)):
        raise ValueError('incomplete/wrong survey identity')
    checks = []
    for fixture,cell in zip(fixtures,result['cells'],strict=True):
        verify_fixture(fixture)
        p,a,b = (fixture[k] for k in ('p','a','b'))
        sources = fixture['width_binding']['source_order']
        source_points = [multiply(p,0,a,s,tuple(fixture['P'])) for s in sources]
        if (cell['fixture_uid']!=fixture['uid'] or cell['curve_uid']!=fixture['ec1']['curve_uid'] or
                any(cell[k]!=fixture[k] for k in ('p','a','b','r')) or cell['source_order']!=sources or
                cell['source_points']!=[list(point) for point in source_points]):
            raise ValueError('fixture/source binding differs')
        roots = {x*x % p for x in range(p)}
        base = [tuple(atom['point']) for atom in fixture['factor_base']]
        if len(cell['rows'])!=p or [row['h'] for row in cell['rows']]!=list(range(p)):
            raise ValueError('incomplete/reordered shift census')
        eligible_h = []
        for row in cell['rows']:
            h = row['h']
            # Ascending coefficients of (h+X²)^3 + a(h+X²)+b,
            # formed by three independent polynomial convolutions.
            coefficients = [1]
            for _ in range(3):
                out = [0]*(len(coefficients)+2)
                for j,value in enumerate(coefficients):
                    out[j] = (out[j]+h*value) % p
                    out[j+2] = (out[j+2]+value) % p
                coefficients = out
            coefficients[0] = (coefficients[0]+a*h+b) % p
            coefficients[2] = (coefficients[2]+a) % p
            c0,c2,c4 = coefficients[0],coefficients[2],coefficients[4]
            expected = dict(h=h,c4=c4,c2=c2,c0=c0,singular=c0==0,
                base_square_mask=''.join('1' if (point[0]-h) % p in roots else '0' for point in base),
                base_zero_mask=''.join('1' if (point[0]-h) % p==0 else '0' for point in base),
                source_square_mask=''.join('1' if (point[0]-h) % p in roots else '0' for point in source_points),
                source_zero_mask=''.join('1' if (point[0]-h) % p==0 else '0' for point in source_points))
            expected['eligible'] = c0!=0 and set(expected['base_square_mask'])=={'1'}
            if row!=expected:
                raise ValueError('complete coefficient/membership row differs')
            if expected['eligible']:eligible_h.append(h)
        if cell['eligible_h']!=eligible_h:
            raise ValueError('eligible frame list differs')
        checks.append(dict(fixture_uid=fixture['uid'],frames_checked=p,
                           source_points_checked=len(sources),checked=True))
    return dict(checked=True,frames_checked=sum(c['frames_checked'] for c in checks),
                source_points_checked=sum(c['source_points_checked'] for c in checks),cells=checks,
                scope='All coefficients/membership/eligible rows and source points; counters not independently verified; not scientific review.')


def write_once(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def phase(path,name,operation):
    started = datetime.now(timezone.utc).isoformat()
    wall,cpu = perf_counter(),process_time()
    record = dict(phase=name,started_at=started,status='complete',wall_valid=False)
    try:
        return operation()
    except BaseException as error:
        record.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:
        record.update(finished_at=datetime.now(timezone.utc).isoformat(),
                      wall_seconds=perf_counter()-wall,cpu_seconds=process_time()-cpu)
        with path.open('a') as stream:stream.write(json.dumps(record,sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs','protocol','release','out'):parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    if args.out.exists():raise ValueError('fresh output directory required')
    admission = admit(ROOT,args.protocol,args.inputs,[Path(__file__),
        ROOT/'src/crypto_autoresearcher/index_calculus/cover_frames.py',
        ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',OLD/'independent.py'],PARAMETERS,args.release)
    fixtures = json.loads(args.inputs.read_text())['fixtures']
    if (len(fixtures)!=2 or any(f['p']!=4099 or len(f['factor_base'])!=16 or
            len(f['width_binding']['source_order'])!=64 for f in fixtures)):
        raise ValueError('exact two original sixteen-atom p4099 fixtures required')
    args.out.mkdir(parents=True)
    write_once(args.out/'admission.json',admission)
    result = phase(args.out/'phases.jsonl','collection',lambda:survey(fixtures,capability=_NATIVE_CAPABILITY))
    result['inputs_sha256'] = sha256(args.inputs.read_bytes()).hexdigest()
    write_once(args.out/'survey.json',result)
    verification = phase(args.out/'phases.jsonl','verification',lambda:check(fixtures,result))
    write_once(args.out/'verification.json',verification)
    print(json.dumps(dict(complete=True,frames=verification['frames_checked'])))


if __name__=='__main__':main()
