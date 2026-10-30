"""Candidate-only source. No solver/reference import; execution requires later admission."""
from __future__ import annotations
import hashlib
import json
import math
import re
from itertools import combinations, product
from pathlib import Path
from constructor import prepare, normalized_miller_coefficient, result
from curve import Counter, Curve, point_json, point_from_json
SCHEMA = "classical.ecdlp.controlled-followup"
MULTIPLIERS=(1,2,3,5)
CIRCUITS=((1,-4),(-2,-1))

def arm_specs():
    return [{"id":f"circuit{n}.a{a}","kind":"candidate","alpha":alpha,"beta":beta,"base_multiplier":a}
            for n,(alpha,beta) in enumerate(CIRCUITS,1) for a in MULTIPLIERS]

def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",",":"),allow_nan=False)+"\n").encode()

def write_json(path,value):
    with Path(path).open("xb") as f: f.write(canonical_json(value))

def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def add_counts(destination, source):
    for name, value in source.items():
        destination.tick(name, value)


def sum_counts(records):
    total = Counter()
    for record in records:
        add_counts(total, record)
    return total.snapshot()


def uniform_below(nonce_hex, role, draw_id, bound, counter=None):
    """Unbiased reduction of domain-separated SHA-256 public PRG draws."""
    if type(bound) is not int or not 1 <= bound <= (1 << 256):
        raise ValueError("positive at-most-256-bit sampling bound required")
    if not re.fullmatch(r"[0-9a-f]{64}", nonce_hex):
        raise ValueError("256-bit public cohort nonce required")
    prefix = bytes.fromhex(nonce_hex) + b"\x00transfer-study/v1/" + role.encode() + b"\x00" + draw_id.encode()
    threshold = ((1 << 256) // bound) * bound
    rejection_counter = 0
    while True:
        digest = hashlib.sha256(prefix + rejection_counter.to_bytes(8, "big")).digest()
        if counter is not None:
            counter.tick("rng_hash256_call")
        value = int.from_bytes(digest, "big")
        if value < threshold:
            sampled = value % bound
            if counter is not None:
                counter.tick("rng_modular_reduction")
            return sampled, {"role": role, "draw_id": draw_id, "bound": bound,
                             "rejection_counter": rejection_counter,
                             "digest_hex": digest.hex(), "value": sampled}
        if counter is not None:
            counter.tick("rng_rejected_digest")
        rejection_counter += 1


def scalar_inverse(value, modulus, counter):
    counter.tick("order_inverse_call")
    counter.tick("order_reduce")
    old_r, rem, old_t, coeff = modulus, value % modulus, 0, 1
    while rem:
        counter.tick("order_euclid_iteration")
        quotient = old_r // rem
        old_r, rem = rem, old_r - quotient * rem
        old_t, coeff = coeff, old_t - quotient * coeff
    if old_r != 1:
        raise ValueError("known target multiplier is not invertible")
    counter.tick("order_reduce")
    return old_t % modulus


def ungated_attempt(prepared, original_base, original_target, base_multiplier,
                     target_multiplier, include_query_counters=False):
    """Fixed L fresh calls; no all-target gate or scalar label is consulted."""
    model, r = prepared.model, prepared.model["r"]
    blinding = Curve(model["p"], model["a"], model["b"])
    if not blinding.contains(original_target) or original_target is None:
        raise ValueError("primary target must be a nonidentity public point")
    transformed_target = blinding.multiply(original_target, target_multiplier)
    curve = Curve(model["p"], model["a"], model["b"])
    length = r.bit_length() + 1
    value, current, fully_defined = 0, transformed_target, True
    evaluate, trace, reasons = Counter(), [], []
    for index in range(length):
        answer, counts = prepared.evaluate(current)
        add_counts(evaluate, counts)
        entry = {"index": index, "target": point_json(current), "answer": answer}
        if include_query_counters:
            entry["counters"] = counts
        trace.append(entry)
        curve.counter.tick("recovery_scalar_digit_update")
        if answer["status"] != "BIT":
            fully_defined = False
            reasons.append(answer["reason"])
        value = 2 * value + (answer["bit"] if answer["status"] == "BIT" else 0)
        if index + 1 < length:
            current = curve.add(current, current)
    denominator = 1 << length
    curve.counter.tick("recovery_scalar_interval_round")
    lower = r * value
    upper = r * (value + 1)
    candidate_prime = (lower + denominator - 1) // denominator if fully_defined else None
    nonempty = bool(fully_defined and candidate_prime < r and denominator * candidate_prime < upper)
    conversion = Counter()
    inverse_b = scalar_inverse(target_multiplier, r, conversion)
    candidate = None
    transformed_check = original_check = None
    if nonempty:
        conversion.tick("order_mul", 2)
        conversion.tick("order_reduce", 2)
        candidate = (base_multiplier * inverse_b % r) * candidate_prime % r
        transformed_check = curve.equal(curve.multiply(prepared.base, candidate_prime), transformed_target)
        original_check = curve.equal(curve.multiply(original_base, candidate), original_target)
    recovered = bool(nonempty and transformed_check and original_check)
    status = "RECOVERED" if recovered else "UNDEFINED" if not fully_defined else "EMPTY_INTERVAL" if not nonempty else "REJECTED_FINAL_VERIFICATION"
    reason = None if recovered else ",".join(sorted(set(reasons))) if not fully_defined else "EMPTY_BINARY_INTERVAL" if not nonempty else "FINAL_VERIFICATION_FAILED"
    return transformed_target, {
        "status": status, "reason": reason, "L": length,
        "candidate_scalar_prime": candidate_prime, "candidate_scalar": candidate,
        "scalar_prime": candidate_prime if recovered else None,
        "scalar": candidate if recovered else None,
        "target_multiplier_inverse": inverse_b,
        "interval": {"value": value if fully_defined else None, "denominator": denominator,
                     "lower_numerator": lower if fully_defined else None,
                     "upper_numerator": upper if fully_defined else None, "nonempty": nonempty},
        "predicate_evaluations": length, "retained_bit_reads": 0, "predicate_trace": trace,
        "counts": {"blinding": blinding.counter.snapshot(), "evaluate": evaluate.snapshot(),
                   "reduction": curve.counter.snapshot(), "conversion": conversion.snapshot()},
        "public_checks": {"transformed": transformed_check, "original": original_check}}


def _next_z(field, value: int, slope: int) -> int:
    field.counter.tick("incremental_z_update")
    return field.add(field.mul(2, value), slope)


def _answer_from_z(prepared, target, z, curve):
    """Internal circuit body, after the same membership/identity boundary."""
    x, y = target
    alpha, beta = prepared.arm["alpha"], prepared.arm["beta"]
    offset = curve.f.mul(prepared.c, curve.f.sub(x, prepared.base[0]))
    bracket = curve.f.add(alpha, curve.f.mul(beta, offset))
    numerator = curve.f.add(z, curve.f.mul(curve.f.mul(prepared.c, y), bracket))
    if curve.f.equal(numerator, 0):
        curve.counter.tick("exception_zero_numerator")
        return result("UNDEFINED", reason="ZERO_NUMERATOR", z=z, g=numerator,
                      anchor=prepared.anchor)
    normalized = curve.f.mul(numerator, prepared.inverse_anchor)
    character = curve.f.power(normalized, (curve.p - 1) // 2)
    if character not in (1, curve.p - 1):
        raise ValueError("non-Legendre character in declared prime field")
    return result("BIT", bit=0 if character == 1 else 1, z=z, g=numerator,
                  anchor=prepared.anchor, normalized=normalized)


def incremental_ungated_attempt(prepared, original_base, original_target,
                                base_multiplier, target_multiplier,
                                include_query_counters=False):
    """Same public inputs and non-counter outputs as compute.ungated_attempt.

    Primitive state is local to one attempt. A ready candidate initializes it
    using the original subgroup-checking Miller chain. Slope reuse occurs only
    at the doubling already required by the reduction. Undefined numerator
    calls never stop the fixed-length sequence. Undefined setups and wrong-root
    controls retain their original evaluator and require no primitive cache.
    """
    model, r = prepared.model, prepared.model["r"]
    blinding = Curve(model["p"], model["a"], model["b"])
    if not blinding.contains(original_target) or original_target is None:
        raise ValueError("primary target must be a nonidentity public point")
    transformed_target = blinding.multiply(original_target, target_multiplier)
    curve = Curve(model["p"], model["a"], model["b"])
    transitions = Curve(model["p"], model["a"], model["b"])
    length = r.bit_length() + 1
    value, current, fully_defined = 0, transformed_target, True
    evaluate, trace, reasons = Counter(), [], []
    use_z = not prepared.setup_reason and prepared.arm["kind"] != "wrong_root"
    z, z_initialized = None, False
    for index in range(length):
        if not use_z:
            answer, counts = prepared.evaluate(current)
        else:
            query = Curve(model["p"], model["a"], model["b"])
            if not query.contains(current):
                raise ValueError("target is not a canonical point on curve")
            if current is None:
                query.counter.tick("exception_identity_predicate")
                z, z_initialized = 0, True
                answer = result("BIT", bit=0, z=0, anchor=prepared.anchor)
            else:
                if not z_initialized:
                    z = normalized_miller_coefficient(query, current, r, prepared.inverse_r)
                    z_initialized = True
                answer = _answer_from_z(prepared, current, z, query)
            counts = query.counter.snapshot()
        add_counts(evaluate, counts)
        entry = {"index": index, "target": point_json(current), "answer": answer}
        if include_query_counters:
            entry["counters"] = counts
        trace.append(entry)
        curve.counter.tick("recovery_scalar_digit_update")
        if answer["status"] != "BIT":
            fully_defined = False
            reasons.append(answer["reason"])
        value = 2 * value + (answer["bit"] if answer["status"] == "BIT" else 0)
        if index + 1 < length:
            current, slope = curve.add_with_slope(current, current)
            if use_z and z_initialized:
                z = _next_z(transitions.f, z, slope)
    denominator = 1 << length
    curve.counter.tick("recovery_scalar_interval_round")
    lower = r * value
    upper = r * (value + 1)
    candidate_prime = (lower + denominator - 1) // denominator if fully_defined else None
    nonempty = bool(fully_defined and candidate_prime < r and denominator * candidate_prime < upper)
    conversion = Counter()
    inverse_b = scalar_inverse(target_multiplier, r, conversion)
    candidate = None
    transformed_check = original_check = None
    if nonempty:
        conversion.tick("order_mul", 2)
        conversion.tick("order_reduce", 2)
        candidate = (base_multiplier * inverse_b % r) * candidate_prime % r
        transformed_check = curve.equal(curve.multiply(prepared.base, candidate_prime), transformed_target)
        original_check = curve.equal(curve.multiply(original_base, candidate), original_target)
    recovered = bool(nonempty and transformed_check and original_check)
    status = "RECOVERED" if recovered else "UNDEFINED" if not fully_defined else "EMPTY_INTERVAL" if not nonempty else "REJECTED_FINAL_VERIFICATION"
    reason = None if recovered else ",".join(sorted(set(reasons))) if not fully_defined else "EMPTY_BINARY_INTERVAL" if not nonempty else "FINAL_VERIFICATION_FAILED"
    return transformed_target, {
        "status": status, "reason": reason, "L": length,
        "candidate_scalar_prime": candidate_prime, "candidate_scalar": candidate,
        "scalar_prime": candidate_prime if recovered else None,
        "scalar": candidate if recovered else None,
        "target_multiplier_inverse": inverse_b,
        "interval": {"value": value if fully_defined else None, "denominator": denominator,
                     "lower_numerator": lower if fully_defined else None,
                     "upper_numerator": upper if fully_defined else None, "nonempty": nonempty},
        "predicate_evaluations": length, "retained_bit_reads": 0, "predicate_trace": trace,
        "counts": {"blinding": blinding.counter.snapshot(), "evaluate": evaluate.snapshot(),
                   "state_updates": transitions.counter.snapshot(),
                   "reduction": curve.counter.snapshot(), "conversion": conversion.snapshot()},
        "public_checks": {"transformed": transformed_check, "original": original_check}}

CELL_SPECS = [(t,e) for t in (0,1,2) for e in (0,2)]

def witness(value):
    if isinstance(value,dict):
        return {k:witness(v) for k,v in value.items() if k not in ('counts','counters')}
    if isinstance(value,(list,tuple)):
        return [witness(v) for v in value]
    return value


def enumerate_words(bits, radius):
    """Erasures lexicographic, then flip weight, then index combinations; MSB first."""
    erased = [i for i,b in enumerate(bits) if b is None]
    defined = [i for i,b in enumerate(bits) if b is not None]
    for assignment in product((0,1), repeat=len(erased)):
        for weight in range(min(radius,len(defined))+1):
            for flipped in combinations(defined,weight):
                word = list(bits)
                for i,b in zip(erased,assignment): word[i]=b
                for i in flipped: word[i]^=1
                value=0
                for b in word: value=2*value+b
                yield {'value':value,'bits':word,'erasure_assignment':list(assignment),
                       'flipped_indices':list(flipped)}


def decode_cell(prepared, base, target, a, b, attempt, radius, erasure_cap):
    if radius not in (0,1,2) or erasure_cap not in (0,2):
        raise ValueError('unfrozen decoder cell')
    r=prepared.model['r']; L=attempt['L']; D=1<<L
    bits=[q['answer']['bit'] if q['answer']['status']=='BIT' else None
          for q in attempt['predicate_trace']]
    if len(bits)!=L: raise ValueError('incomplete predicate trace')
    e=bits.count(None); capped=e>erasure_cap
    expected=0 if capped else (1<<e)*sum(math.comb(L-e,j) for j in range(min(radius,L-e)+1))
    wrapper=Counter(); conversion=Counter(); checks=Curve(prepared.model['p'],prepared.model['a'],prepared.model['b'])
    wrapper.tick('decoder_cap_test'); inverse_b=scalar_inverse(b,r,conversion)
    words=[]; candidates=set(); recoveries=[]; zero=0
    transformed=point_from_json(attempt['predicate_trace'][0]['target'])
    if not capped:
        for enumeration in enumerate_words(bits,radius):
            V=enumeration['value']; k=(r*V+D-1)//D
            wrapper.tick('decoder_word_construct'); wrapper.tick('integer_word_bit',L)
            wrapper.tick('integer_interval_round'); wrapper.tick('integer_mul',3)
            wrapper.tick('integer_add',3); wrapper.tick('integer_divide'); wrapper.tick('integer_compare',3)
            legal=0<=k<r and D*k<r*(V+1)
            x=None; transformed_check=None; original_check=None
            if legal:
                conversion.tick('order_mul',2); conversion.tick('order_reduce',2)
                x=(a*inverse_b%r)*k%r
                wrapper.tick('public_candidate_check'); wrapper.tick('candidate_set_lookup')
                # Both equations run unconditionally, including zero and known failures.
                transformed_check=checks.equal(checks.multiply(prepared.base,k),transformed)
                original_check=checks.equal(checks.multiply(base,x),target)
                if x: candidates.add(x)
                else: zero+=1
                if transformed_check and original_check: recoveries.append(x)
            words.append({**enumeration,'candidate_scalar_prime':k,'legal':legal,
                          'candidate_scalar':x,'public_checks':{'transformed':transformed_check,'original':original_check},
                          'status':'RECOVERED' if transformed_check and original_check else 'REJECTED_FINAL_VERIFICATION' if legal else 'EMPTY_INTERVAL'})
    if len(words)!=expected: raise AssertionError('enumeration count mismatch')
    status=('CAPPED_ERASURES' if capped else 'RECOVERED' if recoveries else
            'EMPTY_INTERVAL' if words and all(w['status']=='EMPTY_INTERVAL' for w in words) else 'REJECTED_FINAL_VERIFICATION')
    # Exact original status at t0.e0, while retaining explicit cap metadata.
    if radius==0 and erasure_cap==0: status=attempt['status']
    return {'radius':radius,'erasure_cap':erasure_cap,'L':L,'erasures':e,'capped':capped,
            'status':status,'expected_word_count':expected,'word_count':len(words),'words':words,
            'M':len(candidates),'distinct_nonzero_candidates':sorted(candidates),
            'zero_candidate_checks':zero,'recovered_scalars':sorted(set(recoveries)),
            'scalar':recoveries[0] if recoveries else None,
            'counts':{'wrapper':wrapper.snapshot(),'conversion':conversion.snapshot(),'verification':checks.counter.snapshot()},
            'memory':{'retained_word_records':len(words),'retained_word_bits':L*len(words),
                      'distinct_nonzero_scalars':len(candidates),'metric':'abstract_payload_not_RSS'}}


def paired_attempt(prepared, original_base, original_target, base_multiplier, target_multiplier):
    r=prepared.model['r']
    if not (1<=base_multiplier<r and 1<=target_multiplier<r):
        raise ValueError('nonzero canonical multipliers required')
    _,original=ungated_attempt(prepared,original_base,original_target,base_multiplier,target_multiplier,True)
    _,incremental=incremental_ungated_attempt(prepared,original_base,original_target,base_multiplier,target_multiplier,True)
    if witness(original)!=witness(incremental): raise AssertionError('original/incremental trace mismatch')
    cells=[decode_cell(prepared,original_base,original_target,base_multiplier,target_multiplier,incremental,t,e) for t,e in CELL_SPECS]
    if cells[0]['status']!=original['status'] or cells[0]['scalar']!=original['scalar']:
        raise AssertionError('original t0.e0 mismatch')
    return {'original':original,'incremental':incremental,'cells':cells,'equal':True}


def sample_coordinate(model, nonce, role, draw_id, proposal_limit):
    """Public coordinate rejection/root/sign sampler; no scalar-labelled generation."""
    if type(proposal_limit) is not int or proposal_limit<1: raise ValueError('frozen positive proposal limit required')
    curve=Curve(model['p'],model['a'],model['b']); records=[]
    if curve.p%4!=3: raise ValueError('root sampler requires p=3 mod4')
    for proposal in range(proposal_limit):
        x,xd=uniform_below(nonce,role,f'{draw_id}/{proposal}/x',curve.p,curve.counter)
        sign,sd=uniform_below(nonce,role,f'{draw_id}/{proposal}/sign',2,curve.counter)
        rhs=curve.f.add(curve.f.add(curve.f.mul(curve.f.square(x),x),curve.f.mul(curve.a,x)),curve.b)
        y=curve.f.power(rhs,(curve.p+1)//4)
        square=curve.f.equal(curve.f.square(y),rhs)
        # Reject y=0 so each eligible nonidentity point has equal proposal mass.
        accepted=square and y!=0
        point=(x,y if sign==0 else curve.f.neg(y))
        if accepted: accepted=curve.multiply(point,model['r']) is None
        records.append({'proposal':proposal,'x_draw':xd,'sign_draw':sd,'status':'ACCEPTED' if accepted else 'REJECTED'})
        curve.counter.tick('coordinate_proposal')
        if accepted: return point,{'status':'ACCEPTED','proposals':records,'counts':curve.counter.snapshot()}
    return None,{'status':'CAPPED_PROPOSALS','proposals':records,'counts':curve.counter.snapshot()}


def record(kind, **fields):
    return {'schema':f'{SCHEMA}.{kind}/v1',**fields}


def fixture_records():
    """Only existing disclosed F11 software fixture; no cohort draws or entropy."""
    model={'p':11,'a':1,'b':6,'r':13}; base=(2,7); target=(7,2)
    arm=arm_specs()[3]  # Existing disclosed circuit1.a5 witness.
    common=Curve(11,1,6); prepared=prepare(model,common.multiply(base,5),arm)
    pair=paired_attempt(prepared,base,target,5,1)
    tid='fixture-F11/target7/rep0'; prov={'protocol_sha256':'0'*64,'source_fingerprint':'0'*64,'cohort_sha256':'0'*64}
    return {
        'setup':record('setup',curve_id='fixture-F11',arm_id=arm['id'],model=model,base=list(base),prepared_base=list(prepared.base),arm=arm,setup_reason=prepared.setup_reason,counts={'common':common.counter.snapshot(),'setup':prepared.setup_counts}),
        'intent':record('intent',trace_id=tid,curve_id='fixture-F11',target_id='target7',arm_id=arm['id'],target=list(target),base_multiplier=5,target_multiplier=1,draw=None),
        'single-point':record('single-point',single_id='fixture-F11/single0000/'+arm['id'],curve_id='fixture-F11',arm_id=arm['id'],point=list(target),sampling=None,answer=prepared.evaluate(target)[0],counts=prepared.evaluate(target)[1]),
        'trace':record('trace',trace_id=tid,curve_id='fixture-F11',target_id='target7',arm_id=arm['id'],target=list(target),base_multiplier=5,target_multiplier=1,draw=None,original=pair['original'],incremental=pair['incremental'],equal=pair['equal']),
        'decoder-cell':record('decoder-cell',cell_id=tid+'/t1.e2',trace_id=tid,**pair['cells'][3]),
        'summary':record('summary',status='complete',expected={'setups':1,'intents':1,'singles':1,'traces':1,'cells':6},observed={'setups':1,'intents':1,'singles':1,'traces':1,'cells':6},errors=[],wall_valid=False,provenance=prov),
        'completion':record('completion',status='complete',files={},wall_valid=False,termination_ack=False,provenance=prov)}


def run_public(plan, public, outdir, provenance):
    """Candidate worker only. Future caller owns admission, broker and termination.

    public.curves contains public model/base/targets only. plan.jobs supplies
    immutable, predeclared single or trace slots and optional public sampler draws.
    No scientific execution is authorized by this source function.
    """
    allowed={'curves','nonce'}
    if set(public)!=allowed: raise ValueError('public input keys must be curves,nonce only')
    if set(provenance)!={'protocol_sha256','source_fingerprint','cohort_sha256'}:
        raise ValueError('exact source/protocol/cohort bindings required')
    for v in provenance.values():
        if not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v): raise ValueError('invalid provenance digest')
    if set(plan)!={'jobs','expected'}: raise ValueError('plan keys must be jobs,expected')
    curves={}
    for c in public['curves']:
        if set(c)!={'curve_id','model','base','targets'}: raise ValueError('extra public curve fields')
        if set(c['model'])!={'p','a','b','r'}: raise ValueError('extra model fields')
        if any(set(t)!={'target_id','point'} for t in c['targets']): raise ValueError('extra target fields')
        if c['curve_id'] in curves: raise ValueError('duplicate curve id')
        curves[c['curve_id']]=c
    out=Path(outdir);out.mkdir(parents=True,exist_ok=False)
    paths={'setups':'setups.jsonl','intents':'attempt-intents.jsonl','singles':'single-points.jsonl','traces':'traces.jsonl','cells':'decoder-cells.jsonl'}
    observed={k:0 for k in paths};errors=[];cache={}
    handles={k:(out/v).open('xb') for k,v in paths.items()}
    def emit(k,v):
        handles[k].write(canonical_json(v));handles[k].flush();observed[k]+=1
    try:
        seen=set()
        for job in plan['jobs']:
            if set(job)!={'kind','id','curve_id','target_id','arm_id','point_index','replicate','proposal_limit'}:
                raise ValueError('unfrozen job keys')
            if job['id'] in seen: raise ValueError('duplicate job id')
            seen.add(job['id']);c=curves[job['curve_id']];model=c['model'];base=point_from_json(c['base'])
            arm=next(a for a in arm_specs() if a['id']==job['arm_id']);a=arm['base_multiplier']
            key=(c['curve_id'],arm['id'])
            if key not in cache:
                common=Curve(model['p'],model['a'],model['b']);prepared=prepare(model,common.multiply(base,a),arm);cache[key]=prepared
                emit('setups',record('setup',curve_id=c['curve_id'],arm_id=arm['id'],model=model,base=c['base'],prepared_base=point_json(prepared.base),arm=arm,setup_reason=prepared.setup_reason,counts={'common':common.counter.snapshot(),'setup':prepared.setup_counts}))
            prepared=cache[key]
            if job['kind']=='single' or job['target_id'] is None:
                role='points' if job['kind']=='single' else 'trace-starts'
                target,sampling=sample_coordinate(model,public['nonce'],role+'/'+c['curve_id'],str(job['point_index']),job['proposal_limit'])
                if target is None: raise RuntimeError('CAPPED_PROPOSALS:'+json.dumps(sampling,sort_keys=True))
            else:
                target=point_from_json(next(t['point'] for t in c['targets'] if t['target_id']==job['target_id']));sampling=None
            if job['kind']=='single':
                answer,counts=prepared.evaluate(target)
                emit('singles',record('single-point',single_id=job['id'],curve_id=c['curve_id'],arm_id=arm['id'],point=point_json(target),sampling=sampling,answer=answer,counts=counts));continue
            if job['kind'] not in ('calibration-trace','confirmation-trace'): raise ValueError('unfrozen job kind')
            rng=Counter();b,draw=uniform_below(public['nonce'],'target-blinding/'+job['id'],'b',model['r']-1,rng);b+=1
            draw={'uniform_draw':draw,'target_multiplier':b,'counts':rng.snapshot(),'point_sampling':sampling}
            emit('intents',record('intent',trace_id=job['id'],curve_id=c['curve_id'],target_id=job['target_id'],arm_id=arm['id'],target=point_json(target),base_multiplier=a,target_multiplier=b,draw=draw))
            if job['kind']=='confirmation-trace':
                if arm['id']!='circuit2.a1': raise ValueError('confirmation requires fixed primary circuit2.a1')
                pair=paired_attempt(prepared,base,target,a,b)
            else:
                _,original=ungated_attempt(prepared,base,target,a,b,True)
                pair={'original':original,'incremental':None,'equal':None,'cells':[]}
            emit('traces',record('trace',trace_id=job['id'],curve_id=c['curve_id'],target_id=job['target_id'],arm_id=arm['id'],target=point_json(target),base_multiplier=a,target_multiplier=b,draw=draw,original=pair['original'],incremental=pair['incremental'],equal=pair['equal']))
            for cell in pair['cells']:
                emit('cells',record('decoder-cell',cell_id=job['id']+f"/t{cell['radius']}.e{cell['erasure_cap']}",trace_id=job['id'],**cell))
    except Exception as exc:
        errors.append({'type':type(exc).__name__,'message':str(exc)})
    finally:
        for h in handles.values(): h.close()
    status='complete' if not errors and observed==plan['expected'] else 'incomplete'
    summary=record('summary',status=status,expected=plan['expected'],observed=observed,errors=errors,wall_valid=False,provenance=provenance)
    write_json(out/'engine-summary.json',summary)
    files={v:{'sha256':sha_file(out/v),'bytes':(out/v).stat().st_size,'records':observed[k]} for k,v in paths.items()}
    files['engine-summary.json']={'sha256':sha_file(out/'engine-summary.json'),'bytes':(out/'engine-summary.json').stat().st_size,'records':1}
    completion=record('completion',status=status,files=files,wall_valid=False,termination_ack=False,provenance=provenance)
    write_json(out/'engine-completion.json',completion)
    return completion
