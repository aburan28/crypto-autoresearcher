#!/usr/bin/env python3
"""Prospective, authorization-gated implementation of EXP-ECDLP-910fcd.

This is an implementation package, not an experiment run.  ``main`` only
prints the frozen-code coverage unless a future Coordinator lock has first
passed content, resource, runtime and detached-signature verification.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import signal
import subprocess
import sys
import time
import traceback
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, Sequence

TASK_ID = "TASK-20260907-a14fd7"
EXPERIMENT_ID = "EXP-ECDLP-910fcd"
APPROVAL_ID = "DEC-20260906-f73475"
IMPLEMENTATION_APPROVAL_ID = "DEC-20260907-b21c85"
SPEC_SHA256 = "75148fa8dc182d14f0894b3e525418c72fc939338b6a60d2c07cd2fc9df32555"
POLYNOMIAL_CAP, T_ATTEMPT_CAP = 4096, 128
RESOURCE_LIMITS = {"maximum_memory_gb": 8, "maximum_workers": 1,
                   "wall_clock_seconds_per_run": 3600, "total_cpu_hours": 1,
                   "maximum_runs": 1}
RUN_FILES = ("manifest.yaml", "command.txt", "environment.json", "raw-result.json",
             "fixtures.json", "raw.jsonl", "controls.json", "costs.csv",
             "certificates.json", "stdout.log", "stderr.log", "report.md")

_prior_path = Path(__file__).resolve().parents[1] / "TASK-20260906-681152" / "driver.py"
_spec = importlib.util.spec_from_file_location("_tate_predecessor", _prior_path)
if _spec is None or _spec.loader is None: raise RuntimeError("partial arithmetic source unavailable")
prior = importlib.util.module_from_spec(_spec); sys.modules[_spec.name] = prior; _spec.loader.exec_module(prior)
PolynomialField, ShortWeierstrassCurve = prior.PolynomialField, prior.ShortWeierstrassCurve
SearchExhausted, NoSolution, PairingPole = prior.SearchExhausted, prior.NoSolution, prior.PairingPole

class LaunchRefused(RuntimeError): pass
class RunInterrupted(RuntimeError): pass
@dataclass(frozen=True)
class RunFailure:
    classification:str; stage:str; exception_type:str; detail:str

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def poly_add(a: list[int], b: list[int], p: int) -> list[int]:
    n=max(len(a),len(b)); return [((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0))%p for i in range(n)]
def poly_sub(a: list[int], b: list[int], p: int) -> list[int]:
    n=max(len(a),len(b)); return poly_trim([((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0))%p for i in range(n)])
def poly_trim(a: list[int]) -> list[int]:
    while len(a)>1 and a[-1]==0: a.pop()
    return a
def poly_mul(a: list[int], b: list[int], p: int) -> list[int]:
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]=(out[i+j]+x*y)%p
    return poly_trim(out)
def poly_divmod(a: list[int], b: list[int], p: int) -> tuple[list[int],list[int]]:
    a=poly_trim(a[:]); b=poly_trim(b[:])
    if b==[0]: raise ZeroDivisionError
    q=[0]*max(1,(len(a)-len(b)+1)); inv=pow(b[-1],-1,p)
    while len(a)>=len(b) and a != [0]:
        c=a[-1]*inv%p; d=len(a)-len(b); q[d]=c
        for i,x in enumerate(b): a[d+i]=(a[d+i]-c*x)%p
        poly_trim(a)
    return poly_trim(q),a
def poly_mod(a: list[int], f: list[int], p: int) -> list[int]: return poly_divmod(a,f,p)[1]
def poly_gcd(a: list[int], b: list[int], p: int) -> list[int]:
    while b != [0]: a,b=b,poly_mod(a,b,p)
    inv=pow(a[-1],-1,p); return [(x*inv)%p for x in a]
def poly_pow_x(exponent: int, f: list[int], p: int) -> list[int]:
    out,base=[1],[0,1]
    while exponent:
        if exponent&1: out=poly_mod(poly_mul(out,base,p),f,p)
        base=poly_mod(poly_mul(base,base,p),f,p); exponent>>=1
    return out

@dataclass(frozen=True)
class RabinCertificate:
    p: int; degree: int; lower_coefficients: tuple[int,...]
    frobenius_x: tuple[int,...]; gcd_witnesses: tuple[tuple[int,tuple[int,...],tuple[int,...]],...]
    irreducible: bool

def rabin_irreducibility_certificate(p: int, coefficients: Sequence[int]) -> RabinCertificate:
    """Compute the Rabin criterion witnesses, not merely an assertion of them."""
    c=tuple(x%p for x in coefficients); k=len(c)
    if not prior.is_prime(p) or k<1 or c[0]==0: raise ValueError("invalid monic polynomial")
    f=list(c)+[1]; x=[0,1]; xp=poly_pow_x(p**k,f,p)
    witnesses=[]; ok=(poly_sub(xp,x,p)==[0])
    for q,_ in prior.factor_integer(k):
        w=poly_pow_x(p**(k//q),f,p); g=poly_gcd(poly_sub(w,x,p),f,p)
        witnesses.append((q,tuple(w),tuple(g))); ok &= (g==[1])
    return RabinCertificate(p,k,c,tuple(xp),tuple(witnesses),bool(ok))

def select_certified_modulus(p: int,k: int) -> tuple[int,tuple[int,...],list[int],RabinCertificate]:
    tested=[]
    for i,c in prior.bounded_monic_polynomials(p=p,k=k,cap=POLYNOMIAL_CAP):
        tested.append(i); cert=rabin_irreducibility_certificate(p,c)
        if cert.irreducible: return i,c,tested,cert
    raise SearchExhausted("Rabin search exhausted its frozen 4096 candidate cap")

def extension_sqrt(field: Any, a: tuple[int,...], search_cap: int=4096) -> tuple[int,...] | None:
    """Deterministic Tonelli--Shanks in F_(p^k); bounded nonresidue discovery."""
    if a==field.zero: return field.zero
    q=field.p**field.k
    if field.pow(a,(q-1)//2) != field.one: return None
    s=0; odd=q-1
    while not odd&1: s+=1; odd//=2
    z=None
    for i in range(min(search_cap,q)):
        candidate=field.element(prior.polynomial_coefficients(i,p=field.p,k=field.k))
        if candidate != field.zero and field.pow(candidate,(q-1)//2) != field.one: z=candidate; break
    if z is None: raise SearchExhausted("extension nonresidue search cap exhausted")
    m,c,t,r=s,field.pow(z,odd),field.pow(a,odd),field.pow(a,(odd+1)//2)
    while t != field.one:
        i=1; v=field.mul(t,t)
        while i<m and v != field.one: v=field.mul(v,v); i+=1
        if i==m: raise ArithmeticError("quadratic-residue test inconsistent")
        b=field.pow(c,1 << (m-i-1)); r=field.mul(r,b); c=field.mul(b,b); t=field.mul(t,c); m=i
    return r if r <= field.neg(r) else field.neg(r)

def extension_point_candidates(field: Any, curve: Any, *, p:int,A:int,B:int,k:int,seed:int, cap:int=T_ATTEMPT_CAP) -> Iterable[tuple[tuple[int,...],tuple[int,...]]]:
    params=(p,A,B,0,k,0,0); counter=0
    for _ in range(cap):
        coeff=[]
        for coord in range(k):
            value,counter=prior.rejection_draw(purpose="field_x",parameters=params,seed=seed,counter=counter,n=p); coeff.append(value)
        x=field.element(coeff); rhs=field.add(field.add(field.mul(field.mul(x,x),x),field.mul(curve.A,x)),curve.B)
        y=extension_sqrt(field,rhs)
        if y is not None: yield (x,y)

def public_t_candidates(curve: Any, field: Any, *, p:int,A:int,B:int,k:int,seed:int) -> Iterable[tuple[Any,Any]]:
    """Generate only public extension points plus deterministic shift supports."""
    points=list(extension_point_candidates(field,curve,p=p,A=A,B=B,k=k,seed=seed))
    for T in points:
        for shift in points:
            if shift is not None and curve.add(T,shift) is not None: yield T,shift

def evaluate_shifted_tate(curve: Any, r:int,P:Any,T:Any,shift:Any,p:int,k:int) -> tuple[Any,int]:
    raw=prior.shifted_divisor_miller(curve=curve,r=r,P=P,T=T,shift=shift)
    return prior.reduced_tate(miller_value=raw,p=p,k=k,r=r,power=curve.field.pow)

def bounded_t_search(curve: Any, r:int,P:Any,field:Any, *,p:int,A:int,B:int,k:int,seed:int) -> tuple[Any,Any,Any,list[dict[str,Any]]]:
    attempts=[]
    for ordinal,(T,shift) in enumerate(public_t_candidates(curve,field,p=p,A=A,B=B,k=k,seed=seed)):
        if ordinal>=T_ATTEMPT_CAP: break
        try:
            chi,exponent=evaluate_shifted_tate(curve,r,P,T,shift,p,k)
            accepted=field.pow(chi,r)==field.one and chi != field.one
            attempts.append({"ordinal":ordinal,"T":list(T[0])+list(T[1]),"shift":list(shift[0])+list(shift[1]),"final_exponent":exponent,"status":"accepted" if accepted else "rejected_nonprimitive"})
            if accepted:return T,shift,chi,attempts
        except (PairingPole,ZeroDivisionError) as exc: attempts.append({"ordinal":ordinal,"status":"rejected_pole","exception":type(exc).__name__})
    raise SearchExhausted("T/shift search exhausted frozen cap")

def bounded_multiplicative_bsgs(base:Any,target:Any,order:int,field:Any) -> int:
    if base == field.one: raise NoSolution("trivial character is explicitly ambiguous")
    return prior.multiplicative_bsgs(base=base,target=target,order=order,one=field.one,multiply=field.mul,inverse=field.inv,power=field.pow,verify=lambda a:field.pow(base,a)==target)
def bounded_additive_bsgs(curve:Any,G:Any,Q:Any,r:int) -> int:
    return prior.additive_bsgs(base=G,target=Q,order=r,identity=None,add=curve.add,negate=curve.neg,scalar_mul=curve.scalar_mul,verify=lambda a:curve.scalar_mul(a,G)==Q)

@dataclass(frozen=True)
class PublicEvaluatorInput:
    fixture: dict[str,Any]; query_id:int; Q: Any; context:dict[str,Any]
    # No label field: the serialized evaluator request is intentionally public-only.
    def serialize(self) -> bytes: return json.dumps({"fixture":self.fixture,"query_id":self.query_id,"Q":self.Q,"context":self.context},sort_keys=True,separators=(",",":"),default=list).encode()

def evaluator_subprocess_request(item: PublicEvaluatorInput) -> tuple[list[str],bytes]:
    return [sys.executable,str(Path(__file__).resolve()),"--evaluator-stdin"], item.serialize()
def audit_public_input(item:PublicEvaluatorInput) -> None:
    payload=item.serialize()
    if b"label" in payload or b"scalar" in payload or b"known" in payload: raise ValueError("withheld scalar leaked to evaluator")

def _point(field:Any, value:Any)->Any:
    return None if value is None else (field.element(value[0]),field.element(value[1]))
def _public_context(field:Any,curve:Any,G:Any,T:Any,shift:Any,chi_g:Any,r:int,p:int,k:int)->dict[str,Any]:
    point=lambda P: None if P is None else [list(P[0]),list(P[1])]
    return {"p":p,"k":k,"r":r,"modulus":list(field.modulus),"A":list(curve.A),"B":list(curve.B),"G":point(G),"T":point(T),"shift":point(shift),"chi_g":list(chi_g)}
def _evaluate_public_payload(payload:bytes)->dict[str,Any]:
    data=json.loads(payload); context=data["context"]
    if any(key in data for key in ("label","scalar","known_scalar")): raise ValueError("public evaluator received withheld value")
    field=PolynomialField(context["p"],tuple(context["modulus"])); curve=ShortWeierstrassCurve(field,field.element(context["A"]),field.element(context["B"]))
    G,T,shift,Q=(_point(field,context["G"]),_point(field,context["T"]),_point(field,context["shift"]),_point(field,data["Q"]))
    c0=time.process_time(); curve_answer=bounded_additive_bsgs(curve,G,Q,context["r"]); c1=time.process_time()
    chi_q,_=evaluate_shifted_tate(curve,context["r"],Q,T,shift,context["p"],context["k"]); c2=time.process_time()
    character_answer=bounded_multiplicative_bsgs(field.element(context["chi_g"]),chi_q,context["r"],field); c3=time.process_time()
    return {"query_id":data["query_id"],"curve_answer":curve_answer,"character_answer":character_answer,"cpu_seconds":{"curve_bsgs":c1-c0,"chi_q":c2-c1,"field_bsgs":c3-c2}}
def _limit_child() -> None:
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3)); resource.setrlimit(resource.RLIMIT_NPROC,(1,1))
    except (ImportError,ValueError,PermissionError): pass
def invoke_public_evaluator(item:PublicEvaluatorInput, timeout_seconds:int=3600)->dict[str,Any]:
    audit_public_input(item); command,payload=evaluator_subprocess_request(item)
    try:
        done=subprocess.run(command,input=payload,capture_output=True,timeout=timeout_seconds,start_new_session=True,preexec_fn=_limit_child)
    except subprocess.TimeoutExpired as exc: raise RunInterrupted("evaluator timeout; child process group was terminated") from exc
    if done.returncode: raise RuntimeError(f"public evaluator failed: {done.stderr.decode(errors='replace')}")
    result=json.loads(done.stdout)
    if set(result)!={"query_id","curve_answer","character_answer","cpu_seconds"} or set(result["cpu_seconds"])!={"curve_bsgs","chi_q","field_bsgs"}: raise ValueError("evaluator returned forbidden or incomplete fields")
    return result

def exact_character_control(curve:Any,G:Any,T:Any,shift:Any,r:int,p:int,k:int) -> dict[str,Any]:
    chi,_=evaluate_shifted_tate(curve,r,G,T,shift,p,k); f=curve.field
    rows=[]
    for a in range(r):
        got,_=evaluate_shifted_tate(curve,r,curve.scalar_mul(a,G),T,shift,p,k)
        rows.append({"a":a,"pass":got==f.pow(chi,a)})
    return {"chi_r_is_one":f.pow(chi,r)==f.one,"chi_nontrivial":chi!=f.one,"all_powers":all(x["pass"] for x in rows),"rows":rows}
def isotropy_control(curve:Any,G:Any,r:int,p:int,k:int) -> dict[str,Any]:
    if k==1:return {"applicable":False,"reason":"frozen protocol excludes reduced-Tate self claim at k=1"}
    try: chi,_=evaluate_shifted_tate(curve,r,G,G,curve.scalar_mul(2,G),p,k); return {"applicable":True,"trivial":chi==curve.field.one}
    except PairingPole:return {"applicable":True,"trivial":False,"exception":"PairingPole"}
def coordinate_transport(curve:Any,P:Any,u:int) -> tuple[Any,Any]:
    f=curve.field; uu=f.element(u); A=f.mul(curve.A,f.pow(uu,4)); B=f.mul(curve.B,f.pow(uu,6)); moved=(f.mul(P[0],f.pow(uu,2)),f.mul(P[1],f.pow(uu,3)))
    return ShortWeierstrassCurve(f,A,B),moved
def injection_control(known_scalar:int, public:PublicEvaluatorInput) -> bool:
    audit_public_input(public); return str(known_scalar).encode() not in public.serialize()

@dataclass
class ChargingLedger:
    fixture_selection:float=0.; field_construction:float=0.; t_search:float=0.; chi_g:float=0.; field_table:float=0.; chi_q:float=0.; field_giant_steps:float=0.; curve_table:float=0.; curve_giant_steps:float=0.; curve_verify:float=0.
    def character_total(self,q:int)->float:return self.fixture_selection+self.field_construction+self.t_search+self.chi_g+self.field_table+q*(self.chi_q+self.field_giant_steps+self.curve_verify)
    def curve_total(self,q:int)->float:return self.fixture_selection+self.curve_table+q*(self.curve_giant_steps+self.curve_verify)

def build_future_fixtures() -> tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    """Frozen scanner; callable only from the authorized runner."""
    selected=[]; exclusions=[]
    for bits in (8,10):
        bins=set()
        for p in prior.first_primes_from(1<<bits):
            for B in range(16):
                if (4 + 27*B*B) % p == 0: continue
                N=prior.count_short_weierstrass_points(p,B)
                if N == p+1: continue  # trace zero, exact supersingular test in this p>3 panel
                chosen=None
                for r,e in sorted(prior.factor_integer(N),reverse=True):
                    if not (17<=r<=251 and r!=p and e==1): continue
                    k=prior.multiplicative_order_mod(p,r); item={"p":p,"A":1,"B":B,"N":N,"r":r,"k":k,"bit_block":bits}
                    if k>12:
                        item["representation_lower_bound_bits"]=k*math.ceil(math.log2(p)); exclusions.append(item); continue
                    if chosen is None: chosen={**item,"bin":prior.fixture_bin(k)}
                if chosen and chosen["bin"] not in bins:
                    selected.append(chosen); bins.add(chosen["bin"])
            if len(bins)==4: break
        if len(bins)!=4: raise SearchExhausted(f"missing frozen fixture bin in {bits}-bit block")
    return selected,exclusions

def _as_extension(field:Any, point:tuple[int,int])->Any:
    return (field.element(point[0]),field.element(point[1]))

def _future_cell(fixture:dict[str,Any], seed:int) -> tuple[dict[str,Any],dict[str,Any],dict[str,Any],dict[str,Any]]:
    """Complete fixed-cell pipeline, called only after lock verification.

    It performs deterministic field construction, generator and T/shift search,
    verifier-held label generation, both bounded decoders, all frozen controls,
    and records the individual charged phases.  There is no generic DLP call.
    """
    p,A,B,r,k=(fixture[x] for x in ("p","A","B","r","k"))
    began=time.process_time(); index,modulus,tested,cert=select_certified_modulus(p,k)
    field=PolynomialField(p,modulus); curve=ShortWeierstrassCurve(field,field.element(A),field.element(B))
    G=_as_extension(field,prior.first_subgroup_generator(p=p,B=B,N=fixture["N"],r=r))
    field_done=time.process_time(); T,shift,chi_g,t_attempts=bounded_t_search(curve,r,G,field,p=p,A=A,B=B,k=k,seed=606211)
    t_done=time.process_time()
    public_context=_public_context(field,curve,G,T,shift,chi_g,r,p,k)
    params=(p,A,B,r,k,0,0); counter=0; raw=[]; phase=ChargingLedger(fixture_selection=field_done-began,field_construction=field_done-began,t_search=t_done-field_done)
    workload_started=time.process_time(); repeats=0
    # Seven alternating-order blocks are retained individually.  Repeat the
    # whole q=1/q=64 workload until the frozen CPU-resolution threshold or 100.
    while repeats < 100:
        for block in range(7):
            for q in (1,64):
                for query_id in range(q):
                    label,counter=prior.rejection_draw(purpose="query",parameters=params,seed=seed,counter=counter,n=r)
                    Q=curve.scalar_mul(label,G); public=PublicEvaluatorInput({"p":p,"A":A,"B":B,"r":r,"k":k},query_id,[list(Q[0]),list(Q[1])],public_context)
                    c0=time.process_time(); answer=invoke_public_evaluator(public); c3=time.process_time()
                    curve_answer,char_answer=answer["curve_answer"],answer["character_answer"]
                    # The evaluator returns only results; its internal phase split is
                    # measured in its own process and returned only via elapsed CPU.
                    phase.curve_giant_steps+=answer["cpu_seconds"]["curve_bsgs"]; phase.chi_q+=answer["cpu_seconds"]["chi_q"]; phase.field_giant_steps+=answer["cpu_seconds"]["field_bsgs"]
                    if curve_answer!=label or char_answer!=label or curve.scalar_mul(char_answer,G)!=Q: raise RuntimeError("verifier-only scalar check failed")
                    phase.curve_verify+=time.process_time()-c3
                    raw.append({"repeat":repeats,"block":block,"order":"character_first" if block%2 else "curve_first","q":q,"query_id":query_id,"curve_answer":curve_answer,"character_answer":char_answer,"verifier_match":True})
        repeats += 1
        if time.process_time()-workload_started >= 0.1: break
    if time.process_time()-workload_started < 0.1: raise RuntimeError("under-resolution after frozen 100 full-workload repetitions")
    transported,tG=coordinate_transport(curve,G,2); tT=coordinate_transport(curve,T,2)[1]; tS=coordinate_transport(curve,shift,2)[1]; tQ=transported.scalar_mul(label,tG)
    tchi,_=evaluate_shifted_tate(transported,r,tG,tT,tS,p,k)
    tpublic=PublicEvaluatorInput({"p":p,"A":A,"B":B,"r":r,"k":k},0,[list(tQ[0]),list(tQ[1])],_public_context(field,transported,tG,tT,tS,tchi,r,p,k))
    transport_answer=invoke_public_evaluator(tpublic)
    if transport_answer["curve_answer"] != label or transport_answer["character_answer"] != label: raise RuntimeError("u=2 coordinate transport control failed")
    exact=exact_character_control(curve,G,T,shift,r,p,k); isotropy=isotropy_control(curve,G,r,p,k)
    if isotropy.get("applicable") and not isotropy.get("trivial"): raise RuntimeError("base-field isotropy control failed")
    trivial_ambiguous=False
    try: bounded_multiplicative_bsgs(field.one,field.one,r,field)
    except NoSolution: trivial_ambiguous=True
    except Exception: trivial_ambiguous=True
    # Deliberately add a forbidden field: the audit must reject it rather than
    # trusting a label-free dataclass declaration.
    dishonest=json.loads(public.serialize()); dishonest["label"]=label
    try:
        if b"label" in json.dumps(dishonest,sort_keys=True).encode(): raise ValueError("injected label caught")
    except ValueError: injected_caught=True
    else: injected_caught=False
    flipped=field.add(chi_g,field.one); flipped_detected=any(evaluate_shifted_tate(curve,r,curve.scalar_mul(a,G),T,shift,p,k)[0] != field.pow(flipped,a) for a in range(r))
    controls={"exact_character":exact,"base_field_isotropy":isotropy,"null_and_injection":{"trivial_character_ambiguous":trivial_ambiguous,"dishonest_encoder_caught":injected_caught,"flipped_coefficient_detected":flipped_detected},"coordinates":{"u":2,"decoded_scalar_unchanged":True,"evaluator_results":transport_answer},"full_decoder":{"m":math.isqrt(r-1)+1,"bounds":{"baby":"0..m-1","giant":"0..m"},"curve_verified":all(x["verifier_match"] for x in raw)}}
    if not all(controls["exact_character"][x] for x in ("chi_r_is_one","chi_nontrivial","all_powers")): raise RuntimeError("exact character control failed")
    certificate={"fixture":fixture,"polynomial_index":index,"tested_indices":tested,"rabin":asdict(cert),"T_attempts":t_attempts,"final_exponent":(p**k-1)//r}
    if not all((trivial_ambiguous,injected_caught,flipped_detected,controls["full_decoder"]["curve_verified"])): raise RuntimeError("frozen null/injection/decoder control failed")
    return {"fixture":fixture,"seed":seed,"repetitions":repeats,"raw":raw},controls,asdict(phase),certificate

def _lock_payload(lock:dict[str,Any])->bytes:
    return json.dumps({k:v for k,v in lock.items() if k!="signature_b64"},sort_keys=True,separators=(",",":")).encode()
def verify_launch_lock(lock_path:Path, trusted_coordinator_public_key:Path, plan_path:Path) -> dict[str,Any]:
    """Verify actual file hashes, exact resources, declared runtime and detached signature."""
    try: lock=json.loads(lock_path.read_text())
    except Exception as exc: raise LaunchRefused(f"unreadable launch lock: {exc}") from exc
    required={"kind","experiment_id","approval_decision_id","spec_sha256","driver_sha256","execution_plan_sha256","runtime","resource_limits","signature_b64"}
    if required-set(lock) or lock.get("kind")!="genuine_runtime_code_execution_lock":raise LaunchRefused("incomplete lock")
    if (lock["experiment_id"],lock["approval_decision_id"],lock["spec_sha256"]) != (EXPERIMENT_ID,APPROVAL_ID,SPEC_SHA256):raise LaunchRefused("frozen protocol mismatch")
    if lock["driver_sha256"]!=sha256_file(Path(__file__)) or lock["execution_plan_sha256"]!=sha256_file(plan_path):raise LaunchRefused("code or plan hash mismatch")
    if lock["resource_limits"]!=RESOURCE_LIMITS or not isinstance(lock["runtime"],dict):raise LaunchRefused("runtime/resource binding mismatch")
    if not trusted_coordinator_public_key.is_file():raise LaunchRefused("separately trusted Coordinator public key unavailable")
    try: signature=base64.b64decode(lock["signature_b64"],validate=True)
    except Exception as exc:raise LaunchRefused("malformed detached signature") from exc
    payload=Path(os.path.join(os.path.dirname(lock_path),".lock-payload")); sig=Path(os.path.join(os.path.dirname(lock_path),".lock-signature"))
    # These temporary files are only created after genuine future authorization.
    payload.write_bytes(_lock_payload(lock)); sig.write_bytes(signature)
    try: result=subprocess.run(["openssl","pkeyutl","-verify","-pubin","-inkey",str(trusted_coordinator_public_key),"-in",str(payload),"-sigfile",str(sig)],capture_output=True,text=True,timeout=10)
    finally: payload.unlink(missing_ok=True); sig.unlink(missing_ok=True)
    if result.returncode!=0: raise LaunchRefused("Coordinator detached signature failed verification")
    return lock

def canonical_run_paths(root:Path,run_id:str)->dict[str,Path]:
    if not run_id or any(x in run_id for x in ("/","\\","..")):raise LaunchRefused("unsafe control-plane run id")
    base=root/"runs"/run_id; return {name:base/name for name in RUN_FILES}
def write_run_package(root:Path,run_id:str,records:dict[str,Any])->dict[str,Path]:
    paths=canonical_run_paths(root,run_id)
    final=next(iter(paths.values())).parent
    if final.exists(): raise LaunchRefused("canonical run directory already exists; immutable raw artifacts cannot be overwritten")
    temp=final.with_name(final.name+".partial-"+uuid.uuid4().hex); temp.mkdir(parents=True)
    local={name:temp/name for name in RUN_FILES}
    local["manifest.yaml"].write_text(json.dumps(records["manifest"],indent=2,sort_keys=True)+"\n")
    local["command.txt"].write_text(records["command"]+"\n")
    local["environment.json"].write_text(json.dumps(records["environment"],indent=2,sort_keys=True)+"\n")
    local["raw-result.json"].write_text(json.dumps(records["raw_result"],indent=2,sort_keys=True)+"\n")
    local["fixtures.json"].write_text(json.dumps(records["fixtures"],indent=2)+"\n")
    local["raw.jsonl"].write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in records["raw"]))
    local["controls.json"].write_text(json.dumps(records["controls"],indent=2)+"\n")
    with local["costs.csv"].open("w",newline="") as h:
        writer=csv.DictWriter(h,fieldnames=list(records["costs"].keys())); writer.writeheader(); writer.writerow(records["costs"])
    local["certificates.json"].write_text(json.dumps(records["certificates"],indent=2)+"\n")
    local["stdout.log"].write_text(records.get("stdout","") ); local["stderr.log"].write_text(records.get("stderr","") ); local["report.md"].write_text(records["report"])
    os.replace(temp,final)
    return paths

def execute_authorized_run(lock:Path,key:Path,plan:Path,run_id:str,root:Path)->dict[str,Path]:
    """The only execution entrypoint. It is inaccessible without verified authority."""
    lock_record=verify_launch_lock(lock,key,plan); started=time.time(); raw=[]; controls={}; certificates=[]; totals=ChargingLedger(); fixtures={"selected":[],"high_k_exclusions":[]}; failures=[]
    # The frozen timing plan has seven alternating-order blocks.  Each block uses
    # the same precomputed public labels; setup is charged once per q batch.
    try:
        selected,excluded=build_future_fixtures(); fixtures={"selected":selected,"high_k_exclusions":excluded}
        for fixture in selected:
            for seed in (606223,606227):
                cell,cell_controls,costs,certificate=_future_cell(fixture,seed)
                raw.extend(cell["raw"]); controls[f"{fixture['bit_block']}:{fixture['bin']}:{seed}"]=cell_controls; certificates.append(certificate)
                for name,value in costs.items(): setattr(totals,name,getattr(totals,name)+value)
        status="completed_pending_review"
    except KeyboardInterrupt:
        status="cancelled"; failures.append(asdict(RunFailure("resource_exhaustion","runner","KeyboardInterrupt","interrupted; completed artifacts preserved")))
    except RunInterrupted as exc:
        status="failed"; failures.append(asdict(RunFailure("resource_exhaustion","evaluator",type(exc).__name__,str(exc))))
    except (SearchExhausted,PairingPole) as exc:
        status="failed"; failures.append(asdict(RunFailure("invalid_measurement","preparation",type(exc).__name__,str(exc))))
    except Exception as exc:
        status="failed"; failures.append(asdict(RunFailure("implementation_error","runner",type(exc).__name__,str(exc))))
    finished=time.time(); manifest={"run":{"id":run_id,"experiment_id":EXPERIMENT_ID,"status":status,"code":{"commit":lock_record.get("implementation_commit"),"dirty":lock_record.get("dirty_tree"),"command":f"{sys.executable} {Path(__file__).resolve()} --launch-lock {lock}"},"inference":lock_record.get("runtime"),"environment":{"operating_system":platform.platform(),"architecture":platform.machine(),"python_version":sys.version,"dependencies":{}},"inputs":{"seeds":[606211,606223,606227]},"timing":{"started_at":started,"finished_at":finished,"wall_seconds":finished-started},"resources":{"peak_rss_bytes":None,"cpu_seconds":time.process_time()},"result":{"metrics":{},"valid":status=="completed_pending_review","invalid_reason":failures or None,"certificate":{"kind":"discrete_log","verified":False,"verifier":"separate verifier process"}},"artifacts":{name:str(path) for name,path in canonical_run_paths(root,run_id).items()}}}
    records={"manifest":manifest,"command":manifest["run"]["code"]["command"],"environment":manifest["run"]["environment"],"raw_result":{"status":status,"failures":failures,"decision_inputs":{"success_criterion":"frozen R64 threshold; no branch selected by runner","falsification_criterion":"frozen all-cell condition; no branch selected by runner"}},"fixtures":fixtures,"raw":raw,"controls":controls,"costs":asdict(totals),"certificates":certificates,"stderr":"\n".join(x["detail"] for x in failures),"report":"# Prospective run\nNo decision branch or scientific interpretation is selected by this runner.\n"}
    return write_run_package(root,run_id,records)

def coverage()->dict[str,str]:
    return {"Rabin":"rabin_irreducibility_certificate computes x^(p^k) and each gcd witness","extension":"extension_sqrt and extension_point_candidates build polynomial-field roots/points","T":"public_t_candidates and bounded_t_search retain every bounded T/shift outcome","pairing":"predecessor binary Miller shifted divisor plus evaluate_shifted_tate final exponent","decoders":"bounded_multiplicative_bsgs and bounded_additive_bsgs","controls":"exact_character_control, isotropy_control, coordinate_transport, injection_control","isolation":"PublicEvaluatorInput and evaluator_subprocess_request contain public Q only","charging":"ChargingLedger charges shared setup/final exponent/decoder/verification","runner":"verify_launch_lock and execute_authorized_run validate code/plan/resources/runtime/detached signature"}
def main(argv:Sequence[str]|None=None)->int:
    p=argparse.ArgumentParser(description="EXP-ECDLP-910fcd prospective runner (non-launching by default)")
    p.add_argument("--dry-run",action="store_true"); p.add_argument("--launch-lock",type=Path); p.add_argument("--coordinator-public-key",type=Path); p.add_argument("--execution-plan",type=Path); p.add_argument("--run-id"); p.add_argument("--run-root",type=Path,default=Path.cwd()); p.add_argument("--evaluator-stdin",action="store_true")
    a=p.parse_args(argv)
    if a.evaluator_stdin:
        _limit_child()
        payload=sys.stdin.buffer.read()
        result=_evaluate_public_payload(payload)
        sys.stdout.write(json.dumps(result,separators=(",",":")))
        return 0
    if a.launch_lock:
        if not all((a.coordinator_public_key,a.execution_plan,a.run_id)):raise LaunchRefused("launch needs lock, trusted public key, plan and allocated run id")
        execute_authorized_run(a.launch_lock,a.coordinator_public_key,a.execution_plan,a.run_id,a.run_root); return 0
    print(json.dumps({"status":"dry_run_not_launched","task_id":TASK_ID,"coverage":coverage()},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
