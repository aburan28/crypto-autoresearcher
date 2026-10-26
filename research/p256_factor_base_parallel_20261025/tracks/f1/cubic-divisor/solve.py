"""Single exact algebraic attempt. Supervisor retains native output and watchdog."""
import argparse,json,sys
from pathlib import Path
import sympy as sp
from cubic import *

def event(kind,**data):print(json.dumps({'event':kind,**data}),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--depth',type=int)
    ap.add_argument('--stratum',choices=['distinct','twoequal','allequal'],required=True)
    ap.add_argument('--target',choices=['positive','twoequal','allequal','base','generator'],default='positive')
    ap.add_argument('--membership-only',action='store_true');args=ap.parse_args()
    fix=fixture(args.case,args.depth,args.target);k,c,Q=fix['k'],fix['c'],fix['Q']
    if args.stratum=='distinct':
        eqs,levels=remainder_circuit(k,c);vs=V;s4=s4_polynomial(Q)
    elif args.stratum=='twoequal':
        eqs=repeated_equations(k,c);levels=[];vs=(X,Y)
        s4=s4_polynomial(Q,vs,(2*X+Y,X*X+2*X*Y,X*X*Y))
    else:
        t=poly(T,(T,))
        for _ in range(k):t=t*t-2
        eqs=[t-c];levels=[];vs=(T,)
        s4=s4_polynomial(Q,vs,(3*T,3*T*T,T*T*T))
    if not args.membership_only:eqs.append(s4)
    expected=oracle(fix,args.stratum,not args.membership_only)
    event('input',k=k,c=c,Q=Q,stratum=args.stratum,target=args.target,
          mode='membership' if args.membership_only else 'joint',equations=shapes(eqs),levels=levels)
    event('groebner-start',order='grevlex')
    gb=sp.groebner([f.as_expr() for f in eqs],*vs,modulus=p,order='grevlex')
    event('groebner-end',polynomials=len(gb.polys),degrees=shapes(gb.polys),standard_monomials=len(quotient_basis(gb)))
    cert=certificate(gb,eqs,expected)
    points=rational_points([f.as_expr() for f in gb.polys],vs)
    assert points==expected
    solutions=[] if args.membership_only else recover(fix,args.stratum,points)
    out={'status':'PASS','k':k,'S':1<<k,'c':c,'target':Q,'target_kind':args.target,
        'stratum':args.stratum,'mode':'membership' if args.membership_only else 'joint',
        'equations':[record(f) for f in eqs],'input_shapes':shapes(eqs),'circuit_shapes':levels,
        'groebner_basis':[record(f) for f in gb.polys],'certificate':cert,
        'complete_stratum_points':points,'complete_point_count':len(points),
        'signed_decompositions':solutions,'signed_decomposition_count':len(solutions),
        'fixture':{'case_file':str(args.case),'domain':fix['xs'],'signed_base':fix['F']},
        'adapter':'SymPy 1.14.0 default Buchberger; lex branch extraction; FLINT roots',
        'timing_claim':False,'independent_session':False}
    write(args.out,out)
    event('complete',point_count=len(points),signed_decompositions=len(solutions),certificate='PASS')

if __name__=='__main__':main()
